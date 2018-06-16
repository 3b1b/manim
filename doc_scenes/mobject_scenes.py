from scene.scene import Scene as Scene
from mobject.geometry import Circle as Circle
from mobject.geometry import Line as Line
from mobject.geometry import Dot as Dot
from mobject.numbers import DecimalNumber as DecimalNumber
from animation.creation import ShowCreation
from constants import RIGHT as RIGHT
from constants import LEFT as LEFT
from constants import UP as UP
from constants import DOWN as DOWN
from constants import TOP as TOP
from constants import BOTTOM as BOTTOM
from constants import LEFT_SIDE as LEFT_SIDE
from constants import RIGHT_SIDE as RIGHT_SIDE

class NumberAndCircle(Scene):
    def construct(self):
        top_border    = Line(TOP + LEFT_SIDE, TOP + RIGHT_SIDE)
        bottom_border = Line(BOTTOM + LEFT_SIDE, BOTTOM + RIGHT_SIDE)
        left_border   = Line(LEFT_SIDE + BOTTOM, LEFT_SIDE + TOP)
        right_border  = Line(RIGHT_SIDE + BOTTOM, RIGHT_SIDE + TOP)
        origin = Dot()
        self.add(top_border)
        self.add(bottom_border)
        self.add(left_border)
        self.add(right_border)
        self.add(origin)

        circle = Circle()
        circle.shift(3 * RIGHT + 2 * UP)
        self.add(circle)

        decimal = DecimalNumber(2.5)
        decimal.shift(LEFT + DOWN)
        self.add(decimal)
