from . import scene
from ..camera.camera import Camera
from ..camera.js_camera import JsCamera
from .. import config
from ..grpc.gen import renderserver_pb2
from ..grpc.gen import renderserver_pb2_grpc
from ..grpc.impl.frame_server_impl import FrameServer
from ..mobject.mobject import Mobject
from ..constants import DEFAULT_WAIT_TIME
from threading import Event
import copy
import grpc
import inspect
import random
import string
import types
from .. import logger


def get_random_name(name_map):
    while True:
        random_name = "".join(random.sample(string.ascii_lowercase, k=10))
        if random_name not in name_map:
            return random_name


class JsScene(scene.Scene):
    def __init__(self, frame_server):
        super().__init__(camera_class=JsCamera)
        self.frame_server = frame_server
        self.start_animation = 0
        self.reached_start_animation = Event()
        self.animation_finished = Event()
        self.renderer_waiting = False

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if type(v) in [FrameServer, Event, Camera]:
                continue
            setattr(result, k, copy.deepcopy(v, memo))

        # Update updaters
        for mobject in self.mobjects:
            cloned_updaters = []
            for updater in mobject.updaters:
                # Make the cloned updater use the cloned Mobjects as free variables
                # rather than the original ones.
                # TODO: The the same for function calls recursively.
                free_variable_map = inspect.getclosurevars(updater).nonlocals
                cloned_co_freevars = []
                cloned_closure = []
                for i, free_variable_name in enumerate(updater.__code__.co_freevars):
                    free_variable_value = free_variable_map[free_variable_name]
                    if isinstance(free_variable_value, Mobject):
                        random_name = get_random_name(free_variable_map)

                        # Put the cloned Mobject in the function's scope.
                        free_variable_map[random_name] = memo[id(free_variable_value)]

                        # Add the cloned Mobject's name to the free variable list.
                        cloned_co_freevars.append(random_name)

                        # Add a cell containing the cloned Mobject's reference to the
                        # closure list.
                        cloned_closure.append(
                            types.CellType(memo[id(free_variable_value)])
                        )
                    else:
                        cloned_co_freevars.append(free_variable_name)
                        cloned_closure.append(updater.__closure__[i])

                cloned_updater = types.FunctionType(
                    updater.__code__.replace(co_freevars=tuple(cloned_co_freevars)),
                    updater.__globals__,
                    updater.__name__,
                    updater.__defaults__,
                    tuple(cloned_closure),
                )
                cloned_updaters.append(cloned_updater)
            memo[id(mobject)].updaters = cloned_updaters
        return result

    def render(self):
        try:
            self.construct()
        except scene.EndSceneEarlyException:
            pass

        self.frame_server.scene_finished = True
        with grpc.insecure_channel("localhost:50052") as channel:
            stub = renderserver_pb2_grpc.RenderServerStub(channel)
            try:
                stub.SceneFinished(renderserver_pb2.EmptyRequest())
            except grpc._channel._InactiveRpcError as e:
                logger.error(e)

    def progress_through_animations(self):
        self.frame_server.keyframes.append(copy.deepcopy(self))
        self.animation_finished.clear()
        if self.num_plays == self.start_animation:
            with grpc.insecure_channel("localhost:50052") as channel:
                stub = renderserver_pb2_grpc.RenderServerStub(channel)
                try:
                    stub.AnimationStatus(renderserver_pb2.EmptyRequest())
                except grpc._channel._InactiveRpcError as e:
                    logger.error(e)
            self.animation_finished.wait()

    def wait(self, duration=DEFAULT_WAIT_TIME, stop_condition=None):
        self.update_mobjects(dt=0)  # Any problems with this?
        self.animations = []
        self.duration = duration
        self.stop_condition = stop_condition
        self.last_t = 0

        self.frame_server.keyframes.append(copy.deepcopy(self))
        self.animation_finished.clear()
        if self.num_plays == self.start_animation:
            with grpc.insecure_channel("localhost:50052") as channel:
                stub = renderserver_pb2_grpc.RenderServerStub(channel)
                try:
                    stub.AnimationStatus(renderserver_pb2.EmptyRequest())
                except grpc._channel._InactiveRpcError as e:
                    logger.error(e)
            self.animation_finished.wait()

    def add_frame(self, serialized_frame, num_frames=1):
        dt = 1 / self.camera.frame_rate
        self.increment_time(num_frames * dt)
        if num_frames != 1:
            duration = num_frames / self.camera.frame_rate
        else:
            duration = 0
        return self.camera.serialized_frame, duration

    def get_frame(self):
        return self.camera.serialized_frame


if config["use_js_renderer"]:
    scene.Scene = JsScene
