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
import ctypes
from ...utils.module_ops import (
    get_module,
    get_scene_classes_from_module,
    get_scenes_to_render,
)
from ... import logger
from ...constants import JS_RENDERER_INFO


class FrameServer(frameserver_pb2_grpc.FrameServerServicer):
    def animation_index_is_cached(self, animation_index):
        return animation_index < len(self.keyframes)

    def __init__(self, server, scene_class):
        self.server = server
        self.keyframes = []
        self.scene = scene_class(self)
        self.scene_thread = threading.Thread(
            target=lambda s: s.render(), args=(self.scene,)
        )
        self.previous_frame_animation_index = None
        self.scene_finished = False

        path = "./example_scenes/basic.py"
        event_handler = UpdateFrontendHandler(self)
        observer = Observer()
        observer.schedule(event_handler, path)
        observer.start()

        # If a javascript renderer is running, notify it of the scene being served. If
        # not, spawn one and it will request the scene when it starts.
        with grpc.insecure_channel("localhost:50052") as channel:
            stub = renderserver_pb2_grpc.RenderServerStub(channel)
            request = renderserver_pb2.NewSceneRequest(name=str(self.scene))
            try:
                stub.NewScene(request)
            except grpc._channel._InactiveRpcError:
                logger.warning(f"No frontend was detected at localhost:50052.")
                try:
                    sp.Popen(config["js_renderer_path"])
                except PermissionError:
                    logger.info(JS_RENDERER_INFO)
                    self.server.stop(None)
                    return

        self.scene_thread.start()

    def signal_pending_animation(self, animation_index):
        self.scene.start_animation = animation_index
        self.scene.animation_finished.set()
        return frameserver_pb2.FrameResponse(frame_pending=True)

    def GetFrameAtTime(self, request, context):
        selected_scene = None
        if self.animation_index_is_cached(request.animation_index):
            selected_scene = self.keyframes[request.animation_index]
        else:
            return self.signal_pending_animation(request.animation_index)

        # play() uses run_time and wait() uses duration TODO: Fix this inconsistency.
        # TODO: What about animations without a fixed duration?
        duration = (
            selected_scene.run_time
            if selected_scene.animations
            else selected_scene.duration
        )

        if request.animation_offset > duration:
            if self.animation_index_is_cached(request.animation_index + 1):
                # TODO: Clone scenes to allow reuse.
                selected_scene = self.keyframes[request.animation_index + 1]
            else:
                return self.signal_pending_animation(request.animation_index + 1)

        setattr(selected_scene, "camera", self.scene.camera)

        if selected_scene.animations:
            # This is a call to play().
            selected_scene.update_animation_to_time(request.animation_offset)
            selected_scene.update_frame(
                selected_scene.moving_mobjects,
                selected_scene.static_image,
            )
            serialized_mobject_list, duration = selected_scene.add_frame(
                selected_scene.renderer.get_frame()
            )
            resp = list_to_frame_response(
                selected_scene, duration, serialized_mobject_list
            )
            return resp
        else:
            # This is a call to wait().
            if selected_scene.should_update_mobjects():
                # TODO, be smart about setting a static image
                # the same way Scene.play does
                selected_scene.update_animation_to_time(time)
                selected_scene.update_frame()
                serialized_mobject_list, duration = selected_scene.add_frame(
                    selected_scene.get_frame()
                )
                frame_response = list_to_frame_response(
                    selected_scene, duration, serialized_mobject_list
                )
                if (
                    selected_scene.stop_condition is not None
                    and selected_scene.stop_condition()
                ):
                    selected_scene.animation_finished.set()
                    frame_response.frame_pending = True
                    selected_scene.renderer_waiting = True
                return frame_response
            elif selected_scene.renderer.skip_animations:
                # Do nothing
                return
            else:
                selected_scene.update_frame()
                dt = 1 / selected_scene.camera.frame_rate
                serialized_mobject_list, duration = selected_scene.add_frame(
                    selected_scene.get_frame(),
                    num_frames=int(selected_scene.duration / dt),
                )
                resp = list_to_frame_response(
                    selected_scene, duration, serialized_mobject_list
                )
                return resp

    def RendererStatus(self, request, context):
        response = frameserver_pb2.RendererStatusResponse()
        response.scene_name = str(self.scene)
        return response

    # def UpdateSceneLocation(self, request, context):
    #     # Reload self.scene.
    #     print(scene_classes_to_render)

    #     response = frameserver_pb2.SceneLocationResponse()
    #     return response


def list_to_frame_response(scene, duration, serialized_mobject_list):
    response = frameserver_pb2.FrameResponse()
    response.frame_pending = False
    response.duration = duration

    for mob_serialization in serialized_mobject_list:
        mob_proto = response.mobjects.add()
        mob_proto.id = mob_serialization["id"]
        mob_proto.needs_redraw = mob_serialization["needs_redraw"]
        for point in mob_serialization["points"]:
            point_proto = mob_proto.points.add()
            point_proto.x = point[0]
            point_proto.y = point[1]
            point_proto.z = point[2]
        mob_proto.style.fill_color = mob_serialization["style"]["fill_color"]
        mob_proto.style.fill_opacity = float(mob_serialization["style"]["fill_opacity"])
        mob_proto.style.stroke_color = mob_serialization["style"]["stroke_color"]
        mob_proto.style.stroke_opacity = float(
            mob_serialization["style"]["stroke_opacity"]
        )
        mob_proto.style.stroke_width = float(mob_serialization["style"]["stroke_width"])
    return response


class UpdateFrontendHandler(FileSystemEventHandler):
    """Logs all the events captured."""

    def __init__(self, frame_server):
        super().__init__()
        self.frame_server = frame_server

    def on_moved(self, event):
        super().on_moved(event)
        raise NotImplementedError("Update not implemented for moved files.")

    def on_deleted(self, event):
        super().on_deleted(event)
        raise NotImplementedError("Update not implemented for deleted files.")

    def on_modified(self, event):
        super().on_modified(event)
        module = get_module(config["input_file"])
        all_scene_classes = get_scene_classes_from_module(module)
        scene_classes_to_render = get_scenes_to_render(all_scene_classes)
        scene_class = scene_classes_to_render[0]

        # Get the old thread's ID.
        old_thread_id = None
        old_thread = self.frame_server.scene_thread
        if hasattr(old_thread, "_thread_id"):
            old_thread_id = old_thread._thread_id
        if old_thread_id is None:
            for thread_id, thread in threading._active.items():
                if thread is old_thread:
                    old_thread_id = thread_id

        # Stop the old thread.
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            old_thread_id, ctypes.py_object(SystemExit)
        )
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(old_thread_id, 0)
            print("Exception raise failure")
        old_thread.join()

        # Start a new thread.
        self.frame_server.initialize_scene(scene_class, start_animation=1)
        self.frame_server.scene.reached_start_animation.wait()

        # Serialize data on Animations up to the target one.
        animations = []
        for scene in self.frame_server.keyframes:
            if scene.animations:
                animation_duration = scene.run_time
                if len(scene.animations) == 1:
                    animation_name = str(scene.animations[0])
                else:
                    animation_name = f"{str(scene.animations[0])}..."
            else:
                animation_duration = scene.duration
                animation_name = "Wait"
            animations.append(
                renderserver_pb2.Animation(
                    name=animation_name,
                    duration=animation_duration,
                )
            )

        # Reset the renderer.
        with grpc.insecure_channel("localhost:50052") as channel:
            stub = renderserver_pb2_grpc.RenderServerStub(channel)
            request = renderserver_pb2.ManimStatusRequest(
                scene_name=str(self.frame_server.scene), animations=animations
            )
            try:
                stub.ManimStatus(request)
            except grpc._channel._InactiveRpcError:
                sp.Popen(config["js_renderer_path"])


def get(scene_class):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    frameserver_pb2_grpc.add_FrameServerServicer_to_server(
        FrameServer(server, scene_class), server
    )
    server.add_insecure_port("localhost:50051")
    return server
