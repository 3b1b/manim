import random
from manimlib.imports import *
from manimlib.mobject.three_dimensions import Cube, Prism
from manimlib.mobject.types.vectorized_mobject import VMobject
from math import sqrt

class Coin(VGroup):
    CONFIG = {
        "fill_opacity": 0.5,
        "fill_color": YELLOW_D,
        "stroke_width": 0.7,
        "side_length": 2,
    }
    def generate_points(self):
        for ln in np.arange(0, 0.5, 0.1):
            face = Circle(
                radius=1.5,
                shade_in_3d=True,
                color = YELLOW_D,
            )
            face.flip()
            face.shift( ln*OUT / 2.0)
            face.apply_matrix(z_to_vector(OUT))
            self.add(face)

class Fraction(ThreeDScene):
	
	def construct(self):
		arc = Sector()
		# self.play(ShowCreation(arc))
		circle = Coin(fill_color='#ff0000')
		self.add(circle)
		half1 = Sector(fill_color=YELLOW_D,outer_radius=1.5,angle= TAU/2,start_angle=TAU)
		half2 = Sector(fill_color=YELLOW_D,outer_radius=1.5,angle= TAU/2,start_angle=TAU/2)
		three1 = Sector(fill_color='#00ff00',outer_radius=1.5,angle= -TAU/3,start_angle=-TAU/12)
		three2 = Sector(fill_color='#00ff00',outer_radius=1.5,angle= -TAU/3,start_angle=-5*TAU/12)
		three3 = Sector(fill_color='#00ff00',outer_radius=1.5,angle= -TAU/3,start_angle=-3*TAU/4)
		#1/4th part is being made
		four1 = Sector(fill_color='#0000ff',outer_radius=1.5,angle= -TAU/4,start_angle=0)
		four2 = Sector(fill_color='#0000ff',outer_radius=1.5,angle= -TAU/4,start_angle=-TAU/4)
		four3 = Sector(fill_color='#0000ff',outer_radius=1.5,angle= -TAU/4,start_angle=-TAU/2)
		four4 = Sector(fill_color='#0000ff',outer_radius=1.5,angle= -TAU/4,start_angle=TAU/4)
								
		self.add(four1)
		# self.wait(1)
		self.add(four2)
		# self.wait(1)
		self.add(four3)
		# self.wait(1)
		self.add(four4)
		# self.wait(1)
		self.add(three1)
		self.add(three2)
		self.add(three3)
		self.add(half1)
		self.add(half2)

		self.play(half2.move_to,DOWN*3,half1.move_to,UP*3,run_time=3)
		# half =TexMobject("\\nicefrac{3}{4}")
		first_eq = TextMobject("$$\\frac{1}{2}$$",color=BLACK,fill_color=BLACK)
		self.play(Write(first_eq))
		self.wait(1)
		self.remove(half1,half2,first_eq)
		self.play(three1.move_to,DOWN*3,three2.move_to,LEFT*3+UP*2,three3.move_to,RIGHT*3+UP*2,run_time=3)
		second_eq = TextMobject("$$\\frac{1}{3}$$",color=BLACK,fill_color=BLACK)
		self.play(Write(second_eq))
		self.wait(2)
		self.remove(three1,three2,three3,second_eq)
		self.play(four1.move_to,RIGHT*2+DOWN*3,four2.move_to,LEFT*2+DOWN*3,four3.move_to,LEFT*2+UP*3,four4.move_to,RIGHT*2+UP*3,run_time=3)
		third_eq = TextMobject("$$\\frac{1}{4}$$",color=BLACK,fill_color=BLACK)
		self.play(Write(third_eq))
		self.wait(1)
		self.remove(four1,four2,four3,four4)


class test(ThreeDScene):
	def construct(self):
		three1 = Sector(fill_color='#00ff00',outer_radius=2,angle= -TAU/3,start_angle=0)
		three2 = Sector(fill_color='#00ff00',outer_radius=2,angle= -TAU/3,start_angle=-TAU/3)
		three3 = Sector(fill_color='#00ff00',outer_radius=2,angle= -TAU/3,start_angle=-2*TAU/3)
		self.play(ShowCreation(three1))
		self.play(ShowCreation(three2))
		self.play(ShowCreation(three3))
		self.wait(2)

class Differences(ThreeDScene):
	def construct(self):
		half = Sector(fill_color=YELLOW_D,outer_radius=1.5,angle= TAU/2,start_angle=TAU/2)
		three = Sector(fill_color='#00ff00',outer_radius=1.5,angle= -TAU/3,start_angle=0)
		four = Sector(fill_color='#0000ff',outer_radius=1.5,angle= -TAU/4,start_angle=0)


		self.play(ShowCreation(half))
		self.play(ShowCreation(three))
		self.play(ShowCreation(four))
		first_eq = TextMobject("$$\\frac{1}{2}$$",color=BLACK,fill_color=BLACK)
		first_eq.shift(UP*2)
		second_eq = TextMobject("$$\\frac{1}{3}$$",color=BLACK,fill_color=BLACK)
		second_eq.shift(UP*2)
		third_eq = TextMobject("$$\\frac{1}{4}$$",color=BLACK,fill_color=BLACK)
		third_eq.shift(UP*2)
		half.add(first_eq)
		three.add(second_eq)
		four.add(third_eq)
		self.play(half.move_to,LEFT*5,four.move_to,RIGHT*5,three.move_to,UP*0)
		self.wait(1)
		great = TexMobject(">",color=BLACK,fill_color=BLACK)
		great.scale(2)
		great.shift(LEFT*2)
		great1 = copy.deepcopy(great)
		great1.shift(RIGHT*4)
		self.add(great,great1)
		self.wait(1)

