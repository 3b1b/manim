from big_ol_pile_of_manim_imports import *

class PatreonLogo(Scene):
	def construct(self):

		patreon_png=ImageMobject("patreon_png")
		patreon=Patreon()\
				.set_width(3)\
				.move_to(ORIGIN)
		patreon_png.match_width(patreon)
		grupo=Group(patreon_png,patreon)\
			  .arrange_submobjects(RIGHT)

		self.add(grupo)

class PatreonLogo2(Scene):
	def construct(self):

		patreon_svg=PatreonSVG2().scale(1.5)
		patreon_png=ImageMobject("patreon_png")

		patreon_png.set_width(patreon_svg.get_width())


		grupo=Group(patreon_png,patreon_svg)\
			  .arrange_submobjects(RIGHT)

		self.add(grupo)

class SacaDePantalla(Transform):
	def __init__(self,mobject,direction=UP,**kwargs):
		#mobject.generate_target()
		target = mobject.deepcopy()
		height = target.get_height()/2
		target.move_to((FRAME_Y_RADIUS+height)*UP*direction[1])
		Transform.__init__(self,mobject,target,**kwargs)

class PatreonIntro(Scene):
	def construct(self):
		
		text_1=Texto("""
		\\sc HI!!\\smallskip 

		Welcome to\\\\ 
		my Patreon""").scale(3.5)\
		.set_color_by_gradient(RED,ORANGE)

		text_2=Texto("""
			""")

		self.play(Escribe(text_1))
		self.wait(1.2)
		self.play(
			SacaDePantalla(text_1[:4],direction=UP),
			SacaDePantalla(text_1[4:],direction=DOWN)
			)
		self.wait(0.5)

class SheenObject(Scene):
	def construct(self):
		obj1=Square().set_fill(RED,1).set_stroke(ORANGE,10)
		obj1.set_sheen(0.6,UP,family=False)

		self.add(obj1)

class InstagramScene(Scene):
	def construct(self):
		instagram=Instagram()
		self.play(DrawBorderThenFill(instagram))
		self.play(instagram.to_edge,LEFT)
		self.wait()

class Instagram2(Scene):
	def construct(self):
		back1=self.color_cell(
			SVGMobject("instagram")[2],
			colors = ["#FED372","#B52C94","#4D67D8"]
			)
		back2=self.color_cell(
			SVGMobject("instagram")[0],
			colors = ["#B52C94"]
			)
		back3=self.color_cell(
			SVGMobject("instagram")[1],
			colors = ["#B83D8D","#8A5DA2","#8A5DA2"]
			)
		back4=self.color_cell(
			SVGMobject("instagram")[3],
			colors = ["#D77A84","#B52C94","#BD368A"],
			vect=[0.2,1,0]
			)

		instagram=VGroup(back1,back2,back3,back4)
		self.play(DrawBorderThenFill(instagram))
		self.play(instagram.to_edge,LEFT)
		#self.add(instagram.set_width(8))
		self.wait()

	def color_cell(self,cell,colors,vect=[0.45,1,0]):
		cell.set_color(color=colors,family=True)
		cell.set_stroke(color=colors)
		cell.set_sheen_direction(vect)
		return cell

