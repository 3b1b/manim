from big_ol_pile_of_manim_imports import *


class BielaManivelaCorredera(Scene):
	CONFIG={
		"a":2,
		"b":-6.5,
		"c":1.7,
		"theta_in":70,
		"theta_fin":70-3*360,
		"biela_color":RED,
		"manivela_color":BLUE,
		"piston_color":GREEN,
		"ancla_color":PURPLE,
		"grosor_linea":10
	}
	def construct(self):
		O2=Dot().shift(LEFT*4+DOWN*1.5)
		a=self.a
		b=self.b
		c=self.c
		theta_in=self.theta_in
		theta_fin=self.theta_fin
		biela_color=self.biela_color
		piston_color=self.piston_color
		radio=0.08

		base_down=Patron(8,0.3,direccion="U",agregar_base=True,grosor=0.1,color=WHITE)
		base_up=Patron(8,0.3,direccion="D",agregar_base=True,grosor=0.1,color=WHITE)
		base_down[0:-1].shift(0.1*DOWN)
		base_up[0:-1].shift(0.1*UP)
		punto_ancla=Dot(O2.get_center(),radius=radio)
		semi_circulo_ancla=Dot(O2.get_center(),radius=0.3,color=self.ancla_color)
		rect_ancla=Square(side_length=0.6).set_stroke(None,0).set_fill(self.ancla_color,1).move_to(O2.get_center()+DOWN*semi_circulo_ancla.get_width()/2)
		patron_ancla=Patron(0.9,0.2,color=self.ancla_color,separacion=0.1,direccion="U",agregar_base=True,grosor=0.1).next_to(rect_ancla,DOWN,buff=0)
		ancla=VGroup(semi_circulo_ancla,rect_ancla,patron_ancla)

		titulo=Texto("\\sc Animar mecanismos",color=WHITE).scale(1.5).to_corner(UL).shift(RIGHT)
		underline=Line(titulo.get_corner(DL),titulo.get_corner(DR)).shift(DOWN*0.1)

		biela 		=self.posicion_biela(O2.get_center(),theta_in,a,biela_color)
		theta_3		=np.arcsin((a*np.sin(theta_in*DEGREES)-c)/b)*180/PI
		piston  	=self.posicion_piston(O2.get_center(),theta_in,theta_3,a,b,c,piston_color)
		manivela  	=Line(biela.get_end(),piston.get_center()).set_stroke(self.manivela_color,self.grosor_linea)
		punto_bm	=Dot(biela.get_end(),radius=radio)
		punto_mp	=Dot(manivela.get_end(),radius=radio)
		grupo   	=VGroup(biela,piston,manivela,punto_mp,punto_bm)

		base_down.next_to(piston,DOWN,buff=0).shift(LEFT)
		base_up.next_to(piston,UP,buff=0).shift(LEFT)
		self.play(Escribe(titulo),ShowCreation(underline))
		self.play(*[FadeIn(objeto)for objeto in [ancla,base_up,base_down]],
					ShowCreation(biela),DrawBorderThenFill(piston),ShowCreation(manivela),
					GrowFromCenter(punto_mp),GrowFromCenter(punto_bm),GrowFromCenter(punto_ancla),
					)
		self.add_foreground_mobject(punto_ancla)

		def update(grupo,alpha):
			dx 			=interpolate(theta_in, theta_fin, alpha)
			biela 		=self.posicion_biela(O2.get_center(),dx,self.a,self.biela_color)

			theta_3=np.arcsin(np.sign(dx)*((self.a*np.sin(dx*DEGREES)-self.c)/self.b))

			piston 		=self.posicion_piston(O2.get_center(),dx,theta_3*180/PI,self.a,self.b,self.c,self.piston_color)
			manivela 	=Line(biela.get_end(),piston.get_center()).set_stroke(self.manivela_color,self.grosor_linea)
			punto_bm	=Dot(biela.get_end(),radius=radio)
			punto_mp	=Dot(manivela.get_end(),radius=radio)

			nuevo_grupo =VGroup(biela,piston,manivela,punto_mp,punto_bm)
			grupo.become(nuevo_grupo)
			return grupo

		self.play(UpdateFromAlphaFunc(grupo,update),run_time=6,rate_func=double_smooth)

	def posicion_biela(self,origen,theta_2,longitud,color):
		punto_final_x=longitud*np.cos(theta_2*DEGREES)
		punto_final_y=longitud*np.sin(theta_2*DEGREES)
		punto_final=origen+np.array([punto_final_x,punto_final_y,0])
		biela=Line(origen,punto_final,color=color).set_stroke(None,self.grosor_linea)
		return biela

	def posicion_piston(self,origen,theta_2,theta_3,a,b,c,color):
		d=a*np.cos(theta_2*DEGREES)-b*np.cos(theta_3*DEGREES)
		punto_final=origen+RIGHT*d+UP*c
		piston=Rectangle(color=color,height=1,witdh=1.5).set_fill(color,0.7).scale(0.7).move_to(origen+RIGHT*d+UP*c)
		return piston

