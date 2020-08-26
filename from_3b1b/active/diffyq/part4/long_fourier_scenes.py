from manimlib.imports import *

from from_3b1b.active.diffyq.part4.fourier_series_scenes import ComplexFourierSeriesExample
from manimlib.once_useful_constructs.fractals import HilbertCurve


class FourierSeriesExampleWithRectForZoom(ComplexFourierSeriesExample):
    CONFIG = {
        "n_vectors": 100,
        "slow_factor": 0.01,
        "rect_scale_factor": 0.1,
        "start_drawn": True,
        "drawing_height": 7,
        "rect_stroke_width": 1,
    }

    def construct(self):
        self.add_vectors_circles_path()
        self.circles.set_stroke(opacity=0.5)
        rect = self.rect = self.get_rect()
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
            stroke_width=self.rect_stroke_width,
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


class ZoomedInFourierSeriesExample100x(ZoomedInFourierSeriesExample):
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
        "drawn_path_stroke_width": 10,
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
        "rect_stroke_width": 0,
    }

    def get_shape(self):
        return TexMobject("\\Sigma")


class SigmaZoomedInFourierSeriesExample(SigmaFourierSeriesExampleWithRectForZoom, ZoomedInFourierSeriesExample):
    pass


class FourierOfFourier(FourierSeriesExampleWithRectForZoom):
    CONFIG = {
        "file_name": "FourierOneLine",
        "n_vectors": 300,
        "rect_stroke_width": 1,
    }


class FourierOfFourierZoomedIn(ZoomedInFourierSeriesExample):
    CONFIG = {
        "file_name": "FourierOneLine",
        "max_circle_stroke_width": 0.3,
        "n_vectors": 300,
    }


class FourierOfFourier100xZoom(ZoomedInFourierSeriesExample100x):
    CONFIG = {
        "file_name": "FourierOneLine",
        "max_circle_stroke_width": 0.3,
        "n_vectors": 300,
        "slow_factor": 0.001,
    }

    def run_one_cycle(self):
        self.vector_clock.set_value(0.3)
        self.wait(40)


class FourierOfHilbert(FourierSeriesExampleWithRectForZoom):
    CONFIG = {
        "n_vectors": 300,
        "rect_stroke_width": 1,
        "drawn_path_stroke_width": 4,
        "drawn_path_color": BLUE,
    }

    def get_path(self):
        path = HilbertCurve(order=5)
        path.set_height(self.drawing_height)
        path.to_edge(DOWN)
        combined_path = VMobject()
        for sm in path.family_members_with_points():
            combined_path.append_vectorized_mobject(sm)
        start = combined_path.get_start()
        end = combined_path.get_end()
        points = [
            interpolate(end, start, alpha)
            for alpha in np.linspace(0, 1, 10)
        ]
        for point in points:
            combined_path.add_line_to(point)

        combined_path.set_stroke(width=0)
        return combined_path


class FourierOfHilbertZoomedIn(FourierOfHilbert, ZoomedInFourierSeriesExample):
    pass


class FourierOfBritain(FourierSeriesExampleWithRectForZoom):
    CONFIG = {
        "file_name": "Britain",
        "n_vectors": 500,
        "drawn_path_color": RED,
    }


class FourierOfBritainZoomedIn(FourierOfBritain, ZoomedInFourierSeriesExample):
    pass


class FourierOfSeattle(FourierSeriesExampleWithRectForZoom):
    CONFIG = {
        "file_name": "SeattleSkyline",
        "drawing_height": 7,
        "n_vectors": 400,
        "drawn_path_color": TEAL,
        "drawn_path_stroke_width": 5,
    }


class FourierOfSeattleZoomedIn(ZoomedInFourierSeriesExample):
    CONFIG = {
        "file_name": "SeattleSkyline",
        "drawing_height": 7,
        "n_vectors": 400,
        "drawn_path_color": TEAL,
        "drawn_path_stroke_width": 5,
        "max_circle_stroke_width": 0.3,
    }


class VideoWrapper(Scene):
    def construct(self):
        fade_rect = FullScreenFadeRectangle()
        fade_rect.set_fill(DARK_GREY, 1)
        screen_rect = ScreenRectangle()
        screen_rect.set_height(4)
        screen_rect.set_fill(BLACK, 1)
        screen_rect.set_stroke(width=0)

        boundary = AnimatedBoundary(screen_rect)

        title = TextMobject("Learn the math")
        title.scale(1.5)
        title.next_to(screen_rect, UP)

        self.add(fade_rect)
        self.add(screen_rect)
        self.add(boundary)

        self.play(FadeInFromDown(title))
        self.wait(19)
