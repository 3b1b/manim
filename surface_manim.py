from big_ol_pile_of_manim_imports import *
# from three_dimensions import Sphere


# class ColoringEquations(Scene):
# #Grouping and coloring parts of equations
#     def construct(self):
#         line1=TexMobject(r"\text{A subset}", r"S \in \mathbb{R}^3$", r" is a \text{regular surface}", 
#             r"if for any point in this set, there exist an open set", r"$V \subset \mathbb{R}^3$", r"\text{, such that,}", "$p \in V$")

#         line1.set_color_by_tex("regular", BLUE)
#         line2=TexMobject("m", "\\text{ and acceleration }", "\\vec{a}", ". ")
#         line2.set_color_by_tex_to_color_map({
#         "m": YELLOW,
#         "{a}": RED
#         })
#         sentence=VGroup(line1,line2)
#         sentence.arrange_submobjects(DOWN, buff=MED_LARGE_BUFF)
#         self.play(Write(sentence))
        
class Surface_Definition(Scene):
    """Compiled with manim (py2.7 commit may 9th)"""
    def construct(self):
        q1 = TextMobject(r"""A subset $S \in \mathbb{R}^3$ is a""", r"\textbf{regular surface} \\",
            r"if for any point in this set, there exist an open set" ,r"$V \subset \mathbb{R}^3$ \\",
            r"\textit{such that}, $p \in V$ and $\exists$ ",
            r"$\bar{X}: U \rightarrow V \cap S$\\",
            r"Where U is an",
            r"\textbf{open set}",
            r"of $\mathbb{R}^2$, and $\bar{X}$ is a ",
            r"\textbf{surjective mapping}")
        q1.set_color_by_tex("regular", BLUE)
        q1.set_color_by_tex(r"$V \subset", MAROON_E)
        q1.set_color_by_tex(r"$\bar{X}:", ORANGE)
        q1.set_color_by_tex(r"\textbf{open set}", PINK)
        q1.set_color_by_tex(r"\textbf{surjective mapping}", GOLD_C)
        # q2 = TextMobject(r"""""")

        bp1 = TexMobject(r"""  i) \text{$\bar{X}$ is $C^{\infty}$}"""); bp1.set_color_by_tex("", YELLOW)
        bp2 = TexMobject(r""" ii) \text{$\bar{X}$ is homeomorphism}"""); bp2.set_color_by_tex("", RED)
        bp3 = TexMobject(r"""iii) \text{$\forall$ q $\in I$, $d_2\bar{X}_q: \mathbb{R}^2 \rightarrow \mathbb{R}^3$ is injective}"""); bp3.set_color_by_tex("", TEAL_D)
        

        # q3 = TextMobject(def_part_2)
        self.play(ShowCreation(q1))
        self.wait(2)
        self.play(ApplyMethod(q1.shift,2.5*UP))
        self.wait(2)
        # q2.shift(1.5*UP)
        # self.play(ShowCreation(q2))
        self.play(ShowCreation(bp1))
        
        self.play(ApplyMethod(bp1.shift, 5*LEFT))
        
        self.play(ShowCreation(bp2))
        self.play(ApplyMethod(bp2.shift, 1*DOWN+3.5*LEFT))
        
        bp3.shift(1.2*RIGHT)
        self.play(ShowCreation(bp3))
        self.play(ApplyMethod(bp3.shift, 2*DOWN+3*LEFT))
        self.wait(2)

        # self.play(FadeIn(q2))
        # self.play(FadeIn(q3))

class Part1(Scene):
    def construct(self):
        q1 = TextMobject(r"""A subset $S \in \mathbb{R}^3$ is a""", r"\textbf{regular surface} \\",
            r"if for any point in this set, there exist an open set" ,r"$V \subset \mathbb{R}^3$ \\",
            r"\textit{such that}, $p \in V$ and $\exists$ ",
            r"$\bar{X}: U \rightarrow V \cap S$\\",
            r"Where U is an",
            r"\textbf{open set}",
            r"of $\mathbb{R}^2$, and $\bar{X}$ is a ",
            r"\textbf{surjective mapping}")
        q1.set_color_by_tex("regular", BLUE)
        q1.set_color_by_tex(r"$V \subset", MAROON_E)
        q1.set_color_by_tex(r"$\bar{X}:", ORANGE)
        q1.set_color_by_tex(r"\textbf{open set}", PINK)
        q1.set_color_by_tex(r"\textbf{surjective mapping}", GOLD_C)
        q1.shift(2.5*UP)
        circle = Circle(fill_color=GREEN_B, fill_opacity=1, color=GOLD_A)
        circle_exp = TextMobject(r"An open set in $\mathbb{R}^2$")
        self.add(q1)
        self.wait(1)
        self.play(Transform(q1, circle_exp))
        self.wait(4)
        circle.shift(3.5*LEFT)
        self.play(ShowCreation(circle))
        self.wait(3)

class Part2(ThreeDScene):
    CONFIG = {'fill_color': GREEN_B}
    def construct(self):
        # STEP 1
        # Build two cube in the 3D scene, one for around the origin,
        # the other shifted along the vector RIGHT + UP + OUT
        # axes = ThreeDAxes()
        cube_origin = Sphere(2, 0.1, opacity=.35)
        self.play(ShowCreation(cube_origin))

        phi, theta, distance = ThreeDCamera().get_spherical_coords()
        angle_factor = 0.9
        phi += 2 * np.pi / 4 * angle_factor
        theta += 3 * 2 * np.pi / 8
        self.set_camera_position(phi, theta, distance)
        theta += 2 * np.pi
        self.move_camera(phi, theta, distance,  run_time=5)

import math

class Donught(ThreeDScene):
    def construct(self):
        d = Torus(5, 2, 0.05)
        self.play(ShowCreation(d))
        phi, theta, distance = ThreeDCamera().get_spherical_coords()
        angle_factor = 0.9
        phi += 2 * np.pi / 4 * angle_factor
        theta += 3 * 2 * np.pi / 8
        self.set_camera_position(phi, theta, distance)
        theta += 2 * np.pi
        self.move_camera(phi, theta, distance,  run_time=5)

class Part3(ThreeDScene):
    CONFIG = {"plane_kwargs" : { "color" : RED_B },
              "point_charge_loc" : 0.5*RIGHT-1.5*UP,
    }
    def construct(self):
        plane = NumberPlane(**self.plane_kwargs)
        plane.main_lines.fade(.9)
        plane.add(plane.get_axis_labels())

        x = lambda a,b: math.sin(a)*math.cos(b)
        y = lambda a,b: math.cos(b)*math.sin(a)
        z = lambda a,b: a+b

        t = Parametric3D(x,y, z, -10,10, -10,10, 0.3) 
        self.play(ShowCreation(t))

        self.set_camera_position(0, -np.pi/2, center_x = 5, center_y = 5, center_z = 1)
        self.wait(1)
        self.move_camera(0.8*np.pi/2, -0.45*np.pi)
        self.play(ShowCreation(plane))
        # self.play(ShowCreation(field2D))
        self.wait()
        self.begin_ambient_camera_rotation()
        self.wait(6)
    
    def return_z(self, a):
        return a


# class 3DSphere(Scene):
#     def construct(self):
#         circle = Circle()        
#         circle.shift(3.5*LEFT)
#         self.play(ShowCreation(circle))
#         self.play(ShowCreation(TextMobject(circle_exp)))

#         closed_set = Circle(fill_color=GREEN_B)