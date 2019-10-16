from manimlib.imports import *

class Coord:
    def __init__(self,x,y):
        self.x=x
        self.y=y
        self.coord=np.array([x,y,0])

    def get_coord(self):
        return self.coord

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

class Rate:
    def __init__(self,init_val,increment=None):
        self.val=init_val
        if increment==None:
            self.increment=init_val

    def increment_value(self):
        self.val+=self.increment

    def get_value(self):
        return self.val

    def set_value(self,val):
        self.val=val

class Caja(VMobject):
    def __init__(self,ancho=3,alto=2,tapas=0.95,grosor_tapas=11,stroke_color="#D2B48C",fill_color="#cdab7e",**kwargs):
        digest_config(self, kwargs)
        VMobject.__init__(self, **kwargs)
        self.set_anchor_points([UP*alto+LEFT*ancho/2,
                                LEFT*ancho/2,
                                RIGHT*ancho/2,
                                UP*alto+RIGHT*ancho/2],mode="corners")
        self.set_stroke(width=6)
        tapaI=VMobject().set_anchor_points([self.points[0],self.points[0]+RIGHT*ancho*tapas/2],mode="corners").set_stroke(width=grosor_tapas)
        tapaD=VMobject().set_anchor_points([self.points[-1],self.points[-1]+LEFT*ancho*tapas/2],mode="corners").set_stroke(width=grosor_tapas)
        self.add(tapaI,tapaD)
        self.set_stroke(stroke_color)
        self.set_fill(fill_color,1)

    def tapa_derecha(self):
        return self[2]

    def tapa_izquierda(self):
        return self[1]

class Patreon(VGroup):
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        VGroup.__init__(self, **kwargs)
        patreon_svg=PatreonSVG()
        circ1 = Circle()
        circ2 = Circle()
        rect  = Rectangle(
            width=patreon_svg[2].get_width(),
            height=patreon_svg[2].get_height(),
            )\
            .set_fill(patreon_svg[2].get_color(),1)\
            .set_stroke(None,0)

        circ1.match_style(patreon_svg[0])\
             .match_width(patreon_svg[0])
        circ2.match_style(patreon_svg[1])\
             .match_width(patreon_svg[1])


        for obj,p in zip([circ1,circ2,rect],patreon_svg):
            obj.move_to(p.get_center())
        for obj,p in zip([circ2,rect],patreon_svg[1:]):
            obj.shift(DOWN*0.1)

        self.add(circ1,circ2,rect)

class Patron(VGroup):
    CONFIG={
        "spaces":0.2,
        "color":GREEN,
        "add_base":False,
        "base_stroke":5,
        "stroke":1
    }
    def __init__(self,width,height,slope=1,**kwargs):
        VGroup.__init__(self, **kwargs)
        #Constants
        W=width
        H=height
        def func(x,m=1,tx=0,ty=0):
            return m*(x-tx)+ty
        def return_x(tx,ty,m,y,space):
            return ((y-ty-space)/m)+tx
        start_point=Coord(W/2,-H/2)
        first_domain=Coord(W/2,H/2)

        # Start
        rate=Rate(self.spaces)
        def func1(x):
            return func(x,slope,start_point.get_x(),start_point.get_y())
        while start_point.get_y()+rate.get_value()<=first_domain.get_y():
            xmin=return_x(
                start_point.get_x(),
                start_point.get_y(),
                slope,
                start_point.get_y(),
                rate.get_value()
                )
            xmax=start_point.get_x()
            line=FunctionGraph(
                    lambda x: func1(x)+rate.get_value(),
                    x_min=xmin,
                    x_max=xmax
                )
            self.add(line)
            rate.increment_value()

class PatternFromProportion(VGroup):
    CONFIG={
        "color":RED,
        "start_proportion_at":0,
        "step_pattern":0.01,
        "add_rectangle":False
    }
    def __init__(self,width,height=None,**kwargs):
        super().__init__(**kwargs)
        if height==None:
            height=width
        rectangle=Rectangle(width=width,height=height)

        middle_proportion=self.start_proportion_at%1
        start_proportion=(self.start_proportion_at-0.5)%1
        end_proportion=(self.start_proportion_at+0.5)%1

        update_proportion=middle_proportion
        pre_coords=[]
        while update_proportion<end_proportion:
            dot=Dot().move_to(rectangle.point_from_proportion(update_proportion))
            pre_coords.append(dot.get_center())
            self.add(dot)
            update_proportion+=self.step_pattern

        update_proportion=middle_proportion
        post_coords=[]
        while update_proportion>start_proportion:
            dot=Dot().move_to(rectangle.point_from_proportion(update_proportion))
            post_coords.append(dot.get_center())
            self.add(dot)
            update_proportion-=self.step_pattern

        for x,y in zip(pre_coords,post_coords):
            self.add(Line(x,y))

class RectanglePattern(VGroup):
    CONFIG={
        "space":0.2,
        "color":RED,
        "add_rectangle":False,
        "rectangle_color":WHITE,
        "rectangle_width":4
    }
    def __init__(self,width,height=None,stroke_width=2,**kwargs):
        super().__init__(**kwargs)
        if height==None:
            height=width
        W=width
        H=height
        b=self.space
        n=1
        if H>=W:
            while -H/2+n*b<H/2+W:
                if -H/2+n*b<-H/2+W:
                    x_i=W/2-n*b
                    x_f=W/2
                if -H/2+W<=(-H)/2+n*b and (-H)/2+n*b<=H/2:
                    x_i=-W/2
                    x_f=W/2
                if H/2<=(-H)/2+n*b and (-H)/2+n*b<H/2+W:
                    x_i=-W/2
                    x_f=H+W/2-n*b
                pat=FunctionGraph(lambda x : x-W/2-H/2+n*b, 
                                    color = self.color,
                                    stroke_width = stroke_width,
                                    x_min = x_i,
                                    x_max = x_f
                                    )
                self.add(pat)
                n+=1
        else:
            while n*b-H/2<W+H/2:
                if n*b-H/2<H/2:
                    x_i=W/2-n*b
                    x_f=W/2
                if H/2<=n*b-H/2 and n*b-H/2<W-H/2:
                    x_i=W/2-n*b
                    x_f=H+W/2-n*b
                if W-H/2<=n*b-H/2 and n*b-H/2<W+H/2:
                    x_i=-W/2
                    x_f=H+W/2-n*b
                pat=FunctionGraph(lambda x : x-W/2+n*b-H/2, 
                                    color = self.color,
                                    stroke_width = stroke_width,
                                    x_min = x_i,
                                    x_max = x_f
                                    )
                self.add(pat)
                n+=1
        if self.add_rectangle:
            self.add(
                Rectangle(
                    width=width,
                    height=height,
                    color=self.rectangle_color,
                    stroke_width=self.rectangle_width
                )
            )


class MeasureDistance(VGroup):
    CONFIG = {
        "color":RED_B,
        "buff":0.3,
        "lateral":0.3,
        "invert":False,
        "dashed_segment_length":0.09,
        "dashed":True,
        "ang_arrows":30*DEGREES,
        "size_arrows":0.2,
        "stroke":2.4,
    }
    def __init__(self,mob,**kwargs):
        VGroup.__init__(self,**kwargs)
        if self.dashed==True:
            medicion=DashedLine(ORIGIN,mob.get_length()*RIGHT,dashed_segment_length=self.dashed_segment_length).set_color(self.color)
        else:
            medicion=Line(ORIGIN,mob.get_length()*RIGHT)

        medicion.set_stroke(None,self.stroke)

        pre_medicion=Line(ORIGIN,self.lateral*RIGHT).rotate(PI/2).set_stroke(None,self.stroke)
        pos_medicion=pre_medicion.copy()

        pre_medicion.move_to(medicion.get_start())
        pos_medicion.move_to(medicion.get_end())

        angulo=mob.get_angle()
        matriz_rotacion=rotation_matrix(PI/2,OUT)
        vector_unitario=mob.get_unit_vector()
        direccion=np.matmul(matriz_rotacion,vector_unitario)
        self.direccion=direccion

        self.add(medicion,pre_medicion,pos_medicion)
        self.rotate(angulo)
        self.move_to(mob)

        if self.invert==True:
            self.shift(-direccion*self.buff)
        else:
            self.shift(direccion*self.buff)
        self.set_color(self.color)
        self.tip_point_index = -np.argmin(self.get_all_points()[-1, :])
        

    def add_tips(self):
        linea_referencia=Line(self[0][0].get_start(),self[0][-1].get_end())
        vector_unitario=linea_referencia.get_unit_vector()

        punto_final1=self[0][-1].get_end()
        punto_inicial1=punto_final1-vector_unitario*self.size_arrows

        punto_inicial2=self[0][0].get_start()
        punto_final2=punto_inicial2+vector_unitario*self.size_arrows

        lin1_1=Line(punto_inicial1,punto_final1).set_color(self[0].get_color()).set_stroke(None,self.stroke)
        lin1_2=lin1_1.copy()
        lin2_1=Line(punto_inicial2,punto_final2).set_color(self[0].get_color()).set_stroke(None,self.stroke)
        lin2_2=lin2_1.copy()

        lin1_1.rotate(self.ang_arrows,about_point=punto_final1,about_edge=punto_final1)
        lin1_2.rotate(-self.ang_arrows,about_point=punto_final1,about_edge=punto_final1)

        lin2_1.rotate(self.ang_arrows,about_point=punto_inicial2,about_edge=punto_inicial2)
        lin2_2.rotate(-self.ang_arrows,about_point=punto_inicial2,about_edge=punto_inicial2)


        return self.add(lin1_1,lin1_2,lin2_1,lin2_2)

    def add_tex(self,text,scale=1,buff=-1,**moreargs):
        linea_referencia=Line(self[0][0].get_start(),self[0][-1].get_end())
        texto=TexMobject(text,**moreargs)
        ancho=texto.get_height()/2
        texto.rotate(linea_referencia.get_angle()).scale(scale).move_to(self)
        texto.shift(self.direccion*(buff+1)*ancho)
        return self.add(texto)

    def add_text(self,text,scale=1,buff=0.1,**moreargs):
        linea_referencia=Line(self[0][0].get_start(),self[0][-1].get_end())
        texto=TextMobject(text,**moreargs)
        ancho=texto.get_height()/2
        texto.rotate(linea_referencia.get_angle()).scale(scale).move_to(self)
        texto.shift(self.direccion*(buff+1)*ancho)
        return self.add(texto)

    def add_size(self,text,scale=1,buff=0.1,**moreargs):
        linea_referencia=Line(self[0][0].get_start(),self[0][-1].get_end())
        texto=TextMobject(text,**moreargs)
        ancho=texto.get_height()/2
        texto.rotate(linea_referencia.get_angle())
        texto.shift(self.direccion*(buff+1)*ancho)
        return self.add(texto)

    def add_letter(self,text,scale=1,buff=0.1,**moreargs):
        linea_referencia=Line(self[0][0].get_start(),self[0][-1].get_end())
        texto=TexMobject(text,**moreargs).scale(scale).move_to(self)
        ancho=texto.get_height()/2
        texto.shift(self.direccion*(buff+1)*ancho)
        return self.add(texto)

    def get_text(self, text,scale=1,buff=0.1,invert_dir=False,invert_texto=False,remove_rot=False,**moreargs):
        linea_referencia=Line(self[0][0].get_start(),self[0][-1].get_end())
        texto=TextMobject(text,**moreargs)
        ancho=texto.get_height()/2
        if invert_texto:
            inv=PI
        else:
            inv=0
        if remove_rot:
            texto.scale(scale).move_to(self)
        else:
            texto.rotate(linea_referencia.get_angle()).scale(scale).move_to(self)
            texto.rotate(inv)
        if invert_dir:
            inv=-1
        else:
            inv=1
        texto.shift(self.direccion*(buff+1)*ancho*inv)
        return texto

    def get_tex(self, tex,scale=1,buff=1,invert_dir=False,invert_texto=False,remove_rot=True,**moreargs):
        linea_referencia=Line(self[0][0].get_start(),self[0][-1].get_end())
        texto=TexMobject(tex,**moreargs)
        ancho=texto.get_height()/2
        if invert_texto:
            inv=PI
        else:
            inv=0
        if remove_rot:
            texto.scale(scale).move_to(self)
        else:
            texto.rotate(linea_referencia.get_angle()).scale(scale).move_to(self)
            texto.rotate(inv)
        if invert_dir:
            inv=-1
        else:
            inv=1
        texto.shift(self.direccion*(buff+1)*ancho)
        return texto


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
        "labels_scale":0.3,
        "labels_buff":0,
        "number_decimals":2
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
                    leyenda=FontText("%s"%coord).scale(self.labels_scale)
                    leyenda.next_to(punto,direcciones_buff,buff=self.labels_buff)
                    puntos.add(punto)
                    leyendas.add(leyenda)

        self.add(grilla,ejes,leyendas)
        if self.show_points==True:
            self.add(puntos)

class Flecha(VMobject):
    CONFIG = {
        "color":ORANGE,
        "stroke":5,
        "proporcion":0.1,
        "height":0.35,
        "v_i":"obj",
        "v_f":"obj",
        "buff":0
    }
    def __init__(self,not1,not2,**kwargs):
        VGroup.__init__(self,**kwargs)
        if self.v_i=="obj":
            coord1=not1.get_center()
        else:
            coord1=not1
        if self.v_f=="obj":
            coord2=not2.get_center()
        else:
            coord2=not2
        linea_principal=Line(coord1,coord2,**kwargs)
        tip = Polygon(coord(0,0),coord(-0.13,0.3),coord(0,0.2),coord(0.13,0.3))
        tip.set_height(0.35)
        tip.set_stroke(width=0)
        tip.set_fill(opacity=1)
        tip.move_to(linea_principal.get_end())
        tip.rotate(linea_principal.get_angle()+PI/2)
        vector_unitario_linea_principal=linea_principal.get_unit_vector()
        punta_flecha=tip.points[0]

        delta_e=linea_principal.get_end()-punta_flecha

        tip.shift(delta_e)

        flecha=Line(LEFT,RIGHT)


        flecha.put_start_and_end_on(linea_principal.get_start(),linea_principal.get_end()-vector_unitario_linea_principal*self.proporcion)

        flecha.set_stroke(self.color,self.stroke)
        tip.set_color(self.color)

        self.add(flecha,tip)

    def get_start(self):
        return self[0].get_start()

    def get_end(self):
        return self[1].points[0]

class VFlecha(Flecha):
    CONFIG = {
        "v_i":"vect",
        "v_f":"vect",        
    }


class DFlecha(VMobject):
    CONFIG = {
        "color":ORANGE,
        "stroke":5,
        "proporcion":0.1,
        "height":0.35,
        "v_i":"obj",
        "v_f":"obj",        
    }
    def __init__(self,not1,not2,**kwargs):
        VGroup.__init__(self,**kwargs)
        if self.v_i=="obj":
            coord1=not1.get_center()
        else:
            coord1=not1
        if self.v_f=="obj":
            coord2=not2.get_center()
        else:
            coord2=not2
        linea_principal=Line(coord1,coord2,**kwargs)
        tip = Polygon(coord(0,0),coord(-0.13,0.3),coord(0,0.2),coord(0.13,0.3))
        tip.set_height(0.35)
        tip.set_stroke(width=0)
        tip.set_fill(opacity=1)
        dtip=tip.copy()

        tip.move_to(linea_principal.get_end())
        tip.rotate(linea_principal.get_angle()+PI/2)

        dtip.move_to(linea_principal.get_start())
        dtip.rotate(linea_principal.get_angle()-PI/2)

        vector_unitario_linea_principal=linea_principal.get_unit_vector()
        punta_flecha=tip.points[0]
        delta_e=linea_principal.get_end()-punta_flecha

        tip.shift(delta_e)

        dpunta_flecha=dtip.points[0]
        ddelta_e=linea_principal.get_start()-dpunta_flecha

        dtip.shift(ddelta_e)

        flecha=Line(LEFT,RIGHT)


        flecha.put_start_and_end_on(linea_principal.get_start()+vector_unitario_linea_principal*self.proporcion,linea_principal.get_end()-vector_unitario_linea_principal*self.proporcion)

        flecha.set_stroke(self.color,self.stroke)
        tip.set_color(self.color)
        dtip.set_color(self.color)

        self.add(flecha,tip,dtip)

    def get_start(self):
        return self[2].points[0]

    def get_end(self):
        return self[1].points[0]

class DVFlecha(DFlecha):
    CONFIG = {
        "v_i":"vect",
        "v_f":"vect",        
    }

class ParteDomo(VMobject):
    CONFIG = {
        "inner_radius": 3,
        "outer_radius": 3,
        "desfase":0,
        "angle": 10*DEGREES,
        "start_angle": 0,
        "fill_opacity": 1,
        "stroke_width": 0,
        "color": WHITE,
        "mark_paths_closed": False,
    }

    def generate_points(self):
        arc1 = Arc(
            angle=self.angle,
            start_angle=self.start_angle+self.desfase,
            radius=self.inner_radius,
        )
        arc2 = Arc(
            angle=self.angle,
            start_angle=PI-self.angle-self.desfase,
            radius=self.outer_radius,
        )
        a1_to_a2_points = np.array([
            interpolate(arc1.points[-1], arc2.points[0], alpha)
            for alpha in np.linspace(0, 1, 4)
        ])
        a2_to_a1_points = np.array([
            interpolate(arc2.points[-1], arc1.points[0], alpha)
            for alpha in np.linspace(0, 1, 4)
        ])
        self.points = np.array(arc1.points)
        self.add_control_points(a1_to_a2_points[1:])
        self.add_control_points(arc2.points[1:])
        self.add_control_points(a2_to_a1_points[1:])

class underline(Line):
    def __init__(self,texto,buff=0.07,**kwargs):
        Line.__init__(self,texto.get_corner(DL),texto.get_corner(DR),**kwargs)
        self.shift(DOWN*buff)

class FreehandDraw(VMobject):
    CONFIG = {
        "sign":1,
        "close":False,
        "dx_random":7,
        "length":0.06
    }
    def __init__(self,path,partitions,**kwargs):
        VMobject.__init__(self,**kwargs)
        coords = []
        for p in range(int(partitions)+1):
            coord_i = path.point_from_proportion((p*0.989/partitions)%1)
            coord_f = path.point_from_proportion((p*0.989/partitions+0.001)%1)
            reference_line = Line(coord_i, coord_f).rotate(self.sign*PI/2, about_point=coord_i)
            normal_unit_vector = reference_line.get_unit_vector()
            static_vector = normal_unit_vector*self.length
            random_dx = random.randint(0,self.dx_random)
            random_normal_vector = random_dx * normal_unit_vector / 100
            point_coord = coord_i + random_normal_vector + static_vector
            coords.append(point_coord)
        if self.close:
            coords.append(coords[0])
        self.set_points_smoothly(coords)

class FreehandRectangle(VMobject):
    CONFIG = {
        "margin":0.7,
        "partitions":120,
    }
    def __init__(self,texmob,**kwargs):
        VMobject.__init__(self,**kwargs)
        rect = Rectangle(
            width  = texmob.get_width() + self.margin,
            height = texmob.get_height() + self.margin
            )
        rect.move_to(texmob)
        w = rect.get_width()  
        h = rect.get_height()
        alpha = w / h
        hp = np.ceil(self.partitions / (2 * (alpha + 1)))
        wp = np.ceil(alpha * hp)
        sides = VGroup(*[
            Line(rect.get_corner(c1),rect.get_corner(c2))
            for c1,c2 in zip([UL,UR,DR,DL],[UR,DR,DL,UL])
            ])
        total_points = []
        for side,p in zip(sides,[wp,hp,wp,hp]):
            path = FreehandDraw(side,p).points
            for point in path:
                total_points.append(point)
        total_points.append(total_points[0])
        self.set_points_smoothly(total_points)

class ZigZag(VMobject):
    CONFIG = {
        "margin":0.4,
        "sign":1
    }
    def __init__(self,path,partitions=10,**kwargs):
        VMobject.__init__(self,**kwargs)
        rect = Rectangle(
            width  = path.get_width() + self.margin,
            height = path.get_height() + self.margin
            )
        rect.move_to(path)
        w = rect.get_width()  
        h = rect.get_height()
        alpha = w / h
        hp = int(np.ceil(partitions / (2 * (alpha + 1))))
        wp = int(np.ceil(alpha * hp))
        sides = VGroup(*[
            Line(rect.get_corner(c1),rect.get_corner(c2))
            for c1,c2 in zip([UL,UR,DR,DL],[UR,DR,DL,UL])
            ])
        total_points = []
        for side,points in zip(sides,[wp,hp,wp,hp]):
            for p in range(points):
                total_points.append(side.point_from_proportion(p/points))
        total_points.append(total_points[0])
        middle = int(np.floor(len(total_points)/2))
        draw_points = []
        for p in range(2,middle):
            draw_points.append(total_points[-p*self.sign])
            draw_points.append(total_points[p*self.sign])
        self.set_points_smoothly(draw_points)

class RotaCompass(Rotating):
    CONFIG = {
        "rate_func": smooth,
        "run_time": 2
    }

class Compass(VGroup):
    CONFIG = {
        "height": 2.5,
        "stroke_material": 0.7,
        "needle_height": 0.1,
        "hinge_radius_1": 0.06,
        "hinge_width": 0.3,
        "hinge_height": 0.7,
        "hinge_support_width": 0.1,
        "hinge_support_height": 0.3,
        "stroke_factor_up": 0.6,
        "stroke_factor_down": 1.4
    }
    def __init__(self,start=ORIGIN,gap=1.5,**kwargs):
        digest_config(self,kwargs)
        super().__init__()
        self.start = start
        self.gap = gap
        needle_a,needle_b = self.set_needles()
        body = self.set_body()
        hinge = self.set_hinge()
        self.draws=VGroup()
        self.needle_a,self.needle_b = needle_a,needle_b
        self.angle = self.get_angle()
        self.add(body,hinge,needle_a,needle_b)
        self.body=body
        self.hinge=hinge
        # Points of compass
    def set_points_compass(self):
        start = self.start
        gap = self.gap
        needle_start_a = start
        needle_end_a = start+UP*self.needle_height
        p3 = start+RIGHT*gap/2+UP*self.height
        p2 = start+RIGHT*gap+UP*self.needle_height
        p1 = start+p3+UP*self.stroke_material
        needle_start_b = p2
        needle_end_b = needle_start_b+DOWN*self.needle_height
        hinge_coord = (p1-p3)/3+p3
        return needle_start_a,needle_end_a,p3,p2,p1,needle_start_b,needle_end_b,hinge_coord 
        # needles
    def set_needles(self):
        needle_start_a,needle_end_a,p3,p2,p1,needle_start_b,needle_end_b,hinge_coord=self.set_points_compass()
        needle_a = Line(needle_start_a,needle_end_a,buff=0,stroke_width=2)
        needle_b = Line(needle_start_b,needle_end_b,buff=0,stroke_width=2)
        needle_a.set_color(color=[WHITE,WHITE])
        needle_b.set_color(color=[WHITE,WHITE])
        return needle_a,needle_b
        # body
    def set_body(self):
        needle_start_a,needle_end_a,p3,p2,p1,needle_start_b,needle_end_b,hinge_coord=self.set_points_compass()
        body = Polygon(needle_end_a,p1,p2,p3).set_fill(BLUE,1)
        body.set_color(color=[interpolate_color(GRAY,BLACK,0.5),GRAY,interpolate_color(GRAY,BLACK,0.5)])
        body.set_sheen_direction(UP)
        return body
        # hinge
    def set_hinge(self):
        needle_start_a,needle_end_a,p3,p2,p1,needle_start_b,needle_end_b,hinge_coord=self.set_points_compass()
        hinge_rectangle = Rectangle(width=self.hinge_width,height=self.hinge_height,fill_opacity=1)
        h_p1 = hinge_rectangle.get_corner(DL)
        h_p2 = hinge_rectangle.get_corner(UL)
        h_p3 = h_p2+RIGHT*(self.hinge_width-self.hinge_support_width)/2
        h_p4 = h_p3 + UP*self.hinge_support_height
        h_p5 = h_p4 + RIGHT*self.hinge_support_width
        h_p6 = h_p5 + DOWN*self.hinge_support_height
        h_p7 = hinge_rectangle.get_corner(UR)
        h_p8 = hinge_rectangle.get_corner(DR)
        hinge_support = Polygon(h_p1,h_p2,h_p3,h_p4,h_p5,h_p6,h_p7,h_p8,fill_opacity=1)
        hinge_support.set_color(color=[ORANGE,RED])
        hinge_support.set_sheen_direction(UP)
        hinge = VGroup(
            hinge_support,
            Dot(radius=self.hinge_radius_1*1.2,color=interpolate_color(GRAY,BLACK,0.5)),
            Dot(radius=self.hinge_radius_1,color=GRAY),
            )
        hinge.move_to(hinge_coord)
        return hinge

    def get_needle_a_coord(self):
        return self.needle_a.get_start()

    def get_needle_b_coord(self):
        return self.needle_b.get_end()

    def get_angle(self):
        line_reference = Line(
                self.needle_a.get_start(),
                self.needle_b.get_end()
            )
        return line_reference.get_angle()

    def Rotate(self,angle,needle="A",arc_color=RED,arc_start=None,draw=True,**anim_kwargs):
        if arc_start== None:
            arc_start = self.get_angle()
        if needle == "A":
            point = self.get_needle_a_coord()
            start_angle = 0 + arc_start
        if needle == "B":
            point = self.get_needle_b_coord()
            start_angle = PI + arc_start
            angle=-angle
        rotate_compass = RotaCompass(self,radians=angle,about_point=point,**anim_kwargs)
        arc = Arc(angle=angle,radius=self.gap,arc_center=point,start_angle=start_angle,color=arc_color)
        if draw:
            draw = ShowCreation(arc,**anim_kwargs)
            self.draws.add(arc)
            return [rotate_compass,draw]
        else:
            return [rotate_compass]

    def set_angle(self,angle,needle="A"):
        start_angle = self.get_angle()
        if needle=="A":
            point = self.get_needle_a_coord()
            self.rotate(-start_angle,about_point=point)
            self.rotate(angle,about_point=point)
        if needle=="B":
            point = self.get_needle_b_coord()
            self.rotate(start_angle,about_point=point)
            self.rotate(-angle,about_point=point)

    def move_compass_to(self,angle,needle="A"):
        start_angle = self.get_angle()
        self.starting_mobject=self.deepcopy()
        if needle=="A":
            point = self.get_needle_a_coord()
            def update_compass(mob,alpha):
                mob.become(mob.starting_mobject)
                mob.rotate(alpha*(angle-start_angle),about_point=point)
            return update_compass
        if needle=="B":
            point = self.get_needle_b_coord()
            def update_compass(mob,alpha):
                mob.become(mob.starting_mobject)
                mob.rotate(alpha*(angle-start_angle),about_point=point)
            return update_compass