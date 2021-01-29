import copy
from ..utils.family import extract_mobject_family_members
from manim import config


class WebGLRenderer:
    def __init__(self, frame_server):
        self.skip_animations = True
        self.frame_server = frame_server
        self.camera = WebGLCamera()
        self.num_plays = 0

    def init_scene(self, scene):
        pass

    def scene_finished(self, scene):
        pass

    def play(self, scene, *args, **kwargs):
        self.num_plays += 1
        # If the scene contains an updater it must be updated frame by frame.
        for mob in extract_mobject_family_members(scene.mobjects):
            if len(mob.updaters) > 0:
                self.skip_animations = False
                break
        s = scene.compile_animation_data(*args, skip_rendering=True, **kwargs)
        self.skip_animations = True

        scene_copy = copy.deepcopy(scene)
        scene_copy.renderer = self
        self.frame_server.keyframes.append(scene_copy)
        if s is None:
            # Nothing happens in this animation, so there's no need to update it.
            scene_copy.is_static = True
        else:
            scene_copy.is_static = False
            scene.play_internal(skip_rendering=True)

    def update_frame(  # TODO Description in Docstring
        self,
        scene,
        mobjects=None,
        include_submobjects=True,
        ignore_skipping=True,
        **kwargs,
    ):
        pass

    def save_static_frame_data(self, scene, static_mobjects):
        pass

    def add_frame(self, frame, num_frames=1):
        pass

    def get_frame(self):
        pass


class WebGLCamera:
    def __init__(self, use_z_index=True):
        self.use_z_index = use_z_index
        self.frame_rate = config["webgl_updater_fps"]
