from big_ol_pile_of_manim_imports import *

AZUL_ST="#64DAF8"
NARANJA_ST="#FF9514"
MORADO_ST="#A682FE"

def dist(ob1,ob2):
	d=ob1.get_right()-ob2.get_left()
	return abs(d[0]*0.9)

def postext(texto,obj):
	ancho=texto.get_width()
	obj[-1].shift(RIGHT*ancho)
	texto.next_to(obj[0],RIGHT,buff=0.05)

class CheckC1(CheckFormulaByTXT):
	CONFIG={
	"text": TextMobject(r"\tt class ObjectPosition","(","Scene","):",tex_to_color_map={
								"ObjectPosition": VERDE_ST,
								"class" : AZUL_ST,
								"Scene": VERDE_ST,
							 }),
	"scale":0.7,
	"set_size":"width",
	"numbers_scale":0.2,
	}

class ObjectPosition(Scene):
	def construct(self):
		relativeText=TextMobject("\\tt ``Reference text''").set_color(AMARILLO_ST)
		text=TextMobject("\\tt ``Text''").set_color(AMARILLO_ST)
		codigo1=TextMobject(r"""\tt
class ObjectPosition(Scene):\\
\ \ \ \ def construct(self):\\
\ \ \ \ \ \ \ \ relativeText = TextMobject(''Relative Text)\\
\ \ \ \ \ \ \ \ object = TextMobject(Text)
			""",
			alignment="\\flushleft",
			color=WHITE,
			tex_to_color_map={
								"TextMobject": AZUL_ST,
								"ObjectPosition": VERDE_ST,
								"class" : AZUL_ST,
								"def": AZUL_ST,
								"construct" : VERDE_ST,
								#"Text": AMARILLO_ST,
								#"Relative Text": AMARILLO_ST,
								"=": ROSA_ST,
								"Scene": VERDE_ST,
								"self":NARANJA_ST
							 }
			)
		#codigo1[-2][-1].set_color(WHITE)

		self.add(codigo1)

class ObjectPosition2(Scene):
	def construct(self):
		relativeText=TextMobject("\\footnotesize\\tt ``Reference text''").set_color(AMARILLO_ST)
		text=TextMobject("\\footnotesize\\tt ``Text''").set_color(AMARILLO_ST)
		direccion=TexMobject("\\tt LEFT*3+2*UP",tex_to_color_map={
								"*": ROSA_ST,
								"3" : MORADO_ST,
								"2": MORADO_ST,
							 })
		agregar=TextMobject("\\footnotesize\\tt referenceText,object")
		codigo1=VGroup(
TextMobject(r"\footnotesize\tt class ObjectPosition","(","Scene","):",tex_to_color_map={
								"ObjectPosition": VERDE_ST,
								"class" : AZUL_ST,
								"Scene": VERDE_ST,
							 }),
TextMobject(r"\footnotesize\tt --------"," def construct","(","self","):",tex_to_color_map={
								"def": AZUL_ST,
								"self" : NARANJA_ST,
								"construct": VERDE_ST,
							 }),
TextMobject(r"\footnotesize\tt ----------------"," grid = ScreenGrid","()",tex_to_color_map={
								"ScreenGrid": AZUL_ST,
								"=":ROSA_ST,
							 }),
TextMobject(r"\footnotesize\tt ----------------","self",".","add","(grid)",tex_to_color_map={
								"self": NARANJA_ST,
								"add": AZUL_ST,
							 }),
TextMobject(r"\footnotesize\tt ----------------"," relativeText = TextMobject","()",tex_to_color_map={
								"TextMobject": AZUL_ST,
								"=":ROSA_ST,
							 }),
TextMobject(r"\footnotesize\tt ----------------"," object = TextMobject","()",tex_to_color_map={
								"TextMobject": AZUL_ST,
								"=":ROSA_ST,
							 }),
TextMobject(r"\footnotesize\tt ----------------"," referenceText",".","move\\_to","()",tex_to_color_map={
								"TextMobject": AZUL_ST,
								"=":ROSA_ST,
								"move\\_to": AZUL_ST
							 }),
TextMobject(r"\footnotesize\tt ----------------","self",".","add","()",tex_to_color_map={
								"self": NARANJA_ST,
								"add": AZUL_ST,
							 }),
			).arrange_submobjects(DOWN,aligned_edge=LEFT,buff=0.2)

		#codigo1[-1][-1].set_color(PURPLE)
		for j in range(2):
			for i in [-3,-2,-1]:
				codigo1[j][i].shift(LEFT*dist(codigo1[j][i-1],codigo1[j][i]))

		for j in [3,6,7]:
			for i in [-3,-2,-1]:
				codigo1[j][i].shift(LEFT*dist(codigo1[j][i-1],codigo1[j][i]))
				
		for j in range(2,5):
			for i in [-1]:
				codigo1[j][i].shift(LEFT*dist(codigo1[j][i-1],codigo1[j][i]))
		for i in codigo1[1:]:
			i[0].set_color(BLACK)
			for w in [-1]:
				i[w].shift(LEFT*dist(i[w-1],i[w]))


		postext(relativeText,codigo1[4][-1])
		postext(text,codigo1[5][-1])
		postext(direccion,codigo1[-2][-1])
		postext(agregar,codigo1[-1][-1])


		prim_codigo=VGroup(codigo1,text,relativeText,direccion,agregar)\
						   .to_edge(UP+LEFT).scale(0.7).shift(LEFT*1.5+UP*0.7)

		self.play(Escribe(prim_codigo))
		self.wait()
