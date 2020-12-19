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
from ...utils.module_ops import (
    get_module,
    get_scene_classes_from_module,
    get_scenes_to_render,
    scene_classes_from_file,
)
from ... import logger
from ...constants import JS_RENDERER_INFO
from ...renderer.js_renderer import JsRenderer
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
                sp.Popen(config["js_renderer_path"])


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
                sp.Popen(config["js_renderer_path"])
            except PermissionError:
                logger.info(JS_RENDERER_INFO)
                self.server.stop(None)
                return

    def GetFrameAtTime(self, request, context):
        try:
            # Determine start and end indices.
            if (
                request.preview_mode
                == frameserver_pb2.FrameRequest.PreviewMode.ANIMATION_RANGE
            ):
                requested_scene_index = request.start_index
            elif request.preview_mode == frameserver_pb2.FrameRequest.PreviewMode.ALL:
                requested_scene_index = 0
            elif request.preview_mode == frameserver_pb2.FrameRequest.PreviewMode.IMAGE:
                requested_scene_index = request.image_index

            if (
                request.preview_mode
                == frameserver_pb2.FrameRequest.PreviewMode.ANIMATION_RANGE
                and request.end_index > request.start_index
            ):
                requested_end_index = request.end_index
            elif request.preview_mode == frameserver_pb2.FrameRequest.PreviewMode.ALL:
                requested_end_index = len(self.keyframes)
            elif request.preview_mode == frameserver_pb2.FrameRequest.PreviewMode.IMAGE:
                requested_end_index = len(self.keyframes)

            # Find the requested scene.
            requested_scene = self.keyframes[requested_scene_index]
            requested_scene_end_time = requested_scene.duration
            scene_finished = False
            while requested_scene_end_time < request.time_offset:
                if requested_scene_index + 1 < requested_end_index:
                    requested_scene_index += 1
                    requested_scene = self.keyframes[requested_scene_index]
                    requested_scene_end_time += requested_scene.duration
                else:
                    scene_finished = True
                    break

            if requested_scene_index == self.previous_scene_index:
                requested_scene = self.previous_scene
            else:
                requested_scene = copy.deepcopy(requested_scene)
                self.previous_scene = requested_scene
                self.previous_scene_index = requested_scene_index

            # Update to the requested time.
            if not scene_finished:
                requested_scene_start_time = (
                    requested_scene_end_time - requested_scene.duration
                )
                animation_offset = request.time_offset - requested_scene_start_time
            else:
                animation_offset = requested_scene.duration
            requested_scene.update_to_time(animation_offset)

            # Serialize the scene's mobjects.
            mobjects = extract_mobject_family_members(
                requested_scene.mobjects, only_those_with_points=True
            )
            serialized_mobjects = [
                serialize_mobject(mobject)
                for mobject in mobjects
                if not isinstance(mobject, ValueTracker)
            ]

            resp = frameserver_pb2.FrameResponse(
                mobjects=serialized_mobjects,
                frame_pending=False,
                animation_finished=False,
                scene_finished=scene_finished
                or request.preview_mode
                == frameserver_pb2.FrameRequest.PreviewMode.IMAGE,
                duration=requested_scene.duration,
                animations=map(
                    lambda anim: anim.__class__.__name__, requested_scene.animations
                ),
                animation_index=requested_scene_index,
                animation_offset=animation_offset,
            )
            return resp
        except Exception as e:
            traceback.print_exc()

    def FetchSceneData(self, request, context):
        try:
            return frameserver_pb2.FetchSceneDataResponse(
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
        self.renderer = JsRenderer(self)
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
            else:
                lines = traceback.format_exception(
                    None, self.exception, self.exception.__traceback__
                )
                request = renderserver_pb2.UpdateSceneDataRequest(
                    has_exception=True, exception="\n".join(lines)
                )
            stub.UpdateSceneData(request)


def animations_to_name(animations):
    if len(animations) == 1:
        return str(animations[0].__class__.__name__)
    return f"{str(animations[0])}..."


def serialize_mobject(mobject):
    mob_proto = frameserver_pb2.MobjectData()

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

        mob_proto.id = id(mobject)
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
        mob_proto.image_mobject_data.height = mobject.get_height()
        mob_proto.image_mobject_data.width = mobject.get_width()
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
