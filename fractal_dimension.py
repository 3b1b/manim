#!/usr/bin/env python

from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from scene import Scene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *


class Britain(SVGMobject):
    CONFIG = {
        "file_name" : "Britain.svg",
        "stroke_width" : 0,
        "fill_color" : BLUE_D,
        "fill_opacity" : 1,
        "propogate_style_to_family" : True,
        "height" : 5,
        "mark_paths_closed" : True,
    }
    def __init__(self, **kwargs):
        SVGMobject.__init__(self, **kwargs)
        self.points = self[0].points
        self.submobjects = []
        self.scale_to_fit_height(self.height)
        self.center()

class KochTest(Scene):
    def construct(self):
        koch = KochCurve(order = 5, stroke_width = 2)

        self.play(ShowCreation(koch, run_time = 3))
        self.play(
            koch.scale, 3, koch.get_left(),
            koch.set_stroke, None, 4
        )
        self.dither()

class SierpinskiTest(Scene):
    def construct(self):
        sierp = Sierpinski(
            order = 5,
        )

        self.play(FadeIn(
            sierp, 
            run_time = 5,
            submobject_mode = "lagged_start",
        ))
        self.dither()
        # self.play(sierp.scale, 2, sierp.get_top())
        # self.dither(3)

class FractalCreation(Scene):
    CONFIG = {
        "fractal_class" : PentagonalFractal,
        "max_order" : 5,
        "path_arc" : np.pi/6,
        "submobject_mode" : "lagged_start"
    }
    def construct(self):
        fractal = self.fractal_class(order = 0)
        self.play(FadeIn(fractal))
        for order in range(1, self.max_order+1):
            new_fractal = self.fractal_class(order = order)
            self.play(Transform(
                fractal, new_fractal,
                path_arc = self.path_arc,
                submobject_mode = self.submobject_mode,
                run_time = 2
            ))
            self.dither()
        self.dither()

###################################


class ZoomInOnFractal(PiCreatureScene):
    CONFIG = {
        "fractal_order" : 6,
        "num_zooms" : 5,
        "fractal_class" : DiamondFractal,
        "index_to_replace" : 0,
    }
    def construct(self):
        morty = self.pi_creature

        fractal = self.fractal_class(order = self.fractal_order)
        fractal.show()

        fractal = self.introduce_fractal()
        self.change_mode("thinking")
        self.blink()
        self.zoom_in(fractal)


    def introduce_fractal(self):
        fractal = self.fractal_class(order = 0)
        self.play(FadeIn(fractal))
        for order in range(1, self.fractal_order+1):
            new_fractal = self.fractal_class(order = order)
            self.play(
                Transform(fractal, new_fractal, run_time = 2),
                self.pi_creature.change_mode, "hooray"
            )
        return fractal

    def zoom_in(self, fractal):
        grower = fractal[self.index_to_replace]
        grower_target = fractal.copy()

        for x in range(self.num_zooms):
            self.tweak_fractal_subpart(grower_target)
            grower_family = grower.family_members_with_points()
            everything = VGroup(*[
                submob
                for submob in fractal.family_members_with_points()
                if not submob.is_off_screen()
                if submob not in grower_family
            ])
            everything.generate_target()
            everything.target.shift(
                grower_target.get_center()-grower.get_center()
            )
            everything.target.scale(
                grower_target.get_height()/grower.get_height()
            )

            self.play(
                Transform(grower, grower_target),
                MoveToTarget(everything),
                self.pi_creature.change_mode, "thinking",
                run_time = 2
            )
            self.dither()
            grower_target = grower.copy()            
            grower = grower[self.index_to_replace]


    def tweak_fractal_subpart(self, subpart):
        subpart.rotate_in_place(np.pi/4)

class WhatAreFractals(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "But what \\emph{is} a fractal?",
            student_index = 2,
            width = 6
        )
        self.change_student_modes("thinking", "pondering", None)
        self.dither()

        name = TextMobject("Benoit Mandelbrot")
        name.to_corner(UP+LEFT)
        # picture = Rectangle(height = 4, width = 3)
        picture = ImageMobject("Mandelbrot")
        picture.scale_to_fit_height(4)
        picture.next_to(name, DOWN)
        self.play(
            Write(name, run_time = 2),
            FadeIn(picture),
            *[
                ApplyMethod(pi.look_at, name)
                for pi in self.get_everyone()
            ]
        )
        self.dither(2)
        question = TextMobject("Aren't they", "self-similar", "shapes?")
        question.highlight_by_tex("self-similar", YELLOW)
        self.student_says(question)
        self.play(self.get_teacher().change_mode, "happy")
        self.dither(2)

class IntroduceVonKochCurve(Scene):
    CONFIG = {
        "order" : 5,
        "stroke_width" : 3,
    }
    def construct(self):
        snowflake = self.get_snowflake()
        name = TextMobject("Von Koch Snowflake")
        name.to_edge(UP)

        self.play(ShowCreation(snowflake, run_time = 3))
        self.play(Write(name, run_time = 2))
        curve = self.isolate_one_curve(snowflake)
        self.dither()
        self.zoom_in_on(curve)

    def get_snowflake(self):
        triangle = RegularPolygon(n = 3, start_angle = np.pi/2)
        triangle.scale_to_fit_height(4)
        curves = VGroup(*[
            KochCurve(
                order = self.order,
                stroke_width = self.stroke_width
            )
            for x in range(3)
        ])
        for index, curve in enumerate(curves):
            width = curve.get_width()
            curve.move_to(
                (np.sqrt(3)/6)*width*UP, DOWN
            )
            curve.rotate(-index*2*np.pi/3)
        curves.gradient_highlight(BLUE, WHITE, BLUE)

        return curves

    def isolate_one_curve(self, snowflake):
        self.play(*[
            ApplyMethod(curve.shift, curve.get_center()/2)
            for curve in snowflake
        ])
        self.dither()
        self.play(
            snowflake.scale, 2.1,
            snowflake.next_to, UP, DOWN
        )
        self.remove(*snowflake[1:])
        return snowflake[0]

    def zoom_in_on(self, curve):
        larger_curve = KochCurve(order = self.order+1)
        larger_curve.replace(curve)
        larger_curve.scale(3, about_point = curve.get_corner(DOWN+LEFT))
        larger_curve.gradient_highlight(
            curve[0].get_color(),
            curve[-1].get_color(),
        )

        self.play(Transform(curve, larger_curve, run_time = 2))
        n_parts = len(curve.split())
        sub_portion = VGroup(*curve[:n_parts/4])
        self.play(
            sub_portion.highlight, YELLOW,
            rate_func = there_and_back
        )
        self.dither()

class IntroduceSierpinskiTriangle(PiCreatureScene):
    CONFIG = {
        "order" : 7,
    }
    def construct(self):
        sierp = Sierpinski(order = self.order)
        sierp.save_state()

        self.play(FadeIn(
            sierp, 
            run_time = 2,
            submobject_mode = "lagged_start" 
        ))
        self.dither()
        self.play(
            self.pi_creature.change_mode, "pondering",
            *[
                ApplyMethod(submob.shift, submob.get_center())
                for submob in sierp
            ]
        )
        self.dither()
        for submob in sierp:
            self.play(sierp.shift, -submob.get_center())
            self.dither()
        self.play(sierp.restore)
        self.change_mode("happy")
        self.dither()
        
class SelfSimilarFractalsAsSubset(Scene):
    CONFIG = {
        "fractal_width" : 1.5
    }
    def construct(self):
        self.add_self_similar_fractals()
        self.add_general_fractals()

    def add_self_similar_fractals(self):
        fractals = VGroup(
            DiamondFractal(order = 5),
            KochSnowFlake(order = 3),
            Sierpinski(order = 5),
        )
        for submob in fractals:
            submob.scale_to_fit_width(self.fractal_width)
        fractals.arrange_submobjects(RIGHT)
        fractals[-1].next_to(VGroup(*fractals[:-1]), DOWN)

        title = TextMobject("Self-similar fractals")
        title.next_to(fractals, UP)

        small_rect = Rectangle()
        small_rect.replace(VGroup(fractals, title), stretch = True)
        small_rect.scale_in_place(1.2)
        self.small_rect = small_rect

        group = VGroup(fractals, title, small_rect)
        group.to_corner(UP+LEFT, buff = 2*MED_BUFF)

        self.play(
            Write(title),
            ShowCreation(fractals),
            run_time = 3
        )
        self.play(ShowCreation(small_rect))
        self.dither()

    def add_general_fractals(self):
        big_rectangle = Rectangle(
            width = 2*SPACE_WIDTH - 2*MED_BUFF,
            height = 2*SPACE_HEIGHT - 2*MED_BUFF,
        )
        title = TextMobject("Fractals")
        title.scale(1.5)
        title.next_to(ORIGIN, RIGHT, buff = LARGE_BUFF)
        title.to_edge(UP, buff = 2*MED_BUFF)

        britain = Britain(
            fill_opacity = 0,
            stroke_width = 2,
            stroke_color = WHITE,
        )
        britain.next_to(self.small_rect, RIGHT)
        britain.shift(2*DOWN)

        randy = Randolph().flip().scale(1.4)
        randy.next_to(britain, buff = SMALL_BUFF)
        randy.generate_target()
        randy.target.change_mode("pleading")
        fractalify(randy.target, order = 2)

        self.play(
            ShowCreation(big_rectangle), 
            Write(title),
        )
        self.play(ShowCreation(britain), run_time = 5)
        self.play(
            britain.set_stroke, BLACK, 0,
            britain.set_fill, BLUE, 1,
        )
        self.play(FadeIn(randy))
        self.play(MoveToTarget(randy, run_time = 2))
        self.dither(2)

class ConstrastSmoothAndFractal(Scene):
    CONFIG = {
        "britain_zoom_point_proportion" : 0.4,
        "scale_factor" : 15,
    }
    def construct(self):
        v_line = Line(UP, DOWN).scale(SPACE_HEIGHT)
        smooth = TextMobject("Smooth")
        smooth.shift(SPACE_WIDTH*LEFT/2)
        fractal = TextMobject("Fractal")
        fractal.shift(SPACE_WIDTH*RIGHT/2)
        VGroup(smooth, fractal).to_edge(UP)
        background_rectangle = Rectangle(
            height = 2*SPACE_HEIGHT,
            width = SPACE_WIDTH,
        )
        background_rectangle.to_edge(RIGHT, buff = 0)
        background_rectangle.set_fill(BLACK, 1)
        background_rectangle.set_stroke(width = 0)
        self.add(v_line, background_rectangle, smooth, fractal)

        britain = Britain(
            fill_opacity = 0,
            stroke_width = 2,
            stroke_color = WHITE,
        )[0]
        anchors = britain.get_anchors()
        smooth_britain = VMobject()
        smooth_britain.set_points_smoothly(anchors[::10])
        smooth_britain.center().shift(SPACE_WIDTH*LEFT/2)
        index = np.argmax(smooth_britain.get_anchors()[:,0])
        smooth_britain.zoom_point = smooth_britain.point_from_proportion(
            self.britain_zoom_point_proportion
        )

        britain.shift(SPACE_WIDTH*RIGHT/2)
        britain.zoom_point = britain.point_from_proportion(
            self.britain_zoom_point_proportion
        )
        fractalify(britain, order = 2, dimension = 1.21)

        britains = VGroup(britain, smooth_britain)
        self.play(*[
            ShowCreation(mob, run_time = 3)
            for mob in britains
        ])
        self.play(
            britains.set_fill, BLUE, 1,
            britains.set_stroke, None, 0,
        )
        self.dither()
        self.play(
            ApplyMethod(
                smooth_britain.scale, 
                self.scale_factor, 
                smooth_britain.zoom_point
            ),
            Animation(v_line),
            Animation(background_rectangle),
            ApplyMethod(
                britain.scale, 
                self.scale_factor, 
                britain.zoom_point
            ),
            Animation(smooth),
            Animation(fractal),
            run_time = 5
        )
        self.dither(2)
        
class ShowIdealizations(Scene):
    def construct(self):
        arrow = DoubleArrow(SPACE_WIDTH*LEFT, SPACE_WIDTH*RIGHT)
        arrow.shift(DOWN)
        left_words = TextMobject("Idealization \\\\ as smooth")
        middle_words = TextMobject("Nature")
        right_words = TextMobject("""
            Idealization 
            as perfectly 
            self-similar
        """)
        for words in left_words, middle_words, right_words:
            words.scale(0.8)
            words.next_to(arrow, DOWN)
        left_words.to_edge(LEFT)
        right_words.to_edge(RIGHT)
        self.add(arrow, left_words, middle_words, right_words)

        britain = Britain()[0]
        britain.scale_to_fit_height(4)
        britain.next_to(arrow, UP)

        anchors = britain.get_anchors()
        smooth_britain = VMobject()
        smooth_britain.set_points_smoothly(anchors[::10])
        smooth_britain.set_stroke(width = 0)
        smooth_britain.set_fill(BLUE_D, opacity = 1)
        smooth_britain.next_to(arrow, UP)
        smooth_britain.to_edge(LEFT)

        koch_snowflake = KochSnowFlake(order = 5, monochromatic = True)
        koch_snowflake.set_stroke(width = 0)
        koch_snowflake.set_fill(BLUE_D, opacity = 1)
        koch_snowflake.scale_to_fit_height(3)
        koch_snowflake.rotate(2*np.pi/3)
        koch_snowflake.next_to(arrow, UP)
        koch_snowflake.to_edge(RIGHT)

        VGroup(smooth_britain, britain, koch_snowflake).gradient_highlight(
            BLUE_B, BLUE_D
        )

        self.play(FadeIn(britain))
        self.dither()
        self.play(Transform(britain.copy(), smooth_britain))
        self.dither()
        self.play(Transform(britain.copy(), koch_snowflake))
        self.dither()
        self.dither(2)

class SayFractalDimension(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("Fractal dimension")
        self.change_student_modes("confused", "hesitant", "pondering")
        self.dither(3)

class ExamplesOfDimension(Scene):
    def construct(self):
        labels = VGroup(*[
            TextMobject("%s-dimensional"%s)
            for s in "1.585", "1.262", "1.21"
        ])
        fractals = VGroup(*[
            Sierpinski(order = 7),
            KochSnowFlake(order = 5),
            Britain(stroke_width = 2, fill_opacity = 0)
        ])
        for fractal, vect in zip(fractals, [LEFT, ORIGIN, RIGHT]):
            fractal.to_edge(vect)
        fractals[2].shift(0.5*UP)
        fractals[1].shift(0.5*RIGHT)
        for fractal, label, vect in zip(fractals, labels, [DOWN, UP, DOWN]):
            label.next_to(fractal, vect)
            label.shift_onto_screen()
            self.play(
                ShowCreation(fractal),
                Write(label),
                run_time = 3
            )
            self.dither()
        self.dither()

class DimensionForNaturalNumbers(Scene):
    def construct(self):
        labels = VGroup(*[
            TextMobject("%d-dimensional"%d)
            for d in 1, 2, 3
        ])
        for label, vect in zip(labels, [LEFT, ORIGIN, RIGHT]):
            label.to_edge(vect)
        labels.shift(2*DOWN)

        line = Line(DOWN+LEFT, 3*UP+RIGHT, color = BLUE)
        line.next_to(labels[0], UP)

        self.play(
            Write(labels[0]),
            ShowCreation(line)
        )
        self.dither()
        for label in labels[1:]:
            self.play(Write(label))
            self.dither()

class Show2DPlanein3D(Scene):
    def construct(self):
        pass

class ShowCubeIn3D(Scene):
    def construct(self):
        pass

class OfCourseItsMadeUp(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            Fractal dimension
            \\emph{is} a made up concept...
        """)
        self.change_student_modes(*["hesitant"]*3)
        self.dither(2)
        self.teacher_says(
            """But it's useful!""",
            target_mode = "hooray"
        )

class FourSelfSimilarShapes(Scene):
    CONFIG = {
        "shape_width" : 2,
        "sierpinski_order" : 6,
    }
    def construct(self):
        titles = self.get_titles()
        shapes = self.get_shapes(titles)

        self.introduce_shapes(titles, shapes)
        self.show_self_similarity(shapes)
        self.mention_measurements()

    def get_titles(self):
        titles = VGroup(*map(TextMobject, [
            "Line", "Square", "Cube", "Sierpinski"
        ]))
        for title, x in zip(titles, np.linspace(-0.75, 0.75, 4)):
            title.shift(x*SPACE_WIDTH*RIGHT)
        titles.to_edge(UP)
        return titles

    def get_shapes(self, titles):
        line = VGroup(
            Line(LEFT, ORIGIN),
            Line(ORIGIN, RIGHT)
        )
        line.highlight(BLUE_C)

        square = VGroup(*[
            Square().next_to(ORIGIN, vect, buff = 0)
            for vect in compass_directions(start_vect = DOWN+LEFT)
        ])
        square.set_stroke(width = 0)
        square.set_fill(BLUE, 0.7)

        cube = TextMobject("TODO")
        cube.set_fill(opacity = 0)

        sierpinski = Sierpinski(order = self.sierpinski_order)

        shapes = VGroup(line, square, cube, sierpinski)
        for shape, title in zip(shapes, titles):
            shape.scale_to_fit_width(self.shape_width)
            shape.next_to(title, DOWN, buff = MED_BUFF)
        line.shift(DOWN)

        return shapes

    def introduce_shapes(self, titles, shapes):
        line, square, cube, sierpinski = shapes

        brace = Brace(VGroup(*shapes[:3]), DOWN)
        brace_text = brace.get_text("Not fractals")

        self.play(ShowCreation(line))
        self.play(GrowFromCenter(square))
        self.play(FadeIn(cube))
        self.play(ShowCreation(sierpinski))
        self.dither()
        self.play(
            GrowFromCenter(brace),
            FadeIn(brace_text)
        )
        self.dither()
        self.play(*map(FadeOut, [brace, brace_text]))
        self.dither()

        for title in titles:
            self.play(Write(title, run_time = 1))
        self.dither(2)

    def show_self_similarity(self, shapes):
        shapes_copy = shapes.copy()
        self.shapes_copy = shapes_copy
        line, square, cube, sierpinski = shapes_copy

        def break_up(mobject, factor = 1.3):
            mobject.scale_in_place(factor)
            for submob in mobject:
                submob.scale_in_place(1./factor)
            return mobject

        self.play(line.shift, 3*DOWN)
        self.play(ApplyFunction(break_up, line))
        self.dither()        
        brace = Brace(line[0], DOWN)
        brace_text = brace.get_text("1/2")
        self.play(
            GrowFromCenter(brace), 
            Write(brace_text)
        )
        brace.add(brace_text)
        self.dither()

        self.play(square.next_to, square, DOWN, LARGE_BUFF)
        self.play(ApplyFunction(break_up, square))
        subsquare = square[0]
        subsquare.save_state()
        self.play(subsquare.replace, shapes[1])
        self.dither()
        self.play(subsquare.restore)
        self.play(brace.next_to, subsquare, DOWN)
        self.dither()

        self.dither(5)#Handle cube

        self.play(sierpinski.next_to, sierpinski, DOWN, LARGE_BUFF)
        self.play(ApplyFunction(break_up, sierpinski))
        self.dither()
        self.play(brace.next_to, sierpinski[0], DOWN)
        self.dither(2)
        self.play(FadeOut(brace))

    def mention_measurements(self):
        line, square, cube, sierpinski = self.shapes_copy

        labels = map(TextMobject, [
            "$1/2$ length", 
            "$1/4$ area", 
            "$1/8$ volume",
            "You'll see...",
        ])
        for label, shape in zip(labels, self.shapes_copy):
            label.next_to(shape, DOWN)
            label.to_edge(DOWN, buff = 2*MED_BUFF)
            if label is labels[-1]:
                label.shift(0.1*UP) #Dumb

            self.play(
                Write(label, run_time = 1),
                shape[0].highlight, YELLOW
            )
            self.dither()

class BreakUpCubeIn3D(Scene):
    def construct(self):
        pass

class BrokenUpCubeIn3D(Scene):
    def construct(self):
        pass

class GeneralWordForMeasurement(Scene):
    def construct(self):
        measure = TextMobject("``Measure''")
        measure.to_edge(UP)
        mass = TextMobject("Mass")
        mass.move_to(measure)

        words = VGroup(*map(TextMobject, [
            "Length", "Area", "Volume"
        ]))
        words.arrange_submobjects(RIGHT, buff = 2*LARGE_BUFF)
        words.next_to(measure, DOWN, buff = 2*LARGE_BUFF)
        colors = color_gradient([BLUE_B, BLUE_D], len(words))
        for word, color in zip(words, colors):
            word.highlight(color)
        lines = VGroup(*[
            Line(
                measure.get_bottom(), word.get_top(), 
                color = word.get_color(),
                buff = MED_BUFF
            )
            for word in words
        ])

        for word in words:
            self.play(FadeIn(word))
        self.play(ShowCreation(lines, run_time = 2))
        self.dither()
        self.play(Write(measure))
        self.dither(2)
        self.play(Transform(measure, mass))
        self.dither(2)

class ImagineShapesAsMetal(FourSelfSimilarShapes):
    def construct(self):
        titles = VGroup(*map(VGroup, self.get_titles()))
        shapes = self.get_shapes(titles)
        shapes.shift(DOWN)
        descriptions = VGroup(*[
            TextMobject(*words, arg_separator = "\\\\")
            for shape, words in zip(shapes, [
                ["Thin", "wire"], 
                ["Flat", "sheet"], 
                ["Solid", "cube"],
                ["Sierpinski", "mesh"]
            ])
        ])
        for title, description in zip(titles, descriptions):
            description.move_to(title, UP)
            title.target = description

        self.add(titles, shapes)
        for shape in shapes:
            shape.generate_target()
            shape.target.highlight(LIGHT_GREY)
        shapes[-1].target.gradient_highlight(GREY, WHITE)
        for shape, title in zip(shapes, titles):
            self.play(
                MoveToTarget(title),
                MoveToTarget(shape)
            )
            self.dither()
        self.dither()

        for shape in shapes:
            self.play(
                shape.scale, 0.5, shape.get_top(),
                run_time = 3,
                rate_func = there_and_back
            )
        self.dither()

class ScaledLineMass(Scene):
    CONFIG = {
        "title" : "Line",
        "mass_scaling_factor" : "\\frac{1}{2}",
        "shape_width" : 2,
        "break_up_factor" : 1.3,
        "vert_distance" : 2,
        "brace_direction" : DOWN,
        "shape_to_shape_buff" : 2*LARGE_BUFF,
    }
    def construct(self):
        title = TextMobject(self.title)
        title.to_edge(UP)
        scaling_factor_label = TextMobject(
            "Scaling factor:", "$\\frac{1}{2}$"
        )
        scaling_factor_label[1].highlight(YELLOW)
        scaling_factor_label.to_edge(LEFT).shift(UP)
        mass_scaling_label = TextMobject(
            "Mass scaling factor:", "$%s$"%self.mass_scaling_factor
        )
        mass_scaling_label[1].highlight(GREEN)
        mass_scaling_label.next_to(
            scaling_factor_label, DOWN, 
            aligned_edge = LEFT,
            buff = LARGE_BUFF
        )

        shape = self.get_shape()
        shape.scale_to_fit_width(self.shape_width)
        shape.center()
        shape.shift(SPACE_WIDTH*RIGHT/2 + self.vert_distance*UP)

        big_brace = Brace(shape, self.brace_direction)
        big_brace_text = big_brace.get_text("$1$")

        shape_copy = shape.copy()
        shape_copy.next_to(shape, DOWN, buff = self.shape_to_shape_buff)
        shape_copy.scale_in_place(self.break_up_factor)
        for submob in shape_copy:
            submob.scale_in_place(1./self.break_up_factor)

        little_brace = Brace(shape_copy[0], self.brace_direction)
        little_brace_text = little_brace.get_text("$\\frac{1}{2}$")

        self.add(title, scaling_factor_label, mass_scaling_label[0])
        self.play(GrowFromCenter(shape))
        self.play(
            GrowFromCenter(big_brace),
            Write(big_brace_text)
        )
        self.dither()

        self.play(
            shape.copy().replace, shape_copy[0]
        )
        self.remove(*self.get_mobjects_from_last_animation())
        self.add(shape_copy[0])
        self.play(
            GrowFromCenter(little_brace),
            Write(little_brace_text)
        )
        self.dither()

        self.play(Write(mass_scaling_label[1], run_time = 1))
        self.dither()
        self.play(FadeIn(
            VGroup(*shape_copy[1:]),
            submobject_mode = "lagged_start"
        ))
        self.dither()
        self.play(Transform(
            shape_copy.copy(), shape
        ))
        self.dither()

    def get_shape(self):
        return VGroup(
            Line(LEFT, ORIGIN),
            Line(ORIGIN, RIGHT)
        ).highlight(BLUE)

class ScaledSquareMass(ScaledLineMass):
    CONFIG = {
        "title" : "Square",
        "mass_scaling_factor" : "\\frac{1}{4} = \\left( \\frac{1}{2} \\right)^2",
        "brace_direction" : LEFT,
    }
    def get_shape(self):
        return VGroup(*[
            Square(
                stroke_width = 0, 
                fill_color =  BLUE,
                fill_opacity = 0.7
            ).shift(vect)
            for vect in compass_directions(start_vect = DOWN+LEFT)
        ])

class ScaledCubeMass(ScaledLineMass):
    CONFIG = {
        "title" : "Cube",
        "mass_scaling_factor" : "\\frac{1}{8} = \\left( \\frac{1}{2} \\right)^3",
    }
    def get_shape(self):
        return TextMobject("TODO").set_fill(opacity = 0)

class FormCubeFromSubcubesIn3D(Scene):
    def construct(self):
        pass

class ScaledSierpinskiMass(ScaledLineMass):
    CONFIG = {
        "title" : "Sierpinski",
        "mass_scaling_factor" : "\\frac{1}{3}",
        "vert_distance" : 2.5,
        "shape_to_shape_buff" : 1.5*LARGE_BUFF,
    }
    def get_shape(self):
        return Sierpinski(order = 6)

class DefineTwoDimensional(PiCreatureScene):
    CONFIG = {
        "dimension" : "2",
        "length_color" : GREEN,
        "dimension_color" : YELLOW,
        "shape_width" : 2,
        "scale_factor" : 1.5,
    }
    def construct(self):
        self.add_title()
        self.add_h_line()
        self.add_shape()
        self.add_width_mass_labels()
        self.show_top_length()
        self.change_mode("thinking")
        self.perform_scaling()
        self.show_dimension()

    def add_title(self):
        title = TextMobject(
            self.dimension, "-dimensional",
            arg_separator = ""
        )
        self.dimension_in_title = title[0]
        self.dimension_in_title.highlight(self.dimension_color)
        title.to_edge(UP)
        self.add(title)

        self.title = title

    def add_h_line(self):
        self.h_line = Line(LEFT, RIGHT).scale(SPACE_WIDTH)
        self.add(self.h_line)

    def add_shape(self):
        shape = self.get_shape()
        shape.scale_to_fit_width(self.shape_width)
        shape.next_to(self.title, DOWN, buff = 2*MED_BUFF)
        # self.shape.shift(SPACE_HEIGHT*UP/2)
        self.mass_color = shape.get_color()
        self.add(shape)

        self.shape = shape

    def add_width_mass_labels(self):
        top_length = TextMobject("Length:", "$L$")
        top_mass = TextMobject("Mass:", "$M$")
        bottom_length = TextMobject(
            "Length: ", "$s$", "$L$", 
            arg_separator = ""
        )
        bottom_mass = TextMobject(
            "Mass: ", "$s^%s$"%self.dimension, "$M$", 
            arg_separator = ""
        )
        self.dimension_in_exp = VGroup(
            *bottom_mass[1][-len(self.dimension):]
        )
        self.dimension_in_exp.highlight(self.dimension_color)

        top_group = VGroup(top_length, top_mass)
        bottom_group = VGroup(bottom_length, bottom_mass)
        for group in top_group, bottom_group:
            group.arrange_submobjects(
                DOWN, 
                buff = 2*MED_BUFF,
                aligned_edge = LEFT
            )
            group[0][-1].highlight(self.length_color)
            group[1][-1].highlight(self.mass_color)

        top_group.next_to(self.h_line, UP, buff = LARGE_BUFF)
        bottom_group.next_to(self.h_line, DOWN, buff = LARGE_BUFF)
        for group in top_group, bottom_group:
            group.to_edge(LEFT)

        self.add(top_group, bottom_group)

        self.top_L = top_length[-1]
        self.bottom_L = VGroup(*bottom_length[-2:])

    def show_top_length(self):
        brace = Brace(self.shape, LEFT)
        top_L = self.top_L.copy()

        self.play(GrowFromCenter(brace))
        self.play(top_L.next_to, brace, LEFT)
        self.dither()

        self.brace = brace

    def perform_scaling(self):
        group = VGroup(self.shape, self.brace).copy()
        self.play(group.shift, (group.get_top()[1]+MED_BUFF)*DOWN)

        shape, brace = group
        bottom_L = self.bottom_L.copy()        
        shape.generate_target()
        shape.target.scale(
            self.scale_factor, 
            about_point = shape.get_corner(UP+LEFT)
        )
        brace.target = Brace(shape.target, LEFT)
        self.play(*map(MoveToTarget, group))
        self.play(bottom_L.next_to, brace, LEFT)
        self.dither()

    def show_dimension(self):
        top_dimension = self.dimension_in_title.copy()
        self.play(self.pi_creature.look_at, top_dimension)
        self.play(
            top_dimension.replace, 
            self.dimension_in_exp,
            run_time = 2,
        )
        self.dither(3)

    def get_shape(self):
        return Square(
            stroke_width = 0,
            fill_color = BLUE,
            fill_opacity = 0.7,
        )
























