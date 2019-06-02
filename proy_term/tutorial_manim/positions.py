from big_ol_pile_of_manim_imports import *

class OrientedObjectProgramming(Scene):
	def construct(self):
		titulo=Texto("Oriented-Object Programming").to_edge(UP)
		ul_titulo=underline(titulo)

		objeto = Circle(color=RED)
		t_objeto=Texto("\\it Object")
		objeto.move_to(LEFT*objeto.get_width())
		t_objeto.next_to(objeto,DOWN,buff=SMALL_BUFF*2)
		centro_objeto=Dot()
		centro_objeto.move_to(objeto.get_center())
		punta_flecha=Dot().fade(1)
		punta_flecha.move_to(centro_objeto.get_center()+objeto.get_width()*RIGHT/2)
		punta_flecha.rotate(35*DEGREES,about_point=centro_objeto.get_center())
		flecha=Flecha(centro_objeto,punta_flecha)
		def update_flecha(flecha):
			new_flecha=Flecha(centro_objeto,punta_flecha)
			flecha.become(new_flecha)
		

		propiedades=VGroup(
			Texto("Properties:"),
			Texto("1. Color"),
			Texto("2. Radius"),
			Texto("3. Stroke"),
			Texto("4. Opacity"),
			Formula("\\vdots")
			).arrange_submobjects(DOWN,aligned_edge=LEFT).move_to(RIGHT*2)
		propiedades[1:].shift(RIGHT*0.5)
		propiedades[1].add_updater(lambda m: m.set_color(objeto.get_color()))
		propiedades[3].add_updater(lambda m: m.set_stroke(None,objeto.get_stroke_width()*0.5-2))
		propiedades[4].add_updater(lambda m: m.fade(1-objeto.get_stroke_opacity()))

		igual=Formula("=").next_to(propiedades[2],RIGHT,buff=SMALL_BUFF*1.4)
		decimal = DecimalNumber(
            0,
            show_ellipsis=False,
            num_decimal_places=2,
            include_sign=False,
        ).next_to(igual,RIGHT,buff=SMALL_BUFF*1.3)
		decimal.add_updater(lambda d: d.set_value(objeto.get_width()/2))

		self.play(Escribe(titulo),GrowFromCenter(ul_titulo))
		self.play(ShowCreation(objeto),Escribe(t_objeto),FadeIn(centro_objeto),FadeIn(punta_flecha))
		self.add_foreground_mobject(centro_objeto)
		self.play(GrowArrow(flecha))
		flecha.add_updater(update_flecha)
		centro_objeto.add_updater(lambda m: m.move_to(objeto.get_center()))
		punta_flecha.add_updater(
			lambda m: m.move_to(centro_objeto.get_center()+objeto.get_width()*RIGHT/2)\
					   .rotate(35*DEGREES,about_point=centro_objeto.get_center())
			)
		t_objeto.add_updater(lambda m: m.next_to(objeto,DOWN,buff=SMALL_BUFF*2))
		self.play(LaggedStart(FadeIn,propiedades))
		self.wait()
		self.play(ApplyMethod(objeto.set_color,YELLOW))
		self.play(FadeIn(igual),FadeIn(decimal))
		self.play(ApplyMethod(objeto.scale,2))
		self.play(ApplyMethod(objeto.set_stroke,None,11))
		self.play(ApplyMethod(objeto.set_stroke,None,None,0.2))
		self.wait()
		self.play(FadeOut(propiedades),FadeOut(centro_objeto),FadeOut(flecha),FadeOut(decimal),FadeOut(igual))

		objeto2=objeto.copy().set_stroke(None,None,0)
		self.play(objeto2.move_to,RIGHT*2,objeto2.scale,0.5,objeto2.set_stroke,BLUE,4,1)
		t_objeto2=Texto("\\it Object 2").next_to(objeto2,DOWN,buff=SMALL_BUFF*1.3)
		self.play(Escribe(t_objeto2))
		self.wait()
		self.play(*[FadeOut(obj)for obj in [objeto2,objeto,t_objeto2,t_objeto]])

		cambio_propiedades=Formula("object.","function","(","parameters",")",alignment="\\tt")
		cambio_propiedades[1].set_color(BLUE)
		cambio_propiedades[-2].set_color(ORANGE)

		cambio_propiedades.scale(2)
		KeyBoard(self,cambio_propiedades[0])
		KeyBoard(self,cambio_propiedades[1])
		KeyBoard(self,cambio_propiedades[2])
		KeyBoard(self,cambio_propiedades[3])
		KeyBoard(self,cambio_propiedades[4])

		self.wait()

class AbsolutePositions(Scene):
	def construct(self):
		t_to_edge=Texto("\\tt .to\\_edge()")
		t_to_edge[1:-2].set_color(BLUE)
		t_to_corner=Texto("\\tt .to\\_corner()")
		t_to_corner[1:-2].set_color(BLUE)
		t_move_to=Texto("\\tt .move\\_to()")
		t_move_to[1:-2].set_color(BLUE)
		t_next_to=Texto("\\tt .next\\_to()")
		t_next_to[1:-2].set_color(BLUE)
		t_shift=Texto("\\tt .shift()")
		t_shift[1:-2].set_color(BLUE)

		pos_abs=VGroup(t_to_edge,t_to_corner).arrange_submobjects(DOWN,aligned_edge=LEFT)
		b_pos_abs=Brace(pos_abs,LEFT)
		t_pos_abs=b_pos_abs.get_text("Absolute positions")
		g_pos_abs=VGroup(pos_abs,b_pos_abs,t_pos_abs)

		pos_rel=VGroup(t_move_to,t_next_to,t_shift).arrange_submobjects(DOWN,aligned_edge=LEFT)
		b_pos_rel=Brace(pos_rel,LEFT)
		t_pos_rel=b_pos_rel.get_text("Relative positions")
		g_pos_rel=VGroup(pos_rel,b_pos_rel,t_pos_rel)

		pos=VGroup(g_pos_abs,g_pos_rel).arrange_submobjects(DOWN,aligned_edge=LEFT)
		b_pos=Brace(pos,LEFT)
		t_pos=b_pos.get_text("Positions")
		g_pos=VGroup(pos,b_pos,t_pos)

		g_pos.move_to(ORIGIN)

		objeto = Dot(color=RED).to_edge(UP)

		obj_vista=VGroup()

		self.play(Escribe(t_pos))
		obj_vista.add(t_pos)
		self.wait(2)
		self.play(GrowFromCenter(b_pos))
		obj_vista.add(b_pos)
		self.wait(2)
		self.play(Escribe(t_pos_abs),Escribe(t_pos_rel))
		obj_vista.add(t_pos_abs,t_pos_rel)
		self.wait(2)
		self.play(FadeToColor(t_pos_abs,RED))
		self.play(GrowFromCenter(objeto))
		self.wait(2)
		for d in [DOWN,LEFT,RIGHT]:
			self.play(objeto.to_edge,d)
		self.play(objeto.scale,0)
		self.wait(2)

		self.play(GrowFromCenter(b_pos_abs))
		obj_vista.add(b_pos_abs)
		KeyBoard(self,t_to_edge)
		obj_vista.add(t_to_edge)
		self.wait()

		self.play(FadeOut(obj_vista))

		def Codigo(texto):
			texto_c=TikzMobject("""
\\begin{lstlisting}[language=Python,style=basic,numbers=none]
%s
\\end{lstlisting}
			"""%texto).set_stroke(None,0).set_fill(WHITE,1)
			return texto_c

		direcciones = VGroup(*[Codigo("%s"%d)
			for d in ["UP    = np.array([ 0, 1,0])",
					  "DOWN  = np.array([ 0,-1,0])",
					  "LEFT  = np.array([-1, 0,0])",
					  "RIGHT = np.array([ 1, 0,0])"]],
					  ).arrange_submobjects(DOWN,aligned_edge=LEFT)
		num_in=[2,4,4,5]
		for d,n in zip(direcciones,num_in):
			d[n].set_color(ROSA_ST)
			d[n+4:n+4+5].set_color(BLUE)
		direcciones.move_to(ORIGIN)
		self.play(LaggedStart(FadeIn,direcciones))
		self.wait(2)

		pos_to_edge=VGroup(*[Texto("\\tt .to\\_edge(%s)"%d)for d in ["UP","DOWN","LEFT","RIGHT"]]).scale(0.7)
		puntos_to_edge=VGroup(*[Dot().to_edge(pos)for pos in [UP,DOWN,LEFT,RIGHT]]).set_color(RED)
		for pos,p_te,d in zip(pos_to_edge,puntos_to_edge,[UP,DOWN,LEFT,RIGHT]):
			pos[1:8].set_color(BLUE)
			pos.next_to(p_te,-d,buff=SMALL_BUFF*1.3)
		for obj1,obj2 in zip(puntos_to_edge,pos_to_edge):
			self.play(LaggedStart(GrowFromCenter,obj1),LaggedStart(FadeIn,obj2))
			self.wait(1.5)

		self.play(FadeOut(pos_to_edge),FadeOut(puntos_to_edge),FadeOut(direcciones))
		self.wait(2)

		self.play(FadeIn(obj_vista))
		KeyBoard(self,t_to_corner)

		self.wait()

		self.play(FadeOut(obj_vista),FadeOut(t_to_corner))

		direcciones_mixtas = VGroup(*[Codigo("%s"%d)
			for d in ["UR = np.array([ 1, 1,0])",
					  "UL = np.array([-1, 1,0])",
					  "DR = np.array([ 1,-1,0])",
					  "DL = np.array([-1,-1,0])"]]
					  ).arrange_submobjects(DOWN,aligned_edge=LEFT)
		direcciones_mixtas.move_to(ORIGIN)

		num_in2=[2,2,2,2]
		for d,n in zip(direcciones_mixtas,num_in2):
			d[n].set_color(ROSA_ST)
			d[n+4:n+4+5].set_color(BLUE)

		self.play(LaggedStart(FadeIn,direcciones_mixtas))

		pos_to_corner=VGroup(*[Texto("\\tt .to\\_corner(%s)"%d)for d in ["UR","UL","DR","DL"]])
		puntos_to_corner=VGroup(*[Dot().to_edge(pos)for pos in [UR,UL,DR,DL]]).set_color(RED)
		for pos,p_te,d in zip(pos_to_corner,puntos_to_corner,[UR,UL,DR,DL]):
			pos[1:10].set_color(BLUE)
			pos.next_to(p_te,-d,buff=SMALL_BUFF*1.3)
		for obj1,obj2 in zip(puntos_to_corner,pos_to_corner):
			self.play(LaggedStart(GrowFromCenter,obj1),LaggedStart(FadeIn,obj2))
			self.wait(1.5)

		self.wait(2)

		self.play(FadeOut(pos_to_corner),FadeOut(puntos_to_corner),FadeOut(direcciones_mixtas))

		punto_esquina=Dot().to_edge(LEFT,buff=-0.08)
		punto_movimiento=Dot(color=YELLOW).scale(3).to_edge(LEFT,buff=1.5)
		linea_mov=Line(punto_esquina.get_center(),punto_movimiento.get_left()).fade(1)
		med=Medicion(linea_mov,dashed=True,buff=0.5).add_tips()
		t_buff=Texto(r"\textit{\texttt{buff}}$=$").next_to(punto_movimiento,UR)
		t_buff[:-1].set_color(ORANGE)
		t_buff[-1].set_color(ROSA_ST)
		decimal = DecimalNumber(
            0,
            show_ellipsis=False,
            num_decimal_places=2,
            include_sign=False,
        ).next_to(t_buff,RIGHT,buff=SMALL_BUFF*1.3)

		decimal.add_updater(lambda m: m.set_value(linea_mov.get_length()).next_to(t_buff,RIGHT,buff=SMALL_BUFF*1.3))
		self.play(
			GrowFromCenter(med),
			Escribe(VGroup(t_buff,decimal)),
			GrowFromCenter(punto_movimiento)
			)
		self.add(linea_mov)

		def update_med(med):
			new_med=Medicion(linea_mov,dashed=True,buff=0.5).add_tips()
			med.become(new_med)

		def update_lin(linea_mov):
			new_linea_mov=Line(punto_esquina.get_center(),punto_movimiento.get_left()).fade(1)
			linea_mov.become(new_linea_mov)

		linea_mov.add_updater(update_lin)
		med.add_updater(update_med)
		t_buff.add_updater(lambda m: m.next_to(punto_movimiento,UR))

		self.play(punto_movimiento.shift,LEFT,run_time=5)
		self.wait(2)

		self.play(
			*[FadeOut(obj)for obj in [decimal,t_buff,med,punto_movimiento]]
			)

		#'''
		t_pos_abs.set_color(WHITE)
		t_pos_rel.set_color(RED)
		self.play(FadeIn(obj_vista),FadeIn(t_to_corner))
		self.wait(2)
		self.play(GrowFromCenter(b_pos_rel))
		self.wait(2)
		for obj in pos_rel:
			KeyBoard(self,obj)
			self.wait(2)

		self.wait(2)


		#self.play(GrowFromCenter(b_pos_abs))
		#self.wait(2)
		#'''

class Grid(VMobject):
    CONFIG = {
        "height": 6.0,
        "width": 6.0,
    }

    def __init__(self, rows, columns, **kwargs):
        digest_config(self, kwargs, locals())
        VMobject.__init__(self, **kwargs)

    def generate_points(self):
        x_step = self.width / self.columns
        y_step = self.height / self.rows

        for x in np.arange(0, self.width + x_step, x_step):
            self.add(Line(
                [x - self.width / 2., -self.height / 2., 0],
                [x - self.width / 2., self.height / 2., 0],
            ))
        for y in np.arange(0, self.height + y_step, y_step):
            self.add(Line(
                [-self.width / 2., y - self.height / 2., 0],
                [self.width / 2., y - self.height / 2., 0]
            ))


class ScreenGrid(VGroup):
    CONFIG = {
        "rows":8,
        "columns":14,
        "height": FRAME_Y_RADIUS*2,
        "width": 14,
        "grid_stroke":0.5,
        "grid_color":WHITE,
        "axis_color":RED,
        "axis_stroke":2,
        "show_points":False,
        "point_radius":0,
        "labels_scale":0.5,
        "labels_buff":0,
        "number_decimals":2,
        "fade":0.5
    }

    def __init__(self,**kwargs):
        VGroup.__init__(self,**kwargs)
        rows=self.rows
        columns=self.columns
        grilla=Grid(width=self.width,height=self.height,rows=rows,columns=columns).set_stroke(self.grid_color,self.grid_stroke)

        vector_ii=ORIGIN+np.array((-self.width/2,-self.height/2,0))
        vector_id=ORIGIN+np.array((self.width/2,-self.height/2,0))
        vector_si=ORIGIN+np.array((-self.width/2,self.height/2,0))
        vector_sd=ORIGIN+np.array((self.width/2,self.height/2,0))

        ejes_x=Line(LEFT*self.width/2,RIGHT*self.width/2)
        ejes_y=Line(DOWN*self.height/2,UP*self.height/2)

        ejes=VGroup(ejes_x,ejes_y).set_stroke(self.axis_color,self.axis_stroke)

        divisiones_x=self.width/columns
        divisiones_y=self.height/rows

        direcciones_buff_x=[UP,DOWN]
        direcciones_buff_y=[RIGHT,LEFT]
        dd_buff=[direcciones_buff_x,direcciones_buff_y]
        vectores_inicio_x=[vector_ii,vector_si]
        vectores_inicio_y=[vector_si,vector_sd]
        vectores_inicio=[vectores_inicio_x,vectores_inicio_y]
        tam_buff=[0,0]
        divisiones=[divisiones_x,divisiones_y]
        orientaciones=[RIGHT,DOWN]
        puntos=VGroup()
        leyendas=VGroup()


        for tipo,division,orientacion,coordenada,vi_c,d_buff in zip([columns,rows],divisiones,orientaciones,[0,1],vectores_inicio,dd_buff):
            for i in range(1,tipo):
                for v_i,direcciones_buff in zip(vi_c,d_buff):
                    ubicacion=v_i+orientacion*division*i
                    punto=Dot(ubicacion,radius=self.point_radius)
                    coord=round(punto.get_center()[coordenada],self.number_decimals)
                    leyenda=TextMobject("%s"%coord).scale(self.labels_scale).fade(self.fade)
                    leyenda.next_to(punto,direcciones_buff,buff=self.labels_buff)
                    puntos.add(punto)
                    leyendas.add(leyenda)

        self.add(grilla,ejes,leyendas)
        if self.show_points==True:
            self.add(puntos)

class RelativePosition1(Scene):
	def construct(self):
		grilla=ScreenGrid()
		dot=Dot()
		coord=Formula("(1,2)")
		self.add(grilla)
		self.wait()
		self.play(GrowFromCenter(dot))
		self.play(dot.move_to,RIGHT+UP*2)
		coord.next_to(dot,RIGHT)
		self.play(FadeIn(coord))
		self.wait(3)

class RelativePosition2(Scene):
	def construct(self):
		grilla=ScreenGrid()
		dot=Dot()
		text=Texto("Text").move_to(3*LEFT+2*UP)
		dot.move_to(text)
		self.add(grilla)
		self.wait()
		self.play(Escribe(text))
		self.play(GrowFromCenter(dot))
		self.wait()
		self.play(dot.shift,RIGHT*5)
		self.wait(7)

class RelativePositionMT(Scene):
	def construct(self):
		grilla=ScreenGrid()
		dot=Dot()
		text=Texto("Text").move_to(3*LEFT+2*UP)
		dot.move_to(text)
		self.add(grilla)
		self.wait()
		self.play(Escribe(text))
		self.play(GrowFromCenter(dot))
		self.wait()
		self.play(dot.shift,RIGHT*5)
		self.wait()
		linea=Line(text.get_center(),dot.get_center())
		med=Medicion(linea,dashed=True).add_tips()
		self.add(med)

class RelativePositionNT(Scene):
	def construct(self):
		grilla=ScreenGrid()
		dot=Dot()
		text=Texto("Text").move_to(3*LEFT+2*UP)
		dot.next_to(text,RIGHT,buff=5)
		self.add(grilla)
		self.wait()
		self.play(Escribe(text))
		self.play(GrowFromCenter(dot))
		self.wait()
		linea=Line(text.get_right(),dot.get_left())
		med=Medicion(linea,dashed=True).add_tips()
		self.add(med)

class RotateP(Scene):
	def construct(self):
		grid=ScreenGrid()
		cod=Formula("\\tt object.","rotate","(","110*DEGREES,","\\mbox{\\textit{\\texttt{about\\_point}}}","=","point",")")
		cod[1].set_color(BLUE)
		cod[4].set_color(ORANGE)
		cod[5].set_color(ROSA_ST)

		dot1=Dot().shift(UP)
		dot2=Dot().move_to(1*DOWN)
		t_dot1=TextMobject("\\tt dot1").next_to(dot1,DOWN+LEFT,buff=SMALL_BUFF)
		t_dot2=TextMobject("\\tt dot2").next_to(dot2,DOWN+LEFT,buff=SMALL_BUFF)

		remark=TextMobject("\\texttt{point} is a coord, not a object.").to_edge(UP)
		cod.to_edge(DOWN)

		self.add(grid)
		self.play(GrowFromCenter(dot1),Escribe(t_dot1))
		self.play(GrowFromCenter(dot2),Escribe(t_dot2))

		t_dot2.add_updater(lambda m: m.next_to(dot2,DOWN+LEFT,buff=SMALL_BUFF))
		self.play(Write(cod))

		arc=Arc(110*DEGREES,radius=2,arc_center=dot1.get_center(),start_angle=-90*DEGREES)

		self.play(Rotate(dot2,110*DEGREES,about_point=dot1.get_center()),ShowCreation(arc))

		self.play(Write(remark))
		self.wait()

class FormulasLatex(Scene):
	def construct(self):
		for1=Formula(r"\int_a^b f(x)dx")
		for2=Formula(r"\lim_{x\to\infty}\frac{1}{x}=0")
		for3=Formula(r"\frac{d}{dx}f(x)=\lim_{h\to 0}\frac{f(x+h)-f(x)}{h}")
		for4=Formula(r"e^{\pi i}+1=0")
		for5=Formula(r"\rho\frac{D{\bf u}}{Dt}=-\nabla p + \nabla\cdot\tau + \rho{\bf g}")
		form=VGroup(
			for1,
			for2,
			for3,
			for4,
			).set_color_by_gradient(PURPLE,ORANGE,BLUE)
		for obj,pos in zip(form,[UR,UL,DR,DL]):
			obj.to_corner(pos)
		self.play(*[Escribe(obj)for obj in form], Escribe(for5))
		self.wait(4)

class MoveToScene(Scene):
	def construct(self):
		grid=ScreenGrid()
		self.add(grid)

		move_to_center=Formula("\\tt .move\\_to(","vector)")
		move_to_center[0][1:-1].set_color(BLUE)
		move_to_object=Formula("\\tt .move\\_to(","reference\\_object.","get\\_center","()+vector)")
		move_to_object[0][1:-1].set_color(BLUE)
		move_to_object[2].set_color(BLUE)
		t_move_to=VGroup(move_to_center,move_to_object).arrange_submobjects(DOWN,aligned_edge=LEFT)
		t_move_to.to_corner(DL)
		rec=Rectangle(width=t_move_to.get_width(),height=t_move_to.get_height()).move_to(t_move_to)\
			.set_stroke(None,0,0).set_fill(BLACK,0.8)

		punto=Dot()
		cuadro=Square(fill_opacity=1).match_width(punto).set_color(YELLOW)
		flecha=VFlecha(ORIGIN,2*UP+3*RIGHT).set_color(PURPLE)
		t_flecha=TextMobject("\\tt vector")

		self.play(GrowFromCenter(punto))
		self.wait(2)
		self.play(FadeIn(rec))
		KeyBoard(self,move_to_center[0])
		KeyBoard(self,move_to_center[1])
		self.wait(3)
		self.add_foreground_mobject(punto)
		self.play(punto.move_to,2*UP+3*RIGHT,GrowArrow(flecha))
		self.wait(3)
		t_flecha.next_to(flecha,DOWN,buff=0.2)
		self.play(ReplacementTransform(flecha[0].copy(),t_flecha))
		self.wait(3)
		KeyBoard(self,move_to_object[0])
		KeyBoard(self,move_to_object[1])
		KeyBoard(self,move_to_object[2])
		KeyBoard(self,move_to_object[3])

		cuadro.move_to(DOWN+LEFT*2)
		flecha_cuadro=VFlecha(cuadro.get_center(),cuadro.get_center()+3*UP+LEFT).set_color(PURPLE)

		self.play(ReplacementTransform(move_to_object[1].copy(),cuadro))
		self.wait(2)
		self.add_foreground_mobject(cuadro)
		self.play(ReplacementTransform(flecha,flecha_cuadro),punto.move_to,cuadro.get_center()+3*UP+LEFT,
				  t_flecha.next_to,flecha_cuadro,DOWN,{"buff":0.2})
		self.wait(2)






