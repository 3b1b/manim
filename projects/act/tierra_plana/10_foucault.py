from big_ol_pile_of_manim_imports import *

class ModeloInicial(Scene):
	CONFIG={
	"angulo_pendulo":30*DEGREES,
	"radio_soporte":4,
	"tam_cuerda":1,
	"radio_masa":0.1,
	"color_cuerda":RED,
	"color_masa":RED,
	"pausa":1
	}
	def esp(self):
		self.wait(self.pausa)

	def construct(self):
		ang=self.angulo_pendulo
		r_s=self.radio_soporte
		r_m=self.radio_masa
		t_c=self.tam_cuerda
		c_c=self.color_cuerda
		c_m=self.color_masa
		tam_sop=0.3
		porc_radio=0.83

		planeta=Planeta()
		ejes=Axes(x_min=-3.5,x_max=3.5,y_min=-3.5,y_max=3.5)

		soporte=Patron(width=tam_sop,height=0.5,stroke_width=2,separacion=0.1,agregar_base=True,direccion="L",grosor=0.1).set_color(WHITE)
		soporte.move_to(RIGHT*r_s)
		soporte.rotate(ang,about_point=ORIGIN)

		vect_lat=VFlecha(ORIGIN,RIGHT*(r_s-tam_sop/2),buff=0)
		vect_lat.rotate(ang,about_point=ORIGIN,about_edge=ORIGIN)

		ang_lat=Arco(ang,radio=porc_radio*r_s)

		e_cuerda=Line(ORIGIN,vect_lat[-2].get_end()).get_unit_vector()
		cuerda=Line(e_cuerda*(r_s-t_c),e_cuerda*(r_s-tam_sop/2),color=c_c)

		masa=Dot(radius=r_m,color=c_m).set_sheen(1).move_to(cuerda.get_start())

		th=Formula("\\theta")
		th.dot=Dot().fade(1).move_to(RIGHT*(porc_radio*r_s+th.get_width()*2))
		th.dot.rotate(ang/2,about_point=ORIGIN,about_edge=ORIGIN)
		th.move_to(th.dot)


		#self.add(planeta,ejes,soporte,vect_lat,ang_lat,cuerda,masa,th,th.dot)
		self.wait(0.5)
		self.play(DrawBorderThenFill(planeta))
		self.esp()
		self.play(Write(ejes))
		self.esp()
		self.play(GrowFromCenter(soporte))
		self.esp()
		self.play(GrowArrow(vect_lat))
		self.esp()
		self.add(th.dot)
		self.play(GrowFromPoint(ang_lat,ORIGIN),Write(th))
		self.play(ShowCreation(cuerda),vect_lat.fade,1)
		self.play(GrowFromCenter(masa))


		def update_flecha(flecha,dt):
			new_vect_lat=VFlecha(ORIGIN,RIGHT*(r_s-tam_sop/2),buff=0).fade(1)
			new_vect_lat.rotate(val_theta.get_value(),about_point=ORIGIN,about_edge=ORIGIN)
			vect_lat.become(new_vect_lat)
		def update_soporte(soporte,dt):
			new_soporte=Patron(width=tam_sop,height=0.5,stroke_width=2,separacion=0.1,agregar_base=True,direccion="L",grosor=0.1).set_color(WHITE)
			new_soporte.move_to(RIGHT*r_s)
			new_soporte.rotate(val_theta.get_value(),about_point=ORIGIN)
			soporte.become(new_soporte)
		def updater_cuerda(cuerda,dt):
			e_cuerda=Line(ORIGIN,vect_lat[-2].get_end()).get_unit_vector()
			new_cuerda=Line(e_cuerda*(r_s-t_c),e_cuerda*(r_s-tam_sop/2),color=c_c)
			cuerda.become(new_cuerda)
		def updater_arco(arco,dt):
			new_ang_lat=Arco(val_theta.get_value(),radio=porc_radio*r_s)
			ang_lat.become(new_ang_lat)
		def updater_dot(dot,dt):
			new_dot=Dot().fade(1).move_to(RIGHT*(porc_radio*r_s+th.get_width()*2))
			new_dot.rotate(val_theta.get_value()/2,about_point=ORIGIN,about_edge=ORIGIN)
			th.dot.become(new_dot)




		val_theta=ValueTracker(30*DEGREES)
		soporte.add_updater(update_soporte)
		vect_lat.add_updater(update_flecha)
		cuerda.add_updater(updater_cuerda)
		masa.add_updater(lambda m: m.move_to(cuerda.get_start()))
		ang_lat.add_updater(updater_arco)
		th.dot.add_updater(updater_dot)
		th.add_updater(lambda m: m.move_to(th.dot))

		self.play(ApplyMethod(val_theta.set_value,50*DEGREES),run_time=2)
		self.wait()
        

class Arco(VGroup):
    CONFIG={
    "start_tip":True,
    "end_tip":True,
    "space_dashed":0.5,
    "tam_stop":0.11
    }
    def __init__(self,ang,radio=1,**kwargs):
        VGroup.__init__(self,**kwargs)
        arco=Arc(ang,radius=radio)
        linea_arco=Line(arco.points[-2],arco.points[-1],color=RED)
        if self.start_tip:
            puntas_flecha=self.add_tips(linea_arco)
        if self.end_tip:
            puntas_flecha_final=self.add_tips(Line(arco.points[1],arco.points[0],color=RED))

        linea_tope_1=Line(LEFT*self.tam_stop,RIGHT*self.tam_stop).rotate(arco.get_angle()).move_to(arco.points[-1])
        linea_tope_2=Line(LEFT*self.tam_stop,RIGHT*self.tam_stop).move_to(arco.points[0])
        conjunto=VGroup(DashedMobject(arco),puntas_flecha,puntas_flecha_final,linea_tope_1,linea_tope_2).set_stroke(width=2.2)
        self.add(conjunto)

    def add_tips(self,linea,ang_flechas=27*DEGREES,tam_flechas=0.2):
        linea_referencia=Line(linea.get_start(),linea.get_end())
        vector_unitario=linea_referencia.get_unit_vector()

        punto_final1=linea.get_end()
        punto_inicial1=punto_final1-vector_unitario*tam_flechas
        punto_intermedio=punto_final1-vector_unitario*tam_flechas*0.6

        punto_inicial2=linea.get_start()
        punto_final2=punto_inicial2+vector_unitario*tam_flechas

        lin1_1=Line(punto_inicial1,punto_final1)
        lin1_2=lin1_1.copy()
        lin2_1=Line(punto_inicial2,punto_final2)
        lin2_2=lin2_1.copy()

        lin_int=Line(linea.get_end(),punto_final1-vector_unitario*tam_flechas*0.6)

        lin1_1.rotate(ang_flechas,about_point=punto_final1,about_edge=punto_final1)
        lin1_2.rotate(-ang_flechas,about_point=punto_final1,about_edge=punto_final1)

        lin2_1.rotate(ang_flechas,about_point=punto_inicial2,about_edge=punto_inicial2)
        lin2_2.rotate(-ang_flechas,about_point=punto_inicial2,about_edge=punto_inicial2)

        return VMobject(lin1_1,lin1_2)
