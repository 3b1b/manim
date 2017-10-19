from nn.network import *
from nn.part1 import *
from nn.part2 import *

class LayOutPlan(Scene):
    def construct(self):
        title = TextMobject("Plan")
        title.scale(1.5)
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT).scale(SPACE_WIDTH - 1)
        h_line.next_to(title, DOWN)

        items = BulletedList(
            "Recap",
            "Intuitive walkthrough",
            "Derivatives in \\\\ computational graphs",
        )
        items.to_edge(LEFT, buff = LARGE_BUFF)
        self.add(items)

        rect = ScreenRectangle()
        rect.scale_to_fit_width(2*SPACE_WIDTH - items.get_width() - 2)
        rect.next_to(items, RIGHT, MED_LARGE_BUFF)

        self.play(
            Write(title),
            ShowCreation(h_line),
            ShowCreation(rect),
            run_time = 2
        )
        for i in range(len(items)):
            self.play(items.fade_all_but, i)
            self.dither(2)

class TODOInsertFeedForwardAnimations(TODOStub):
    CONFIG = {
        "message" : "Insert Feed Forward Animations"
    }

class TODOInsertStepsDownCostSurface(TODOStub):
    CONFIG = {
        "message" : "Insert Steps Down Cost Surface"
    }

class TODOInsertDefinitionOfCostFunction(TODOStub):
    CONFIG = {
        "message" : "Insert Definition of cost function"
    }


class TODOInsertGradientNudging(TODOStub):
    CONFIG = {
        "message" : "Insert GradientNudging"
    }

















































