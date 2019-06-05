from big_ol_pile_of_manim_imports import *

class Grilla3(Scene):
    def construct(self):
        grillax=Grilla()
        p1=Dot(coord(3.05,-1))
        self.play(ShowCreation(grillax),DrawBorderThenFill(p1))
        self.wait()

class NuevaEscrituraA(Scene):
    def construct(self):
        texto=Texto("Teoría de la gravedad").to_corner(UL)
        texto2=Texto("Contradicción con la ciencia").move_to(texto,aligned_edge=LEFT+UP)
        #self.add(texto2)
        linea_guia=Line(texto.get_corner(UL),texto.get_corner(DL)).shift(LEFT*0.4).scale(1.3)
        self.play(FadeIn(linea_guia))
        grupo_lineas=VGroup()
        for letter in texto:
            linea = Line(letter.get_top(),letter.get_bottom())
            # circle = letter.copy()
            linea.replace(letter, dim_to_match=1)
            linea.fade(1)
            linea.save_state()
            grupo_lineas.add(linea)
            linea.target = letter
        #------------------------------------------
        linea_guia2=Line(texto2.get_corner(UL),texto2.get_corner(DL)).shift(LEFT*0.4).scale(1.3)
        grupo_lineas2=VGroup()
        for letter in texto2:
            linea = Line(letter.get_top(),letter.get_bottom())
            # circle = letter.copy()
            linea.replace(letter, dim_to_match=1)
            linea.fade(1)
            linea.save_state()
            grupo_lineas2.add(linea)
            linea.target = letter
        
        self.play(LaggedStart(MoveToTarget,grupo_lineas,run_time=1.1),linea_guia.move_to,texto[-1].get_right()+RIGHT*0.4)
        self.play(FadeOut(linea_guia))
        self.wait()
        self.play(FadeIn(linea_guia2))
        self.play(LaggedStart(Restore,grupo_lineas,run_time=1.1),LaggedStart(MoveToTarget,grupo_lineas2,run_time=1.1),
            linea_guia2.move_to,texto2[-1].get_right()+RIGHT*0.4)
        self.play(FadeOut(linea_guia2))
        self.wait()

class Perturbacion(ContinualAnimation):
    CONFIG = {
        "amplitude": 0.4,
        "jiggles_per_second": 1,
    }

    def __init__(self, group, **kwargs):
        for submob in group.submobjects:
            submob.jiggling_direction = rotate_vector(
                RIGHT, np.random.random() * TAU,
            )
            submob.jiggling_phase = np.random.random() * TAU
        ContinualAnimation.__init__(self, group, **kwargs)

    def update_mobject(self, dt):
        for submob in self.mobject.submobjects:
            submob.jiggling_phase += dt * self.jiggles_per_second * TAU
            submob.shift(
                self.amplitude *
                submob.jiggling_direction *
                np.sin(submob.jiggling_phase) * dt
            )

class Particula(Scene):
    def construct(self):
        punto=VGroup(Dot(radius=0.6).shift(LEFT+UP),Dot(radius=0.6).shift(RIGHT+DOWN),Dot(radius=0.6))
        punto2=punto.copy().shift(LEFT*2)
        self.play(GrowFromCenter(punto),GrowFromCenter(punto2))
        self.add(Perturbacion(punto),Perturbacion(punto2))
        self.wait(5)
        self.remove(Perturbacion(punto),Perturbacion(punto2))
        self.add(Perturbacion(punto,amplitude=0.6),Perturbacion(punto2,amplitude=0.6))
        self.wait(5)
        self.remove(Perturbacion(punto),Perturbacion(punto2))
        self.add(Perturbacion(punto,amplitude=0.8),Perturbacion(punto2,amplitude=0.8))
        self.wait(5)
        self.remove(Perturbacion(punto),Perturbacion(punto2))
        self.add(punto,punto2)
        self.wait(5)

class Dimensiones(Scene):
    def construct(self):
        rectangulo=Rectangle(width=5,height=3)
        rectangulo.rotate(30*DEGREES)
        linea=Line(LEFT*1.5,RIGHT*1.5)
        linea.rotate(20*DEGREES)
        linea.shift(LEFT*2)
        v_medicion=Medicion(linea,color=BLUE,dashed=False)
        self.play(ShowCreation(linea))
        self.play(GrowFromCenter(v_medicion))
        def update(grupo):
            angulo=linea.get_angle()
            tam_med=grupo[1].get_length()/2
            vu=linea.get_unit_vector()
            mr=rotation_matrix(PI/2,OUT)
            #grupo.rotate(angulo)
            grupo[0].put_start_and_end_on(linea.get_start(),linea.get_end())
            direccion=np.matmul(mr,vu)
            grupo[0].shift(direccion*0.3)
            origen1=grupo[0].get_end()
            fin1_1=origen1+direccion*tam_med
            fin1_2=origen1-direccion*tam_med
            grupo[1].put_start_and_end_on(fin1_1,fin1_2)

            origen2=grupo[0].get_start()
            fin2_1=origen2+direccion*tam_med
            fin2_2=origen2-direccion*tam_med
            grupo[2].put_start_and_end_on(fin2_1,fin2_2)


        self.play(linea.scale,2,linea.rotate,PI/8,
            UpdateFromFunc(
            v_medicion,update))
        self.wait(2)


class Codigu(Scene):
    def construct(self):
        cod=TikzMobject("""
\\begin{lstlisting}[language=Python,style=basic]
import numpy as np
    
def incmatrix(genl1,genl2):
    m = len(genl1)
    n = len(genl2)
    M = None #to become the incidence matrix
    VT = np.zeros((n*m,1), int)        #dummy variable
    
\\end{lstlisting}
            """,color=WHITE).set_width(FRAME_WIDTH*0.85).set_stroke(None,0).set_fill(WHITE,1)
        self.play(Write(cod))
        self.wait()

class Diagrama(Scene):
    def construct(self):
        cod=TikzMobject("""
\\begin{tikzpicture}[node distance = 1.5cm, auto]
\\node [cloud] (init) {Inicio};
\\node [oi, below of= init, node distance=1.7cm] (imp) {Hola Mundo!};
\\node [cloud, below of=imp, node distance=1.7cm] (fin) {Fin}; 
\\path [line] (init)--(imp);
\\path [line] (imp)--(fin);
\\end{tikzpicture}
            """).set_height(FRAME_HEIGHT*0.85).set_width(FRAME_WIDTH*0.85).set_stroke(None,0).set_fill(WHITE,1)
        self.play(Write(cod))
        self.wait()

class Tabla(Scene):
    def construct(self):
        cod=TextMobject("""
   \\begin{tabular}{|c|c|c|}\\hline
Medición    &   $x_n$   &   $y_{n,k}$   \\\\\\hline
1   &   67  &   62.5    \\\\\\cline{1-1} \\cline{3-3}
2   &   &   61.04   \\\\\\cline{1-1} \\cline{3-3}
3   &   &   61.04   \\\\\\cline{1-1} \\cline{3-3}
4   &   &   62.01   \\\\\\cline{1-1} \\cline{3-3}
5   &   &   62.5    \\\\\\cline{1-1} \\cline{3-3}
6   &   &   63.48   \\\\\\cline{1-1} \\cline{3-3}
7   &   &   63.48   \\\\\\cline{1-1} \\cline{3-3}
8   &   &   63.96   \\\\\\cline{1-1} \\cline{3-3}
9   &   &   64.94   \\\\\\cline{1-1} \\cline{3-3}
10  &   &   65.043  \\\\\\hline
   \\end{tabular}
            """).set_height(FRAME_HEIGHT*0.85)
        self.play(Write(cod))
        self.wait()

class Grafica(Scene):
    def construct(self):
        cod=TikzMobject("""
    \\begin{tikzpicture}[scale=1]
\\begin{axis}[
    xlabel={$x_n$ [\\textcelsius]},
    ylabel={$y_n$ [\\textcelsius]},
    xmin=15, xmax=70,
    ymin=15, ymax=70,
    xtick={15,20,...,70},
    ytick={15,20,...,70},
    legend pos=north west,
    ymajorgrids=true,
    xmajorgrids=true,
    grid style=dashed,
]

\\addplot[
    color=blue,
    mark=square,
    ]
    coordinates {
(   67  ,   62.9993 )
(   43  ,   36.603  )
(   28  ,   32.52   )
(   28  ,   31.787  )
(   24  ,   23.342  )
(   22  ,   23.636  )
(   18  ,   22.509  )
(   24  ,   24.41   )
(   20  ,   21.97   )
(   21.5    ,   22.85   )

    };
    \\addlegendentry{Abajo hacia arriba}

\\addplot [blue, domain=15:70,dashed] {5.7675+0.8289*x};
\\addlegendentry{$y_n=mx_n+b$ ($\\uparrow$)}
    
\\addplot[
    color=red,
    mark=triangle,
    ]
    coordinates {
(   22.5    ,   20.95   )
(   25  ,   22.36   )
(   24  ,   24.36   )
(   26  ,   25.97   )
(   26  ,   24.07   )
(   29  ,   27.05   )
(   33  ,   29.91   )
(   37.5    ,   31.61   )
(   41  ,   33.49   )
(   52.3    ,   36.37   )
    };
    \\addlegendentry{Arriba hacia abajo}

\\addplot [red, domain=15:70,dashed] {11.0398+0.5127*x};
\\addlegendentry{$y_n=mx_n+b$ ($\\downarrow$)}
\\end{axis}
\\end{tikzpicture}
            """).set_height(FRAME_HEIGHT*0.85).set_fill(None,0).set_stroke(None,1)
        self.play(Write(cod))
        self.wait()


class MaquinaEscribir(Scene):
    CONFIG = {"include_sound": True}
    def construct(self):
        self.wait()
        texto=TextMobject("\\tt <opinión>").scale(2)
        TypeWriter(self,texto,end=True)
        self.wait()

class Teclado(Scene):
    CONFIG = {"include_sound": True}
    def construct(self):
        self.wait()
        texto=TextMobject("""
            \\tt </contenido>
            """).scale(2)
        KeyBoard_(self,texto,p=0.1,time_random=0.1)
        self.wait()

class Teclado2(Scene):
    CONFIG = {"include_sound": True}
    def construct(self):
        self.wait()
        texto=TextMobject("""
            \\tt Qué onda Denyche\\\\
            ¿Qué te parece mi animación\\\\
            de máquina de escribir?\\\\
            :)
            """).scale(2)
        TypeWriter(self,texto,spaces=[3,7,18,20,26,28,39,46,48],enters=[14,37,60],p=0.08,time_random=0.08,end=True)
        self.wait()

class TecladoPrueba(Scene):
    CONFIG = {"include_sound": True}
    def construct(self):
        self.wait()
        texto="""
            \\tt Qué onda Denyche\\\\
            Qué te .
            """
        texto_t=TextMobject(texto).scale(2)
        KeyBoard_(self,texto_t,p=0.05,time_random=0.06)
        self.wait()

class PruebaSplit(Scene):
    CONFIG = {"include_sound": True}
    def construct(self):
        texto=TextMobject("\\tt <a> ... ||| ,,,\\\\ Empieza contenido\\\\ </a>",color=WHITE)
        contador_espacios=0
        contador_enters=0
        for i in range(len(texto)-1):
            pre_ty=texto[i].get_center()[1]
            pre_tx=texto[i].get_center()[0]
            pos_ty=texto[i+1].get_center()[1]
            pos_tx=texto[i+1].get_center()[0]
            pre_width=texto[i].get_width()/2
            pos_width=texto[i+1].get_width()/2
            pre_height=texto[i].get_height()/2
            pos_height=texto[i+1].get_height()/2
            dist_min_x=(pre_width+pos_width)*1.6
            dist_min_y=(pre_height+pos_height)*1.2
            if abs(pre_ty-pos_ty)>dist_min_y:
                contador_enters+=1
            elif abs(pre_tx-pos_tx)>dist_min_x and abs(pre_ty-pos_ty)<dist_min_y:
                contador_espacios+=1


        resultados=VGroup(TextMobject("%d"%contador_espacios),
                    TextMobject("%d"%contador_enters),texto
                    ).arrange_submobjects(DOWN)
        self.add(resultados)
        self.wait()

class TecladoCheck(CheckFormula):
    CONFIG={
    "svg_type": "text",
    "show_numbers": True
    }
    def import_text(self):
        return TextMobject("""
            \\tt Qué onda Denyche\\\\
            ¿Qué te parece mi animación\\\\
            de teclado de computadora?\\\\
            :)
            """).scale(2)

class SoundTest(Scene):
    CONFIG = {"include_sound": True}
    def construct(self):
        title=TextMobject("Sound Test").to_edge(UP)
        self.play(Write(title))
        self.wait()
        self.add_sound("a3",gain=-10)
        self.add_sound("a5",gain=-10)
        self.add_sound("a6",gain=-10)
        self.wait()

class NuevoEfecto1(Scene):
    def construct(self):
        texto=TextMobject("Texto",color=WHITE).scale(3)
        self.play(Escribe(texto))
        pre_rectangulo=Rectangle(width=0.01,height=texto.get_height()*1.1).set_fill(YELLOW).fade(0.7).set_stroke(None,0)
        pos_rectangulo=Rectangle(width=texto.get_width()*1.1,height=texto.get_height()*1.1).set_fill(YELLOW).fade(0.7).set_stroke(None,0)
        pos_rectangulo.move_to(texto)
        pre_rectangulo.next_to(pos_rectangulo,LEFT,buff=0)
        self.play(Transform(pre_rectangulo,pos_rectangulo))
        self.wait()
        self.play(pre_rectangulo.fade,1)
        self.wait()

class NuevoEfecto2(Scene):
    def construct(self):
        texto1=TextMobject("Texto 1",color=WHITE).scale(3)
        texto2=TextMobject("Texto 2",color=WHITE).scale(3)
        VGroup(texto1,texto2).arrange_submobjects(DOWN,buff=0.5)
        self.play(Escribe(texto1),Escribe(texto2))
        rectangulo1=Rectangle(width=FRAME_WIDTH,height=texto1.get_height()*1.1).set_fill(YELLOW).fade(0.7).set_stroke(None,0)
        rectangulo2=Rectangle(width=FRAME_WIDTH,height=texto2.get_height()*1.1).set_fill(YELLOW).fade(0.7).set_stroke(None,0)
        rectangulo1.move_to(texto1)
        rectangulo2.move_to(texto2)
        #self.add(rectangulo1)
        self.wait()
        self.play(FadeIn(rectangulo1))
        self.wait()
        self.play(Transform(rectangulo1,rectangulo2))
        #self.remove(rectangulo1)
        #self.add(rectangulo2)
        self.wait()



class Soporte(Scene):
    def construct(self):
        pat1=Patron(width=4,height=7,grosor=0.5,agregar_base=True,direccion="R",stroke_width=5)
        pat1[-1].scale(1.007).shift(RIGHT*0.02)
        pat2=Patron(width=2,height=7,grosor=0.5,agregar_base=True,direccion="R",stroke_width=5)
        pat2[-1].scale(1.007).shift(RIGHT*0.02)
        pat1.shift(LEFT*4)
        pat2.shift(LEFT*4)
        self.play(*[LaggedStart(ShowCreation,pat1[i],rate_func=linear)for i in range(len(pat1))])
        self.play(Transform(pat1,pat2))
        self.wait()

class Codigo(Scene):
    def construct(self):
        cod=TikzMobject("""
\\begin{lstlisting}[language=Python]
import numpy as np
    
def incmatrix(genl1,genl2):
    m = len(genl1)
    n = len(genl2)
    M = None #to become the incidence matrix
    VT = np.zeros((n*m,1), int)  #dummy variable
    
    #compute the bitwise xor matrix
    M1 = bitxormatrix(genl1)
    M2 = np.triu(bitxormatrix(genl2),1) 

    for i in range(m-1):
        for j in range(i+1, m):
            [r,c] = np.where(M2 == M1[i,j])
            for k in range(len(r)):
                VT[(i)*n + r[k]] = 1;
                VT[(i)*n + c[k]] = 1;
                VT[(j)*n + r[k]] = 1;
                VT[(j)*n + c[k]] = 1;
                
                if M is None:
                    M = np.copy(VT)
                else:
                    M = np.concatenate((M, VT), 1)
                
                VT = np.zeros((n*m,1), int)
    
    return M
\\end{lstlisting}
            """)
        self.play(Write(cod))
        self.wait()



class SVG1(CheckSVG):
    CONFIG={
    "camera_config":{"background_color":N_FONDO_VERDE_PASTEL},
    "file":"pruebas/output3",
    "set_size":"height",
    "stroke_width":0.1,
    "animation":True
    }

class SVG2(CheckSVG):
    CONFIG={
    "svg_type": "text",
    }
    def import_text(self):
        return TexMobject("a+b+c+d=\\sqrt{x}")

class Indice(EscenaContenido):
    CONFIG={
    "escala":0.7
    }
    def setup(self):
        self.contenido=[
            "Tema de lo que \\\\ sea - (6:20)",
                "Sub tema",
                "Sub tema",
            "--",
            "Tema - (6:12)",
                "Sub tema",
                "Sub tema",
            "--",
            "Tema",
                "Sub tema",
                "Sub tema",
                "Sub tema",
            "--",
            "Tema",
                "Sub tema",
            "--",]

	
class ImagenE(Scene):
    def construct(self):
        nota=Nota1()
        cinta=Cinta1()
        self.play(GrowFromCenter(nota))
        self.wait()
        self.play(GrowFromCenter(cinta))
        self.wait()
	
class SquareToCircle(Scene):
    def construct(self):
        circle = Circle()
        square = Square()
        square.flip(RIGHT)
        square.rotate(-3 * TAU / 8)
        circle.set_fill(PINK, opacity=0.5)

        self.play(ShowCreation(square))
        self.play(Transform(square, circle))
        self.play(FadeOut(square))


class WarpSquare(Scene):
    def construct(self):
        square = Square()
        self.play(ApplyPointwiseFunction(
            lambda point: complex_to_R3(np.exp(R3_to_complex(point))),
            square
        ))
        self.wait()


class WriteStuff(Scene):
    def construct(self):
        example_text = TextMobject(
            "Alexander, cómo estas?? is a some text",color=WHITE,
            tex_to_colo_map={"text": YELLOW,"some":N_ROJO_1}
        )
        example_tex = TexMobject(
            "\\sum_{k=1}^\\infty {1 \\over k^2} = {\\pi^2 \\over 6}",
        )
        group = VGroup(example_text, example_tex)
        group.arrange_submobjects(DOWN)
        group.set_width(FRAME_WIDTH - 2 * LARGE_BUFF)

        self.play(Write(example_text))
        self.play(Write(example_tex))
        self.wait()


class UdatersExample(Scene):
    def construct(self):
        decimal = DecimalNumber(
            0,
            show_ellipsis=True,
            num_decimal_places=3,
            include_sign=True,
        )
        square = Square().to_edge(UP)

        decimal.add_updater(lambda d: d.next_to(square, RIGHT))
        decimal.add_updater(lambda d: d.set_value(square.get_center()[1]))
        self.add(square, decimal)
        self.play(
            square.to_edge, DOWN,
            rate_func=there_and_back,
            run_time=5,
        )
        self.wait()
	
class ObjetoCaja(Scene):
    def construct(self):
        objeto=Caja(ancho=4)
        cinta=Nota1()
        cinta.move_to(objeto)
        objeto_etiqueta=Formula("A",color=BLACK).move_to(objeto)
        cinta.set_height(objeto_etiqueta.get_height()*2)
        self.play(ShowCreation(objeto))
        self.play(objeto.set_fill,None,0.85)

        def update(imagen):
            imagen.move_to(objeto_etiqueta)
            return imagen
        self.play(FadeInFrom(cinta,UP))
        self.wait()

        self.play(Escribe(objeto_etiqueta))
        objeto.add(objeto_etiqueta)
        self.play(objeto.shift,DOWN*3+LEFT*2,UpdateFromFunc(cinta,update),path_arc=PI/4)
        self.wait()
        self.play(objeto_etiqueta.move_to,objeto.get_corner(UL),objeto_etiqueta.shift,cinta.get_width()*RIGHT*1.3/2+cinta.get_height()*DOWN*1.3/2,UpdateFromFunc(cinta,update))
        self.play(abrir_caja(objeto))

        self.play(objeto.shift,UP*4.5+RIGHT*4,UpdateFromFunc(cinta,update),path_arc=PI/4)
        self.wait()
        self.play(cerrar_caja(objeto))
        self.wait()
        
class Acentos(Scene):
    def construct(self):
        acentos_tradicional=TextMobject("Acento tradicional: \\'a \\~n").scale(2).to_edge(DOWN)
        acentos_moderno=TextMobject("Acento moderno: á ñ").scale(2).to_edge(UP)
        self.play(Write(acentos_tradicional))
        self.play(Write(acentos_moderno))
        self.wait()

class Cancel(Scene):
    def construct(self):
        example_text = TexMobject(
            "\\cancel{x^2}"
        ).scale(3)
        example_text[0:2].set_color(RED)
        self.play(Write(example_text[2:]))
        self.play(Write(example_text[0:2]))
        self.wait()
        
#Probar \\ECFAugie si puedes usar emerald
class AnimacionEscribe(Scene):
    def construct(self):
        esc_desv=TextMobject("Escribe y luego \\\\ se desvanece").scale(2)
        esc=TextMobject("Escribe").scale(3)
        self.play(Escribe_y_desvanece(esc_desv,color_orilla=GREEN_B,stroke_width=2,factor_desvanecimiento=8.5),run_time=4.5)
        self.play(Escribe(esc,color_orilla=YELLOW_B,stroke_width=1,factor_desvanecimiento=6))
        self.wait()
        
class Titulo(Scene):
    def construct(self):
        tikz="""
            \\begin{tikzpicture}[pencildraw/.style={decorate,
            decoration={random steps,segment length=0.8pt,amplitude=0.3pt}}]
                \\node[pencildraw,draw] {\\sc Derivada};
            \\end{tikzpicture} 
              """
        tit=TikzMobject(tikz,stroke_width=2,fill_opacity=.1).scale(3)
        tit[1:].set_stroke(None,0).set_fill(WHITE,1)
        self.play(Write(tit),run_time=3)
        self.wait()


class Dedo(Scene):
    def construct(self):
        dedo = SVGMobject(
            file_name = "tu",
            fill_opacity = 0,
            stroke_width = 0.2,
            height = 4,
            stroke_color = WHITE,
        )
        dedo[0].set_fill("#F4D7AB",1).set_stroke(None,3)
        dedo[1:].set_stroke(None,0.1)
        dedo[4:].set_fill("#EDCE9F",1)
        dedo[11:15].set_fill(WHITE,1)
        dedo[7].set_fill(BLACK,1)
        dedo[10].set_fill(BLACK,1)
        dedo[12:14].set_fill("#EDCE9F",1)

        self.play(DrawBorderThenFill(dedo))
        self.wait()
        self.play(ApplyMethod(dedo.scale, 1.5,rate_func=there_and_back))
        self.wait()


class Dedo2(Scene):
    def construct(self):
        ecuation=TexMobject("ax+b=0").scale(1)
        dedo = SVGMobject(
            file_name = "dedo",
            fill_opacity = 0,
            stroke_width = 1.5,
            height = 1,
            stroke_color = TT_TEXTO,
        ).flip()
        dedo.next_to(ecuation,RIGHT,buff=0.5)
        senhalar=ApplyMethod(dedo.shift, np.array([-0.3,0,0]),rate_func=there_and_back,run_time=0.7)
        self.play(Write(ecuation))
        self.play(LaggedStart(Write,dedo,submobject_mode = "lagged_start",rate_func=lambda t : smooth(t)),run_time=1.5)
        self.play(senhalar)

        self.wait()
        
class Redes(Scene):
    def construct(self):
        twitter = Twitter().set_fill("#12C0FF").set_stroke("#12C0FF").scale(0.6)
        facebook = Facebook().set_fill("#3C5A9A").set_stroke("#3C5A9A").scale(0.6)
        github = GitHub()
        youtube=YouTube().set_fill("#FE0000").set_stroke("#FE0000").scale(0.6)
        facebook.shift(LEFT*2)
        github.set_height(facebook.get_height()).scale(0.96)
        twitter.next_to(facebook,LEFT,buff=1)
        youtube.next_to(facebook,RIGHT,buff=1)
        github.next_to(youtube,RIGHT,buff=1)
        redes_s=VGroup(twitter,facebook,youtube,github)
        redes_s.move_to(ORIGIN)
        redes_f=redes_s.copy()
        redes_f.arrange_submobjects(
            DOWN, aligned_edge=LEFT, buff=0.4
            )
        texto=VGroup(
            TextMobject("\\tt twitter").match_color(twitter),
            TextMobject("\\tt facebook").match_color(facebook),
            TextMobject("\\tt youtube").match_color(youtube),
            TextMobject("\\tt github").match_color(github)
            )
        redes_f.to_edge(LEFT).scale(0.7).shift(LEFT*0.7)
        for i in range(len(texto)):
            texto[i].next_to(redes_f[i],RIGHT,buff=0.8)


        self.play(DrawBorderThenFill(redes_s),run_time=3)
        self.play(ReplacementTransform(redes_s,redes_f))
        self.wait(0.1)
        self.add_foreground_mobject(redes_f)
        circles=VGroup(*[Dot(redes_f[i].get_center(),color=WHITE,radius=twitter.get_width()*0.5).scale(0.9)for i in range(len(redes_f)-1)])
        texto.shift(RIGHT*2)
        punto=Dot(redes_f.get_center()).shift(RIGHT*2)
        vector=punto.get_center()[0]-redes_f.get_center()[0]
        circles.set_fill(None,0)
        self.add(circles)
        def update(grupo):
            for i in range(len(grupo)):
                grupo[i].move_to(redes_f[i].get_center())
                dif=(punto.get_center()[0]-grupo.get_center()[0])
                grupo.set_fill(WHITE,smooth(1-dif/vector))
            return grupo
        

        #self.play(FadeIn(circles))
        self.play(redes_f.shift,RIGHT*2,
            UpdateFromFunc(circles,update),
            *[Escribe(texto[i],color_orilla=texto[i].get_color(),factor_desvanecimiento=8,stroke_width=0.7)for i in range(len(texto))])
        circles.set_fill(WHITE,1)
        self.add(circles)
        redes_fc=redes_f.copy()
        redes_fc.set_fill(opacity=0)
        redes_fc.set_stroke(WHITE,3)
        redes_fc[-1].set_stroke(BLACK,1.5)
        
        
        for x in range(2):
            self.play(
                ShowPassingFlash(
                    redes_fc, 
                    time_width = 0.5,
                    run_time = 2,
                    rate_func=linear
                )
            )
        
        self.wait()


class OmegaDice(Scene):
    def construct(self):
        Ale=Alex()
        palabras_ale = TextMobject("Yo soy OmegaCreature")
        self.play(FadeIn(Ale.to_edge(DL)))
        self.play(Blink(Ale))
        self.play(OmegaCreatureDice(
            Ale, palabras_ale, 
            bubble_kwargs = {"height" : 3, "width" : 4},
            target_mode="speaking"
        ))
        self.wait()
        self.play(Blink(Ale))
        self.play(RemueveDialogo(Ale))
        self.play(
            Ale.change_mode, "participa"
        )
        self.play(OmegaCreatureDice(
            Ale, palabras_ale, 
            bubble_kwargs = {"height" : 3, "width" : 4},
            target_mode="participa"
        ))
        self.wait()
        self.play(Blink(Ale))
        self.play(RemueveDialogo(Ale))       
        self.play(FadeOut(Ale))
        self.wait(0.5)
        

#-------Funciones para Circuito
def imprimir_formula_paso_1(self,texto,escala,escala_inversa,direccion,excepcion,separacion):
    excepcion=0
    self.add(texto.scale(escala))
    contador = 0
    for j in range(len(texto)):
        elemento = TexMobject("%d" %contador)
        texto[j].set_color(RED)
        self.add(texto[j])
        elemento.set_fill(opacity=1)
        elemento.to_edge(UP)
        self.add(elemento)
        self.wait(0.02)
        elemento.set_fill(opacity=0)
        texto[j].set_color(WHITE)
        contador = contador + 1 

#exporta -s
def imprimir_formula_paso_2(self,texto,escala,escala_inversa,direccion,excepcion,separacion):
    texto.scale(escala).set_color(RED)
    self.add(texto)
    contador = 0
    for j in range(len(texto)):
        permiso_imprimir=True
        for w in excepcion:
            if j==w:
                permiso_imprimir=False
        if permiso_imprimir:
            self.add(texto[j].set_color("#808080"))
        contador = contador + 1

    contador=0
    for j in range(len(texto)):
        permiso_imprimir=True
        elemento = TexMobject("%d" %contador,color=WHITE)
        elemento.scale(escala_inversa)
        elemento.next_to(texto[j],direccion,buff=separacion)
        for w in excepcion:
            if j==w:
                permiso_imprimir=False
        if permiso_imprimir:
            self.add(elemento)
        contador = contador + 1 

def devolver_formula_excepcion(formula,excepcion):
    form=VGroup()
    for i in range(len(formula)):
        vt=True
        for e in excepcion:
            if i==e:
                vt=False
        if vt:
            form.add(formula[i])
    return form

def devolver_formula_adicion(formula,adicion):
    form=VGroup()
    for i in range(len(formula)):
        vt=False
        for e in adicion:
            if i==e:
                vt=True
        if vt:
            form.add(formula[i])
    return form

#------------

class Circuito(Scene):
    def construct(self):
        p_tex="""  \\begin{circuitikz}[american]
                    \\draw[ultra thin](-2,-2) to [vsourcesin,invert,f<=$5\\un{A}$,o-,l=$V$] (-2,2); 
                    \\draw[ultra thin](-2,2) to [R,v^=$ $,l_=$8\\un{k\\Omega}$,o-*] (0,2) to [cute inductor,v_=$ $,l^=$7\\un{H}$,*-*] (2,2);
                    \\draw[ultra thin](2,2) to [C,i<=$5\\un{A}$,l^=$8\\un{\\mu F}$] (2,-2) to[lamp,*-] (-2,-2);
                    \\draw[-stealth] ([shift=(20:1cm)]0,0) arc (20:300:1cm) node [above] {$i=5\\un{A}$};
                    \\end{circuitikz}"""
        tex_a=TikzMobject(p_tex,stroke_width=2,fill_opacity=0)
        tex_b=TikzMobject(p_tex,stroke_width=0,fill_opacity=1)
        tex_c=TikzMobject(p_tex,stroke_width=0,fill_opacity=1)
        excepcion=[
                        3,15,27,28,30,44,45,18,9,10,11,12,7,8,19,20,21,22,23,31,32,33,34,46,47,78,49,39,40,41,42,43,53,54,55,56,57,6,48,58,51,59,60
                    ]
        adicion1=[35,36,25,24]
        adicion2=[16,17,4,29]
        circ1=devolver_formula_excepcion(tex_a,excepcion)
        circ2=devolver_formula_adicion(tex_b,adicion1)
        circ3=devolver_formula_adicion(tex_c,adicion2)
        circ1.add(circ2).add(circ3)
        dots_black=VGroup(
            *[Dot(circ1[i].get_center(),radius = 0.07,color=BLACK)for i in [12,8,18]]
            )
        self.add_foreground_mobject(dots_black)
        ################
        light = AmbientLight(
                source_point=VectorizedPoint(tex_a[50].get_center()),
                num_levels=100,
            )
        corriente1=DashedLine(circ1[3].get_center()+UP*2.8,circ1[7].get_center(),
            dashed_segment_length=0.05,
            color = YELLOW,stroke_width = 5,
            stroke_color = YELLOW)
        corriente2=DashedLine(circ1[7].get_center(),circ1[12].get_center(),
            dashed_segment_length=0.05,
            color = YELLOW,stroke_width = 5,
            stroke_color = YELLOW)
        corriente3=DashedLine(circ1[12].get_center(),circ1[18].get_center(),
            dashed_segment_length=0.05,
            color = YELLOW,stroke_width = 5,
            stroke_color = YELLOW)
        corriente4=DashedLine(circ1[18].get_center(),circ1[3].get_center(),
            dashed_segment_length=0.05,
            color = YELLOW,stroke_width = 5,
            stroke_color = YELLOW)
        corriente5=DashedLine(circ1[3].get_center(),circ1[3].get_center()+UP*2.8,
            dashed_segment_length=0.05,
            color = YELLOW,stroke_width = 5,
            stroke_color = YELLOW)
        
        ################
        self.play(Write(circ1))
        self.play(  Succession(Animation, Mobject(), {"run_time" : 0.0001},
                    ShowCreationThenDestruction,corriente1,{"submobject_mode":"lagged_start","run_time" : 3}),
                    Succession(Animation, Mobject(), {"run_time" : 1},
                    ShowCreationThenDestruction,corriente2,{"submobject_mode":"lagged_start","run_time" : 3}),
                    Succession(Animation, Mobject(), {"run_time" : 2},
                    ShowCreationThenDestruction,corriente3,{"submobject_mode":"lagged_start","run_time" : 3}),
                    Succession(Animation, Mobject(), {"run_time" : 3},
                    ShowCreationThenDestruction,corriente4,{"submobject_mode":"lagged_start","run_time" : 3}),
                    Succession(Animation, Mobject(), {"run_time" : 4.2},
                    SwitchOn, light,{"submobject_mode":"lagged_start","run_time" : 0.2}),
                    Succession(Animation, Mobject(), {"run_time" : 4},
                    ShowCreationThenDestruction,corriente5,{"submobject_mode":"lagged_start","run_time" : 3})
                )

        
'''
Codigo y Speach.svg de Conversacion por Miroslav Olsak
https://github.com/mkoconnor
https://www.youtube.com/user/procdalsinazev/feed
'''
class Conversacion(Scene):
    def construct(self):
        conversation = Conversation(self)
        conversation.add_bubble("Hola!")
        self.wait(2)
        conversation.add_bubble("Hola, qué tal?")
        self.wait(2)
        conversation.add_bubble("Esta es mi primera animación de\\\\ conversación.")
        self.wait(3) # 41
        conversation.add_bubble("Está muy bien!")
        self.wait(2) # 48
        conversation.add_bubble("Gracias! :D")
        self.wait(2)
        self.play(FadeOut(conversation.dialog[:]))
        self.wait()




#Escenas de musica
class Percusion(Scene):
    def construct(self):
        tikz="""
            \\begin{music}
            \\instrumentnumber{1}
            \\generalmeter{\\meterfrac44}
            \\setclefsymbol1\\drumclef
            \\parindent0pt\\startpiece
            \\Notes\\zql f\\rlap\\qp\\ibu0m0\\xqb0{nn}\\en
            \\Notes\\kzq d\\zql f\\zq j\\xqb0n\\tbu0\\xqb0n\\en
            \\Notes\\zql f\\rlap\\qp\\ibu0m0\\xqb0{nn}\\en
            \\Notes\\kzq d\\zql f\\zq j\\xqb0n\\tbu0\\xqb0n\\en
            \\bar
            \\Notes\\zql f\\rlap\\qp\\ibu0m0\\kqb0{nn}\\en
            \\Notes\\xzq d\\zql f\\zq j\\kqb0n\\tbu0\\kqb0n\\en
            \\Notes\\zql f\\rlap\\qp\\ibu0m0\\kqb0{nn}\\en
            \\Notes\\xzq d\\zql f\\zq j\\kqb0n\\tbu0\\kqb0n\\en
            \\endpiece
            \\end{music}
              """
        perc=TikzMobject(tikz,stroke_width=0,fill_opacity=1).scale(0.6)
        self.play(Write(perc),run_time=3)
        self.wait()


class EscenaMusica(MusicalScene):
    def construct(self):
        self.teclado_transparente=self.definir_teclado(4,self.prop,0).set_stroke(None,0)
        self.teclado_base=self.definir_teclado(4,self.prop,1)
        self.teclado_base.move_to(ORIGIN+DOWN*3)
        self.teclado_transparente.move_to(ORIGIN+DOWN*3)

        self.wait(0.3)
        self.agregar_escenario()
        self.mandar_frente_sostenido(4,self.teclado_base)
        self.mandar_frente_sostenido(4,self.teclado_transparente)

        self.primer_paso(simbolos_faltantes=[14,15,16,17,18,19,20,21])
        self.progresion(0,run_time=2)
        self.progresion_con_desfase(paso=1,desfase=22,y1=8,x2=8,y2=16,run_time=2)
        self.progresion_con_desfase(paso=2,desfase=30,y1=8,x2=10,y2=18,simbolos_faltantes=[38,39],run_time=2)

        self.intervalos()

        self.salida_teclado()
        
        self.wait(2)


    def importar_partitura(self):
        self.partitura=TextMobject("""
                \\begin{music}
                \\parindent10mm
                \\instrumentnumber{1}
                \\setname1{} 
                \\setstaffs1{2}
                \\setclef16
                \\startextract
                \\NOTEs\\zql{'C}\\qu G|\\zql{e}\\qu j\\en
                \\NOTEs\\zql{F}\\qu{''A}|\\zql{f}\\qu{'c}\\en
                \\NOTEs\\zql{G}\\qu{'G}|\\zql{d}\\qu{'b}\\en
                \\NOTEs\\zhl{C}\\hu{'G}|\\zhl{e}\\hu{'c}\\en
                \\endextract
                \\end{music}
            """,color=BLACK).shift(UP)

    def definir_cambios_notas(self):
        self.cambios_notas=[[[
                (   14, 15, 17, 16, 18, 19, 21, 20, ),
                (   22, 23, 25, 24, 26, 27, 29, 28, )
        ]]]

        self.teclas=[[29,37,28,36],
                    [30,35,29,36],
                    [27,36,26,35],
                    [1,20,28,36]]

    def definir_colores(self):
        
        self.colores_notas=[
                       ([21,20,29,28,36,37,47,46],self.colores[3]),
                       ([18,19,26,27,34,35,44,45],self.colores[2]),
                       ([17,16,25,24,33,32,43,42],self.colores[1]),
                       ([14,15,22,23,30,31,40,41,38,39],self.colores[0])
                      ]


    def definir_cifrado(self):
        cifrado=VGroup(
            TexMobject("\\mbox{I}_3^6",color=BLACK),
            TexMobject("\\mbox{IV}_3^4",color=BLACK),
            TexMobject("\\mbox{V}",color=BLACK),
            TexMobject("\\mbox{I}",color=BLACK)
            )
        bajo=[15,23,31,41]
        cifrado[0].next_to(self.partitura[15],DOWN,buff=1.3)
        cords_x=[*[self.partitura[w].get_center()[0]for w in bajo]]
        
        for i in range(1,4):
            cifrado[i].move_to(cifrado[i-1])
            dis=cords_x[i]-cords_x[i-1]
            cifrado[i].shift(np.array([dis,0,0]))

        self.cifrado=cifrado        

    def agregar_escenario(self):
        self.grupoA=VGroup(*[self.partitura[cont]for cont in [12,13]])
        self.linea=Line(self.teclado_transparente[0].get_top(),self.teclado_transparente[-1].get_top()).set_stroke(BLACK,width=1.5)
        self.play(*[LaggedStart(GrowFromCenter, self.partitura[i],run_time=2)for i in range(1,11)],
            LaggedStart(DrawBorderThenFill,self.teclado_transparente),LaggedStart(DrawBorderThenFill,self.teclado_base)
            )
        self.play(*[GrowFromCenter(x)for x in self.grupoA],FadeIn(self.linea))



    def intervalos(self):
        i6m_v=self.intervalo_v(21,15,"6-")
        i5J_v=self.intervalo_v(25,29,"5\\rm J",direccion=RIGHT)

        i2m_h=self.intervalo_h(17,25,"2+")
        i5J_h=self.intervalo_h(15,23,"5\\rm J")

        self.ap_inter_v(i6m_v)
        self.wait()
        self.play(ReplacementTransform(i6m_v.copy(),i5J_v))
        self.wait()
        self.ap_inter_h(i2m_h)
        self.wait()
        self.play(ReplacementTransform(i2m_h,i5J_h))
        self.wait()
        
    def salida_teclado(self):
        self.play(*[
                ApplyMethod(
                    self.teclado_transparente[i].set_fill,None,0
                    )
                for i,color in self.cambios_colores_teclas[3]
                ],
                FadeOut(self.linea),
            run_time=1
        )
        for i in range(len(self.teclado_transparente)):
            self.remove(self.teclado_transparente[i])
        for i in range(len(self.teclado_base)):
            self.remove(self.teclado_base[i])
        self.play(
            LaggedStart(FadeOutAndShiftDown,self.teclado_base,lambda m: (m, DOWN),run_time=1),
            LaggedStart(FadeOutAndShiftDown,self.teclado_transparente,lambda m: (m, DOWN),run_time=1)
            )
        
class Escala2(MusicalScene2):
    def setup(self):
        self.definir_teclados(1,ORIGIN,0.6)
        self.definir_teclas(1)

    def construct(self):
        self.agregar_escenario()
        self.mover_teclas()
        self.copiar_teclado()
        self.wait()
        #self.mostrar_notas(self.teclado_base)


    def agregar_escenario(self):
        #self.linea=Line(self.teclado_transparente[0].get_top(),self.teclado_transparente[-1].get_top()).set_stroke(BLACK,width=1.5)
        self.play(
            LaggedStart(FadeInFromDown,self.teclado_base)
            )
        self.wait()
        #self.play(FadeIn(self.linea))

    def mover_teclas(self):
        self.teclado_base2=self.teclado_base.copy()
        for i in range(1,len(self.teclado_base2)):
            self.teclado_base2[i].next_to(self.teclado_base2[i-1],RIGHT,buff=0)
        self.teclado_base2.move_to(ORIGIN)

        self.play(ReplacementTransform(self.teclado_base,self.teclado_base2),run_time=3.4)
        self.teclado_base3=self.teclado_base2.copy()
        self.wait()

        self.teclado_base3.move_to(np.array([0,-1.65,0]))
        for i in range(1,len(self.teclado_base3)):
            if i in [1,3,6,8,10]:
                self.teclado_base3[i].shift(UP*abs(self.teclado_base3[i].get_height()-self.teclado_base3[i-1].get_height())/2+UP*0.3*i)
            else:
                self.teclado_base3[i].shift(UP*0.3*i)

        self.play(ReplacementTransform(self.teclado_base2,self.teclado_base3),run_time=3)
        self.teclado_base=self.teclado_base3
        
        #self.teclado_base.move_to(ORIGIN)
        #self.add(Texto("%f\\\\%f"%(self.teclado_base[0].get_center()[0],self.teclado_base[0].get_center()[1]),color=RED))

    def copiar_teclado(self):
        self.play(self.teclado_base.scale,0.5)
        self.teclado_superior1=self.teclado_base.copy()
        self.teclado_superior1.next_to(self.teclado_base,RIGHT,buff=0).shift(UP*(self.teclado_base.get_height()/2+0.2))
        self.teclado_inferior1=self.teclado_base.copy()
        self.teclado_inferior1.next_to(self.teclado_base,LEFT,buff=0).shift(DOWN*(self.teclado_base.get_height()/2+0.2))
        self.play(ReplacementTransform(self.teclado_base.copy(),self.teclado_superior1,path_arc=PI),
            ReplacementTransform(self.teclado_base.copy(),self.teclado_inferior1,path_arc=PI),run_time=2.5)
        self.teclado_superior2=self.teclado_superior1.copy()
        self.teclado_inferior2=self.teclado_inferior1.copy()
        self.teclado_superior2.next_to(self.teclado_superior1,RIGHT,buff=0).shift(UP*(self.teclado_base.get_height()/2+0.2))
        self.teclado_inferior2.next_to(self.teclado_inferior1,LEFT,buff=0).shift(DOWN*(self.teclado_base.get_height()/2+0.2))
        self.play(ReplacementTransform(self.teclado_inferior1.copy(),self.teclado_inferior2,path_arc=PI),
            ReplacementTransform(self.teclado_superior1.copy(),self.teclado_superior2,path_arc=PI),run_time=2.5)

        self.teclado_superior3=self.teclado_superior2.copy()
        self.teclado_inferior3=self.teclado_inferior2.copy()
        self.teclado_superior3.next_to(self.teclado_superior2,RIGHT,buff=0).shift(UP*(self.teclado_base.get_height()/2+0.2))
        self.teclado_inferior3.next_to(self.teclado_inferior2,LEFT,buff=0).shift(DOWN*(self.teclado_base.get_height()/2+0.2))
        self.play(ReplacementTransform(self.teclado_inferior2.copy(),self.teclado_inferior3,path_arc=PI),
            ReplacementTransform(self.teclado_superior2.copy(),self.teclado_superior3,path_arc=PI),run_time=2.5)


        self.teclado_superior4=self.teclado_superior3.copy()
        self.teclado_inferior4=self.teclado_inferior3.copy()
        self.teclado_superior4.next_to(self.teclado_superior3,RIGHT,buff=0).shift(UP*(self.teclado_base.get_height()/2+0.2))
        self.teclado_inferior4.next_to(self.teclado_inferior3,LEFT,buff=0).shift(DOWN*(self.teclado_base.get_height()/2+0.2))
        self.play(ReplacementTransform(self.teclado_inferior3.copy(),self.teclado_inferior4,path_arc=PI),
            ReplacementTransform(self.teclado_superior3.copy(),self.teclado_superior4,path_arc=PI),run_time=2.5)

        self.teclado_escala=VGroup(self.teclado_base,
            self.teclado_superior1,
            self.teclado_superior2,
            self.teclado_superior3,
            self.teclado_superior4,
            self.teclado_inferior1,
            self.teclado_inferior2,
            self.teclado_inferior3,
            self.teclado_inferior4)

        self.play(self.teclado_escala.shift,np.array([2,1.8,0]),rate_func=there_and_back,run_time=3)
        self.play(self.teclado_escala.shift,np.array([-2,-1.8,0]),rate_func=there_and_back,run_time=3)




        self.teclado_3octavas=self.definir_octava_back(9).move_to(ORIGIN).scale(0.4)
        self.wait()

        
        self.play(
            *[ReplacementTransform(self.teclado_inferior4[i4],self.teclado_3octavas[i4])for i4 in range(len(self.teclado_inferior1))],
            *[ReplacementTransform(self.teclado_inferior3[i3],self.teclado_3octavas[i3+12])for i3 in range(len(self.teclado_inferior1))],
            *[ReplacementTransform(self.teclado_inferior2[i2],self.teclado_3octavas[i2+24])for i2 in range(len(self.teclado_inferior1))],
            *[ReplacementTransform(self.teclado_inferior1[i1],self.teclado_3octavas[i1+36])for i1 in range(len(self.teclado_inferior1))],
            *[ReplacementTransform(self.teclado_base[j],self.teclado_3octavas[j+48])for j in range(len(self.teclado_base))],
            *[ReplacementTransform(self.teclado_superior1[k1],self.teclado_3octavas[k1+60])for k1 in range(len(self.teclado_superior1))],
            *[ReplacementTransform(self.teclado_superior2[k2],self.teclado_3octavas[k2+72])for k2 in range(len(self.teclado_superior1))],
            *[ReplacementTransform(self.teclado_superior3[k3],self.teclado_3octavas[k3+84])for k3 in range(len(self.teclado_superior1))],
            *[ReplacementTransform(self.teclado_superior4[k4],self.teclado_3octavas[k4+96])for k4 in range(len(self.teclado_superior1))])
            #'''

        self.play(self.teclado_3octavas.shift,LEFT*3,rate_func=there_and_back,run_time=3)
        self.play(self.teclado_3octavas.shift,RIGHT*3,rate_func=there_and_back,run_time=3)

class Armonicos(Scene):
    def construct(self):
        conjunto_lineas=self.Armonics(10,tamanho=12)
        lineas_planas=conjunto_lineas[2]
        lineas_down=conjunto_lineas[1]
        lineas_up=conjunto_lineas[0]
        

        self.play(ShowCreation(lineas_planas[0]))
        for i in range(3):
            lpr=lineas_planas[i].copy()
            for w in range(2):
                self.play(Transform(lineas_planas[i],lineas_up[i]))
                self.play(Transform(lineas_planas[i],lineas_down[i]))
            self.play(ReplacementTransform(lineas_planas[i],lpr),run_time=0.7)
            self.remove(lpr)
            self.add(lineas_planas[i+1])

        self.wait()

    def Armonics(self,numero_armonicos,disminucion=False,amplitud=5,tamanho=12):
        conjunto_lineas=VGroup()
        lineas_up=VMobject()
        lineas_down=VMobject()
        lineas_planas=VMobject()
        punto_referencia=ORIGIN+LEFT*tamanho/2
        for linea_v in [lineas_up,lineas_down,lineas_planas]:
            for i in range(numero_armonicos):
                cuerda=VGroup()
                for j in range(i+1):
                    particion=tamanho/(i+1)
                    punto_inicio=punto_referencia+RIGHT*j*particion
                    punto_final=punto_referencia+RIGHT*(j+1)*particion
                    linea=Line(punto_inicio,punto_final,buff=0)
                    for k in range(3):
                        linea.points[0]=linea.get_start()
                        if linea_v==lineas_up:
                            if disminucion==True:
                                linea.points[1]=linea.points[0]+RIGHT*linea.get_length()/2+np.array([0,amplitud*np.sin(PI/2+PI*j)*0.5**i,0])
                            else:
                                linea.points[1]=linea.points[0]+RIGHT*linea.get_length()/2+np.array([0,amplitud*np.sin(PI/2+PI*j),0])
                        if linea_v==lineas_down:
                            if disminucion==True:
                                linea.points[1]=linea.points[0]+RIGHT*linea.get_length()/2+np.array([0,-amplitud*np.sin(PI/2+PI*j)*0.5**i,0])
                            else:
                                linea.points[1]=linea.points[0]+RIGHT*linea.get_length()/2+np.array([0,-amplitud*np.sin(PI/2+PI*j),0])
                        if linea_v==lineas_planas:
                            linea.points[1]=linea.points[0]+RIGHT*linea.get_length()/2
                        linea.points[2]=linea.get_end()
                    cuerda.add(linea)
                linea_v.add(cuerda)
            conjunto_lineas.add(linea_v)
        return conjunto_lineas

class Cylinder(Sphere):
    """
    Inherits from sphere so as to be as aligned as possible
    for transformations
    """

    def func(self, u, v):
        return np.array([
            np.cos(v),
            np.sin(v),
            np.cos(u)
        ])


class UnwrappedCylinder(Cylinder):
    def func(self, u, v):
        return np.array([
            v - PI,
            -self.radius,
            np.cos(u)
        ])


class ParametricDisc(Sphere):
    CONFIG = {
        "u_min": 0,
        "u_max": 1,
        "stroke_width": 0,
        "checkerboard_colors": [BLUE_D],
    }

    def func(self, u, v):
        return np.array([
            u * np.cos(v),
            u * np.sin(v),
            0,
        ])


class SphereCylinderScene(SpecialThreeDScene):
    CONFIG = {
        "cap_config": {
            "stroke_width": 1,
            "stroke_color": WHITE,
            "fill_color": BLUE_D,
            "fill_opacity": 1,
        }
    }

    def get_cylinder(self, **kwargs):
        config = merge_config([kwargs, self.sphere_config])
        return Cylinder(**config)

    def get_cylinder_caps(self):
        R = self.sphere_config["radius"]
        caps = VGroup(*[
            Circle(
                radius=R,
                **self.cap_config,
            ).shift(R * vect)
            for vect in [IN, OUT]
        ])
        caps.set_shade_in_3d(True)
        return caps

    def get_unwrapped_cylinder(self):
        return UnwrappedCylinder(**self.sphere_config)

    def get_xy_plane(self):
        pass

    def get_ghost_surface(self, surface):
        result = surface.copy()
        result.set_fill(BLUE_E, opacity=0.5)
        result.set_stroke(WHITE, width=0.5, opacity=0.5)
        return result

    def project_point(self, point):
        radius = self.sphere_config["radius"]
        result = np.array(point)
        result[:2] = normalize(result[:2]) * radius
        return result

    def project_mobject(self, mobject):
        return mobject.apply_function(self.project_point)

class ShowProjection(SphereCylinderScene):
    CONFIG = {
        # "default_angled_camera_position": {
        #     "theta": -155 * DEGREES,
        # }
    }

    def construct(self):
        self.setup_shapes()
        self.show_many_tiny_rectangles()
        #self.project_all_rectangles()
        #self.focus_on_one()
        #self.label_sides()
        #self.show_length_scaled_up()
        #self.show_height_scaled_down()

    def setup_shapes(self):
        self.sphere = self.get_sphere()
        self.cylinder = self.get_cylinder()
        self.ghost_sphere = self.get_ghost_surface(self.sphere)
        self.ghost_sphere.scale(0.99)
        self.ghost_cylinder = self.get_ghost_surface(self.cylinder)
        self.ghost_cylinder.set_stroke(width=0)

        self.add(self.get_axes())
        self.set_camera_to_default_position()
        self.begin_ambient_camera_rotation()

    def show_many_tiny_rectangles(self):
        ghost_sphere = self.ghost_sphere
        pieces = self.sphere.copy()
        random.shuffle(pieces.submobjects)
        for piece in pieces:
            piece.save_state()
        pieces.space_out_submobjects(2)
        pieces.fade(1)

        self.add(ghost_sphere)
        self.play(LaggedStart(Restore, pieces))
        self.wait()

        self.pieces = pieces

    def project_all_rectangles(self):
        pieces = self.pieces
        for piece in pieces:
            piece.save_state()
            piece.generate_target()
            self.project_mobject(piece.target)
            piece.target.set_fill(opacity=0.5)

        example_group = self.get_example_group([1, -1, 2])
        proj_lines = example_group[1]
        self.example_group = example_group

        self.play(*map(ShowCreation, proj_lines))
        self.play(
            LaggedStart(MoveToTarget, pieces),
        )
        self.wait()

    def focus_on_one(self):
        ghost_cylinder = self.ghost_cylinder
        pieces = self.pieces

        example_group = self.example_group
        original_rect, rect_proj_lines, rect = example_group

        equation = self.get_equation(rect)
        lhs, equals, rhs = equation[:3]
        lhs.save_state()
        rhs.save_state()

        self.play(
            FadeIn(ghost_cylinder),
            FadeOut(pieces),
            FadeIn(original_rect),
        )
        self.play(TransformFromCopy(original_rect, rect))
        self.wait()
        self.add_fixed_in_frame_mobjects(lhs, equals, rhs)
        self.move_fixed_in_frame_mob_to_unfixed_mob(lhs, original_rect)
        self.move_fixed_in_frame_mob_to_unfixed_mob(rhs, rect)
        self.play(
            Restore(lhs),
            Restore(rhs),
            FadeInFromDown(equals),
        )
        self.wait(5)

        self.equation = equation
        self.example_group = example_group

    def label_sides(self):
        sphere = self.sphere
        equation = self.equation
        w_brace, h_brace = equation.braces
        width_label, height_label = equation.labels

        u_values, v_values = sphere.get_u_values_and_v_values()
        radius = sphere.radius
        lat_lines = VGroup(*[
            ParametricFunction(
                lambda t: radius * sphere.func(u, t),
                t_min=sphere.v_min,
                t_max=sphere.v_max,
            )
            for u in u_values
        ])
        lon_lines = VGroup(*[
            ParametricFunction(
                lambda t: radius * sphere.func(t, v),
                t_min=sphere.u_min,
                t_max=sphere.u_max,
            )
            for v in v_values
        ])
        for lines in lat_lines, lon_lines:
            for line in lines:
                line.add(DashedMobject(line, spacing=-1))
                line.set_points([])
                line.set_stroke(width=2)
            lines.set_shade_in_3d(True)
        lat_lines.set_color(RED)
        lon_lines.set_color(PINK)

        self.play(
            *map(ShowCreationThenDestruction, lat_lines),
            run_time=2
        )
        self.add_fixed_in_frame_mobjects(w_brace, width_label)
        self.play(
            GrowFromCenter(w_brace),
            Write(width_label),
        )
        self.wait()
        self.play(
            *map(ShowCreationThenDestruction, lon_lines),
            run_time=2
        )
        self.add_fixed_in_frame_mobjects(h_brace, height_label)
        self.play(
            GrowFromCenter(h_brace),
            Write(height_label),
        )
        self.wait(2)

    def show_length_scaled_up(self):
        ghost_sphere = self.ghost_sphere
        example_group = self.example_group
        equation = self.equation
        equation.save_state()
        new_example_groups = [
            self.get_example_group([1, -1, z])
            for z in [6, 0.25]
        ]
        r1, lines, r2 = example_group

        self.stop_ambient_camera_rotation()
        self.move_camera(
            phi=65 * DEGREES,
            theta=-80 * DEGREES,
            added_anims=[
                ghost_sphere.set_stroke, {"opacity": 0.1},
                lines.set_stroke, {"width": 3},
            ]
        )
        for eg in new_example_groups:
            eg[1].set_stroke(width=3)
        self.show_length_stretch_of_rect(example_group)
        all_example_groups = [example_group, *new_example_groups]
        for eg1, eg2 in zip(all_example_groups, all_example_groups[1:]):
            if eg1 is new_example_groups[0]:
                self.move_camera(
                    phi=70 * DEGREES,
                    theta=-110 * DEGREES
                )
            self.remove(eg1)
            self.play(
                ReplacementTransform(eg1.deepcopy(), eg2),
                Transform(
                    equation,
                    self.get_equation(eg2[2])
                )
            )
            if eg1 is example_group:
                self.move_camera(
                    phi=0,
                    theta=-90 * DEGREES,
                )
            self.show_length_stretch_of_rect(eg2)
        self.play(
            ReplacementTransform(all_example_groups[-1], example_group),
            Restore(equation)
        )

    def show_length_stretch_of_rect(self, example_group):
        s_rect, proj_lines, c_rect = example_group
        rects = VGroup(s_rect, c_rect)
        line1, line2 = lines = VGroup(*[
            Line(m.get_anchors()[1], m.get_anchors()[2])
            for m in rects
        ])
        lines.set_stroke(YELLOW, 5)
        lines.set_shade_in_3d(True)
        proj_lines_to_fade = VGroup(
            proj_lines[0],
            proj_lines[3],
        )
        self.play(
            FadeIn(lines[0]),
            FadeOut(rects),
            FadeOut(proj_lines_to_fade)
        )
        for x in range(3):
            anims = []
            if lines[1] in self.mobjects:
                anims.append(FadeOut(lines[1]))
            self.play(
                TransformFromCopy(lines[0], lines[1]),
                *anims
            )
        self.play(
            FadeOut(lines),
            FadeIn(rects),
            FadeIn(proj_lines_to_fade),
        )
        self.remove(rects, proj_lines_to_fade)
        self.add(example_group)

    def show_height_scaled_down(self):
        ghost_sphere = self.ghost_sphere
        ghost_cylinder = self.ghost_cylinder
        example_group = self.example_group
        equation = self.equation
        r1, lines, r2 = example_group
        to_fade = VGroup(*[
            mob
            for mob in it.chain(ghost_sphere, ghost_cylinder)
            if np.dot(mob.get_center(), [1, 1, 0]) < 0
        ])
        to_fade.save_state()

        new_example_groups = [
            self.get_example_group([1, -1, z])
            for z in [6, 0.25]
        ]
        for eg in new_example_groups:
            eg[::2].set_stroke(YELLOW, 2)
            eg.set_stroke(width=1)
        all_example_groups = VGroup(example_group, *new_example_groups)

        self.play(
            to_fade.shift, IN,
            to_fade.fade, 1,
            remover=True
        )
        self.move_camera(
            phi=85 * DEGREES,
            theta=-135 * DEGREES,
            added_anims=[
                lines.set_stroke, {"width": 1},
                r1.set_stroke, YELLOW, 2, 1,
                r2.set_stroke, YELLOW, 2, 1,
            ]
        )
        self.show_shadow(example_group)
        for eg1, eg2 in zip(all_example_groups, all_example_groups[1:]):
            self.remove(*eg1.get_family())
            self.play(
                ReplacementTransform(eg1.deepcopy(), eg2),
                Transform(
                    equation,
                    self.get_equation(eg2[2])
                )
            )
            self.show_shadow(eg2)
        self.move_camera(
            phi=70 * DEGREES,
            theta=-115 * DEGREES,
            added_anims=[
                ReplacementTransform(
                    all_example_groups[-1],
                    example_group,
                ),
                Restore(equation),
            ]
        )
        self.begin_ambient_camera_rotation()
        self.play(Restore(to_fade))
        self.wait(5)

    def show_shadow(self, example_group):
        s_rect, lines, c_rect = example_group
        for x in range(3):
            self.play(TransformFromCopy(s_rect, c_rect))

    #
    def get_projection_lines(self, piece):
        result = VGroup()
        radius = self.sphere_config["radius"]
        for corner in piece.get_anchors()[:-1]:
            start = np.array(corner)
            end = np.array(corner)
            start[:2] = np.zeros(2)
            end[:2] = (radius + 0.03) * normalize(end[:2])
            kwargs = {
                "color": YELLOW,
                "stroke_width": 0.5,
            }
            result.add(VGroup(*[
                Line(p1, p2, **kwargs)
                for p1, p2 in [(start, corner), (corner, end)]
            ]))
        result.set_shade_in_3d(True)
        return result

    def get_equation(self, rect):
        length = get_norm(rect.get_anchors()[1] - rect.get_anchors()[0])
        height = get_norm(rect.get_anchors()[2] - rect.get_anchors()[1])
        lhs = Rectangle(width=length, height=height)
        rhs = Rectangle(width=height, height=length)
        eq_rects = VGroup(lhs, rhs)
        eq_rects.set_stroke(width=0)
        eq_rects.set_fill(YELLOW, 1)
        eq_rects.scale(2)
        equals = TexMobject("=")
        equation = VGroup(lhs, equals, rhs)
        equation.arrange_submobjects(RIGHT)
        equation.to_corner(UR)

        brace = Brace(Line(ORIGIN, 0.5 * RIGHT), DOWN)
        w_brace = brace.copy().match_width(lhs, stretch=True)
        h_brace = brace.copy().rotate(-90 * DEGREES)
        h_brace.match_height(lhs, stretch=True)
        w_brace.next_to(lhs, DOWN, buff=SMALL_BUFF)
        h_brace.next_to(lhs, LEFT, buff=SMALL_BUFF)
        braces = VGroup(w_brace, h_brace)

        width_label = TextMobject("Width")
        height_label = TextMobject("Height")
        labels = VGroup(width_label, height_label)
        labels.scale(0.75)
        width_label.next_to(w_brace, DOWN, SMALL_BUFF)
        height_label.next_to(h_brace, LEFT, SMALL_BUFF)

        equation.braces = braces
        equation.labels = labels
        equation.add(braces, labels)

        return equation

    def move_fixed_in_frame_mob_to_unfixed_mob(self, m1, m2):
        phi = self.camera.phi_tracker.get_value()
        theta = self.camera.theta_tracker.get_value()
        target = m2.get_center()
        target = rotate_vector(target, -theta - 90 * DEGREES, OUT)
        target = rotate_vector(target, -phi, RIGHT)

        m1.move_to(target)
        m1.scale(0.1)
        m1.shift(SMALL_BUFF * UR)
        return m1

    def get_example_group(self, vect):
        pieces = self.pieces
        rect = pieces[np.argmax([
            np.dot(r.saved_state.get_center(), vect)
            for r in pieces
        ])].saved_state.copy()
        rect_proj_lines = self.get_projection_lines(rect)
        rect.set_fill(YELLOW, 1)
        original_rect = rect.copy()
        self.project_mobject(rect)
        rect.shift(
            0.001 * np.array([*rect.get_center()[:2], 0])
        )
        result = VGroup(original_rect, rect_proj_lines, rect)
        result.set_shade_in_3d(True)
        return result

class Example1(Scene):
    def construct(self):
        text=TextMobject("Hola")
        self.play(Write(text))
        self.wait()
