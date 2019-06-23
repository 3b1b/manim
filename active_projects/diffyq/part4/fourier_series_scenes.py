from manimlib.imports import *

from active_projects.diffyq.part2.fourier_series import FourierOfTrebleClef


class ComplexFourierSeriesExample(FourierOfTrebleClef):
    CONFIG = {
        "file_name": "EighthNote",
        "run_time": 10,
        "n_vectors": 200,
        "n_cycles": 2,
        "max_circle_stroke_width": 0.75,
        "drawing_height": 5,
        "center_point": DOWN,
        "top_row_y": 3,
        "top_row_label_y": 2,
        "top_row_x_spacing": 1.75,
        "top_row_copy_scale_factor": 0.9,
        "start_drawn": False,
    }

    def construct(self):
        self.add_vectors_circles_path()
        self.add_top_row(self.vectors, self.circles)
        self.write_title()
        self.highlight_vectors_one_by_one()
        self.change_shape()

    def write_title(self):
        title = TextMobject("Complex\\\\Fourier series")
        title.scale(1.5)
        title.to_edge(LEFT)
        title.match_y(self.path)

        self.wait(5)
        self.play(FadeInFromDown(title))
        self.wait(2)
        self.title = title

    def highlight_vectors_one_by_one(self):
        # Don't know why these vectors can't get copied.
        # That seems like a problem that will come up again.
        labels = self.top_row[-1]
        next_anims = []
        for vector, circle, label in zip(self.vectors, self.circles, labels):
            # v_color = vector.get_color()
            c_color = circle.get_color()
            c_stroke_width = circle.get_stroke_width()

            rect = SurroundingRectangle(label, color=PINK)
            self.play(
                # vector.set_color, PINK,
                circle.set_stroke, RED, 3,
                FadeIn(rect),
                *next_anims
            )
            self.wait()
            next_anims = [
                # vector.set_color, v_color,
                circle.set_stroke, c_color, c_stroke_width,
                FadeOut(rect),
            ]
        self.play(*next_anims)

    def change_shape(self):
        # path_mob = TexMobject("\\pi")
        path_mob = SVGMobject("Nail_And_Gear")
        new_path = path_mob.family_members_with_points()[0]
        new_path.set_height(4)
        new_path.move_to(self.path, DOWN)
        new_path.shift(0.5 * UP)

        self.transition_to_alt_path(new_path)
        for n in range(self.n_cycles):
            self.run_one_cycle()

    def transition_to_alt_path(self, new_path, morph_path=False):
        new_coefs = self.get_coefficients_of_path(new_path)
        new_vectors = self.get_rotating_vectors(
            coefficients=new_coefs
        )
        new_drawn_path = self.get_drawn_path(new_vectors)

        self.vector_clock.suspend_updating()

        vectors = self.vectors
        anims = []

        for vect, new_vect in zip(vectors, new_vectors):
            new_vect.update()
            new_vect.clear_updaters()

            line = Line(stroke_width=0)
            line.put_start_and_end_on(*vect.get_start_and_end())
            anims.append(ApplyMethod(
                line.put_start_and_end_on,
                *new_vect.get_start_and_end()
            ))
            vect.freq = new_vect.freq
            vect.phase = new_vect.phase
            vect.coefficient = new_vect.coefficient

            vect.line = line
            vect.add_updater(
                lambda v: v.put_start_and_end_on(
                    *v.line.get_start_and_end()
                )
            )
        if morph_path:
            anims.append(
                ReplacementTransform(
                    self.drawn_path,
                    new_drawn_path
                )
            )
        else:
            anims.append(
                FadeOut(self.drawn_path)
            )

        self.play(*anims, run_time=3)
        for vect in self.vectors:
            vect.remove_updater(vect.updaters[-1])

        if not morph_path:
            self.add(new_drawn_path)
            self.vector_clock.set_value(0)

        self.vector_clock.resume_updating()
        self.drawn_path = new_drawn_path

    #
    def get_path(self):
        path = super().get_path()
        path.set_height(self.drawing_height)
        path.to_edge(DOWN)
        return path

    def add_top_row(self, vectors, circles, max_freq=3):
        self.top_row = self.get_top_row(
            vectors, circles, max_freq
        )
        self.add(self.top_row)

    def get_top_row(self, vectors, circles, max_freq=3):
        vector_copies = VGroup()
        circle_copies = VGroup()
        for vector, circle in zip(vectors, circles):
            if vector.freq > max_freq:
                break
            vcopy = vector.copy()
            vcopy.clear_updaters()
            ccopy = circle.copy()
            ccopy.clear_updaters()
            ccopy.original = circle
            vcopy.original = vector

            vcopy.center_point = np.array([
                vector.freq * self.top_row_x_spacing,
                self.top_row_y,
                0
            ])
            ccopy.center_point = vcopy.center_point
            vcopy.add_updater(self.update_top_row_vector_copy)
            ccopy.add_updater(self.update_top_row_circle_copy)
            vector_copies.add(vcopy)
            circle_copies.add(ccopy)

        dots = VGroup(*[
            TexMobject("\\dots").next_to(
                circle_copies, direction,
                MED_LARGE_BUFF,
            )
            for direction in [LEFT, RIGHT]
        ])
        labels = self.get_top_row_labels(vector_copies)
        return VGroup(
            vector_copies,
            circle_copies,
            dots,
            labels,
        )

    def update_top_row_vector_copy(self, vcopy):
        vcopy.become(vcopy.original)
        vcopy.scale(self.top_row_copy_scale_factor)
        vcopy.shift(vcopy.center_point - vcopy.get_start())
        return vcopy

    def update_top_row_circle_copy(self, ccopy):
        ccopy.become(ccopy.original)
        ccopy.scale(self.top_row_copy_scale_factor)
        ccopy.move_to(ccopy.center_point)
        return ccopy

    def get_top_row_labels(self, vector_copies):
        labels = VGroup()
        for vector_copy in vector_copies:
            freq = vector_copy.freq
            label = Integer(freq)
            label.move_to(np.array([
                freq * self.top_row_x_spacing,
                self.top_row_label_y,
                0
            ]))
            labels.add(label)
        return labels


class PiFourierSeries(ComplexFourierSeriesExample):
    CONFIG = {
        "n_vectors": 101,
        "max_circle_stroke_width": 1,
        "top_row_copy_scale_factor": 0.6,
    }

    def construct(self):
        self.setup_plane()
        self.add_vectors_circles_path()
        self.add_top_row(self.vectors, self.circles)

        for n in range(self.n_cycles):
            self.run_one_cycle()

    def setup_plane(self):
        plane = ComplexPlane(
            axis_config={"unit_size": 2},
            y_min=-1.25,
            y_max=1.25,
            x_min=-2.5,
            x_max=2.5,
            background_line_style={
                "stroke_width": 1,
                "stroke_color": LIGHT_GREY,
            },
        )
        plane.shift(self.center_point)
        # plane.fade(0.5)
        plane.add_coordinates()

        top_rect = Rectangle(
            width=FRAME_WIDTH,
            fill_color=BLACK,
            fill_opacity=1,
            stroke_width=0,
            height=2.5
        )
        top_rect.to_edge(UP, buff=0)

        self.plane = plane
        self.add(plane)
        self.add(top_rect)

    def get_path(self):
        pi = TexMobject("\\pi")
        path = pi.family_members_with_points()[0]
        path.set_height(3.5)
        path.move_to(3 * DOWN, DOWN)
        path.set_stroke(YELLOW, 0)
        path.set_fill(opacity=0)
        return path


class RealValuedFunctionFourierSeries(PiFourierSeries):
    CONFIG = {
        "n_vectors": 101,
        "start_drawn": True,
    }

    def construct(self):
        self.setup_plane()
        self.add_vectors_circles_path()
        self.add_top_row(self.vectors, self.circles)

        self.flatten_path()
        self.focus_on_vector_pair()

    def flatten_path(self):
        new_path = self.path.copy()
        new_path.stretch(0, 1)
        new_path.set_y(self.plane.n2p(0)[1])
        self.vector_clock.set_value(10)
        self.transition_to_alt_path(new_path, morph_path=True)
        self.run_one_cycle()

    def focus_on_vector_pair(self):
        vectors = self.vectors
        circles = self.circles
        top_row = self.top_row
        top_vectors, top_circles, dots, labels = top_row

        rects1, rects2, rects3 = [
            VGroup(*[
                SurroundingRectangle(VGroup(
                    top_circles[i],
                    labels[i],
                ))
                for i in pair
            ]).set_stroke(LIGHT_GREY, 2)
            for pair in [(1, 2), (3, 4), (5, 6)]
        ]

        def get_opacity_animation(i1, i2, alpha_func):
            v_group = vectors[i1:i2]
            c_group = circles[i1:i2]
            return AnimationGroup(
                UpdateFromAlphaFunc(
                    VectorizedPoint(),
                    lambda m, a: v_group.set_opacity(
                        alpha_func(a)
                    )
                ),
                UpdateFromAlphaFunc(
                    VectorizedPoint(),
                    lambda m, a: c_group.set_stroke(
                        opacity=alpha_func(a)
                    )
                ),
            )

        self.remove(self.path)
        self.play(
            get_opacity_animation(
                3, len(vectors), lambda a: smooth(1 - a),
            ),
            ShowCreation(rects1, lag_ratio=0.3),
        )
        for n in range(2):
            self.run_one_cycle()

        self.play(
            get_opacity_animation(3, 5, smooth),
            get_opacity_animation(
                0, 3,
                lambda a: 1 - 0.75 * smooth(a)
            ),
            ReplacementTransform(rects1, rects2),
        )
        self.run_one_cycle()
        self.play(
            get_opacity_animation(5, 7, smooth),
            get_opacity_animation(
                3, 5,
                lambda a: 1 - 0.75 * smooth(a)
            ),
            ReplacementTransform(rects2, rects3),
        )
        self.run_one_cycle()
        self.run_one_cycle()


# Pure fourier series with zooming.
# Note to self, put out a single video with nothing
# but these?

class FourierSeriesExampleWithRectForZoom(ComplexFourierSeriesExample):
    CONFIG = {
        "n_vectors": 100,
        "slow_factor": 0.01,
        "rect_scale_factor": 0.1,
        "start_drawn": True,
        "drawing_height": 7,
    }

    def construct(self):
        self.add_vectors_circles_path()
        self.circles.set_stroke(opacity=0.5)
        rect = self.get_rect()
        rect.set_height(self.rect_scale_factor * FRAME_HEIGHT)
        rect.add_updater(lambda m: m.move_to(
            self.get_rect_center()
        ))
        self.add(rect)
        self.run_one_cycle()

    def get_rect_center(self):
        return center_of_mass([
            v.get_end()
            for v in self.vectors
        ])

    def get_rect(self):
        return ScreenRectangle(
            color=BLUE,
            stroke_width=1,
        )

    def get_path_end(self, vectors, stroke_width=None, **kwargs):
        if stroke_width is None:
            stroke_width = self.drawn_path_st
        full_path = self.get_vector_sum_path(vectors, **kwargs)
        path = VMobject()
        path.set_stroke(
            self.drawn_path_color,
            stroke_width
        )

        def update_path(p):
            alpha = self.get_vector_time() % 1
            p.pointwise_become_partial(
                full_path,
                np.clip(alpha - 0.01, 0, 1),
                np.clip(alpha, 0, 1),
            )
            p.points[-1] = vectors[-1].get_end()

        path.add_updater(update_path)
        return path

    def get_drawn_path_alpha(self):
        return super().get_drawn_path_alpha() - 0.002

    def get_drawn_path(self, vectors, stroke_width=2, **kwargs):
        odp = super().get_drawn_path(vectors, stroke_width, **kwargs)
        return VGroup(
            odp,
            self.get_path_end(vectors, stroke_width, **kwargs),
        )


class ZoomedInFourierSeriesExample(FourierSeriesExampleWithRectForZoom, MovingCameraScene):
    CONFIG = {
        "vector_config": {
            "max_tip_length_to_length_ratio": 0.15,
            "tip_length": 0.05,
        },
        "parametric_function_step_size": 0.001,
    }

    def setup(self):
        ComplexFourierSeriesExample.setup(self)
        MovingCameraScene.setup(self)

    def get_rect(self):
        return self.camera_frame

    def add_vectors_circles_path(self):
        super().add_vectors_circles_path()
        for v in self.vectors:
            if v.get_stroke_width() < 1:
                v.set_stroke(width=1)


class ZoomedInFourierSeriesExample10xMore(ZoomedInFourierSeriesExample):
    CONFIG = {
        "vector_config": {
            "max_tip_length_to_length_ratio": 0.15 * 0.4,
            "tip_length": 0.05 * 0.2,
            "max_stroke_width_to_length_ratio": 80,
            "stroke_width": 3,
        },
        "max_circle_stroke_width": 0.5,
        "rect_scale_factor": 0.01,
        # "parametric_function_step_size": 0.01,
    }

    def get_rect_center(self):
        return self.vectors[-1].get_end()

    # def get_drawn_path(self, vectors, stroke_width=2, **kwargs):
    #     return self.get_path_end(vectors, stroke_width, **kwargs)


class TrebleClefFourierSeriesExampleWithRectForZoom(FourierSeriesExampleWithRectForZoom):
    CONFIG = {
        "file_name": "TrebleClef",
    }


class TrebleClefZoomedInFourierSeriesExample(ZoomedInFourierSeriesExample):
    CONFIG = {
        "file_name": "TrebleClef",
    }


class NailAndGearFourierSeriesExampleWithRectForZoom(FourierSeriesExampleWithRectForZoom):
    CONFIG = {
        "file_name": "Nail_And_Gear",
        "n_vectors": 200,
        "drawn_path_color": "#39FF14",
    }


class NailAndGearZoomedInFourierSeriesExample(ZoomedInFourierSeriesExample):
    CONFIG = {
        "file_name": "Nail_And_Gear",
        "n_vectors": 200,
        "drawn_path_color": "#39FF14",
    }


class SigmaFourierSeriesExampleWithRectForZoom(FourierSeriesExampleWithRectForZoom):
    CONFIG = {
        "n_vectors": 200,
        "drawn_path_color": PINK,
    }

    def get_shape(self):
        return TexMobject("\\Sigma")

    def get_rect(self):
        result = super().get_rect()
        result.set_opacity(0)
        return result


class SigmaZoomedInFourierSeriesExample(SigmaFourierSeriesExampleWithRectForZoom, ZoomedInFourierSeriesExample):
    pass
