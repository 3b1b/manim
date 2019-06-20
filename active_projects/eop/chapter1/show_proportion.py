from manimlib.imports import *


class ProbabilityRect(VMobject):
    CONFIG = {
        "unit_width" : 2,
        "unit_height" : 2,
        "alignment" : LEFT,
        "color": YELLOW,
        "opacity": 1.0,
        "num_decimal_places": 2,
        "use_percent" : False
    }

    def __init__(self, p0, **kwargs):

        VMobject.__init__(self, **kwargs)
        self.unit_rect = Rectangle(
            width = self.unit_width,
            height = self.unit_height,
            stroke_color = self.color
        )
        self.p = p0
        self.prob_rect = self.create_prob_rect(p0)
        self.prob_label = self.create_prob_label(p0)
        
        self.add(self.unit_rect, self.prob_rect, self.prob_label)


    def create_prob_rect(self, p):

        prob_width, prob_height = self.unit_width, self.unit_height

        if self.alignment in [LEFT, RIGHT]:
            prob_width *= p
        elif self.alignment in [UP, DOWN]:
            prob_height *= p
        else:
            raise Exception("Aligment must be LEFT, RIGHT, UP or DOWN")

        prob_rect = Rectangle(
            width = prob_width,
            height = prob_height,
            fill_color = self.color,
            fill_opacity = self.opacity,
            stroke_color = self.color
        )

        prob_rect.align_to(self.unit_rect, direction = self.alignment)
        return prob_rect


    def create_prob_label(self, p):

        if self.use_percent:
            prob_label = DecimalNumber(
                p * 100,
                color = BLACK,
                num_decimal_places = self.num_decimal_places,
                unit = "\%"
            )
        else:
            prob_label = DecimalNumber(
                p,
                color = BLACK,
                num_decimal_places = self.num_decimal_places,
            )

        prob_label.move_to(self.prob_rect)

        return prob_label


class ChangeProbability(Animation):

    def __init__(self, prob_mob, p1, **kwargs):

        if not isinstance(prob_mob, ProbabilityRect):
            raise Exception("ChangeProportion's mobject must be a ProbabilityRect")

        self.p1 = p1
        self.p0 = prob_mob.p
        Animation.__init__(self, prob_mob, **kwargs)


    def interpolate_mobject(self, alpha):

        p = (1 - alpha) * self.p0 + alpha * self.p1
        self.mobject.remove(self.mobject.prob_rect, self.mobject.prob_label)
        self.mobject.prob_rect = self.mobject.create_prob_rect(p)
        self.mobject.prob_label = self.mobject.create_prob_label(p)
        self.mobject.add(self.mobject.prob_rect, self.mobject.prob_label)


    def clean_up_from_scene(self, scene=None):
        self.mobject.p = self.p1
        super(ChangeProbability, self).clean_up_from_scene(scene = scene)





class ShowProbAsProportion(Scene):

    def construct(self):

        p0 = 0.3
        p1 = 1
        p2 = 0.18
        p3 = 0.64

        prob_mob = ProbabilityRect(p0,
            unit_width = 4,
            unit_height = 2,
            use_percent = False,
            num_decimal_places = 2
        )

        self.add(prob_mob)
        self.wait()
        self.play(
            ChangeProbability(prob_mob, p1,
                run_time = 3)
        )
        self.wait(0.5)
        self.play(
            ChangeProbability(prob_mob, p2,
                run_time = 3)
        )
        self.wait(0.5)
        self.play(
            ChangeProbability(prob_mob, p3,
                run_time = 3)
        )











