
from manimlib.imports import *
from functools import reduce

def break_up(mobject, factor = 1.3):
    mobject.scale_in_place(factor)
    for submob in mobject:
        submob.scale_in_place(1./factor)
    return mobject

class Britain(SVGMobject):
    CONFIG = {
        "file_name" : "Britain.svg",
        "stroke_width" : 0,
        "fill_color" : BLUE_D,
        "fill_opacity" : 1,
        "height" : 5,
        "mark_paths_closed" : True,
    }
    def __init__(self, **kwargs):
        SVGMobject.__init__(self, **kwargs)
        self.points = self[0].points
        self.submobjects = []
        self.set_height(self.height)
        self.center()

class Norway(Britain):
    CONFIG = {
        "file_name" : "Norway",
        "mark_paths_closed" : False
    }

class KochTest(Scene):
    def construct(self):
        koch = KochCurve(order = 5, stroke_width = 2)

        self.play(ShowCreation(koch, run_time = 3))
        self.play(
            koch.scale, 3, koch.get_left(),
            koch.set_stroke, None, 4
        )
        self.wait()

class SierpinskiTest(Scene):
    def construct(self):
        sierp = Sierpinski(
            order = 5,
        )

        self.play(FadeIn(
            sierp,
            run_time = 5,
            lag_ratio = 0.5,
        ))
        self.wait()
        # self.play(sierp.scale, 2, sierp.get_top())
        # self.wait(3)




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
            self.wait()
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
        self.wait()

        name = TextMobject("Benoit Mandelbrot")
        name.to_corner(UP+LEFT)
        # picture = Rectangle(height = 4, width = 3)
        picture = ImageMobject("Mandelbrot")
        picture.set_height(4)
        picture.next_to(name, DOWN)
        self.play(
            Write(name, run_time = 2),
            FadeIn(picture),
            *[
                ApplyMethod(pi.look_at, name)
                for pi in self.get_pi_creatures()
            ]
        )
        self.wait(2)
        question = TextMobject("Aren't they", "self-similar", "shapes?")
        question.set_color_by_tex("self-similar", YELLOW)
        self.student_says(question)
        self.play(self.get_teacher().change_mode, "happy")
        self.wait(2)

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
        self.wait()

        self.zoom_in_on(curve)
        self.zoom_in_on(curve)
        self.zoom_in_on(curve)

    def get_snowflake(self):
        triangle = RegularPolygon(n = 3, start_angle = np.pi/2)
        triangle.set_height(4)
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
        curves.set_color_by_gradient(BLUE, WHITE, BLUE)

        return curves

    def isolate_one_curve(self, snowflake):
        self.play(*[
            ApplyMethod(curve.shift, curve.get_center()/2)
            for curve in snowflake
        ])
        self.wait()
        self.play(
            snowflake.scale, 2.1,
            snowflake.next_to, UP, DOWN
        )
        self.remove(*snowflake[1:])
        return snowflake[0]

    def zoom_in_on(self, curve):
        larger_curve = KochCurve(
            order = self.order+1,
            stroke_width = self.stroke_width
        )
        larger_curve.replace(curve)
        larger_curve.scale(3, about_point = curve.get_corner(DOWN+LEFT))
        larger_curve.set_color_by_gradient(
            curve[0].get_color(),
            curve[-1].get_color(),
        )

        self.play(Transform(curve, larger_curve, run_time = 2))
        n_parts = len(curve.split())
        sub_portion = VGroup(*curve[:n_parts/4])
        self.play(
            sub_portion.set_color, YELLOW,
            rate_func = there_and_back
        )
        self.wait()

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
            lag_ratio = 0.5
        ))
        self.wait()
        self.play(
            self.pi_creature.change_mode, "pondering",
            *[
                ApplyMethod(submob.shift, submob.get_center())
                for submob in sierp
            ]
        )
        self.wait()
        for submob in sierp:
            self.play(sierp.shift, -submob.get_center())
            self.wait()
        self.play(sierp.restore)
        self.change_mode("happy")
        self.wait()

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
            submob.set_width(self.fractal_width)
        fractals.arrange(RIGHT)
        fractals[-1].next_to(VGroup(*fractals[:-1]), DOWN)

        title = TextMobject("Self-similar fractals")
        title.next_to(fractals, UP)

        small_rect = Rectangle()
        small_rect.replace(VGroup(fractals, title), stretch = True)
        small_rect.scale_in_place(1.2)
        self.small_rect = small_rect

        group = VGroup(fractals, title, small_rect)
        group.to_corner(UP+LEFT, buff = MED_LARGE_BUFF)

        self.play(
            Write(title),
            ShowCreation(fractals),
            run_time = 3
        )
        self.play(ShowCreation(small_rect))
        self.wait()

    def add_general_fractals(self):
        big_rectangle = Rectangle(
            width = FRAME_WIDTH - MED_LARGE_BUFF,
            height = FRAME_HEIGHT - MED_LARGE_BUFF,
        )
        title = TextMobject("Fractals")
        title.scale(1.5)
        title.next_to(ORIGIN, RIGHT, buff = LARGE_BUFF)
        title.to_edge(UP, buff = MED_LARGE_BUFF)

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
            britain.set_fill, BLUE, 1,
            britain.set_stroke, None, 0,
            run_time = 2
        )
        self.play(FadeIn(randy))
        self.play(MoveToTarget(randy, run_time = 2))
        self.wait(2)

class ConstrastSmoothAndFractal(Scene):
    CONFIG = {
        "britain_zoom_point_proportion" : 0.45,
        "scale_factor" : 50,
        "fractalification_order" : 2,
        "fractal_dimension" : 1.21,
    }
    def construct(self):
        v_line = Line(UP, DOWN).scale(FRAME_Y_RADIUS)
        smooth = TextMobject("Smooth")
        smooth.shift(FRAME_X_RADIUS*LEFT/2)
        fractal = TextMobject("Fractal")
        fractal.shift(FRAME_X_RADIUS*RIGHT/2)
        VGroup(smooth, fractal).to_edge(UP)
        background_rectangle = Rectangle(
            height = FRAME_HEIGHT,
            width = FRAME_X_RADIUS,
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
        smooth_britain.center().shift(FRAME_X_RADIUS*LEFT/2)
        index = np.argmax(smooth_britain.get_anchors()[:,0])
        smooth_britain.zoom_point = smooth_britain.point_from_proportion(
            self.britain_zoom_point_proportion
        )

        britain.shift(FRAME_X_RADIUS*RIGHT/2)
        britain.zoom_point = britain.point_from_proportion(
            self.britain_zoom_point_proportion
        )
        fractalify(
            britain,
            order = self.fractalification_order,
            dimension = self.fractal_dimension,
        )

        britains = VGroup(britain, smooth_britain)
        self.play(*[
            ShowCreation(mob, run_time = 3)
            for mob in britains
        ])
        self.play(
            britains.set_fill, BLUE, 1,
            britains.set_stroke, None, 0,
        )
        self.wait()
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
            run_time = 10,
        )
        self.wait(2)

class InfiniteKochZoom(Scene):
    CONFIG = {
        "order" : 6,
        "left_point" : 3*LEFT,
    }
    def construct(self):
        small_curve = self.get_curve(self.order)
        larger_curve = self.get_curve(self.order + 1)
        larger_curve.scale(3, about_point = small_curve.points[0])
        self.play(Transform(small_curve, larger_curve, run_time = 2))
        self.repeat_frames(5)



    def get_curve(self, order):
        koch_curve = KochCurve(
            monochromatic = True,
            order = order,
            color = BLUE,
            stroke_width = 2,
        )
        koch_curve.set_width(18)
        koch_curve.shift(
            self.left_point - koch_curve.points[0]
        )
        return koch_curve

class ShowIdealizations(Scene):
    def construct(self):
        arrow = DoubleArrow(FRAME_X_RADIUS*LEFT, FRAME_X_RADIUS*RIGHT)
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
        britain.set_height(4)
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
        koch_snowflake.set_height(3)
        koch_snowflake.rotate(2*np.pi/3)
        koch_snowflake.next_to(arrow, UP)
        koch_snowflake.to_edge(RIGHT)

        VGroup(smooth_britain, britain, koch_snowflake).set_color_by_gradient(
            BLUE_B, BLUE_D
        )

        self.play(FadeIn(britain))
        self.wait()
        self.play(Transform(britain.copy(), smooth_britain))
        self.wait()
        self.play(Transform(britain.copy(), koch_snowflake))
        self.wait()
        self.wait(2)

class SayFractalDimension(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("Fractal dimension")
        self.change_student_modes("confused", "hesitant", "pondering")
        self.wait(3)

class ExamplesOfDimension(Scene):
    def construct(self):
        labels = VGroup(*[
            TextMobject("%s-dimensional"%s)
            for s in ("1.585", "1.262", "1.21")
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
            self.wait()
        self.wait()

class FractalDimensionIsNonsense(Scene):
    def construct(self):
        morty = Mortimer().shift(DOWN+3*RIGHT)
        mathy = Mathematician().shift(DOWN+3*LEFT)
        morty.make_eye_contact(mathy)

        self.add(morty, mathy)
        self.play(
            PiCreatureSays(
                mathy, "It's 1.585-dimensional!",
                target_mode = "hooray"
            ),
            morty.change_mode, "hesitant"
        )
        self.play(Blink(morty))
        self.play(
            PiCreatureSays(morty, "Nonsense!", target_mode = "angry"),
            FadeOut(mathy.bubble),
            FadeOut(mathy.bubble.content),
            mathy.change_mode, "guilty"
        )
        self.play(Blink(mathy))
        self.wait()

class DimensionForNaturalNumbers(Scene):
    def construct(self):
        labels = VGroup(*[
            TextMobject("%d-dimensional"%d)
            for d in (1, 2, 3)
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
        self.wait()
        for label in labels[1:]:
            self.play(Write(label))
            self.wait()

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
        self.wait(2)
        self.teacher_says(
            """But it's useful!""",
            target_mode = "hooray"
        )
        self.change_student_modes(*["happy"]*3)
        self.wait(3)

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
        titles = VGroup(*list(map(TextMobject, [
            "Line", "Square", "Cube", "Sierpinski"
        ])))
        for title, x in zip(titles, np.linspace(-0.75, 0.75, 4)):
            title.shift(x*FRAME_X_RADIUS*RIGHT)
        titles.to_edge(UP)
        return titles

    def get_shapes(self, titles):
        line = VGroup(
            Line(LEFT, ORIGIN),
            Line(ORIGIN, RIGHT)
        )
        line.set_color(BLUE_C)

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
            shape.set_width(self.shape_width)
            shape.next_to(title, DOWN, buff = MED_SMALL_BUFF)
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
        self.wait()
        self.play(
            GrowFromCenter(brace),
            FadeIn(brace_text)
        )
        self.wait()
        self.play(*list(map(FadeOut, [brace, brace_text])))
        self.wait()

        for title in titles:
            self.play(Write(title, run_time = 1))
        self.wait(2)

    def show_self_similarity(self, shapes):
        shapes_copy = shapes.copy()
        self.shapes_copy = shapes_copy
        line, square, cube, sierpinski = shapes_copy

        self.play(line.shift, 3*DOWN)
        self.play(ApplyFunction(break_up, line))
        self.wait()
        brace = Brace(line[0], DOWN)
        brace_text = brace.get_text("1/2")
        self.play(
            GrowFromCenter(brace),
            Write(brace_text)
        )
        brace.add(brace_text)
        self.wait()

        self.play(square.next_to, square, DOWN, LARGE_BUFF)
        self.play(ApplyFunction(break_up, square))
        subsquare = square[0]
        subsquare.save_state()
        self.play(subsquare.replace, shapes[1])
        self.wait()
        self.play(subsquare.restore)
        self.play(brace.next_to, subsquare, DOWN)
        self.wait()

        self.wait(5)#Handle cube

        self.play(sierpinski.next_to, sierpinski, DOWN, LARGE_BUFF)
        self.play(ApplyFunction(break_up, sierpinski))
        self.wait()
        self.play(brace.next_to, sierpinski[0], DOWN)
        self.wait(2)
        self.play(FadeOut(brace))

    def mention_measurements(self):
        line, square, cube, sierpinski = self.shapes_copy

        labels = list(map(TextMobject, [
            "$1/2$ length",
            "$1/4$ area",
            "$1/8$ volume",
            "You'll see...",
        ]))
        for label, shape in zip(labels, self.shapes_copy):
            label.next_to(shape, DOWN)
            label.to_edge(DOWN, buff = MED_LARGE_BUFF)
            if label is labels[-1]:
                label.shift(0.1*UP) #Dumb

            self.play(
                Write(label, run_time = 1),
                shape[0].set_color, YELLOW
            )
            self.wait()

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

        words = VGroup(*list(map(TextMobject, [
            "Length", "Area", "Volume"
        ])))
        words.arrange(RIGHT, buff = 2*LARGE_BUFF)
        words.next_to(measure, DOWN, buff = 2*LARGE_BUFF)
        colors = color_gradient([BLUE_B, BLUE_D], len(words))
        for word, color in zip(words, colors):
            word.set_color(color)
        lines = VGroup(*[
            Line(
                measure.get_bottom(), word.get_top(),
                color = word.get_color(),
                buff = MED_SMALL_BUFF
            )
            for word in words
        ])

        for word in words:
            self.play(FadeIn(word))
        self.play(ShowCreation(lines, run_time = 2))
        self.wait()
        self.play(Write(measure))
        self.wait(2)
        self.play(Transform(measure, mass))
        self.wait(2)

class ImagineShapesAsMetal(FourSelfSimilarShapes):
    def construct(self):
        titles = VGroup(*list(map(VGroup, self.get_titles())))
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
            shape.target.set_color(LIGHT_GREY)
        shapes[-1].target.set_color_by_gradient(GREY, WHITE)
        for shape, title in zip(shapes, titles):
            self.play(
                MoveToTarget(title),
                MoveToTarget(shape)
            )
            self.wait()
        self.wait()

        for shape in shapes:
            self.play(
                shape.scale, 0.5, shape.get_top(),
                run_time = 3,
                rate_func = there_and_back
            )
        self.wait()

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
        scaling_factor_label[1].set_color(YELLOW)
        scaling_factor_label.to_edge(LEFT).shift(UP)
        mass_scaling_label = TextMobject(
            "Mass scaling factor:", "$%s$"%self.mass_scaling_factor
        )
        mass_scaling_label[1].set_color(GREEN)
        mass_scaling_label.next_to(
            scaling_factor_label, DOWN,
            aligned_edge = LEFT,
            buff = LARGE_BUFF
        )

        shape = self.get_shape()
        shape.set_width(self.shape_width)
        shape.center()
        shape.shift(FRAME_X_RADIUS*RIGHT/2 + self.vert_distance*UP)

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
        self.wait()

        self.play(
            shape.copy().replace, shape_copy[0]
        )
        self.remove(*self.get_mobjects_from_last_animation())
        self.add(shape_copy[0])
        self.play(
            GrowFromCenter(little_brace),
            Write(little_brace_text)
        )
        self.wait()

        self.play(Write(mass_scaling_label[1], run_time = 1))
        self.wait()
        self.play(FadeIn(
            VGroup(*shape_copy[1:]),
            lag_ratio = 0.5
        ))
        self.wait()
        self.play(Transform(
            shape_copy.copy(), shape
        ))
        self.wait()

    def get_shape(self):
        return VGroup(
            Line(LEFT, ORIGIN),
            Line(ORIGIN, RIGHT)
        ).set_color(BLUE)

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
        return VectorizedPoint()

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
        "scale_factor" : 0.5,
        "bottom_shape_buff" : MED_SMALL_BUFF,
        "scalar" : "s",
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
        self.dimension_in_title.set_color(self.dimension_color)
        title.to_edge(UP)
        self.add(title)

        self.title = title

    def add_h_line(self):
        self.h_line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS)
        self.add(self.h_line)

    def add_shape(self):
        shape = self.get_shape()
        shape.set_width(self.shape_width)
        shape.next_to(self.title, DOWN, buff = MED_LARGE_BUFF)
        # self.shape.shift(FRAME_Y_RADIUS*UP/2)
        self.mass_color = shape.get_color()
        self.add(shape)

        self.shape = shape

    def add_width_mass_labels(self):
        top_length = TextMobject("Length:", "$L$")
        top_mass = TextMobject("Mass:", "$M$")
        bottom_length = TextMobject(
            "Length: ", "$%s$"%self.scalar, "$L$",
            arg_separator = ""
        )
        bottom_mass = TextMobject(
            "Mass: ",
            "$%s^%s$"%(self.scalar, self.dimension),
            "$M$",
            arg_separator = ""
        )
        self.dimension_in_exp = VGroup(
            *bottom_mass[1][-len(self.dimension):]
        )
        self.dimension_in_exp.set_color(self.dimension_color)

        top_group = VGroup(top_length, top_mass)
        bottom_group = VGroup(bottom_length, bottom_mass)
        for group in top_group, bottom_group:
            group.arrange(
                DOWN,
                buff = MED_LARGE_BUFF,
                aligned_edge = LEFT
            )
            group[0][-1].set_color(self.length_color)
            group[1][-1].set_color(self.mass_color)

        top_group.next_to(self.h_line, UP, buff = LARGE_BUFF)
        bottom_group.next_to(self.h_line, DOWN, buff = LARGE_BUFF)
        for group in top_group, bottom_group:
            group.to_edge(LEFT)

        self.add(top_group, bottom_group)

        self.top_L = top_length[-1]
        self.bottom_L = VGroup(*bottom_length[-2:])
        self.bottom_mass = bottom_mass

    def show_top_length(self):
        brace = Brace(self.shape, LEFT)
        top_L = self.top_L.copy()

        self.play(GrowFromCenter(brace))
        self.play(top_L.next_to, brace, LEFT)
        self.wait()

        self.brace = brace

    def perform_scaling(self):
        group = VGroup(self.shape, self.brace).copy()
        self.play(
            group.shift,
            (group.get_top()[1]+self.bottom_shape_buff)*DOWN
        )

        shape, brace = group
        bottom_L = self.bottom_L.copy()
        shape.generate_target()
        shape.target.scale_in_place(
            self.scale_factor,
        )
        brace.target = Brace(shape.target, LEFT)
        self.play(*list(map(MoveToTarget, group)))
        self.play(bottom_L.next_to, brace, LEFT)
        self.wait()

    def show_dimension(self):
        top_dimension = self.dimension_in_title.copy()
        self.play(self.pi_creature.look_at, top_dimension)
        self.play(Transform(
            top_dimension,
            self.dimension_in_exp,
            run_time = 2,
        ))
        self.wait(3)

    def get_shape(self):
        return Square(
            stroke_width = 0,
            fill_color = BLUE,
            fill_opacity = 0.7,
        )

class DefineThreeDimensional(DefineTwoDimensional):
    CONFIG = {
        "dimension" : "3",
    }
    def get_shape(self):
        return Square(
            stroke_width = 0,
            fill_opacity = 0
        )

class DefineSierpinskiDimension(DefineTwoDimensional):
    CONFIG = {
        "dimension" : "D",
        "scalar" : "\\left( \\frac{1}{2} \\right)",
        "sierpinski_order" : 6,
        "equation_scale_factor" : 1.3,
    }
    def construct(self):
        DefineTwoDimensional.construct(self)
        self.change_mode("confused")
        self.wait()
        self.add_one_third()
        self.isolate_equation()

    def add_one_third(self):
        equation = TextMobject(
            "$= \\left(\\frac{1}{3}\\right)$", "$M$",
            arg_separator = ""
        )
        equation.set_color_by_tex("$M$", self.mass_color)
        equation.next_to(self.bottom_mass)

        self.play(Write(equation))
        self.change_mode("pondering")
        self.wait()

        self.equation = VGroup(self.bottom_mass, equation)
        self.distilled_equation = VGroup(
            self.bottom_mass[1],
            equation[0]
        ).copy()

    def isolate_equation(self):
        # everything = VGroup(*self.get_mobjects())
        keepers = [self.pi_creature, self.equation]
        for mob in keepers:
            mob.save_state()
        keepers_copies = [mob.copy() for mob in keepers]
        self.play(
            *[
                ApplyMethod(mob.fade, 0.5)
                for mob in self.get_mobjects()
            ] + [
                Animation(mob)
                for mob in keepers_copies
            ]
        )
        self.remove(*keepers_copies)
        for mob in keepers:
            ApplyMethod(mob.restore).update(1)
        self.add(*keepers)
        self.play(
            self.pi_creature.change_mode, "confused",
            self.pi_creature.look_at, self.equation
        )
        self.wait()

        equation = self.distilled_equation
        self.play(
            equation.arrange, RIGHT,
            equation.scale, self.equation_scale_factor,
            equation.to_corner, UP+RIGHT,
            run_time = 2
        )
        self.wait(2)

        simpler_equation = TexMobject("2^D = 3")
        simpler_equation[1].set_color(self.dimension_color)
        simpler_equation.scale(self.equation_scale_factor)
        simpler_equation.next_to(equation, DOWN, buff = MED_LARGE_BUFF)

        log_expression = TexMobject("\\log_2(3) \\approx", "1.585")
        log_expression[-1].set_color(self.dimension_color)
        log_expression.scale(self.equation_scale_factor)
        log_expression.next_to(simpler_equation, DOWN, buff = MED_LARGE_BUFF)
        log_expression.shift_onto_screen()

        self.play(Write(simpler_equation))
        self.change_mode("pondering")
        self.wait(2)
        self.play(Write(log_expression))
        self.play(
            self.pi_creature.change_mode, "hooray",
            self.pi_creature.look_at, log_expression
        )
        self.wait(2)

    def get_shape(self):
        return Sierpinski(
            order = self.sierpinski_order,
            color = RED,
        )

class ShowSierpinskiCurve(Scene):
    CONFIG = {
        "max_order" : 8,
    }
    def construct(self):
        curve = self.get_curve(2)
        self.play(ShowCreation(curve, run_time = 2))
        for order in range(3, self.max_order + 1):
            self.play(Transform(
                curve, self.get_curve(order),
                run_time = 2
            ))
            self.wait()

    def get_curve(self, order):
        curve = SierpinskiCurve(order = order, monochromatic = True)
        curve.set_color(RED)
        return curve

class LengthAndAreaOfSierpinski(ShowSierpinskiCurve):
    CONFIG = {
        "curve_start_order" : 5,
        "sierpinski_start_order" : 4,
        "n_iterations" : 3,
    }
    def construct(self):
        length = TextMobject("Length = $\\infty$")
        length.shift(FRAME_X_RADIUS*LEFT/2).to_edge(UP)
        area = TextMobject("Area = $0$")
        area.shift(FRAME_X_RADIUS*RIGHT/2).to_edge(UP)
        v_line = Line(UP, DOWN).scale(FRAME_Y_RADIUS)
        self.add(length, area, v_line)

        curve = self.get_curve(order = self.curve_start_order)
        sierp = self.get_sierpinski(order = self.sierpinski_start_order)
        self.add(curve, sierp)
        self.wait()

        for x in range(self.n_iterations):
            new_curve = self.get_curve(order = self.curve_start_order+x+1)
            alpha = (x+1.0)/self.n_iterations
            stroke_width = interpolate(3, 1, alpha)
            new_curve.set_stroke(width = stroke_width)

            new_sierp = self.get_sierpinski(
                order = self.sierpinski_start_order+x+1
            )
            self.play(
                Transform(curve, new_curve),
                Transform(sierp, new_sierp),
                run_time = 2
            )
        self.play(sierp.set_fill, None, 0)
        self.wait()

    def get_curve(self, order):
        # curve = ShowSierpinskiCurve.get_curve(self, order)
        curve = SierpinskiCurve(order = order)
        curve.set_height(4).center()
        curve.shift(FRAME_X_RADIUS*LEFT/2)
        return curve

    def get_sierpinski(self, order):
        result = Sierpinski(order = order)
        result.shift(FRAME_X_RADIUS*RIGHT/2)
        return result

class FractionalAnalogOfLengthAndArea(Scene):
    def construct(self):
        last_sc = LengthAndAreaOfSierpinski(skip_animations = True)
        self.add(*last_sc.get_mobjects())

        morty = Mortimer()
        morty.to_corner(DOWN+RIGHT)
        self.play(FadeIn(morty))
        self.play(PiCreatureSays(
            morty,
            """
            Better described with a
            1.585-dimensional measure.
            """
        ))
        self.play(Blink(morty))
        self.wait()

class DimensionOfKoch(Scene):
    CONFIG = {
        "scaling_factor_color" : YELLOW,
        "mass_scaling_color" : BLUE,
        "dimension_color" : GREEN_A,
        "curve_class" : KochCurve,
        "scaling_factor" : 3,
        "mass_scaling_factor" : 4,
        "num_subparts" : 4,
        "koch_curve_order" : 5,
        "koch_curve_width" : 5,
        "break_up_factor" : 1.5,
        "down_shift" : 3*DOWN,
        "dimension_rhs" : "\\approx 1.262",
    }
    def construct(self):
        self.add_labels()
        self.add_curve()
        self.break_up_curve()
        self.compare_sizes()
        self.show_dimension()

    def add_labels(self):
        scaling_factor = TextMobject(
            "Scaling factor:",
            "$\\frac{1}{%d}$"%self.scaling_factor,
        )
        scaling_factor.next_to(ORIGIN, UP)
        scaling_factor.to_edge(LEFT)
        scaling_factor[1].set_color(self.scaling_factor_color)
        self.add(scaling_factor[0])

        mass_scaling = TextMobject(
            "Mass scaling factor:",
            "$\\frac{1}{%d}$"%self.mass_scaling_factor
        )
        mass_scaling.next_to(ORIGIN, DOWN)
        mass_scaling.to_edge(LEFT)
        mass_scaling[1].set_color(self.mass_scaling_color)
        self.add(mass_scaling[0])

        self.scaling_factor_mob = scaling_factor[1]
        self.mass_scaling_factor_mob = mass_scaling[1]

    def add_curve(self):
        curve = self.curve_class(order = self.koch_curve_order)
        curve.set_width(self.koch_curve_width)
        curve.to_corner(UP+RIGHT, LARGE_BUFF)

        self.play(ShowCreation(curve, run_time = 2))
        self.wait()
        self.curve = curve

    def break_up_curve(self):
        curve_copy = self.curve.copy()
        length = len(curve_copy)
        n_parts = self.num_subparts
        broken_curve = VGroup(*[
            VGroup(*curve_copy[i*length/n_parts:(i+1)*length/n_parts])
            for i in range(n_parts)
        ])
        self.play(broken_curve.shift, self.down_shift)

        broken_curve.generate_target()
        break_up(broken_curve.target, self.break_up_factor)
        broken_curve.target.shift_onto_screen
        self.play(MoveToTarget(broken_curve))
        self.wait()

        self.add(broken_curve)
        self.broken_curve = broken_curve

    def compare_sizes(self):
        big_brace = Brace(self.curve, DOWN)
        one = big_brace.get_text("$1$")
        little_brace = Brace(self.broken_curve[0], DOWN)
        one_third = little_brace.get_text("1/%d"%self.scaling_factor)
        one_third.set_color(self.scaling_factor_color)

        self.play(
            GrowFromCenter(big_brace),
            GrowFromCenter(little_brace),
            Write(one),
            Write(one_third),
        )
        self.wait()
        self.play(Write(self.scaling_factor_mob))
        self.wait()
        self.play(Write(self.mass_scaling_factor_mob))
        self.wait()

    def show_dimension(self):
        raw_formula = TexMobject("""
            \\left( \\frac{1}{%s} \\right)^D
            =
            \\left( \\frac{1}{%s} \\right)
        """%(self.scaling_factor, self.mass_scaling_factor))
        formula = VGroup(
            VGroup(*raw_formula[:5]),
            VGroup(raw_formula[5]),
            VGroup(raw_formula[6]),
            VGroup(*raw_formula[7:]),
        )
        formula.to_corner(UP+LEFT)

        simpler_formula = TexMobject(
            str(self.scaling_factor),
            "^D", "=",
            str(self.mass_scaling_factor)
        )
        simpler_formula.move_to(formula, UP)

        for mob in formula, simpler_formula:
            mob[0].set_color(self.scaling_factor_color)
            mob[1].set_color(self.dimension_color)
            mob[3].set_color(self.mass_scaling_color)

        log_expression = TexMobject(
            "D = \\log_%d(%d) %s"%(
                self.scaling_factor,
                self.mass_scaling_factor,
                self.dimension_rhs
            )
        )
        log_expression[0].set_color(self.dimension_color)
        log_expression[5].set_color(self.scaling_factor_color)
        log_expression[7].set_color(self.mass_scaling_color)
        log_expression.next_to(
            simpler_formula, DOWN,
            aligned_edge = LEFT,
            buff = MED_LARGE_BUFF
        )

        third = self.scaling_factor_mob.copy()
        fourth = self.mass_scaling_factor_mob.copy()
        for mob in third, fourth:
            mob.add(VectorizedPoint(mob.get_right()))
            mob.add_to_back(VectorizedPoint(mob.get_left()))



        self.play(
            Transform(third, formula[0]),
            Transform(fourth, formula[-1]),
        )
        self.play(*list(map(FadeIn, formula[1:-1])))
        self.remove(third, fourth)
        self.add(formula)
        self.wait(2)
        self.play(Transform(formula, simpler_formula))
        self.wait(2)
        self.play(Write(log_expression))
        self.wait(2)

class DimensionOfQuadraticKoch(DimensionOfKoch):
    CONFIG = {
        "curve_class" : QuadraticKoch,
        "scaling_factor" : 4,
        "mass_scaling_factor" : 8,
        "num_subparts" : 8,
        "koch_curve_order" : 4,
        "koch_curve_width" : 4,
        "break_up_factor" : 1.7,
        "down_shift" : 4*DOWN,
        "dimension_rhs" : "= \\frac{3}{2} = 1.5",
    }
    def construct(self):
        self.add_labels()
        self.add_curve()
        self.set_color_curve_subparts()
        self.show_dimension()

    def get_curve(self, order):
        curve = self.curve_class(
            order = order,
            monochromatic = True
        )
        curve.set_width(self.koch_curve_width)
        alpha = float(order) / self.koch_curve_order
        stroke_width = interpolate(3, 1, alpha)
        curve.set_stroke(width = stroke_width)
        return curve

    def add_curve(self):
        seed_label = TextMobject("Seed")
        seed_label.shift(FRAME_X_RADIUS*RIGHT/2).to_edge(UP)
        seed = self.get_curve(order = 1)
        seed.next_to(seed_label, DOWN)

        curve = seed.copy()

        resulting_fractal = TextMobject("Resulting fractal")
        resulting_fractal.shift(FRAME_X_RADIUS*RIGHT/2)

        self.add(seed_label, seed)
        self.wait()
        self.play(
            curve.next_to, resulting_fractal, DOWN, MED_LARGE_BUFF,
            Write(resulting_fractal, run_time = 1)
        )
        for order in range(2, self.koch_curve_order+1):
            new_curve = self.get_curve(order)
            new_curve.move_to(curve)
            n_curve_parts = curve.get_num_curves()
            curve.insert_n_curves(6 * n_curve_parts)
            curve.make_jagged()
            self.play(Transform(curve, new_curve, run_time = 2))
        self.wait()

        self.curve = curve

    def set_color_curve_subparts(self):
        n_parts = self.num_subparts
        colored_curve = self.curve_class(
            order = self.koch_curve_order,
            stroke_width = 1
        )
        colored_curve.replace(self.curve)
        length = len(colored_curve)
        broken_curve = VGroup(*[
            VGroup(*colored_curve[i*length/n_parts:(i+1)*length/n_parts])
            for i in range(n_parts)
        ])
        colors = it.cycle([WHITE, RED])
        for subpart, color in zip(broken_curve, colors):
            subpart.set_color(color)
        self.play(
            FadeOut(self.curve),
            FadeIn(colored_curve)
        )
        self.play(
            ApplyFunction(
                lambda m : break_up(m, self.break_up_factor),
                broken_curve,
                rate_func = there_and_back,
                run_time = 2
            )
        )
        self.wait()
        self.play(Write(self.scaling_factor_mob))
        self.play(Write(self.mass_scaling_factor_mob))
        self.wait(2)

class ThisIsSelfSimilarityDimension(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            This is called
            ``self-similarity dimension''
        """)
        self.change_student_modes(*["pondering"]*3)
        self.wait(2)

class ShowSeveralSelfSimilarityDimensions(Scene):
    def construct(self):
        vects = [
            4*LEFT,
            ORIGIN,
            4*RIGHT,
        ]
        fractal_classes = [
            PentagonalFractal,
            QuadraticKoch,
            DiamondFractal,
        ]
        max_orders = [
            4,
            4,
            5,
        ]
        dimensions = [
            1.668,
            1.500,
            1.843,
        ]

        title = TextMobject("``Self-similarity dimension''")
        title.to_edge(UP)
        title.set_color(YELLOW)
        self.add(title)


        def get_curves(order):
            curves = VGroup()
            for Class, vect in zip(fractal_classes, vects):
                curve = Class(order = order)
                curve.set_width(2),
                curve.shift(vect)
                curves.add(curve)
            return curves
        curves = get_curves(1)
        self.add(curves)

        for curve, dimension, u in zip(curves, dimensions, [1, -1, 1]):
            label = TextMobject("%.3f-dimensional"%dimension)
            label.scale(0.85)
            label.next_to(curve, u*UP, buff = LARGE_BUFF)
            self.add(label)

        self.wait()

        for order in  range(2, max(max_orders)+1):
            anims = []
            for curve, max_order in zip(curves, max_orders):
                if order <= max_order:
                    new_curve = curve.__class__(order = order)
                    new_curve.replace(curve)
                    anims.append(Transform(curve, new_curve))
            self.play(*anims, run_time = 2)
        self.wait()
        self.curves = curves

class SeparateFractals(Scene):
    def construct(self):
        last_sc = ShowSeveralSelfSimilarityDimensions(skip_animations = True)
        self.add(*last_sc.get_mobjects())
        quad_koch = last_sc.curves[1]
        length = len(quad_koch)
        new_quad_koch = VGroup(*[
            VGroup(*quad_koch[i*length/8:(i+1)*length/8])
            for i in range(8)
        ])
        curves = list(last_sc.curves)
        curves[1] = new_quad_koch
        curves = VGroup(*curves)
        curves.save_state()
        self.play(*[
            ApplyFunction(
                lambda m : break_up(m, 2),
                curve
            )
            for curve in curves
        ])
        self.wait(2)
        self.play(curves.restore)
        self.wait()

class ShowDiskScaling(Scene):
    def construct(self):
        self.show_non_self_similar_shapes()
        self.isolate_disk()
        self.scale_disk()
        self.write_mass_scaling_factor()
        self.try_fitting_small_disks()

    def show_non_self_similar_shapes(self):
        title = TextMobject(
            "Most shapes are not self-similar"
        )
        title.to_edge(UP)
        self.add(title)

        hexagon = RegularPolygon(n = 6)
        disk = Circle()
        blob = VMobject().set_points_smoothly([
            RIGHT, RIGHT+UP, ORIGIN, RIGHT+DOWN, LEFT, UP, RIGHT
        ])
        britain = Britain()
        shapes = VGroup(hexagon, blob, disk, britain)
        for shape in shapes:
            shape.set_width(1.5)
            shape.set_stroke(width = 0)
            shape.set_fill(opacity = 1)
        shapes.set_color_by_gradient(BLUE_B, BLUE_E)
        shapes.arrange(RIGHT, buff = LARGE_BUFF)
        shapes.next_to(title, DOWN)
        for shape in shapes:
            self.play(FadeIn(shape))
        self.wait(2)

        self.disk = disk
        self.to_fade = VGroup(
            title, hexagon, blob, britain
        )

    def isolate_disk(self):
        disk = self.disk
        self.play(
            FadeOut(self.to_fade),
            disk.set_width, 2,
            disk.next_to, ORIGIN, LEFT, 2,
            disk.set_fill, BLUE_D, 0.7
        )

        radius = Line(
            disk.get_center(), disk.get_right(),
            color = YELLOW
        )
        one = TexMobject("1").next_to(radius, DOWN, SMALL_BUFF)

        self.play(ShowCreation(radius))
        self.play(Write(one))
        self.wait()

        self.disk.add(radius, one)

    def scale_disk(self):
        scaled_disk = self.disk.copy()
        scaled_disk.generate_target()
        scaled_disk.target.scale(2)
        scaled_disk.target.next_to(ORIGIN, RIGHT)

        one = scaled_disk.target[-1]
        two = TexMobject("2")
        two.move_to(one, UP)
        scaled_disk.target.submobjects[-1] = two

        self.play(MoveToTarget(scaled_disk))
        self.wait()

        self.scaled_disk = scaled_disk

    def write_mass_scaling_factor(self):
        mass_scaling = TextMobject(
            "Mass scaling factor: $2^2 = 4$"
        )
        mass_scaling.next_to(self.scaled_disk, UP)
        mass_scaling.to_edge(UP)
        self.play(Write(mass_scaling))
        self.wait()

    def try_fitting_small_disks(self):
        disk = self.disk.copy()
        disk.submobjects = []
        disk.set_fill(opacity = 0.5)
        foursome = VGroup(*[
            disk.copy().next_to(ORIGIN, vect, buff = 0)
            for vect in compass_directions(start_vect = UP+RIGHT)
        ])
        foursome.move_to(self.scaled_disk)

        self.play(Transform(disk, foursome))
        self.remove(*self.get_mobjects_from_last_animation())
        self.add(foursome)
        self.wait()
        self.play(ApplyFunction(
            lambda m : break_up(m, 0.2),
            foursome,
            rate_func = there_and_back,
            run_time = 4,
        ))
        self.wait()
        self.play(FadeOut(foursome))
        self.wait()

class WhatDoYouMeanByMass(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "What do you mean \\\\ by mass?",
            target_mode = "sassy"
        )
        self.change_student_modes("pondering", "sassy", "confused")
        self.wait()
        self.play(self.get_teacher().change_mode, "thinking")
        self.wait(2)
        self.teacher_thinks("")
        self.zoom_in_on_thought_bubble()

class BoxCountingScene(Scene):
    CONFIG = {
        "box_width" : 0.25,
        "box_color" : YELLOW,
        "box_opacity" : 0.5,
        "num_boundary_check_points" : 200,
        "corner_rect_left_extension" : 0,
    }
    def setup(self):
        self.num_rows = 2*int(FRAME_Y_RADIUS/self.box_width)+1
        self.num_cols = 2*int(FRAME_X_RADIUS/self.box_width)+1

    def get_grid(self):
        v_line = Line(UP, DOWN).scale(FRAME_Y_RADIUS)
        v_lines = VGroup(*[
            v_line.copy().shift(u*x*self.box_width*RIGHT)
            for x in range(self.num_cols/2+1)
            for u in [-1, 1]
        ])
        h_line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS)
        h_lines = VGroup(*[
            h_line.copy().shift(u*y*self.box_width*UP)
            for y in range(self.num_rows/2+1)
            for u in [-1, 1]
        ])

        grid = VGroup(v_lines, h_lines)
        if self.box_width > 0.2:
            grid.set_stroke(width = 1)
        else:
            grid.set_stroke(width = 0.5)
        return grid

    def get_highlighted_boxes(self, vmobject):
        points = []
        if vmobject.stroke_width > 0:
            for submob in vmobject.family_members_with_points():
                alphas = np.linspace(0, 1, self.num_boundary_check_points)
                points += [
                    submob.point_from_proportion(alpha)
                    for alpha in alphas
                ]
        if vmobject.fill_opacity > 0:
            camera = Camera(**LOW_QUALITY_CAMERA_CONFIG)
            camera.capture_mobject(vmobject)
            box_centers = self.get_box_centers()
            pixel_coords = camera.points_to_pixel_coords(box_centers)
            for index, (x, y) in enumerate(pixel_coords):
                try:
                    rgb = camera.pixel_array[y, x]
                    if not np.all(rgb == np.zeros(3)):
                        points.append(box_centers[index])
                except:
                    pass
        return self.get_boxes(points)

    def get_box_centers(self):
        bottom_left = reduce(op.add, [
            self.box_width*(self.num_cols/2)*LEFT,
            self.box_width*(self.num_rows/2)*DOWN,
            self.box_width*RIGHT/2,
            self.box_width*UP/2,
        ])
        return np.array([
            bottom_left + (x*RIGHT+y*UP)*self.box_width
            for x in range(self.num_cols)
            for y in range(self.num_rows)
        ])

    def get_boxes(self, points):
        points = np.array(points)
        rounded_points = np.floor(points/self.box_width)*self.box_width
        unique_rounded_points = np.vstack({
            tuple(row) for
            row in rounded_points
        })

        return VGroup(*[
            Square(
                side_length = self.box_width,
                stroke_width = 0,
                fill_color = self.box_color,
                fill_opacity = self.box_opacity,
            ).move_to(point, DOWN+LEFT)
            for point in unique_rounded_points
        ])

    def get_corner_rect(self):
        rect = Rectangle(
            height = FRAME_Y_RADIUS/2,
            width = FRAME_X_RADIUS+self.corner_rect_left_extension,
            stroke_width = 0,
            fill_color = BLACK,
            fill_opacity = 0.8
        )
        rect.to_corner(UP+RIGHT, buff = 0)
        return rect

    def get_counting_label(self):
        label = TextMobject("Boxes touched:")
        label.next_to(ORIGIN, RIGHT)
        label.to_edge(UP)
        label.shift(self.corner_rect_left_extension*LEFT)
        self.counting_num_reference = label[-1]
        rect = BackgroundRectangle(label)
        rect.stretch(1.3, 0)
        rect.move_to(label, LEFT)
        label.add_to_back(rect)
        return label

    def count_boxes(self, boxes):
        num = DecimalNumber(len(boxes), num_decimal_places = 0)
        num.next_to(boxes, RIGHT)
        num.add_to_back(BackgroundRectangle(num))

        self.play(ShowCreation(boxes, run_time = 3))
        self.play(Write(num))
        self.play(
            num.next_to, self.counting_num_reference, RIGHT, MED_SMALL_BUFF, DOWN,
            num.set_color, YELLOW
        )
        return num

class BoxCountingWithDisk(BoxCountingScene):
    CONFIG = {
        "box_width" : 0.25,
        "num_boundary_check_points" : 200,
        "corner_rect_left_extension" : 2,
        "disk_opacity" : 0.5,
        "disk_stroke_width" : 0.5,
        "decimal_string" : "= %.2f",
    }
    def construct(self):
        disk = Circle(radius = 1)
        disk.set_fill(BLUE, opacity = self.disk_opacity)
        disk.set_stroke(BLUE, width = self.disk_stroke_width)
        disk.shift(0.1*np.sqrt(2)*(UP+RIGHT))

        radius = Line(disk.get_center(), disk.get_right())
        disk.add(radius)
        one = TexMobject("1").next_to(radius, DOWN, SMALL_BUFF)

        boxes = self.get_highlighted_boxes(disk)
        small_box_num = len(boxes)
        grid = self.get_grid()
        corner_rect = self.get_corner_rect()
        counting_label = self.get_counting_label()

        prop_words = TextMobject("Proportional to", "$\\pi r^2$")
        prop_words[1].set_color(BLUE)
        prop_words.next_to(counting_label, DOWN, aligned_edge = LEFT)

        self.add(disk, one)
        self.play(
            ShowCreation(grid),
            Animation(disk),
        )
        self.wait()
        self.play(
            FadeIn(corner_rect),
            FadeIn(counting_label)
        )
        counting_mob = self.count_boxes(boxes)
        self.wait()
        self.play(Write(prop_words, run_time = 2))
        self.wait(2)
        self.play(FadeOut(prop_words))


        disk.generate_target()
        disk.target.scale(2, about_point = disk.get_top())
        two = TexMobject("2").next_to(disk.target[1], DOWN, SMALL_BUFF)
        self.play(
            MoveToTarget(disk),
            Transform(one, two),
            FadeOut(boxes),
        )
        self.play(counting_mob.next_to, counting_mob, DOWN)
        boxes = self.get_highlighted_boxes(disk)
        large_box_count = len(boxes)
        new_counting_mob = self.count_boxes(boxes)
        self.wait()

        frac_line = TexMobject("-")
        frac_line.set_color(YELLOW)
        frac_line.stretch_to_fit_width(new_counting_mob.get_width())
        frac_line.next_to(new_counting_mob, DOWN, buff = SMALL_BUFF)
        decimal = TexMobject(self.decimal_string%(float(large_box_count)/small_box_num))
        decimal.next_to(frac_line, RIGHT)
        approx = TexMobject("\\approx 2^2")
        approx.next_to(decimal, RIGHT, aligned_edge = DOWN)
        approx.shift_onto_screen()
        self.play(*list(map(Write, [frac_line, decimal])))
        self.play(Write(approx))
        self.wait()

        randy = Randolph().shift(3*RIGHT).to_edge(DOWN)
        self.play(FadeIn(randy))
        self.play(PiCreatureSays(
            randy, "Is it?",
            target_mode = "sassy",
            bubble_kwargs = {"direction" : LEFT}
        ))
        self.play(Blink(randy))
        self.wait()

class FinerBoxCountingWithDisk(BoxCountingWithDisk):
    CONFIG = {
        "box_width" : 0.03,
        "num_boundary_check_points" : 1000,
        "disk_stroke_width" : 0.5,
        "decimal_string" : "= %.2f",
    }

class PlotDiskBoxCounting(GraphScene):
    CONFIG = {
        "x_axis_label" : "Scaling factor",
        "y_axis_label" : "Number of boxes \\\\ touched",
        "x_labeled_nums" : [],
        "y_labeled_nums" : [],
        "x_min" : 0,
        "y_min" : 0,
        "y_max" : 30,
        "func" : lambda x : 0.5*x**2,
        "func_label" : "f(x) = cx^2",
    }
    def construct(self):
        self.plot_points()
        self.describe_better_fit()

    def plot_points(self):
        self.setup_axes()
        self.graph_function(self.func)
        self.remove(self.graph)

        data_points = [
            self.input_to_graph_point(x) + ((random.random()-0.5)/x)*UP
            for x in np.arange(2, 10, 0.5)
        ]
        data_dots = VGroup(*[
            Dot(point, radius = 0.05, color = YELLOW)
            for point in data_points
        ])

        self.play(ShowCreation(data_dots))
        self.wait()
        self.play(ShowCreation(self.graph))
        self.label_graph(
            self.graph,
            self.func_label,
            direction = RIGHT+DOWN,
            buff = SMALL_BUFF,
            color = WHITE,
        )
        self.wait()

    def describe_better_fit(self):
        words = TextMobject("Better fit at \\\\ higher inputs")
        arrow = Arrow(2*LEFT, 2*RIGHT)
        arrow.next_to(self.x_axis_label_mob, UP)
        arrow.shift(2*LEFT)
        words.next_to(arrow, UP)

        self.play(ShowCreation(arrow))
        self.play(Write(words))
        self.wait(2)

class FineGridSameAsLargeScaling(BoxCountingScene):
    CONFIG = {
        "box_width" : 0.25/6,
        "scale_factor" : 6
    }
    def construct(self):
        disk = Circle(radius = 1)
        disk.set_fill(BLUE, opacity = 0.5)
        disk.set_stroke(BLUE, width = 1)

        grid = self.get_grid()
        grid.scale(self.scale_factor)

        self.add(grid, disk)
        self.wait()
        self.play(disk.scale, self.scale_factor)
        self.wait()
        self.play(
            grid.scale, 1./self.scale_factor,
            disk.scale, 1./self.scale_factor,
            disk.set_stroke, None, 0.5,
        )
        self.wait()
        boxes = self.get_highlighted_boxes(disk)
        self.play(ShowCreation(boxes, run_time = 3))
        self.wait(2)

class BoxCountingSierpinski(BoxCountingScene):
    CONFIG = {
        "box_width" : 0.1,
        "sierpinski_order" : 7,
        "sierpinski_width" : 3,
        "num_boundary_check_points" : 6,
        "corner_rect_left_extension" : 2,
    }
    def construct(self):
        self.add(self.get_grid())
        sierp = Sierpinski(order = self.sierpinski_order)
        sierp.set_fill(opacity = 0)
        sierp.move_to(3*DOWN, DOWN+RIGHT)
        sierp.set_width(self.sierpinski_width)
        boxes = self.get_highlighted_boxes(sierp)

        corner_rect = self.get_corner_rect()
        counting_label = self.get_counting_label()

        self.play(ShowCreation(sierp))
        self.play(*list(map(FadeIn, [corner_rect, counting_label])))
        self.wait()
        counting_mob = self.count_boxes(boxes)
        self.wait()
        self.play(
            FadeOut(boxes),
            sierp.scale, 2, sierp.get_corner(DOWN+RIGHT),
        )
        self.play(counting_mob.next_to, counting_mob, DOWN)
        boxes = self.get_highlighted_boxes(sierp)
        new_counting_mob = self.count_boxes(boxes)
        self.wait()

        frac_line = TexMobject("-")
        frac_line.set_color(YELLOW)
        frac_line.stretch_to_fit_width(new_counting_mob.get_width())
        frac_line.next_to(new_counting_mob, DOWN, buff = SMALL_BUFF)
        approx_three = TexMobject("\\approx 3")
        approx_three.next_to(frac_line, RIGHT)
        equals_exp = TexMobject("= 2^{1.585...}")
        equals_exp.next_to(approx_three, RIGHT, aligned_edge = DOWN)
        equals_exp.shift_onto_screen()

        self.play(*list(map(Write, [frac_line, approx_three])))
        self.wait()
        self.play(Write(equals_exp))
        self.wait()

class PlotSierpinskiBoxCounting(PlotDiskBoxCounting):
    CONFIG = {
        "func" : lambda x : 0.5*x**1.585,
        "func_label" : "f(x) = cx^{1.585}",
    }
    def construct(self):
        self.plot_points()

class BoxCountingWithBritain(BoxCountingScene):
    CONFIG = {
        "box_width" : 0.1,
        "num_boundary_check_points" : 5000,
        "corner_rect_left_extension" : 1,
    }
    def construct(self):
        self.show_box_counting()
        self.show_formula()

    def show_box_counting(self):
        self.add(self.get_grid())
        britain = Britain(
            stroke_width = 2,
            fill_opacity = 0
        )
        britain = fractalify(britain, order = 1, dimension = 1.21)
        britain.shift(DOWN+LEFT)
        boxes = self.get_highlighted_boxes(britain)

        self.play(ShowCreation(britain, run_time = 3))
        self.wait()
        self.play(ShowCreation(boxes, run_time = 3))
        self.wait()
        self.play(FadeOut(boxes))
        self.play(britain.scale, 2.5, britain.get_corner(DOWN+RIGHT))
        boxes = self.get_highlighted_boxes(britain)
        self.play(ShowCreation(boxes, run_time = 2))
        self.wait()

    def show_formula(self):
        corner_rect = self.get_corner_rect()
        equation = TextMobject("""
            Number of boxes $\\approx$
            \\quad $c(\\text{scaling factor})^{1.21}$
        """)
        equation.next_to(
            corner_rect.get_corner(UP+LEFT), DOWN+RIGHT
        )

        N = equation[0].copy()
        word_len = len("Numberofboxes")
        approx = equation[word_len].copy()
        c = equation[word_len+1].copy()
        s = equation[word_len+3].copy()
        dim = VGroup(*equation[-len("1.21"):]).copy()

        N.set_color(YELLOW)
        s.set_color(BLUE)
        dim.set_color(GREEN)

        simpler_eq = VGroup(N, approx, c, s, dim)
        simpler_eq.generate_target()
        simpler_eq.target.arrange(buff = SMALL_BUFF)
        simpler_eq.target.move_to(N, LEFT)
        simpler_eq.target[-1].next_to(
            simpler_eq.target[-2].get_corner(UP+RIGHT),
            RIGHT,
            buff = SMALL_BUFF
        )

        self.play(
            FadeIn(corner_rect),
            Write(equation)
        )
        self.wait(2)
        self.play(FadeIn(simpler_eq))
        self.wait()
        self.play(
            FadeOut(equation),
            Animation(simpler_eq)
        )
        self.play(MoveToTarget(simpler_eq))
        self.wait(2)

        log_expression1 = TexMobject(
            "\\log(", "N", ")", "=",
            "\\log(", "c", "s", "^{1.21}", ")"
        )
        log_expression2 = TexMobject(
            "\\log(", "N", ")", "=",
            "\\log(", "c", ")", "+",
            "1.21", "\\log(", "s", ")"
        )
        for log_expression in log_expression1, log_expression2:
            log_expression.next_to(simpler_eq, DOWN, aligned_edge = LEFT)
            log_expression.set_color_by_tex("N", N.get_color())
            log_expression.set_color_by_tex("s", s.get_color())
            log_expression.set_color_by_tex("^{1.21}", dim.get_color())
            log_expression.set_color_by_tex("1.21", dim.get_color())
        rewired_log_expression1 = VGroup(*[
            log_expression1[index].copy()
            for index in [
                0, 1, 2, 3, #match with log_expression2
                4, 5, 8, 8,
                7, 4, 6, 8
            ]
        ])

        self.play(Write(log_expression1))
        self.remove(log_expression1)
        self.add(rewired_log_expression1)
        self.wait()
        self.play(Transform(
            rewired_log_expression1,
            log_expression2,
            run_time = 2
        ))
        self.wait(2)

        self.final_expression = VGroup(
            simpler_eq, rewired_log_expression1
        )

class GiveShapeAndPonder(Scene):
    def construct(self):
        morty = Mortimer()
        randy = Randolph()
        morty.next_to(ORIGIN, DOWN).shift(3*RIGHT)
        randy.next_to(ORIGIN, DOWN).shift(3*LEFT)

        norway = Norway(fill_opacity = 0, stroke_width = 1)
        norway.set_width(2)
        norway.next_to(morty, UP+LEFT, buff = -MED_SMALL_BUFF)

        self.play(
            morty.change_mode, "raise_right_hand",
            morty.look_at, norway,
            randy.look_at, norway,
            ShowCreation(norway)
        )
        self.play(Blink(morty))
        self.play(randy.change_mode, "pondering")
        self.play(Blink(randy))
        self.wait()

class CheapBoxCountingWithBritain(BoxCountingWithBritain):
    CONFIG = {
        "skip_animations" : True,
    }
    def construct(self):
        self.show_formula()

class ConfusedAtParabolicData(PlotDiskBoxCounting):
    CONFIG = {
        "func" : lambda x : 0.5*x**1.6,
        "func_label" : "f(x) = cx^{1.21}",
    }

    def construct(self):
        self.plot_points()
        randy = Randolph()
        randy.to_corner(DOWN+LEFT)
        randy.shift(RIGHT)

        self.play(FadeIn(randy))
        self.play(randy.change_mode, "confused")
        self.play(randy.look_at, self.x_axis_label_mob)
        self.play(Blink(randy))
        self.wait(2)

class IntroduceLogLogPlot(GraphScene):
    CONFIG = {
        "x_axis_label" : "\\log(s)",
        "y_axis_label" : "\\log(N)",
        "x_labeled_nums" : [],
        "y_labeled_nums" : [],
        "graph_origin" : 2.5*DOWN+6*LEFT,
        "dimension" : 1.21,
        "y_intercept" : 2,
        "x_max" : 16,
    }
    def construct(self):
        last_scene = CheapBoxCountingWithBritain()
        expression = last_scene.final_expression
        box = Rectangle(
            stroke_color = WHITE,
            fill_color = BLACK,
            fill_opacity = 0.7,
        )
        box.replace(expression, stretch = True)
        box.scale_in_place(1.2)
        expression.add_to_back(box)
        self.add(expression)

        self.setup_axes(animate = False)
        self.x_axis_label_mob[-2].set_color(BLUE)
        self.y_axis_label_mob[-2].set_color(YELLOW)
        graph = self.graph_function(
            lambda x : self.y_intercept+self.dimension*x
        )
        self.remove(graph)
        p1 = self.input_to_graph_point(2)
        p2 = self.input_to_graph_point(3)
        interim_point = p2[0]*RIGHT + p1[1]*UP
        h_line = Line(p1, interim_point)
        v_line = Line(interim_point, p2)
        slope_lines = VGroup(h_line, v_line)
        slope_lines.set_color(GREEN)

        slope = TextMobject("Slope = ", "$%.2f$"%self.dimension)
        slope[-1].set_color(GREEN)
        slope.next_to(slope_lines, RIGHT)

        self.wait()
        data_points = [
            self.input_to_graph_point(x) + ((random.random()-0.5)/x)*UP
            for x in np.arange(1, 8, 0.7)
        ]
        data_dots = VGroup(*[
            Dot(point, radius = 0.05, color = YELLOW)
            for point in data_points
        ])
        self.play(ShowCreation(data_dots, run_time = 3))
        self.wait()

        self.play(
            ShowCreation(graph),
            Animation(expression)
        )
        self.wait()
        self.play(ShowCreation(slope_lines))
        self.play(Write(slope))
        self.wait()

class ManyBritainCounts(BoxCountingWithBritain):
    CONFIG = {
        "box_width" : 0.1,
        "num_boundary_check_points" : 10000,
        "corner_rect_left_extension" : 1,
    }
    def construct(self):
        britain = Britain(
            stroke_width = 2,
            fill_opacity = 0
        )
        britain = fractalify(britain, order = 1, dimension = 1.21)
        britain.next_to(ORIGIN, LEFT)
        self.add(self.get_grid())
        self.add(britain)

        for x in range(5):
            self.play(britain.scale, 2, britain.point_from_proportion(0.8))
            boxes = self.get_highlighted_boxes(britain)
            self.play(ShowCreation(boxes))
            self.wait()
            self.play(FadeOut(boxes))

class ReadyForRealDefinition(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            Now for what
            fractals really are.
        """)
        self.change_student_modes(*["hooray"]*3)
        self.wait(2)

class DefineFractal(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            Fractals are shapes
            with a non-integer dimension.
        """)
        self.change_student_modes("thinking", "happy", "erm")
        self.wait(3)
        self.teacher_says(
            "Kind of...",
            target_mode = "sassy"
        )
        self.change_student_modes(*["pondering"]*3)
        self.play(*[
            ApplyMethod(pi.look, DOWN)
            for pi in self.get_pi_creatures()
        ])
        self.wait(3)

class RoughnessAndFractionalDimension(Scene):
    def construct(self):
        title = TextMobject(
            "Non-integer dimension $\\Leftrightarrow$ Roughness"
        )
        title.to_edge(UP)
        self.add(title)

        randy = Randolph().scale(2)
        randy.to_corner(DOWN+RIGHT)
        self.add(randy)

        target = randy.copy()
        target.change_mode("hooray")
        ponder_target = randy.copy()
        ponder_target.change_mode("pondering")
        for mob in target, ponder_target:
            fractalify(mob, order = 2)

        dimension_label = TextMobject("Boundary dimension = ", "1")
        dimension_label.to_edge(LEFT)
        one = dimension_label[1]
        one.set_color(BLUE)
        new_dim = TexMobject("1.2")
        new_dim.move_to(one, DOWN+LEFT)
        new_dim.set_color(one.get_color())
        self.add(dimension_label)

        self.play(Blink(randy))
        self.play(
            Transform(randy, target, run_time = 2),
            Transform(one, new_dim)
        )
        self.wait()
        self.play(Blink(randy))
        self.play(randy.look, DOWN+RIGHT)
        self.wait()
        self.play(randy.look, DOWN+LEFT)
        self.play(Blink(randy))
        self.wait()
        self.play(Transform(randy, ponder_target))
        self.wait()

class DifferentSlopesAtDifferentScales(IntroduceLogLogPlot):
    def construct(self):
        self.setup_axes(animate = False)
        self.x_axis_label_mob[-2].set_color(BLUE)
        self.y_axis_label_mob[-2].set_color(YELLOW)
        self.graph_function(
            lambda x : 0.01*(x-5)**3 + 0.3*x + 3
        )
        self.remove(self.graph)

        words = TextMobject("""
            Different slopes
            at different scales
        """)
        words.to_edge(RIGHT)
        arrows = VGroup(*[
            Arrow(words.get_left(), self.input_to_graph_point(x))
            for x in (1, 7, 12)
        ])


        data_points = [
            self.input_to_graph_point(x) + (0.3*(random.random()-0.5))*UP
            for x in np.arange(1, self.x_max, 0.7)
        ]
        data_dots = VGroup(*[
            Dot(point, radius = 0.05, color = YELLOW)
            for point in data_points
        ])

        self.play(ShowCreation(data_dots, run_time = 2))
        self.play(ShowCreation(self.graph))
        self.wait()
        self.play(
            Write(words),
            ShowCreation(arrows)
        )
        self.wait()

class HoldUpCoilExample(TeacherStudentsScene):
    def construct(self):
        point = UP+RIGHT
        self.play(
            self.get_teacher().change_mode, "raise_right_hand",
            self.get_teacher().look_at, point
        )
        self.play(*[
            ApplyMethod(pi.look_at, point)
            for pi in self.get_students()
        ])
        self.wait(5)
        self.change_student_modes(*["thinking"]*3)
        self.play(*[
            ApplyMethod(pi.look_at, point)
            for pi in self.get_students()
        ])
        self.wait(5)

class SmoothHilbertZoom(Scene):
    def construct(self):
        hilbert = HilbertCurve(
            order = 7,
            color = MAROON_B,
            monochromatic = True
        )
        hilbert.make_smooth()
        self.add(hilbert)

        two_d_title = TextMobject("2D at a distance...")
        one_d_title = TextMobject("1D up close")
        for title in two_d_title, one_d_title:
            title.to_edge(UP)

        self.add(two_d_title)
        self.wait()
        self.play(
            ApplyMethod(
                hilbert.scale, 100,
                hilbert.point_from_proportion(0.3),
            ),
            Transform(
                two_d_title, one_d_title,
                rate_func = squish_rate_func(smooth)
            ),
            run_time = 3
        )
        self.wait()

class ListDimensionTypes(PiCreatureScene):
    CONFIG = {
        "use_morty" : False,
    }
    def construct(self):
        types = VGroup(*list(map(TextMobject, [
            "Box counting dimension",
            "Information dimension",
            "Hausdorff dimension",
            "Packing dimension"
        ])))
        types.arrange(DOWN, aligned_edge = LEFT)
        for text in types:
            self.play(
                Write(text, run_time = 1),
                self.pi_creature.change_mode, "pondering"
            )
        self.wait(3)

class ZoomInOnBritain(Scene):
    CONFIG = {
        "zoom_factor" : 1000
    }
    def construct(self):
        britain = Britain()
        fractalify(britain, order = 3, dimension = 1.21)
        anchors = britain.get_anchors()

        key_value = int(0.3*len(anchors))
        point = anchors[key_value]
        thinning_factor = 100
        num_neighbors_kept = 1000

        britain.set_points_as_corners(reduce(
            lambda a1, a2 : np.append(a1, a2, axis = 0),
            [
            anchors[:key_value-num_neighbors_kept:thinning_factor,:],
            anchors[key_value-num_neighbors_kept:key_value+num_neighbors_kept,:],
            anchors[key_value+num_neighbors_kept::thinning_factor,:],
            ]
        ))

        self.add(britain)
        self.wait()
        self.play(
            britain.scale, self.zoom_factor, point,
            run_time = 10
        )
        self.wait()

class NoteTheConstantSlope(Scene):
    def construct(self):
        words = TextMobject("Note the \\\\ constant slope")
        words.set_color(YELLOW)
        self.play(Write(words))
        self.wait(2)

class FromHandwavyToQuantitative(Scene):
    def construct(self):
        randy = Randolph()
        morty = Mortimer()
        for pi in randy, morty:
            pi.next_to(ORIGIN, DOWN)
        randy.shift(2*LEFT)
        morty.shift(2*RIGHT)
        randy.make_eye_contact(morty)

        self.add(randy, morty)
        self.play(PiCreatureSays(
            randy, "Fractals are rough",
            target_mode = "shruggie"
        ))
        self.play(morty.change_mode, "sassy")
        self.play(Blink(morty))
        self.play(
            PiCreatureSays(
                morty, "We can make \\\\ that quantitative!",
                target_mode = "hooray"
            ),
            FadeOut(randy.bubble),
            FadeOut(randy.bubble.content),
            randy.change_mode, "happy"
        )
        self.play(Blink(randy))
        self.wait()

class WhatSlopeDoesLogLogPlotApproach(IntroduceLogLogPlot):
    CONFIG = {
        "words" : "What slope does \\\\ this approach?",
        "x_max" : 20,
        "y_max" : 15,
    }
    def construct(self):
        self.setup_axes(animate = False)
        self.x_axis_label_mob[-2].set_color(BLUE)
        self.y_axis_label_mob[-2].set_color(YELLOW)

        spacing = 0.5
        x_range = np.arange(1, self.x_max, spacing)
        randomness = [
            0.5*np.exp(-x/2)+spacing*(0.8 + random.random()/(x**(0.5)))
            for x in x_range
        ]
        cum_sums = np.cumsum(randomness)
        data_points = [
            self.coords_to_point(x, cum_sum)
            for x, cum_sum in zip(x_range, cum_sums)
        ]
        data_dots = VGroup(*[
            Dot(point, radius = 0.025, color = YELLOW)
            for point in data_points
        ])

        words = TextMobject(self.words)
        p1, p2 = [
            data_dots[int(alpha*len(data_dots))].get_center()
            for alpha in (0.3, 0.5)
        ]
        words.rotate(Line(p1, p2).get_angle())
        words.next_to(p1, RIGHT, aligned_edge = DOWN, buff = 1.5)

        morty = Mortimer()
        morty.to_corner(DOWN+RIGHT)
        self.add(morty)

        self.play(ShowCreation(data_dots, run_time = 7))
        self.play(
            Write(words),
            morty.change_mode, "speaking"
        )
        self.play(Blink(morty))
        self.wait()

class BritainBoxCountHighZoom(BoxCountingWithBritain):
    def construct(self):
        britain = Britain(
            stroke_width = 2,
            fill_opacity = 0
        )
        britain = fractalify(britain, order = 2, dimension = 1.21)
        self.add(self.get_grid())
        self.add(britain)

        for x in range(2):
            self.play(
                britain.scale, 10, britain.point_from_proportion(0.3),
                run_time = 2
            )
            if x == 0:
                a, b = 0.2, 0.5
            else:
                a, b = 0.25, 0.35
            britain.pointwise_become_partial(britain, a, b)
            self.count_britain(britain)
            self.wait()

    def count_britain(self, britain):
        boxes = self.get_highlighted_boxes(britain)
        self.play(ShowCreation(boxes))
        self.wait()
        self.play(FadeOut(boxes))

class IfBritainWasEventuallySmooth(Scene):
    def construct(self):
        britain = Britain()
        britain.make_smooth()
        point = britain.point_from_proportion(0.3)

        self.add(britain)
        self.wait()
        self.play(
            britain.scale, 200, point,
            run_time = 10
        )
        self.wait()

class SmoothBritainLogLogPlot(IntroduceLogLogPlot):
    CONFIG = {
    }
    def construct(self):
        self.setup_axes()
        self.graph_function(
            lambda x : (1 + np.exp(-x/5.0))*x
        )
        self.remove(self.graph)

        p1, p2, p3, p4 = [
            self.input_to_graph_point(x)
            for x in (1, 2, 7, 8)
        ]
        interim_point1 = p2[0]*RIGHT + p1[1]*UP
        interim_point2 = p4[0]*RIGHT + p3[1]*UP

        print(self.func(2))

        slope_lines1, slope_lines2 = VMobject(), VMobject()
        slope_lines1.set_points_as_corners(
            [p1, interim_point1, p2]
        )
        slope_lines2.set_points_as_corners(
            [p3, interim_point2, p4]
        )
        slope_lines_group = VGroup(slope_lines1, slope_lines2)
        slope_lines_group.set_color(GREEN)

        slope_label1 = TextMobject("Slope $> 1$")
        slope_label2 = TextMobject("Slope $= 1$")
        slope_label1.next_to(slope_lines1)
        slope_label2.next_to(slope_lines2)

        data_points = [
            self.input_to_graph_point(x) + ((random.random()-0.5)/x)*UP
            for x in np.arange(1, 12, 0.7)
        ]
        data_dots = VGroup(*[
            Dot(point, radius = 0.05, color = YELLOW)
            for point in data_points
        ])

        self.play(ShowCreation(data_dots, run_time = 3))
        self.play(ShowCreation(self.graph))
        self.wait()
        self.play(
            ShowCreation(slope_lines1),
            Write(slope_label1)
        )
        self.wait()
        self.play(
            ShowCreation(slope_lines2),
            Write(slope_label2)
        )
        self.wait()

class SlopeAlwaysAboveOne(WhatSlopeDoesLogLogPlotApproach):
    CONFIG = {
        "words" : "Slope always $> 1$",
        "x_max" : 20,
    }

class ChangeWorldview(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            This changes how
            you see the world.
        """)
        self.change_student_modes(*["thinking"]*3)
        self.wait(3)

class CompareBritainAndNorway(Scene):
    def construct(self):
        norway = Norway(
            fill_opacity = 0,
            stroke_width = 2,
        )
        norway.to_corner(UP+RIGHT, buff = 0)
        fractalify(norway, order = 1, dimension = 1.5)
        anchors = list(norway.get_anchors())
        anchors.append(FRAME_X_RADIUS*RIGHT+FRAME_Y_RADIUS*UP)
        norway.set_points_as_corners(anchors)

        britain = Britain(
            fill_opacity = 0,
            stroke_width = 2
        )
        britain.shift(FRAME_X_RADIUS*LEFT/2)
        britain.to_edge(UP)
        fractalify(britain, order = 1, dimension = 1.21)

        britain_label = TextMobject("""
            Britain coast:
            1.21-dimensional
        """)
        norway_label = TextMobject("""
            Norway coast:
            1.52-dimensional
        """)
        britain_label.next_to(britain, DOWN)
        norway_label.next_to(britain_label, RIGHT, aligned_edge = DOWN)
        norway_label.to_edge(RIGHT)

        self.add(britain_label, norway_label)
        self.play(
            *list(map(ShowCreation, [norway, britain])),
            run_time = 3
        )
        self.wait()
        self.play(*it.chain(*[
            [
                mob.set_stroke, None, 0,
                mob.set_fill, BLUE, 1
            ]
            for mob in (britain, norway)
        ]))
        self.wait(2)

class CompareOceansLabels(Scene):
    def construct(self):
        label1 = TextMobject("Dimension $\\approx 2.05$")
        label2 = TextMobject("Dimension $\\approx 2.3$")

        label1.shift(FRAME_X_RADIUS*LEFT/2).to_edge(UP)
        label2.shift(FRAME_X_RADIUS*RIGHT/2).to_edge(UP)

        self.play(Write(label1))
        self.wait()
        self.play(Write(label2))
        self.wait()

class CompareOceans(Scene):
    def construct(self):
        pass

class FractalNonFractalFlowChart(Scene):
    def construct(self):
        is_fractal = TextMobject("Is it a \\\\ fractal?")
        nature = TextMobject("Probably from \\\\ nature")
        man_made = TextMobject("Probably \\\\ man-made")

        is_fractal.to_edge(UP)
        nature.shift(FRAME_X_RADIUS*LEFT/2)
        man_made.shift(FRAME_X_RADIUS*RIGHT/2)

        yes_arrow = Arrow(
            is_fractal.get_bottom(),
            nature.get_top()
        )
        no_arrow = Arrow(
            is_fractal.get_bottom(),
            man_made.get_top()
        )

        yes = TextMobject("Yes")
        no = TextMobject("No")
        yes.set_color(GREEN)
        no.set_color(RED)

        for word, arrow in (yes, yes_arrow), (no, no_arrow):
            word.next_to(ORIGIN, UP)
            word.rotate(arrow.get_angle())
            if word is yes:
                word.rotate(np.pi)
            word.shift(arrow.get_center())

        britain = Britain()
        britain.set_height(3)
        britain.to_corner(UP+LEFT)
        self.add(britain)

        randy = Randolph()
        randy.set_height(3)
        randy.to_corner(UP+RIGHT)
        self.add(randy)

        self.add(is_fractal)
        self.wait()
        for word, arrow, answer in (yes, yes_arrow, nature), (no, no_arrow, man_made):
            self.play(
                ShowCreation(arrow),
                Write(word, run_time = 1)
            )
            self.play(Write(answer, run_time = 1))
            if word is yes:
                self.wait()
            else:
                self.play(Blink(randy))

class ShowPiCreatureFractalCreation(FractalCreation):
    CONFIG = {
        "fractal_class" : PentagonalPiCreatureFractal,
        "max_order" : 4,
    }

class FractalPatreonThanks(PatreonThanks):
    CONFIG = {
        "specific_patrons" : [
            "Meshal  Alshammari",
            "Ali Yahya",
            "CrypticSwarm    ",
            "Yu  Jun",
            "Shelby  Doolittle",
            "Dave    Nicponski",
            "Damion  Kistler",
            "Juan    Batiz-Benet",
            "Othman  Alikhan",
            "Markus  Persson",
            "Dan Buchoff",
            "Derek   Dai",
            "Joseph  John Cox",
            "Luc Ritchie",
            "Jerry   Ling",
            "Mark    Govea",
            "Guido   Gambardella",
            "Vecht   ",
            "Jonathan Eppele",
            "Shimin Kuang",
            "Rish    Kundalia",
            "Achille Brighton",
            "Kirk    Werklund",
            "Ripta   Pasay",
            "Felipe  Diniz",
        ]
    }

class AffirmLogo(SVGMobject):
    CONFIG = {
        "fill_color" : "#0FA0EA",
        "fill_opacity" : 1,
        "stroke_color" : "#0FA0EA",
        "stroke_width" : 0,
        "file_name" : "affirm_logo",
        "width" : 3,
    }
    def __init__(self, **kwargs):
        SVGMobject.__init__(self, **kwargs)
        self.set_width(self.width)

class MortyLookingAtRectangle(Scene):
    def construct(self):
        morty = Mortimer()
        morty.to_corner(DOWN+RIGHT)
        url = TextMobject("affirmjobs.3b1b.co")
        url.to_corner(UP+LEFT)
        rect = Rectangle(height = 9, width = 16)
        rect.set_height(5)
        rect.next_to(url, DOWN)
        rect.shift_onto_screen()
        url.save_state()
        url.next_to(morty.get_corner(UP+LEFT), UP)

        affirm_logo = AffirmLogo()[0]
        affirm_logo.to_corner(UP+RIGHT, buff = MED_LARGE_BUFF)
        affirm_logo.shift(0.5*DOWN)

        self.add(morty)
        affirm_logo.save_state()
        affirm_logo.shift(DOWN)
        affirm_logo.set_fill(opacity = 0)
        self.play(
            ApplyMethod(affirm_logo.restore, run_time = 2),
            morty.look_at, affirm_logo,
        )
        self.play(
            morty.change_mode, "raise_right_hand",
            morty.look_at, url,
        )
        self.play(Write(url))
        self.play(Blink(morty))
        self.wait()
        self.play(
            url.restore,
            morty.change_mode, "happy"
        )
        self.play(ShowCreation(rect))
        self.wait()
        self.play(Blink(morty))
        for mode in ["wave_2", "hooray", "happy", "pondering", "happy"]:
            self.play(morty.change_mode, mode)
            self.wait(2)
            self.play(Blink(morty))
            self.wait(2)



class Thumbnail(Scene):
    def construct(self):
        title = TextMobject("1.5-dimensional")
        title.scale(2)
        title.to_edge(UP)


        koch_curve = QuadraticKoch(order = 6, monochromatic = True)
        koch_curve.set_stroke(width = 0)
        koch_curve.set_fill(BLUE)
        koch_curve.set_height(1.5*FRAME_Y_RADIUS)
        koch_curve.to_edge(DOWN, buff = SMALL_BUFF)

        self.add(koch_curve, title)
