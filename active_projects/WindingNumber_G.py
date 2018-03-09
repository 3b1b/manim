from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.compositions import *
from animation.playground import *
from animation.continual_animation import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from topics.objects import *
from topics.probability import *
from topics.complex_numbers import *
from scene import Scene
from scene.reconfigurable_scene import ReconfigurableScene
from scene.zoomed_scene import *
from camera import *
from mobject.svg_mobject import *
from mobject.tex_mobject import *
from topics.graph_scene import *

from active_projects.WindingNumber import *

class AltTeacherStudentsScene(TeacherStudentsScene):
    def setup(self):
        TeacherStudentsScene.setup(self)
        self.teacher.set_color(YELLOW_E)

###############


class IntroSceneWrapper(PiCreatureScene):
    CONFIG = {
        "default_pi_creature_kwargs" : {
            "color" : YELLOW_E,
            "flip_at_start" : False,
            "height" : 2,
        },
        "default_pi_creature_start_corner" : DOWN+LEFT,
    }
    def construct(self):
        self.introduce_two_words()
        self.describe_main_topic()
        self.describe_meta_topic()

    def introduce_two_words(self):
        morty = self.pi_creature
        rect = ScreenRectangle(height = 5)
        rect.to_corner(UP+RIGHT)
        self.add(rect)

        h_line = Line(LEFT, RIGHT).scale(2)
        h_line.to_corner(UP+LEFT)
        h_line.shift(0.5*DOWN)

        main_topic, meta_topic = topics = VGroup(
            TextMobject("Main topic"),
            TextMobject("Meta topic"),
        )
        topics.next_to(morty, UP)
        topics.shift_onto_screen()

        self.play(
            morty.change, "raise_left_hand",
            FadeInFromDown(main_topic)
        )
        self.wait()
        self.play(
            morty.change, "raise_right_hand",
            main_topic.next_to, meta_topic.get_top(), UP, MED_SMALL_BUFF,
            FadeInFromDown(meta_topic)
        )
        self.wait()
        self.play(
            morty.change, "happy",
            main_topic.next_to, h_line, UP,
            meta_topic.set_fill, {"opacity" : 0.2},
        )
        self.play(ShowCreation(h_line))
        self.wait()

        self.set_variables_as_attrs(h_line, main_topic, meta_topic)

    def describe_main_topic(self):
        h_line = self.h_line
        morty = self.pi_creature
        main_topic = self.main_topic
        meta_topic = self.meta_topic

        solver = TextMobject("2d equation solver")
        solver.match_width(h_line)
        solver.next_to(h_line, DOWN)
        rainbow_solver1 = solver.copy()
        rainbow_solver2 = solver.copy()
        colors = ["RED", "ORANGE", "YELLOW", "GREEN", BLUE, "PURPLE", PINK]
        rainbow_solver1.gradient_highlight(*colors)
        rainbow_solver2.gradient_highlight(*reversed(colors))


        xy_equation = TexMobject(
            "y", "e", "^x", "=\\sin(|", "x", "y", "|)"
        )
        xy_equation.highlight_by_tex_to_color_map({
            "x" : BLUE,
            "y" : YELLOW
        })
        xy_equation.next_to(solver, DOWN, MED_LARGE_BUFF)

        z_equation = TexMobject("z", "^5", "+", "z", "+", "1", "=", "0")
        z_equation.highlight_by_tex("z", GREEN)
        z_equation.move_to(xy_equation, UP)

        zeta = TexMobject("\\zeta(s) = 0")
        zeta[2].highlight(GREEN)
        zeta.next_to(z_equation, DOWN, MED_LARGE_BUFF)

        self.play(Write(solver))
        self.play(
            LaggedStart(FadeIn, xy_equation, run_time = 1),
            morty.change, "pondering"
        )
        self.wait(2)
        self.play(
            FadeOut(xy_equation),
            FadeIn(z_equation)
        )
        self.wait()
        self.play(Write(zeta))
        self.wait()
        solver.save_state()
        for rainbow_solver in rainbow_solver1, rainbow_solver2:
            self.play(Transform(
                solver, rainbow_solver,
                run_time = 2,
                submobject_mode = "lagged_start"
            ))
        self.play(solver.restore)
        self.wait()

        self.play(LaggedStart(
            FadeOut, VGroup(solver, z_equation, zeta)
        ))
        self.play(
            main_topic.move_to, meta_topic,
            main_topic.set_fill, {"opacity" : 0.2},
            meta_topic.move_to, main_topic,
            meta_topic.set_fill, {"opacity" : 1},
            morty.change, "hesitant",
            path_arc = TAU/8,
        )

    def describe_meta_topic(self):
        h_line = self.h_line
        morty = self.pi_creature

        words = TextMobject("Seek constructs which \\\\ compose nicely")
        words.scale(0.7)
        words.next_to(h_line, DOWN)

        self.play(Write(words))
        self.play(morty.change, "happy")
        self.wait(3)

class PiCreaturesAreIntrigued(AltTeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "You can extend \\\\ this to 2d",
            bubble_kwargs = {"width" : 4, "height" : 3}
        )
        self.change_student_modes("pondering", "confused", "erm")
        self.look_at(self.screen)
        self.wait(3)

class RewriteEquationWithTeacher(AltTeacherStudentsScene):
    def construct(self):
        equations = VGroup(
            TexMobject(
                "f(\\text{2d input})", "", "=", 
                "g(\\text{2d input})", ""
            ),
            TexMobject(
                "f(\\text{2d input})", "-", 
                "g(\\text{2d input})", "=", "0"
            ),
        )
        specific_equations = VGroup(
            TexMobject("x^2", "", "=", "2", ""),
            TexMobject("x^2", "-", "2", "=", "0"),
        )
        for equation in it.chain(equations, specific_equations):
            equation.sort_submobjects_alphabetically()
            for part in equation.get_parts_by_tex("text"):
                part[2:-1].highlight(YELLOW)
                part[2:-1].scale(0.9)
            equation.move_to(self.hold_up_spot, DOWN)

        self.teacher_holds_up(specific_equations[0])
        self.play(Transform(*specific_equations, path_arc = TAU/4))
        self.play(self.get_student_changes(*["pondering"]*3))
        self.play(FadeOut(specific_equations[0]), FadeIn(equations[0]))
        self.wait()
        self.play(Transform(*equations, path_arc = TAU/4))
        self.change_student_modes(*["happy"]*3)

        # 2d plane
        plane = NumberPlane(x_radius = 2.5, y_radius = 2.5)
        plane.scale(0.8)
        plane.to_corner(UP+LEFT)
        plane.add_coordinates()

        dot = Dot(color = YELLOW)
        label = TextMobject("Sign?")
        label.add_background_rectangle()
        label.scale(0.5)
        label.next_to(dot, UP, SMALL_BUFF)
        dot.add(label)
        dot.move_to(plane.coords_to_point(1, 1))
        dot.save_state()
        dot.fade(1)
        dot.center()

        question = TextMobject(
            "Wait...what would \\\\", "+", "and", "\\textminus", " \\, be in 2d?",
        )
        question.highlight_by_tex_to_color_map({
            "+" : "green", 
            "textminus" : "red"
        })

        self.student_says(
            question,
            target_mode = "sassy",
            student_index = 2,
            added_anims = [
                equations[0].to_corner, UP+RIGHT,
                self.teacher.change, "plain",
            ],
            bubble_kwargs = {"direction" : LEFT},
            run_time = 1,
        )
        self.play(
            Write(plane, run_time = 1),
            self.students[0].change, "confused",
            self.students[1].change, "confused",
        )
        self.play(dot.restore)
        for coords in (-1, 1), (1, -1), (0, -2), (-2, 1):
            self.wait(0.5)
            self.play(dot.move_to, plane.coords_to_point(*coords))
        self.wait()

class InputOutputScene(Scene):
    CONFIG = {
        "plane_width" : 6,
        "plane_height" : 6,
        "x_shift" : SPACE_WIDTH/2,
        "y_shift" : MED_LARGE_BUFF,
        "output_scalar" : 10,
        "non_renormalized_func" : plane_func_by_wind_spec(
            (-2, -1, 2), 
            (1, 1, 1), 
            (2, -2, -1),
        ),
    }
    def construct(self):
        input_coloring, output_coloring = self.get_colorings()
        input_plane, output_plane = self.get_planes()
        v_line = self.get_v_line()
        self.add(input_coloring, output_coloring, input_plane, output_plane)


        # Draw both planes, with curved arrow in between
        # 

    ###

    def func(self, coord_pair):
        out_coords = np.array(self.non_renormalized_func(coord_pair))
        out_norm = np.linalg.norm(out_coords)
        if out_norm > 0.01:
            angle = angle_of_vector(out_coords)
            factor = 0.5-0.1*np.cos(4*angle)
            target_norm = factor*np.log(out_norm)
            out_coords *= target_norm / out_norm
        return tuple(out_coords)

    def point_function(self, point):
        in_coords = self.input_plane.point_to_coords(point)
        out_coords = self.func(in_coords)
        return self.output_plane.coords_to_point(*out_coords)

    def get_colorings(self):
        in_cmos = ColorMappedObjectsScene(
            func = lambda p : self.non_renormalized_func(
                (p[0]+self.x_shift, p[1]+self.y_shift)
            )
        )
        scalar = self.output_scalar
        out_cmos = ColorMappedObjectsScene(
            func = lambda p : (
                scalar*(p[0]-self.x_shift), scalar*(p[1]+self.y_shift)
            )
        )

        input_coloring = Rectangle(
            height = self.plane_height,
            width = self.plane_width,
            stroke_width = 0,
            fill_color = WHITE,
            fill_opacity = 1,
        )
        output_coloring = input_coloring.copy()
        colorings = [input_coloring, output_coloring]
        vects = [LEFT, RIGHT]
        cmos_pair = [in_cmos, out_cmos]
        for coloring, vect, cmos in zip(colorings, vects, cmos_pair):
            coloring.move_to(self.x_shift*vect + self.y_shift*DOWN)
            coloring.color_using_background_image(cmos.background_image_file)
        return colorings

    def get_planes(self):
        input_plane = self.input_plane = NumberPlane(
            x_radius = self.plane_width/2.0,
            y_radius = self.plane_height/2.0,
        )
        output_plane = self.output_plane = input_plane.copy()
        planes = [input_plane, output_plane]
        vects = [LEFT, RIGHT]
        label_texts = ["Input", "Output"]
        label_colors = [GREEN, RED]
        for plane, vect, text, color in zip(planes, vects, label_texts, label_colors):
            plane.stretch_to_fit_width(self.plane_width)
            plane.add_coordinates(x_vals = range(-2, 3), y_vals = range(-2, 3))
            plane.white_parts = VGroup(plane.axes, plane.coordinate_labels)
            plane.lines_to_fade = VGroup(plane.main_lines, plane.secondary_lines)
            plane.move_to(vect*SPACE_WIDTH/2 + self.y_shift*DOWN)
            label = TextMobject(text)
            label.scale(1.5)
            label.add_background_rectangle()
            label.move_to(plane)
            label.to_edge(UP, buff = MED_SMALL_BUFF)
            plane.add(label)
            plane.label = label
            for submob in plane.submobject_family():
                if isinstance(submob, TexMobject) and hasattr(submob, "background_rectangle"):
                    submob.remove(submob.background_rectangle)

        return planes

    def get_v_line(self):
        v_line = Line(UP, DOWN).scale(SPACE_HEIGHT)
        v_line.set_stroke(WHITE, 5)
        return v_line

    def get_dots(self, input_plane, output_plane):
        step = self.dot_density
        x_min = -3.0
        x_max = 3.0
        y_min = -3.0
        y_max = 3.0
        dots = VGroup()
        for x in np.arange(x_min, x_max + step, step):
            for y in np.arange(y_max, y_min - step, -step):
                out_coords = self.func((x, y))
                dot = Dot(radius = self.dot_radius)
                dot.set_stroke(BLACK, 1)
                dot.move_to(input_plane.coords_to_point(x, y))
                dot.original_position = dot.get_center()
                dot.generate_target()
                dot.target.move_to(output_plane.coords_to_point(*out_coords))
                dot.target_color = rgba_to_color(point_to_rgba(
                    tuple(self.output_scalar*np.array(out_coords))
                ))
                dots.add(dot)
        return dots


class TwoDScreenInOurThreeDWorld(AltTeacherStudentsScene, ThreeDScene):
    def construct(self):
        self.ask_about_2d_functions()
        self.show_3d()

    def ask_about_2d_functions(self):
        in_plane = NumberPlane(x_radius = 2.5, y_radius = 2.5)
        in_plane.add_coordinates()
        in_plane.scale_to_fit_height(3)
        out_plane = in_plane.copy()

        in_text = TextMobject("Input space")
        out_text = TextMobject("Output space")
        VGroup(in_text, out_text).scale(0.75)
        in_text.next_to(in_plane, UP, SMALL_BUFF)
        out_text.next_to(out_plane, UP, SMALL_BUFF)
        in_plane.add(in_text)
        out_plane.add(out_text)

        arrow = CurvedArrow(RIGHT, LEFT, angle = TAU/4)
        arrow.pointwise_become_partial(arrow, 0.05, 1.0)
        group = VGroup(in_plane, arrow, out_plane)
        group.arrange_submobjects(RIGHT)
        arrow.shift(UP)
        group.move_to(self.students)
        group.to_edge(UP)

        dots = VGroup()
        dots_target = VGroup()
        for x in np.arange(-2.5, 3.0, 0.5):
            for y in np.arange(-2.5, 3.0, 0.5):
                dot = Dot(radius = 0.05)
                dot.move_to(in_plane.coords_to_point(x, y))
                dot.generate_target()
                dot.target.move_to(out_plane.coords_to_point(
                    x + 0.25*np.cos(5*y), y + 0.25*np.sin(3*x)
                ))
                dots.add(dot)
                dots_target.add(dot.target)
        dots.gradient_highlight(YELLOW, RED)
        dots_target.gradient_highlight(YELLOW, RED)

        self.play(
            self.teacher.change, "raise_right_hand",
            Write(in_plane, run_time = 1)
        )
        self.play(
            ShowCreation(arrow),
            ReplacementTransform(
                in_plane.copy(), out_plane,
                path_arc = -TAU/4,
            )
        )
        self.play(
            LaggedStart(GrowFromCenter, dots, run_time = 1),
            self.get_student_changes(*3*["erm"]),
        )
        self.play(LaggedStart(MoveToTarget, dots, path_arc = -TAU/4))
        self.wait(3)


    def show_3d(self):
        laptop = Laptop().scale(2)
        laptop.rotate(-TAU/12, DOWN)
        laptop.rotate(-5*TAU/24, LEFT)
        laptop.rotate(TAU/8, LEFT)
        laptop.scale(2.3*SPACE_WIDTH/laptop.screen_plate.get_width())
        laptop.shift(-laptop.screen_plate.get_center() + 0.1*IN)
        should_shade_in_3d(laptop)

        everything = VGroup(laptop, *self.mobjects)
        everything.generate_target()
        # for mob in everything.target.submobject_family():
        #     if isinstance(mob, PiCreature):
        #         mob.change_mode("confused")
        everything.target.rotate(TAU/12, LEFT)
        everything.target.rotate(TAU/16, UP)
        everything.target.shift(4*UP)

        self.move_camera(
            distance = 12,
            run_time = 4,
            added_anims = [MoveToTarget(everything, run_time = 4)],
        )
        self.add(AmbientRotation(everything, axis = UP, rate = 3*DEGREES))
        self.wait(10)

class DotsHoppingToColor(InputOutputScene):
    CONFIG = {
        "dot_radius" : 0.05,
        "dot_density" : 0.25,
    }
    def construct(self):
        input_coloring, output_coloring = self.get_colorings()
        input_plane, output_plane = self.get_planes()
        v_line = self.get_v_line()

        dots = self.get_dots(input_plane, output_plane)

        right_half_block = Rectangle(
            height = 2*SPACE_HEIGHT,
            width = SPACE_WIDTH - SMALL_BUFF,
            stroke_width = 0,
            fill_color = BLACK,
            fill_opacity = 0.8,
        )
        right_half_block.to_edge(RIGHT, buff = 0)

        #Introduce parts
        self.add(input_plane, output_plane, v_line)
        self.play(
            FadeIn(output_coloring), 
            Animation(output_plane),
            output_plane.white_parts.highlight, BLACK,
            output_plane.lines_to_fade.set_stroke, {"width" : 0},
        )
        self.wait()
        self.play(LaggedStart(GrowFromCenter, dots, run_time = 3))
        self.wait()

        #Hop over and back
        self.play(LaggedStart(
            MoveToTarget, dots, 
            path_arc = -TAU/4,
            run_time = 3,
        ))
        self.wait()
        self.play(LaggedStart(
            ApplyMethod, dots,
            lambda d : (d.set_fill, d.target_color),
        ))
        self.wait()
        self.play(LaggedStart(
            ApplyMethod, dots,
            lambda d : (d.move_to, d.original_position),
            path_arc = TAU/4,
            run_time = 3,
        ))
        self.wait()
        self.play(
            FadeIn(input_coloring),
            Animation(input_plane),
            input_plane.white_parts.highlight, BLACK,
            input_plane.lines_to_fade.set_stroke, {"width" : 0},
            FadeOut(dots),
        )
        self.wait()

        #Cover output half
        right_half_block.save_state()
        right_half_block.next_to(SPACE_WIDTH*RIGHT, RIGHT)
        self.play(right_half_block.restore)
        self.wait()

        # Show yellow points
        inspector = DashedLine(
            ORIGIN, TAU*UP,
            dashed_segment_length = TAU/24,
            fill_opacity = 0,
            stroke_width = 3,
            stroke_color = WHITE,
        )
        inspector.add(*inspector.copy().highlight(BLACK).shift((TAU/24)*UP))
        inspector.apply_complex_function(np.exp)
        inspector.scale(0.15)

        inspector_image = inspector.copy()
        def update_inspector_image(inspector_image):
            inspector_image.move_to(self.point_function(inspector.get_center()))

        inspector_image_update_anim = UpdateFromFunc(
            inspector_image, update_inspector_image
        )
        pink_points_label = TextMobject("Pink points")
        pink_points_label.scale(0.7)
        pink_points_label.highlight(BLACK)

        self.play(
            inspector.move_to, input_plane.coords_to_point(-2.75, 2.75),
            inspector.set_stroke, {"width" : 2},
        )
        pink_points_label.next_to(inspector, RIGHT)
        self.play(
            Rotating(
                inspector, about_point = inspector.get_center(),
                rate_func = smooth,
                run_time = 2,
            ),
            Write(pink_points_label)
        )
        self.wait()
        self.play(right_half_block.next_to, SPACE_WIDTH*RIGHT, RIGHT)
        inspector_image_update_anim.update(0)
        self.play(ReplacementTransform(
            inspector.copy(), inspector_image,
            path_arc = -TAU/4,
        ))
        self.play(
            ApplyMethod(
                inspector.move_to, 
                input_plane.coords_to_point(-2, 0),
                path_arc = -TAU/8,
                run_time = 3,
            ),
            inspector_image_update_anim
        )
        self.play(
            ApplyMethod(
                inspector.move_to, 
                input_plane.coords_to_point(-2.75, 2.75),
                path_arc = TAU/8,
                run_time = 3,
            ),
            inspector_image_update_anim
        )
        self.play(FadeOut(pink_points_label))

        # Show black zero
        zeros = tuple(it.starmap(input_plane.coords_to_point, [
            (-2, -1), (1, 2), (2, -2),
        ]))
        for x in range(2):
            for zero in zeros:
                self.play(
                    ApplyMethod(
                        inspector.move_to, zero,
                        path_arc = -TAU/8,
                        run_time = 2,
                    ),
                    inspector_image_update_anim,
                )
                self.wait()
        self.play(FadeOut(VGroup(inspector, inspector_image)))

        # Show all dots and slowly fade them out
        for dot in dots:
            dot.scale(1.5)
        self.play(
            FadeOut(input_coloring),
            input_plane.white_parts.highlight, WHITE,
            LaggedStart(GrowFromCenter, dots)
        )
        self.wait()
        random.shuffle(dots.submobjects)
        self.play(LaggedStart(
            FadeOut, dots,
            lag_ratio = 0.05,
            run_time = 10,
        ))

        # Ask about whether a region contains a zero
        question = TextMobject("Does this region \\\\ contain a zero?")
        question.add_background_rectangle(opacity = 1)
        question.next_to(input_plane.label, DOWN)
        square = Square()
        square.match_background_image_file(input_coloring)
        square.move_to(input_plane)

        self.play(ShowCreation(square), Write(question))
        self.wait()
        quads = [
            (0, 0.5, 6, 6.25),
            (1, 1, 0.5, 2),
            (-1, -1, 3, 4.5),
            (0, 1.25, 5, 1.7),
            (-2, -1, 1, 1),
        ]
        for x, y, width, height in quads:
            self.play(
                square.stretch_to_fit_width, width,
                square.stretch_to_fit_height, height,
                square.move_to, input_plane.coords_to_point(x, y)
            )
            self.wait()

class SoWeFoundTheZeros(AltTeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Aha! So we \\\\ found the solutions!",
            target_mode = "hooray",
            student_index = 2,
            bubble_kwargs = {"direction" : LEFT},
        )
        self.wait()
        self.teacher_says(
            "Er...only \\\\ kind of",
            target_mode = "hesitant"
        )
        self.wait(3)

class PiCreatureAsksWhatWentWrong(PiCreatureScene):
    def construct(self):
        randy = self.pi_creature
        randy.set_color(YELLOW_E)
        randy.flip()
        randy.to_corner(DOWN+LEFT)
        question = TextMobject("What went wrong?")
        question.next_to(randy, UP)
        question.shift_onto_screen()
        question.save_state()
        question.shift(DOWN).fade(1)

        self.play(randy.change, "erm")
        self.wait(2)
        self.play(
            Animation(VectorizedPoint(ORIGIN)),
            question.restore,
            randy.change, "confused",
        )
        self.wait(5)

class ForeverNarrowingLoop(InputOutputScene):
    def construct(self):
        input_coloring, output_coloring = colorings = VGroup(*self.get_colorings())
        input_plane, output_plane = planes = VGroup(*self.get_planes())
        for plane in planes:
            plane.white_parts.highlight(BLACK)
            plane.lines_to_fade.set_stroke(width = 0)

        v_line = Line(UP, DOWN).scale(SPACE_HEIGHT)
        v_line.set_stroke(WHITE, 5)

        self.add(colorings, v_line, planes)
        self.play(*it.chain(
            [
                ApplyMethod(coloring.set_fill, {"opacity" : 0.2})
                for coloring in colorings
            ],
            [
                ApplyMethod(plane.white_parts.highlight, WHITE)
                for plane in planes
            ]
        ), run_time = 2)

        # circle
        circle = Circle(color = WHITE, radius = 2.25)
        circle.flip(axis = RIGHT)
        circle.insert_n_anchor_points(50)
        circle.next_to(input_coloring.get_corner(UP+RIGHT), DOWN+LEFT, SMALL_BUFF)
        circle.set_stroke(width = 5)
        circle_image = circle.copy()
        circle.match_background_image_file(input_coloring)
        circle_image.match_background_image_file(output_coloring)

        def update_circle_image(circle_image):
            circle_image.points = circle.points
            circle_image.apply_function(self.point_function)
            circle_image.make_smooth()

        circle_image_update_anim = UpdateFromFunc(
            circle_image, update_circle_image
        )

        self.play(
            ShowCreation(circle),
            ShowCreation(circle_image),
            run_time = 3,
            rate_func = bezier([0, 0, 1, 1])
        )
        # self.play(
        #     ReplacementTransform(
        #         circle.copy(), 
        #         circle_image.copy().match_background_image_file(
        #             input_coloring
        #         ).set_stroke(width = 0)
        #     ),
        #     ReplacementTransform(
        #         circle.copy().match_background_image_file(
        #             output_coloring
        #         ).set_stroke(width = 0), 
        #         circle_image
        #     ),
        #     run_time = 2
        # )
        self.play(
            circle.scale, 0.015,
            circle.move_to, input_plane.coords_to_point(1, 1),
            circle_image_update_anim,
            run_time = 20,
            rate_func = bezier([0, 0, 1, 1])
        )

class FailureOfComposition(ColorMappedObjectsScene):
    CONFIG = {
        "func" : lambda p : (
            np.cos(TAU*p[1]/3.5), 
            np.sin(TAU*p[1]/3.5)
        )
    }
    def construct(self):
        ColorMappedObjectsScene.construct(self)

        big_square = Square(side_length = 4)
        big_square.move_to(ORIGIN, RIGHT)
        small_squares = VGroup(*[
            Square(side_length = 2) for x in range(2)
        ])
        small_squares.match_width(big_square, stretch = True)
        small_squares.arrange_submobjects(DOWN, buff = 0)
        small_squares.move_to(big_square)
        small_squares.space_out_submobjects(1.1)
        all_squares = VGroup(big_square, *small_squares)
        all_squares.set_stroke(width = 6)

        for square in all_squares:
            square.highlight(WHITE)
            square.color_using_background_image(self.background_image_file)

        question = TextMobject("Does my border go through every color?")
        question.to_edge(UP)
        no_answers = VGroup()
        yes_answers = VGroup()
        for square in all_squares:
            if square is big_square:
                square.answer = TextMobject("Yes")
                square.answer.highlight(GREEN)
                yes_answers.add(square.answer)
            else:
                square.answer = TextMobject("No")
                square.answer.highlight(RED)
                no_answers.add(square.answer)
            square.answer.move_to(square)

        no_answers_in_equation = no_answers.copy()
        yes_answers_in_equation = yes_answers.copy()
        plus, equals = plus_equals = TexMobject("+=")
        equation = VGroup(
            no_answers_in_equation[0], plus,
            no_answers_in_equation[1], equals,
            yes_answers_in_equation
        )
        equation.arrange_submobjects(RIGHT, buff = SMALL_BUFF)
        equation.next_to(big_square, RIGHT, MED_LARGE_BUFF)
        q_marks = TexMobject("???")
        q_marks.next_to(equals, UP)


        self.add(question)
        self.play(LaggedStart(ShowCreation, small_squares, lag_ratio = 0.8))
        self.play(LaggedStart(Write, no_answers))
        self.wait()
        self.play(
            small_squares.arrange_submobjects, DOWN, {"buff" : 0},
            small_squares.move_to, big_square,
            no_answers.space_out_submobjects, 0.9,
        )
        self.add(big_square)
        no_answers_copy = no_answers.copy()
        small_squares.save_state()
        self.play(
            Transform(no_answers, no_answers_in_equation),
            Write(plus_equals),
            small_squares.set_stroke, {"width" : 0},
        )
        self.play(
            Write(yes_answers),
            Write(yes_answers_in_equation),
        )
        self.play(LaggedStart(FadeIn, q_marks, run_time = 1, lag_ratio = 0.8))
        self.wait(2)
        self.play(
            small_squares.restore,
            FadeOut(yes_answers),
            FadeIn(no_answers_copy),
        )
        self.wait()
        self.play(
            small_squares.set_stroke, {"width" : 0},
            FadeOut(no_answers_copy),
            FadeIn(yes_answers),
        )
        self.wait()

        # We can find a better notion of what we want

        cross = Cross(question)

        self.play(
            ShowCreation(cross, run_time = 2),
            FadeOut(equation),
            FadeOut(no_answers),
            FadeOut(q_marks),
            FadeOut(yes_answers),
        )

        x, plus, y = x_plus_y = TexMobject("x+y")
        x_plus_y.move_to(big_square)
        x_plus_y.save_state()
        x.move_to(no_answers_copy[0])
        y.move_to(no_answers_copy[1])
        plus.fade(1)

        for square, char in zip(small_squares, [x, y]):
            ghost = square.copy()
            ghost.set_stroke(width = 5)
            ghost.background_image_file = None
            self.play(
                small_squares.restore,
                ShowPassingFlash(ghost),
                Write(char)
            )
        self.wait()
        ghost = big_square.copy()
        ghost.background_image_file = None
        self.play(
            small_squares.set_stroke, {"width" : 0},
            x_plus_y.restore,
        )
        self.play(ShowPassingFlash(ghost))
        self.wait()










































