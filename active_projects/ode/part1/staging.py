from big_ol_pile_of_manim_imports import *


def pendulum_vector_field(point, mu=0.1, g=9.8, L=3):
    theta, omega, z = point
    return np.array([
        omega,
        -np.sqrt(g / L) * np.sin(theta) - mu * omega,
        0,
    ])


class VectorFieldTest(Scene):
    def construct(self):
        plane = NumberPlane(
            # axis_config={"unit_size": 2}
        )
        field = VectorField(
            lambda p: pendulum_vector_field(
                [*plane.point_to_coords(p), 0],
                mu=0.1
            ),
            max_magnitude=4,
            # length_func=lambda norm: norm,
        )

        self.add(plane, field)
