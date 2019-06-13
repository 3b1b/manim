from big_ol_pile_of_manim_imports import *
from Proyectos.ecuacion_2do_grado.formulas.formulas import *
#Inicia parametros -----------------------------------------
a_color=RED_B
b_color=BLUE_B
c_color=GREEN_B
x_color=YELLOW_B
#line_class

class CasoE(Scene):
	def construct(self):
		self.importar_formulas()
		self.imprime_formula()
		self.paso_1()
		#'''

	def importar_formulas(self):
		self.formulas=[]
		self.formulas.append(TexMobject("\\lim_{x\\to\\infty}{1\\over x}=0").to_edge(RIGHT))
		self.formulas.append(TexMobject("\\lim_{x\\to\\infty}{1\\over x}=0").to_edge(LEFT))

	def imprime_formula(self):
		self.play(Write(self.formulas[0]))


		
	def paso_1(self):
		#Parámetros
		paso=1
		cambios = [[
						(0,3,4,5,1,8,9,10),
						(0,3,4,5,1,8,9,10)
		]]
		pre_fade=[]
		pre_write=[]

		fade = []
		write = []
		
		post_fade=[]
		post_write= []

		arco=0

		copias=[]
		copia_fin=[]
		formula_copia=[] #No modificar
		for c in copias: #No modificar
			formula_copia.append(self.formulas[paso-1][c].copy()) #No modificar
		#Parametros extra
		#self.formulas[paso][].shift(RIGHT*0.2)
		#Caso especial
		#	Variables
		#Inicia escena------------------------
		#self.add(self.formulas[paso-1])
		#self.play(*[FadeOut(self.formulas[paso-1][f])for f in pre_fade])
		#self.play(*[Write(self.formulas[paso-1][f])for f in pre_write])
		for pre_ind,post_ind in cambios:
			self.play(*[
				ReplacementTransform(
					self.formulas[paso-1][i],self.formulas[paso][j],
					path_arc=arco
					)
				for i,j in zip(pre_ind,post_ind)
				],
				*[FadeOut(self.formulas[paso-1][f])for f in fade],
				*[Write(self.formulas[paso][w])for w in write],
				*[ReplacementTransform(formula_copia[j],self.formulas[paso][f])
				for j,f in zip(range(len(copia_fin)),copia_fin)
				],
				run_time=4
			)
			self.wait()
		#self.play(*[FadeOut(self.formulas[paso][f])for f in post_fade])
		#self.play(*[Write(self.formulas[paso][f])for f in post_write])