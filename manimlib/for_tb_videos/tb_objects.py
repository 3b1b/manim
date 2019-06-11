from manimlib.imports import *

<<<<<<< HEAD:manimlib/for_tb_videos/svg_basicos.py
class MatrixGroup(VGroup):
    def __init__(self,matrix_complete,show_desg=False,start=3):
        matrix_complete_full=""
        coords=[]
        for w in range(len(matrix_complete)):
            coords_r=[]
            for i in range(len(matrix_complete[w])):
                tex_i=""
                for j in matrix_complete[w][i]:
                    matrix_complete_full+=j
                    tex_i+=j
                    matrix_complete_full+=" "
                    tex_i+=" "
                l_tex=len(Formula(tex_i))
                coords_r.append(l_tex)
                print(l_tex)
                if i<len(matrix_complete[w])-1:
                    matrix_complete_full+=" & "
                else:
                    matrix_complete_full+=r" \\ "
            coords.append(coords_r)

        VGroup.__init__(self)
        matrix_frag=VGroup()

        matrix_desg=TexMobject(r"""
            \begin{bmatrix}
            %s
            \end{bmatrix}
        """%(matrix_complete_full))
        end=start
        
        for w in range(len(matrix_complete)):
            matrix_rows=VGroup()
            for i in range(len(matrix_complete[w])):
                element=VGroup(Formula(*matrix_complete[w][i]))
                element.set_height(matrix_desg[start:start+coords[w][i]].get_height())
                element.move_to(matrix_desg[start:start+coords[w][i]])
                start+=coords[w][i]
                matrix_rows.add(element)
            matrix_frag.add(matrix_rows)
        matrix_frag.add(matrix_desg[:end],matrix_desg[-end:])

        if show_desg==True:
            self.add(*matrix_desg)
        else:
            self.add(*matrix_frag)

class Instagram(VGroup):
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        back1=self.color_cell(
            SVGMobject("instagram")[2],
            colors = ["#FED372","#B52C94","#4D67D8"]
            )
        back2=self.color_cell(
            SVGMobject("instagram")[0],
            colors = ["#B52C94"]
            )
        back3=self.color_cell(
            SVGMobject("instagram")[1],
            colors = ["#B83D8D","#8A5DA2","#8A5DA2"]
            )
        back4=self.color_cell(
            SVGMobject("instagram")[3],
            colors = ["#D77A84","#B52C94","#BD368A"],
            vect=[0.2,1,0]
            )
        VGroup.__init__(self,**kwargs)
        self.add(back1,back2,back3,back4)

    def color_cell(self,cell,colors,vect=[0.45,1,0]):
        cell.set_color(color=colors,family=True)
        cell.set_stroke(color=colors)
        cell.set_sheen_direction(vect)
        return cell

class PatreonSVG(SVGMobject):
    CONFIG={
    "file_name":"patreon.svg"
    }
    def __init__(self, **kwargs):
=======
class Caja(VMobject):
    def __init__(self,ancho=3,alto=2,tapas=0.95,grosor_tapas=11,stroke_color="#D2B48C",fill_color="#cdab7e",**kwargs):
>>>>>>> 8dc98dab123f6fce8f47d8c4e58b0a4cd54c78d6:manimlib/for_tb_videos/tb_objects.py
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
    def __init__(self,width,height,separacion=0.2,color=GREEN,agregar_base=False,direccion="R",grosor=1,stroke_width=2,**kwargs):
        digest_config(self, kwargs)
        VGroup.__init__(self, **kwargs)
        W=width
        H=height
        b=separacion
        if H>=W:
            n=0
            while n*b<W:
                x_i=W/2-n*b
                x_f=W/2
                pat=FunctionGraph(lambda x : x-W/2+n*b-H/2, 
                                    color = color,
                                    stroke_width = stroke_width,
                                    x_min = x_i,
                                    x_max = x_f
                                    )
                self.add(pat)
                n=n+1
            n=0
            while n*b<=H-W:
                x_f=W/2
                x_i=-W/2
                pat=FunctionGraph(lambda x : x-x_i+n*b-H/2, 
                                    color = color,
                                    stroke_width = stroke_width,
                                    x_min = x_i,
                                    x_max = x_f
                                    )
                self.add(pat)
                n=n+1
            while n*b-H/2<H/2:
                x_f=H-n*b+x_i
                x_i=-W/2
                pat=FunctionGraph(lambda x : x-x_i+n*b-H/2, 
                                    color = color,
                                    stroke_width = stroke_width,
                                    x_min = x_i,
                                    x_max = x_f
                                    )
                self.add(pat)
                n=n+1
        else:
            n=0
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
                                    color = color,
                                    stroke_width = stroke_width,
                                    x_min = x_i,
                                    x_max = x_f
                                    )
                self.add(pat)
                n=n+1
        if agregar_base==True:
            if direccion=="L":
                orientacion=LEFT
            elif direccion=="R":
                orientacion=RIGHT
            elif direccion=="U":
                orientacion=UP
            elif direccion=="D":
                orientacion=DOWN
            if direccion=="L" or direccion=="R":
                grosor=Rectangle(height=H,width=grosor).set_fill(color,1).set_stroke(None,0)
                grosor.shift(orientacion*W/2-orientacion*grosor.get_width()/2)
            else:
                grosor=Rectangle(height=grosor,width=W).set_fill(color,1).set_stroke(None,0)
                grosor.shift(orientacion*H/2-orientacion*grosor.get_height()/2)
            self.add(grosor)

class Medicion(VGroup):
    CONFIG = {
        "color":RED_B,
        "buff":0.3,
        "laterales":0.3,
        "invertir":False,
        "dashed_segment_length":0.09,
        "dashed":False,
        "con_flechas":True,
        "ang_flechas":30*DEGREES,
        "tam_flechas":0.2,
        "stroke":2.4
    }
    def __init__(self,objeto,**kwargs):
        VGroup.__init__(self,**kwargs)
        if self.dashed==True:
            medicion=DashedLine(ORIGIN,objeto.get_length()*RIGHT,dashed_segment_length=self.dashed_segment_length).set_color(self.color)
        else:
            medicion=Line(ORIGIN,objeto.get_length()*RIGHT)

        medicion.set_stroke(None,self.stroke)

        pre_medicion=Line(ORIGIN,self.laterales*RIGHT).rotate(PI/2).set_stroke(None,self.stroke)
        pos_medicion=pre_medicion.copy()

        pre_medicion.move_to(medicion.get_start())
        pos_medicion.move_to(medicion.get_end())

        angulo=objeto.get_angle()
        matriz_rotacion=rotation_matrix(PI/2,OUT)
        vector_unitario=objeto.get_unit_vector()
        direccion=np.matmul(matriz_rotacion,vector_unitario)
        self.direccion=direccion

        self.add(medicion,pre_medicion,pos_medicion)
        self.rotate(angulo)
        self.move_to(objeto)

        if self.invertir==True:
            self.shift(-direccion*self.buff)
        else:
            self.shift(direccion*self.buff)
        self.set_color(self.color)
        self.tip_point_index = -np.argmin(self.get_all_points()[-1, :])
        

    def add_tips(self):
        linea_referencia=Line(self[0][0].get_start(),self[0][-1].get_end())
        vector_unitario=linea_referencia.get_unit_vector()

        punto_final1=self[0][-1].get_end()
        punto_inicial1=punto_final1-vector_unitario*self.tam_flechas

        punto_inicial2=self[0][0].get_start()
        punto_final2=punto_inicial2+vector_unitario*self.tam_flechas

        lin1_1=Line(punto_inicial1,punto_final1).set_color(self[0].get_color()).set_stroke(None,self.stroke)
        lin1_2=lin1_1.copy()
        lin2_1=Line(punto_inicial2,punto_final2).set_color(self[0].get_color()).set_stroke(None,self.stroke)
        lin2_2=lin2_1.copy()

        lin1_1.rotate(self.ang_flechas,about_point=punto_final1,about_edge=punto_final1)
        lin1_2.rotate(-self.ang_flechas,about_point=punto_final1,about_edge=punto_final1)

        lin2_1.rotate(self.ang_flechas,about_point=punto_inicial2,about_edge=punto_inicial2)
        lin2_2.rotate(-self.ang_flechas,about_point=punto_inicial2,about_edge=punto_inicial2)


        return self.add(lin1_1,lin1_2,lin2_1,lin2_2)

    def add_tex(self,texto,escala=1,buff=0.1,**moreargs):
        linea_referencia=Line(self[0][0].get_start(),self[0][-1].get_end())
        texto=TexMobject(texto,**moreargs)
        ancho=texto.get_height()/2
        texto.rotate(linea_referencia.get_angle()).scale(escala).move_to(self)
        texto.shift(self.direccion*(buff+1)*ancho)
        return self.add(texto)

    def add_text(self,text,escala=1,buff=0.1,**moreargs):
        linea_referencia=Line(self[0][0].get_start(),self[0][-1].get_end())
        texto=TextMobject(text,**moreargs)
        ancho=texto.get_height()/2
        texto.rotate(linea_referencia.get_angle()).scale(escala).move_to(self)
        texto.shift(self.direccion*(buff+1)*ancho)
        return self.add(texto)

    def add_size(self,texto,escala=1,buff=0.1,**moreargs):
        linea_referencia=Line(self[0][0].get_start(),self[0][-1].get_end())
        texto=TextMobject(texto,**moreargs)
        ancho=texto.get_height()/2
        texto.rotate(linea_referencia.get_angle())
        texto.shift(self.direccion*(buff+1)*ancho)
        return self.add(texto)

    def add_letter(self,texto,escala=1,buff=0.1,**moreargs):
        linea_referencia=Line(self[0][0].get_start(),self[0][-1].get_end())
        texto=TexMobject(texto,**moreargs).scale(escala).move_to(self)
        ancho=texto.get_height()/2
        texto.shift(self.direccion*(buff+1)*ancho)
        return self.add(texto)

    def get_text(self, text,escala=1,buff=0.1,invert_dir=False,invert_texto=False,elim_rot=False,**moreargs):
        linea_referencia=Line(self[0][0].get_start(),self[0][-1].get_end())
        texto=TextMobject(text,**moreargs)
        ancho=texto.get_height()/2
        if invert_texto:
            inv=PI
        else:
            inv=0
        if elim_rot:
            texto.scale(escala).move_to(self)
        else:
            texto.rotate(linea_referencia.get_angle()).scale(escala).move_to(self)
            texto.rotate(inv)
        if invert_dir:
            inv=-1
        else:
            inv=1
        texto.shift(self.direccion*(buff+1)*ancho*inv)
        return texto

    def get_tex(self, tex,escala=1,buff=0.1,invert_dir=False,invert_texto=False,elim_rot=False,**moreargs):
        linea_referencia=Line(self[0][0].get_start(),self[0][-1].get_end())
        texto=TexMobject(texto,**moreargs)
        ancho=texto.get_height()/2
        if invert_texto:
            inv=PI
        else:
            inv=0
        if elim_rot:
            texto.scale(escala).move_to(self)
        else:
            texto.rotate(linea_referencia.get_angle()).scale(escala).move_to(self)
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
        "labels_scale":0.5,
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
                    leyenda=TextMobject("%s"%coord).scale(self.labels_scale)
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
