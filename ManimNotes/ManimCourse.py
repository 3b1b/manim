from manimlib import *

class TestScene(Scene):
    def construct(self):
        #text = Text("Hello, Manim!")
        #self.play(Write(text))
        #self.wait(2)
        intro_words = Text("""
            The original motivation for manim was to
            better illustrate mathematical functions
            as transformations.
        """)
        intro_words.to_edge(UP)
        
        circ = Circle(radius=2.4,
                      stroke_color=BLUE, 
                      fill_color=YELLOW, 
                      fill_opacity=0.5)
        self.add(circ)
        self.play(Write(intro_words))
        self.wait(2)


class PithyScene(Scene):
    def construct(self):
        sq = Square(side_length=2.0,
                    stroke_color=GREEN,
                    fill_color=BLUE,
                    fill_opacity=0.75)
        self.play(ShowCreation(sq), run_time=3)
        self.wait()


class AnotherScene(Scene):
    def construct(self):
        name = Text("Te quiero mucho, mi Violeta!❤️")
        name.to_edge(UL,buff=0.5)
        sq = Square(side_length=2.0,
                    stroke_color=BLUE_A,
                    fill_color=PINK,
                    fill_opacity=0.6)
        tri = Triangle(stroke_color=RED,
                       fill_color=YELLOW,
                       fill_opacity=0.5)
        tri.scale(1.0).to_edge(DR)
        self.add(sq)
        self.play(Transform(sq, tri), run_time=4)
        self.wait()
        self.play(Write(name))
        self.wait(2)
        self.play(name.animate.to_edge(DOWN), run_time=2)
        self.play(tri.animate.scale(0.5).to_edge(DR), run_time=2)


class Testing(Scene):
    def construct(self):
        name = Text("Amedee").to_edge(UL,buff=0.95)

        sq= Square(side_length=0.5,
                    fill_color=GREEN,
                    fill_opacity=0.75).shift(3*LEFT)
        
        tri = Triangle().scale(0.6).to_edge(DR)

        self.play(Write(name))
        self.play(DrawBorderThenFill(sq), run_time=2)
        self.play(ShowCreation(tri), run_time=2)
        self.wait(2)
        self.play(name.animate.to_edge(UR), run_time=2)
        self.play(sq.animate.scale(2), tri.animate.to_edge(DL), run_time=2)
        self.wait(2)



class Library(Scene):
    def construct(self):
        ax = Axes(
            x_range=[-3, 3, 0.1],
            y_range=[-2, 2, 0.1],
            axis_config={"color": BLUE},
        )
        self.play(ShowCreation(ax), run_time=2)
        #func = ax.plot(lambda x: 0.5 * x**2, color=RED)
        #self.play(ShowCreation(func), run_time=2)
        self.wait(2)

class Getters(Scene):
    def construct(self):
        rect = Rectangle(color=WHITE,
                         width=1.5, 
                         height=1.5,
                         stroke_color=YELLOW,
                         fill_color=GREEN,
                         fill_opacity=0.5).to_edge(UL)
        circ = Circle(color=WHITE,
                      radius=1.0,
                      stroke_color=BLUE,
                      fill_color=RED,
                      fill_opacity=0.5)

        arrow = always_redraw( lambda:
            Line(start=rect.get_bottom(),
                  end=circ.get_top(),
                  stroke_color=PURPLE,
                  stroke_width=4, buff=0.1).add_tip()
        )

        self.play(ShowCreation(VGroup(rect, circ, arrow)), run_time=2)
        self.wait(2)
        self.play(rect.animate.to_edge(UR), circ.animate.scale(0.4), run_time=4)



class Updaters(Scene):
    def construct(self):
        num = TexText("ln(2)")
        box = always_redraw(lambda: SurroundingRectangle(num, 
                                   color=BLUE,
                                   fill_opacity=0.4,
                                   fill_color=RED,
                                   buff=0.5)
        )
        name = always_redraw(lambda: TexText("Natural Logarithm of 2").next_to(box, DOWN,buff=0.5)
                )
        self.play(ShowCreation(VGroup(num, box, name)), run_time=2)
        self.play(num.animate.shift(RIGHT*2), run_time=2)
        self.wait(2)



class ValueTrackers(Scene): # https://youtu.be/KHGoFDB-raE?si=YkTUq0Su9T43fFL0  seg 39:43
    def construct(self):
        k  = ValueTracker(5.0)

        num = always_redraw(lambda: DecimalNumber().set_value(k.get_value()))

        self.play(FadeIn(num))
        self.wait()
        self.play(k.animate.set_value(0), 
                  run_time=5,
                  rate_func=linear)
        self.wait()



class Graphing1(Scene):
    def construct(self):
        # Plano cuadriculado de fondo (opcional)
        #plane = NumberPlane(
        #    x_range = (-4, 4, 1),
        #    y_range = (0, 16, 1)
        #).to_edge(DOWN)
        #plane.add_coordinate_labels()  # <-- en ManimGL es "add_coordinate_labels"

        # Ejes para poder usar get_graph
        axes = Axes(
            x_range=(-4, 4, 1),
            y_range=(0, 16, 1),
            axis_config=dict(include_ticks=True, include_tip=False)
        ).to_edge(DOWN)
        axes.add_coordinate_labels(font_size=12)

        # y = x^2 sobre los ejes
        parab = axes.get_graph(lambda x: x**2, x_range=[-4, 4], color=GREEN)
        label = axes.get_graph_label(parab, Tex("y=x^2"), x=2.2, direction=UR)

        # Animaciones
        #self.play(ShowCreation(plane))
        self.play(ShowCreation(axes))
        self.play(ShowCreation(parab))
        self.play(FadeIn(label, shift=0.2*UP))
        self.wait()


class Graphing2(Scene): 
    def construct(self):
        LIM = 3
        plane1 = NumberPlane(x_range=[-LIM, LIM, 1], y_range=[0, LIM*LIM, 1]).to_edge(DOWN)
        parab = plane1.get_graph(lambda x: x**2, x_range=[-LIM, LIM], color=GREEN)
        plane1.add_coordinate_labels()
        #label = plane1.get_graph_label(parab, Tex("y=x^2"), x=2.2, direction=UR)
        label = Tex("y=x^2").scale(0.6).next_to(parab, RIGHT, buff=0.5 )
        label.set_color(YELLOW)
        axislables = plane1.get_axis_labels(x_label_tex="x", y_label_tex="y")
        self.play(DrawBorderThenFill(plane1))
        #self.play(DrawBorderThenFill(plane2))
        self.play(ShowCreation(VGroup(parab,label)))
        self.play(ShowCreation(axislables))
        self.play(FadeIn(label, shift=0.2*UP))
        self.wait()



class Graphing3(Scene): 
    def construct(self):
        LIM = 3
        plane1 = NumberPlane(x_range=[-LIM, LIM, 1], y_range=[0, LIM*LIM, 1]).to_edge(DOWN)
        parab = plane1.get_graph(lambda x: x**2, x_range=[-LIM, LIM], color=GREEN)
        plane1.add_coordinate_labels()
        #label = plane1.get_graph_label(parab, Tex("y=x^2"), x=2.2, direction=UR)
        label = Tex("y=x^2").scale(0.6).next_to(parab, RIGHT, buff=0.5 )
        label.set_color(YELLOW)
        axislables = plane1.get_axis_labels(x_label_tex="x", y_label_tex="y")

        area = plane1.get_riemann_rectangles(parab, 
                                             x_range=[-LIM, LIM], 
                                             dx=0.1, 
                                             stroke_width=0.01, 
                                             stroke_color=WHITE, 
                                             fill_opacity=0.75)
        
        tangent = plane1.get_tangent_line(1, parab, length=1)
        self.play(DrawBorderThenFill(plane1))
        #self.play(DrawBorderThenFill(plane2))
        self.play(ShowCreation(VGroup(parab,label)))
        self.play(ShowCreation(axislables))
        self.play(label.animate.to_edge(UP))
        self.wait()
        self.play(ShowCreation(area))
        self.wait()
        self.play(ShowCreation(tangent))
        self.wait() 

#  53 : 25 me quede aqui viendo el video de 3Blue1Brown sobre Manim
# To run this file, use the following command in your terminal:
# manimgl -pql ManimNotes/ManimCourse.py TestScene -w
# manimgl -pql ManimNotes/ManimCourse.py PithyScene -w
# manim -pql ManimNotes/ManimCourse.py AnotherScene -w
# The -p flag automatically opens the video when done.
# The -ql flag sets the quality to "low" for faster rendering.
# The -w flag suppresses the preview window (useful for some systems).


