from big_ol_pile_of_manim_imports import *

class PruebaSVG(Scene):
	CONFIG={
	"camera_config":{"background_color": WHITE},
	"tipo_svg":"svg",
	"file":"",
	"escala":1.4,
	"angle":0,
	"vflip":False,
	"opacidad_fondo": 1,
	"remover": [],
	"color": BLACK,
	"fondo": BLACK,
	"grosor": 3,
	"escala_numeros":0.5,
	"mostrar_todos_numeros": False,
	"animacion": False,
	"direccion_numeros": UP,
	"color_numeros": RED,
	"separacion_numeros":0,
	"muestra_elementos":[],
	"color_resaltado":BLUE,
	}
	def construct(self):
		if self.tipo_svg=="svg":
			self.imagen=SVGMobject(
		        "%s"%self.file,
		        fill_opacity = 1,
		        stroke_width = self.grosor,
		        stroke_color = self.color,
		    ).rotate(self.angle).set_fill(self.fondo,self.opacidad_fondo).scale(self.escala)
		else:
			self.imagen=self.importa_texto().set_fill(self.fondo,self.opacidad_fondo).rotate(self.angle).set_stroke(self.color,self.grosor).scale(self.escala)
		if self.vflip==True:
			self.imagen.flip()
		self.cambiar_colores(self.imagen)
		if self.animacion==True:
			self.play(DrawBorderThenFill(self.imagen))
		else:
			self.add(self.imagen)
		if self.mostrar_todos_numeros==True:
			self.imprimir_formula(self.imagen,
				self.escala_numeros,
				self.direccion_numeros,
				self.remover,
				self.separacion_numeros,
				self.color_numeros)

		self.devolver(self.imagen,self.muestra_elementos)
		
		self.wait()
	def importa_texto(self):
		return TexMobject("")

	def cambiar_colores(self,imagen):
		pass

	def imprimir_formula(self,texto,escala_inversa,direccion,excepcion,separacion,color):
		texto.set_color(RED)
		self.add(texto)
		contador = 0
		for j in range(len(texto)):
			permiso_imprimir=True
			for w in excepcion:
				if j==w:
					permiso_imprimir=False
			if permiso_imprimir:
				self.add(texto[j].set_color(self.color))
		contador = contador + 1

		contador=0
		for j in range(len(texto)):
			permiso_imprimir=True
			elemento = TexMobject("%d" %contador,color=color)
			elemento.scale(escala_inversa)
			elemento.next_to(texto[j],direccion,buff=separacion)
			for w in excepcion:
				if j==w:
					permiso_imprimir=False
			if permiso_imprimir:
				self.add(elemento)
			contador = contador + 1 

	def devolver(self,formula,adicion):
		for i in adicion:
			self.add_foreground_mobjects(formula[i].set_color(self.color_resaltado),
				TexMobject("%d"%i,color=self.color_resaltado).next_to(formula[i],self.direccion_numeros,buff=self.separacion_numeros).scale(self.escala_numeros))

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
    def tema(self,texto,**kwargs):
        return Texto("\\begin{flushleft} %s \\end{flushleft}"%texto,**kwargs)

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
    		bloque=VGroup()
    		while self.contenido[c]!="--":
    			bloque.add(self.tema(self.contenido[c]))
    			c=c+1
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
        self.titulo=Texto("\\sc\\underline{Contenido}").scale(2).to_edge(UR)
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
    		self.titulo.shift,UP*5,
    		self.bloques.shift,DOWN*10,
    		self.bloques_estatica.shift,DOWN*10)
