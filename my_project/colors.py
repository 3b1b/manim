from big_ol_pile_of_manim_imports import *

COLOR_MAP = {
    "DARK_BROWN": "#8B4513",
    "LIGHT_BROWN": "#CD853F",
    "GREY_BROWN": "#736357",
}

class Colors(Scene):
	CONFIG = {
		's': [
			(BLUE_E      , ( 2  )*UP + (-2  )*RIGHT),
			(BLUE_D      , ( 2  )*UP + (-1  )*RIGHT),
			(BLUE_C      , ( 2  )*UP + ( 0  )*RIGHT),
			(BLUE_B      , ( 2  )*UP + ( 1  )*RIGHT),
			(BLUE_A      , ( 2  )*UP + ( 2  )*RIGHT),
			(TEAL_E      , ( 1.5)*UP + (-2  )*RIGHT),
			(TEAL_D      , ( 1.5)*UP + (-1  )*RIGHT),
			(TEAL_C      , ( 1.5)*UP + ( 0  )*RIGHT),
			(TEAL_B      , ( 1.5)*UP + ( 1  )*RIGHT),
			(TEAL_A      , ( 1.5)*UP + ( 2  )*RIGHT),
			(GREEN_E     , ( 1  )*UP + (-2  )*RIGHT),
			(GREEN_D     , ( 1  )*UP + (-1  )*RIGHT),
			(GREEN_C     , ( 1  )*UP + ( 0  )*RIGHT),
			(GREEN_B     , ( 1  )*UP + ( 1  )*RIGHT),
			(GREEN_A     , ( 1  )*UP + ( 2  )*RIGHT),
			(YELLOW_E    , ( 0.5)*UP + (-2  )*RIGHT),
			(YELLOW_D    , ( 0.5)*UP + (-1  )*RIGHT),
			(YELLOW_C    , ( 0.5)*UP + ( 0  )*RIGHT),
			(YELLOW_B    , ( 0.5)*UP + ( 1  )*RIGHT),
			(YELLOW_A    , ( 0.5)*UP + ( 2  )*RIGHT),
			(GOLD_E      , (-0.5)*UP + (-2  )*RIGHT),
			(GOLD_D      , (-0.5)*UP + (-1  )*RIGHT),
			(GOLD_C      , (-0.5)*UP + ( 0  )*RIGHT),
			(GOLD_B      , (-0.5)*UP + ( 1  )*RIGHT),
			(GOLD_A      , (-0.5)*UP + ( 2  )*RIGHT),
			(RED_E       , (-1  )*UP + (-2  )*RIGHT),
			(RED_D       , (-1  )*UP + (-1  )*RIGHT),
			(RED_C       , (-1  )*UP + ( 0  )*RIGHT),
			(RED_B       , (-1  )*UP + ( 1  )*RIGHT),
			(RED_A       , (-1  )*UP + ( 2  )*RIGHT),
			(MAROON_E    , (-1.5)*UP + (-2  )*RIGHT),
			(MAROON_D    , (-1.5)*UP + (-1  )*RIGHT),
			(MAROON_C    , (-1.5)*UP + ( 0  )*RIGHT),
			(MAROON_B    , (-1.5)*UP + ( 1  )*RIGHT),
			(MAROON_A    , (-1.5)*UP + ( 2  )*RIGHT),
			(PURPLE_E    , (-2  )*UP + (-2  )*RIGHT),
			(PURPLE_D    , (-2  )*UP + (-1  )*RIGHT),
			(PURPLE_C    , (-2  )*UP + ( 0  )*RIGHT),
			(PURPLE_B    , (-2  )*UP + ( 1  )*RIGHT),
			(PURPLE_A    , (-2  )*UP + ( 2  )*RIGHT),

			(DARK_BLUE   , ( 2  )*UP + ( 3.5)*RIGHT),
			(GREEN_SCREEN, ( 1  )*UP + ( 3.5)*RIGHT),
			(PINK        , (-1  )*UP + ( 3.5)*RIGHT),
			(ORANGE      , ( 0.5)*UP + ( 3.5)*RIGHT),

			(WHITE       , ( 3  )*UP + (-2  )*RIGHT),
			(LIGHT_GRAY  , ( 3  )*UP + (-1  )*RIGHT),
			(GRAY        , ( 3  )*UP + ( 0  )*RIGHT),
			(DARK_GREY   , ( 3  )*UP + ( 1  )*RIGHT),
			(DARKER_GREY , ( 3  )*UP + ( 2  )*RIGHT),

			(DARK_BROWN  , ( 3.5)*UP + (-1  )*RIGHT),
			(LIGHT_BROWN , ( 3.5)*UP + ( 0  )*RIGHT),
			(GREY_BROWN  , ( 3.5)*UP + ( 1  )*RIGHT),

		]
	}
	def construct(self):
		self.dots = [
			Dot(position).set_color(color)
			for color, position in self.s
		]
		self.add(*self.dots)
		self.wait()