from manimlib.imports import *

from active_projects.ode.part2.fourier_series import FourierOfTrebleClef


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
        new_coefs = self.get_coefficients_of_path(new_path)
        new_vectors = self.get_rotating_vectors(
            coefficients=new_coefs
        )
        new_drawn_path = self.get_drawn_path(new_vectors)

        self.vector_clock.set_value(0)
        self.vector_clock.suspend_updating(0)

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
        anims += [
            FadeOut(self.drawn_path)
        ]

        self.play(*anims, run_time=3)
        self.vector_clock.resume_updating()
        for vect in self.vectors:
            vect.remove_updater(vect.updaters[-1])

        self.add(new_drawn_path)
        for n in range(self.n_cycles):
            self.run_one_cycle()

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


class ComplexFourierSeriesExampleEnd(ExternallyAnimatedScene):
    pass


class FourierSeriesExampleWithRectForZoom(ComplexFourierSeriesExample):
    CONFIG = {
        "n_vectors": 100,
        "slow_factor": 0.01,
        "rect_scale_factor": 0.15,
        "parametric_function_step_size": 0.0001,
        "start_drawn": True,
    }

    def construct(self):
        self.add_vectors_circles_path()
        self.circles.set_stroke(opacity=0.5)
        rect = self.get_rect()
        rect.set_height(self.rect_scale_factor * FRAME_HEIGHT)
        rect.add_updater(lambda m: m.move_to(
            center_of_mass([
                v.get_end()
                for v in self.vectors
            ])
        ))
        self.add(rect)
        self.run_one_cycle()

    def get_rect(self):
        return ScreenRectangle(
            color=WHITE,
            stroke_width=2,
        )


class ZoomedInFourierSeriesExample(FourierSeriesExampleWithRectForZoom, MovingCameraScene):
    CONFIG = {
        "vector_config": {
            "max_tip_length_to_length_ratio": 0.15,
            "tip_length": 0.05,
        }
    }

    def setup(self):
        ComplexFourierSeriesExample.setup(self)
        MovingCameraScene.setup(self)

    def get_rect(self):
        return self.camera_frame
