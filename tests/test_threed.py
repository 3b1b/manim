from manim import *


class CubeTest(ThreeDScene):
    def construct(self):
        self.play(Animation(Cube()))


class SphereTest(ThreeDScene):
    def construct(self):
        self.play(Animation(Sphere()))


class AxesTest(ThreeDScene):
    def construct(self):
        self.play(Animation(ThreeDAxes()))


class CameraMoveTest(ThreeDScene):
    def construct(self):
        cube = Cube()
        self.play(Animation(cube))
        self.move_camera(phi=PI/4, theta=PI/4)


class AmbientCameraMoveTest(ThreeDScene):
    def construct(self):
        cube = Cube()
        self.begin_ambient_camera_rotation(rate=0.5)
        self.play(Animation(cube))


def test_scenes(get_config_test, Tester):
    CONFIG = get_config_test
    module_name = os.path.splitext(os.path.basename(__file__))[
        0].replace('test_', '')
    for _, scene_tested in inspect.getmembers(sys.modules[__name__], lambda m: inspect.isclass(m) and m.__module__ == __name__):
        Tester(scene_tested, CONFIG, module_name).test()
