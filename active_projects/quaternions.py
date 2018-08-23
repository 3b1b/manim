from big_ol_pile_of_manim_imports import *
# from pprint import pprint


# Constants
# HIGH_QUALITY = True
HIGH_QUALITY = False


# Helpers
def get_three_d_scene_config():
    hq_config = {
        "camera_config": {
            "should_apply_shading": True,
        },
        "three_d_axes_config": {
            "num_axis_pieces": 20,
            "number_line_config": {
                "unit_size": 2,
                "tick_frequency": 0.5,
                "numbers_with_elongated_ticks": [0, 1, 2],
            }
        },
        "sphere_config": {
            "radius": 1,
        }
    }
    lq_added_config = {
        "camera_config": {
            "should_apply_shading": False,
        },
        "three_d_axes_config": {
            "num_axis_pieces": 5,
        },
    }
    if HIGH_QUALITY:
        return hq_config
    else:
        return merge_config([
            lq_added_config,
            hq_config
        ])


def q_mult(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
    z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
    return np.array([w, x, y, z])


def stereo_project_point(point, axis=0, max_r=100):
    point = fdiv(point, point[axis] + 1)
    point[axis] = 0
    norm = get_norm(point)
    if norm > max_r:
        point *= max_r / norm
    return point


def stereo_project(mobject, axis=0, **kwargs):
    epsilon = 0.01
    for submob in mobject.family_members_with_points():
        eq_neg_1 = submob.points[:, axis] == -1
        if np.any(eq_neg_1):
            # Whoof, pretty messy, and not general.
            # Clean this up?
            N = len(eq_neg_1)
            neg_1_indices = np.arange(N)[eq_neg_1]

            if len(neg_1_indices) == 2:
                # Dumb hack
                submob.points = np.array([
                    *submob.points[3:-1],
                    *submob.points[0:4],
                ])
                eq_neg_1 = submob.points[:, axis] == -1
                neg_1_indices = np.arange(N)[eq_neg_1]

            i = neg_1_indices[0]
            p1 = interpolate(
                submob.points[i - 1],
                submob.points[i],
                1 - epsilon
            )
            p2 = interpolate(
                submob.points[i],
                submob.points[i + 1],
                epsilon
            )
            submob.points = np.array([
                *submob.points[:i],
                p1,
                interpolate(p1, p2, 1 / 3),
                interpolate(p1, p2, 2 / 3),
                p2,
                *submob.points[i + 1:],
            ])
        submob.apply_function(
            lambda p: stereo_project_point(
                p, axis=axis, **kwargs
            )
        )
    return mobject


# Abstract scenes
class SpecialThreeDScene(ThreeDScene):
    CONFIG = get_three_d_scene_config()

    def get_axes(self):
        return ThreeDAxes(**self.three_d_axes_config)

    def get_sphere(self):
        return Sphere(**self.sphere_config)


# Animated scenes
class Test(SpecialThreeDScene):
    CONFIG = {
        "sphere_config": {}
    }

    def construct(self):
        sphere = self.get_sphere()
        sphere.set_fill(opacity=0.5)
        axes = self.get_axes()
        cube = Cube()
        cube.set_depth(4)
        cube.set_fill(BLUE_E, opacity=1)

        sphere_shadow = sphere.deepcopy()
        sphere_shadow.add_updater(
            lambda ss: ss.become(
                stereo_project(sphere.deepcopy())
            )
        )

        self.add(axes)
        self.add(sphere)
        self.add(sphere_shadow)
        # self.add(cube)
        self.move_camera(
            phi=70 * DEGREES,
            theta=-45 * DEGREES,
            run_time=0
        )
        # self.begin_ambient_camera_rotation()
        self.play(
            Rotate(sphere, 180 * DEGREES, axis=UP),
            run_time=3,
        )
        self.wait()
