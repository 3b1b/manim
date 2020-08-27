from manimlib.imports import *
from active_projects.eop.reusable_imports import *


class ShowUncertaintyDarts(Scene):


    def throw_darts(self, n, run_time = 1):

        points = np.random.normal(
            loc = self.dartboard.get_center(),
            scale = 0.6 * np.ones(3),
            size = (n,3)
        )
        points[:,2] = 0
        dots = VGroup()
        for point in points:
            dot = Dot(point, radius = 0.04, fill_opacity = 0.7)
            dots.add(dot)
            self.add(dot)

        self.play(
            LaggedStartMap(FadeIn, dots, lag_ratio = 0.01, run_time = run_time)
        )


    def construct(self):

        self.dartboard = ImageMobject("dartboard").scale(2)
        dartboard_circle = Circle(
            radius = self.dartboard.get_width() / 2,
            fill_color = BLACK,
            fill_opacity = 0.5,
            stroke_color = WHITE,
            stroke_width = 5
        )
        self.dartboard.add(dartboard_circle)

        self.add(self.dartboard)
    
        self.throw_darts(5,5)
        self.throw_darts(20,5)
        self.throw_darts(100,5)
        self.throw_darts(1000,5)

