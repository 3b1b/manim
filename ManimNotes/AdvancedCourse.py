from manimlib import *
import numpy as np

# --- Curva estrellada suave en coordenadas polares ---
def polar_star(theta: float):
    r = 2.0 + 0.5 * np.sin(5.0 * theta)   # suave y acotada
    return np.array([r * np.cos(theta), r * np.sin(theta), 0.0])

class CarlesonStarCurve(Scene):
    def construct(self):
        self.wait(2.5)
        # fondo sutil (opcional)
        bg = Rectangle(width=FRAME_WIDTH, height=FRAME_HEIGHT)\
            .set_color_by_gradient(BLUE_D, PURPLE_E).set_opacity(1.0)
        self.add(bg)

        title = TexText(r"\textbf{Carleson-like star curve}").scale(0.9).to_edge(UP, buff=0.6)
        subtitle = TexText(r"$r(\theta)=2+0.5\sin(5\theta)$").scale(0.8).next_to(title, DOWN, buff=0.25)

        # OJO: aquí usamos ParametricCurve con t_range=(t_min, t_max, paso)
        curve = ParametricCurve(
            t_func=polar_star,
            t_range=(0.0, TAU, 0.01),
            color=WHITE,
            stroke_width=4,
            use_smoothing=True
        )

        frame = SurroundingRectangle(curve, color=YELLOW, buff=0.5, fill_color=YELLOW_E, fill_opacity=0.06)

        self.play(Write(title), FadeIn(subtitle, UP))
        self.play(ShowCreation(curve), ShowCreation(frame), run_time=3)
        self.wait(2)


class CarlesonNeighborhood(Scene):
    def construct(self):
        self.wait(2.5)
        bg = Rectangle(width=FRAME_WIDTH, height=FRAME_HEIGHT)\
            .set_color_by_gradient(BLUE_E, BLUE_D).set_opacity(1.0)
        self.add(bg)

        curve = ParametricCurve(
            t_func=polar_star,
            t_range=(0.0, TAU, 0.01),
            color=WHITE,
            stroke_width=4,
            use_smoothing=True
        )
        self.play(ShowCreation(curve), run_time=2)

        # Punto móvil + disco (vecindad)
        t0 = ValueTracker(0.0)
        eps = 0.6          # radio del disco (diámetro = 1.2)
        span = 0.25        # ventana paramétrica local

        dot = always_redraw(lambda: Dot(polar_star(t0.get_value()), color=YELLOW))
        disk = always_redraw(lambda: Circle(radius=eps, color=BLUE, stroke_width=3).move_to(polar_star(t0.get_value())))

        # Arco local resaltado (aprox. por muestreo paramétrico alrededor de t0)
        def make_local_arc():
            vm = VMobject(color=RED, stroke_width=6)
            ts = np.linspace(t0.get_value() - span, t0.get_value() + span, 120)
            pts = np.array([polar_star((u % TAU)) for u in ts])
            vm.set_points_as_corners(pts)
            return vm
        local_arc = always_redraw(make_local_arc)

        # Pequeña leyenda (solo estética)
        label = VGroup(
            TexText(r"Local arc around $t_0$", color=WHITE).scale(0.6),
            TexText(r"diameter $\approx 2\varepsilon$", color=BLUE).scale(0.6)
        ).arrange(RIGHT, buff=0.25).to_corner(UR).shift(LEFT*0.3 + DOWN*0.3)

        self.play(FadeIn(dot), FadeIn(disk), FadeIn(local_arc), FadeIn(label))
        self.play(t0.animate.set_value(2*PI), run_time=8, rate_func=linear)
        self.wait(1)


class PortadaTesis(Scene):
    def construct(self):
        # Fondo animado sutil
        background = Rectangle(
            width=FRAME_WIDTH,
            height=FRAME_HEIGHT,
            fill_color=BLUE_E,
            fill_opacity=1
        )
        self.add(background)

        # Título principal
        titulo = TexText(
            r"\textbf{Fredholm Operators on Carleson Curves}",
            color=WHITE
        ).scale(1.2)
        subtitulo = TexText(
            r"\textit{Doctoral Thesis Proposal}",
            color=WHITE
        ).next_to(titulo, DOWN, buff=0.8).scale(0.9)

        # Autor y director
        autor = TexText(
            r"Author: Enrique Díaz Ocampo",
            color=WHITE
        ).scale(0.8)
        director = TexText(
            r"Advisor: Dr.\ Yuriy Karlovych",
            color=WHITE
        ).scale(0.8)
        institucion = TexText(
            r"UAEM -- Doctorado en Ciencias Matemáticas",
            color=WHITE
        ).scale(0.8)

        datos = VGroup(autor, director, institucion).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        datos.next_to(subtitulo, DOWN, buff=0.8)

        # Decoración: rectángulo alrededor del título
        marco = always_redraw(lambda: SurroundingRectangle(
            titulo,
            color=YELLOW,
            buff=0.4,
            fill_color=YELLOW_D,
            fill_opacity=0.15
        ))

        # Animaciones
        self.play(FadeIn(background))
        self.play(Write(titulo), ShowCreation(marco))
        self.wait(0.5)
        self.play(FadeIn(subtitulo, UP))
        self.play(LaggedStartMap(FadeIn, datos, lag_ratio=0.3))
        self.wait(0.5)

        # Pequeño efecto de respiración (cambia opacidad del marco)
        def update_opacity(mobj, dt):
            mobj.set_fill(opacity=0.15 + 0.05 * np.sin(self.time * 2))
        marco.add_updater(update_opacity)

        self.wait(6)



class Graphing3(Scene):
    def construct(self):
        LIM = 3

        # 1) Un único sistema de coords: NumberPlane
        plane = NumberPlane(
            x_range=[-LIM, LIM, 1],
            y_range=[0, LIM*LIM, 1],
            background_line_style={"stroke_opacity": 0.35},
        )
        # Que llene el frame y quede pegado abajo (sin margen):
        plane.set_height(FRAME_HEIGHT, stretch=True)\
             .set_width(FRAME_WIDTH, stretch=True)\
             .to_edge(DOWN, buff=0)

        plane.add_coordinate_labels()
        axis_labels = plane.get_axis_labels("x", "y")

        # 2) Grafica usando SIEMPRE el mapeo del MISMO plane
        parab = ParametricCurve(
            lambda t: plane.c2p(t, t**2),
            t_range=[-LIM, LIM, 0.1],
            color=GREEN
        )

        # 3) Label posicionado en coords del mismo plane
        label = Tex(r"y=x^2", color=YELLOW).scale(0.7)
        label.move_to(plane.c2p(1.3, 2.1))

        # 4) Animaciones
        self.play(FadeIn(plane))
        self.play(ShowCreation(parab))
        self.play(ShowCreation(axis_labels))
        self.play(FadeIn(label))
        self.wait()




# Intructions to run the scenes:
# manimgl ManimNotes/ManimCourse.py CarlesonStarCurve
# manimgl ManimNotes/ManimCourse.py CarlesonNeighborhood
# manimgl ManimNotes/ManimCourse.py PortadaTesis