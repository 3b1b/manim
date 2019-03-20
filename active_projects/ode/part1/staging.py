from big_ol_pile_of_manim_imports import *


def pendulum_vector_field(point, mu=0.1, g=9.8, L=3):
    theta, omega = point[:2]
    return np.array([
        omega,
        -np.sqrt(g / L) * np.sin(theta) - mu * omega,
        0,
    ])


# Scenes

class VectorFieldTest(Scene):
    def construct(self):
        plane = NumberPlane(
            # axis_config={"unit_size": 2}
        )
        mu_tracker = ValueTracker(1)
        field = VectorField(
            lambda p: pendulum_vector_field(
                plane.point_to_coords(p),
                mu=mu_tracker.get_value()
            ),
            delta_x=0.5,
            delta_y=0.5,
            max_magnitude=4,
            opacity=0.5,
            # length_func=lambda norm: norm,
        )
        stream_lines = StreamLines(
            field.func,
            delta_x=0.5,
            delta_y=0.5,
        )
        animated_stream_lines = AnimatedStreamLines(
            stream_lines,
            line_anim_class=ShowPassingFlashWithThinningStrokeWidth,
        )

        self.add(plane, field, animated_stream_lines)
        self.wait(10)


class NewSceneName(Scene):
    def construct(self):
        pass
