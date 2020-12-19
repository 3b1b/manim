import copy


class JsRenderer:
    def __init__(self, frame_server):
        self.skip_animations = True
        self.frame_server = frame_server
        self.camera = JsCamera()
        self.num_plays = 0

    def init_scene(self, scene):
        pass

    def scene_finished(self, scene):
        pass

    def play(self, scene, *args, **kwargs):
        self.num_plays += 1
        s = scene.compile_animation_data(*args, skip_rendering=True, **kwargs)
        scene_copy = copy.deepcopy(scene)
        scene_copy.renderer = self
        self.frame_server.keyframes.append(scene_copy)
        if s is None:
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


class JsCamera:
    def __init__(self, use_z_index=True):
        self.use_z_index = use_z_index
