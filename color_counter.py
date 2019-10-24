import random
from manimlib.imports import *
from manimlib.mobject.three_dimensions import Cube, Prism
from manimlib.mobject.types.vectorized_mobject import VMobject
from math import sqrt


class Coin(VGroup):
    CONFIG = {
        "fill_opacity": 0.45,
        "fill_color": YELLOW_D,
        "stroke_width": 0.7,
        "side_length": 2,
    }
    def generate_points(self):
        for ln in np.arange(0, 0.5, 0.1):
            face = Circle(
                radius=0.4,
                shade_in_3d=True,
                color = YELLOW_D,
            )
            face.flip()
            face.shift( ln*OUT / 2.0)
            face.apply_matrix(z_to_vector(OUT))
            self.add(face)


class Counting(ThreeDScene):

	def get_hit_flash(self, point):
		flash = Flash(point,line_length=0.2,flash_radius=0.4,run_time=1,remover=True,color=BLACK)
		flash_mob = flash.mobject
		for submob in flash_mob:
			submob.reverse_points()
		return Uncreate(flash.mobject,run_time=0.25,lag_ratio=0,)


	def construct(self):
		red_coin = Coin(fill_color=RED_D)

		# coin_list = list()
		# for i in range(20):
		# 	coins = Coin(fill_color=RED_D)
		# 	coin_list.append(coins)

		one = TextMobject("One ",color=BLACK)
		one.shift(LEFT*3+UP*2)
		one.scale(2)
		two = TextMobject("Two ",color=BLACK)
		two.scale(2)
		three = TextMobject("Three ",color=BLACK)
		three.scale(2)
		two.next_to(one,DOWN*3)	
		two.align_to(one,LEFT)
		three.next_to(two,DOWN*3)
		three.align_to(one,LEFT)
		arrow1 = TexMobject("\\rightarrow",color=BLACK,fill_color=BLACK)
		arrow2 = TexMobject("\\rightarrow",color=BLACK,fill_color=BLACK)
		arrow3 = TexMobject("\\rightarrow",color=BLACK,fill_color=BLACK)
		arrow1.scale(2)
		arrow2.scale(2)
		arrow3.scale(2)
		
		arrow1.shift(UP*2)	
		one.add(arrow1)
		arrow2.shift(UP*0.5)
		two.add(arrow2)
		arrow3.shift(DOWN)
		three.add(arrow3)


		number = [one,two,three]
		position = RIGHT+UP*2
		# self.set_camera_orientation(1,np.pi/2)
		self.move_camera(0.7*np.pi/2, -1*np.pi/2)  
		for i in range(1,4):
			self.play(Write(number[i-1]))
			position_temp = np.copy(position)
			# print(position_temp, position)
			for j in range(i):
				position_temp+=RIGHT*1.2
				coin = Coin(color='#ff0000',fill_color='#ff0000')
				coin.shift(position_temp)
				self.play(GrowFromCenter(coin))
			print("1", position)
			position+=DOWN*1.5
			print("2", position)

		rect = ScreenRectangle(height=2.7,color=BLACK)
		rect.shift(RIGHT*3+UP*1.3)
		self.move_camera(0*np.pi/2, -1*np.pi/2)        
		self.play(ShowCreation(rect))
		self.wait(1)

		glow_circle = Circle(fill_color=RED_D,radius = 0.5)
		glow_circle.shift(RIGHT*3.4+UP*2)
		self.play(Write(glow_circle))
		self.play(self.get_hit_flash(RIGHT*3.4+UP*2))
		# self.missing(point)

		missing = TextMobject("Missing circle",fill_color=BLACK)
		arrow = Vector(0.5 * DOWN, color='#ff0000')
		arrow.shift(RIGHT*3.4+UP*3)
		missing.shift(RIGHT*3.4+UP*3.2)
		self.play(Write(missing),GrowArrow(arrow))
		# self.play(GrowArrow(arrow))

		self.wait(1)

		self.remove(glow_circle)
		self.remove(arrow,missing)
		self.play(rect.move_to, RIGHT*3.5+DOWN*0.2)

		glow_circle = Circle(fill_color=RED_D,radius = 0.5)
		glow_circle.shift(RIGHT*4.6+UP*0.45)
		self.play(Write(glow_circle))
		self.play(self.get_hit_flash(RIGHT*4.6+UP*0.45))

		# point = RIGHT*4.6+DOWN*1.2
		# self.missing(point)
		missing = TextMobject("Missing circle",fill_color=BLACK)
		arrow = Vector(0.5 * DOWN, color='#ff0000')
		arrow.shift(RIGHT*4.6+UP*1.45)
		missing.shift(RIGHT*4.6+UP*1.65)
		self.play(Write(missing),GrowArrow(arrow))
		self.wait(1)

		#removing coins and arrow and everything except the name of the circle

		# self.remove()

class Counting2(ThreeDScene):

	def NumofCoin(self,num):
		coin1 = Coin(fill_color='#ff0000')
		for i in range(num):
			coin = Coin(fill_color='#ff0000')
			coin.shift(RIGHT*i)
			coin1.add(coin)
		return VGroup(coin1)


	def construct(self):
		red_coin = Coin(fill_color=RED_D)


		one = TextMobject("One ",color=BLACK)
		one.shift(LEFT*3+UP*2)
		one.scale(2)
		one1 = copy.deepcopy(one)
		two = TextMobject("Two ",color=BLACK)
		two.scale(2)
		two1 = copy.deepcopy(two)
		three = TextMobject("Three ",color=BLACK)
		three.scale(2)
		three1 = copy.deepcopy(three)
		two.next_to(one,DOWN*3)	
		two.align_to(one,LEFT)
		three.next_to(two,DOWN*3)
		three.align_to(one,LEFT)

		two1.next_to(one1,DOWN*3)	
		two1.align_to(one1,LEFT)
		three1.next_to(two1,DOWN*3)
		three1.align_to(one1,LEFT)

		arrow1 = TexMobject("\\rightarrow",color=BLACK,fill_color=BLACK)
		arrow2 = TexMobject("\\rightarrow",color=BLACK,fill_color=BLACK)
		arrow3 = TexMobject("\\rightarrow",color=BLACK,fill_color=BLACK)
		arrow1.scale(2)
		arrow2.scale(2)
		arrow3.scale(2)
		
		arrow1.shift(UP*2)	
		one.add(arrow1)
		arrow2.shift(UP*0.5)
		two.add(arrow2)
		arrow3.shift(DOWN)
		three.add(arrow3)


		number = [one,two,three]
		numbers = [one1,two1,three1]
		position = RIGHT+UP*2
		# self.set_camera_orientation(1,np.pi/2)
		self.move_camera(0.7*np.pi/2, -1*np.pi/2)  
		# for i in range(1,4):
		# 	self.play(Write(number[i-1]))
		# 	position_temp = np.copy(position)
		# 	# print(position_temp, position)
		# 	for j in range(i):
		# 		position_temp+=RIGHT*1.2
		# 		coin = Coin(color='#ff0000',fill_color='#ff0000')
		# 		coin.shift(position_temp)
		# 		self.play(GrowFromCenter(coin))
		# 	print("1", position)
		# 	position+=DOWN*1.5
		# 	print("2", position)
		coinL = list()
		for i in range(3):
			self.play(Write(number[i]))
			shw = self.NumofCoin(i+1)
			coinL.append(shw)
			shw.shift(position)
			self.add(shw)
			position+=DOWN*1.6

		self.move_camera(0*np.pi/2, -1*np.pi/2)  
		missing = TextMobject("Extra circle",fill_color=BLACK)
		arrow = Vector(0.5*DOWN+LEFT*0.5, color='#ff0000')
		arrow.shift(LEFT+DOWN*0.15)

		miss = VGroup(missing,arrow)
		miss.shift(RIGHT*4+UP*1.4)
		rect = Rectangle(height=3,width=1,color=BLACK)
		rect.shift(RIGHT+UP*1.25)
		self.play(ShowCreation(rect))
		self.add(miss)
		self.wait(1)
		self.remove(rect,miss)

		rect1 = Rectangle(height=3,width=1.9,color=BLACK)
		missing = TextMobject("Extra circle",fill_color=BLACK)
		arrow = Vector(0.8*UP, color='#ff0000')
		arrow.shift(UP*0.15)
		miss2 = VGroup(missing,arrow)
		miss2.shift(RIGHT*3+DOWN*2.7)
		rect1.shift(RIGHT*1.5+DOWN*0.3)

		self.play(ShowCreation(rect1))
		self.add(miss2)
		self.wait(1)
		self.remove(rect1,miss2)
		self.wait(1)

		# self.remove(arrow1,arrow2,arrow3)

		self.wait(1)
		self.remove(one,two,three)
		great = TexMobject("<",color=BLACK,fill_color=BLACK)
		great.scale(7)
		great.shift(LEFT*3)
		great1 = copy.deepcopy(great)
		great1.shift(RIGHT*5)
		# for i in range(1):
			# self.play((number[i].move_to, RIGHT*3.5+DOWN*0.2),(number[i+1].move_to, RIGHT*2.5+DOWN*0.2),(number[i+2].move_to, RIGHT*1.5+DOWN*0.2))
			# self.play(coinL[i].move_to, RIGHT*3.5+DOWN*0.2),(coinL[i+1].move_to, RIGHT*2.5+DOWN*0.2),(coinL[i+2].move_to, RIGHT*1.5+DOWN*0.2))
			# anim_grp = coinL[0].move_to(RIGHT*3.5+DOWN*0.2), coinL[1].move_to(RIGHT*3.5+DOWN*0.2), coinL[2].move_to(RIGHT*3.5+DOWN*0.2))
		self.play(numbers[0].move_to, LEFT*5+UP,numbers[1].move_to, LEFT*0.5+UP,numbers[2].move_to, RIGHT*5+UP,coinL[0].move_to, LEFT*5.5+DOWN, coinL[1].move_to, LEFT*0.6+DOWN,coinL[2].move_to,RIGHT*5+DOWN)
		self.add(great)
		self.add(great1)
		self.wait(2)

            