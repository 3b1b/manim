from big_ol_pile_of_manim_imports import *

class NameOfScene(Scene):
	def construct(self):
		pass

codigo="""
\\begin{lstlisting}[language=Python,style=basic,numbers=none,showtabs=false]
# This is a comment, is not a code

from big_ol_pile_of_manim_imports import * 	# Old versions

from manimlib.imports import * 				# New versions

class NameOfScene(Scene):
	def construct(self):
		# Animation progress
\\end{lstlisting}
            """
'''
class CheckC1(CheckFormulaByTXT):
	CONFIG={
	"text": TextMobject(codigo),
	"set_size":"width",
	"numbers_scale":0.2,
	}
#'''
AZUL_ST="#64DAF8"
NARANJA_ST="#FF9514"
MORADO_ST="#A682FE"
class SceneConfig(Scene):
	def construct(self):
		texto=TextMobject(codigo,color=WHITE).to_edge(UP)
		com_sup=texto[:26].set_color(GRAY)
		old_from=texto[26:77]
		texto[26:30].set_color(ROSA_ST)
		texto[58:64].set_color(ROSA_ST)
		texto[64].set_color(MORADO_ST)
		texto[77:81].set_color(ROSA_ST)
		texto[97:103].set_color(ROSA_ST)
		texto[103].set_color(MORADO_ST)
		texto[116:121].set_color(AZUL_ST)
		texto[140:143].set_color(AZUL_ST)
		texto[153:157].set_color(NARANJA_ST)
		VGroup(texto[121:132],texto[133:138],texto[143:152]).set_color(VERDE_ST)
		VGroup(texto[159:],texto[65:77],texto[104:116]).set_color(GRAY)

		self.play(Escribe(texto))
		self.wait(10)

		self.play(Indicate(texto[121:132]))

		texto_error1=TextMobject("\\tt 1NameOfScene",color=VERDE_ST).shift(RIGHT*3)
		texto_error2=TextMobject("\\tt class",color=VERDE_ST).next_to(texto_error1,DOWN,aligned_edge=LEFT)
		texto_error2c=TextMobject("\\tt Class",color=VERDE_ST).next_to(texto_error2,DOWN,aligned_edge=LEFT)
		correcto=TextMobject(r"""
			\tikz\fill[scale=0.4](0,.35) -- (.25,0) -- (1,.7) -- (.25,.15) -- cycle;
			""",fill_opacity=1,stroke_width=1,color=GREEN).next_to(texto_error2c,RIGHT)
		self.play(Write(texto_error1),Write(texto_error2),Write(texto_error2c))
		cross1=Cross(texto_error1)
		cross2=Cross(texto_error2)
		self.wait(1)
		self.play(ShowCreation(cross1),ShowCreation(cross2),DrawBorderThenFill(correcto))
		self.wait(7)
		texto_correcto2=TextMobject("\\tt Name\\_of\\_scene2",color=VERDE_ST).next_to(texto_error2c,DOWN,aligned_edge=LEFT)
		correcto2=correcto.copy().next_to(texto_correcto2,RIGHT)
		self.play(Escribe(texto_correcto2),DrawBorderThenFill(correcto2))
		self.wait(5)
		tab1=DashedLine(texto[140].get_left(),np.array([texto[116].get_left()[0],texto[140].get_left()[1],0]))
		self.play(ShowCreationThenDestruction(tab1))
		tab2=tab1.copy().scale(2).next_to(texto[159],LEFT,buff=0)
		self.wait(5)

		rec1=SurroundingRectangle(texto[140:159],submobject_mode = "lagged_start")
		t_method=TextMobject("$\\leftarrow$ Method").next_to(texto[158],RIGHT,buff=0.3)
		self.play(ShowCreation(rec1),FadeInFrom(t_method,LEFT))
		self.wait(15)
		self.play(FadeOut(rec1),FadeOut(t_method))
		self.play(ShowCreationThenDestruction(tab1,submobject_mode = "lagged_start"),ShowCreationThenDestruction(tab2,submobject_mode = "lagged_start"))
		self.wait(4)

class NextVideo(Scene):
	def construct(self):
		self.wait(0.3)
		titulo=TextMobject("Next video: ").to_corner(UL)
		ul=underline(titulo)
		self.play(FadeInFrom(titulo,UP),ShowCreation(ul))
		escala=1.5
		textos=VGroup(
			TextMobject("Hello world!").scale(escala),
			TextMobject("\\sl See you in the next video").scale(escala),
			TextMobject("\\sf If you liked give me a like.").scale(escala),
			TextMobject("\\it If you did not like give me a dislike.").scale(escala),
			TextMobject("\\sc Until next time").scale(escala)
			)
		textos.arrange_submobjects(DOWN,buff=0.4).set_color_by_gradient(RED,BLUE,PURPLE)
		tim=0.3
		self.play(Escribe(textos[0]))
		self.wait(tim)
		self.play(FadeIn(textos[1]))
		self.wait(tim)
		self.play(GrowFromCenter(textos[2]))
		self.wait(tim)
		self.play(Write(textos[3]))
		self.wait(tim)
		self.play(DrawBorderThenFill(textos[4]))
		self.wait(tim)
		self.wait(3)

