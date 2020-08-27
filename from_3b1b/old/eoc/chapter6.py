from manimlib.imports import *

SPACE_UNIT_TO_PLANE_UNIT = 0.75

class Chapter6OpeningQuote(OpeningQuote):
    CONFIG = {
        "quote" : [
            "Do not ask whether a ",
            "statement is true until",
            "you know what it means."
        ],
        "author" : "Errett Bishop"
    }

class ThisWasConfusing(TeacherStudentsScene):
    def construct(self):
        words = TextMobject("Implicit differentiation")
        words.move_to(self.get_teacher().get_corner(UP+LEFT), DOWN+RIGHT)
        words.set_fill(opacity = 0)

        self.play(
            self.get_teacher().change_mode, "raise_right_hand",
            words.set_fill, None, 1,
            words.shift, 0.5*UP
        )
        self.change_student_modes(
            *["confused"]*3,
            look_at_arg = words,
            added_anims = [Animation(self.get_teacher())]
        )
        self.wait()
        self.play(
            self.get_teacher().change_mode, "confused",
            self.get_teacher().look_at, words,
        )
        self.wait(3)

class SlopeOfCircleExample(ZoomedScene):
    CONFIG = {
        "plane_kwargs" : {
            "x_radius" : FRAME_X_RADIUS/SPACE_UNIT_TO_PLANE_UNIT,
            "y_radius" : FRAME_Y_RADIUS/SPACE_UNIT_TO_PLANE_UNIT,
            "space_unit_to_x_unit" : SPACE_UNIT_TO_PLANE_UNIT,
            "space_unit_to_y_unit" : SPACE_UNIT_TO_PLANE_UNIT,
        },
        "example_point" : (3, 4),
        "circle_radius" : 5,
        "circle_color" : YELLOW,
        "example_color" : MAROON_B,
        "zoom_factor" : 20,
        "zoomed_canvas_corner" : UP+LEFT,
        "zoomed_canvas_corner_buff" : MED_SMALL_BUFF,
    }
    def construct(self):
        self.setup_plane()
        self.introduce_circle()
        self.talk_through_pythagorean_theorem()
        self.draw_example_slope()
        self.show_perpendicular_radius()
        self.show_dx_and_dy()
        self.write_slope_as_dy_dx()
        self.point_out_this_is_not_a_graph()
        self.perform_implicit_derivative()
        self.show_final_slope()

    def setup_plane(self):
        self.plane = NumberPlane(**self.plane_kwargs)
        self.planes.fade()
        self.plane.add(self.plane.get_axis_labels())
        self.plane.add_coordinates()

        self.add(self.plane)

    def introduce_circle(self):
        circle = Circle(
            radius = self.circle_radius*SPACE_UNIT_TO_PLANE_UNIT,
            color = self.circle_color,
        )
        equation = TexMobject("x^2 + y^2 = 5^2")
        equation.add_background_rectangle()
        equation.next_to(
            circle.point_from_proportion(1./8), 
            UP+RIGHT
        )
        equation.to_edge(RIGHT)

        self.play(ShowCreation(circle, run_time = 2))
        self.play(Write(equation))
        self.wait()

        self.circle = circle
        self.circle_equation = equation

    def talk_through_pythagorean_theorem(self):
        point = self.plane.num_pair_to_point(self.example_point)
        x_axis_point = point[0]*RIGHT
        dot = Dot(point, color = self.example_color)

        x_line = Line(ORIGIN, x_axis_point, color = GREEN)
        y_line = Line(x_axis_point, point, color = RED)
        radial_line = Line(ORIGIN, point, color = self.example_color)
        lines = VGroup(radial_line, x_line, y_line)
        labels = VGroup()

        self.play(ShowCreation(dot))
        for line, tex in zip(lines, "5xy"):
            label = TexMobject(tex)
            label.set_color(line.get_color())
            label.add_background_rectangle()
            label.next_to(
                line.get_center(), 
                rotate_vector(UP, line.get_angle()),
                buff = SMALL_BUFF
            )
            self.play(
                ShowCreation(line),
                Write(label)
            )
            labels.add(label)

        full_group = VGroup(dot, lines, labels)
        start_angle = angle_of_vector(point)
        end_angle = np.pi/12
        spatial_radius = get_norm(point)
        def update_full_group(group, alpha):
            dot, lines, labels = group
            angle = interpolate(start_angle, end_angle, alpha)
            new_point = spatial_radius*rotate_vector(RIGHT, angle)
            new_x_axis_point = new_point[0]*RIGHT
            dot.move_to(new_point)

            radial_line, x_line, y_line = lines
            x_line.put_start_and_end_on(ORIGIN, new_x_axis_point)
            y_line.put_start_and_end_on(new_x_axis_point, new_point)
            radial_line.put_start_and_end_on(ORIGIN, new_point)
            for line, label in zip(lines, labels):
                label.next_to(
                    line.get_center(), 
                    rotate_vector(UP, line.get_angle()),
                    buff = SMALL_BUFF
                )
            return group

        self.play(UpdateFromAlphaFunc(
            full_group, update_full_group,
            rate_func = there_and_back,
            run_time = 5,
        ))
        self.wait(2)

        #Move labels to equation
        movers = labels.copy()
        pairs = list(zip(
            [movers[1], movers[2], movers[0]],
            self.circle_equation[1][0:-1:3]
        ))
        self.play(*[
            ApplyMethod(m1.replace, m2)
            for m1, m2 in pairs
        ])
        self.wait()

        self.play(*list(map(FadeOut, [lines, labels, movers])))
        self.remove(full_group)
        self.add(dot)
        self.wait()

        self.example_point_dot = dot

    def draw_example_slope(self):
        point = self.example_point_dot.get_center()
        line = Line(ORIGIN, point)
        line.set_color(self.example_color)
        line.rotate(np.pi/2)
        line.scale(2)
        line.move_to(point)

        word = TextMobject("Slope?")
        word.next_to(line.get_start(), UP, aligned_edge = LEFT)
        word.add_background_rectangle()

        coords = TexMobject("(%d, %d)"%self.example_point)
        coords.add_background_rectangle()
        coords.scale(0.7)
        coords.next_to(point, LEFT)
        coords.shift(SMALL_BUFF*DOWN)
        coords.set_color(self.example_color)

        self.play(GrowFromCenter(line))
        self.play(Write(word))
        self.wait()
        self.play(Write(coords))
        self.wait()

        self.tangent_line = line
        self.slope_word = word
        self.example_point_coords_mob = coords

    def show_perpendicular_radius(self):
        point = self.example_point_dot.get_center()
        radial_line = Line(ORIGIN, point, color = RED)

        perp_mark = VGroup(
            Line(UP, UP+RIGHT),
            Line(UP+RIGHT, RIGHT),
        )
        perp_mark.scale(0.2)
        perp_mark.set_stroke(width = 2)
        perp_mark.rotate(radial_line.get_angle()+np.pi)
        perp_mark.shift(point)

        self.play(ShowCreation(radial_line))
        self.play(ShowCreation(perp_mark))
        self.wait()
        self.play(Indicate(perp_mark))
        self.wait()
        
        morty =  Mortimer().flip().to_corner(DOWN+LEFT)
        self.play(FadeIn(morty))
        self.play(PiCreatureBubbleIntroduction(
            morty, "Suppose you \\\\ don't know this.",
        ))
        to_fade =self.get_mobjects_from_last_animation()
        self.play(Blink(morty))
        self.wait()

        self.play(*list(map(FadeOut, to_fade)))
        self.play(*list(map(FadeOut, [radial_line, perp_mark])))
        self.wait()

    def show_dx_and_dy(self):
        dot = self.example_point_dot
        point = dot.get_center()
        step_vect = rotate_vector(point, np.pi/2)
        step_length = 1./self.zoom_factor
        step_vect *= step_length/get_norm(step_vect)

        step_line = Line(ORIGIN, LEFT)
        step_line.set_color(WHITE)
        brace = Brace(step_line, DOWN)
        step_text = brace.get_text("Step", buff = SMALL_BUFF)
        step_group = VGroup(step_line, brace, step_text)
        step_group.rotate(angle_of_vector(point) - np.pi/2)
        step_group.scale(1./self.zoom_factor)
        step_group.shift(point)

        interim_point = step_line.get_corner(UP+RIGHT)
        dy_line = Line(point, interim_point)
        dx_line = Line(interim_point, point+step_vect)
        dy_line.set_color(RED)
        dx_line.set_color(GREEN)
        for line, tex in (dx_line, "dx"), (dy_line, "dy"):
            label = TexMobject(tex)
            label.scale(1./self.zoom_factor)
            next_to_vect = np.round(
                rotate_vector(DOWN, line.get_angle())
            )
            label.next_to(
                line, next_to_vect,
                buff = MED_SMALL_BUFF/self.zoom_factor
            )
            label.set_color(line.get_color())
            line.label = label

        self.activate_zooming()
        self.little_rectangle.move_to(step_line.get_center())
        self.little_rectangle.save_state()
        self.little_rectangle.scale_in_place(self.zoom_factor)
        self.wait()        
        self.play(
            self.little_rectangle.restore,
            dot.scale_in_place, 1./self.zoom_factor,
            run_time = 2
        )
        self.wait()
        self.play(ShowCreation(step_line))
        self.play(GrowFromCenter(brace))
        self.play(Write(step_text))
        self.wait()
        for line in dy_line, dx_line:
            self.play(ShowCreation(line))
            self.play(Write(line.label))
            self.wait()
        self.wait()

        self.step_group = step_group
        self.dx_line = dx_line
        self.dy_line = dy_line

    def write_slope_as_dy_dx(self):
        slope_word = self.slope_word
        new_slope_word = TextMobject("Slope =")
        new_slope_word.add_background_rectangle()
        new_slope_word.next_to(ORIGIN, RIGHT)
        new_slope_word.shift(slope_word.get_center()[1]*UP)

        dy_dx = TexMobject("\\frac{dy}{dx}")
        VGroup(*dy_dx[:2]).set_color(RED)
        VGroup(*dy_dx[-2:]).set_color(GREEN)
        dy_dx.next_to(new_slope_word, RIGHT)
        dy_dx.add_background_rectangle()

        self.play(Transform(slope_word, new_slope_word))
        self.play(Write(dy_dx))
        self.wait()

        self.dy_dx = dy_dx

    def point_out_this_is_not_a_graph(self):
        equation = self.circle_equation
        x = equation[1][0]
        y = equation[1][3]
        brace = Brace(equation, DOWN)
        brace_text = brace.get_text(
            "Not $y = f(x)$",
            buff = SMALL_BUFF
        )
        brace_text.set_color(RED)
        alt_brace_text = brace.get_text("Implicit curve")
        for text in brace_text, alt_brace_text:
            text.add_background_rectangle()
            text.to_edge(RIGHT, buff = MED_SMALL_BUFF)

        new_circle = self.circle.copy()
        new_circle.set_color(BLUE)

        self.play(
            GrowFromCenter(brace),
            Write(brace_text)
        )
        self.wait()
        self.play(Indicate(x))
        self.wait()
        self.play(Indicate(y))
        self.wait()
        self.play(Transform(brace_text, alt_brace_text))
        self.wait()
        self.play(
            ShowCreation(new_circle, run_time = 2),
            Animation(brace_text)
        )
        self.play(new_circle.set_stroke, None, 0)
        self.wait()
        self.play(*list(map(FadeOut, [brace, brace_text])))
        self.wait()

    def perform_implicit_derivative(self):
        equation = self.circle_equation
        morty = Mortimer()
        morty.flip()
        morty.next_to(ORIGIN, LEFT)
        morty.to_edge(DOWN, buff = SMALL_BUFF)
        q_marks = TexMobject("???")
        q_marks.next_to(morty, UP)

        rect = Rectangle(
            width = FRAME_X_RADIUS - SMALL_BUFF, 
            height = FRAME_Y_RADIUS - SMALL_BUFF,
            stroke_width = 0,
            fill_color = BLACK,
            fill_opacity = 0.8,
        )
        rect.to_corner(DOWN+RIGHT, buff = 0)

        derivative = TexMobject("2x\\,dx + 2y\\,dy = 0")
        dx = VGroup(*derivative[2:4])
        dy = VGroup(*derivative[7:9])
        dx.set_color(GREEN)
        dy.set_color(RED)



        self.play(
            FadeIn(rect),
            FadeIn(morty),            
            equation.next_to, ORIGIN, DOWN, MED_LARGE_BUFF,
            equation.shift, FRAME_X_RADIUS*RIGHT/2,
        )
        self.play(
            morty.change_mode, "confused",
            morty.look_at, equation
        )
        self.play(Blink(morty))
        derivative.next_to(equation, DOWN)
        derivative.shift(
            equation[1][-3].get_center()[0]*RIGHT - \
            derivative[-2].get_center()[0]*RIGHT
        )


        #Differentiate
        self.play(
            morty.look_at, derivative[0],
            *[
                ReplacementTransform(
                    equation[1][i].copy(),
                    derivative[j],
                )
                for i, j in ((1, 0), (0, 1))
            ]
        )
        self.play(Write(dx, run_time = 1))
        self.wait()
        self.play(*[
            ReplacementTransform(
                equation[1][i].copy(),
                derivative[j],
            )
            for i, j in ((2, 4), (3, 6), (4, 5))
        ])
        self.play(Write(dy, run_time = 1))
        self.play(Blink(morty)) 
        self.play(*[
            ReplacementTransform(
                equation[1][i].copy(),
                derivative[j],
            )
            for i, j in ((-3, -2), (-2, -1), (-1, -1))
        ])
        self.wait()

        #React
        self.play(morty.change_mode, "erm")
        self.play(Blink(morty))
        self.play(Write(q_marks))
        self.wait()
        self.play(Indicate(dx), morty.look_at, dx)
        self.play(Indicate(dy), morty.look_at, dy)
        self.wait()
        self.play(
            morty.change_mode, "shruggie",
            FadeOut(q_marks)
        )
        self.play(Blink(morty))
        self.play(
            morty.change_mode, "pondering",
            morty.look_at, derivative,
        )

        #Rearrange
        x, y, eq = np.array(derivative)[[1, 6, 9]]
        final_form = TexMobject(
            "\\frac{dy}{dx} = \\frac{-x}{y}"
        )
        new_dy = VGroup(*final_form[:2])
        new_dx = VGroup(*final_form[3:5])
        new_dy.set_color(dy.get_color())
        new_dx.set_color(dx.get_color())
        new_dy.add(final_form[2])
        new_x = VGroup(*final_form[6:8])
        new_y = VGroup(*final_form[8:10])
        new_eq = final_form[5]

        final_form.next_to(derivative, DOWN)
        final_form.shift((eq.get_center()[0]-new_eq.get_center()[0])*RIGHT)


        self.play(*[
            ReplacementTransform(
                mover.copy(), target,
                run_time = 2,
                path_arc = np.pi/2,
            )
            for mover, target in [
                (dy, new_dy), 
                (dx, new_dx), 
                (eq, new_eq), 
                (x, new_x), 
                (y, new_y)
            ]
        ] + [
            morty.look_at, final_form
        ])
        self.wait(2)

        self.morty = morty
        self.neg_x_over_y = VGroup(*final_form[6:])

    def show_final_slope(self):
        morty = self.morty
        dy_dx = self.dy_dx
        coords = self.example_point_coords_mob
        x, y = coords[1][1].copy(), coords[1][3].copy()        

        frac = self.neg_x_over_y.copy()
        frac.generate_target()
        eq = TexMobject("=")
        eq.add_background_rectangle()
        eq.next_to(dy_dx, RIGHT)
        frac.target.next_to(eq, RIGHT)
        frac.target.shift(SMALL_BUFF*DOWN)
        rect = BackgroundRectangle(frac.target)

        self.play(
            FadeIn(rect),
            MoveToTarget(frac),
            Write(eq),
            morty.look_at, rect,
            run_time = 2,
        )
        self.wait()
        self.play(FocusOn(coords), morty.look_at, coords)
        self.play(Indicate(coords))
        scale_factor = 1.4
        self.play(
            x.scale, scale_factor,
            x.set_color, GREEN,
            x.move_to, frac[1],
            FadeOut(frac[1]),
            y.scale, scale_factor,
            y.set_color, RED,
            y.move_to, frac[3], DOWN,
            y.shift, SMALL_BUFF*UP,
            FadeOut(frac[3]),
            morty.look_at, frac,
            run_time = 2
        )
        self.wait()
        self.play(Blink(morty))

class NameImplicitDifferentation(TeacherStudentsScene):
    def construct(self):
        title = TextMobject("``Implicit differentiation''")

        equation = TexMobject("x^2", "+", "y^2", "=", "5^2")
        derivative = TexMobject(
            "2x\\,dx", "+", "2y\\,dy", "=", "0"
        )
        VGroup(*derivative[0][2:]).set_color(GREEN)
        VGroup(*derivative[2][2:]).set_color(RED)
        arrow = Arrow(ORIGIN, DOWN, buff = SMALL_BUFF)
        group = VGroup(title, equation, arrow, derivative)
        group.arrange(DOWN)
        group.to_edge(UP)

        self.add(title, equation)
        self.play(
            self.get_teacher().change_mode, "raise_right_hand",
            ShowCreation(arrow)
        )
        self.change_student_modes(
            *["confused"]*3,
            look_at_arg = derivative,
            added_anims = [ReplacementTransform(equation.copy(), derivative)]
        )
        self.wait(2)
        self.teacher_says(
            "Don't worry...",
            added_anims = [
                group.scale, 0.7,
                group.to_corner, UP+LEFT,
            ]
        )
        self.change_student_modes(*["happy"]*3)
        self.wait(3)

class Ladder(VMobject):
    CONFIG = {
        "height" : 4,
        "width" : 1,
        "n_rungs" : 7,
    }
    def generate_points(self):
        left_line, right_line = [
            Line(ORIGIN, self.height*UP).shift(self.width*vect/2.0)
            for vect in (LEFT, RIGHT)
        ]
        rungs = [
            Line(
                left_line.point_from_proportion(a),
                right_line.point_from_proportion(a),
            )
            for a in np.linspace(0, 1, 2*self.n_rungs+1)[1:-1:2]
        ]
        self.add(left_line, right_line, *rungs)
        self.center()

class RelatedRatesExample(ThreeDScene):
    CONFIG = {
        "start_x" : 3.0,
        "start_y" : 4.0,
        "wall_dimensions" : [0.3, 5, 5],
        "wall_color" : color_gradient([GREY_BROWN, BLACK], 4)[1],
        "wall_center" : 1.5*LEFT+0.5*UP,
    }
    def construct(self):
        self.introduce_ladder()
        self.write_related_rates()
        self.measure_ladder()
        self.slide_ladder()
        self.ponder_question()
        self.write_equation()
        self.isolate_x_of_t()
        self.discuss_lhs_as_function()
        self.let_dt_pass()
        self.take_derivative_of_rhs()
        self.take_derivative_of_lhs()
        self.bring_back_velocity_arrows()
        self.replace_terms_in_final_form()
        self.write_final_solution()

    def introduce_ladder(self):
        ladder = Ladder(height = self.get_ladder_length())

        wall = Prism(
            dimensions = self.wall_dimensions,
            fill_color = self.wall_color,
            fill_opacity = 1,
        )
        wall.rotate(np.pi/12, UP)
        wall.shift(self.wall_center)

        ladder.generate_target()
        ladder.fallen = ladder.copy()
        ladder.target.rotate(self.get_ladder_angle(), LEFT)
        ladder.fallen.rotate(np.pi/2, LEFT)
        for ladder_copy in ladder.target, ladder.fallen:
            ladder_copy.rotate(-5*np.pi/12, UP)
            ladder_copy.next_to(wall, LEFT, 0, DOWN)
            ladder_copy.shift(0.8*RIGHT) ##BAD!


        self.play(
            ShowCreation(ladder, run_time = 2)
        )
        self.wait()

        self.play(
            DrawBorderThenFill(wall),
            MoveToTarget(ladder),
            run_time = 2
        )
        self.wait()

        self.ladder = ladder

    def write_related_rates(self):
        words = TextMobject("Related rates")
        words.to_corner(UP+RIGHT)
        self.play(Write(words))
        self.wait()

        self.related_rates_words = words

    def measure_ladder(self):
        ladder = self.ladder
        ladder_brace = self.get_ladder_brace(ladder)

        x_and_y_lines = self.get_x_and_y_lines(ladder)
        x_line, y_line = x_and_y_lines

        y_label = TexMobject("%dm"%int(self.start_y))
        y_label.next_to(y_line, LEFT, buff = SMALL_BUFF)
        y_label.set_color(y_line.get_color())

        x_label = TexMobject("%dm"%int(self.start_x))
        x_label.next_to(x_line, UP)
        x_label.set_color(x_line.get_color())

        self.play(Write(ladder_brace))
        self.wait()
        self.play(ShowCreation(y_line), Write(y_label))
        self.wait()
        self.play(ShowCreation(x_line), Write(x_label))
        self.wait(2)
        self.play(*list(map(FadeOut, [x_label, y_label])))

        self.ladder_brace = ladder_brace
        self.x_and_y_lines = x_and_y_lines
        self.numerical_x_and_y_labels = VGroup(x_label, y_label)

    def slide_ladder(self):
        ladder = self.ladder
        brace = self.ladder_brace
        x_and_y_lines = self.x_and_y_lines
        x_line, y_line = x_and_y_lines

        down_arrow, left_arrow = [
            Arrow(ORIGIN, vect, color = YELLOW, buff = 0)
            for vect in (DOWN, LEFT)
        ]
        down_arrow.shift(y_line.get_start()+MED_SMALL_BUFF*RIGHT)
        left_arrow.shift(x_line.get_start()+SMALL_BUFF*DOWN)

        # speed_label = TexMobject("1 \\text{m}/\\text{s}")
        speed_label = TexMobject("1 \\frac{\\text{m}}{\\text{s}}")
        speed_label.next_to(down_arrow, RIGHT, buff = SMALL_BUFF)

        q_marks = TexMobject("???")
        q_marks.next_to(left_arrow, DOWN, buff = SMALL_BUFF)


        added_anims = [
            UpdateFromFunc(brace, self.update_brace),
            UpdateFromFunc(x_and_y_lines, self.update_x_and_y_lines),
            Animation(down_arrow),
        ]
        self.play(ShowCreation(down_arrow))
        self.play(Write(speed_label))
        self.let_ladder_fall(ladder, *added_anims)
        self.wait()
        self.reset_ladder(ladder, *added_anims)
        self.play(ShowCreation(left_arrow))
        self.play(Write(q_marks))
        self.wait()
        self.let_ladder_fall(ladder, *added_anims)
        self.wait()
        self.reset_ladder(ladder, *added_anims)
        self.wait()

        self.dy_arrow = down_arrow
        self.dy_label = speed_label
        self.dx_arrow = left_arrow
        self.dx_label = q_marks

    def ponder_question(self):
        randy = Randolph(mode = "pondering")
        randy.flip()
        randy.to_corner(DOWN+RIGHT)

        self.play(FadeIn(randy))
        self.play(Blink(randy))
        self.wait()
        self.play(
            randy.change_mode, "confused",
            randy.look_at, self.ladder.get_top()
        )
        self.play(randy.look_at, self.ladder.get_bottom())
        self.play(randy.look_at, self.ladder.get_top())
        self.play(Blink(randy))
        self.wait()
        self.play(PiCreatureSays(
            randy, "Give names"
        ))
        self.play(Blink(randy))
        self.play(*list(map(FadeOut, [
            randy, randy.bubble, randy.bubble.content
        ])))

    def write_equation(self):
        self.x_and_y_labels = self.get_x_and_y_labels()
        x_label, y_label = self.x_and_y_labels

        equation = TexMobject(
            "x(t)", "^2", "+", "y(t)", "^2", "=", "5^2"
        )
        equation[0].set_color(GREEN)
        equation[3].set_color(RED)
        equation.next_to(self.related_rates_words, DOWN, buff = MED_LARGE_BUFF)
        equation.to_edge(RIGHT, buff = LARGE_BUFF)

        self.play(Write(y_label))
        self.wait()
        self.let_ladder_fall(
            self.ladder,
            y_label.shift, self.start_y*DOWN/2,
            *self.get_added_anims_for_ladder_fall()[:-1],
            rate_func = lambda t : 0.2*there_and_back(t),
            run_time = 3
        )
        self.play(FocusOn(x_label))
        self.play(Write(x_label))
        self.wait(2)
        self.play(
            ReplacementTransform(x_label.copy(), equation[0]),
            ReplacementTransform(y_label.copy(), equation[3]),
            Write(VGroup(*np.array(equation)[[1, 2, 4, 5, 6]]))
        )
        self.wait(2)
        self.let_ladder_fall(
            self.ladder,
            *self.get_added_anims_for_ladder_fall(),
            rate_func = there_and_back,
            run_time = 6
        )
        self.wait()

        self.equation = equation

    def isolate_x_of_t(self):
        alt_equation = TexMobject(
            "x(t)", "=", "\\big(5^2", "-", "y(t)", "^2 \\big)", "^{1/2}",
        )
        alt_equation[0].set_color(GREEN)
        alt_equation[4].set_color(RED)
        alt_equation.next_to(self.equation, DOWN, buff = MED_LARGE_BUFF)
        alt_equation.to_edge(RIGHT)

        randy = Randolph()
        randy.next_to(
            alt_equation, DOWN, 
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT,
        )
        randy.look_at(alt_equation)

        find_dx_dt = TexMobject("\\text{Find } \\,", "\\frac{dx}{dt}")
        find_dx_dt.next_to(randy, RIGHT, aligned_edge = UP)
        find_dx_dt[1].set_color(GREEN)

        self.play(FadeIn(randy))
        self.play(
            randy.change_mode, "raise_right_hand", 
            randy.look_at, alt_equation,
            *[
                ReplacementTransform(
                    self.equation[i].copy(), 
                    alt_equation[j],
                    path_arc = np.pi/2,
                    run_time = 3,
                    rate_func = squish_rate_func(
                        smooth, j/12.0, (j+6)/12.0
                    )
                )
                for i, j in enumerate([0, 6, 3, 4, 5, 1, 2])
            ]
        )
        self.play(Blink(randy))
        self.wait()
        self.play(
            Write(find_dx_dt),
            randy.change_mode, "pondering",
            randy.look_at, find_dx_dt,
        )
        self.let_ladder_fall(
            self.ladder, *self.get_added_anims_for_ladder_fall(),
            run_time = 8,
            rate_func = there_and_back
        )
        self.play(*list(map(FadeOut, [
            randy, find_dx_dt, alt_equation
        ])))
        self.wait()

    def discuss_lhs_as_function(self):
        equation = self.equation
        lhs = VGroup(*equation[:5])
        brace = Brace(lhs, DOWN)
        function_of_time = brace.get_text(
            "Function of time"
        )
        constant_words = TextMobject(
            """that happens to
            be constant"""
        )
        constant_words.set_color(YELLOW)
        constant_words.next_to(function_of_time, DOWN)

        derivative = TexMobject(
            "\\frac{d\\left(x(t)^2 + y(t)^2 \\right)}{dt}"
        )
        derivative.next_to(equation, DOWN, buff = MED_LARGE_BUFF)
        derivative.shift( ##Align x terms
            equation[0][0].get_center()[0]*RIGHT-\
            derivative[2].get_center()[0]*RIGHT
        )
        derivative_interior = lhs.copy()
        derivative_interior.move_to(VGroup(*derivative[2:13]))
        derivative_scaffold = VGroup(
            *list(derivative[:2])+list(derivative[13:])
        )

        self.play(
            GrowFromCenter(brace),
            Write(function_of_time)
        )
        self.wait()
        self.play(Write(constant_words))
        self.let_ladder_fall(
            self.ladder, *self.get_added_anims_for_ladder_fall(),
            run_time = 6,
            rate_func = lambda t : 0.5*there_and_back(t)
        )
        self.wait()
        self.play(*list(map(FadeOut, [
            brace, constant_words, function_of_time
        ])))
        self.play(
            ReplacementTransform(lhs.copy(), derivative_interior),
            Write(derivative_scaffold),
        )
        self.wait()

        self.derivative = VGroup(
            derivative_scaffold, derivative_interior
        )

    def let_dt_pass(self):
        dt_words = TextMobject("After", "$dt$", "seconds...")
        dt_words.to_corner(UP+LEFT)
        dt = dt_words[1]
        dt.set_color(YELLOW)
        dt_brace = Brace(dt, buff = SMALL_BUFF)
        dt_brace_text = dt_brace.get_text("Think 0.01", buff = SMALL_BUFF)
        dt_brace_text.set_color(dt.get_color())

        shadow_ladder = self.ladder.copy()
        shadow_ladder.fade(0.5)

        x_line, y_line = self.x_and_y_lines
        y_top = y_line.get_start()
        x_left = x_line.get_start()

        self.play(Write(dt_words, run_time = 2))
        self.play(
            GrowFromCenter(dt_brace),
            Write(dt_brace_text, run_time = 2)
        )
        self.play(*list(map(FadeOut, [
            self.dy_arrow, self.dy_label, 
            self.dx_arrow, self.dx_label, 
        ])))
        self.add(shadow_ladder)
        self.let_ladder_fall(
            self.ladder, *self.get_added_anims_for_ladder_fall(),
            rate_func = lambda t : 0.1*smooth(t),
            run_time = 1
        )

        new_y_top = y_line.get_start()
        new_x_left = x_line.get_start()

        dy_line = Line(y_top, new_y_top)
        dy_brace = Brace(dy_line, RIGHT, buff = SMALL_BUFF)
        dy_label = dy_brace.get_text("$dy$", buff = SMALL_BUFF)
        dy_label.set_color(RED)

        dx_line = Line(x_left, new_x_left)
        dx_brace = Brace(dx_line, DOWN, buff = SMALL_BUFF)
        dx_label = dx_brace.get_text("$dx$")
        dx_label.set_color(GREEN)

        VGroup(dy_line, dx_line).set_color(YELLOW)

        for line, brace, label in (dy_line, dy_brace, dy_label), (dx_line, dx_brace, dx_label):
            self.play(
                ShowCreation(line),
                GrowFromCenter(brace),
                Write(label),
                run_time = 1
            )
        self.wait()
        self.play(Indicate(self.derivative[1]))
        self.wait()

        self.dy_group = VGroup(dy_line, dy_brace, dy_label)
        self.dx_group = VGroup(dx_line, dx_brace, dx_label)
        self.shadow_ladder = shadow_ladder

    def take_derivative_of_rhs(self):
        derivative = self.derivative
        equals_zero = TexMobject("= 0")
        equals_zero.next_to(derivative)

        rhs = self.equation[-1]

        self.play(Write(equals_zero))
        self.wait()
        self.play(FocusOn(rhs))
        self.play(Indicate(rhs))
        self.wait()
        self.reset_ladder(
            self.ladder, 
            *self.get_added_anims_for_ladder_fall()+[
                Animation(self.dy_group),
                Animation(self.dx_group),
            ],
            rate_func = there_and_back,
            run_time = 3
        )
        self.wait()

        self.equals_zero = equals_zero

    def take_derivative_of_lhs(self):
        derivative_scaffold, equation = self.derivative
        equals_zero_copy = self.equals_zero.copy()

        lhs_derivative = TexMobject(
            "2", "x(t)", "\\frac{dx}{dt}", "+",
            "2", "y(t)", "\\frac{dy}{dt}",
        )
        lhs_derivative[1].set_color(GREEN)
        VGroup(*lhs_derivative[2][:2]).set_color(GREEN)
        lhs_derivative[5].set_color(RED)
        VGroup(*lhs_derivative[6][:2]).set_color(RED)
        lhs_derivative.next_to(
            derivative_scaffold, DOWN,
            aligned_edge = RIGHT,
            buff = MED_LARGE_BUFF
        )
        equals_zero_copy.next_to(lhs_derivative, RIGHT)

        pairs = [
            (0, 1), (1, 0), #x^2 -> 2x
            (2, 3), (3, 5), (4, 4), #+y^2 -> +2y
        ]
        def perform_replacement(index_pairs):
            self.play(*[
                ReplacementTransform(
                    equation[i].copy(), lhs_derivative[j],
                    path_arc = np.pi/2,
                    run_time = 2
                )
                for i, j in index_pairs
            ])

        perform_replacement(pairs[:2])
        self.play(Write(lhs_derivative[2]))
        self.wait()
        self.play(Indicate(
            VGroup(
                *list(lhs_derivative[:2])+\
                list(lhs_derivative[2][:2])
            ),
            run_time = 2
        ))
        self.play(Indicate(VGroup(*lhs_derivative[2][3:])))
        self.wait(2)
        perform_replacement(pairs[2:])
        self.play(Write(lhs_derivative[6]))
        self.wait()

        self.play(FocusOn(self.equals_zero))
        self.play(ReplacementTransform(
            self.equals_zero.copy(),
            equals_zero_copy
        ))
        self.wait(2)

        lhs_derivative.add(equals_zero_copy)
        self.lhs_derivative = lhs_derivative

    def bring_back_velocity_arrows(self):
        dx_dy_group = VGroup(self.dx_group, self.dy_group)
        arrow_group = VGroup(
            self.dy_arrow, self.dy_label,
            self.dx_arrow, self.dx_label,
        )
        ladder_fall_args = [self.ladder] + self.get_added_anims_for_ladder_fall()


        self.reset_ladder(*ladder_fall_args + [
            FadeOut(dx_dy_group),
            FadeOut(self.derivative),
            FadeOut(self.equals_zero),
            self.lhs_derivative.shift, 2*UP,
        ])
        self.remove(self.shadow_ladder)
        self.play(FadeIn(arrow_group))
        self.let_ladder_fall(*ladder_fall_args)
        self.wait()
        self.reset_ladder(*ladder_fall_args)
        self.wait()

    def replace_terms_in_final_form(self):
        x_label, y_label = self.x_and_y_labels
        num_x_label, num_y_label = self.numerical_x_and_y_labels

        new_lhs_derivative = TexMobject(
            "2", "(%d)"%int(self.start_x), "\\frac{dx}{dt}", "+",
            "2", "(%d)"%int(self.start_y), "(-1)",
            "= 0"
        )
        new_lhs_derivative[1].set_color(GREEN)
        VGroup(*new_lhs_derivative[2][:2]).set_color(GREEN)
        new_lhs_derivative[5].set_color(RED)
        new_lhs_derivative.next_to(
            self.lhs_derivative, DOWN,
            buff = MED_LARGE_BUFF,
            aligned_edge = RIGHT
        )
        def fill_in_equation_part(*indices):
            self.play(*[
                ReplacementTransform(
                    self.lhs_derivative[i].copy(),
                    new_lhs_derivative[i],
                    run_time = 2
                )
                for i in indices
            ])

        self.play(FadeOut(y_label), FadeIn(num_y_label))
        fill_in_equation_part(3, 4, 5)
        self.play(FadeOut(x_label), FadeIn(num_x_label))
        for indices in [(0, 1), (6,), (2, 7)]:
            fill_in_equation_part(*indices)
            self.wait()
        self.wait()

        self.new_lhs_derivative = new_lhs_derivative

    def write_final_solution(self):
        solution = TexMobject(
            "\\frac{dx}{dt} = \\frac{4}{3}"
        )
        for i in 0, 1, -1:
            solution[i].set_color(GREEN)
        solution[-3].set_color(RED)
        solution.next_to(
            self.new_lhs_derivative, DOWN,
            buff = MED_LARGE_BUFF,
            aligned_edge = RIGHT
        )

        box = Rectangle(color = YELLOW)
        box.replace(solution)
        box.scale_in_place(1.5)

        self.play(Write(solution))
        self.wait()
        self.play(ShowCreation(box))
        self.wait()

    #########

    def get_added_anims_for_ladder_fall(self):
        return [
            UpdateFromFunc(self.ladder_brace, self.update_brace),
            UpdateFromFunc(self.x_and_y_lines, self.update_x_and_y_lines),
            UpdateFromFunc(self.x_and_y_labels, self.update_x_and_y_labels),
        ]

    def let_ladder_fall(self, ladder, *added_anims, **kwargs):
        kwargs["run_time"] = kwargs.get("run_time", self.start_y)
        kwargs["rate_func"] = kwargs.get("rate_func", None)
        self.play(
            Transform(ladder, ladder.fallen),
            *added_anims,
            **kwargs
        )

    def reset_ladder(self, ladder, *added_anims, **kwargs):
        kwargs["run_time"] = kwargs.get("run_time", 2)
        self.play(
            Transform(ladder, ladder.target),
            *added_anims,
            **kwargs
        )

    def update_brace(self, brace):
        Transform(
            brace, self.get_ladder_brace(self.ladder)
        ).update(1)
        return brace

    def update_x_and_y_lines(self, x_and_y_lines):
        Transform(
            x_and_y_lines,
            self.get_x_and_y_lines(self.ladder)
        ).update(1)
        return x_and_y_lines

    def update_x_and_y_labels(self, x_and_y_labels):
        Transform(
            x_and_y_labels,
            self.get_x_and_y_labels()
        ).update(1)
        return x_and_y_labels

    def get_ladder_brace(self, ladder):
        vect = rotate_vector(LEFT, -self.get_ladder_angle())
        brace = Brace(ladder, vect)        
        length_string = "%dm"%int(self.get_ladder_length())
        length_label = brace.get_text(
            length_string, use_next_to = False
        )
        brace.add(length_label)
        brace.length_label = length_label
        return brace

    def get_x_and_y_labels(self):
        x_line, y_line = self.x_and_y_lines

        x_label = TexMobject("x(t)")
        x_label.set_color(x_line.get_color())
        x_label.next_to(x_line, DOWN, buff = SMALL_BUFF)

        y_label = TexMobject("y(t)")
        y_label.set_color(y_line.get_color())
        y_label.next_to(y_line, LEFT, buff = SMALL_BUFF)

        return VGroup(x_label, y_label)

    def get_x_and_y_lines(self, ladder):
        bottom_point, top_point = np.array(ladder[1].get_start_and_end())
        interim_point = top_point[0]*RIGHT + bottom_point[1]*UP
        interim_point += SMALL_BUFF*DOWN
        y_line = Line(top_point, interim_point)
        y_line.set_color(RED)
        x_line = Line(bottom_point, interim_point)
        x_line.set_color(GREEN)

        return VGroup(x_line, y_line)

    def get_ladder_angle(self):
        if hasattr(self, "ladder"):
            c1 = self.ladder.get_corner(UP+RIGHT)
            c2 = self.ladder.get_corner(DOWN+LEFT)
            vect = c1-c2
            return np.pi/2 - angle_of_vector(vect)
        else:
            return np.arctan(self.start_x/self.start_y)

    def get_ladder_length(self):
        return get_norm([self.start_x, self.start_y])

class LightweightLadderScene(RelatedRatesExample):
    CONFIG = {
        "skip_animations" : True
    }
    def construct(self):
        self.introduce_ladder()
        self.measure_ladder()
        self.add(self.numerical_x_and_y_labels)

class LightweightCircleExample(SlopeOfCircleExample):
    CONFIG = {
        "skip_animations" : True,
        "plane_kwargs" : {
            "x_radius" : 5,
            "y_radius" : 5,
            "space_unit_to_x_unit" : SPACE_UNIT_TO_PLANE_UNIT,
            "space_unit_to_y_unit" : SPACE_UNIT_TO_PLANE_UNIT,
        },
    }
    def construct(self):
        self.setup_plane()
        self.introduce_circle()
        self.talk_through_pythagorean_theorem()
        self.draw_example_slope()

        self.remove(self.circle_equation)
        self.remove(self.slope_word)
        self.example_point_coords_mob.scale(
            1.5, about_point = self.example_point_coords_mob.get_corner(UP+RIGHT)
        )
        self.plane.axis_labels[0].shift(3*LEFT)

class CompareLadderAndCircle(PiCreatureScene, ThreeDScene):
    def construct(self):
        self.introduce_both_scenes()
        self.show_derivatives()
        self.comment_on_ladder_derivative()
        self.comment_on_circle_derivative()

    def introduce_both_scenes(self):
        ladder_scene = LightweightLadderScene()
        ladder_mobs = VGroup(*ladder_scene.get_top_level_mobjects())
        circle_scene = LightweightCircleExample()
        circle_mobs = VGroup(*circle_scene.get_top_level_mobjects())
        for mobs, vect in (ladder_mobs, LEFT), (circle_mobs, RIGHT):
            mobs.set_height(FRAME_Y_RADIUS-MED_LARGE_BUFF)
            mobs.next_to(
                self.pi_creature.get_corner(UP+vect), UP,
                buff = SMALL_BUFF,
                aligned_edge = -vect
            )

        ladder_mobs.save_state()
        ladder_mobs.fade(1)
        ladder_mobs.rotate_in_place(np.pi/3, UP)
        self.play(
            self.pi_creature.change_mode, "raise_right_hand",
            self.pi_creature.look_at, ladder_mobs,
            ApplyMethod(ladder_mobs.restore, run_time = 2)
        )
        self.play(
            self.pi_creature.change_mode, "raise_left_hand",
            self.pi_creature.look_at, circle_mobs,
            Write(circle_mobs, run_time = 2)
        )
        self.wait(2)
        self.play(
            circle_mobs.to_edge, RIGHT,
            ladder_mobs.to_edge, LEFT,
        )

    def show_derivatives(self):
        equation = TexMobject(
            "x", "^2", "+", "y", "^2", "= 5^2"
        )
        derivative = TexMobject(
            "2", "x", "dx", "+", "2", "y", "dy", "=0"
        )
        self.color_equations(equation, derivative)
        equation.to_edge(UP)
        equation.shift(MED_LARGE_BUFF*LEFT)
        derivative.next_to(equation, DOWN, buff = MED_LARGE_BUFF)

        self.play(
            Write(equation),
            self.pi_creature.change_mode, "plain",
            self.pi_creature.look_at, equation
        )
        self.wait()
        self.play(*[
            ReplacementTransform(
                equation[i].copy(), derivative[j],
                path_arc = np.pi/2
            )
            for i, j in enumerate([1, 0, 3, 5, 4, 7])
        ]+[
            Write(derivative[j])
            for j in (2, 6)
        ])
        self.play(
            self.pi_creature.change_mode, "pondering",
            self.pi_creature.look_at, derivative
        )
        self.wait()

        self.equation = equation
        self.derivative = derivative

    def comment_on_ladder_derivative(self):
        equation = self.equation
        derivative = self.derivative

        time_equation = TexMobject(
            "x(t)", "^2", "+", "y(t)", "^2", "= 5^2"
        )
        time_derivative = TexMobject(
            "2", "x(t)", "\\frac{dx}{dt}", "+", 
            "2", "y(t)", "\\frac{dy}{dt}", "=0"
        )
        self.color_equations(time_equation, time_derivative)
        time_equation.move_to(equation)
        time_derivative.move_to(derivative, UP)

        brace = Brace(time_derivative)
        brace_text = brace.get_text("A rate")

        equation.save_state()
        derivative.save_state()

        self.play(Transform(equation, time_equation))
        self.wait()
        self.play(Transform(derivative, time_derivative))
        self.wait()
        self.play(GrowFromCenter(brace))
        self.play(Write(brace_text))
        self.change_mode("hooray")
        self.wait(2)
        self.play(
            equation.restore,
            derivative.restore,
            FadeOut(brace),
            FadeOut(brace_text),
            self.pi_creature.change_mode, "confused"
        )
        self.wait()

    def comment_on_circle_derivative(self):
        derivative = self.derivative
        dx = derivative.get_part_by_tex("dx")
        dy = derivative.get_part_by_tex("dy")

        for mob in dx, dy:
            brace = Brace(mob)
            brace.next_to(mob[0], DOWN, buff = SMALL_BUFF, aligned_edge = LEFT)
            text = brace.get_text("No $dt$", buff = SMALL_BUFF)
            text.set_color(YELLOW)

            self.play(
                GrowFromCenter(brace),
                Write(text)
            )
            self.wait()

        self.play(
            self.pi_creature.change_mode, "pondering",
            self.pi_creature.look, DOWN+LEFT
        )
        self.wait(2)

    #######

    def create_pi_creature(self):
        self.pi_creature = Mortimer().to_edge(DOWN)
        return self.pi_creature

    def color_equations(self, equation, derivative):
        for mob in equation[0], derivative[1]:
            mob.set_color(GREEN)
        for mob in equation[3], derivative[5]:
            mob.set_color(RED)

class TwoVariableFunctionAndDerivative(SlopeOfCircleExample):
    CONFIG = {
        "zoomed_canvas_corner" : DOWN+RIGHT,
        "zoomed_canvas_frame_shape" : (3, 4),
    }
    def construct(self):
        self.setup_plane()
        self.write_equation()
        self.show_example_point()
        self.shift_example_point((4, 4))
        self.shift_example_point((3, 3))
        self.shift_example_point(self.example_point)
        self.take_derivative_symbolically()
        self.show_dx_dy_step()
        self.plug_in_example_values()
        self.ask_about_equalling_zero()
        self.show_tangent_step()
        self.point_out_equalling_zero()
        self.show_tangent_line()

    def write_equation(self):
        equation = TexMobject("x", "^2", "+", "y", "^2")
        equation.add_background_rectangle()

        brace = Brace(equation, UP, buff = SMALL_BUFF)
        s_expression = self.get_s_expression("x", "y")
        s_rect, s_of_xy = s_expression
        s, xy = s_of_xy
        s_expression.next_to(brace, UP, buff = SMALL_BUFF)

        group = VGroup(equation, s_expression, brace)
        group.shift(FRAME_WIDTH*LEFT/3)
        group.to_edge(UP, buff = MED_SMALL_BUFF)

        s.save_state()
        s.next_to(brace, UP)


        self.play(Write(equation))
        self.play(GrowFromCenter(brace))
        self.play(Write(s))
        self.wait()
        self.play(
            FadeIn(s_rect),
            s.restore, 
            GrowFromCenter(xy)
        )
        self.wait()

        self.equation = equation
        self.s_expression = s_expression

    def show_example_point(self):
        point = self.plane.num_pair_to_point(self.example_point)
        dot = Dot(point, color = self.example_color)
        new_s_expression = self.get_s_expression(*self.example_point)
        new_s_expression.next_to(dot, UP+RIGHT, buff = 0)
        new_s_expression.set_color(self.example_color)
        equals_25 = TexMobject("=%d"%int(get_norm(self.example_point)**2))
        equals_25.set_color(YELLOW)
        equals_25.next_to(new_s_expression, RIGHT, align_using_submobjects = True)
        equals_25.add_background_rectangle()

        circle = Circle(
            radius = self.circle_radius*self.plane.space_unit_to_x_unit,
            color = self.circle_color,
        )

        self.play(
            ReplacementTransform(
                self.s_expression.copy(),
                new_s_expression
            ),
            ShowCreation(dot)
        )
        self.play(ShowCreation(circle), Animation(dot))
        self.play(Write(equals_25))
        self.wait()

        self.example_point_dot = dot
        self.example_point_label = VGroup(
            new_s_expression, equals_25
        )

    def shift_example_point(self, coords):
        point = self.plane.num_pair_to_point(coords)
        s_expression = self.get_s_expression(*coords)
        s_expression.next_to(point, UP+RIGHT, buff = SMALL_BUFF)
        s_expression.set_color(self.example_color)
        result = coords[0]**2 + coords[1]**2
        rhs = TexMobject("=%d"%int(result))
        rhs.add_background_rectangle()
        rhs.set_color(YELLOW)
        rhs.next_to(s_expression, RIGHT, align_using_submobjects = True)
        point_label = VGroup(s_expression, rhs)

        self.play(
            self.example_point_dot.move_to, point,
            Transform(self.example_point_label, point_label)
        )
        self.wait(2)

    def take_derivative_symbolically(self):
        equation = self.equation
        derivative = TexMobject(
            "dS =", "2", "x", "\\,dx", "+", "2", "y", "\\,dy",
        )
        derivative[2].set_color(GREEN)
        derivative[6].set_color(RED)
        derivative.next_to(equation, DOWN, buff = MED_LARGE_BUFF)
        derivative.add_background_rectangle()
        derivative.to_edge(LEFT)

        self.play(*[
            FadeIn(derivative[0])
        ]+[
            ReplacementTransform(
                self.s_expression[1][0].copy(),
                derivative[1][0],
            )
        ]+[
            Write(derivative[1][j])
            for j in (3, 7)
        ])
        self.play(*[
            ReplacementTransform(
                equation[1][i].copy(), derivative[1][j],
                path_arc = np.pi/2,
                run_time = 2,
                rate_func = squish_rate_func(smooth, (j-1)/12., (j+6)/12.)
            )
            for i, j in enumerate([2, 1, 4, 6, 5])
        ])
        self.wait(2)

        self.derivative = derivative

    def show_dx_dy_step(self):
        dot = self.example_point_dot
        s_label = self.example_point_label
        rhs = s_label[-1]
        s_label.remove(rhs)

        point = dot.get_center()
        vect = 2*LEFT + DOWN
        new_point = point + vect*0.6/self.zoom_factor
        interim_point = new_point[0]*RIGHT + point[1]*UP

        dx_line = Line(point, interim_point, color = GREEN)
        dy_line = Line(interim_point, new_point, color = RED)
        for line, tex, vect in (dx_line, "dx", UP), (dy_line, "dy", LEFT):
            label = TexMobject(tex)
            label.set_color(line.get_color())
            label.next_to(line, vect, buff = SMALL_BUFF)
            label.add_background_rectangle()
            label.scale(
                1./self.zoom_factor, 
                about_point = line.get_center()
            )
            line.label = label

        self.activate_zooming()
        lil_rect = self.little_rectangle        
        lil_rect.move_to(dot)
        lil_rect.shift(0.05*lil_rect.get_width()*LEFT)
        lil_rect.shift(0.2*lil_rect.get_height()*DOWN)
        lil_rect.save_state()
        lil_rect.set_height(FRAME_Y_RADIUS - MED_LARGE_BUFF)
        lil_rect.move_to(s_label, UP)
        lil_rect.shift(MED_SMALL_BUFF*UP)
        self.wait()
        self.play(
            FadeOut(rhs),
            dot.scale, 1./self.zoom_factor, point,
            s_label.scale, 1./self.zoom_factor, point,
            lil_rect.restore,
            run_time = 2
        )
        self.wait()
        for line in dx_line, dy_line:
            self.play(ShowCreation(line))
            self.play(Write(line.label, run_time = 1))
            self.wait()

        new_dot = Dot(color = dot.get_color())
        new_s_label = self.get_s_expression(
            "%d + dx"%int(self.example_point[0]),
            "%d + dy"%int(self.example_point[1]),
        )
        new_dot.set_height(dot.get_height())
        new_dot.move_to(new_point)
        new_s_label.set_height(s_label.get_height())
        new_s_label.scale(0.8)
        new_s_label.next_to(
            new_dot, DOWN, 
            buff = SMALL_BUFF/self.zoom_factor, 
            aligned_edge = LEFT
        )
        new_s_label.shift(MED_LARGE_BUFF*LEFT/self.zoom_factor)
        new_s_label.set_color(self.example_color)
        VGroup(*new_s_label[1][1][3:5]).set_color(GREEN)
        VGroup(*new_s_label[1][1][-3:-1]).set_color(RED)

        self.play(ShowCreation(new_dot))
        self.play(Write(new_s_label))
        self.wait()

        ds = self.derivative[1][0]
        self.play(FocusOn(ds))
        self.play(Indicate(ds))
        self.wait()

        self.tiny_step_group = VGroup(
            dx_line, dx_line.label,
            dy_line, dy_line.label,
            s_label, new_s_label, new_dot
        )

    def plug_in_example_values(self):
        deriv_example = TexMobject(
            "dS =", "2", "(3)", "\\,(-0.02)", "+", "2", "(4)", "\\,(-0.01)",
        )

        deriv_example[2].set_color(GREEN)
        deriv_example[6].set_color(RED)
        deriv_example.add_background_rectangle()
        deriv_example.scale(0.8)
        deriv_example.next_to(ORIGIN, UP, buff = SMALL_BUFF)
        deriv_example.to_edge(LEFT, buff = MED_SMALL_BUFF)

        def add_example_parts(*indices):
            self.play(*[
                ReplacementTransform(
                    self.derivative[1][i].copy(),
                    deriv_example[1][i],
                    run_time = 2
                )
                for i in indices
            ])

        self.play(FadeIn(deriv_example[0]))
        add_example_parts(0)
        self.wait()
        add_example_parts(1, 2, 4, 5, 6)
        self.wait(2)
        add_example_parts(3)
        self.wait()
        add_example_parts(7)
        self.wait()

        #React
        randy = Randolph()
        randy.next_to(ORIGIN, LEFT)
        randy.to_edge(DOWN)

        self.play(FadeIn(randy))
        self.play(
            randy.change_mode, "pondering",
            randy.look_at, deriv_example.get_left()
        )
        self.play(Blink(randy))
        self.play(randy.look_at, deriv_example.get_right())
        self.wait()
        self.play(
            Indicate(self.equation),
            randy.look_at, self.equation
        )
        self.play(Blink(randy))
        self.play(
            randy.change_mode, "thinking",
            randy.look_at, self.big_rectangle
        )
        self.wait(2)
        self.play(PiCreatureSays(
            randy, "Approximately",
            target_mode = "sassy"
        ))
        self.wait()
        self.play(RemovePiCreatureBubble(randy))
        self.play(randy.look_at, deriv_example)
        self.play(FadeOut(deriv_example))
        self.wait()

        self.randy = randy

    def ask_about_equalling_zero(self):
        dot = self.example_point_dot
        randy = self.randy

        equals_zero = TexMobject("=0")
        equals_zero.set_color(YELLOW)
        equals_zero.add_background_rectangle()
        equals_zero.next_to(self.derivative, RIGHT)

        self.play(
            Write(equals_zero),
            randy.change_mode, "confused",
            randy.look_at, equals_zero
        )
        self.wait()
        self.play(Blink(randy))
        self.play(
            randy.change_mode, "plain",
            randy.look_at, self.big_rectangle,
        )
        self.play(
            FadeOut(self.tiny_step_group),
            self.little_rectangle.move_to, dot,
        )
        self.wait()

        self.equals_zero = equals_zero

    def show_tangent_step(self):
        dot = self.example_point_dot
        randy = self.randy

        point = dot.get_center()
        step_vect = rotate_vector(point, np.pi/2)/get_norm(point)
        new_point = point + step_vect/self.zoom_factor
        interim_point = point[0]*RIGHT + new_point[1]*UP
        new_dot = dot.copy().move_to(new_point)

        step_line = Line(point, new_point, color = WHITE)
        dy_line = Line(point, interim_point, color = RED)
        dx_line = Line(interim_point, new_point, color = GREEN)

        s_label = TexMobject("S = 25")
        s_label.set_color(self.example_color)
        s_label.next_to(
            point, DOWN,
            buff = MED_LARGE_BUFF,
            aligned_edge = RIGHT
        )
        s_label.scale(1./self.zoom_factor, about_point = point)
        arrow1, arrow2 = [
            Arrow(
                s_label.get_top(), mob,
                preserve_tip_size_when_scaling = False,
                color = self.example_color,
                buff = SMALL_BUFF/self.zoom_factor,
                tip_length = 0.15/self.zoom_factor
            )
            for mob in (dot, new_dot)
        ]

        for line, tex, vect in (dy_line, "dy", RIGHT), (dx_line, "dx", UP):
            label = TexMobject(tex)
            label.set_color(line.get_color())
            label.next_to(line, vect)
            label.scale(
                1./self.zoom_factor, 
                about_point = line.get_center()
            )
            line.label = label

            self.play(ShowCreation(line))
            self.play(Write(label))
        self.play(ShowCreation(new_dot))
        self.play(
            randy.change_mode, "pondering",
            randy.look_at, self.big_rectangle
        )
        self.play(Blink(randy))
        self.wait()

        self.play(Write(s_label))
        self.play(ShowCreation(arrow1))
        self.wait()
        self.play(ReplacementTransform(arrow1.copy(), arrow2))
        self.wait(2)

    def point_out_equalling_zero(self):
        derivative = self.derivative
        equals_zero = self.equals_zero
        randy = self.randy

        self.play(
            FocusOn(equals_zero),
            self.randy.look_at, equals_zero
        )
        self.play(Indicate(equals_zero, color = RED))
        self.play(Blink(randy))
        self.play(randy.change_mode, "happy")
        self.play(randy.look_at, self.big_rectangle)
        self.wait(2)

    def show_tangent_line(self):
        randy = self.randy
        point = self.example_point_dot.get_center()
        line = Line(ORIGIN, 5*RIGHT)
        line.rotate(angle_of_vector(point)+np.pi/2)
        line.move_to(point)

        self.play(PiCreatureSays(
            randy, "Approximately...",
        ))
        self.play(Blink(randy))
        self.play(RemovePiCreatureBubble(randy))
        self.play(
            GrowFromCenter(line),
            randy.look_at, line
        )
        self.wait(2)
        self.play(
            self.little_rectangle.scale_in_place, self.zoom_factor/2,
            run_time = 4,
            rate_func = there_and_back
        )
        self.wait(2)

    ############

    def get_s_expression(self, x, y):
        result = TexMobject("S", "(%s, %s)"%(str(x), str(y)))
        result.add_background_rectangle()
        return result

class TryOtherExamples(TeacherStudentsScene):
    def construct(self):
        formula = TexMobject("\\sin(x)y^2 = x")
        formula.next_to(
            self.get_teacher().get_corner(UP+LEFT), UP,
            buff = MED_LARGE_BUFF,
            aligned_edge = RIGHT
        )


        self.teacher_says(
            """Nothing special
            about $x^2 + y^2 = 25$"""
        )
        self.wait()
        self.play(RemovePiCreatureBubble(
            self.get_teacher(),
            target_mode = "raise_right_hand"
        ))
        self.play(Write(formula, run_time = 1))
        self.change_student_modes(*["pondering"]*3)
        self.wait(2)
        self.play(formula.to_corner, UP+LEFT)
        self.wait()

class AlternateExample(ZoomedScene):
    CONFIG = {
        "example_color" : MAROON_B,
        "zoom_factor" : 10,
        "zoomed_canvas_corner" : DOWN+RIGHT,
        "zoomed_canvas_frame_shape" : (3, 4),
    }
    def construct(self): 
        self.add_plane()
        self.draw_graph()
        self.emphasize_meaning_of_points()
        self.zoom_in()
        self.show_tiny_step()
        self.ask_about_derivatives()
        self.differentiate_lhs()
        self.differentiate_rhs()
        self.put_step_on_curve()
        self.emphasize_equality()
        self.manipulate_to_find_dy_dx()

    def add_plane(self):
        formula = TexMobject("\\sin(x)y^2 = x")
        formula.to_corner(UP+LEFT)
        formula.add_background_rectangle()

        plane = NumberPlane(
            space_unit_to_x_unit = 0.75,
            x_radius = FRAME_WIDTH,
        )
        plane.fade()
        plane.add_coordinates()

        self.add(formula)
        self.play(Write(plane, run_time = 2), Animation(formula))
        self.wait()

        self.plane = plane
        self.formula = formula
        self.lhs = VGroup(*formula[1][:8])
        self.rhs = VGroup(formula[1][-1])

    def draw_graph(self):
        graphs = VGroup(*[
            FunctionGraph(
                lambda x : u*np.sqrt(x/np.sin(x)),
                num_steps = 200,
                x_min = x_min+0.1,
                x_max = x_max-0.1,
            )
            for u in [-1, 1]
            for x_min, x_max in [
                (-4*np.pi, -2*np.pi),
                (-np.pi, np.pi),
                (2*np.pi, 4*np.pi),
            ]
        ])
        graphs.stretch(self.plane.space_unit_to_x_unit, dim = 0)

        self.play(
            ShowCreation(
                graphs, 
                run_time = 3, 
                lag_ratio = 0
            ),
            Animation(self.formula)
        )
        self.wait()

        self.graphs = graphs

    def emphasize_meaning_of_points(self):
        graph = self.graphs[4]
        dot = Dot(color = self.example_color)
        label = TexMobject("(x, y)")
        label.add_background_rectangle()
        label.set_color(self.example_color)

        def update_dot(dot, alpha):
            prop = interpolate(0.9, 0.1, alpha)
            point = graph.point_from_proportion(prop)
            dot.move_to(point)
            return dot

        def update_label(label):
            point = dot.get_center()
            vect = np.array(point)/get_norm(point)
            vect[0] *= 2
            vect[1] *= -1
            label.move_to(
                point + vect*0.4*label.get_width()
            )

        update_dot(dot, 0)
        update_label(label)

        self.play(
            ShowCreation(dot),
            Write(label),
            run_time = 1
        )
        self.play(
            UpdateFromAlphaFunc(dot, update_dot),
            UpdateFromFunc(label, update_label),
            run_time = 3,
        )
        self.wait()
        self.play(*[
            ApplyMethod(
                label[1][i].copy().move_to, self.formula[1][j],
                run_time = 3,
                rate_func = squish_rate_func(smooth, count/6., count/6.+2./3)
            )
            for count, (i, j) in enumerate([(1, 4), (1, 9), (3, 6)])
        ])
        movers = self.get_mobjects_from_last_animation()
        self.wait()
        self.play(
            UpdateFromAlphaFunc(dot, update_dot),
            UpdateFromFunc(label, update_label),
            run_time = 3,
            rate_func = lambda t : 1-smooth(t)
        )
        self.wait()
        self.play(*[
            ApplyMethod(mover.set_fill, None, 0, remover = True)
            for mover in movers
        ])

        self.dot = dot
        self.label = label

    def zoom_in(self):
        dot = self.dot
        label = self.label

        self.activate_zooming()
        self.little_rectangle.scale(self.zoom_factor)
        self.little_rectangle.move_to(dot)
        self.wait()
        for mob in VGroup(dot, label), self.little_rectangle:
            self.play(
                ApplyMethod(
                    mob.scale, 1./self.zoom_factor,
                    method_kwargs = {"about_point" : dot.get_center()},
                    run_time = 1,
                )
            )
        self.wait()

    def show_tiny_step(self):
        dot = self.dot
        label = self.label
        point = dot.get_center()
        step_vect = 1.2*(UP+LEFT)/float(self.zoom_factor)
        new_point = point + step_vect
        interim_point = new_point[0]*RIGHT + point[1]*UP

        dx_line = Line(point, interim_point, color = GREEN)
        dy_line = Line(interim_point, new_point, color = RED)
        for line, tex, vect in (dx_line, "dx", DOWN), (dy_line, "dy", LEFT):
            label = TexMobject(tex)
            label.next_to(line, vect, buff = SMALL_BUFF)
            label.set_color(line.get_color())
            label.scale(1./self.zoom_factor, about_point = line.get_center())
            label.add_background_rectangle()
            line.label = label

        arrow = Arrow(
            point, new_point, buff = 0,
            tip_length = 0.15/self.zoom_factor,
            color = WHITE
        )

        self.play(ShowCreation(arrow))
        for line in dx_line, dy_line:
            self.play(ShowCreation(line), Animation(arrow))
            self.play(Write(line.label, run_time = 1))
        self.wait()

        self.step_group = VGroup(
            arrow, dx_line, dx_line.label, dy_line, dy_line.label
        )

    def ask_about_derivatives(self):
        formula = self.formula
        lhs, rhs = self.lhs, self.rhs

        word = TextMobject("Change?")
        word.add_background_rectangle()
        word.next_to(
            Line(lhs.get_center(), rhs.get_center()),
            DOWN, buff = 1.5*LARGE_BUFF
        )

        arrows = VGroup(*[
            Arrow(word, part)
            for part in (lhs, rhs)
        ])

        self.play(FocusOn(formula))
        self.play(
            Write(word),
            ShowCreation(arrows)
        )
        self.wait()
        self.play(*list(map(FadeOut, [word, arrows])))

    def differentiate_lhs(self):
        formula = self.formula
        lhs = self.lhs
        brace = Brace(lhs, DOWN, buff = SMALL_BUFF)
        sine_x = VGroup(*lhs[:6])
        sine_rect = BackgroundRectangle(sine_x)
        y_squared = VGroup(*lhs[6:])

        mnemonic = TextMobject(
            "``", 
            "Left", " d-Right", " + ",
            "Right",  " d-Left"
            "''",
            arg_separator = ""
        )
        mnemonic.set_color_by_tex("d-Right", RED)
        mnemonic.set_color_by_tex("d-Left", GREEN)
        mnemonic.add_background_rectangle()
        mnemonic.set_width(FRAME_X_RADIUS-2*MED_LARGE_BUFF)
        mnemonic.next_to(ORIGIN, UP)
        mnemonic.to_edge(LEFT)

        derivative = TexMobject(
            "\\sin(x)", "(2y\\,dy)", "+", 
            "y^2", "(\\cos(x)\\,dx)",
        )
        derivative.set_color_by_tex("dx", GREEN)
        derivative.set_color_by_tex("dy", RED)
        derivative.set_width(FRAME_X_RADIUS - 2*MED_LARGE_BUFF)
        derivative.next_to(
            brace, DOWN, 
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT
        )
        derivative_rects = [
            BackgroundRectangle(VGroup(*subset))
            for subset in (derivative[:2], derivative[2:])
        ]
        derivative_rects[1].stretch(1.05, dim = 0)

        self.play(GrowFromCenter(brace))
        self.play(Write(mnemonic))
        self.wait()
        pairs = [
            (sine_rect, derivative_rects[0]),
            (sine_x, derivative[0]),
            (y_squared, derivative[1]),
            (sine_rect, derivative_rects[1]),
            (y_squared, derivative[2]),
            (y_squared, derivative[3]),
            (sine_x, derivative[4]),
        ]
        for pairs_subset in pairs[:3], pairs[3:]:
            self.play(*[
                ReplacementTransform(m1.copy(), m2, path_arc = np.pi/2)
                for m1, m2 in pairs_subset
            ])
            self.wait()
            self.play(Indicate(pairs_subset[-1][1]))
            self.wait()
        self.wait()
        self.play(FadeOut(mnemonic))

        self.lhs_derivative = VGroup(*derivative_rects+[derivative])
        self.lhs_brace = brace

    def differentiate_rhs(self):
        lhs_derivative = self.lhs_derivative
        lhs_brace = self.lhs_brace
        rhs = self.rhs

        equals, dx = equals_dx = TexMobject("=", "dx")
        equals_dx.scale(0.9)
        equals_dx.set_color_by_tex("dx", GREEN)
        equals_dx.add_background_rectangle()
        equals_dx.next_to(lhs_derivative, RIGHT, buff = SMALL_BUFF)

        circle = Circle(color = GREEN)
        circle.replace(self.rhs)
        circle.scale_in_place(1.7)

        arrow = Arrow(rhs.get_right(), dx.get_top())
        arrow.set_color(GREEN)

        self.play(ReplacementTransform(lhs_brace, circle))
        self.play(ShowCreation(arrow))
        self.play(Write(equals_dx))
        self.wait()
        self.play(*list(map(FadeOut, [circle, arrow])))

        self.equals_dx = equals_dx

    def put_step_on_curve(self):
        dot = self.dot
        point = dot.get_center()
        graph = self.graphs[4]
        arrow, dx_line, dx_line.label, dy_line, dy_line.label = self.step_group

        #Find graph point at right x_val
        arrow_end = arrow.get_end()
        graph_points = [
            graph.point_from_proportion(alpha)
            for alpha in np.linspace(0, 1, 1000)
        ]
        distances = np.apply_along_axis(
            lambda p : np.abs(p[0] - arrow_end[0]),
            1, graph_points
        )
        index = np.argmin(distances)
        new_end_point = graph_points[index]

        lil_rect = self.little_rectangle
        self.play(
            arrow.put_start_and_end_on, point, new_end_point,
            dy_line.put_start_and_end_on, 
                dy_line.get_start(), new_end_point,
            MaintainPositionRelativeTo(dy_line.label, dy_line),
            lil_rect.shift, lil_rect.get_height()*DOWN/3,
            run_time = 2
        )
        self.wait(2)

    def emphasize_equality(self):
        self.play(FocusOn(self.lhs))
        self.wait()
        for mob in self.lhs, self.rhs:
            self.play(Indicate(mob))
        self.wait()

    def manipulate_to_find_dy_dx(self):
        full_derivative = VGroup(
            self.lhs_derivative, self.equals_dx
        )
        brace = Brace(full_derivative, DOWN, buff = SMALL_BUFF)
        words = brace.get_text(
            "Commonly, solve for", "$dy/dx$",
            buff = SMALL_BUFF
        )
        VGroup(*words[1][:2]).set_color(RED)
        VGroup(*words[1][3:]).set_color(GREEN)
        words.add_background_rectangle()

        self.play(GrowFromCenter(brace))
        self.play(Write(words))
        self.wait()

        randy = Randolph()
        randy.to_corner(DOWN+LEFT)
        randy.look_at(full_derivative)

        self.play(FadeIn(randy))
        self.play(randy.change_mode, "confused")
        self.play(Blink(randy))
        self.wait(2)
        self.play(randy.change_mode, "pondering")
        self.play(Blink(randy))
        self.wait()

class AskAboutNaturalLog(TeacherStudentsScene):
    def construct(self):
        exp_deriv = TexMobject("\\frac{d(e^x)}{dx} = e^x")
        for i in 2, 3, 9, 10:
            exp_deriv[i].set_color(BLUE)
        log_deriv = TexMobject("\\frac{d(\\ln(x))}{dx} = ???")
        VGroup(*log_deriv[2:2+5]).set_color(GREEN)

        for deriv in exp_deriv, log_deriv:
            deriv.next_to(self.get_teacher().get_corner(UP+LEFT), UP)

        self.teacher_says(
            """We can find
            new derivatives""",
            target_mode = "hooray"
        )
        self.change_student_modes(*["happy"]*3)
        self.play(RemovePiCreatureBubble(
            self.get_teacher(),
            target_mode = "raise_right_hand"
        ))
        self.play(Write(exp_deriv))
        self.wait()
        self.play(
            Write(log_deriv),
            exp_deriv.next_to, log_deriv, UP, LARGE_BUFF,
            *[
                ApplyMethod(pi.change_mode, "confused")
                for pi in self.get_pi_creatures()
            ]
        )
        self.wait(3)

class DerivativeOfNaturalLog(ZoomedScene):
    CONFIG = {
        "zoom_factor" : 10,
        "zoomed_canvas_corner" : DOWN+RIGHT,
        "example_color" : MAROON_B,
    }
    def construct(self):
        should_skip_animations = self.skip_animations
        self.skip_animations = True

        self.add_plane()
        self.draw_graph()
        self.describe_as_implicit_curve()
        self.slope_gives_derivative()
        self.rearrange_equation()
        self.take_derivative()
        self.show_tiny_nudge()
        self.note_derivatives()
        self.solve_for_dy_dx()
        self.skip_animations = should_skip_animations
        self.show_slope_above_x()

    def add_plane(self):
        plane = NumberPlane()
        plane.fade()
        plane.add_coordinates()
        self.add(plane)
        self.plane = plane

    def draw_graph(self):
        graph = FunctionGraph(
            np.log, 
            x_min = 0.01, 
            x_max = FRAME_X_RADIUS,
            num_steps = 100
        )
        formula = TexMobject("y = \\ln(x)")
        formula.next_to(ORIGIN, LEFT, buff = MED_LARGE_BUFF)
        formula.to_edge(UP)
        formula.add_background_rectangle()

        self.add(formula)
        self.play(ShowCreation(graph))
        self.wait()

        self.formula = formula
        self.graph = graph

    def describe_as_implicit_curve(self):
        formula = self.formula #y = ln(x)
        graph = self.graph

        dot = Dot(color = self.example_color)
        label = TexMobject("(x, y)")
        label.add_background_rectangle()
        label.set_color(self.example_color)

        def update_dot(dot, alpha):
            prop = interpolate(0.1, 0.7, alpha)
            point = graph.point_from_proportion(prop)
            dot.move_to(point)
            return dot

        def update_label(label):
            point = dot.get_center()
            vect = point - FRAME_Y_RADIUS*(DOWN+RIGHT)
            vect = vect/get_norm(vect)
            label.move_to(
                point + vect*0.5*label.get_width()
            )

        update_dot(dot, 0)
        update_label(label)

        self.play(*list(map(FadeIn, [dot, label])))
        self.play(
            UpdateFromAlphaFunc(dot, update_dot),
            UpdateFromFunc(label, update_label),
            run_time = 3,
        )
        self.wait()
        xy_start = VGroup(label[1][1], label[1][3]).copy()
        xy_end = VGroup(formula[1][5], formula[1][0]).copy()
        xy_end.set_color(self.example_color)
        self.play(Transform(
            xy_start, xy_end,
            run_time = 2,
        ))
        self.wait()
        self.play(
            UpdateFromAlphaFunc(dot, update_dot),
            UpdateFromFunc(label, update_label),
            run_time = 3,
            rate_func = lambda t : 1-0.6*smooth(t),
        )
        self.play(*list(map(FadeOut, [xy_start, label])))

        self.dot = dot

    def slope_gives_derivative(self):
        dot = self.dot
        point = dot.get_center()
        line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS)
        slope = 1./point[0]
        line.rotate(np.arctan(slope))
        line.move_to(point)

        new_point = line.point_from_proportion(0.6)
        interim_point = point[0]*RIGHT + new_point[1]*UP
        dy_line = Line(point, interim_point, color = RED)
        dx_line = Line(interim_point, new_point, color = GREEN)

        equation = TexMobject(
            "\\text{Slope} = ",
            "\\frac{dy}{dx} = ",
            "\\frac{d(\\ln(x))}{dx}",
        )
        VGroup(*equation[1][:2]).set_color(RED)
        VGroup(*equation[2][:8]).set_color(RED)
        VGroup(*equation[1][3:5]).set_color(GREEN)
        VGroup(*equation[2][-2:]).set_color(GREEN)
        for part in equation:
            rect = BackgroundRectangle(part)
            rect.stretch_in_place(1.2, 0)
            part.add_to_back(rect)
        equation.scale(0.8)
        equation.next_to(ORIGIN, RIGHT)
        equation.to_edge(UP, buff = MED_SMALL_BUFF)


        self.play(
            GrowFromCenter(line),
            Animation(dot)
        )
        self.play(ShowCreation(VGroup(dy_line, dx_line)))
        for part in equation:
            self.play(Write(part, run_time = 2))
        self.wait()

        self.dx_line, self.dy_line = dx_line, dy_line
        self.slope_equation = equation
        self.tangent_line = line

    def rearrange_equation(self):
        formula = self.formula
        y, eq = formula[1][:2]
        ln = VGroup(*formula[1][2:4])
        x = formula[1][5]

        new_formula = TexMobject("e", "^y", "=", "x")
        e, new_y, new_eq, new_x = new_formula
        new_formula.next_to(
            formula, DOWN, 
            buff = MED_LARGE_BUFF,
        )
        rect = BackgroundRectangle(new_formula)

        y = new_y.copy().replace(y)
        self.play(Indicate(formula, scale_factor = 1))
        self.play(ReplacementTransform(ln.copy(), e))
        self.play(ReplacementTransform(y, new_y))
        self.play(ReplacementTransform(eq.copy(), new_eq))
        self.play(
            FadeIn(rect),
            Animation(VGroup(e, new_y, new_eq)),
            ReplacementTransform(x.copy(), new_x)
        )
        self.wait(2)
        for mob in e, new_y, new_x:
            self.play(Indicate(mob))
        self.wait()

        self.new_formula = new_formula

    def take_derivative(self):
        new_formula = self.new_formula
        e, y, eq, x = new_formula
        derivative = TexMobject("e", "^y", "\\,dy", "=", "dx")
        new_e, new_y, dy, new_eq, dx = derivative
        derivative.next_to(new_formula, DOWN, MED_LARGE_BUFF)
        derivative.add_background_rectangle()
        dx.set_color(GREEN)
        dy.set_color(RED)

        pairs = [
            (VGroup(e, y), VGroup(new_e, new_y)),
            (new_y, dy),
            (eq, new_eq),
            (x, dx)
        ]
        for start, target in pairs:
            self.play(
                ReplacementTransform(start.copy(), target)
            )
        self.play(FadeIn(derivative[0]), Animation(derivative[1]))
        self.remove(derivative, pairs[0][1])
        self.add(derivative)
        self.wait()

        self.derivative = derivative

    def show_tiny_nudge(self):
        dot = self.dot
        point = dot.get_center()
        dx_line = self.dx_line
        dy_line = self.dy_line
        group = VGroup(dot, dx_line, dy_line)
        self.play(group.scale, 1./self.zoom_factor, point)
        for line, tex, vect in (dx_line, "dx", UP), (dy_line, "dy", LEFT):
            label = TexMobject(tex)
            label.add_background_rectangle()
            label.next_to(line, vect, buff = SMALL_BUFF)
            label.set_color(line.get_color())
            label.scale(
                1./self.zoom_factor, 
                about_point = line.get_center()
            )
            line.label = label

        self.activate_zooming()
        lil_rect = self.little_rectangle
        lil_rect.move_to(group)
        lil_rect.scale_in_place(self.zoom_factor)
        self.play(lil_rect.scale_in_place, 1./self.zoom_factor)
        self.play(Write(dx_line.label))
        self.play(Write(dy_line.label))
        self.wait()

    def note_derivatives(self):
        e, y, dy, eq, dx = self.derivative[1]

        self.play(FocusOn(e))
        self.play(Indicate(VGroup(e, y, dy)))
        self.wait()
        self.play(Indicate(dx))
        self.wait()

    def solve_for_dy_dx(self):
        e, y, dy, eq, dx = self.derivative[1]
        ey_group = VGroup(e, y)
        original_rect = self.derivative[0]

        rearranged = TexMobject(
            "{dy \\over ", " dx}", "=", "{1 \\over ", "e", "^y}"
        )
        new_dy, new_dx, new_eq, one_over, new_e, new_y = rearranged
        new_ey_group = VGroup(new_e, new_y)
        new_dx.set_color(GREEN)
        new_dy.set_color(RED)
        rearranged.shift(eq.get_center() - new_eq.get_center())
        rearranged.shift(MED_SMALL_BUFF*DOWN)
        new_rect = BackgroundRectangle(rearranged)

        self.play(*[
            ReplacementTransform(
                m1, m2, 
                run_time = 2,
                path_arc = -np.pi/2,
            )
            for m1, m2 in [
                (original_rect, new_rect),
                (dx, new_dx),
                (dy, new_dy),
                (eq, new_eq),
                (ey_group, new_ey_group),
                (e.copy(), one_over)
            ]
        ])
        self.wait()

        #Change denominator
        e, y, eq, x = self.new_formula
        ey_group = VGroup(e, y).copy()
        ey_group.set_color(YELLOW)
        x_copy = x.copy()

        self.play(new_ey_group.set_color, YELLOW)
        self.play(Transform(new_ey_group, ey_group))
        self.play(
            new_ey_group.set_color, WHITE,
            x_copy.set_color, YELLOW
        )
        self.play(x_copy.next_to, one_over, DOWN, MED_SMALL_BUFF)
        self.wait(2)

        equals_one_over_x = VGroup(
            new_eq, one_over, x_copy
        ).copy()
        rect = BackgroundRectangle(equals_one_over_x)
        rect.stretch_in_place(1.1, dim = 0)
        equals_one_over_x.add_to_back(rect)

        self.play(
            equals_one_over_x.next_to, 
            self.slope_equation, RIGHT, 0,
            run_time = 2
        )
        self.wait()

    def show_slope_above_x(self):
        line = self.tangent_line
        start_x = line.get_center()[0]
        target_x = 0.2
        graph = FunctionGraph(
            lambda x : 1./x, 
            x_min = 0.1,
            x_max = FRAME_X_RADIUS,
            num_steps = 100,
            color = PINK,
        )

        def update_line(line, alpha):
            x = interpolate(start_x, target_x, alpha)
            point = x*RIGHT + np.log(x)*UP
            angle = np.arctan(1./x)
            line.rotate(angle - line.get_angle())
            line.move_to(point)

        self.play(UpdateFromAlphaFunc(
            line, update_line,
            rate_func = there_and_back,
            run_time = 6
        ))
        self.wait()
        self.play(ShowCreation(graph, run_time = 3))
        self.wait()
        self.play(UpdateFromAlphaFunc(
            line, update_line,
            rate_func = there_and_back,
            run_time = 6
        ))
        self.wait()

class FinalWords(TeacherStudentsScene):
    def construct(self):
        words = TextMobject(
            "This is a peek into \\\\",
            "Multivariable", "calculus"
        )
        mvc = VGroup(*words[1:])
        words.set_color_by_tex("Multivariable", YELLOW)
        formula = TexMobject("f(x, y) = \\sin(x)y^2")
        formula.next_to(self.get_teacher().get_corner(UP+LEFT), UP)

        self.teacher_says(words)
        self.change_student_modes("erm", "hooray", "sassy")
        self.play(
            FadeOut(self.teacher.bubble),
            FadeOut(VGroup(*words[:1])),
            mvc.to_corner, UP+LEFT,
            self.teacher.change_mode, "raise_right_hand",
            self.teacher.look_at, formula,
            Write(formula, run_time = 2),
        )
        self.change_student_modes("pondering", "confused", "thinking")
        self.wait(3)

        ##Show series
        series = VideoSeries()
        series.to_edge(UP)
        video = series[5]
        lim = TexMobject("\\lim_{h \\to 0} \\frac{f(x+h)-f(x)}{h}")
        self.play(
            FadeOut(mvc),
            FadeOut(formula),
            self.teacher.change_mode, "plain",
            FadeIn(
                series, run_time = 2,
                lag_ratio = 0.5,
            ),
        )
        self.play(
            video.set_color, YELLOW,
            video.shift, video.get_height()*DOWN/2
        )
        lim.next_to(video, DOWN)
        self.play(
            Write(lim),
            *it.chain(*[
                [pi.change_mode, "pondering", pi.look_at, lim]
                for pi in self.get_pi_creatures()
            ])
        )
        self.wait(3)

class Chapter6PatreonThanks(PatreonThanks):
    CONFIG = {
        "specific_patrons" : [
            "Ali  Yahya",
            "Meshal  Alshammari",
            "CrypticSwarm    ",
            "Nathan Pellegrin",
            "Karan Bhargava", 
            "Justin Helps",
            "Ankit   Agarwal",
            "Yu  Jun",
            "Dave    Nicponski",
            "Damion  Kistler",
            "Juan    Benet",
            "Othman  Alikhan",
            "Justin Helps",
            "Markus  Persson",
            "Dan Buchoff",
            "Derek   Dai",
            "Joseph  John Cox",
            "Luc Ritchie",
            "Daan Smedinga",
            "Jonathan Eppele",
            "Nils Schneider",
            "Albert Nguyen",
            "Mustafa Mahdi",
            "Mathew Bramson",
            "Guido   Gambardella",
            "Jerry   Ling",
            "Mark    Govea",
            "Vecht",
            "Shimin Kuang",
            "Rish    Kundalia",
            "Achille Brighton",
            "Kirk    Werklund",
            "Ripta   Pasay",
            "Felipe  Diniz",
        ]
    }

class Thumbnail(AlternateExample):
    def construct(self):
        title = VGroup(*list(map(TextMobject, [
            "Implicit", "Differentiation"
        ])))
        title.arrange(DOWN)
        title.scale(3)
        title.next_to(ORIGIN, UP)

        for word in title:
            word.add_background_rectangle()

        self.add_plane()
        self.draw_graph()
        self.graphs.set_stroke(width = 8)
        self.remove(self.formula)
        self.add(title)
