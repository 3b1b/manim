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
from topics.objects import *
from scene import Scene
from scene.zoomed_scene import ZoomedScene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

from eoc.chapter1 import OpeningQuote, PatreonThanks
from eoc.chapter2 import DISTANCE_COLOR, TIME_COLOR, VELOCITY_COLOR
from eoc.graph_scene import *

OUTPUT_COLOR = DISTANCE_COLOR
INPUT_COLOR = TIME_COLOR
DERIVATIVE_COLOR = VELOCITY_COLOR

class Chapter3OpeningQuote(OpeningQuote):
    CONFIG = {
        "quote" : [
            "You know, for a mathematician, he did not have \\\\ enough",
            "imagination.", 
            "But he has become a poet and \\\\ now he is fine.",
        ],
        "highlighted_quote_terms" : {
            "imagination." : BLUE,
        },
        "author" : "David Hilbert"
    }








class DerivativeOfXSquaredAsGraph(GraphScene, ZoomedScene, PiCreatureScene):
    CONFIG = {
        "start_x" : 2,
        "big_x" : 3,
        "dx" : 0.1,
        "x_min" : -9,
        "x_labeled_nums" : range(-8, 0, 2) + range(2, 10, 2),
        "y_labeled_nums" : range(2, 12, 2),
        "little_rect_nudge" : 0.5*(1.5*UP+RIGHT),
        "graph_origin" : 2.5*DOWN + LEFT,
        "zoomed_canvas_corner" : UP+LEFT,
    }
    def construct(self):
        self.draw_graph()
        self.ask_about_df_dx()
        self.show_differing_slopes()
        self.mention_alternate_view()

    def draw_graph(self):
        self.setup_axes()
        graph = self.get_graph(lambda x : x**2)
        label = self.get_graph_label(
            graph, "f(x) = x^2",
        )
        self.play(ShowCreation(graph))
        self.play(Write(label))
        self.dither()
        self.graph = graph

    def ask_about_df_dx(self):
        ss_group = self.get_secant_slope_group(
            self.start_x, self.graph,
            dx = self.dx,
            dx_label = "dx",
            df_label = "df",
        )
        secant_line = ss_group.secant_line
        ss_group.remove(secant_line)

        v_line, nudged_v_line = [
            self.get_vertical_line_to_graph(
                x, self.graph,
                line_class = DashedLine,
                color = RED,
                dashed_segment_length = 0.025
            )
            for x in self.start_x, self.start_x+self.dx
        ]

        df_dx = TexMobject("\\frac{df}{dx} ?")
        VGroup(*df_dx[:2]).highlight(ss_group.df_line.get_color())
        VGroup(*df_dx[3:5]).highlight(ss_group.dx_line.get_color())
        df_dx.next_to(
            self.input_to_graph_point(self.start_x, self.graph),
            DOWN+RIGHT,
            buff = MED_SMALL_BUFF
        )

        self.play(ShowCreation(v_line))
        self.dither()
        self.play(Transform(v_line.copy(), nudged_v_line))
        self.remove(self.get_mobjects_from_last_animation()[0])
        self.add(nudged_v_line)
        self.dither()
        self.activate_zooming()
        self.little_rectangle.replace(self.big_rectangle)
        self.play(
            FadeIn(self.little_rectangle),
            FadeIn(self.big_rectangle),
        )
        self.play(
            ApplyFunction(
                lambda r : self.position_little_rectangle(r, ss_group),
                self.little_rectangle
            ),
            self.pi_creature.change_mode, "pondering",
            self.pi_creature.look_at, ss_group
        )
        self.play(
            ShowCreation(ss_group.dx_line),
            Write(ss_group.dx_label),
        )
        self.dither()
        self.play(
            ShowCreation(ss_group.df_line),
            Write(ss_group.df_label),
        )
        self.dither()
        self.play(Write(df_dx))
        self.dither()
        self.play(*map(FadeOut, [
            v_line, nudged_v_line,
        ]))
        self.ss_group = ss_group

    def position_little_rectangle(self, rect, ss_group):
        rect.scale_to_fit_width(3*self.dx)
        rect.move_to(
            ss_group.dx_line.get_left()
        )
        rect.shift(
            self.dx*self.little_rect_nudge
        )
        return rect

    def show_differing_slopes(self):
        ss_group = self.ss_group
        def rect_update(rect):
            self.position_little_rectangle(rect, ss_group)

        self.play(
            ShowCreation(ss_group.secant_line),
            self.pi_creature.change_mode, "thinking"
        )
        ss_group.add(ss_group.secant_line)
        self.dither()
        for target_x in self.big_x, -self.dx/2, 1, 2:
            self.animate_secant_slope_group_change(
                ss_group, target_x = target_x,
                added_anims = [
                    UpdateFromFunc(self.little_rectangle, rect_update)
                ]
            )
            self.dither()

    def mention_alternate_view(self):
        self.remove(self.pi_creature)
        everything = VGroup(*self.get_mobjects())
        self.add(self.pi_creature)
        self.disactivate_zooming()
        self.play(
            ApplyMethod(
                everything.shift, 2*SPACE_WIDTH*LEFT,
                rate_func = lambda t : running_start(t, -0.1)
            ),
            self.pi_creature.change_mode, "happy"
        )
        self.say("Let's try \\\\ another view.", target_mode = "speaking")
        self.dither(2)

class NudgeSideLengthOfSquare(PiCreatureScene):
    CONFIG = {
        "square_width" : 3,
        "alt_square_width" : 5,
        "dx" : 0.25,
        "alt_dx" : 0.01,
        "square_color" : GREEN,
        "square_fill_opacity" : 0.75,
        "three_color" : GREEN,
        "dx_color" : BLUE_B,
        "is_recursing_on_dx" : False,
        "is_recursing_on_square_width" : False,
    }
    def construct(self):
        ApplyMethod(self.pi_creature.change_mode, "speaking").update(1)
        self.add_function_label()
        self.introduce_square()
        self.increase_area()
        self.write_df_equation()
        self.highlight_shapes()
        self.examine_thin_rectangles()
        self.examine_tiny_square()
        self.show_smaller_dx()
        self.rule_of_thumb()
        self.write_out_derivative()

    def add_function_label(self):
        label = TexMobject("f(x) = x^2")
        label.next_to(ORIGIN, RIGHT, buff = (self.square_width-3)/2.)
        label.to_edge(UP)
        self.add(label)
        self.function_label = label

    def introduce_square(self):
        square = Square(
            side_length = self.square_width,
            stroke_width = 0,
            fill_opacity = self.square_fill_opacity,
            fill_color = self.square_color,
        )
        square.to_corner(UP+LEFT, buff = LARGE_BUFF)
        x_squared = TexMobject("x^2")
        x_squared.move_to(square)

        braces = VGroup()
        for vect in RIGHT, DOWN:
            brace = Brace(square, vect)
            text = brace.get_text("$x$")
            brace.add(text)
            braces.add(brace)

        self.play(
            DrawBorderThenFill(square),
            self.pi_creature.change_mode, "plain"
        )
        self.play(*map(GrowFromCenter, braces))
        self.play(Write(x_squared))
        self.change_mode("pondering")
        self.dither()

        self.square = square
        self.side_braces = braces

    def increase_area(self):
        color_kwargs = {
            "fill_color" : YELLOW,
            "fill_opacity" : self.square_fill_opacity,
            "stroke_width" : 0,
        }
        right_rect = Rectangle(
            width = self.dx,
            height = self.square_width,
            **color_kwargs
        )
        bottom_rect = right_rect.copy().rotate(-np.pi/2)
        right_rect.next_to(self.square, RIGHT, buff = 0)
        bottom_rect.next_to(self.square, DOWN, buff = 0)
        corner_square = Square(
            side_length = self.dx,
            **color_kwargs
        )
        corner_square.next_to(self.square, DOWN+RIGHT, buff = 0)

        right_line = Line(
            self.square.get_corner(UP+RIGHT),
            self.square.get_corner(DOWN+RIGHT),
            stroke_width = 0
        )
        bottom_line = Line(
            self.square.get_corner(DOWN+RIGHT),
            self.square.get_corner(DOWN+LEFT),
            stroke_width = 0
        )
        corner_point = VectorizedPoint(
            self.square.get_corner(DOWN+RIGHT)
        )

        little_braces = VGroup()
        for vect in RIGHT, DOWN:
            brace = Brace(
                corner_square, vect, 
                buff = SMALL_BUFF,
                tex_string = "\\underbrace{%s}"%(3*"\\quad"),
            )
            text = brace.get_text("$dx$", buff = SMALL_BUFF)
            text.highlight(self.dx_color)
            brace.add(text)
            little_braces.add(brace)

        right_brace, bottom_brace = self.side_braces
        self.play(
            Transform(right_line, right_rect),
            Transform(bottom_line, bottom_rect),
            Transform(corner_point, corner_square),
            right_brace.next_to, right_rect, RIGHT, SMALL_BUFF,
            bottom_brace.next_to, bottom_rect, DOWN, SMALL_BUFF,
        )
        self.remove(corner_point, bottom_line, right_line)
        self.add(corner_square, bottom_rect, right_rect)
        self.play(*map(GrowFromCenter, little_braces))
        self.dither()
        self.play(*it.chain(*[
            [mob.shift, vect*SMALL_BUFF]
            for mob, vect in [
                (right_rect, RIGHT),
                (bottom_rect, DOWN),
                (corner_square, DOWN+RIGHT),
                (right_brace, RIGHT),
                (bottom_brace, DOWN),
                (little_braces, DOWN+RIGHT)
            ]
        ]))
        self.change_mode("thinking")
        self.dither()
        self.right_rect = right_rect
        self.bottom_rect = bottom_rect
        self.corner_square = corner_square
        self.little_braces = little_braces

    def write_df_equation(self):
        right_rect = self.right_rect
        bottom_rect = self.bottom_rect
        corner_square = self.corner_square

        df_equation = VGroup(
            TexMobject("df").highlight(right_rect.get_color()),
            TexMobject("="),
            right_rect.copy(),
            TextMobject("+"),
            right_rect.copy(),
            TexMobject("+"),
            corner_square.copy()
        )
        df_equation.arrange_submobjects()
        df_equation.next_to(
            self.function_label, DOWN, 
            aligned_edge = LEFT,
            buff = SMALL_BUFF
        )
        df, equals, r1, plus1, r2, plus2, s = df_equation

        pairs = [
            (df, self.function_label[0]),
            (r1, right_rect), 
            (r2, bottom_rect), 
            (s, corner_square),
        ]
        for mover, origin in pairs:
            mover.save_state()
            Transform(mover, origin).update(1)
        self.play(df.restore)
        self.dither()
        self.play(
            *[
                mob.restore
                for mob in r1, r2, s
            ]+[
                Write(symbol)
                for symbol in equals, plus1, plus2
            ], 
            run_time = 2
        )
        self.change_mode("happy")
        self.dither()

        self.df_equation = df_equation

    def highlight_shapes(self):
        df, equals, r1, plus1, r2, plus2, s = self.df_equation

        tups = [
            (self.right_rect, self.bottom_rect, r1, r2),
            (self.corner_square, s)
        ]
        for tup in tups:
            self.play(
                *it.chain(*[
                    [m.scale_in_place, 1.2, m.highlight, RED]
                    for m in tup
                ]), 
                rate_func = there_and_back
            )
            self.dither()

    def examine_thin_rectangles(self):
        df, equals, r1, plus1, r2, plus2, s = self.df_equation

        rects = VGroup(r1, r2)
        thin_rect_brace = Brace(rects, DOWN)
        text = thin_rect_brace.get_text("$2x \\, dx$")
        VGroup(*text[-2:]).highlight(self.dx_color)
        text.save_state()
        alt_text = thin_rect_brace.get_text("$2(3)(0.01)$")
        alt_text[2].highlight(self.three_color)
        VGroup(*alt_text[-5:-1]).highlight(self.dx_color)

        example_value = TexMobject("=0.06")
        example_value.next_to(alt_text, DOWN)

        self.play(GrowFromCenter(thin_rect_brace))
        self.play(
            Write(text),
            self.pi_creature.change_mode, "pondering"
        )
        self.dither()

        xs = VGroup(*[
            brace[-1] 
            for brace in self.side_braces
        ])
        dxs = VGroup(*[
            brace[-1]
            for brace in self.little_braces
        ])
        for group, tex, color in (xs, "3", self.three_color), (dxs, "0.01", self.dx_color):
            group.save_state()            
            group.generate_target()            
            for submob in group.target:
                number = TexMobject(tex)
                number.highlight(color)
                number.move_to(submob, LEFT)
                Transform(submob, number).update(1)
        self.play(MoveToTarget(xs))
        self.play(MoveToTarget(dxs))
        self.dither()
        self.play(Transform(text, alt_text))
        self.dither()
        self.play(Write(example_value))
        self.dither()
        self.play(
            FadeOut(example_value),
            *[
                mob.restore
                for mob in xs, dxs, text
            ]
        )
        self.remove(text)
        text.restore()
        self.add(text)

        self.dither()
        self.dxs = dxs
        self.thin_rect_brace = thin_rect_brace
        self.thin_rect_area = text        

    def examine_tiny_square(self):
        text = TexMobject("dx^2")
        VGroup(*text[:2]).highlight(self.dx_color)
        text.next_to(self.df_equation[-1], UP)
        text.save_state()
        alt_text = TextMobject("0.0001")
        alt_text.move_to(text)

        self.play(Write(text))
        self.change_mode("surprised")
        self.dither()
        self.play(
            MoveToTarget(self.dxs),
            self.pi_creature.change_mode, "plain"
        )
        for submob in self.dxs.target:
            number = TexMobject("0.01")
            number.highlight(self.dx_color)
            number.move_to(submob, LEFT)
            Transform(submob, number).update(1)
        self.play(MoveToTarget(self.dxs))
        self.play(
            Transform(text, alt_text),
            self.pi_creature.change_mode, "raise_right_hand"
        )
        self.dither(2)
        self.play(*[
            mob.restore
            for mob in self.dxs, text
        ] + [
            self.pi_creature.change_mode, "erm"
        ])
        self.dx_squared = text

    def show_smaller_dx(self):
        self.mobjects_at_start_of_show_smaller_dx = [
            mob.copy() for mob in self.get_mobjects()
        ]
        if self.is_recursing_on_dx:
            return

        alt_scene = self.__class__(
            skip_animations = True,
            dx = self.alt_dx,
            is_recursing_on_dx = True
        )
        for mob in self.get_mobjects():
            mob.save_state()
        self.play(*[
            Transform(*pair)
            for pair in zip(
                self.get_mobjects(),
                alt_scene.mobjects_at_start_of_show_smaller_dx,
            )
        ])
        self.dither()
        self.play(*[
            mob.restore
            for mob in self.get_mobjects()
        ])
        self.change_mode("happy")
        self.dither()

    def rule_of_thumb(self):
        circle = Circle(color = RED)
        dx_squared_group = VGroup(self.dx_squared, self.df_equation[-1])
        circle.replace(dx_squared_group, stretch = True)
        dx_squared_group.add(self.df_equation[-2])
        circle.scale_in_place(1.5)
        safe_to_ignore = TextMobject("Safe to ignore")
        safe_to_ignore.next_to(circle, DOWN, aligned_edge = LEFT)
        safe_to_ignore.highlight(circle.get_color())

        self.play(ShowCreation(circle))
        self.play(
            Write(safe_to_ignore, run_time = 2),
            self.pi_creature.change_mode, "raise_right_hand"
        )
        self.play(
            FadeOut(circle),
            FadeOut(safe_to_ignore),
            dx_squared_group.fade, 0.5,
            dx_squared_group.to_corner, UP+RIGHT,
            self.pi_creature.change_mode, "plain"
        )
        self.dither()

    def write_out_derivative(self):
        df, equals, r1, plus1, r2, plus2, s = self.df_equation
        frac_line = TexMobject("-")
        frac_line.stretch_to_fit_width(df.get_width())
        frac_line.move_to(df)
        dx = VGroup(*self.thin_rect_area[-2:]) 
        x = self.thin_rect_area[1]

        self.play(
            Transform(r1, self.right_rect),
            Transform(r2, self.bottom_rect),
            FadeOut(plus1),
            FadeOut(self.thin_rect_brace)
        )
        self.play(
            self.thin_rect_area.next_to, VGroup(df, equals),
            RIGHT, MED_SMALL_BUFF, UP,
            self.pi_creature.change_mode, "thinking"
        )
        self.dither(2)
        self.play(
            ApplyMethod(df.next_to, frac_line, UP, SMALL_BUFF),
            ApplyMethod(dx.next_to, frac_line, DOWN, SMALL_BUFF),
            Write(frac_line),            
            path_arc = -np.pi
        )
        self.dither()

        brace_xs = [
            brace[-1]
            for brace in self.side_braces
        ]
        xs = list(brace_xs) + [x]
        for x_mob in xs:
            number = TexMobject("(%d)"%self.square_width)
            number.move_to(x_mob, LEFT)
            number.shift(
                (x_mob.get_bottom()[1] - number[1].get_bottom()[1])*UP
            )
            x_mob.save_state()
            x_mob.target = number
        self.play(*map(MoveToTarget, xs))
        self.dither(2)

        #Recursively transform to what would have happened
        #with a wider square width
        self.mobjects_at_end_of_write_out_derivative = self.get_mobjects()
        if self.is_recursing_on_square_width or self.is_recursing_on_dx:
            return
        alt_scene = self.__class__(
            skip_animations = True,
            square_width = self.alt_square_width,
            is_recursing_on_square_width = True,
        )
        self.play(*[
            Transform(*pair)
            for pair in zip(
                self.mobjects_at_end_of_write_out_derivative,
                alt_scene.mobjects_at_end_of_write_out_derivative
            )
        ])
        self.change_mode("happy")
        self.dither(2)

class NudgeSideLengthOfCube(Scene):
    CONFIG = {
        "x_color" : BLUE,
        "dx_color" : GREEN,
        "df_color" : YELLOW,
        "use_morty" : False,
        "x" : 3,
        "dx" : 0.2,
        "alt_dx" : 0.02,
        "offset_vect" : OUT,
        "pose_angle" : np.pi/12,
        "pose_axis" : UP+RIGHT,
        "small_piece_scaling_factor" : 0.7,
        "is_recursing" : False,
    }
    def construct(self):
        self.add_title()
        self.introduce_cube()
        self.write_df_equation()

    def add_title(self):
        title = TexMobject("f(x) = x^3")
        title.shift(SPACE_WIDTH*LEFT/2)
        title.to_edge(UP)
        self.play(Write(title))
        self.dither()

    def introduce_cube(self):
        cube = self.get_cube()
        cube.to_edge(LEFT, buff = 2*LARGE_BUFF)
        cube.shift(DOWN)

        dv_pieces = self.get_dv_pices(cube)
        original_dx = self.dx
        self.dx = 0
        alt_dv_pieces = self.get_dv_pices(cube)
        self.dx = original_dx
        alt_dv_pieces.set_fill(opacity = 0)

        x_brace = Brace(cube, LEFT, buff = SMALL_BUFF)
        dx_brace = Brace(
            dv_pieces[1], LEFT, buff = SMALL_BUFF,
            tex_string = "\\underbrace{%s}"%(3*"\\quad"),
        )
        dx_brace.stretch_in_place(1.5, 1)
        for brace, tex in (x_brace, "x"), (dx_brace, "dx"):
            brace.scale_in_place(0.95)
            brace.rotate_in_place(-np.pi/96)
            brace.shift(0.3*(UP+LEFT))
            brace.add(brace.get_text("$%s$"%tex))


        cube_group = VGroup(cube, dv_pieces, alt_dv_pieces)
        self.pose_3d_mobject(cube_group)

        self.play(DrawBorderThenFill(cube))
        self.play(GrowFromCenter(x_brace))
        self.dither()
        self.play(Transform(alt_dv_pieces, dv_pieces))
        self.remove(alt_dv_pieces)
        self.add(dv_pieces)
        self.play(GrowFromCenter(dx_brace))
        self.dither()
        self.play(*[
            ApplyMethod(
                piece.shift, 
                0.5*(piece.get_center()-cube.get_center())
            )
            for piece in dv_pieces
        ]+[
            ApplyMethod(dx_brace.shift, 0.7*UP)
        ])
        self.dither()

        self.cube = cube
        self.faces, self.bars, self.corner_cube = [
            VGroup(*[
                piece 
                for piece in dv_pieces
                if piece.type == target_type
            ])
            for target_type in "face", "bar", "corner_cube"
        ]

    def write_df_equation(self):
        df_equation = VGroup(
            TexMobject("df"),
            TexMobject("="),
            self.organize_faces(self.faces.copy()),
            TexMobject("+"),
            self.organize_bars(self.bars.copy()),
            TexMobject("+"),
            self.corner_cube.copy()
        )
        df, equals, faces, plus1, bars, plus2, corner_cube = df_equation
        df.highlight(self.df_color)
        for three_d_mob in faces, bars, corner_cube:
            three_d_mob.scale(self.small_piece_scaling_factor)
            # self.pose_3d_mobject(three_d_mob)
        faces.set_fill(opacity = 0.3)
        df_equation.arrange_submobjects(RIGHT)
        df_equation.next_to(ORIGIN, RIGHT)
        df_equation.to_edge(UP)

        faces_brace = Brace(faces, DOWN)
        faces_brace_text = faces_brace.get_text("$3x^2", "\\, dx$")
        extras_brace = Brace(VGroup(bars, corner_cube), DOWN)
        ignore_text = extras_brace.get_text(
            "Multiple \\\\ of $dx^2$"
        )
        ignore_text.scale_in_place(0.7)
        x_squared_dx = TexMobject("x^2", "\\, dx")


        self.play(*map(Write, [df, equals]))
        self.grab_pieces(self.faces, faces)
        self.dither()
        # self.shrink_dx()
        face = self.faces[0]
        face.save_state()
        self.play(face.shift, SPACE_WIDTH*RIGHT)
        x_squared_dx.move_to(self.faces[0])
        self.play(Write(x_squared_dx, run_time = 1))
        for submob in x_squared_dx:
            self.play(submob.highlight, RED, rate_func = there_and_back)
            self.play(submob.highlight, RED, rate_func = there_and_back)
        self.dither()
        self.play(
            face.restore,
            Transform(x_squared_dx, faces_brace_text),
            GrowFromCenter(faces_brace)
        )
        self.dither()
        self.grab_pieces(self.bars, bars, plus1)
        self.grab_pieces(self.corner_cube, corner_cube, plus2)
        self.play(
            GrowFromCenter(extras_brace),
            Write(ignore_text)
        )
        self.dither()
        self.play(*[
            ApplyMethod(mob.fade, 0.7)
            for mob in [
                plus1, bars, plus2, corner_cube, 
                extras_brace, ignore_text
            ]
        ])
        self.dither()

    def grab_pieces(self, start_pieces, end_pices, to_write = None):
        for piece in start_pieces:
            piece.generate_target()
            piece.target.rotate_in_place(
                np.pi/12, piece.get_center()-self.cube.get_center()
            )
            piece.target.highlight(RED)
        self.play(*map(MoveToTarget, start_pieces), rate_func = wiggle)
        self.dither()
        added_anims = []
        if to_write is not None:
            added_anims.append(Write(to_write))
        self.play(
            Transform(start_pieces.copy(), end_pices),
            *added_anims
        )

    def shrink_dx(self):
        self.mobjects_at_start_of_shrink_dx = self.get_mobjects()
        if self.is_recursing:
            return
        alt_scene = self.__class__(
            dx = self.alt_dx,
            skip_animations = True,
            is_recursing = True
        )
        for mob in self.get_mobjects():
            mob.save_state()
        self.play(*[
            Transform(*pair)
            for pair in zip(
                self.get_mobjects(),
                alt_scene.mobjects_at_start_of_shrink_dx
            )
        ])
        self.dither()
        self.play(*[
            mob.restore
            for mob in self.get_mobjects()
        ])

    def get_cube(self):
        cube = self.get_prism(self.x, self.x, self.x)
        cube.set_fill(color = BLUE, opacity = 0.3)
        cube.set_stroke(color = WHITE, width = 1)
        return cube

    def get_dv_pices(self, cube):
        pieces = VGroup()
        for vect in it.product([0, 1], [0, 1], [0, 1]):
            if np.all(vect == ORIGIN):
                continue
            args = [
                self.x if bit is 0 else self.dx
                for bit in vect
            ]
            piece = self.get_prism(*args)
            piece.next_to(cube, np.array(vect), buff = 0)
            pieces.add(piece)
            if sum(vect) == 1:
                piece.type = "face"
            elif sum(vect) == 2:
                piece.type = "bar"
            else:
                piece.type = "corner_cube"

        return pieces

    def organize_faces(self, faces):
        self.unpose_3d_mobject(faces)
        for face in faces:
            dimensions = [
                face.length_over_dim(dim)
                for dim in range(3)
            ]
            thin_dim = np.argmin(dimensions)
            if thin_dim == 0:
                face.rotate(np.pi/2, DOWN)
            elif thin_dim == 1:
                face.rotate(np.pi/2, RIGHT)
        faces.arrange_submobjects(OUT, buff = LARGE_BUFF)
        self.pose_3d_mobject(faces)
        return faces

    def organize_bars(self, bars):
        self.unpose_3d_mobject(bars)
        for bar in bars:
            dimensions = [
                bar.length_over_dim(dim)
                for dim in range(3)
            ]
            thick_dim = np.argmax(dimensions)
            if thick_dim == 0:
                bar.rotate(np.pi/2, OUT)
            elif thick_dim == 2:
                bar.rotate(np.pi/2, LEFT)
        bars.arrange_submobjects(OUT, buff = LARGE_BUFF)
        self.pose_3d_mobject(bars)
        return bars

    def get_corner_cube(self):
        return self.get_prism(self.dx, self.dx,  self.dx)


    def get_prism(self, width, height, depth):
        color_kwargs = {
            "fill_color" : YELLOW,
            "fill_opacity" : 0.4,
            "stroke_color" : WHITE,            
            "stroke_width" : 0.1,
        }
        front = Rectangle(
            width = width,
            height = height,
            **color_kwargs
        )
        face = VGroup(front)
        for vect in LEFT, RIGHT, UP, DOWN:
            if vect is LEFT or vect is RIGHT:
                side = Rectangle(
                    height = height, 
                    width = depth, 
                    **color_kwargs
                )
            else:
                side = Rectangle(
                    height = depth,
                    width = width, 
                    **color_kwargs
                )
            side.next_to(front, vect, buff = 0)
            side.rotate(
                np.pi/2, rotate_vector(vect, -np.pi/2),
                about_point = front.get_edge_center(vect)
            )
            face.add(side)
        return face

    def pose_3d_mobject(self, mobject):
        mobject.rotate_in_place(self.pose_angle, self.pose_axis)
        return mobject

    def unpose_3d_mobject(self, mobject):
        mobject.rotate_in_place(-self.pose_angle, self.pose_axis)
        return mobject

class ShowCubeDVIn3D(Scene):
    def construct(self):
        raise Exception("This scene is only here for the stage_scenes script.")








































