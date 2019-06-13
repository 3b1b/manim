from big_ol_pile_of_manim_imports import *

h_resulution=420
v_frame_rate=12
video_parameters=[
    ("pixel_height",h_resulution),
    ("pixel_width",int(h_resulution*16/9)),
    ("frame_rate",v_frame_rate)
]
for v_property,v_value in video_parameters:
    LOW_QUALITY_CAMERA_CONFIG[v_property]=v_value

def piramide(n,**kwargs):
	grupo_piramides=VGroup()
	pasos=list(range(1,n+1))
	pasos.reverse()
	for i in pasos:
		nivel=VGroup(*[Square(**kwargs)for w in range(i)])
		nivel.arrange_submobjects(RIGHT,buff=0)
		if i<n:
			nivel.next_to(grupo_piramides,UP,buff=0)
		grupo_piramides.add(nivel)
	return grupo_piramides

class Piramides(Scene):
	CONFIG={
	"te":0,
	}
	def espera(self):
		self.wait(self.te)

	def construct(self):
		self.muestra_titulo()
		self.ejemplos_piramides()


	def muestra_titulo(self):
		tikz="""
		\\begin{tikzpicture}[pencildraw/.style={decorate,
		decoration={random steps,segment length=0.8pt,amplitude=0.3pt}}]
		    \\node[pencildraw,draw] {\\sc Suma(toria)};
		\\end{tikzpicture} 
		  """
		tit=TikzMobject(tikz,stroke_width=2,fill_opacity=.1,color=WHITE).scale(3)
		tit[0].set_fill(BLACK,1)
		tit[1:].set_stroke(None,0).set_fill(WHITE,1)
		titulo=escribe_texto(self,tit[1:])
		self.add_foreground_mobject(tit[0])
		self.add_foreground_mobject(tit[1:])
		self.play(Write(tit[0]))
		esq_left=tit[1:].get_left()
		esq_right=tit[1:].get_right()
		cuerda_left=Line(esq_left+UP*5,esq_left,color=WHITE)
		cuerda_right=Line(esq_right+UP*5,esq_right,color=WHITE)
		self.play(ShowCreation(cuerda_left),ShowCreation(cuerda_right))
		self.espera()
		self.add_foreground_mobjects(tit[0],tit[1:])
		self.play(
		VGroup(tit[0],cuerda_left,cuerda_right,titulo,tit[1:]).shift,UP*8
		)
	

	def ejemplos_piramides(self):
		titulo=TextoB("Acertijo").to_edge(UP)
		ul=underline(titulo)
		lado_piramides=0.8
		color_inicial=GREEN_D
		color_final=BLUE_D
		piramide_1=piramide(1,side_length=lado_piramides).set_fill(interpolate_color(color_inicial,color_final,0),1)
		piramide_2=piramide(2,side_length=lado_piramides).set_fill(interpolate_color(color_inicial,color_final,0.33),1)
		piramide_3=piramide(3,side_length=lado_piramides).set_fill(interpolate_color(color_inicial,color_final,0.66),1)
		num_1=TextoB("1")
		num_2=TextoB("2")
		num_3=TextoB("3")
		num_2_1=TextoB("1")
		num_3_2=TextoB("2")
		num_3_1=TextoB("1")
		num_100=TextoB("100")
		#piramide_4=piramide(4,side_length=lado_piramides).set_fill(interpolate_color(color_inicial,color_final,1),1)
		conjunto_piramides_1=VGroup(piramide_1,piramide_2,piramide_3).arrange_submobjects(RIGHT,buff=0.5,aligned_edge=DOWN)
		#conjunto_piramides_1.set_submobject_colors_by_gradient(YELLOW,RED)
		dots=FormulaB("\\dots").scale(1.2)
		conjunto_piramides_1.to_edge(LEFT)
		dots.next_to(conjunto_piramides_1,RIGHT,buff=1)
		pregunta=TextoB("Numero de cuadrados\\\\ de pirámide de base 1000").to_edge(RIGHT)
		for obj,i in zip([num_1,num_2,num_3],range(3)):
			obj.next_to(conjunto_piramides_1[i],DOWN,buff=0.6)
		respuesta_pregunta=FormulaB("\\mbox{\\rm Pirámide}_{base=100}=","1+2+3+4+\\cdots+99+100").scale(1.2)
		otra_pregunta=Texto("¿Existe una forma más rápida?")

		self.play(DrawBorderThenFill(conjunto_piramides_1),
			Write(dots),
			Escribe(pregunta),
			Escribe(titulo),
			ShowCreation(ul),
			*[Escribe(obj)for obj in [num_1,num_2,num_3]]
			)

		self.espera()

		def update(grupo):
			for g,p in zip(grupo,conjunto_piramides_1):
				g.next_to(p,DOWN,buff=0.6)

		self.play(
			pregunta.shift,RIGHT*6,
			dots.shift,RIGHT*7,
			conjunto_piramides_1.arrange_submobjects,RIGHT,{"buff":1.5,"aligned_edge":DOWN},
			conjunto_piramides_1.scale,1.3,
			UpdateFromFunc(Mobject(num_1,num_2,num_3),update)
			)

		self.espera()

		self.play(
					num_1.next_to,conjunto_piramides_1[0][0],RIGHT,{"buff":0.6},
					num_2.next_to,conjunto_piramides_1[1][0],RIGHT,{"buff":0.6},
					num_3.next_to,conjunto_piramides_1[2][0],RIGHT,{"buff":0.6},
					path_arc=PI/2
				)

		self.espera()

		self.play(
			conjunto_piramides_1[1][1].shift,RIGHT*conjunto_piramides_1[1][1].get_width()/2,
			conjunto_piramides_1[2][1].shift,RIGHT*conjunto_piramides_1[2][1].get_width()/4,
			conjunto_piramides_1[2][2].shift,RIGHT*conjunto_piramides_1[2][2].get_width(),
			)

		num_2_1.next_to(conjunto_piramides_1[1][1],RIGHT,buff=0.6)
		num_3_2.next_to(conjunto_piramides_1[2][1],RIGHT,buff=0.6)
		num_3_1.next_to(conjunto_piramides_1[2][2],RIGHT,buff=0.6)

		self.play(*[Write(obj)for obj in [num_2_1,num_3_2,num_3_1]])

		total_1=TextoB("1").next_to(conjunto_piramides_1[0],DOWN,buff=0.6)
		total_2=TextoB("1","+","2").next_to(conjunto_piramides_1[1],DOWN,buff=0.6)
		total_3=TextoB("1","+","2","+","3").next_to(conjunto_piramides_1[2],DOWN,buff=0.6)

		self.play(
			ReplacementTransform(num_1,total_1),
			*[ReplacementTransform(obj1,obj2[:])for obj1,obj2 in zip([num_2,num_2_1],[total_2[2],total_2[0]])],
			*[ReplacementTransform(obj3,obj4[:])for obj3,obj4 in zip([num_3_1,num_3_2,num_3],[total_3[0],total_3[2],total_3[4]])],
			)
		self.play(Write(total_2[1]),Write(total_3[1]),Write(total_3[3]))

		self.espera()

		self.play(
			*[ApplyMethod(obj.shift,LEFT*FRAME_WIDTH)for obj in [total_1,total_2,total_3]],
			*[ApplyMethod(obj1.shift,RIGHT*FRAME_WIDTH)for obj1 in conjunto_piramides_1]
			)

		self.espera()

		self.play(Escribe(respuesta_pregunta[0]))
		self.espera()
		self.play(LaggedStart(Write,respuesta_pregunta[1]))
		otra_pregunta.scale(1.5).next_to(respuesta_pregunta,DOWN,buff=2)

		self.espera()
		self.play(Escribe(otra_pregunta))
		self.espera()
		self.play(
			*[Write(obj,rate_func=lambda t: smooth(1-1.1*t))for obj in [otra_pregunta,respuesta_pregunta,titulo,ul]]
			)
		#self.add(conjunto_piramides_1)
