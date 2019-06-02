from big_ol_pile_of_manim_imports import *

class QueSonLosArreglos(Scene):
	def espera(self,factor=3):
		self.wait(factor)

	def construct(self):
		ej_texto=TexMobject("\\tt norm\\_text","=","TextMobject","(","\\mbox{``","Text","''}",")").scale(1.3)
		#                          0            1       2         3      4          5
		ej_arreglo=TexMobject("\\tt array\\_text","=","TextMobject","(","\\mbox{``T''}",",","\\mbox{``e''}",",","\\mbox{``x''}",",","\\mbox{``t''}",")").scale(1.3)
		#                             0            1        2        3         4         5           6       7          8        9          10
		esc_arreglos=VGroup(*[TexMobject("\\tt array\\_text","\\mbox{\\tt [%s]}"%i,"=")for i in range(4)])
		esc_arreglos.arrange_submobjects(DOWN)
		for i in range(len(esc_arreglos)):
			esc_arreglos[i][2].set_color(ROSA_ST)
			esc_arreglos[i][1][1].set_color(MORADO_ST)

		ej_texto_c=ej_texto[0].copy()
		ej_arreglo_c=ej_arreglo[0].copy()

		ej_texto[1].set_color(ROSA_ST)
		ej_texto[4:7].set_color(AMARILLO_ST)
		ej_arreglo[1].set_color(ROSA_ST)
		ej_texto[2].set_color(AZUL_ST)
		ej_arreglo[2].set_color(AZUL_ST)
		ej_arreglo_grupo=VGroup()
		for i in [4,6,8,10]:
			ej_arreglo[i].set_color(AMARILLO_ST)
			ej_arreglo_grupo.add(ej_arreglo[i])

		texto_objetos,texto_lineas,texto_brace=self.listamemoria(["$\\cdots$","Text","$\\cdots$"],add_listado=False,escala=2)
		arreglo_objetos,arreglo_lineas,arreglo_brace,arreglo_listado=self.listamemoria(["$\\cdots$","T"," e"," x"," t","$\\cdots$"])
		arreglo_text=TextMobject("T"," e"," x"," t").set_color(AMARILLO_ST)
		esc_arreglos.next_to(arreglo_lineas,DOWN).shift(LEFT)

		texto_lista=VGroup(texto_objetos,texto_lineas,texto_brace)
		arreglo_lista=VGroup(arreglo_objetos,arreglo_lineas,arreglo_brace,arreglo_listado)

		grupo_normal=VGroup(texto_lista,ej_texto_c,ej_texto).arrange_submobjects(DOWN,buff=0.3)
		grupo_arreglo=VGroup(arreglo_lista,ej_arreglo_c,ej_arreglo).arrange_submobjects(DOWN)
		grupo_arreglo_new=VGroup(arreglo_lista,ej_arreglo_c,ej_arreglo_grupo)

		ej_texto_c.next_to(texto_brace,UP)
		ej_arreglo_c.next_to(arreglo_brace,UP)

		for i,w in zip(range(len(arreglo_text)),[4,6,8,10]):
			arreglo_text[i].match_width(ej_arreglo[w][2])
			arreglo_text[i].move_to(ej_arreglo[w][2])

		self.play(Escribe(ej_texto))
		self.espera()
		self.play(ShowCreation(texto_lineas),Write(texto_objetos[0]),Write(texto_objetos[-1]))
		self.espera()
		self.play(ReplacementTransform(ej_texto[5].copy(),texto_objetos[1][:]),run_time=2)
		self.espera()
		self.play(GrowFromCenter(texto_brace))
		self.espera()
		self.play(ReplacementTransform(ej_texto[0].copy(),ej_texto_c),run_time=2)
		self.espera()
		self.play(
			grupo_normal[0:2].move_to,UP*FRAME_Y_RADIUS+UP*grupo_normal[0:2].get_center(),
			grupo_normal[2].move_to,DOWN*FRAME_Y_RADIUS+UP*grupo_normal[2].get_center()
			)
		self.espera()

		self.play(Escribe(ej_arreglo))
		self.espera()
		self.play(ShowCreation(arreglo_lineas),Write(arreglo_objetos[0]),Write(arreglo_objetos[-1]),run_time=2)
		self.espera()
		for i,d in zip(range(len(arreglo_text)),arreglo_objetos[1:-1]):
			self.play(ReplacementTransform(arreglo_text[i],d[:]))
		self.espera()
		self.play(GrowFromCenter(arreglo_brace))
		self.espera()
		self.play(ReplacementTransform(ej_arreglo[0].copy(),ej_arreglo_c),run_time=2)
		self.espera()
		self.play(LaggedStart(Write,arreglo_listado),run_time=2)
		self.espera()
		self.play(
				ReplacementTransform(ej_arreglo[0][:],esc_arreglos[0][0]),
				*[ReplacementTransform(ej_arreglo[0].copy()[:],esc_arreglos[i][0])for i in range(1,4)],
				*[FadeOut(ej_arreglo[w])for w in [1,2,3,5,7,9,11]],run_time=2
			)
		self.espera()
		self.play(
				*[ReplacementTransform(arreglo_listado[i].copy()[:],esc_arreglos[i][1][:])for i in range(4)],run_time=2
			)
		self.espera()
		self.play(*[Write(esc_arreglos[i][2])for i in range(len(esc_arreglos))],run_time=2)
		self.espera()
		self.play(
				*[ApplyMethod(ej_arreglo[i].next_to,d,RIGHT)for i,d in zip([4,6,8,10],esc_arreglos)],run_time=2
			)
		self.espera()
		self.play(
			Escribe(grupo_arreglo_new,rate_func=lambda t: smooth(1-t)),
			Escribe(esc_arreglos,rate_func=lambda t: smooth(1-t)),
			)
		self.espera()
		
	def listamemoria(self,parametros,buff_line=0.9,buff_x=0.25,buff=0.9,direccion_listado=DOWN,color=AMARILLO_ST,escala=1.6,brace_direccion=UP,buff_brace=0.8,add_listado=True):
		objetos=VGroup(*[TextMobject(obj).scale(escala)for obj in parametros]).scale(1)
		for obj in range(1,len(parametros)-1):
			objetos[obj].set_color(color)
		objetos.arrange_submobjects(RIGHT,buff=buff)
		grupo_lineas=VGroup()
		linea_sup=Line(objetos.get_corner(UL)+LEFT*buff_line,objetos.get_corner(UR)+RIGHT*buff_line)\
				 .shift(UP*buff_x)
		linea_inf=Line(objetos.get_corner(DL)+LEFT*buff_line,objetos.get_corner(DR)+RIGHT*buff_line)\
				 .shift(DOWN*buff_x)

		lineas_transversales=VGroup()
		for i in range(1,len(parametros)):
			coord=(objetos[i-1].get_center()-objetos[i].get_center())/2+objetos[i].get_center()
			linea_trans=Line(linea_sup.get_center(),linea_inf.get_center())
			linea_trans.move_to(coord)
			lineas_transversales.add(linea_trans)

		brace=Brace(Line(lineas_transversales[0].get_center(),lineas_transversales[-1].get_center()),brace_direccion,buff=buff_brace)
		
		listado=VGroup()
		for i in range(1,len(parametros)-1):
			label=TextMobject("\\tt [%s]"%(i-1)).next_to(objetos[i],direccion_listado,buff=2*buff_x)
			label[1].set_color(MORADO_ST)
			if i>1:
				coord_x=label.get_center()[0]
				coord_y=listado[0].get_center()[1]
				vect_pos=np.array([coord_x,coord_y,0])
				label.move_to(vect_pos)
			listado.add(label)


		grupo_lineas.add(linea_sup,linea_inf,lineas_transversales)

		if add_listado:
			return objetos,grupo_lineas,brace,listado
		else:
			return objetos,grupo_lineas,brace
