from big_ol_pile_of_manim_imports import *
#Cambiar el color de Texto en tex_mobject.py
h_resulution=420
v_frame_rate=12
video_parameters=[
    ("pixel_height",h_resulution),
    ("pixel_width",int(h_resulution*16/9)),
    ("frame_rate",v_frame_rate)
]
for v_property,v_value in video_parameters:
    LOW_QUALITY_CAMERA_CONFIG[v_property]=v_value

class Formula1(CheckSVG):
    CONFIG={
    #"set_size":"height",
    "stroke_width":0.1,
    "svg_type":"text",
    "show_numbers":True
    }
    def import_text(self):
        return Formula("f","(","x",",","y",",","z",")=","x","\\cdot","a","+","{","y","+","z","\\over","b","}")

class Receta(Scene):
	CONFIG={
	"te":0.4,
	"color_variables":N_ROJO_1,
	"color_constantes":TT_AZULROYAL_1,
	"color_hoja":N_FONDO_VERDE_PASTEL,
	"color_titulo":PURPLE,
	"opacidad_hoja":0.9
	}
	def espera(self):
		self.wait(self.te)

	def construct(self):
		self.muestra_titulo()
		self.mostrar_receta()
		self.espera()
		todos_elementos=Mobject(*[Mobject(self.mobjects[i])for i in range(len(self.mobjects))])
		self.play(todos_elementos.shift,UP*FRAME_HEIGHT)

	def muestra_titulo(self):
		tikz="""
		\\begin{tikzpicture}[pencildraw/.style={decorate,
		decoration={random steps,segment length=0.8pt,amplitude=0.3pt}}]
		    \\node[pencildraw,draw] {\\sc Funciones};
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

	def mostrar_receta(self):
		hoja=Rectangle(width=6,height=FRAME_HEIGHT).set_stroke(WHITE,2).set_color(self.color_hoja).set_fill(self.color_hoja,self.opacidad_hoja).scale(0.9)
		nombre_receta=Texto("Nombre de la receta",color=self.color_titulo).next_to(hoja.get_top(),DOWN,buff=0.2)
		ul=underline(nombre_receta)
		datos_receta=VGroup(
			Texto("$-$","Ingredientes",color=WHITE).set_color(self.color_variables),
			Texto("$-$","Utensilios",color=WHITE).set_color(self.color_constantes),
			Texto("$-$\\ \\!Procedimiento",color=BLACK),
			Texto("$-$","Resultado",color=BLACK)
			).arrange_submobjects(DOWN,buff=0.7,aligned_edge=LEFT).next_to(ul,DOWN,buff=1.5)

		receta=VGroup(hoja,nombre_receta,ul,datos_receta)
		self.receta_inicial=receta

		self.play(DrawBorderThenFill(hoja),*[Escribe(objeto)for objeto in [nombre_receta,datos_receta]],ShowCreation(ul))

		self.wait(self.te)

		self.play(receta.to_edge,LEFT,{"buff":1.4})

		self.add_foreground_mobject(receta)

		hoja_receta_ejemplo=hoja.copy().to_edge(RIGHT,buff=1.4)

		self.play(ReplacementTransform(hoja.copy(),hoja_receta_ejemplo))

		titulo_agua_limon=Texto("Agua de limón",color=self.color_titulo).next_to(hoja_receta_ejemplo.get_top(),DOWN,buff=0.2)
		ul2=underline(titulo_agua_limon)
		ingredientes=VGroup(
			Texto("$-$","5 limones",color=WHITE).scale(0.8),
			Texto("$-$","2 litros de agua",color=WHITE).scale(0.8),
			Texto("$-$","4 cucharadas de azucar",color=WHITE).scale(0.8),
			#Texto("",color=WHITE),
			).arrange_submobjects(DOWN,buff=0.1,aligned_edge=LEFT).set_color(self.color_variables)
		utensilios=VGroup(
			Texto("$-$","1 jarrón",color=WHITE).scale(0.8),
			Texto("$-$","1 cuchara",color=WHITE).scale(0.8),
			Texto("$-$","1 cuchillo",color=WHITE).scale(0.8),
			#Texto("",color=WHITE),
			).arrange_submobjects(DOWN,buff=0.1,aligned_edge=LEFT).set_color(self.color_constantes)
		procedimiento=VGroup(Texto("""
			$-$\\ \\!Partir y exprimir los limones en un jarrón\\\\
			con los dos litros de agua, luego añadir las\\\\
			cuatro cucharadas de azucar y revolver.
			""",alignment="\\justify").scale(0.5)).arrange_submobjects(DOWN,buff=0.1,aligned_edge=LEFT)
		resultado=VGroup(SVGMobject("jarra")).set_color(GREEN).rotate(PI).scale(0.6)
		receta_limon=VGroup(ingredientes,utensilios,procedimiento,resultado).arrange_submobjects(DOWN,buff=0.6,aligned_edge=LEFT).next_to(titulo_agua_limon.get_top(),DOWN,buff=1.2)
		resultado.next_to(procedimiento,DOWN,buff=0.2)
		cambios=(
			(datos_receta[0],ingredientes),
			(datos_receta[1],utensilios),
			(datos_receta[2],procedimiento),
			)

		self.wait(self.te)

		self.remove_foreground_mobject(receta)

		#self.add_foreground_mobjects(nombre_receta,receta_limon)
		self.play(ReplacementTransform(nombre_receta.copy(),titulo_agua_limon),
			ReplacementTransform(ul.copy(),ul2),
			)

		self.espera()

		for obj1,obj2 in cambios:
			self.play(*[ReplacementTransform(obj1.copy(),obj2[i])for i in range(len(obj2))])

			self.espera()

		self.play(ReplacementTransform(datos_receta[3].copy(),resultado))

		self.wait(self.te)

		receta_limon.add(titulo_agua_limon,ul2,resultado)

		conjunto_limon=VGroup(hoja_receta_ejemplo,receta_limon)

		self.play(receta.shift,LEFT*8,conjunto_limon.to_edge,LEFT,{"buff":1.4})

		self.remove(hoja,nombre_receta,ul,datos_receta)

		hoja_funcion=hoja_receta_ejemplo.copy().to_edge(RIGHT,buff=1.4)
		titulo_funcion=Formula("f",color=self.color_titulo).next_to(hoja_funcion.get_top(),DOWN,buff=0.2)
		ul3=underline(titulo_funcion)
		variables=VGroup(
			Formula("-\\ ","x",color=WHITE).scale(0.8),
			Formula("-\\ ","y",color=WHITE).scale(0.8),
			Formula("-\\ ","z",color=WHITE).scale(0.8),
			).arrange_submobjects(DOWN,buff=0.1,aligned_edge=LEFT).set_color(self.color_variables)
		constantes=VGroup(
			Formula("-\\ ","a",color=WHITE).scale(0.8),
			Formula("-\\ ","b",color=WHITE).scale(0.8),
			).arrange_submobjects(DOWN,buff=0.1,aligned_edge=LEFT).set_color(self.color_constantes)
		#							   0     1      2   3   4   5   6   7     8     9    10
		procedimiento_funcion=Formula("x","\\cdot","a","+","{","y","+","z","\\over","b","}",
			tex_to_color_map={"x":self.color_variables,
			"y":self.color_variables,
			"z":self.color_variables,
			"a":self.color_constantes,
			"b":self.color_constantes})
		#				 0   1   2   3   4   5   6    7   8     9      10  11  12 13  14  15    16     17  18
		funcion=Formula("f","(","x",",","y",",","z",")=","x","\\cdot","a","+","{","y","+","z","\\over","b","}",
			tex_to_color_map={"x":self.color_variables,
			"y":self.color_variables,
			"z":self.color_variables,
			"a":self.color_constantes,
			"b":self.color_constantes,
			"f":self.color_titulo}).scale(0.9)
		receta_funcion=VGroup(
			variables,constantes,procedimiento_funcion,funcion
			).arrange_submobjects(DOWN,buff=0.6,aligned_edge=LEFT).next_to(titulo_funcion.get_top(),DOWN,buff=1.2)
		procedimiento_funcion.shift(RIGHT)

		brazo_variables=Brace(variables,RIGHT)
		texto_brazo_variables=brazo_variables.get_text("Pueden variar")

		brazo_constantes=Brace(constantes,RIGHT)
		texto_brazo_constantes=brazo_constantes.get_text("No varían")

		self.add_foreground_mobjects(conjunto_limon)

		self.play(ReplacementTransform(hoja_receta_ejemplo.copy(),hoja_funcion))

		self.remove_foreground_mobjects(conjunto_limon)

		self.wait(self.te)

		for obj in [VGroup(titulo_funcion,ul3),variables,constantes]:
			self.play(Escribe(obj))

		self.wait(self.te)

		self.play(GrowFromCenter(brazo_variables),Escribe(texto_brazo_variables),run_time=1.2)
		self.wait(self.te)
		self.play(GrowFromCenter(brazo_constantes),Escribe(texto_brazo_constantes),run_time=1.2)

		self.wait(self.te)

		self.play(
			brazo_constantes.fade,0.79,
			brazo_variables.fade,0.79,
			texto_brazo_constantes.fade,0.79,
			texto_brazo_variables.fade,0.79,
			)

		self.espera()

		signos_procedimiento_funcion=[
		procedimiento_funcion[1],
		procedimiento_funcion[3],
		procedimiento_funcion[6],
		procedimiento_funcion[8],
		]
		pre_variables_constantes_procedimiento_funcion=[
		variables[0][1],
		constantes[0][1],
		variables[1][1],
		variables[2][1],
		constantes[1][1],
		]
		pos_variables_constantes_procedimiento_funcion=[
		procedimiento_funcion[0],
		procedimiento_funcion[2],
		procedimiento_funcion[5],
		procedimiento_funcion[7],
		procedimiento_funcion[9]
		]

		self.play(*[Write(obj)for obj in signos_procedimiento_funcion])

		self.espera()

		self.play(*[ReplacementTransform(obj1.copy()[:],obj2)
			for obj1,obj2 in zip(pre_variables_constantes_procedimiento_funcion,pos_variables_constantes_procedimiento_funcion)],
			run_time=3)

		self.espera()

		self.play(
			ReplacementTransform(titulo_funcion[:].copy(),funcion[0],run_time=2),
			Escribe(VGroup(funcion[1],funcion[3],funcion[5],funcion[7])),run_time=2
			)

		self.espera()

		self.play(ReplacementTransform(procedimiento_funcion.copy()[:],funcion[8:]),run_time=2.5)

		self.espera()

		pre_variables_xyz=[
		variables[0][1],
		variables[1][1],
		variables[2][1],
		]
		pos_variables_xyz=[
		funcion[2],
		funcion[4],
		funcion[6],
		]

		self.play(*[ReplacementTransform(obj1.copy()[:],obj2)for obj1,obj2 in zip(pre_variables_xyz,pos_variables_xyz)],run_time=2.5)

		self.espera()



