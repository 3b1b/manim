import numpy as np

from manimlib.animation.creation import ShowCreation
from manimlib.animation.fading import FadeOut
from manimlib.animation.transform import ApplyMethod
from manimlib.animation.transform import Transform
from manimlib.constants import *
from manimlib.mobject.geometry import Circle
from manimlib.mobject.geometry import Line
from manimlib.mobject.matrix import Matrix
from manimlib.mobject.svg.tex_mobject import TexMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.scene.scene import Scene


class NumericalMatrixMultiplication(Scene):
    CONFIG = {
        "left_matrix": [[1, 2], [3, 4]],
        "right_matrix": [[5, 6], [7, 8]],
        "use_parens": True,
    }

    def construct(self):
        left_string_matrix, right_string_matrix = [
            np.array(matrix).astype("string")
            for matrix in (self.left_matrix, self.right_matrix)
        ]
        if right_string_matrix.shape[0] != left_string_matrix.shape[1]:
            raise Exception("Incompatible shapes for matrix multiplication")

        left = Matrix(left_string_matrix)
        right = Matrix(right_string_matrix)
        result = self.get_result_matrix(
            left_string_matrix, right_string_matrix
        )

        self.organize_matrices(left, right, result)
        self.animate_product(left, right, result)

    def get_result_matrix(self, left, right):
        (m, k), n = left.shape, right.shape[1]
        mob_matrix = np.array([VGroup()]).repeat(m * n).reshape((m, n))
        for a in range(m):
            for b in range(n):
                template = "(%s)(%s)" if self.use_parens else "%s%s"
                parts = [
                    prefix + template % (left[a][c], right[c][b])
                    for c in range(k)
                    for prefix in ["" if c == 0 else "+"]
                ]
                mob_matrix[a][b] = TexMobject(parts, next_to_buff=0.1)
        return Matrix(mob_matrix)

    def add_lines(self, left, right):
        line_kwargs = {
            "color": BLUE,
            "stroke_width": 2,
        }
        left_rows = [
            VGroup(*row) for row in left.get_mob_matrix()
        ]
        h_lines = VGroup()
        for row in left_rows[:-1]:
            h_line = Line(row.get_left(), row.get_right(), **line_kwargs)
            h_line.next_to(row, DOWN, buff=left.v_buff / 2.)
            h_lines.add(h_line)

        right_cols = [
            VGroup(*col) for col in np.transpose(right.get_mob_matrix())
        ]
        v_lines = VGroup()
        for col in right_cols[:-1]:
            v_line = Line(col.get_top(), col.get_bottom(), **line_kwargs)
            v_line.next_to(col, RIGHT, buff=right.h_buff / 2.)
            v_lines.add(v_line)

        self.play(ShowCreation(h_lines))
        self.play(ShowCreation(v_lines))
        self.wait()
        self.show_frame()

    def organize_matrices(self, left, right, result):
        equals = TexMobject("=")
        everything = VGroup(left, right, equals, result)
        everything.arrange()
        everything.set_width(FRAME_WIDTH - 1)
        self.add(everything)

    def animate_product(self, left, right, result):
        l_matrix = left.get_mob_matrix()
        r_matrix = right.get_mob_matrix()
        result_matrix = result.get_mob_matrix()
        circle = Circle(
            radius=l_matrix[0][0].get_height(),
            color=GREEN
        )
        circles = VGroup(*[
            entry.get_point_mobject()
            for entry in (l_matrix[0][0], r_matrix[0][0])
        ])
        (m, k), n = l_matrix.shape, r_matrix.shape[1]
        for mob in result_matrix.flatten():
            mob.set_color(BLACK)
        lagging_anims = []
        for a in range(m):
            for b in range(n):
                for c in range(k):
                    l_matrix[a][c].set_color(YELLOW)
                    r_matrix[c][b].set_color(YELLOW)
                for c in range(k):
                    start_parts = VGroup(
                        l_matrix[a][c].copy(),
                        r_matrix[c][b].copy()
                    )
                    result_entry = result_matrix[a][b].split()[c]

                    new_circles = VGroup(*[
                        circle.copy().shift(part.get_center())
                        for part in start_parts.split()
                    ])
                    self.play(Transform(circles, new_circles))
                    self.play(
                        Transform(
                            start_parts,
                            result_entry.copy().set_color(YELLOW),
                            path_arc=-np.pi / 2,
                            lag_ratio=0,
                        ),
                        *lagging_anims
                    )
                    result_entry.set_color(YELLOW)
                    self.remove(start_parts)
                    lagging_anims = [
                        ApplyMethod(result_entry.set_color, WHITE)
                    ]

                for c in range(k):
                    l_matrix[a][c].set_color(WHITE)
                    r_matrix[c][b].set_color(WHITE)
        self.play(FadeOut(circles), *lagging_anims)
        self.wait()
