import random
from manimlib.imports import *
from manimlib.mobject.three_dimensions import Cube, Prism
from manimlib.mobject.types.vectorized_mobject import VMobject
from math import sqrt

class Scale(VGroup):
    CONFIG = {
        "fill_opacity": 0.5,
        # "fill_color": BLUE_D,
        "stroke_width": 0.7,
        "side_length": 2,
    }
    height,width=0,0
    color = WHITE
    def generate_points(self):
        for ln in np.arange(0, 0.5, 0.1):
            face = Rectangle(
            	height=self.height,
            	width=self.width,
                shade_in_3d=True,
                color = self.color,
            )
            face.flip()
            face.shift( ln*OUT / 2.0)
            face.apply_matrix(z_to_vector(OUT))
            self.add(face)
class Coin(VGroup):
    CONFIG = {
        "fill_opacity": 0.45,
        "fill_color": '#808000',
        "stroke_width": 0.7,
        "side_length": 2,
    }
    def generate_points(self):
        for ln in np.arange(0, 0.5, 0.1):
            face = Circle(
                radius=1,
                shade_in_3d=True,
                color = '#808000',
            )
            face.flip()
            face.shift( ln*OUT / 2.0)
            face.apply_matrix(z_to_vector(OUT))
            self.add(face)

class FractionStrip(ThreeDScene):
	def construct(self):
		rect = Scale(width=9,height=1,color='#000000')
		rect.shift(UP*2.5)
		self.add(rect)
		half1 = Scale(width=4.5,height=1,color='#808080')
		half2 = copy.deepcopy(half1)
		half1.shift(LEFT*2.24+UP*2.5)
		half2.shift(RIGHT*2.24+UP*2.5)
		
		# self.wait(1)

		third1 = Scale(width=3,height=1,color='#808000')
		third2 = Scale(width=3,height=1,color='#808000')
		third3 = Scale(width=3,height=1,color='#808000')
		third1.shift(RIGHT*3+UP*2.5)
		third2.shift(LEFT*3+UP*2.5)
		third3.shift(UP*2.5)
		# self.wait(1)

		four1 = Scale(width=2.25,height=1,color='#008080')
		four2 = copy.deepcopy(four1)
		four3 = copy.deepcopy(four1)
		four4 = copy.deepcopy(four1)
		four1.shift(RIGHT*3.375+UP*2.5)
		four2.shift(RIGHT*1.125+UP*2.5)
		four3.shift(LEFT*3.375+UP*2.5)
		four4.shift(LEFT*1.125+UP*2.5)
		
		six1 = Scale(width=1.5,height=1,color='#800080')
		six2 = copy.deepcopy(six1)
		six3 = copy.deepcopy(six1)
		six4 = copy.deepcopy(six1)
		six5 = copy.deepcopy(six1)
		six6 = copy.deepcopy(six1)

		six1.shift(LEFT*3.75+UP*2.5)
		six2.shift(LEFT*2.25+UP*2.5)
		six3.shift(LEFT*0.75+UP*2.5)
		six4.shift(RIGHT*3.75+UP*2.5)
		six5.shift(RIGHT*2.25+UP*2.5)
		six6.shift(RIGHT*0.75+UP*2.5)

		# self.wait(1)
		self.add(six1,six2,six3,six4,six5,six6)
		self.add(four1,four2,four3,four4)
		self.add(third1,third2,third3)
		self.add(half1,half2)
		
		# self.wait(1)
		self.play(half1.move_to,LEFT*3+UP*1.4,half2.move_to,RIGHT*3+UP*1.4,run_time=1)
		self.play(half1.move_to,LEFT*2.27+UP*1.23,half2.move_to,RIGHT*2.27+UP*1.23,run_time=0.7)
		first_eq1 = TextMobject("$$\\frac{1}{2}$$",color=BLACK,fill_color=BLACK)
		first_eq1.scale(0.7)
		first_eq2 = copy.deepcopy(first_eq1)
		first_eq1.shift(LEFT*2.27+UP*1.23)
		first_eq2.shift(RIGHT*2.27+UP*1.23)
		self.play(ShowCreation(first_eq1),ShowCreation(first_eq2))

		self.play(third2.move_to,LEFT*5+UP*0,third1.move_to,RIGHT*5+UP*0,third3.move_to,UP*0,run_time=1)
		self.play(third2.move_to,LEFT*3.05+DOWN*0,third1.move_to,RIGHT*3.05+DOWN*0,third3.move_to,DOWN*0,run_time=0.7)
		third_eq1 = TextMobject("$$\\frac{1}{3}$$",color=BLACK,fill_color=BLACK)
		third_eq1.scale(0.7)
		third_eq2 = copy.deepcopy(third_eq1)
		third_eq3 = copy.deepcopy(third_eq1)
		third_eq1.shift(LEFT*3.05+DOWN*0)
		third_eq2.shift(RIGHT*3.05+DOWN*0)
		third_eq3.shift(DOWN*0)
		self.play(ShowCreation(third_eq1),ShowCreation(third_eq2),ShowCreation(third_eq3))

		self.play(four3.move_to,LEFT*5+DOWN*1.25,four4.move_to,LEFT*2+DOWN*1.25,four2.move_to,RIGHT*2+DOWN*1.25,four1.move_to,RIGHT*5+DOWN*1.25,run_time=1)
		self.play(four3.move_to,LEFT*3.44+DOWN*1.25,four4.move_to,LEFT*1.145+DOWN*1.25,four2.move_to,RIGHT*1.143+DOWN*1.25,four1.move_to,RIGHT*3.44+DOWN*1.25)
		four_eq1 = TextMobject("$$\\frac{1}{4}$$",color=BLACK,fill_color=BLACK)
		four_eq1.scale(0.7)
		four_eq2 = copy.deepcopy(four_eq1)
		four_eq3 = copy.deepcopy(four_eq1)
		four_eq4 = copy.deepcopy(four_eq1)
		four_eq1.shift(LEFT*3.44+DOWN*1.25)
		four_eq2.shift(LEFT*1.145+DOWN*1.25)
		four_eq3.shift(RIGHT*1.143+DOWN*1.25)
		four_eq4.shift(RIGHT*3.44+DOWN*1.25)
		self.play(ShowCreation(four_eq1),ShowCreation(four_eq2),ShowCreation(four_eq3),ShowCreation(four_eq4))


		self.play(six1.move_to,LEFT*6+DOWN*2.5,six2.move_to,LEFT*4+DOWN*2.5,six3.move_to,LEFT*2+DOWN*2.5,six4.move_to,RIGHT*6+DOWN*2.5,six5.move_to,RIGHT*4+DOWN*2.5,six6.move_to,RIGHT*2+DOWN*2.5)
		self.play(six1.move_to,LEFT*3.85+DOWN*2.5,six2.move_to,LEFT*2.3+DOWN*2.5,six3.move_to,LEFT*0.77+DOWN*2.5,six4.move_to,RIGHT*3.85+DOWN*2.5,six5.move_to,RIGHT*2.3+DOWN*2.5,six6.move_to,RIGHT*0.75+DOWN*2.5)

		six_eq1 = TextMobject("$$\\frac{1}{6}$$",color=BLACK,fill_color=BLACK)
		six_eq1.scale(0.7)
		six_eq2 = copy.deepcopy(six_eq1)
		six_eq3 = copy.deepcopy(six_eq1)
		six_eq4 = copy.deepcopy(six_eq1)
		six_eq5 = copy.deepcopy(six_eq1)
		six_eq6 = copy.deepcopy(six_eq1)
		six_eq1.shift(LEFT*3.85+DOWN*2.5)
		six_eq2.shift(LEFT*2.3+DOWN*2.5)
		six_eq3.shift(LEFT*0.77+DOWN*2.5)
		six_eq4.shift(RIGHT*3.85+DOWN*2.5)
		six_eq5.shift(RIGHT*2.3+DOWN*2.5)
		six_eq6.shift(RIGHT*0.75+DOWN*2.5)

		self.play(ShowCreation(six_eq1),ShowCreation(six_eq2),ShowCreation(six_eq3),ShowCreation(six_eq4),ShowCreation(six_eq5),ShowCreation(six_eq6))

		one = TextMobject("1")
		one.scale(0.7)
		one.shift(UP*2.5)
		self.play(ShowCreation(one))
		self.wait(2)

		
		self.play(FadeOut(six_eq2),FadeOut(six_eq3),FadeOut(six_eq4),FadeOut(six_eq5),FadeOut(six_eq6))
		self.play(FadeOut(four_eq2),FadeOut(four_eq3),FadeOut(four_eq4))
		self.play(FadeOut(third_eq2),FadeOut(third_eq3))
		self.play(FadeOut(first_eq2))
		#camera orientation has change from horizontal to vertical
		# self.move_camera(0*np.pi/2, np.pi)

		# self.play(FadeOut(six2),FadeOut(six3),FadeOut(six4),FadeOut(six5),FadeOut(six6))
		# self.play(FadeOut(four4),FadeOut(four2),FadeOut(four1))
		# self.play(FadeOut(third3),FadeOut(third1))
		# self.play(FadeOut(half2))
		self.wait(1)

		cross2 = TextMobject("$$\\times 2 = 1$$",color=BLACK)
		cross2.shift(UP*1.23+RIGHT*2)
		self.play(FadeOut(half2),Write(cross2))
		cross3 = TextMobject("$$\\times 3 = 1$$",color=BLACK)
		cross3.shift(RIGHT*2)
		self.play(FadeOut(third3),FadeOut(third1),Write(cross3))
		cross4 = TextMobject("$$\\times 4 = 1$$",color=BLACK)
		cross4.shift(DOWN*1.25+RIGHT*2)
		self.play(FadeOut(four4),FadeOut(four2),FadeOut(four1),Write(cross4))
		cross6 = TextMobject("$$\\times 6 = 1$$",color=BLACK)
		cross6.shift(DOWN*2.5+RIGHT*2)
		self.play(FadeOut(six2),FadeOut(six3),FadeOut(six4),FadeOut(six5),FadeOut(six6),Write(cross6))


class ScaleAndCircle(ThreeDScene):
	CONFIG= {
	# radius = 1.5,
	# fill_color='#008800',
	}
	def construct(self):
		rect = Scale(width=4,height=1,color='#008080')
		rect.shift(UP*2.5+LEFT*3)
		self.add(rect)
		circle = Coin(radius=1,fill_color='#808000')
		circle.shift(RIGHT*3+UP*2.5)
		self.add(circle)

		half_scale = Scale(width=2,height=1,color='#008080')
		half_scale.next_to(rect,DOWN*6)
		half_scale.align_to(rect,LEFT)
		# half_scale.shift(LEFT*3)
		half_scale2 = Scale(width=2,height=1,color='#9DA4AD')
		half_scale2.next_to(rect,DOWN*6)
		half_scale2.align_to(rect,RIGHT)
		half_circle = Sector(fill_color='#808000',outer_radius=1,angle= TAU/2,start_angle=TAU)
		circel = Coin(fill_color='#B8D2F2')
		half_circle.next_to(circle,DOWN*2)
		circel.next_to(circle,DOWN*2)
		'''
		third_scale = Scale(width=1.33,height=1,color='#008080')
		third_circle = Sector(fill_color='#808000',outer_radius=1,angle= -TAU/3,start_angle=-TAU/12)
		third_scale.next_to(half_scale,DOWN*3)
		third_scale.align_to(half_scale,LEFT)
		# third_scale.shift(LEFT*3+DOWN*1.5)
		third_circle.next_to(half_circle,DOWN*3)
		'''
		quad_scale = Scale(width=1,height=1,color='#008080')
		quad_scale1 = Scale(width=3,height=1,color='#9DA4AD')
		quad_circle = Sector(fill_color='#808000',outer_radius=1,angle= TAU/4,start_angle=0)
		quad_scale1.align_to(half_scale2,RIGHT)

		quad_scale.next_to(half_scale,DOWN*5)
		quad_scale1.next_to(half_scale2,DOWN*5)
		quad_scale.align_to(half_scale,LEFT)
		quad_scale1.align_to(half_scale2,RIGHT)
		# quad_scale.shift(LEFT*3+DOWN*4)
		quad_circle.next_to(circel,DOWN*2)
		quad_circle.align_to(circel,RIGHT)
		circel1 = Coin(fill_color='#B8D2F2')
		circel1.next_to(circel,DOWN*2)

		sim = TextMobject("$$\\sim$$",color=BLACK)
		sim.scale(3)
		sim1 = copy.deepcopy(sim)
		sim2 = copy.deepcopy(sim1)

		self.wait(1)
		self.play(ShowCreation(half_scale),ShowCreation(half_scale2),ShowCreation(half_circle),Write(circel))
		# self.play(ShowCreation(third_scale),ShowCreation(third_circle))

		self.play(ShowCreation(quad_scale),ShowCreation(quad_scale1),ShowCreation(quad_circle),Write(circel1))
		self.wait(1)
		sim.shift(RIGHT*0.7)
		sim1.next_to(sim,UP*9)
		sim2.next_to(sim,DOWN*9)
		self.play(ShowCreation(sim),ShowCreation(sim1),ShowCreation(sim2))

		one = TextMobject("1",fill_color=BLACK,color=BLACK)
		one.scale(1)
		one.shift(RIGHT*5+UP*2.5)
		first = TextMobject("$$\\frac{1}{2}$$",color=BLACK,fill_color=BLACK)
		first.scale(1)
		first.next_to(one,DOWN*7)
		third = TextMobject("$$\\frac{1}{4}$$",color=BLACK,fill_color=BLACK)
		third.scale(1)
		third.next_to(first,DOWN*7)
		self.play(Write(one),Write(first),Write(third))
		self.wait(1)

