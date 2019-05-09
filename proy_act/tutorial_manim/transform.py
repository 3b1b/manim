from big_ol_pile_of_manim_imports import *

codigo1="""
\\begin{lstlisting}[language=Python,style=basic,numbers=none,showtabs=false]
class WhatIsTransform(Scene):
	def construct(self):
		M1 = TextMobject("|\\rm A|")
		M2 = TextMobject("|\\rm B|")
		M3 = TextMobject("|\\rm C|")
		M4 = TextMobject("|\\rm D|")
		self.add(M1)
		self.wait()

		self.play(Transform(M1,M2))
		self.wait()

		self.play(Transform(M1,M3))
		self.wait()

		self.play(Transform(M1,M4))
		self.wait()

		self.play(FadeOut(M1))
\\end{lstlisting}
            """

codigo2="""
\\begin{lstlisting}[language=Python,style=basic,numbers=none,showtabs=false]
class WhatIsReplacementTransform(Scene):
	def construct(self):
		M1 = TextMobject("|\\rm A|")
		M2 = TextMobject("|\\rm B|")
		M3 = TextMobject("|\\rm C|")
		M4 = TextMobject("|\\rm D|")
		self.add(1)
		self.wait()

		self.play(ReplacementTransform(M1,M2))
		self.wait()

		self.play(ReplacementTransform(M2,M3))
		self.wait()

		self.play(ReplacementTransform(M3,M4))
		self.wait()

		self.play(FadeOut(M4))
\\end{lstlisting}
            """
'''
class CheckC1(CheckFormulaByTXT):
	CONFIG={
	"text": TextMobject(codigo1),
	"set_size":"height",
	"numbers_scale":0.2,
	}
'''
'''
class CheckC2(CheckFormulaByTXT):
	CONFIG={
	"text": TextMobject(codigo2),
	"set_size":"height",
	"numbers_scale":0.2,
	}
#'''

class EjemploTransform(Scene):
	def construct(self):
		self.muestra_codigo()
		self.muestra_lista()
		self.transform_lista()
		self.explicacion_transform()
		self.explicacion_replacementtransform()
		self.wait()

	def muestra_codigo(self):
		texto=Texto(codigo1)
		texto[:5].set_color("#64DAF8")
		texto[5:20].set_color(VERDE_ST)
		texto[21:26].set_color(VERDE_ST)
		texto[31:40].set_color(VERDE_ST)
		VGroup(texto[41:45],
			   texto[123:127],
			   texto[135:139],
			   texto[146:150],
			   texto[173:177],
			   texto[184:188],
			   texto[211:215],
			   texto[222:226],
			   texto[249:253],
			   texto[260:264]).set_color("#FF9514")
		VGroup(texto[28:31],
			   texto[123+5:127+4],
			   texto[135+5:139+5],
			   texto[146+5:150+5],
			   texto[173+5:177+5],
			   texto[184+5:188+5],
			   texto[211+5:215+5],
			   texto[222+5:226+5],
			   texto[249+5:253+5],
			   texto[260+5:264+5],
			   texto[50:61],
			   texto[69:80],
			   texto[88:99],
			   texto[107:118],
			   texto[156:165],
			   texto[194:203],
			   texto[232:241],
			   texto[270:277],
			   ).set_color("#64DAF8")
		VGroup(texto[49],
			texto[68],
			texto[87],
			texto[106]).set_color(ROSA_ST)
		VGroup(texto[62:62+3],
			   texto[81:81+3],
			   texto[100:100+3],
			   texto[119:119+3]).set_color(AMARILLO_ST)
		self.texto=texto
		self.texto_1=texto[:146]
		self.texto_2=texto[146:]
		self.play(Escribe(self.texto_1))
		#self.add(self.texto_1)


	def muestra_lista(self):
		lista1=self.listamemoria(["$\\cdots$","``A''","``B''","``C''","``D''","$\\cdots$"])
		grupo_comillas=VGroup()
		for obj,color in zip(*[lista1[1:5]],[RED,BLUE,GREEN,ORANGE]):
			obj[2].set_color(color)
			obj[0:2].set_color(YELLOW)
			obj[3:5].set_color(YELLOW)
			grupo_comillas.add(obj[0:2],obj[3:5])
		#Escribe(lista1[:-2]),
		lista1.next_to(self.texto_1,DOWN,buff=0.5)
		self.play(Escribe(grupo_comillas),LaggedStart(ShowCreation,lista1[-2]),Escribe(VGroup(lista1[0],lista1[-3])))
		self.lista1=lista1
		self.wait()

	def listamemoria(self,parametros,buff_line=0.9,buff_x=0.25,buff=0.5,direccion_listado=DOWN):
		objetos=VGroup(*[TextMobject(obj)for obj in parametros]).scale(1)
		objetos.arrange_submobjects(RIGHT,buff=buff)
		grupo_lineas=VGroup()
		linea_sup=Line(objetos.get_corner(UL)+LEFT*buff_line,objetos.get_corner(UR)+RIGHT*buff_line)\
				 .shift(UP*buff_x)
		linea_inf=Line(objetos.get_corner(DL)+LEFT*buff_line,objetos.get_corner(DR)+RIGHT*buff_line)\
				 .shift(DOWN*buff_x)

		lineas_transversales=VGroup()
		for i in range(1,len(parametros)-2):
			coord=(objetos[i].get_center()+(objetos[i].get_center()-objetos[i+1].get_center())/2)
			linea_trans=Line(linea_sup.get_center(),linea_inf.get_center())
			linea_trans.move_to(coord)
			lineas_transversales.add(linea_trans)

		for i in range(len(parametros)-4,len(parametros)-2):
			coord=(objetos[i+1].get_center()-(objetos[i].get_center()-objetos[i+1].get_center())/2)
			linea_trans=Line(linea_sup.get_center(),linea_inf.get_center())
			linea_trans.move_to(coord)
			lineas_transversales.add(linea_trans)
		
		listado=VGroup()
		for i in range(1,len(parametros)-1):
			label=TextMobject("\\tt M%s"%i).next_to(objetos[i],direccion_listado,buff=2*buff_x)
			listado.add(label)


		grupo_lineas.add(linea_sup,linea_inf,lineas_transversales)
		objetos.add(grupo_lineas,listado)

		return objetos

	def transform_lista(self):
		flecha=Dedo1().flip().scale(0.6)
		flecha.next_to(self.texto[65])
		renglones=[84,103,122,134]
		grupo_letras=VGroup(*[self.texto[i]for i in [63,82,101,120]])
		grupo_m_texto=VGroup(*[self.texto[i:i+2]for i in [47,66,85,104]])
		grupo_m_pre=VGroup(*[TextMobject("\\tt M%s"%i).match_width(obj).move_to(obj)for i,obj in zip(range(1,5),grupo_m_texto)])
		grupo_letras_pre=VGroup(*[TextMobject(i).match_width(obj).move_to(obj).match_color(obj)for i,obj in zip(["A","B","C","D"],grupo_letras)])
		grupo_m_lista=VGroup(*self.lista1[-1])
		self.play(Write(flecha))
		contador1=0
		for obj_c,obj_l,obj_mt,obj_ml,reng in zip(grupo_letras_pre,*[self.lista1[1:6]],grupo_m_pre,grupo_m_lista,renglones):
			if contador1>1:
				run_time=0.7
				wait_time=0.3
				move_time=0.3
			else:
				run_time=2
				wait_time=2
				move_time=1
			if contador1==3:
				move_time=1
				wait_time=1.5
			self.play(ReplacementTransform(obj_mt,obj_ml),run_time=run_time)
			self.play(ReplacementTransform(obj_c[:],obj_l[2][:]),run_time=run_time)
			self.wait(wait_time)
			self.play(flecha.next_to,self.texto[reng],run_time=move_time)
			contador1=contador1+1

		self.pantalla=Square(color=WHITE).scale(0.8).next_to(self.lista1,DOWN)
		esc1=1.6
		self.Ap=self.lista1[1][2].copy().scale(esc1).move_to(self.pantalla)
		self.Bp=self.lista1[2][2].copy().scale(esc1)
		self.Cp=self.lista1[3][2].copy().scale(esc1)
		self.Dp=self.lista1[4][2].copy().scale(esc1)
		
		self.play(ShowCreation(self.pantalla))
		self.play(ReplacementTransform(self.lista1[1][2].copy(),self.Ap))
		#self.add(self.Ap)
		self.wait(2)
		self.play(Write(flecha,rate_func=lambda t: smooth(1-t)))
		self.play(FadeOut(self.texto_1),self.lista1.to_edge,UP)
		self.wait(2)
		grupo_pantalla=VGroup(self.pantalla,self.Ap)
		self.play(grupo_pantalla.scale,1.3,
			      grupo_pantalla.move_to,LEFT*4.5)
		self.flecha=flecha

	def explicacion_transform(self):
		grupo_m1_texto=VGroup(*[self.texto[i:i+2]for i in [166,204,242,278]])
		grupo_m_texto=VGroup(*[self.texto[i:i+2]for i in [169,207,245]])
		#for obj,color in zip(grupo_m_texto,[BLUE_B,GREEN_B,TT_NARANJA_T]):
		#	obj.set_color()
		grupo_m_lista=VGroup(*self.lista1[-1])
		grupo_letras_lista=VGroup(*[w[2] for w in self.lista1[1:6]])
		self.gll=grupo_letras_lista.copy()
		self.texto_2.to_edge(RIGHT).shift(UP*1.3+LEFT*3)
		for letra in [self.Bp,self.Cp,self.Dp]:
			letra.match_width(self.Ap)
			letra.move_to(self.Ap)
		self.play(Escribe(self.texto_2))
		self.add(self.texto_2)
		flecha=Dedo1().flip().scale(0.4)
		posiciones_flecha=[172,210,248,281]
		flecha.next_to(self.texto[posiciones_flecha[0]],RIGHT)
		#flecha.fade(0).set_stroke(None,2).set_fill(None,1)

		self.play(Indicate(grupo_m_lista[0]),
			*[Indicate(obj)for obj in grupo_m1_texto],
			run_time=1.3)
		self.wait()
		self.wait(2)

		grupo_proyeccion=VGroup()
		grupo_cuadros=[]

		#p1=Dot(self.lista1[-2][-1][0].get_end())

		#'''
		for punto in range(4):
			cuadro=[]
			cuadro.append(self.lista1[-2][-1][punto].get_end())
			cuadro.append(self.lista1[-2][-1][punto].get_start())
			cuadro.append(self.lista1[-2][-1][punto+1].get_start())
			cuadro.append(self.lista1[-2][-1][punto+1].get_end())
			grupo_cuadros.append(cuadro)

		dl=0.3

		for punto in range(4):
			lt=VGroup()
			lt.add(DashedLine(grupo_cuadros[punto][0],self.pantalla.get_corner(DL),dash_lenght=dl))
			lt.add(DashedLine(grupo_cuadros[punto][1],self.pantalla.get_corner(UL),dash_lenght=dl))
			lt.add(DashedLine(grupo_cuadros[punto][2],self.pantalla.get_corner(UR),dash_lenght=dl))
			lt.add(DashedLine(grupo_cuadros[punto][3],self.pantalla.get_corner(DR),dash_lenght=dl))
			grupo_proyeccion.add(lt)

		rectangulos=VGroup()
		for punto in range(4):
			rectangulos.add(Polygon(grupo_cuadros[punto][0],grupo_cuadros[punto][1],grupo_cuadros[punto][2],grupo_cuadros[punto][3]).set_color(PURPLE))
		#'''

		#--------------------------
		grupo_proyeccion.fade(0.75)
		self.grupo_proyeccion=grupo_proyeccion.copy()
		self.rectangulos=rectangulos
		self.vars=VGroup(self.Ap,self.Bp,self.Cp,self.Dp).copy()
		#self.add(p1)
		self.play(LaggedStart(ShowCreation,grupo_proyeccion[0]),ShowCreation(rectangulos[0]),FadeToColor(self.pantalla,PURPLE))
		self.add_foreground_mobject(grupo_proyeccion[0])
		self.wait(2)
		self.play(Write(flecha))

		new_letter=grupo_letras_lista[1].copy()
		self.play(FadeOut(grupo_letras_lista[0]),
			new_letter.move_to,grupo_letras_lista[0],
			ReplacementTransform(self.Ap,self.Bp),run_time=2.5)
		self.wait(2)

		self.play(flecha.next_to,self.texto[posiciones_flecha[1]])
		self.wait(2)

		new_letter2=grupo_letras_lista[2].copy()
		self.play(FadeOut(new_letter),
			new_letter2.move_to,grupo_letras_lista[0],
			ReplacementTransform(self.Bp,self.Cp),run_time=2.5)
		self.wait(2)

		self.play(flecha.next_to,self.texto[posiciones_flecha[2]])
		self.wait(2)

		new_letter3=grupo_letras_lista[3].copy()
		self.play(FadeOut(new_letter2),
			new_letter3.move_to,grupo_letras_lista[0],
			ReplacementTransform(self.Cp,self.Dp),run_time=2.5)
		self.wait(2)

		self.play(flecha.next_to,self.texto[posiciones_flecha[3]])
		self.wait(2)

		self.play(FadeOut(self.Dp),
			LaggedStart(ShowCreation,
				grupo_proyeccion[0],
				rate_func=lambda t: smooth(1-t)),
			FadeOut(rectangulos[0]),
			FadeToColor(self.pantalla,WHITE))
		self.play(Write(flecha,rate_func=lambda t:smooth(1-t)))
		self.wait(2)
		self.play(FadeOut(new_letter3),FadeIn(self.gll[0]))
		self.Vp=VGroup(*grupo_letras_lista[1:])
		self.wait(2)

	def explicacion_replacementtransform(self):
		self.texto2=TextMobject(codigo2)
		t1=self.texto[156:173];rt1=self.texto2[177:194];wrt1=self.texto2[166:177]
		t2=self.texto[194:211];rt2=self.texto2[226:243];wrt2=self.texto2[215:226]
		t3=self.texto[232:249];rt3=self.texto2[275:292];wrt3=self.texto2[264:275]
		t4=self.texto[279];rt4=self.texto2[322];
		self.texto2[166:186].set_color("#64DAF8")
		self.texto2[215:235].set_color("#64DAF8")
		self.texto2[264:284].set_color("#64DAF8")
		self.texto2[156:325].move_to(self.texto_2,aligned_edge=LEFT)
		self.play(
			ReplacementTransform(t1,rt1),
			ReplacementTransform(t2,rt2),
			ReplacementTransform(t3,rt3),
			ReplacementTransform(t4,rt4),
			Escribe(wrt1),Escribe(wrt2),Escribe(wrt3),FadeIn(self.vars[0])
			)
		self.play(LaggedStart(ShowCreation,self.grupo_proyeccion[0]),ShowCreation(self.rectangulos[0]),FadeToColor(self.pantalla,PURPLE))
		flecha=Dedo1().flip().scale(0.4)
		posiciones_flecha=[193,242,291,324]
		flecha.next_to(self.texto2[posiciones_flecha[0]])
		self.add(self.gll)

		self.play(FadeIn(flecha))
		self.wait(2)

		for i in range(1,4):
			#pre_var=self.gll[i].copy()

			self.play(
				FadeOut(self.gll[i-1],run_time=2.5),
				ApplyMethod(self.Vp[i-1].move_to,self.gll[i-1],run_time=2.5),
				ReplacementTransform(self.vars[i-1],self.vars[i],run_time=2.5),
				ReplacementTransform(self.rectangulos[i-1],self.rectangulos[i],run_time=2.5),
				ReplacementTransform(self.grupo_proyeccion[i-1],self.grupo_proyeccion[i],run_time=2.5),
				)
			self.wait(2)
			#self.gll[i](pre_var)
			self.play(ApplyMethod(flecha.next_to,self.texto2[posiciones_flecha[i]]))
			self.wait(2)

		self.play(FadeOut(self.Dp),
			LaggedStart(ShowCreation,
				self.grupo_proyeccion[-1],
				rate_func=lambda t: smooth(1-t)),
			ShowCreation(self.rectangulos[-1],rate_func=lambda t:smooth(1-t)),
			FadeToColor(self.pantalla,WHITE),
			FadeOut(self.vars[-1]))

		self.play(Write(flecha,rate_func=lambda t:smooth(1-t)))

		self.wait()

		
		
