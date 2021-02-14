from ... import config
from ..gen import frameserver_pb2
from ..gen import frameserver_pb2_grpc
from ..gen import renderserver_pb2
from ..gen import renderserver_pb2_grpc
from concurrent import futures
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import grpc
import subprocess as sp
import threading
import time
import traceback
import types
from ...utils.module_ops import (
    get_module,
    get_scene_classes_from_module,
    get_scenes_to_render,
    scene_classes_from_file,
)
from ... import logger
from ...constants import WEBGL_RENDERER_INFO
from ...renderer.webgl_renderer import WebGLRenderer
from ...utils.family import extract_mobject_family_members
import logging
import copy
from ...mobject.value_tracker import ValueTracker
from ...mobject.types.vectorized_mobject import VMobject
from ...mobject.types.image_mobject import ImageMobject


class ScriptUpdateHandler(FileSystemEventHandler):
    def __init__(self, frame_server):
        super().__init__()
        self.frame_server = frame_server

    def catch_all_handler(self, event):
        print(event)

    def on_moved(self, event):
        self.catch_all_handler(event)

    def on_created(self, event):
        self.catch_all_handler(event)

    def on_deleted(self, event):
        self.catch_all_handler(event)

    def on_modified(self, event):
        self.frame_server.load_scene_module()

        with grpc.insecure_channel("localhost:50052") as channel:
            stub = renderserver_pb2_grpc.RenderServerStub(channel)
            try:
                self.frame_server.update_renderer_scene_data()
            except grpc._channel._InactiveRpcError:
                logger.warning("No frontend was detected at localhost:50052.")
                sp.Popen(config["webgl_renderer_path"])


class FrameServer(frameserver_pb2_grpc.FrameServerServicer):
    def __init__(self, server, input_file_path):
        self.server = server
        self.input_file_path = input_file_path
        self.exception = None
        self.load_scene_module()

        observer = Observer()
        event_handler = ScriptUpdateHandler(self)
        path = self.input_file_path
        observer.schedule(event_handler, path)
        observer.start()  # When / where to stop?

        try:
            self.update_renderer_scene_data()
        except grpc._channel._InactiveRpcError:
            logger.warning("No frontend was detected at localhost:50052.")
            try:
                sp.Popen(config["webgl_renderer_path"])
            except PermissionError:
                logger.info(WEBGL_RENDERER_INFO)
                self.server.stop(None)
                return

    def GetFrameAtTime(self, request, context):
        try:
            requested_scene_index = request.animation_index

            # Find the requested scene.
            scene_finished = False
            if requested_scene_index == request.end_index:
                scene_finished = True

            if (
                request.animation_offset
                <= self.keyframes[requested_scene_index].duration
            ):
                animation_offset = request.animation_offset
            else:
                if requested_scene_index + 1 < request.end_index:
                    requested_scene_index += 1
                    animation_offset = 0
                else:
                    scene_finished = True
                    animation_offset = self.keyframes[requested_scene_index].duration

            if requested_scene_index == self.previous_scene_index:
                requested_scene = self.previous_scene
                update_previous_scene = False
            else:
                requested_scene = copy.deepcopy(self.keyframes[requested_scene_index])
                update_previous_scene = True

            requested_scene.update_to_time(animation_offset)

            ids_to_remove = []
            mobjects_to_add = []
            animations = []
            updaters = []
            update_data = []
            # TODO: Only remove/add changed mobjects rather than all of them.
            if self.previous_scene is not None and (
                request.first_request or self.previous_scene != requested_scene
            ):
                previous_mobjects = extract_mobject_family_members(
                    self.previous_scene.mobjects, only_those_with_points=True
                )
                # Remove everything from the previous scene.
                ids_to_remove = [
                    mob.original_id
                    for mob in previous_mobjects
                    if not isinstance(mob, ValueTracker)
                ]

            if request.first_request or self.previous_scene != requested_scene:
                # Add everything from the requested scene.
                mobjects_to_add = [
                    serialize_mobject(mobject)
                    for mobject in extract_mobject_family_members(
                        requested_scene.mobjects, only_those_with_points=True
                    )
                    if not isinstance(mobject, ValueTracker)
                ]

                # Send animation and updater info.
                all_animations_tweened = True
                for animation in requested_scene.animations:
                    attribute_tween_data = generate_attribute_tween_data(animation)
                    mobject_tween_data_list = []
                    flickered_mobject_ids = []
                    if attribute_tween_data is None:
                        all_animations_tweened = False
                        flickered_mobject_ids = [
                            mob.original_id
                            for mob in extract_mobject_family_members(
                                animation.mobject, only_those_with_points=True
                            )
                        ]
                    else:
                        if animation.mobject is not None:
                            # Add offset vector to submobjects.
                            root_mobject_center = animation.mobject.get_center()
                            for updated_mobject in extract_mobject_family_members(
                                animation.mobject, only_those_with_points=True
                            ):
                                mobject_tween_data_list.append(
                                    frameserver_pb2.Animation.MobjectTweenData(
                                        id=updated_mobject.original_id,
                                        root_mobject_offset=updated_mobject.get_center()
                                        - root_mobject_center,
                                    )
                                )
                    animation_proto = frameserver_pb2.Animation(
                        name=animation.__class__.__name__,
                        duration=requested_scene.duration,
                        easing_function=animation.rate_func.__name__,
                        attribute_tween_data=attribute_tween_data,
                        mobject_tween_data=mobject_tween_data_list,
                        flickered_mobject_ids=flickered_mobject_ids,
                    )
                    animations.append(animation_proto)
                for (
                    updated_mobject,
                    updater_list,
                ) in requested_scene.mobject_updater_lists:
                    all_updaters_tweened = True
                    for updater in updater_list:
                        attribute_tween_data = generate_attribute_tween_data(updater)
                        if attribute_tween_data is None:
                            all_animations_tweened = False
                            all_updaters_tweened = False
                            updaters.append(
                                frameserver_pb2.Updater(
                                    flickered_mobject_ids=[
                                        mob.original_id
                                        for mob in extract_mobject_family_members(
                                            updated_mobject, only_those_with_points=True
                                        )
                                    ]
                                )
                            )
                            break
                        else:
                            raise NotImplementedError("Add tween data for updaters.")
                    if all_updaters_tweened:
                        # Append an updater with tween data.
                        pass
            else:
                all_animations_tweened = False
                for animation in requested_scene.animations:
                    # Only send update data for animations that don't have tween data.
                    if generate_attribute_tween_data(animation) is None:
                        update_data.extend(
                            [
                                serialize_mobject(mobject)
                                for mobject in extract_mobject_family_members(
                                    animation.mobject, only_those_with_points=True
                                )
                                if not isinstance(mobject, ValueTracker)
                            ]
                        )
                for (
                    updated_mobject,
                    updater_list,
                ) in requested_scene.mobject_updater_lists:
                    for updater in updater_list:
                        # Only send update data for updaters that don't have tween data.
                        if generate_attribute_tween_data(updater) is None:
                            update_data.extend(
                                [
                                    serialize_mobject(mobject)
                                    for mobject in extract_mobject_family_members(
                                        updated_mobject, only_those_with_points=True
                                    )
                                    if not isinstance(mobject, ValueTracker)
                                ]
                            )

            resp = frameserver_pb2.FrameResponse(
                frame_data=frameserver_pb2.FrameData(
                    remove=ids_to_remove, add=mobjects_to_add, update=update_data
                ),
                scene_finished=scene_finished,
                animations=animations,
                updaters=updaters,
                animation_index=requested_scene_index,
                animation_offset=animation_offset,
                all_animations_tweened=all_animations_tweened,
            )
            if update_previous_scene:
                self.previous_scene = requested_scene
                self.previous_scene_index = requested_scene_index
            return resp
        except Exception as e:
            traceback.print_exc()

    def FetchSceneData(self, request, context):
        try:
            request = frameserver_pb2.FetchSceneDataResponse(
                scene=frameserver_pb2.Scene(
                    name=str(self.scene),
                    animations=[
                        frameserver_pb2.Animation(
                            name=animations_to_name(scene.animations),
                            duration=scene.duration,
                        )
                        for scene in self.keyframes
                    ],
                ),
            )
            if hasattr(self.scene.camera, "background_color"):
                request.scene.background_color = self.scene.camera.background_color
            else:
                request.scene.background_color = "#000000"
            return request
        except Exception as e:
            traceback.print_exc()

    def load_scene_module(self):
        self.exception = None
        try:
            self.scene_class = scene_classes_from_file(
                self.input_file_path, require_single_scene=True
            )
            self.generate_keyframe_data()
        except Exception as e:
            self.exception = e

    def generate_keyframe_data(self):
        self.keyframes = []
        self.previous_scene_index = None
        self.previous_scene = None
        self.renderer = WebGLRenderer(self)
        self.scene = self.scene_class(self.renderer)
        self.scene.render()

    def update_renderer_scene_data(self):
        # If a javascript renderer is running, notify it of the scene being served. If
        # not, spawn one and it will request the scene when it starts.
        with grpc.insecure_channel("localhost:50052") as channel:
            stub = renderserver_pb2_grpc.RenderServerStub(channel)
            if not self.exception:
                request = renderserver_pb2.UpdateSceneDataRequest(
                    scene=renderserver_pb2.Scene(
                        name=str(self.scene),
                        animations=[
                            renderserver_pb2.Animation(
                                name=animations_to_name(scene.animations),
                                duration=scene.duration,
                            )
                            for scene in self.keyframes
                        ],
                    ),
                )
                if hasattr(self.scene.camera, "background_color"):
                    request.scene.background_color = self.scene.camera.background_color
                else:
                    request.scene.background_color = "#000000"
            else:
                lines = traceback.format_exception(
                    None, self.exception, self.exception.__traceback__
                )
                request = renderserver_pb2.UpdateSceneDataRequest(
                    has_exception=True, exception="\n".join(lines)
                )
            stub.UpdateSceneData(request)


def generate_attribute_tween_data(animation):
    if isinstance(animation, types.FunctionType):
        return None
    animation_name = animation.__class__.__name__
    if animation_name == "_MethodAnimation":
        tween_data_array = []
        for method in animation.methods:
            if method.__name__ in ["shift", "to_edge"]:
                tween_data_array.append(
                    frameserver_pb2.Animation.AttributeTweenData(
                        attribute="position",
                        start_data=animation.starting_mobject.get_center(),
                        end_data=animation.target_mobject.get_center(),
                    )
                )
            else:
                return None
        return tween_data_array
    elif animation_name == "FadeIn":
        return [
            frameserver_pb2.Animation.AttributeTweenData(
                attribute="fill_opacity",
                start_data=[animation.starting_mobject.fill_opacity],
                end_data=[animation.target_copy.fill_opacity],
            ),
            frameserver_pb2.Animation.AttributeTweenData(
                attribute="stroke_opacity",
                start_data=[animation.starting_mobject.stroke_opacity],
                end_data=[animation.target_copy.stroke_opacity],
            ),
        ]
    elif animation_name == "Wait":
        return []
    else:
        return None


def animations_to_name(animations):
    if len(animations) == 1:
        return str(animations[0].__class__.__name__)
    return f"{str(animations[0].__class__.__name__)}..."


def serialize_mobject(mobject):
    mob_proto = frameserver_pb2.MobjectData(id=mobject.original_id)

    if isinstance(mobject, VMobject):
        needs_redraw = False
        point_hash = hash(tuple(mobject.points.flatten()))
        if mobject.point_hash != point_hash:
            mobject.point_hash = point_hash
            needs_redraw = True
        mob_proto.vectorized_mobject_data.needs_redraw = needs_redraw

        for point in mobject.points:
            point_proto = mob_proto.vectorized_mobject_data.points.add()
            point_proto.x = point[0]
            point_proto.y = point[1]
            point_proto.z = point[2]

        mob_style = mobject.get_style(simple=True)
        mob_proto.style.fill_color = mob_style["fill_color"]
        mob_proto.style.fill_opacity = float(mob_style["fill_opacity"])
        mob_proto.style.stroke_color = mob_style["stroke_color"]
        mob_proto.style.stroke_opacity = float(mob_style["stroke_opacity"])
        mob_proto.style.stroke_width = float(mob_style["stroke_width"])
    elif isinstance(mobject, ImageMobject):
        mob_proto.type = frameserver_pb2.MobjectData.MobjectType.IMAGE_MOBJECT
        mob_style = mobject.get_style()
        mob_proto.style.fill_color = mob_style["fill_color"]
        mob_proto.style.fill_opacity = float(mob_style["fill_opacity"])
        assets_dir_path = str(config.get_dir("assets_dir"))
        if mobject.path.startswith(assets_dir_path):
            mob_proto.image_mobject_data.path = mobject.path[len(assets_dir_path) + 1 :]
        else:
            logger.info(
                f"Expected path {mobject.path} to be under the assets dir ({assets_dir_path})"
            )
        mob_proto.image_mobject_data.height = mobject.height
        mob_proto.image_mobject_data.width = mobject.width
        mob_center = mobject.get_center()
        mob_proto.image_mobject_data.center.x = mob_center[0]
        mob_proto.image_mobject_data.center.y = mob_center[1]
        mob_proto.image_mobject_data.center.z = mob_center[2]
    return mob_proto


def get(input_file_path):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    frameserver_pb2_grpc.add_FrameServerServicer_to_server(
        FrameServer(server, input_file_path), server
    )
    server.add_insecure_port("localhost:50051")
    return server
