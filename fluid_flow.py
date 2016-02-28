from mobject import Mobject
from mobject.image_mobject import MobjectFromRegion
from mobject.tex_mobject import TextMobject
from mobject.region import  region_from_polygon_vertices
from topics.geometry import Arrow, Dot, Circle, Line, FilledRectangle
from topics.number_line import NumberPlane, XYZAxes
from topics.three_dimensions import Sphere
from scene import Scene
from animation.simple_animations import \
    ShowCreation, Rotating, PhaseFlow, ApplyToCenters
from animation.transform import \
    Transform, ApplyMethod, FadeOut, ApplyFunction

from helpers import *


class FluidFlow(Scene):
    CONFIG = {
        "arrow_spacing" : 1,
        "dot_spacing" : 0.5,
        "dot_color" : BLUE_C,
        "text_color" : WHITE,
        "arrow_color" : GREEN_A,
        "points_height" : SPACE_HEIGHT,
        "points_width" : SPACE_WIDTH,
    }
    def use_function(self, function):
        self.function = function

    def get_points(self, spacing):
        x_radius, y_radius = [
            val-val%spacing
            for val in self.points_width, self.points_height
        ]
        return map(np.array, it.product(
            np.arange(-x_radius, x_radius+spacing, spacing),
            np.arange(-y_radius, y_radius+spacing, spacing),
            [0]
        ))


    def add_plane(self):
        self.add(NumberPlane().fade())

    def add_dots(self):
        points = self.get_points(self.dot_spacing)
        self.dots = Mobject(*map(Dot, points))
        self.dots.highlight(self.dot_color)
        self.play(ShowCreation(self.dots))
        self.dither()

    def add_arrows(self, true_length = False):
        if not hasattr(self, "function"):
            raise Exception("Must run use_function first")
        points = self.get_points(self.arrow_spacing)
        points = filter(
            lambda p : np.linalg.norm(self.function(p)) > 0.01,
            points
        )
        angles = map(angle_of_vector, map(self.function, points))
        prototype = Arrow(
            ORIGIN, RIGHT*self.arrow_spacing/2.,
            color = self.arrow_color, 
            tip_length = 0.1,
            buff = 0
        )
        arrows = []
        for point in points:
            arrow = prototype.copy()
            output = self.function(point)
            if true_length:
                arrow.scale(np.linalg.norm(output))
            arrow.rotate(angle_of_vector(output))
            arrow.shift(point)
            arrows.append(arrow)
        self.arrows = Mobject(*arrows)

        self.play(ShowCreation(self.arrows))
        self.dither()

    def add_paddle(self):
        pass

    def flow(self, **kwargs):
        if not hasattr(self, "function"):
            raise Exception("Must run use_function first")
        self.play(ApplyToCenters(
            PhaseFlow,
            self.dots.split(),
            function = self.function,
            **kwargs
        ))

    def label(self, text, time = 5):
        mob = TextMobject(text)
        mob.scale(1.5)
        mob.to_edge(UP)
        rectangle = region_from_polygon_vertices(*[
            mob.get_corner(vect) + 0.3*vect
            for vect in [
                UP+RIGHT,
                UP+LEFT,
                DOWN+LEFT,
                DOWN+RIGHT
            ]
        ])
        mob.highlight(self.text_color)
        rectangle = MobjectFromRegion(rectangle, "#111111")
        rectangle.point_thickness = 3
        self.add(rectangle, mob)
        self.dither(time)
        self.remove(mob, rectangle)



class NegativeDivergenceExamlpe(FluidFlow):
    CONFIG = {
        "points_width" : 2*SPACE_WIDTH,
        "points_height" : 2*SPACE_HEIGHT,
    }
    def construct(self):
        circle = Circle(color = YELLOW_C)
        self.use_function(
            lambda p : -p/(2*np.linalg.norm(0.5*p)**0.5+0.01)
        )
        self.add_plane()
        self.add(circle)
        self.add_arrows()
        self.add_dots()        
        self.flow(run_time = 2, virtual_time = 2)
        self.dither(2)


class PositiveDivergenceExample(FluidFlow):
    def construct(self):
        circle = Circle(color = YELLOW_C)
        self.use_function(
            lambda p : p/(2*np.linalg.norm(0.5*p)**0.5+0.01)
        )
        self.add_plane()
        self.add(circle)
        self.add_arrows()  
        self.add_dots()        
        self.flow(run_time = 2, virtual_time = 2)
        self.dither(2)

class DivergenceArticleExample(FluidFlow):
    def construct(self):
        def raw_function((x, y, z)):
            return (2*x-y, y*y, 0)
        def normalized_function(p):
            result = raw_function(p)
            return result/(np.linalg.norm(result)+0.01)
        self.use_function(normalized_function)

        self.add_plane()
        self.add_arrows()
        self.add_dots()
        self.flow(
            virtual_time = 4,
            run_time = 5
        )

class QuadraticField(FluidFlow):
    def construct(self):
        self.use_function(
            lambda (x, y, z) : 0.25*((x*x-y*y)*RIGHT+x*y*UP)
        )
        self.add_plane()
        self.add_arrows()
        self.add_dots()
        self.flow(
            virtual_time = 10,
            run_time = 20,
            rate_func = None
        )


class IncompressibleFluid(FluidFlow):
    CONFIG = {
        "points_width" : 2*SPACE_WIDTH,
        "points_height" : 1.4*SPACE_HEIGHT
    }
    def construct(self):
        self.use_function(
            lambda (x, y, z) : RIGHT+np.sin(x)*UP
        )
        self.add_plane()
        self.add_arrows()
        self.add_dots()
        for x in range(8):
            self.flow(
                run_time = 1,
                rate_func = None,
            )



class ConstantInwardFlow(FluidFlow):
    CONFIG = {
        "points_height" : 3*SPACE_HEIGHT,
        "points_width" : 3*SPACE_WIDTH,
    }
    def construct(self):
        self.use_function(
            lambda p : -3*p/(np.linalg.norm(p)+0.1)
        )
        self.add_plane()
        self.add_arrows()
        self.add_dots()
        for x in range(4):
            self.flow(
                run_time = 5,
                rate_func = None,
            )




class ConstantOutwardFlow(FluidFlow):
    def construct(self):
        self.use_function(
            lambda p : p/(2*np.linalg.norm(0.5*p)**0.5+0.01)
        )
        self.add_plane()
        self.add_arrows()
        self.add_dots()
        for x in range(4):
            self.flow(rate_func = None)
            dot = self.dots.split()[0].copy()
            dot.center()
            new_dots = [
                dot.copy().shift(0.5*vect)
                for vect in [
                    UP, DOWN, LEFT, RIGHT, 
                    UP+RIGHT, UP+LEFT, DOWN+RIGHT, DOWN+LEFT
                ]
            ]
            self.dots.add(*new_dots)


class ConstantPositiveCurl(FluidFlow):
    CONFIG = {
        "points_height" : SPACE_WIDTH,
    }
    def construct(self):
        self.use_function(
            lambda p : 0.5*(-p[1]*RIGHT+p[0]*UP)
        )
        self.add_plane()
        self.add_arrows(true_length = True)
        self.add_dots()
        for x in range(10):
            self.flow(
                rate_func = None
            )



class ComplexCurlExample(FluidFlow):
    def construct(self):
        self.use_function(
            lambda (x, y, z) : np.cos(x+y)*RIGHT+np.sin(x*y)*UP
        )
        self.add_plane()
        self.add_arrows(true_length = True)
        self.add_dots()
        for x in range(4):
            self.flow(
                run_time = 5,
                rate_func = None,
            )

class SingleSwirl(FluidFlow):
    CONFIG = {
        "points_height" : SPACE_WIDTH,
    }
    def construct(self):
        self.use_function(
            lambda p : (-p[1]*RIGHT+p[0]*UP)/np.linalg.norm(p)
        )
        self.add_plane()
        self.add_arrows()
        self.add_dots()
        for x in range(10):
            self.flow(rate_func = None)


class CurlArticleExample(FluidFlow):
    CONFIG = {
        "points_height" : 3*SPACE_HEIGHT,
        "points_width" : 3*SPACE_WIDTH
    }
    def construct(self):
        self.use_function(
            lambda (x, y, z) : np.cos(0.5*(x+y))*RIGHT + np.sin(0.25*x*y)*UP
        )
        circle = Circle().shift(3*UP)
        self.add_plane()
        self.add_arrows()
        self.play(ShowCreation(circle))
        self.add_dots()
        self.show_frame()
        self.flow(
            rate_func = None,
            run_time = 15,
            virtual_time = 10
        )


class FourSwirlsWithoutCircles(FluidFlow):
    CONFIG = {
        "points_height" : SPACE_WIDTH,
    }
    def construct(self):
        circles = [
            Circle().shift(3*vect)
            for vect in compass_directions()
        ]
        self.use_function(
            lambda (x, y, z) : 0.5*(y**3-9*y)*RIGHT+(x**3-9*x)*UP
        )
        self.add_plane()
        self.add_arrows()
        # for circle in circles:
        #     self.play(ShowCreation(circle))
        self.add_dots()
        self.add_extra_dots()
        self.flow(
            virtual_time = 4,
            run_time = 20,
            rate_func = None
        )

    def add_extra_dots(self):
        dots = self.dots.split()
        for vect in UP+LEFT, DOWN+RIGHT:
            for n in range(5, 15):
                dots.append(
                    dots[0].copy().center().shift(n*vect)
                )
        self.dots = Mobject(*dots)


class CopyPlane(Scene):
    def construct(self):
        def special_rotate(mob):
            mob.rotate(0.9*np.pi/2, RIGHT)
            mob.rotate(-np.pi/4, UP)
            return mob
        plane = NumberPlane()
        copies = [
            special_rotate(plane.copy().shift(u*n*OUT))
            for n in range(1, 3)
            for u in -1, 1
        ]
        line = Line(4*IN, 4*OUT)


        self.add(plane)
        self.play(*[
            ApplyFunction(special_rotate, mob, run_time = 3)
            for mob in plane, line
        ])
        self.dither()
        for copy in copies:
            self.play(Transform(plane.copy(), copy))
        self.dither()


class Test3DMovement(Scene):
    def construct(self):
        axes = XYZAxes()
        axes.highlight(WHITE)
        plane = NumberPlane()
        vects = [
            Arrow(point, point+(3./27)*(3*x**2-3*y**2)*OUT, color = MAROON_D)
            for x in range(-4, 5, 2)
            for y in range(-5, 5, 2)
            for point in [x*RIGHT + y*UP]
        ]
        everybody = Mobject(axes, plane, *vects)

        self.play(ApplyMethod(
            everybody.rotate, 0.9*np.pi/2, RIGHT
        ))
        self.dither()
        self.play(ApplyMethod(
            everybody.rotate,
            np.pi/2,
            run_time = 5
        ))



class DropletFlow(FluidFlow):
    def construct(self):
        seconds = 20
        droplets = Mobject(*[
            Dot(x*RIGHT+y*UP, color = BLUE_D)
            for x in range(-7, 9)
            for y in range(-3, 4)
        ])
        self.use_function(
            lambda (x, y, z) : 0.5*(y**3-9*y)*RIGHT+(x**3-9*x)*UP,
        )
        self.add_arrows()
        self.play(ShowCreation(droplets))
        for x in range(seconds):
            self.play(PhaseFlow(
                self.function,    
                droplets,
                virtual_time = 1./10,
                rate_func = None,
            ))
            droplets.add(*[
                Dot(5*vect, color = BLUE_D)
                for vect in UP+LEFT, DOWN+RIGHT
            ])

class AltDropletFlow(FluidFlow):
    def construct(self):
        self.use_function(lambda (x, y, z):
            (np.sin(x)+np.sin(y))*RIGHT+\
            (np.sin(x)-np.sin(y))*UP
        )
        self.add_dots()
        self.flow(
            rate_func = None,
            run_time = 10,
            virtual_time = 2
        )













