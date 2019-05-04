from big_ol_pile_of_manim_imports import *

class CheckSVG(Scene):
    CONFIG={
    "camera_config":{"background_color": WHITE},
    "svg_type":"svg",
    "file":"",
    "svg_scale":0.9,
    "angle":0,
    "flip_svg":False,
    "fill_opacity": 1,
    "remove": [],
    "stroke_color": BLACK,
    "fill_color": BLACK,
    "stroke_width": 3,
    "numbers_scale":0.5,
    "show_numbers": False,
    "animation": False,
    "direction_numbers": UP,
    "color_numbers": RED,
    "space_between_numbers":0,
    "show_elements":[],
    "color_element":BLUE,
    "set_size":"width",
    "remove_stroke":[],
    "show_stroke":[],
    "stroke_":1
    }
    def construct(self):
        if self.set_size=="width":
            width_size=FRAME_WIDTH
            height_size=None
        else:
            width_size=None
            height_size=FRAME_HEIGHT

        if self.svg_type=="svg":
            self.imagen=SVGMobject(
                "%s"%self.file,
                #fill_opacity = 1,
                stroke_width = self.stroke_width,
                stroke_color = self.stroke_color,
                width=width_size,
                height=height_size
            ).rotate(self.angle).set_fill(self.fill_color,self.fill_opacity).scale(self.svg_scale)
        else:
            self.imagen=self.import_text().set_fill(self.fill_color,self.fill_opacity).rotate(self.angle).set_stroke(self.stroke_color,0)
            if self.set_size=="width":
                self.imagen.set_width(FRAME_WIDTH)
            else:
                self.imagen.set_height(FRAME_HEIGHT)
            self.imagen.scale(self.svg_scale)
        self.personalize_image()
        if self.flip_svg==True:
            self.imagen.flip()
        if self.show_numbers==True:
            self.print_formula(self.imagen,
                self.numbers_scale,
                self.direction_numbers,
                self.remove,
                self.space_between_numbers,
                self.color_numbers)

        self.return_elements(self.imagen,self.show_elements)
        for st in self.remove_stroke:
            self.imagen[st].set_stroke(None,0)
        for st in self.show_stroke:
            self.imagen[st].set_stroke(None,self.stroke_)
        if self.animation==True:
            self.play(DrawBorderThenFill(self.imagen))
        else:
            self.add(self.imagen)
        self.wait()
    def import_text(self):
        return TexMobject("")

    def personalize_image(self):
        pass

    def print_formula(self,text,inverse_scale,direction,exception,buff,color):
        text.set_color(RED)
        self.add(text)
        c = 0
        for j in range(len(text)):
            permission_print=True
            for w in exception:
                if j==w:
                    permission_print=False
            if permission_print:
                self.add(text[j].set_color(self.stroke_color))
        c = c + 1

        c=0
        for j in range(len(text)):
            permission_print=True
            element = TexMobject("%d" %c,color=color)
            element.scale(inverse_scale)
            element.next_to(text[j],direction,buff=buff)
            for w in exception:
                if j==w:
                    permission_print=False
            if permission_print:
                self.add(element)
            c = c + 1 

    def return_elements(self,formula,adds):
        for i in adds:
            self.add_foreground_mobjects(formula[i].set_color(self.color_element),
                TexMobject("%d"%i,color=self.color_element,background_stroke_width=0).scale(self.numbers_scale).next_to(formula[i],self.direction_numbers,buff=self.space_between_numbers))

class CheckFormula(Scene):
    CONFIG={
    "camera_config":{"background_color": BLACK},
    "svg_type":"text",
    "file":"",
    "svg_scale":0.9,
    "angle":0,
    "flip_svg":False,
    "fill_opacity": 1,
    "remove": [],
    "stroke_color": WHITE,
    "fill_color": WHITE,
    "stroke_width": 0,
    "numbers_scale":0.5,
    "show_numbers": True,
    "animation": False,
    "direction_numbers": UP,
    "color_numbers": RED,
    "space_between_numbers":0,
    "show_elements":[],
    "color_element":BLUE,
    "set_size":"width",
    "remove_stroke":[],
    "show_stroke":[],
    "stroke_":1
    }
    def construct(self):
        self.imagen=self.import_text()
        if self.set_size=="width":
            self.imagen.set_width(FRAME_WIDTH)
        else:
            self.imagen.set_height(FRAME_HEIGHT)
            self.imagen.scale(self.svg_scale)
        if self.flip_svg==True:
            self.imagen.flip()
        if self.show_numbers==True:
            self.print_formula(self.imagen.copy(),
                self.numbers_scale,
                self.direction_numbers,
                self.remove,
                self.space_between_numbers,
                self.color_numbers)

        self.return_elements(self.imagen.copy(),self.show_elements)
        for st in self.remove_stroke:
            self.imagen[st].set_stroke(None,self.stroke_width)
        for st in self.show_stroke:
            self.imagen[st].set_stroke(None,self.stroke_)
        if self.animation==True:
            self.play(DrawBorderThenFill(self.imagen))
        else:
            self.add(self.imagen)
        self.personalize_image()
        self.wait()
    def import_text(self):
        return TexMobject("")

    def personalize_image(self):
        pass

    def print_formula(self,text,inverse_scale,direction,exception,buff,color):
        text.set_color(RED)
        self.add(text)
        c = 0
        for j in range(len(text)):
            permission_print=True
            for w in exception:
                if j==w:
                    permission_print=False
            if permission_print:
                self.add(text[j].set_color(self.stroke_color))
        c = c + 1

        c=0
        for j in range(len(text)):
            permission_print=True
            element = TexMobject("%d" %c,color=color)
            element.scale(inverse_scale)
            element.next_to(text[j],direction,buff=buff)
            for w in exception:
                if j==w:
                    permission_print=False
            if permission_print:
                self.add_foreground_mobjects(element)
            c = c + 1 

    def return_elements(self,formula,adds):
        for i in adds:
            self.add_foreground_mobjects(formula[i].set_color(self.color_element),
                TexMobject("%d"%i,color=self.color_element,background_stroke_width=0).scale(self.numbers_scale).next_to(formula[i],self.direction_numbers,buff=self.space_between_numbers))

class CheckFormulaByTXT(Scene):
    CONFIG={
    "camera_config":{"background_color": BLACK},
    "svg_type":"text",
    "text": TexMobject(""),
    "file":"",
    "svg_scale":0.9,
    "angle":0,
    "flip_svg":False,
    "fill_opacity": 1,
    "remove": [],
    "stroke_color": WHITE,
    "fill_color": WHITE,
    "stroke_width": 3,
    "numbers_scale":0.5,
    "show_numbers": True,
    "animation": False,
    "direction_numbers": UP,
    "color_numbers": RED,
    "space_between_numbers":0,
    "show_elements":[],
    "color_element":BLUE,
    "set_size":"width",
    "remove_stroke":[],
    "show_stroke":[],
    "warning_color":RED,
    "stroke_":1
    }
    def construct(self):
        self.imagen=self.text
        if self.set_size=="width":
            self.imagen.set_width(FRAME_WIDTH)
        else:
            self.imagen.set_height(FRAME_HEIGHT)
        self.imagen.scale(self.svg_scale)
        if self.flip_svg==True:
            self.imagen.flip()
        if self.show_numbers==True:
            self.print_formula(self.imagen.copy(),
                self.numbers_scale,
                self.direction_numbers,
                self.remove,
                self.space_between_numbers,
                self.color_numbers)

        self.return_elements(self.imagen.copy(),self.show_elements)
        for st in self.remove_stroke:
            self.imagen[st].set_stroke(None,0)
        for st in self.show_stroke:
            self.imagen[st].set_stroke(None,self.stroke_)
        if self.animation==True:
            self.play(DrawBorderThenFill(self.imagen))
        else:
            c=0
            for j in range(len(self.imagen)):
                permission_print=True
                for w in self.remove:
                    if j==w:
                        permission_print=False
                if permission_print:
                    self.add(self.imagen[j])
            c = c + 1
        self.personalize_image()
        self.wait()

    def personalize_image(self):
        pass

    def print_formula(self,text,inverse_scale,direction,exception,buff,color):
        text.set_color(self.warning_color)
        self.add(text)
        c = 0
        for j in range(len(text)):
            permission_print=True
            for w in exception:
                if j==w:
                    permission_print=False
            if permission_print:
                self.add(text[j].set_color(self.stroke_color))
        c = c + 1

        c=0
        for j in range(len(text)):
            permission_print=True
            element = TexMobject("%d" %c,color=color)
            element.scale(inverse_scale)
            element.next_to(text[j],direction,buff=buff)
            for w in exception:
                if j==w:
                    permission_print=False
            if permission_print:
                self.add_foreground_mobjects(element)
            c = c + 1 

    def return_elements(self,formula,adds):
        for i in adds:
            self.add_foreground_mobjects(formula[i].set_color(self.color_element),
                TexMobject("%d"%i,color=self.color_element,background_stroke_width=0).scale(self.numbers_scale).next_to(formula[i],self.direction_numbers,buff=self.space_between_numbers))

class EscenaContenido2(Scene):
    CONFIG={"camera_config":{"background_color":BLACK},
    "tiempo":2,
    "desplazamiento":2.5,
    "distancia_entre_bloques":0.3,
    "distancia_entre_temas":0.25,
    "tiempo_espera":3
    }
    def tema(self,texto,**kwargs):
        return Texto("\\begin{flushleft} %s \\end{flushleft}"%texto,**kwargs)

    def setup(self):
        self.bloques=VGroup()  


    def construct(self):
        self.convertidor_bloques()
        self.aparicion_contenido(self.tiempo)
        self.wait(self.tiempo_espera)
        self.salida_contenido()

    def convertidor_bloques(self):
    	bloque_listo=VGroup()
    	for i in range(len(self.bloques)):
    		bloque_listo.add(self.temas(self.bloques[i],i+1))

    	self.bloques=bloque_listo


    def aparicion_contenido(self,tiempo):
        self.bloques.arrange_submobjects(
            DOWN, buff=self.distancia_entre_bloques,
            aligned_edge=LEFT
        )
        self.contenido=Texto("\\sc\\underline{Contenido}").scale(2).to_edge(UR)
        self.bloques_estatica=self.bloques.copy().shift(LEFT*self.desplazamiento)
        for i in range(len(self.bloques)):
            self.bloques[i].shift(LEFT*(FRAME_X_RADIUS+self.bloques[i].get_width()/2)*np.sin(PI/2+i*PI))
        for i in range(len(self.bloques)):
            self.play(
                *[Escribe(self.contenido,run_time=5)for w in range(1)for w in range(1) if i==0],
                ReplacementTransform(self.bloques[i],self.bloques_estatica[i]),run_time=tiempo
                )



    def temas(self,bloque,num):
        bloque.arrange_submobjects(
            DOWN, buff=self.distancia_entre_temas,
            aligned_edge=LEFT
        )
        bloque[1:].shift(RIGHT)
        indices=VGroup()
        indices.add(Texto("%d"%num))
        for i in range(len(bloque)-1):
            indices.add(Texto("%d.%s"%(num,i+1)))
        for i in range(len(bloque)):
            indices[i].next_to(bloque[i],LEFT,buff=0.5).move_to(np.array((
                                                                    indices[i].get_center()[0],
                                                                    bloque[i][0].get_center()[1],
                                                                    indices[i].get_center()[2]
                                                                    )))
        bloque_final=VGroup()
        for i in range(len(bloque)):
            bloque_final.add(indices[i])
            bloque_final.add(bloque[i])

        return bloque_final

    def salida_contenido(self):
    	self.play(
    		self.contenido.shift,UP*5,
    		self.bloques.shift,DOWN*10,
    		self.bloques_estatica.shift,DOWN*10)

class EscenaContenido(Scene):
    CONFIG={"camera_config":{"background_color":BLACK},
    "tiempo":2,
    "desplazamiento":2.5,
    "distancia_entre_bloques":0.3,
    "distancia_entre_temas":0.25,
    "tiempo_espera":2,
    "escala":1
    }
    def tema(self,texto,color=TT_TEXTO,**kwargs):
        return Texto("\\begin{flushleft}\\it %s \\end{flushleft}"%texto,color=color,**kwargs)

    def subtema(self,texto,color=TT_TEXTO,**kwargs):
        return Texto("\\begin{flushleft} %s \\end{flushleft}"%texto,color=color,**kwargs)

    def setup(self):
        self.contenido=[]  


    def construct(self):
        self.convertidor_bloques()
        self.aparicion_contenido(self.tiempo)
        self.wait(self.tiempo_espera)
        self.salida_contenido()

    def convertidor_bloques(self):
        bloque=VGroup()
        self.bloques=VGroup()
        pasos=len(self.contenido)-1
        c=0
        while True:
            tem=0
            bloque=VGroup()
            while self.contenido[c]!="--":
                if tem==0:
                    bloque.add(self.tema(self.contenido[c]))
                else:
                    bloque.add(self.subtema(self.contenido[c]))
                c=c+1
                tem=tem+1
            if c<pasos-1:
                c=c+1
            self.bloques.add(bloque)
            if c==pasos:
                break

        bloque_listo=VGroup()
        for i in range(len(self.bloques)):
            bloque_listo.add(self.temas(self.bloques[i],i+1))

        self.bloques=bloque_listo


    def aparicion_contenido(self,tiempo):
        self.bloques.arrange_submobjects(
            DOWN, buff=self.distancia_entre_bloques,
            aligned_edge=LEFT
        )
        self.bloques.scale(self.escala)
        self.titulo=Texto("\\sc\\underline{Contenido}",color=TT_TEXTO).scale(2).to_edge(UR)
        self.bloques_estatica=self.bloques.copy().shift(LEFT*self.desplazamiento)
        for i in range(len(self.bloques)):
            self.bloques[i].shift(LEFT*(FRAME_X_RADIUS+self.bloques[i].get_width()/2)*np.sin(PI/2+i*PI))
        for i in range(len(self.bloques)):
            self.play(
                *[Escribe(self.titulo,rate_func=linear)for w in range(1)for w in range(1) if i==0],
                #*[Escribe(self.titulo[-1])for w in range(1)for w in range(1) if i==1],
                ReplacementTransform(self.bloques[i],self.bloques_estatica[i]),run_time=tiempo
                )



    def temas(self,bloque,num):
        bloque.arrange_submobjects(
            DOWN, buff=self.distancia_entre_temas,
            aligned_edge=LEFT
        )
        bloque[1:].shift(RIGHT)
        indices=VGroup()
        indices.add(Texto("%d"%num,color=M_TEXTO_VERDE))
        for i in range(len(bloque)-1):
            indices.add(Texto("%d.%s"%(num,i+1),color=M_TEXTO_VERDE))
        for i in range(len(bloque)):
            indices[i].next_to(bloque[i],LEFT,buff=0.5).move_to(np.array((
                                                                    indices[i].get_center()[0],
                                                                    bloque[i][0].get_center()[1],
                                                                    indices[i].get_center()[2]
                                                                    )))
        bloque_final=VGroup()
        for i in range(len(bloque)):
            bloque_final.add(indices[i])
            bloque_final.add(bloque[i])

        return bloque_final

    def salida_contenido(self):
    	self.play(
    		self.titulo.shift,UP*5,
    		self.bloques.shift,DOWN*10,
    		self.bloques_estatica.shift,DOWN*10)
        
class EscenaTitulo(Scene):
	CONFIG={
	"title":"Hola mundo!",
	"te":0.4,
	"escala":2,
	"especificaciones":{},
	"tipo_animacion":"escribe_texto"
	}
	def construct(self):
		self.muestra_titulo()

	def muestra_titulo(self):
		tit=TikzMobject("""
		\\begin{tikzpicture}[pencildraw/.style={decorate,
		decoration={random steps,segment length=0.8pt,amplitude=0.3pt}}]
		    \\node[pencildraw,draw] {\\sc %s};
		\\end{tikzpicture} 
		  """%self.title,stroke_width=2,fill_opacity=.1,color=WHITE).scale(self.escala)
		tit[0].set_fill(BLACK,1)
		tit[1:].set_stroke(None,0).set_fill(WHITE,1)
		if self.tipo_animacion=="escribe_texto":
			titulo=escribe_texto(self,tit[1:],**self.especificaciones)
		elif self.tipo_animacion=="Escribe":
			titulo=tit[1:]
			self.play(Escribe(titulo),**self.especificaciones)
		elif self.tipo_animacion=="Aparece":
			titulo=tit[1:]
			seleccion_texto(self,titulo,opacidad=0,color=BLACK,direccion=RIGHT)
			self.add(titulo)
			self.play(Transform(titulo.pos_rect,titulo.rect),**self.especificaciones)
		elif self.tipo_animacion=="Teclea":
			titulo=tit[1:]
			TypeWriter(self,titulo,**self.especificaciones)
			self.wait()
		self.add_foreground_mobject(tit[0])
		self.add_foreground_mobject(tit[1:])
		self.play(Write(tit[0]))
		esq_left=tit[1:].get_left()
		esq_right=tit[1:].get_right()
		cuerda_left=Line(esq_left+UP*5,esq_left,color=WHITE)
		cuerda_right=Line(esq_right+UP*5,esq_right,color=WHITE)
		self.play(ShowCreation(cuerda_left),ShowCreation(cuerda_right))
		self.wait(self.te)
		self.add_foreground_mobjects(tit[0],tit[1:])
		self.play(
		VGroup(tit[0],cuerda_left,cuerda_right,titulo,tit[1:]).shift,UP*8
		)

