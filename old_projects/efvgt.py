from manimlib.imports import *

ADDER_COLOR = GREEN
MULTIPLIER_COLOR = YELLOW

def normalize(vect):
    norm = get_norm(vect)
    if norm == 0:
        return OUT
    else:
        return vect/norm

def get_composite_rotation_angle_and_axis(angles, axes):
    angle1, axis1 = 0, OUT
    for angle2, axis2 in zip(angles, axes):
        ## Figure out what (angle3, axis3) is the same 
        ## as first applying (angle1, axis1), then (angle2, axis2)
        axis2 = normalize(axis2)
        dot = np.dot(axis2, axis1)
        cross = np.cross(axis2, axis1)
        angle3 = 2*np.arccos(
            np.cos(angle2/2)*np.cos(angle1/2) - \
            np.sin(angle2/2)*np.sin(angle1/2)*dot
        )
        axis3 = (
            np.sin(angle2/2)*np.cos(angle1/2)*axis2 + \
            np.cos(angle2/2)*np.sin(angle1/2)*axis1 + \
            np.sin(angle2/2)*np.sin(angle1/2)*cross
        )
        axis3 = normalize(axis3)
        angle1, axis1 = angle3, axis3

    if angle1 > np.pi:
        angle1 -= 2*np.pi
    return angle1, axis1

class ConfettiSpiril(Animation):
    CONFIG = {
        "x_start" : 0,
        "spiril_radius" : 0.5,
        "num_spirils" : 4,
        "run_time" : 10,
        "rate_func" : None,
    }
    def __init__(self, mobject, **kwargs):
        digest_config(self, kwargs)
        mobject.next_to(self.x_start*RIGHT + FRAME_Y_RADIUS*UP, UP)
        self.total_vert_shift = \
            FRAME_HEIGHT + mobject.get_height() + 2*MED_SMALL_BUFF
        
        Animation.__init__(self, mobject, **kwargs)

    def interpolate_submobject(self, submobject, starting_submobject, alpha):
        submobject.points = np.array(starting_submobject.points)

    def interpolate_mobject(self, alpha):
        Animation.interpolate_mobject(self, alpha)
        angle = alpha*self.num_spirils*2*np.pi
        vert_shift = alpha*self.total_vert_shift

        start_center = self.mobject.get_center()
        self.mobject.shift(self.spiril_radius*OUT)
        self.mobject.rotate(angle, axis = UP, about_point = start_center)
        self.mobject.shift(vert_shift*DOWN)

def get_confetti_animations(num_confetti_squares):
    colors = [RED, YELLOW, GREEN, BLUE, PURPLE, RED]
    confetti_squares = [
        Square(
            side_length = 0.2,
            stroke_width = 0,
            fill_opacity = 0.75,
            fill_color = random.choice(colors),
        )
        for x in range(num_confetti_squares)
    ]
    confetti_spirils = [
        ConfettiSpiril(
            square,
            x_start = 2*random.random()*FRAME_X_RADIUS - FRAME_X_RADIUS,
            rate_func = squish_rate_func(lambda t : t, a, a+0.5)
        )
        for a, square in zip(
            np.linspace(0, 0.5, num_confetti_squares),
            confetti_squares
        )
    ]
    return confetti_spirils

class Anniversary(TeacherStudentsScene):
    CONFIG = {
        "num_confetti_squares" : 50,
    }
    def construct(self):
        self.celebrate()
        self.complain()

    def celebrate(self):
        title = TextMobject("2 year Anniversary!")
        title.scale(1.5)
        title.to_edge(UP)

        first_video = Rectangle(
            height = 2, width = 2*(16.0/9),
            stroke_color = WHITE,
            fill_color = "#111111",
            fill_opacity = 0.75,
        )
        first_video.next_to(self.get_teacher(), UP+LEFT)
        first_video.shift(RIGHT)
        formula = TexMobject("e^{\\pi i} = -1")
        formula.move_to(first_video)
        first_video.add(formula)

        hats = self.get_party_hats()
        confetti_spirils = get_confetti_animations(
            self.num_confetti_squares
        )
        self.play(
            Write(title, run_time = 2),
            *[
                ApplyMethod(pi.change_mode, "hooray")
                for pi in self.get_pi_creatures()
            ]
        )
        self.play(
            DrawBorderThenFill(
                hats,
                lag_ratio = 0.5,
                rate_func=linear,
                run_time = 2,
            ),
            *confetti_spirils + [
                Succession(
                    Animation(pi, run_time = 2),
                    ApplyMethod(pi.look, UP+LEFT),
                    ApplyMethod(pi.look, UP+RIGHT),
                    Animation(pi),
                    ApplyMethod(pi.look_at, first_video),
                    rate_func=linear
                )
                for pi in self.get_students()
            ] + [
                Succession(
                    Animation(self.get_teacher(), run_time = 2),
                    Blink(self.get_teacher()),
                    Animation(self.get_teacher(), run_time = 2),
                    ApplyMethod(self.get_teacher().change_mode, "raise_right_hand"),
                    rate_func=linear
                ),
                DrawBorderThenFill(
                    first_video, 
                    run_time = 10,
                    rate_func = squish_rate_func(smooth, 0.5, 0.7)
                )
            ]
        )
        self.change_student_modes(*["confused"]*3)

    def complain(self):
        self.student_says(
            "Why were you \\\\ talking so fast?",
            student_index = 0,
            target_mode = "sassy",
        )
        self.change_student_modes(*["sassy"]*3)
        self.play(self.get_teacher().change_mode, "shruggie")
        self.wait(2)

    def get_party_hats(self):
        hats = VGroup(*[
            PartyHat(
                pi_creature = pi,
                height = 0.5*pi.get_height()
            )
            for pi in self.get_pi_creatures()
        ])
        max_angle = np.pi/6
        for hat in hats:
            hat.rotate(
                random.random()*2*max_angle - max_angle,
                about_point = hat.get_bottom()
            )
        return hats

class HomomophismPreview(Scene):
    def construct(self):
        raise Exception("Meant as a place holder, not to be excecuted")

class WatchingScreen(PiCreatureScene):
    CONFIG = {
        "screen_height" : 5.5
    }
    def create_pi_creatures(self):
        randy = Randolph().to_corner(DOWN+LEFT)
        return VGroup(randy)

    def construct(self):
        screen = Rectangle(height = 9, width = 16)
        screen.set_height(self.screen_height)
        screen.to_corner(UP+RIGHT)

        self.add(screen)
        for mode in "erm", "pondering", "confused":
            self.wait()
            self.change_mode(mode)
            self.play(Animation(screen))
            self.wait()

class LetsStudyTheBasics(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("Let's learn some \\\\ group theory!")
        self.change_student_modes(*["hooray"]*3)
        self.wait(2)

class JustGiveMeAQuickExplanation(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "I ain't got \\\\ time for this!",
            target_mode = "angry",
        )
        self.play(*it.chain(*[
            [
                pi.change_mode, "hesitant", 
                pi.look_at, self.get_students()[1].eyes
            ]
            for pi in self.get_students()[::2]
        ]))
        self.wait(2)

class QuickExplanation(ComplexTransformationScene):
    CONFIG = {
        "plane_config" : {
            "x_line_frequency" : 1,
            "y_line_frequency" : 1,
            "secondary_line_ratio" : 1,
            "space_unit_to_x_unit" : 1.5,
            "space_unit_to_y_unit" : 1.5,
        },
        "background_fade_factor" : 0.2,
        "background_label_scale_val" : 0.7,
        "velocity_color" : RED,
        "position_color" : YELLOW,
    }
    def construct(self):
        # self.add_transformable_plane()
        self.add_equation()
        self.add_explanation()
        self.add_vectors()

    def add_equation(self):
        equation = TexMobject(
            "\\frac{d(e^{it})}{dt}",
            "=",
            "i", "e^{it}"
        )
        equation[0].set_color(self.velocity_color)
        equation[-1].set_color(self.position_color)
        equation.add_background_rectangle()        
        brace = Brace(equation, UP)
        equation.add(brace)
        brace_text = TextMobject(
            "Velocity vector", "is a", 
            "$90^\\circ$ \\\\ rotation", 
            "of", "position vector"
        )
        brace_text[0].set_color(self.velocity_color)
        brace_text[-1].set_color(self.position_color)
        brace_text.add_background_rectangle()
        brace_text.scale(0.8)
        brace_text.to_corner(UP+LEFT, buff = MED_SMALL_BUFF)
        equation.next_to(brace_text, DOWN)

        self.add_foreground_mobjects(brace_text, equation)
        self.brace_text = brace_text

    def add_explanation(self):
        words = TextMobject("""
            Only a walk around the unit
            circle at rate 1 satisfies both
            this property and e^0 = 1.
        """)
        words.scale(0.8)
        words.add_background_rectangle()
        words.to_corner(UP+RIGHT, buff = MED_SMALL_BUFF)
        arrow = Arrow(RIGHT, 1.5*LEFT, color = WHITE)
        arrow.to_edge(UP)

        self.add(words, arrow)

    def add_vectors(self):
        right = self.z_to_point(1)
        s_vector = Arrow(
            ORIGIN, right,
            tip_length = 0.2,
            buff = 0,            
            color = self.position_color,
        )

        v_vector = s_vector.copy().rotate(np.pi/2)
        v_vector.set_color(self.velocity_color)
        circle = Circle(
            radius = self.z_to_point(1)[0],
            color = self.position_color
        )

        self.wait(2)
        self.play(ShowCreation(s_vector))
        self.play(ReplacementTransform(
            s_vector.copy(), v_vector, path_arc = np.pi/2
        ))
        self.wait()
        self.play(v_vector.shift, right)
        self.wait()
        self.vectors = VGroup(s_vector, v_vector)

        kwargs = {
            "rate_func" : None,
            "run_time" : 5,
        }
        rotation = Rotating(self.vectors, about_point = ORIGIN, **kwargs)
        self.play(
            ShowCreation(circle, **kwargs),
            rotation            
        )
        self.play(rotation)
        self.play(rotation)

class SymmetriesOfSquare(ThreeDScene):
    CONFIG = {
        "square_config" : {
            "side_length" : 2,
            "stroke_width" : 0,
            "fill_color" : BLUE,
            "fill_opacity" : 0.75,
        },
        "dashed_line_config" : {},
    }
    def construct(self):
        self.add_title()
        self.ask_about_square_symmetry()
        self.talk_through_90_degree_rotation()
        self.talk_through_vertical_flip()
        self.confused_by_lack_of_labels()
        self.add_labels()
        self.show_full_group()
        self.show_top_actions()
        self.show_bottom_actions()
        self.name_dihedral_group()

    def add_title(self):
        title = TextMobject("Groups", "$\\leftrightarrow$", "Symmetry")
        title.to_edge(UP)

        for index in 0, 2:
            self.play(Write(title[index], run_time = 1))
        self.play(GrowFromCenter(title[1]))
        self.wait()

        self.title = title

    def ask_about_square_symmetry(self):
        brace = Brace(self.title[-1])
        q_marks = brace.get_text("???")

        self.square = Square(**self.square_config)

        self.play(DrawBorderThenFill(self.square))
        self.play(GrowFromCenter(brace), Write(q_marks))
        self.rotate_square()
        self.wait()
        for axis in UP, UP+RIGHT:
            self.flip_square(axis)
            self.wait()
        self.rotate_square(-np.pi)
        self.wait()
        self.play(*list(map(FadeOut, [brace, q_marks])))

    def talk_through_90_degree_rotation(self):
        arcs = self.get_rotation_arcs(self.square, np.pi/2)

        self.play(*list(map(ShowCreation, arcs)))
        self.wait()
        self.rotate_square(np.pi/2, run_time = 2)
        self.wait()
        self.play(FadeOut(arcs))
        self.wait()

    def talk_through_vertical_flip(self):
        self.flip_square(UP, run_time = 2)
        self.wait()

    def confused_by_lack_of_labels(self):
        randy = Randolph(mode = "confused")
        randy.next_to(self.square, LEFT, buff = LARGE_BUFF)
        randy.to_edge(DOWN)
        self.play(FadeIn(randy))
        for axis in OUT, RIGHT, UP:
            self.rotate_square(
                angle = np.pi, axis = axis,
                added_anims = [randy.look_at, self.square.points[0]]
            )
        self.play(Blink(randy))
        self.wait()

        self.randy = randy

    def add_labels(self):
        self.add_randy_to_square(self.square)

        self.play(
            FadeIn(self.square.randy),
            self.randy.change_mode, "happy",
            self.randy.look_at, self.square.randy.eyes
        )
        self.play(Blink(self.randy))
        self.play(FadeOut(self.randy))

        self.wait()

    def show_full_group(self):
        new_title = TextMobject("Group", "of", "symmetries")
        new_title.move_to(self.title)

        all_squares = VGroup(*[
            self.square.copy().scale(0.5)
            for x in range(8)
        ])
        all_squares.arrange(RIGHT, buff = LARGE_BUFF)

        top_squares = VGroup(*all_squares[:4])
        bottom_squares = VGroup(*all_squares[4:])
        bottom_squares.next_to(top_squares, DOWN, buff = LARGE_BUFF)

        all_squares.set_width(FRAME_WIDTH-2*LARGE_BUFF)
        all_squares.center()
        all_squares.to_edge(DOWN, buff = LARGE_BUFF)

        self.play(ReplacementTransform(self.square, all_squares[0]))
        self.play(ReplacementTransform(self.title, new_title))
        self.title = new_title
        self.play(*[
            ApplyMethod(mob.set_color, GREY)
            for mob in self.title[1:]
        ])

        for square, angle in zip(all_squares[1:4], [np.pi/2, np.pi, -np.pi/2]):
            arcs = self.get_rotation_arcs(square, angle, MED_SMALL_BUFF)
            self.play(*list(map(FadeIn, [square, arcs])))
            square.rotation_kwargs = {"angle" : angle}
            self.rotate_square(square = square, **square.rotation_kwargs)
            square.add(arcs)

        for square, axis in zip(bottom_squares, [RIGHT, RIGHT+UP, UP, UP+LEFT]):
            axis_line = self.get_axis_line(square, axis)
            self.play(FadeIn(square))
            self.play(ShowCreation(axis_line))
            square.rotation_kwargs = {"angle" : np.pi, "axis" : axis}
            self.rotate_square(square = square, **square.rotation_kwargs)
            square.add(axis_line)
        self.wait()

        self.all_squares = all_squares

    def show_top_actions(self):
        all_squares = self.all_squares

        self.play(Indicate(all_squares[0]))
        self.wait()

        self.play(*[
            Rotate(
                square,
                rate_func = lambda t : -there_and_back(t),
                run_time = 3,
                about_point = square.get_center(),
                **square.rotation_kwargs
            )
            for square in all_squares[1:4]
        ])
        self.wait()

    def show_bottom_actions(self):
        for square in self.all_squares[4:]:
            self.rotate_square(
                square = square,
                rate_func = there_and_back,
                run_time = 2,
                **square.rotation_kwargs
            )
        self.wait()

    def name_dihedral_group(self):
        new_title = TextMobject(
            "``Dihedral group'' of order 8"
        )
        new_title.to_edge(UP)

        self.play(FadeOut(self.title))
        self.play(FadeIn(new_title))
        self.wait()

    ##########

    def rotate_square(
        self, 
        angle = np.pi/2, 
        axis = OUT, 
        square = None, 
        show_axis = False,
        added_anims = None,
        **kwargs
        ):
        if square is None:
            assert hasattr(self, "square")
            square = self.square
        added_anims = added_anims or []
        rotation = Rotate(
            square, 
            angle = angle, 
            axis = axis, 
            about_point = square.get_center(),
            **kwargs
        )
        if hasattr(square, "labels"):
            for label in rotation.target_mobject.labels:
                label.rotate_in_place(-angle, axis)

        if show_axis:
            axis_line = self.get_axis_line(square, axis)
            self.play(
                ShowCreation(axis_line),
                Animation(square)
            )
        self.play(rotation, *added_anims)
        if show_axis:
            self.play(
                FadeOut(axis_line),
                Animation(square)
            )

    def flip_square(self, axis = UP, **kwargs):
        self.rotate_square(
            angle = np.pi, 
            axis = axis,
            show_axis = True,
            **kwargs
        )

    def get_rotation_arcs(self, square, angle, angle_buff = SMALL_BUFF):
        square_radius = get_norm(
            square.points[0] - square.get_center()
        )
        arc = Arc(
            radius = square_radius + SMALL_BUFF,
            start_angle = np.pi/4 + np.sign(angle)*angle_buff,
            angle = angle - np.sign(angle)*2*angle_buff,
            color = YELLOW
        )
        arc.add_tip()
        if abs(angle) < 3*np.pi/4:
            angle_multiple_range = list(range(1, 4))
        else:
            angle_multiple_range = [2]
        arcs = VGroup(arc, *[
            arc.copy().rotate(i*np.pi/2)
            for i in angle_multiple_range
        ])
        arcs.move_to(square[0])

        return arcs

    def get_axis_line(self, square, axis):
        axis_line = DashedLine(2*axis, -2*axis, **self.dashed_line_config)
        axis_line.replace(square, dim_to_match = np.argmax(np.abs(axis)))
        axis_line.scale_in_place(1.2)
        return axis_line

    def add_labels_and_dots(self, square):
        labels = VGroup()
        dots = VGroup()
        for tex, vertex in zip("ABCD", square.get_anchors()):
            label = TexMobject(tex)
            label.add_background_rectangle()
            label.next_to(vertex, vertex-square.get_center(), SMALL_BUFF)
            labels.add(label)
            dot = Dot(vertex, color = WHITE)
            dots.add(dot)
        square.add(labels, dots)
        square.labels = labels
        square.dots = dots

    def add_randy_to_square(self, square, mode = "pondering"):
        randy = Randolph(mode = mode)
        randy.set_height(0.75*square.get_height())
        randy.move_to(square)
        square.add(randy)
        square.randy = randy

class ManyGroupsAreInfinite(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("Many groups are infinite")
        self.change_student_modes(*["pondering"]*3)
        self.wait(2)

class CircleSymmetries(Scene):
    CONFIG = {
        "circle_radius" : 2,
    }
    def construct(self):
        self.add_circle_and_title()        
        self.show_range_of_angles()
        self.associate_rotations_with_points()

    def add_circle_and_title(self):
        title = TextMobject("Group of rotations")
        title.to_edge(UP)

        circle = self.get_circle()

        self.play(Write(title), ShowCreation(circle, run_time = 2))
        self.wait()
        angles = [
            np.pi/2, -np.pi/3, 5*np.pi/6, 
            3*np.pi/2 + 0.1
        ]
        angles.append(-sum(angles))
        for angle in angles:
            self.play(Rotate(circle, angle = angle))
            self.wait()

        self.circle = circle

    def show_range_of_angles(self):
        self.add_radial_line()
        arc_circle = self.get_arc_circle()

        theta = TexMobject("\\theta = ")
        theta_value = DecimalNumber(0.00)
        theta_value.next_to(theta, RIGHT)
        theta_group = VGroup(theta, theta_value)
        theta_group.next_to(arc_circle, UP)
        def theta_value_update(theta_value, alpha):
            new_theta_value = DecimalNumber(alpha*2*np.pi)
            new_theta_value.set_height(theta.get_height())
            new_theta_value.next_to(theta, RIGHT)
            Transform(theta_value, new_theta_value).update(1)
            return new_theta_value


        self.play(FadeIn(theta_group))
        for rate_func in smooth, lambda t : smooth(1-t):
            self.play(
                Rotate(self.circle, 2*np.pi-0.001),
                ShowCreation(arc_circle),
                UpdateFromAlphaFunc(theta_value, theta_value_update),
                run_time = 7,
                rate_func = rate_func
            )
            self.wait()
        self.play(FadeOut(theta_group))
        self.wait()

    def associate_rotations_with_points(self):
        zero_dot = Dot(self.circle.point_from_proportion(0))
        zero_dot.set_color(RED)
        zero_arrow = Arrow(UP+RIGHT, ORIGIN)
        zero_arrow.set_color(zero_dot.get_color())
        zero_arrow.next_to(zero_dot, UP+RIGHT, buff = SMALL_BUFF)

        self.play(
            ShowCreation(zero_arrow),
            DrawBorderThenFill(zero_dot)
        )
        self.circle.add(zero_dot)
        self.wait()

        for alpha in 0.2, 0.6, 0.4, 0.8:
            point = self.circle.point_from_proportion(alpha)
            dot = Dot(point, color = YELLOW)
            vect = np.sign(point)
            arrow = Arrow(vect, ORIGIN)
            arrow.next_to(dot, vect, buff = SMALL_BUFF)
            arrow.set_color(dot.get_color())
            angle = alpha*2*np.pi

            self.play(
                ShowCreation(arrow),
                DrawBorderThenFill(dot)
            )
            self.play(
                Rotate(self.circle, angle, run_time = 2),
                Animation(dot)
            )
            self.wait()            
            self.play(
                Rotate(self.circle, -angle, run_time = 2),
                FadeOut(dot),
                FadeOut(arrow),
            )
            self.wait()

    ####

    def get_circle(self):
        circle = Circle(color = MAROON_B, radius = self.circle_radius)
        circle.ticks = VGroup()
        for alpha in np.arange(0, 1, 1./8):
            point = circle.point_from_proportion(alpha)
            tick = Line((1 - 0.05)*point, (1 + 0.05)*point)
            circle.ticks.add(tick)
        circle.add(circle.ticks)
        return circle

    def add_radial_line(self):
        radius = Line(
            self.circle.get_center(), 
            self.circle.point_from_proportion(0)
        )
        static_radius = radius.copy().set_color(GREY)

        self.play(ShowCreation(radius))
        self.add(static_radius, radius)
        self.circle.radius = radius
        self.circle.static_radius = static_radius
        self.circle.add(radius)

    def get_arc_circle(self):
        arc_radius = self.circle_radius/5.0
        arc_circle = Circle(
            radius = arc_radius,
            color = WHITE
        )
        return arc_circle

class GroupOfCubeSymmetries(ThreeDScene):
    CONFIG = {
        "cube_opacity" : 0.5,
        "cube_colors" : [BLUE],
        "put_randy_on_cube" : True,
    }
    def construct(self):
        title = TextMobject("Group of cube symmetries")
        title.to_edge(UP)
        self.add(title)

        cube = self.get_cube()

        face_centers = [face.get_center() for face in cube[0:7:2]]
        angle_axis_pairs = list(zip(3*[np.pi/2], face_centers))
        for i in range(3):
            ones = np.ones(3)
            ones[i] = -1
            axis = np.dot(ones, face_centers)
            angle_axis_pairs.append((2*np.pi/3, axis))

        for angle, axis in angle_axis_pairs:
            self.play(Rotate(
                cube, angle = angle, axis = axis,
                run_time = 2
            ))
            self.wait()

    def get_cube(self):
        cube = Cube(fill_opacity = self.cube_opacity)
        cube.set_color_by_gradient(*self.cube_colors)
        if self.put_randy_on_cube:
            randy = Randolph(mode = "pondering")
            # randy.pupils.shift(0.01*OUT)
            # randy.add(randy.pupils.copy().shift(0.02*IN))
            # for submob in randy.get_family():
            #     submob.part_of_three_d_mobject = True
            randy.scale(0.5)
            face = cube[1]
            randy.move_to(face)
            face.add(randy)
        pose_matrix = self.get_pose_matrix()
        cube.apply_function(
            lambda p : np.dot(p, pose_matrix.T),
            maintain_smoothness = False
        )
        return cube

    def get_pose_matrix(self):
        return np.dot(
            rotation_matrix(np.pi/8, UP),
            rotation_matrix(np.pi/24, RIGHT)
        )

class HowDoSymmetriesPlayWithEachOther(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "How do symmetries \\\\ play with each other?",
            target_mode = "hesitant",
        )
        self.change_student_modes("pondering", "maybe", "confused")
        self.wait(2)

class AddSquareSymmetries(SymmetriesOfSquare):
    def construct(self):
        square = Square(**self.square_config)
        square.flip(RIGHT)
        square.shift(DOWN)
        self.add_randy_to_square(square, mode = "shruggie")
        alt_square = square.copy()
        equals = TexMobject("=")
        equals.move_to(square)

        equation_square = Square(**self.square_config)
        equation = VGroup(
            equation_square, TexMobject("+"), 
            equation_square.copy(), TexMobject("="),
            equation_square.copy(),
        )
        equation[0].add(self.get_rotation_arcs(
            equation[0], np.pi/2,
        ))
        equation[2].add(self.get_axis_line(equation[4], UP))
        equation[4].add(self.get_axis_line(equation[4], UP+RIGHT))
        for mob in equation[::2]:
            mob.scale(0.5)
        equation.arrange(RIGHT)
        equation.to_edge(UP)

        arcs = self.get_rotation_arcs(square, np.pi/2)

        self.add(square)
        self.play(FadeIn(arcs))
        self.rotate_square(
            square = square, angle = np.pi/2,
            added_anims = list(map(FadeIn, equation[:2]))
        )
        self.wait()
        self.play(FadeOut(arcs))
        self.flip_square(
            square = square, axis = UP,
            added_anims = list(map(FadeIn, equation[2:4]))
        )
        self.wait()
        alt_square.next_to(equals, RIGHT, buff = LARGE_BUFF)
        alt_square.save_state()
        alt_square.move_to(square)
        alt_square.set_fill(opacity = 0)
        self.play(
            square.next_to, equals, LEFT, LARGE_BUFF,
            alt_square.restore,
            Write(equals)
        )
        self.flip_square(
            square = alt_square, axis = UP+RIGHT,
            added_anims = list(map(FadeIn, equation[4:])),
        )
        self.wait(2)

        ## Reiterate composition
        self.rotate_square(square = square, angle = np.pi/2)
        self.flip_square(square = square, axis = UP)
        self.wait()
        self.flip_square(square = alt_square, axis = UP+RIGHT)
        self.wait()

class AddCircleSymmetries(CircleSymmetries):
    def construct(self):
        circle = self.circle = self.get_circle()
        arc_circle = self.get_arc_circle()
        angles = [3*np.pi/2, 2*np.pi/3, np.pi/6]
        arcs = [
            arc_circle.copy().scale(scalar)
            for scalar in [1, 1.2, 1.4]
        ]

        equation = TexMobject(
            "270^\\circ", "+", "120^\\circ", "=", "30^\\circ",
        )
        equation.to_edge(UP)

        colors = [BLUE, YELLOW, GREEN]
        for color, arc, term in zip(colors, arcs, equation[::2]):
            arc.set_color(color)
            term.set_color(color)

        self.play(FadeIn(circle))
        self.add_radial_line()
        alt_radius = circle.radius.copy()
        alt_radius.set_color(GREY)
        alt_circle = circle.copy()
        equals = TexMobject("=")
        equals.move_to(circle)

        def rotate(circle, angle, arc, terms):
            self.play(
                Rotate(circle, angle, in_place = True),
                ShowCreation(
                    arc,
                    rate_func = lambda t : (angle/(2*np.pi))*smooth(t)
                ),
                Write(VGroup(*terms)),
                run_time = 2,
            )

        rotate(circle, angles[0], arcs[0], equation[:2])
        self.wait()
        circle.add(alt_radius)
        rotate(circle, angles[1], arcs[1], equation[2:4])
        self.play(FadeOut(alt_radius))
        circle.remove(alt_radius)
        self.wait()

        circle.add(circle.static_radius)
        circle.add(*arcs[:2])

        alt_static_radius = circle.static_radius.copy()
        alt_circle.add(alt_static_radius)
        alt_circle.next_to(equals, RIGHT, buff = LARGE_BUFF)
        alt_circle.save_state()
        alt_circle.move_to(circle)
        alt_circle.set_stroke(width = 0)
        self.play(
            circle.next_to, equals, LEFT, LARGE_BUFF,
            alt_circle.restore,
            Write(equals)
        )
        arcs[2].shift(alt_circle.get_center())
        alt_circle.remove(alt_static_radius)
        self.wait()
        rotate(alt_circle, angles[2], arcs[2], equation[4:])
        self.wait()
        self.play(
            Rotate(arcs[1], angles[0], about_point = circle.get_center())
        )
        self.wait(2)
        for term, arc in zip(equation[::2], arcs):
            self.play(*[
                ApplyMethod(mob.scale_in_place, 1.2, rate_func = there_and_back)
                for mob in (term, arc)
            ])
            self.wait()

class AddCubeSymmetries(GroupOfCubeSymmetries):
    CONFIG = {
        "angle_axis_pairs" : [
            (np.pi/2, RIGHT),
            (np.pi/2, UP),
        ],
        "cube_opacity" : 0.5,
        "cube_colors" : [BLUE],
    }
    def construct(self):
        angle_axis_pairs = list(self.angle_axis_pairs)
        angle_axis_pairs.append(
            self.get_composition_angle_and_axis()
        )
        self.pose_matrix = self.get_pose_matrix()
        cube = self.get_cube()

        equation = cube1, plus, cube2, equals, cube3 = VGroup(
            cube, TexMobject("+"), 
            cube.copy(), TexMobject("="),
            cube.copy()
        )
        equation.arrange(RIGHT, buff = MED_LARGE_BUFF)
        equation.center()

        self.add(cube1)
        self.rotate_cube(cube1, *angle_axis_pairs[0])
        cube_copy = cube1.copy()
        cube_copy.set_fill(opacity = 0)
        self.play(
            cube_copy.move_to, cube2,
            cube_copy.set_fill, None, self.cube_opacity,
            Write(plus)
        )
        self.rotate_cube(cube_copy, *angle_axis_pairs[1])
        self.play(Write(equals))
        self.play(DrawBorderThenFill(cube3, run_time = 1))
        self.rotate_cube(cube3, *angle_axis_pairs[2])
        self.wait(2)

        times = TexMobject("\\times")
        times.scale(1.5)
        times.move_to(plus)
        times.set_color(RED)
        self.wait()
        self.play(ReplacementTransform(plus, times))
        self.play(Indicate(times))
        self.wait()
        for cube, (angle, axis) in zip([cube1, cube_copy, cube3], angle_axis_pairs):
            self.rotate_cube(
                cube, -angle, axis, add_arrows = False,
                rate_func = there_and_back,
                run_time = 1.5
            )
        self.wait()

    def rotate_cube(self, cube, angle, axis, add_arrows = True, **kwargs):
        axis = np.dot(axis, self.pose_matrix.T)
        anims = []
        if add_arrows:
            arrows = VGroup(*[
                Arc(
                    start_angle = np.pi/12+a, angle = 5*np.pi/6,
                    color = YELLOW
                ).add_tip()
                for a in (0, np.pi)
            ])
            arrows.set_height(1.5*cube.get_height())
            z_to_axis = z_to_vector(axis)
            arrows.apply_function(
                lambda p : np.dot(p, z_to_axis.T),
                maintain_smoothness = False
            )
            arrows.move_to(cube)
            arrows.shift(-axis*cube.get_height()/2/get_norm(axis))
            anims += list(map(ShowCreation, arrows))
        anims.append(
            Rotate(
                cube, axis = axis, angle = angle, in_place = True,
                **kwargs
            )
        )
        self.play(*anims, run_time = 1.5)

    def get_composition_angle_and_axis(self):
        return get_composite_rotation_angle_and_axis(
            *list(zip(*self.angle_axis_pairs))
        )

class DihedralGroupStructure(SymmetriesOfSquare):
    CONFIG = {
        "dashed_line_config" : {
            "dash_length" : 0.1
        },
        "filed_sum_scale_factor" : 0.4,
        "num_rows" : 5,
    }
    def construct(self):
        angle_axis_pairs = [
            (np.pi/2, OUT),
            (np.pi, OUT),
            (-np.pi/2, OUT),
            # (np.pi, RIGHT),
            # (np.pi, UP+RIGHT),
            (np.pi, UP),
            (np.pi, UP+LEFT),
        ]
        pair_pairs = list(it.product(*[angle_axis_pairs]*2))
        random.shuffle(pair_pairs)
        for pair_pair in pair_pairs[:4]:
            sum_expression = self.demonstrate_sum(pair_pair)
            self.file_away_sum(sum_expression)
        for pair_pair in pair_pairs[4:]:
            should_skip_animations = self.skip_animations
            self.skip_animations = True
            sum_expression = self.demonstrate_sum(pair_pair)
            self.file_away_sum(sum_expression)
            self.skip_animations = should_skip_animations
            self.play(FadeIn(sum_expression))
        self.wait(3)


    def demonstrate_sum(self, angle_axis_pairs):
        angle_axis_pairs = list(angle_axis_pairs) + [
            get_composite_rotation_angle_and_axis(
                *list(zip(*angle_axis_pairs))
            )
        ]

        prototype_square = Square(**self.square_config)
        prototype_square.flip(RIGHT)
        self.add_randy_to_square(prototype_square)

        # self.add_labels_and_dots(prototype_square)
        prototype_square.scale(0.7)
        expression = s1, plus, s2, equals, s3 = VGroup(
            prototype_square, TexMobject("+").scale(2), 
            prototype_square.copy(), TexMobject("=").scale(2),
            prototype_square.copy()
        )

        final_expression = VGroup()
        for square, (angle, axis) in zip([s1, s2, s3], angle_axis_pairs):
            if np.cos(angle) > 0.5:
                square.action_illustration = VectorizedPoint()
            elif np.argmax(np.abs(axis)) == 2: ##Axis is in z direction
                square.action_illustration = self.get_rotation_arcs(
                    square, angle
                )
            else:
                square.action_illustration = self.get_axis_line(
                    square, axis
                )
            square.add(square.action_illustration)
            final_expression.add(square.action_illustration)
            square.rotation_kwargs = {
                "square" : square,
                "angle" : angle,
                "axis" : axis,
            }
        expression.arrange()
        expression.set_width(FRAME_X_RADIUS+1)
        expression.to_edge(RIGHT, buff = SMALL_BUFF)
        for square in s1, s2, s3:
            square.remove(square.action_illustration)

        self.play(FadeIn(s1))
        self.play(*list(map(ShowCreation, s1.action_illustration)))
        self.rotate_square(**s1.rotation_kwargs)

        s1_copy = s1.copy()
        self.play(
            # FadeIn(s2),
            s1_copy.move_to, s2,
            Write(plus)
        )
        Transform(s2, s1_copy).update(1)
        self.remove(s1_copy)
        self.add(s2)
        self.play(*list(map(ShowCreation, s2.action_illustration)))
        self.rotate_square(**s2.rotation_kwargs)

        self.play(
            Write(equals),
            FadeIn(s3)
        )
        self.play(*list(map(ShowCreation, s3.action_illustration)))
        self.rotate_square(**s3.rotation_kwargs)
        self.wait()
        final_expression.add(*expression)

        return final_expression

    def file_away_sum(self, sum_expression):
        if not hasattr(self, "num_sum_expressions"):
            self.num_sum_expressions = 0
        target = sum_expression.copy()
        target.scale(self.filed_sum_scale_factor)
        y_index = self.num_sum_expressions%self.num_rows
        y_prop = float(y_index)/(self.num_rows-1)
        y = interpolate(FRAME_Y_RADIUS-LARGE_BUFF, -FRAME_Y_RADIUS+LARGE_BUFF, y_prop)
        x_index = self.num_sum_expressions//self.num_rows
        x_spacing = FRAME_WIDTH/3
        x = (x_index-1)*x_spacing

        target.move_to(x*RIGHT + y*UP)

        self.play(Transform(sum_expression, target))
        self.wait()

        self.num_sum_expressions += 1
        self.last_sum_expression = sum_expression

class ThisIsAVeryGeneralIdea(Scene):
    def construct(self):
        groups = TextMobject("Groups")
        groups.to_edge(UP)
        groups.set_color(BLUE)

        examples = VGroup(*list(map(TextMobject, [
            "Square matrices \\\\ \\small (Where $\\det(M) \\ne 0$)",
            "Molecular \\\\ symmetry",
            "Cryptography",
            "Numbers",
        ])))
        numbers = examples[-1]
        examples.arrange(buff = LARGE_BUFF)
        examples.set_width(FRAME_WIDTH-1)
        examples.move_to(UP)

        lines = VGroup(*[
            Line(groups.get_bottom(), ex.get_top(), buff = MED_SMALL_BUFF)
            for ex in examples
        ])
        lines.set_color(groups.get_color())

        self.add(groups)

        for example, line in zip(examples, lines):
            self.play(
                ShowCreation(line),
                Write(example, run_time = 2)
            )
        self.wait()
        self.play(
            VGroup(*examples[:-1]).fade, 0.7,
            VGroup(*lines[:-1]).fade, 0.7,
        )

        self.play(
            numbers.scale, 1.2, numbers.get_corner(UP+RIGHT),
        )
        self.wait(2)

        sub_categories = VGroup(*list(map(TextMobject, [
            "Numbers \\\\ (Additive)",
            "Numbers \\\\ (Multiplicative)",
        ])))
        sub_categories.arrange(RIGHT, buff = MED_LARGE_BUFF)
        sub_categories.next_to(numbers, DOWN, 1.5*LARGE_BUFF)
        sub_categories.to_edge(RIGHT)
        sub_categories[0].set_color(ADDER_COLOR)
        sub_categories[1].set_color(MULTIPLIER_COLOR)

        sub_lines = VGroup(*[
            Line(numbers.get_bottom(), sc.get_top(), buff = MED_SMALL_BUFF)
            for sc in sub_categories
        ])
        sub_lines.set_color(numbers.get_color())

        self.play(*it.chain(
            list(map(ShowCreation, sub_lines)),
            list(map(Write, sub_categories))
        ))
        self.wait()

class NumbersAsActionsQ(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Numbers are actions?",
            target_mode = "confused",
        )
        self.change_student_modes("pondering", "confused", "erm")
        self.play(self.get_teacher().change_mode, "happy")
        self.wait(3)

class AdditiveGroupOfReals(Scene):
    CONFIG = {
        "number_line_center" : UP,
        "shadow_line_center" : DOWN,
        "zero_color" : GREEN_B,
        "x_min" : -FRAME_WIDTH,
        "x_max" : FRAME_WIDTH,
    }
    def construct(self):
        self.add_number_line()
        self.show_example_slides(3, -7)
        self.write_group_of_slides()
        self.show_example_slides(2, 6, -1, -3)
        self.mark_zero()
        self.show_example_slides_labeled(3, -2)
        self.comment_on_zero_as_identity()
        self.show_example_slides_labeled(
            5.5, added_anims = [self.get_write_name_of_group_anim()]
        )
        self.show_example_additions((3, 2), (2, -5), (-4, 4))

    def add_number_line(self):
        number_line = NumberLine(
            x_min = self.x_min,
            x_max = self.x_max,
        )

        number_line.shift(self.number_line_center)
        shadow_line = NumberLine(color = GREY, stroke_width = 2)
        shadow_line.shift(self.shadow_line_center)
        for line in number_line, shadow_line:
            line.add_numbers()
        shadow_line.numbers.fade(0.25)
        shadow_line.save_state()
        shadow_line.set_color(BLACK)
        shadow_line.move_to(number_line)


        self.play(*list(map(Write, number_line)), run_time = 1)
        self.play(shadow_line.restore, Animation(number_line))
        self.wait()

        self.number_line = number_line
        self.shadow_line = shadow_line

    def show_example_slides(self, *nums):
        for num in nums:
            zero_point = self.number_line.number_to_point(0)            
            num_point = self.number_line.number_to_point(num)
            arrow = Arrow(zero_point, num_point, buff = 0)
            arrow.set_color(ADDER_COLOR)
            arrow.shift(MED_LARGE_BUFF*UP)

            self.play(ShowCreation(arrow))
            self.play(
                self.number_line.shift,
                num_point - zero_point,
                run_time = 2
            )
            self.play(FadeOut(arrow))

    def write_group_of_slides(self):
        title = TextMobject("Group of line symmetries")
        title.to_edge(UP)
        self.play(Write(title))
        self.title = title

    def mark_zero(self):
        dot = Dot(
            self.number_line.number_to_point(0),
            color = self.zero_color
        )
        arrow = Arrow(dot, color = self.zero_color)
        words = TextMobject("Follow zero")
        words.next_to(arrow.get_start(), UP)
        words.set_color(self.zero_color)

        self.play(
            ShowCreation(arrow),
            DrawBorderThenFill(dot),
            Write(words),
        )
        self.wait()
        self.play(*list(map(FadeOut, [arrow, words])))

        self.number_line.add(dot)

    def show_example_slides_labeled(self, *nums, **kwargs):
        for num in nums:
            line = DashedLine(
                self.number_line.number_to_point(num)+MED_LARGE_BUFF*UP,
                self.shadow_line.number_to_point(num)+MED_LARGE_BUFF*DOWN,
            )
            vect = self.number_line.number_to_point(num) - \
                   self.number_line.number_to_point(0)
            self.play(ShowCreation(line))
            self.wait()
            self.play(self.number_line.shift, vect, run_time = 2)
            self.wait()
            if "added_anims" in kwargs:
                self.play(*kwargs["added_anims"])
                self.wait()
            self.play(
                self.number_line.shift, -vect,
                FadeOut(line)
            )

    def comment_on_zero_as_identity(self):
        line = DashedLine(
            self.number_line.number_to_point(0)+MED_LARGE_BUFF*UP,
            self.shadow_line.number_to_point(0)+MED_LARGE_BUFF*DOWN,
        )
        words = TexMobject("0 \\leftrightarrow \\text{Do nothing}")
        words.shift(line.get_top()+MED_SMALL_BUFF*UP - words[0].get_bottom())

        self.play(
            ShowCreation(line),
            Write(words)
        )
        self.wait(2)
        self.play(*list(map(FadeOut, [line, words])))

    def get_write_name_of_group_anim(self):
        new_title = TextMobject("Additive group of real numbers")
        VGroup(*new_title[-len("realnumbers"):]).set_color(BLUE)
        VGroup(*new_title[:len("Additive")]).set_color(ADDER_COLOR)
        new_title.to_edge(UP)
        return Transform(self.title, new_title)

    def show_example_additions(self, *num_pairs):
        for num_pair in num_pairs:
            num_mobs = VGroup()
            arrows = VGroup()
            self.number_line.save_state()
            for num in num_pair:
                zero_point, num_point, arrow, num_mob = \
                    self.get_adder_mobs(num)
                if len(num_mobs) > 0:
                    last_num_mob = num_mobs[0]
                    x = num_mob.get_center()[0]
                    if x < last_num_mob.get_right()[0] and x > last_num_mob.get_left()[0]:
                        num_mob.next_to(last_num_mob, RIGHT)
                num_mobs.add(num_mob)
                arrows.add(arrow)

                self.play(
                    ShowCreation(arrow),
                    Write(num_mob, run_time = 1)
                )
                self.play(
                    self.number_line.shift, 
                    num_point - zero_point
                )
                self.wait()
            #Reset
            self.play(
                FadeOut(num_mobs),
                FadeOut(self.number_line)
            )
            ApplyMethod(self.number_line.restore).update(1)
            self.play(FadeIn(self.number_line))

            #Sum arrow
            num = sum(num_pair)
            zero_point, sum_point, arrow, sum_mob = \
                self.get_adder_mobs(sum(num_pair))
            VGroup(arrow, sum_mob).shift(MED_LARGE_BUFF*UP)
            arrows.add(arrow)
            self.play(
                ShowCreation(arrow),
                Write(sum_mob, run_time = 1)
            )
            self.wait()
            self.play(
                self.number_line.shift, 
                num_point - zero_point,
                run_time = 2
            )
            self.wait()
            self.play(
                self.number_line.restore,
                *list(map(FadeOut, [arrows, sum_mob]))
            )

    def get_adder_mobs(self, num):
        zero_point = self.number_line.number_to_point(0)            
        num_point = self.number_line.number_to_point(num)
        arrow = Arrow(zero_point, num_point, buff = 0)
        arrow.set_color(ADDER_COLOR)
        arrow.shift(MED_SMALL_BUFF*UP)
        if num == 0:
            arrow = DashedLine(UP, ORIGIN)
            arrow.move_to(zero_point)
        elif num < 0:
            arrow.set_color(RED)
            arrow.shift(SMALL_BUFF*UP)
        sign = "+" if num >= 0 else ""
        num_mob = TexMobject(sign + str(num))
        num_mob.next_to(arrow, UP)
        num_mob.set_color(arrow.get_color())
        return zero_point, num_point, arrow, num_mob

class AdditiveGroupOfComplexNumbers(ComplexTransformationScene):
    CONFIG = {
        "x_min" : -2*int(FRAME_X_RADIUS),
        "x_max" : 2*int(FRAME_X_RADIUS),
        "y_min" : -FRAME_HEIGHT,
        "y_max" : FRAME_HEIGHT,
        "example_points" : [
            complex(3, 2),
            complex(1, -3),
        ]
    }
    def construct(self):
        self.add_plane()
        self.show_preview_example_slides()
        self.show_vertical_slide()
        self.show_example_point()
        self.show_example_addition()
        self.write_group_name()
        self.show_some_random_slides()

    def add_plane(self):
        self.add_transformable_plane(animate = True)
        zero_dot = Dot(
            self.z_to_point(0),
            color = ADDER_COLOR
        )
        self.play(ShowCreation(zero_dot))
        self.plane.add(zero_dot)
        self.plane.zero_dot = zero_dot
        self.wait()

    def show_preview_example_slides(self):
        example_vect = 2*UP+RIGHT
        for vect in example_vect, -example_vect:
            self.play(self.plane.shift, vect, run_time = 2)
            self.wait()

    def show_vertical_slide(self):
        dots = VGroup(*[
            Dot(self.z_to_point(complex(0, i)))
            for i in range(1, 4)
        ])
        dots.set_color(YELLOW)
        labels = VGroup(*self.imag_labels[-3:])

        arrow = Arrow(ORIGIN, dots[-1].get_center(), buff = 0)
        arrow.set_color(ADDER_COLOR)

        self.plane.save_state()
        for dot, label in zip(dots, labels):
            self.play(
                Indicate(label),
                ShowCreation(dot)
            )
        self.add_foreground_mobjects(dots)
        self.wait()
        Scene.play(self, ShowCreation(arrow))
        self.add_foreground_mobjects(arrow)
        self.play(
            self.plane.shift, dots[-1].get_center(),
            run_time = 2
        )
        self.wait()
        self.play(FadeOut(arrow))
        self.foreground_mobjects.remove(arrow)
        self.play(
            self.plane.shift, 6*DOWN,
            run_time = 3,
        )
        self.wait()
        self.play(self.plane.restore, run_time = 2)
        self.foreground_mobjects.remove(dots)
        self.play(FadeOut(dots))

    def show_example_point(self):
        z = self.example_points[0]
        point = self.z_to_point(z)
        dot = Dot(point, color = YELLOW)
        arrow = Vector(point, buff = dot.radius)
        arrow.set_color(dot.get_color())
        label = TexMobject("%d + %di"%(z.real, z.imag))
        label.next_to(point, UP)
        label.set_color(dot.get_color())
        label.add_background_rectangle()

        real_arrow = Vector(self.z_to_point(z.real))
        imag_arrow = Vector(self.z_to_point(z - z.real))
        VGroup(real_arrow, imag_arrow).set_color(ADDER_COLOR)

        self.play(
            Write(label),
            DrawBorderThenFill(dot)
        )
        self.wait()
        self.play(ShowCreation(arrow))
        self.add_foreground_mobjects(label, dot, arrow)
        self.wait()
        self.slide(z)
        self.wait()
        self.play(FadeOut(self.plane))
        self.plane.restore()
        self.plane.set_stroke(width = 0)
        self.play(self.plane.restore)
        self.play(ShowCreation(real_arrow))
        self.add_foreground_mobjects(real_arrow)
        self.slide(z.real)
        self.wait()
        self.play(ShowCreation(imag_arrow))
        self.wait()
        self.play(imag_arrow.shift, self.z_to_point(z.real))
        self.add_foreground_mobjects(imag_arrow)
        self.slide(z - z.real)
        self.wait()

        self.foreground_mobjects.remove(real_arrow)
        self.foreground_mobjects.remove(imag_arrow)
        self.play(*list(map(FadeOut, [real_arrow, imag_arrow, self.plane])))
        self.plane.restore()
        self.plane.set_stroke(width = 0)
        self.play(self.plane.restore)

        self.z1 = z
        self.arrow1 = arrow
        self.dot1 = dot
        self.label1 = label

    def show_example_addition(self):
        z1 = self.z1
        arrow1 = self.arrow1
        dot1 = self.dot1
        label1 = self.label1

        z2 = self.example_points[1]
        point2 = self.z_to_point(z2)
        dot2 = Dot(point2, color = TEAL)
        arrow2 = Vector(
            point2, 
            buff = dot2.radius,
            color = dot2.get_color()
        )
        label2 = TexMobject(
            "%d %di"%(z2.real, z2.imag)
        )
        label2.next_to(point2, UP+RIGHT)
        label2.set_color(dot2.get_color())
        label2.add_background_rectangle()

        self.play(ShowCreation(arrow2))
        self.play(
            DrawBorderThenFill(dot2),
            Write(label2)
        )
        self.add_foreground_mobjects(arrow2, dot2, label2)
        self.wait()

        self.slide(z1)
        arrow2_copy = arrow2.copy()
        self.play(arrow2_copy.shift, self.z_to_point(z1))
        self.add_foreground_mobjects(arrow2_copy)
        self.slide(z2)
        self.play(FadeOut(arrow2_copy))
        self.foreground_mobjects.remove(arrow2_copy)
        self.wait()

        ##Break into components
        real_arrow, imag_arrow = component_arrows = [
            Vector(
                self.z_to_point(z),
                color = ADDER_COLOR
            )
            for z in [
                z1.real+z2.real,
                complex(0, z1.imag+z2.imag),
            ]
        ]
        imag_arrow.shift(real_arrow.get_end())
        plus = TexMobject("+").next_to(
            real_arrow.get_center(), UP+RIGHT
        )
        plus.add_background_rectangle()

        rp1, rp2, ip1, ip2 = label_parts = [
            VGroup(label1[1][0].copy()),
            VGroup(label2[1][0].copy()),
            VGroup(*label1[1][2:]).copy(),
            VGroup(*label2[1][1:]).copy(),
        ]
        for part in label_parts:
            part.generate_target()

        rp1.target.next_to(plus, LEFT)
        rp2.target.next_to(plus, RIGHT)
        ip1.target.next_to(imag_arrow.get_center(), RIGHT)
        ip1.target.shift(SMALL_BUFF*DOWN)
        ip2.target.next_to(ip1.target, RIGHT)

        real_background_rect = BackgroundRectangle(
            VGroup(rp1.target, rp2.target)
        )
        imag_background_rect = BackgroundRectangle(
            VGroup(ip1.target, ip2.target)
        )

        self.play(
            ShowCreation(real_arrow),
            ShowCreation(
                real_background_rect,
                rate_func = squish_rate_func(smooth, 0.75, 1),
            ),
            Write(plus),
            *list(map(MoveToTarget, [rp1, rp2]))
        )
        self.wait()
        self.play(
            ShowCreation(imag_arrow),
            ShowCreation(
                imag_background_rect,
                rate_func = squish_rate_func(smooth, 0.75, 1),
            ),
            *list(map(MoveToTarget, [ip1, ip2]))
        )
        self.wait(2)
        to_remove = [
            arrow1, dot1, label1,
            arrow2, dot2, label2,
            real_background_rect,
            imag_background_rect,
            plus,
        ] + label_parts + component_arrows
        for mob in to_remove:
            if mob in self.foreground_mobjects:
                self.foreground_mobjects.remove(mob)
        self.play(*list(map(FadeOut, to_remove)))
        self.play(self.plane.restore, run_time = 2)
        self.wait()

    def write_group_name(self):
        title = TextMobject(
            "Additive", "group of", "complex numbers"
        )
        title[0].set_color(ADDER_COLOR)
        title[2].set_color(BLUE)
        title.add_background_rectangle()
        title.to_edge(UP, buff = MED_SMALL_BUFF)

        self.play(Write(title))
        self.add_foreground_mobjects(title)
        self.wait()

    def show_some_random_slides(self):
        example_slides = [
            complex(3),
            complex(0, 2),
            complex(-4, -1),
            complex(-2, -1),
            complex(4, 2),
        ]
        for z in example_slides:
            self.slide(z)
            self.wait()

    #########

    def slide(self, z, *added_anims, **kwargs):
        kwargs["run_time"] = kwargs.get("run_time", 2)
        self.play(
            ApplyMethod(
                self.plane.shift, self.z_to_point(z),
                **kwargs
            ),
            *added_anims
        )

class SchizophrenicNumbers(Scene):
    def construct(self):
        v_line = DashedLine(
            FRAME_Y_RADIUS*UP,
            FRAME_Y_RADIUS*DOWN
        )
        left_title = TextMobject("Additive group")
        left_title.shift(FRAME_X_RADIUS*LEFT/2)
        right_title = TextMobject("Multiplicative group")
        right_title.shift(FRAME_X_RADIUS*RIGHT/2)
        VGroup(left_title, right_title).to_edge(UP)
        self.add(v_line, left_title, right_title)

        numbers = VGroup(
            Randolph(mode = "happy").scale(0.2),
            TexMobject("3").shift(UP+LEFT),
            TexMobject("5.83").shift(UP+RIGHT),
            TexMobject("\\sqrt{2}").shift(DOWN+LEFT),
            TexMobject("2-i").shift(DOWN+RIGHT),
        )
        for number in numbers:
            number.set_color(ADDER_COLOR)
            number.scale(1.5)            
            if isinstance(number, PiCreature):
                continue
            number.eyes = Eyes(number[0], height = 0.1)
            number.add(number.eyes)
        numbers[3].eyes.next_to(numbers[3][1], UP, buff = 0)
        numbers.shift(FRAME_X_RADIUS*LEFT/2)

        self.play(FadeIn(numbers))
        self.blink_numbers(numbers)
        self.wait()
        self.add(numbers.copy())
        for number in numbers:
            number.generate_target()
            number.target.shift(FRAME_X_RADIUS*RIGHT)
            number.target.eyes.save_state()
            number.target.set_color(MULTIPLIER_COLOR)
            number.target.eyes.restore()
        self.play(*[
            MoveToTarget(
                number, 
                rate_func = squish_rate_func(
                    smooth, alpha, alpha+0.5
                ),
                run_time = 2,
            )
            for number, alpha in zip(numbers, np.linspace(0, 0.5, len(numbers)))
        ])
        self.wait()
        self.blink_numbers(numbers)
        self.wait()

    def blink_numbers(self, numbers):
        self.play(*[
            num.eyes.blink_anim(
                rate_func = squish_rate_func(
                    there_and_back, alpha, alpha+0.2
                )
            )
            for num, alpha in zip(
                numbers[1:], 0.8*np.random.random(len(numbers))
            )
        ])

class MultiplicativeGroupOfReals(AdditiveGroupOfReals):
    CONFIG = {
        "number_line_center" : 0.5*UP,
        "shadow_line_center" : 1.5*DOWN,
        "x_min" : -3*FRAME_X_RADIUS,
        "x_max" : 3*FRAME_X_RADIUS,
        "positive_reals_color" : MAROON_B,
    }
    def setup(self):
        self.foreground_mobjects = VGroup()

    def construct(self):
        self.add_title()
        self.add_number_line()
        self.introduce_stretch_and_squish()
        self.show_zero_fixed_in_place()
        self.follow_one()
        self.every_positive_number_association()
        self.compose_actions(3, 2)
        self.compose_actions(4, 0.5)
        self.write_group_name()
        self.compose_actions(1.5, 1.5)

    def add_title(self):
        self.title = TextMobject("Group of stretching/squishing actions")
        self.title.to_edge(UP)
        self.add(self.title)

    def add_number_line(self):
        AdditiveGroupOfReals.add_number_line(self)
        self.zero_point = self.number_line.number_to_point(0)
        self.one = [m for m in self.number_line.numbers if m.get_tex_string() is "1"][0]
        self.one.add_background_rectangle()
        self.one.background_rectangle.scale_in_place(1.3)
        self.number_line.save_state()        

    def introduce_stretch_and_squish(self):
        for num in [3, 0.25]:
            self.stretch(num)
            self.wait()
        self.play(self.number_line.restore)
        self.wait()

    def show_zero_fixed_in_place(self):
        arrow = Arrow(self.zero_point + UP, self.zero_point, buff = 0)
        arrow.set_color(ADDER_COLOR)
        words = TextMobject("Fix zero")
        words.set_color(ADDER_COLOR)
        words.next_to(arrow, UP)

        self.play(
            ShowCreation(arrow),
            Write(words)
        )
        self.foreground_mobjects.add(arrow)
        self.stretch(4)
        self.stretch(0.1)
        self.wait()
        self.play(self.number_line.restore)
        self.play(FadeOut(words))
        self.wait()

        self.zero_arrow = arrow

    def follow_one(self):
        dot = Dot(self.number_line.number_to_point(1))
        arrow = Arrow(dot.get_center()+UP+RIGHT, dot)
        words = TextMobject("Follow one")
        words.next_to(arrow.get_start(), UP)
        for mob in dot, arrow, words:
            mob.set_color(MULTIPLIER_COLOR)

        three_line, half_line = [
            DashedLine(
                self.number_line.number_to_point(num),
                self.shadow_line.number_to_point(num)
            )
            for num in (3, 0.5)
        ]
        three_mob = [m for m in self.shadow_line.numbers if m.get_tex_string() == "3"][0]
        half_point = self.shadow_line.number_to_point(0.5)
        half_arrow = Arrow(
            half_point+UP+LEFT, half_point, buff = SMALL_BUFF,
            tip_length = 0.15,
        )
        half_label = TexMobject("1/2")
        half_label.scale(0.7)
        half_label.set_color(MULTIPLIER_COLOR)
        half_label.next_to(half_arrow.get_start(), LEFT, buff = SMALL_BUFF)
        
        self.play(
            ShowCreation(arrow),
            DrawBorderThenFill(dot),
            Write(words)
        )
        self.number_line.add(dot)
        self.number_line.numbers.add(dot)
        self.number_line.save_state()
        self.wait()
        self.play(*list(map(FadeOut, [arrow, words])))

        self.stretch(3)
        self.play(
            ShowCreation(three_line),
            Animation(self.one)
        )
        dot_copy = dot.copy()
        self.play(
            dot_copy.move_to, three_line.get_bottom()
        )
        self.play(Indicate(three_mob, run_time = 2))
        self.wait()
        self.play(
            self.number_line.restore,
            *list(map(FadeOut, [three_line, dot_copy]))
        )
        self.wait()
        self.stretch(0.5)
        self.play(
            ShowCreation(half_line),
            Animation(self.one)
        )
        dot_copy = dot.copy()
        self.play(
            dot_copy.move_to, half_line.get_bottom()
        )
        self.play(
            Write(half_label),
            ShowCreation(half_arrow)
        )
        self.wait()
        self.play(
            self.number_line.restore,
            *list(map(FadeOut, [
                half_label, half_arrow, 
                half_line, dot_copy
            ]))
        )
        self.wait()

        self.one_dot = dot

    def every_positive_number_association(self):
        positive_reals_line = Line(
            self.shadow_line.number_to_point(0),
            self.shadow_line.number_to_point(FRAME_X_RADIUS),
            color = self.positive_reals_color
        )
        positive_reals_words = TextMobject("All positive reals")
        positive_reals_words.set_color(self.positive_reals_color)
        positive_reals_words.next_to(positive_reals_line, UP)
        positive_reals_words.add_background_rectangle()

        third_line, one_line = [
            DashedLine(
                self.number_line.number_to_point(num),
                self.shadow_line.number_to_point(num)
            )
            for num in (0.33, 1)
        ]

        self.play(
            self.zero_arrow.shift, 0.5*UP,
            rate_func = there_and_back
        )
        self.wait()
        self.play(
            self.one_dot.shift, 0.25*UP,
            rate_func = wiggle
        )
        self.stretch(3)
        self.stretch(0.33/3, run_time = 3)
        self.wait()
        self.play(ShowCreation(third_line), Animation(self.one))
        self.play(
            ShowCreation(positive_reals_line),
            Write(positive_reals_words),
        )
        self.wait()
        self.play(
            ReplacementTransform(third_line, one_line),
            self.number_line.restore,
            Animation(positive_reals_words),
            run_time = 2
        )
        self.number_line.add_to_back(one_line)
        self.number_line.save_state()
        self.stretch(
            7, run_time = 10, rate_func = there_and_back,
            added_anims = [Animation(positive_reals_words)]
        )
        self.wait()

    def compose_actions(self, num1, num2):
        words = VGroup(*[
            TextMobject("(%s by %s)"%(word, str(num)))
            for num in (num1, num2, num1*num2)
            for word in ["Stretch" if num > 1 else "Squish"]
        ])
        words.submobjects.insert(2, TexMobject("="))
        words.arrange(RIGHT)
        top_words = VGroup(*words[:2])
        top_words.set_color(MULTIPLIER_COLOR)
        bottom_words = VGroup(*words[2:])
        bottom_words.next_to(top_words, DOWN)
        words.scale(0.8)
        words.next_to(self.number_line, UP)
        words.to_edge(RIGHT)

        for num, word in zip([num1, num2], top_words):
            self.stretch(
                num, 
                added_anims = [FadeIn(word)],
                run_time = 3
            )
            self.wait()
        self.play(Write(bottom_words, run_time = 2))
        self.wait(2)
        self.play(
            ApplyMethod(self.number_line.restore, run_time = 2),
            FadeOut(words),
        )
        self.wait()

    def write_group_name(self):
        new_title = TextMobject(
            "Multiplicative group of positive real numbers"
        )
        new_title.to_edge(UP)
        VGroup(
            *new_title[:len("Multiplicative")]
        ).set_color(MULTIPLIER_COLOR)
        VGroup(
            *new_title[-len("positiverealnumbers"):]
        ).set_color(self.positive_reals_color)

        self.play(Transform(self.title, new_title))
        self.wait()

    ###

    def stretch(self, factor, run_time = 2, **kwargs):
        kwargs["run_time"] = run_time
        target = self.number_line.copy()
        target.stretch_about_point(factor, 0, self.zero_point)
        total_factor = (target.number_to_point(1)-self.zero_point)[0]
        for number in target.numbers:
            number.stretch_in_place(1./factor, dim = 0)
            if total_factor < 0.7:
                number.stretch_in_place(total_factor, dim = 0)
        self.play(
            Transform(self.number_line, target, **kwargs),
            *kwargs.get("added_anims", [])
        )

    def play(self, *anims, **kwargs):
        anims = list(anims) + [Animation(self.foreground_mobjects)]
        Scene.play(self, *anims, **kwargs)

class MultiplicativeGroupOfComplexNumbers(AdditiveGroupOfComplexNumbers):
    CONFIG = {
        "dot_radius" : Dot.CONFIG["radius"],
        "y_min" : -3*FRAME_Y_RADIUS,
        "y_max" : 3*FRAME_Y_RADIUS,
    }
    def construct(self):
        self.add_plane()
        self.add_title()
        self.fix_zero_and_move_one()
        self.show_example_actions()
        self.show_action_at_i()
        self.show_action_at_i_again()
        self.show_i_squared_is_negative_one()
        self.talk_through_specific_example()
        self.show_break_down()
        self.example_actions_broken_down()

    def add_plane(self):
        AdditiveGroupOfComplexNumbers.add_plane(self)
        one_dot = Dot(
            self.z_to_point(1), 
            color = MULTIPLIER_COLOR,
            radius = self.dot_radius,
        )
        self.plane.add(one_dot)
        self.plane.one_dot = one_dot
        self.plane.save_state()
        self.add(self.plane)

    def add_title(self):
        title = TextMobject(
            "Multiplicative", "group of", 
            "complex numbers"
        )
        title.to_edge(UP)
        title[0].set_color(MULTIPLIER_COLOR)
        title[2].set_color(BLUE)
        title.add_background_rectangle()

        self.play(Write(title, run_time = 2))
        self.wait()
        self.add_foreground_mobjects(title)

    def fix_zero_and_move_one(self):
        zero_arrow = Arrow(
            UP+1.25*LEFT, ORIGIN, 
            buff = 2*self.dot_radius
        )
        zero_arrow.set_color(ADDER_COLOR)
        zero_words = TextMobject("Fix zero")
        zero_words.set_color(ADDER_COLOR)
        zero_words.add_background_rectangle()
        zero_words.next_to(zero_arrow.get_start(), UP)

        one_point = self.z_to_point(1)
        one_arrow = Arrow(
            one_point+UP+1.25*RIGHT, one_point, 
            buff = 2*self.dot_radius,
            color = MULTIPLIER_COLOR,
        )
        one_words = TextMobject("Drag one")
        one_words.set_color(MULTIPLIER_COLOR)
        one_words.add_background_rectangle()
        one_words.next_to(one_arrow.get_start(), UP)

        self.play(
            Write(zero_words, run_time = 2),
            ShowCreation(zero_arrow),
            Indicate(self.plane.zero_dot, color = RED),
        )
        self.play(
            Write(one_words, run_time = 2),
            ShowCreation(one_arrow),
            Indicate(self.plane.one_dot, color = RED),
        )
        self.wait(2)
        self.play(*list(map(FadeOut, [
            zero_words, zero_arrow,
            one_words, one_arrow,
        ])))

    def show_example_actions(self):
        z_list = [
            complex(2),
            complex(0.5),
            complex(2, 1),
            complex(-2, 2),
        ]
        for last_z, z in zip([1] + z_list, z_list):
            self.multiply_by_z(z/last_z)
            self.wait()
        self.reset_plane()
        self.wait()

    def show_action_at_i(self):
        i_point = self.z_to_point(complex(0, 1))
        i_dot = Dot(i_point)
        i_dot.set_color(RED)
        i_arrow = Arrow(i_point+UP+LEFT, i_point)
        i_arrow.set_color(i_dot.get_color())

        arc = Arc(
            start_angle = np.pi/24,
            angle = 10*np.pi/24,
            radius = self.z_to_point(1)[0],
            num_anchors = 20,
        )
        arc.add_tip(tip_length = 0.15)
        arc.set_color(YELLOW)

        self.play(
            ShowCreation(i_arrow),
            DrawBorderThenFill(i_dot)
        )
        self.wait()
        self.play(
            FadeOut(i_arrow),
            ShowCreation(arc)
        )
        self.add_foreground_mobjects(arc)
        self.wait(2)
        self.multiply_by_z(complex(0, 1), run_time = 3)
        self.remove(i_dot)
        self.wait()

        self.turn_arrow = arc

    def show_action_at_i_again(self):
        neg_one_label = [m for m in self.real_labels if m.get_tex_string() == "-1"][0]
        half_turn_arc = Arc(
            start_angle = np.pi/12,
            angle = 10*np.pi/12,
            color = self.turn_arrow.get_color()
        )
        half_turn_arc.add_tip(tip_length = 0.15)

        self.multiply_by_z(complex(0, 1), run_time = 3)
        self.wait()
        self.play(Transform(
            self.turn_arrow, half_turn_arc,
            path_arc = np.pi/2
        ))
        self.wait()        
        self.play(Indicate(neg_one_label, run_time = 2))
        self.wait()
        self.foreground_mobjects.remove(self.turn_arrow)
        self.reset_plane(FadeOut(self.turn_arrow))

    def show_i_squared_is_negative_one(self):
        equation = TexMobject("i", "\\cdot", "i", "=", "-1")
        terms = equation[::2]
        equation.add_background_rectangle()
        equation.next_to(ORIGIN, RIGHT)
        equation.shift(1.5*UP)
        equation.set_color(MULTIPLIER_COLOR)

        self.play(Write(equation, run_time = 2))
        self.wait()
        for term in terms[:2]:
            self.multiply_by_z(
                complex(0, 1),
                added_anims = [
                    Animation(equation),
                    Indicate(term, color = RED, run_time = 2)
                ]
            )
            self.wait()
        self.play(Indicate(terms[-1], color = RED, run_time = 2))
        self.wait()
        self.reset_plane(FadeOut(equation))

    def talk_through_specific_example(self):
        z = complex(2, 1)
        angle = np.angle(z)
        point = self.z_to_point(z)
        dot = Dot(point, color = WHITE)
        label = TexMobject("%d + %di"%(z.real, z.imag))
        label.add_background_rectangle()
        label.next_to(dot, UP+RIGHT, buff = 0)

        brace = Brace(
            Line(ORIGIN, self.z_to_point(np.sqrt(5))),
            UP
        )
        brace_text = brace.get_text("$\\sqrt{5}$")
        brace_text.add_background_rectangle()
        brace_text.scale(0.7, about_point = brace.get_top())
        brace.rotate(angle)
        brace_text.rotate(angle).rotate_in_place(-angle)
        VGroup(brace, brace_text).set_color(MAROON_B)
        arc = Arc(angle, color = WHITE, radius = 0.5)
        angle_label = TexMobject("30^\\circ")
        angle_label.scale(0.7)
        angle_label.next_to(
            arc, RIGHT, 
            buff = SMALL_BUFF, aligned_edge = DOWN
        )
        angle_label.set_color(MULTIPLIER_COLOR)

        self.play(
            Write(label),
            DrawBorderThenFill(dot)
        )
        self.add_foreground_mobjects(label, dot)
        self.wait()
        self.multiply_by_z(z, run_time = 3)
        self.wait()
        self.reset_plane()
        self.multiply_by_z(
            np.exp(complex(0, 1)*angle),
            added_anims = [
                ShowCreation(arc, run_time = 2),
                Write(angle_label)
            ]
        )
        self.add_foreground_mobjects(arc, angle_label)
        self.wait()
        self.play(
            GrowFromCenter(brace),
            Write(brace_text)
        )
        self.add_foreground_mobjects(brace, brace_text)
        self.multiply_by_z(np.sqrt(5), run_time = 3)
        self.wait(2)
        to_remove = [
            label, dot,
            brace, brace_text, 
            arc, angle_label,
        ]
        for mob in to_remove:
            self.foreground_mobjects.remove(mob)
        self.reset_plane(*list(map(FadeOut, to_remove)))
        self.wait()

    def show_break_down(self):
        positive_reals = Line(ORIGIN, FRAME_X_RADIUS*RIGHT)
        positive_reals.set_color(MAROON_B)
        circle = Circle(
            radius = self.z_to_point(1)[0],
            color = MULTIPLIER_COLOR
        )
        real_actions = [3, 0.5, 1]
        rotation_actions = [
            np.exp(complex(0, angle))
            for angle in np.linspace(0, 2*np.pi, 4)[1:]
        ]

        self.play(ShowCreation(positive_reals))
        self.add_foreground_mobjects(positive_reals)
        for last_z, z in zip([1]+real_actions, real_actions):
            self.multiply_by_z(z/last_z)
        self.wait()
        self.play(ShowCreation(circle))
        self.add_foreground_mobjects(circle)
        for last_z, z in zip([1]+rotation_actions, rotation_actions):
            self.multiply_by_z(z/last_z, run_time = 3)
        self.wait()

    def example_actions_broken_down(self):
        z_list = [
            complex(2, -1),
            complex(-2, -3),
            complex(0.5, 0.5),
        ]
        for z in z_list:
            dot = Dot(self.z_to_point(z))
            dot.set_color(WHITE)
            dot.save_state()
            dot.move_to(self.plane.one_dot)
            dot.set_fill(opacity = 1)

            norm = np.abs(z)
            angle = np.angle(z)
            rot_z = np.exp(complex(0, angle))

            self.play(dot.restore)
            self.multiply_by_z(norm)
            self.wait()
            self.multiply_by_z(rot_z)
            self.wait()
            self.reset_plane(FadeOut(dot))

    ##

    def multiply_by_z(self, z, run_time = 2, **kwargs):
        target = self.plane.copy()
        target.apply_complex_function(lambda w : z*w)
        for dot in target.zero_dot, target.one_dot:
            dot.set_width(2*self.dot_radius)
        angle = np.angle(z)
        kwargs["path_arc"] = kwargs.get("path_arc", angle)
        self.play(
            Transform(self.plane, target, run_time = run_time, **kwargs),
            *kwargs.get("added_anims", [])
        )

    def reset_plane(self, *added_anims):
        self.play(FadeOut(self.plane), *added_anims)
        self.plane.restore()
        self.play(FadeIn(self.plane))

class ExponentsAsRepeatedMultiplication(TeacherStudentsScene):
    def construct(self):
        self.show_repeated_multiplication()
        self.show_non_counting_exponents()

    def show_repeated_multiplication(self):
        three_twos = TexMobject("2 \\cdot 2 \\cdot 2")
        five_twos = TexMobject("2 \\cdot "*4 + "2")
        exponents = []
        teacher_corner = self.get_teacher().get_corner(UP+LEFT)
        for twos in three_twos, five_twos:
            twos.next_to(teacher_corner, UP)
            twos.generate_target()
            d = sum(np.array(list(twos.get_tex_string())) == "2")
            exponents.append(d)
            twos.brace = Brace(twos, UP)
            twos.exp = twos.brace.get_text("$2^%d$"%d)
            twos.generate_target()
            twos.brace_anim = MaintainPositionRelativeTo(
                VGroup(twos.brace, twos.exp), twos
            )

        self.play(
            GrowFromCenter(three_twos.brace),
            Write(three_twos.exp),
            self.get_teacher().change_mode, "raise_right_hand",
        )
        for mob in three_twos:
            self.play(Write(mob, run_time = 1))
        self.change_student_modes(*["pondering"]*3)
        self.wait(2)
        self.play(
            FadeIn(five_twos.brace),
            FadeIn(five_twos.exp),
            three_twos.center,
            three_twos.to_edge, UP, 2*LARGE_BUFF,
            three_twos.brace_anim,
        )
        self.play(FadeIn(
            five_twos, 
            run_time = 3,
            lag_ratio = 0.5
        ))
        self.wait(2)

        cdot = TexMobject("\\cdot")
        lhs = TexMobject("2^{%d + %d} = "%tuple(exponents))
        rule = VGroup(
            lhs, three_twos.target, cdot, five_twos.target
        )
        rule.arrange()
        lhs.next_to(three_twos.target, LEFT, aligned_edge = DOWN)
        rule.next_to(self.get_pi_creatures(), UP)

        self.play(
            MoveToTarget(three_twos),
            three_twos.brace_anim,
            MoveToTarget(five_twos),
            five_twos.brace_anim,
            Write(cdot),
            self.get_teacher().change_mode, "happy",
        )
        self.wait()
        self.play(Write(lhs))
        self.wait()
        self.change_student_modes(*["happy"]*3)
        self.wait()

        general_equation = TexMobject("2^{x+y}=", "2^x", "2^y")
        general_equation.to_edge(UP, buff = MED_LARGE_BUFF)
        general_equation[0].set_color(GREEN_B)
        VGroup(*general_equation[1:]).set_color(MULTIPLIER_COLOR)
        self.play(*[
            ReplacementTransform(
                mob.copy(), term, run_time = 2
            )
            for term, mob in zip(general_equation, [
                lhs, three_twos.exp, five_twos.exp
            ])
        ])
        self.wait(2)

        self.exponential_rule = general_equation
        self.expanded_exponential_rule = VGroup(
            lhs, three_twos, three_twos.brace, three_twos.exp,
            cdot, five_twos, five_twos.brace, five_twos.exp,
        )

    def show_non_counting_exponents(self):
        self.play(
            self.expanded_exponential_rule.scale, 0.5,
            self.expanded_exponential_rule.to_corner, UP+LEFT
        )
        half_power, neg_power, imag_power = alt_powers = VGroup(
            TexMobject("2^{1/2}"),
            TexMobject("2^{-1}"),
            TexMobject("2^{i}"),
        )
        alt_powers.arrange(RIGHT, buff = LARGE_BUFF)
        alt_powers.next_to(self.get_students(), UP, buff = LARGE_BUFF)

        self.play(
            Write(half_power, run_time = 2),
            *[
                ApplyMethod(pi.change_mode, "pondering")
                for pi in self.get_pi_creatures()
            ]
        )
        for mob in alt_powers[1:]:
            self.play(Write(mob, run_time = 1))
            self.wait()
        self.wait()
        self.play(*it.chain(*[
            [pi.change_mode, "confused", pi.look_at, half_power]
            for pi in self.get_students()
        ]))
        for power in alt_powers[:2]:
            self.play(Indicate(power))
            self.wait()
        self.wait()

        self.teacher_says("Extend the \\\\ definition")
        self.change_student_modes("pondering", "confused", "erm")
        self.wait()

        half_expression = TexMobject(
            "\\big(", "2^{1/2}", "\\big)", 
            "\\big(2^{1/2}\\big) = 2^{1}"
        )
        neg_one_expression = TexMobject(
            "\\big(", "2^{-1}", "\\big)", 
            "\\big( 2^{1} \\big) = 2^{0}"
        )
        expressions = VGroup(half_expression, neg_one_expression)
        expressions.arrange(
            DOWN, aligned_edge = LEFT, buff = MED_LARGE_BUFF
        )
        expressions.next_to(self.get_students(), UP, buff = LARGE_BUFF)
        expressions.to_edge(LEFT)

        self.play(
            Transform(half_power, half_expression[1]),
            Write(half_expression),            
            RemovePiCreatureBubble(self.get_teacher()),            
        )
        self.wait()
        self.play(
            Transform(neg_power, neg_one_expression[1]),
            Write(neg_one_expression)
        )
        self.wait(2)
        self.play(
            self.exponential_rule.next_to,
            self.get_teacher().get_corner(UP+LEFT), UP, MED_LARGE_BUFF,
            self.get_teacher().change_mode, "raise_right_hand",
        )
        self.wait(2)
        self.play(
            imag_power.move_to, UP,
            imag_power.scale_in_place, 1.5,
            imag_power.set_color, BLUE,
            self.exponential_rule.to_edge, RIGHT,
            self.get_teacher().change_mode, "speaking"
        )
        self.play(*it.chain(*[
            [pi.change_mode, "pondering", pi.look_at, imag_power]
            for pi in self.get_students()
        ]))
        self.wait()

        group_theory_words = TextMobject("Group theory?")
        group_theory_words.next_to(
            self.exponential_rule, UP, buff = LARGE_BUFF
        )
        arrow = Arrow(
            group_theory_words,
            self.exponential_rule,
            color = WHITE,
            buff = SMALL_BUFF
        )
        group_theory_words.shift_onto_screen()
        self.play(
            Write(group_theory_words), 
            ShowCreation(arrow)
        )
        self.wait(2)

class ExponentsAsHomomorphism(Scene):
    CONFIG = {
        "top_line_center" : 2.5*UP,
        "top_line_config" : {
            "x_min" : -16,
            "x_max" : 16,
        },
        "bottom_line_center" : 2.5*DOWN,
        "bottom_line_config" : {
            "x_min" : -FRAME_WIDTH,
            "x_max" : FRAME_WIDTH,
        }
    }
    def construct(self):
        self.comment_on_equation()
        self.show_adders()
        self.show_multipliers()
        self.confused_at_mapping()
        self.talk_through_composition()
        self.add_quote()

    def comment_on_equation(self):
        equation = TexMobject(
            "2", "^{x", "+", "y}", "=", "2^x", "2^y"
        )
        lhs = VGroup(*equation[:4])
        rhs = VGroup(*equation[5:])
        lhs_brace = Brace(lhs, UP)
        lhs_text = lhs_brace.get_text("Add inputs")
        lhs_text.set_color(GREEN_B)
        rhs_brace = Brace(rhs, DOWN)
        rhs_text = rhs_brace.get_text("Multiply outputs")
        rhs_text.set_color(MULTIPLIER_COLOR)

        self.add(equation)
        for brace, text in (lhs_brace, lhs_text), (rhs_brace, rhs_text):
            self.play(
                GrowFromCenter(brace),
                Write(text)
            )
            self.wait()
        self.wait()

        self.equation = equation
        self.lhs_brace_group = VGroup(lhs_brace, lhs_text)
        self.rhs_brace_group = VGroup(rhs_brace, rhs_text)

    def show_adders(self):
        equation = self.equation
        adders = VGroup(equation[1], equation[3]).copy()
        top_line = NumberLine(**self.top_line_config)
        top_line.add_numbers()
        top_line.shift(self.top_line_center)

        self.play(
            adders.scale, 1.5,
            adders.center,
            adders.space_out_submobjects, 2,
            adders.to_edge, UP,
            adders.set_color, GREEN_B,
            FadeOut(self.lhs_brace_group),
            Write(top_line)
        )
        self.wait()
        for x in 3, 5, -8:
            self.play(top_line.shift, x*RIGHT, run_time = 2)
            self.wait()

        self.top_line = top_line
        self.adders = adders

    def show_multipliers(self):
        equation = self.equation
        multipliers = VGroup(*self.equation[-2:]).copy()

        bottom_line = NumberLine(**self.bottom_line_config)
        bottom_line.add_numbers()
        bottom_line.shift(self.bottom_line_center)

        self.play(
            multipliers.space_out_submobjects, 4,
            multipliers.next_to, self.bottom_line_center, 
                UP, MED_LARGE_BUFF,
            multipliers.set_color, YELLOW,
            FadeOut(self.rhs_brace_group),
            Write(bottom_line),
        )
        stretch_kwargs = {
        }
        for x in 3, 1./5, 5./3:
            self.play(
                self.get_stretch_anim(bottom_line, x),
                run_time = 3
            )
        self.wait()

        self.bottom_line = bottom_line
        self.multipliers = multipliers

    def confused_at_mapping(self):
        arrow = Arrow(
            self.top_line.get_bottom()[1]*UP,
            self.bottom_line.get_top()[1]*UP,
            color = WHITE
        )
        randy = Randolph(mode = "confused")
        randy.scale(0.75)
        randy.flip()
        randy.next_to(arrow, RIGHT, LARGE_BUFF)
        randy.look_at(arrow.get_top())

        self.play(self.equation.to_edge, LEFT)
        self.play(
            ShowCreation(arrow),
            FadeIn(randy)
        )
        self.play(randy.look_at, arrow.get_bottom())
        self.play(Blink(randy))
        self.wait()
        for x in 1, -2, 3, 1, -3:
            self.play(
                self.get_stretch_anim(self.bottom_line, 2**x),
                self.top_line.shift, x*RIGHT,
                randy.look_at, self.top_line,
                run_time = 2
            )
            if random.random() < 0.3:
                self.play(Blink(randy))
            else:
                self.wait()

        self.randy = randy

    def talk_through_composition(self):
        randy = self.randy
        terms = list(self.adders) + list(self.multipliers)
        inputs = [-1, 2]
        target_texs = list(map(str, inputs))
        target_texs += ["2^{%d}"%x for x in inputs]
        for mob, target_tex in zip(terms, target_texs):
            target = TexMobject(target_tex)
            target.set_color(mob[0].get_color())
            target.move_to(mob, DOWN)
            if mob in self.adders:
                target.to_edge(UP)
            mob.target = target

        self.play(
            self.equation.next_to, ORIGIN, LEFT, MED_LARGE_BUFF,
            randy.change_mode, "pondering",
            randy.look_at, self.equation
        )
        self.wait()
        self.play(randy.look_at, self.top_line)
        self.show_composition(
            *inputs,
            parallel_anims = list(map(MoveToTarget, self.adders))
        )
        self.play(
            FocusOn(self.bottom_line_center),
            randy.look_at, self.bottom_line_center,
        )
        self.show_composition(
            *inputs,
            parallel_anims = list(map(MoveToTarget, self.multipliers))
        )
        self.wait()

    def add_quote(self):
        brace = Brace(self.equation, UP)
        quote = TextMobject("``Preserves the group structure''")
        quote.add_background_rectangle()
        quote.next_to(brace, UP)

        self.play(
            GrowFromCenter(brace),
            Write(quote),
            self.randy.look_at, quote,
        )
        self.play(self.randy.change_mode, "thinking")
        self.play(Blink(self.randy))
        self.wait()
        self.show_composition(-1, 2)
        self.wait()

    ####

    def show_composition(self, *inputs, **kwargs):
        parallel_anims = kwargs.get("parallel_anims", [])
        for x in range(len(inputs) - len(parallel_anims)):
            parallel_anims.append(Animation(Mobject()))

        for line in self.top_line, self.bottom_line:
            line.save_state()

        for x, parallel_anim in zip(inputs, parallel_anims):
            anims = [
                ApplyMethod(self.top_line.shift, x*RIGHT),
                self.get_stretch_anim(self.bottom_line, 2**x),
            ]
            for anim in anims:
                anim.set_run_time(2)
            self.play(parallel_anim)
            self.play(*anims)
            self.wait()
        self.play(*[
            line.restore 
            for line in (self.top_line, self.bottom_line)
        ])

    def get_stretch_anim(self, bottom_line, x):
        target = bottom_line.copy()
        target.stretch_about_point(
            x, 0, self.bottom_line_center,
        )
        for number in target.numbers:
            number.stretch_in_place(1./x, dim = 0)
        return Transform(bottom_line, target)

class DihedralCubeHomomorphism(GroupOfCubeSymmetries, SymmetriesOfSquare):
    def construct(self):
        angle_axis_pairs = [
            (np.pi/2, OUT),
            (np.pi, RIGHT),
            (np.pi, OUT),
            (np.pi, UP+RIGHT),
            (-np.pi/2, OUT),
            (np.pi, UP+LEFT),
        ]
        angle_axis_pairs *= 3

        title = TextMobject(
            "``", "Homo", "morph", "ism", "''", 
            arg_separator = ""
        )
        homo_brace = Brace(title[1], UP, buff = SMALL_BUFF)
        homo_def = homo_brace.get_text("same")
        morph_brace = Brace(title[2], UP, buff = SMALL_BUFF)
        morph_def = morph_brace.get_text("shape", buff = SMALL_BUFF)
        def_group = VGroup(
            homo_brace, homo_def, 
            morph_brace, morph_def
        )
        VGroup(title, def_group).to_edge(UP)
        homo_group = VGroup(title[1], homo_brace, homo_def)
        morph_group = VGroup(title[2], morph_brace, morph_def)

        equation = TexMobject("f(X \\circ Y) = f(X) \\circ f(Y)")
        equation.next_to(title, DOWN)

        self.add(title, equation)

        arrow = Arrow(LEFT, RIGHT)
        cube = self.get_cube()
        cube.next_to(arrow, RIGHT)
        pose_matrix = self.get_pose_matrix()

        square = self.square = Square(**self.square_config)
        self.add_randy_to_square(square)
        square.next_to(arrow, LEFT)

        VGroup(square, arrow, cube).next_to(
            equation, DOWN, buff = MED_LARGE_BUFF
        )

        self.add(square, cube)
        self.play(ShowCreation(arrow))
        for i, (angle, raw_axis) in enumerate(angle_axis_pairs):
            posed_axis = np.dot(raw_axis, pose_matrix.T)
            self.play(*[
                Rotate(
                    mob, angle = angle, axis = axis, 
                    in_place = True,
                    run_time = abs(angle/(np.pi/2))
                )
                for mob, axis in [(square, raw_axis), (cube, posed_axis)]
            ])
            self.wait()
            if i == 2:
                for group, color in (homo_group, YELLOW), (morph_group, BLUE):
                    part, remainder = group[0], VGroup(*group[1:])
                    remainder.set_color(color)
                    self.play(
                        part.set_color, color,
                        FadeIn(remainder)
                    )

class ComplexExponentiationAbstract():
    CONFIG = {
        "start_base" : 2,
        "new_base" : 5,
        "group_type" : None,
        "color" : None,
        "vect" : None,
    }
    def construct(self):
        self.base = self.start_base
        example_inputs = [2, -3, 1]
        self.add_vertical_line()
        self.add_plane_unanimated()
        self.add_title()
        self.add_arrow()
        self.show_example(complex(1, 1))
        self.draw_real_line()
        self.show_real_actions(*example_inputs)
        self.show_pure_imaginary_actions(*example_inputs)
        self.set_color_vertical_line()
        self.set_color_unit_circle()
        self.show_pure_imaginary_actions(*example_inputs)
        self.walk_input_up_vertical()
        self.change_base(self.new_base, str(self.new_base))
        self.walk_input_up_vertical()
        self.change_base(np.exp(1), "e")
        self.take_steps_for_e()
        self.write_eulers_formula()
        self.show_pure_imaginary_actions(-np.pi, np.pi)
        self.wait()

    def add_vertical_line(self):
        line = Line(FRAME_Y_RADIUS*UP, FRAME_Y_RADIUS*DOWN)
        line.set_stroke(color = self.color, width = 10)
        line.shift(-FRAME_X_RADIUS*self.vect/2)
        self.add(line)
        self.add_foreground_mobjects(line)

    def add_plane_unanimated(self):
        should_skip_animations = self.skip_animations
        self.skip_animations = True
        self.add_plane()
        self.skip_animations = should_skip_animations

    def add_title(self):
        title = TextMobject(self.group_type, "group")
        title.scale(0.8)
        title[0].set_color(self.color)
        title.add_background_rectangle()
        title.to_edge(UP, buff = MED_SMALL_BUFF)
        self.add_foreground_mobjects(title)

    def add_arrow(self):
        arrow = Arrow(LEFT, RIGHT, color = WHITE)
        arrow.move_to(-FRAME_X_RADIUS*self.vect/2 + 2*UP)
        arrow.set_stroke(width = 6),
        func_mob = TexMobject("2^x")    
        func_mob.next_to(arrow, UP, aligned_edge = LEFT)
        func_mob.add_background_rectangle()

        self.add_foreground_mobjects(arrow, func_mob)
        self.wait()
        self.func_mob = func_mob

    def show_example(self, z):
        self.apply_action(
            z,
            run_time = 5,
            rate_func = there_and_back
        )

    def draw_real_line(self):
        line = VGroup(Line(ORIGIN, FRAME_X_RADIUS*RIGHT))
        if self.vect[0] < 0:
            line.add(Line(ORIGIN, FRAME_X_RADIUS*LEFT))
        line.set_color(RED)

        self.play(*list(map(ShowCreation, line)), run_time = 3)
        self.add_foreground_mobjects(line)

        self.real_line = line

    def show_real_actions(self, *example_inputs):
        for x in example_inputs:
            self.apply_action(x)
            self.wait()

    def show_pure_imaginary_actions(self, *example_input_imag_parts):
        for y in example_input_imag_parts:
            self.apply_action(complex(0, y), run_time = 3)
            self.wait()

    def change_base(self, new_base, new_base_tex):
        new_func_mob = TexMobject(new_base_tex + "^x")
        new_func_mob.add_background_rectangle()
        new_func_mob.move_to(self.func_mob)

        self.play(FocusOn(self.func_mob))
        self.play(Transform(self.func_mob, new_func_mob))
        self.wait()
        self.base = new_base

    def write_eulers_formula(self):
        formula = TexMobject("e^", "{\\pi", "i}", "=", "-1")
        VGroup(*formula[1:3]).set_color(ADDER_COLOR)
        formula[-1].set_color(MULTIPLIER_COLOR)
        formula.scale(1.5)
        formula.next_to(ORIGIN, UP)
        formula.shift(-FRAME_X_RADIUS*self.vect/2)
        for part in formula:
            part.add_to_back(BackgroundRectangle(part))

        Scene.play(self, Write(formula))
        self.add_foreground_mobjects(formula)
        self.wait(2)

class ComplexExponentiationAdderHalf(
    ComplexExponentiationAbstract, 
    AdditiveGroupOfComplexNumbers
    ):
    CONFIG = {
        "group_type" : "Additive",
        "color" : GREEN_B,
        "vect" : LEFT,
    }
    def construct(self):
        ComplexExponentiationAbstract.construct(self)

    def apply_action(self, z, run_time = 2, **kwargs):
        kwargs["run_time"] = run_time
        self.play(
            ApplyMethod(
                self.plane.shift, self.z_to_point(z),
                **kwargs
            ),
            *kwargs.get("added_anims", [])
        )

    def set_color_vertical_line(self):
        line = VGroup(
            Line(ORIGIN, FRAME_Y_RADIUS*UP),
            Line(ORIGIN, FRAME_Y_RADIUS*DOWN),
        )
        line.set_color(YELLOW)

        self.play(
            FadeOut(self.real_line),
            *list(map(ShowCreation, line))
        )
        self.foreground_mobjects.remove(self.real_line)
        self.play(
            line.rotate, np.pi/24,
            rate_func = wiggle,
        )
        self.wait()

        self.foreground_mobjects = [line] + self.foreground_mobjects
        self.vertical_line = line

    def set_color_unit_circle(self):
        line = VGroup(
            Line(ORIGIN, FRAME_Y_RADIUS*UP),
            Line(ORIGIN, FRAME_Y_RADIUS*DOWN),
        )
        line.set_color(YELLOW)
        for submob in line:
            submob.insert_n_curves(10)
            submob.make_smooth()
        circle = VGroup(
            Circle(),
            Circle().flip(RIGHT),
        )
        circle.set_color(YELLOW)
        circle.shift(FRAME_X_RADIUS*RIGHT)

        self.play(ReplacementTransform(
            line, circle, run_time = 3
        ))
        self.remove(circle)
        self.wait()

    def walk_input_up_vertical(self):
        arrow = Arrow(ORIGIN, UP, buff = 0, tip_length = 0.15)
        arrow.set_color(GREEN)
        brace = Brace(arrow, RIGHT, buff = SMALL_BUFF)
        brace_text = brace.get_text("1 unit")
        brace_text.add_background_rectangle()

        Scene.play(self, ShowCreation(arrow))
        self.add_foreground_mobjects(arrow)
        self.play(
            GrowFromCenter(brace),
            Write(brace_text, run_time = 1)
        )
        self.add_foreground_mobjects(brace, brace_text)        
        self.wait()
        self.apply_action(complex(0, 1))
        self.wait(7)##Line up with MultiplierHalf

        to_remove = arrow, brace, brace_text
        for mob in to_remove:
            self.foreground_mobjects.remove(mob)
        self.play(*list(map(FadeOut, to_remove)))
        self.apply_action(complex(0, -1))

    def take_steps_for_e(self):
        slide_values = [1, 1, 1, np.pi-3]
        braces = [
            Brace(Line(ORIGIN, x*UP), RIGHT, buff = SMALL_BUFF)
            for x in np.cumsum(slide_values)
        ]
        labels = list(map(TextMobject, [
            "1 unit",
            "2 units",
            "3 units",
            "$\\pi$ units",
        ]))
        for label, brace in zip(labels, braces):
            label.add_background_rectangle()
            label.next_to(brace, RIGHT, buff = SMALL_BUFF)

        curr_brace = None
        curr_label = None
        for slide_value, label, brace in zip(slide_values, labels, braces):
            self.apply_action(complex(0, slide_value))
            if curr_brace is None:
                curr_brace = brace
                curr_label = label
                self.play(
                    GrowFromCenter(curr_brace),
                    Write(curr_label)
                )
                self.add_foreground_mobjects(brace, label)
            else:
                self.play(
                    Transform(curr_brace, brace),
                    Transform(curr_label, label),
                )
            self.wait()
            self.wait(4) ##Line up with multiplier half

class ComplexExponentiationMultiplierHalf(
    ComplexExponentiationAbstract, 
    MultiplicativeGroupOfComplexNumbers
    ):
    CONFIG = {
        "group_type" : "Multiplicative",
        "color" : MULTIPLIER_COLOR,
        "vect" : RIGHT,
    }

    def construct(self):
        ComplexExponentiationAbstract.construct(self)

    def apply_action(self, z, run_time = 2, **kwargs):
        kwargs["run_time"] = run_time
        self.multiply_by_z(self.base**z, **kwargs)

    def set_color_vertical_line(self):
        self.play(FadeOut(self.real_line))
        self.foreground_mobjects.remove(self.real_line)
        self.wait(2)

    def set_color_unit_circle(self):
        line = VGroup(
            Line(ORIGIN, FRAME_Y_RADIUS*UP),
            Line(ORIGIN, FRAME_Y_RADIUS*DOWN),
        )
        line.set_color(YELLOW)
        line.shift(FRAME_X_RADIUS*LEFT)
        for submob in line:
            submob.insert_n_curves(10)
            submob.make_smooth()
        circle = VGroup(
            Circle(),
            Circle().flip(RIGHT),
        )
        circle.set_color(YELLOW)

        self.play(ReplacementTransform(
            line, circle, run_time = 3
        ))
        self.add_foreground_mobjects(circle)
        self.wait()

    def walk_input_up_vertical(self):
        output_z = self.base**complex(0, 1)
        angle = np.angle(output_z)

        arc, brace, curved_brace, radians_label = \
            self.get_arc_braces_and_label(angle)

        self.wait(3)
        self.apply_action(complex(0, 1))

        Scene.play(self, ShowCreation(arc))
        self.add_foreground_mobjects(arc)
        self.play(GrowFromCenter(brace))
        self.play(Transform(brace, curved_brace))
        self.play(Write(radians_label, run_time = 2))
        self.wait(2)

        self.foreground_mobjects.remove(arc)
        self.play(*list(map(FadeOut, [arc, brace, radians_label])))
        self.apply_action(complex(0, -1))

    def get_arc_braces_and_label(self, angle):
        arc = Arc(angle)
        arc.set_stroke(GREEN, width = 6)
        arc_line = Line(RIGHT, RIGHT+angle*UP)
        brace = Brace(arc_line, RIGHT, buff = 0)
        for submob in brace.family_members_with_points():
            submob.insert_n_curves(10)
        curved_brace = brace.copy()
        curved_brace.shift(LEFT)
        curved_brace.apply_complex_function(
            np.exp, maintain_smoothness = False
        )

        half_point = arc.point_from_proportion(0.5)
        radians_label = TexMobject("%.3f"%angle)
        radians_label.add_background_rectangle()
        radians_label.next_to(
            1.5*half_point, np.round(half_point), buff = 0
        )

        return arc, brace, curved_brace, radians_label

    def take_steps_for_e(self):
        angles = [1, 2, 3, np.pi]

        curr_brace = None
        curr_label = None
        curr_arc = None
        for last_angle, angle in zip([0]+angles, angles):
            arc, brace, curved_brace, label = self.get_arc_braces_and_label(angle)
            if angle == np.pi:
                label = TexMobject("%.5f\\dots"%np.pi)
                label.add_background_rectangle(opacity = 1)
                label.next_to(curved_brace, UP, buff = SMALL_BUFF)

            self.apply_action(complex(0, angle-last_angle))
            self.wait(2)#Line up with Adder half
            if curr_brace is None:
                curr_brace = curved_brace
                curr_label = label
                curr_arc = arc
                brace.set_fill(opacity = 0)
                Scene.play(self, ShowCreation(curr_arc))
                self.add_foreground_mobjects(curr_arc)
                self.play(
                    ReplacementTransform(brace, curr_brace),
                    Write(curr_label)
                )
                self.add_foreground_mobjects(curr_brace, curr_label)
            else:
                Scene.play(self, ShowCreation(arc))
                self.add_foreground_mobjects(arc)
                self.foreground_mobjects.remove(curr_arc)
                self.remove(curr_arc)
                curr_arc = arc
                self.play(
                    Transform(curr_brace, curved_brace),
                    Transform(curr_label, label),
                )
            self.wait()
            self.wait()

class ExpComplexHomomorphismPreviewAbstract(ComplexExponentiationAbstract):
    def construct(self):
        self.base = self.start_base

        self.add_vertical_line()
        self.add_plane_unanimated()
        self.add_title()
        self.add_arrow()
        self.change_base(np.exp(1), "e")
        self.write_eulers_formula()
        self.show_pure_imaginary_actions(np.pi, 0, -np.pi)
        self.wait()

class ExpComplexHomomorphismPreviewAdderHalf(
    ExpComplexHomomorphismPreviewAbstract,
    ComplexExponentiationAdderHalf
    ):
    def construct(self):
        ExpComplexHomomorphismPreviewAbstract.construct(self)

class ExpComplexHomomorphismPreviewMultiplierHalf(
    ExpComplexHomomorphismPreviewAbstract,
    ComplexExponentiationMultiplierHalf
    ):
    def construct(self):
        ExpComplexHomomorphismPreviewAbstract.construct(self)

class WhyE(TeacherStudentsScene):
    def construct(self):
        self.student_says("Why e?")
        self.play(self.get_teacher().change_mode, "pondering")
        self.wait(3)

class ReadFormula(Scene):
    def construct(self):
        formula = TexMobject("e^", "{\\pi i}", "=", "-1")
        formula[1].set_color(GREEN_B)
        formula[3].set_color(MULTIPLIER_COLOR)
        formula.scale(2)

        randy = Randolph()
        randy.shift(2*LEFT)
        formula.next_to(randy, RIGHT, aligned_edge = UP)
        randy.look_at(formula)

        self.add(randy, formula)
        self.wait()
        self.play(randy.change_mode, "thinking")
        self.wait()
        self.play(Blink(randy))
        self.wait(3)

class EfvgtPatreonThanks(PatreonThanks):
    CONFIG = {
        "specific_patrons" : [
            "Ali Yahya",
            "Meshal  Alshammari",
            "CrypticSwarm    ",
            "Justin Helps",
            "Ankit Agarwal",
            "Yu  Jun",
            "Shelby  Doolittle",
            "Dave    Nicponski",
            "Damion  Kistler",
            "Juan    Benet",
            "Othman  Alikhan",
            "Markus  Persson",
            "Dan Buchoff",
            "Derek Dai",
            "Joseph  John Cox",
            "Luc Ritchie",
            "Nils Schneider",
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

class EmeraldLogo(SVGMobject):
    CONFIG = {
        "file_name" : "emerald_logo",
        "stroke_width" : 0,
        "fill_opacity" : 1,
        # "helix_color" : "#439271",
        "helix_color" : GREEN_E,
    }
    def __init__(self, **kwargs):
        SVGMobject.__init__(self, **kwargs)
        self.set_height(1)
        for submob in self.split()[18:]:
            submob.set_color(self.helix_color)

class ECLPromo(PiCreatureScene):
    CONFIG = {
        "seconds_to_blink" : 4,
    }
    def construct(self):
        logo = EmeraldLogo()
        logo.to_corner(UP+LEFT, buff = MED_SMALL_BUFF)
        logo_part1 = VGroup(*logo[:15])
        logo_part2 = VGroup(*logo[15:])

        rect = Rectangle(height = 9, width = 16)
        rect.set_height(5)
        rect.next_to(logo, DOWN)
        rect.to_edge(LEFT)

        self.play(
            self.pi_creature.change_mode, "hooray",
            ShowCreation(rect)
        )
        self.wait(3)
        self.play(FadeIn(
            logo_part1, run_time = 3, 
            lag_ratio = 0.5
        ))
        logo_part2.save_state()
        logo_part2.scale(2)
        logo_part2.next_to(self.pi_creature.get_corner(UP+LEFT), UP)
        logo_part2.shift(MED_SMALL_BUFF*RIGHT)
        self.play(
            self.pi_creature.change_mode, "raise_right_hand",
        )        
        self.play(DrawBorderThenFill(logo_part2))
        self.play(
            logo_part2.scale_in_place, 0.5,
            logo_part2.to_edge, UP
        )
        self.play(
            logo_part2.restore,
            self.pi_creature.change_mode, "happy"
        )
        self.play(self.pi_creature.look_at, rect)
        self.wait(10)
        self.play(
            self.pi_creature.change_mode, "pondering",
            self.pi_creature.look, DOWN
        )
        self.wait(10)

class ExpTransformation(ComplexTransformationScene):
    CONFIG = {
        "camera_class": ThreeDCamera,
    }
    def construct(self):
        self.camera.camera_distance = 10,
        self.add_transformable_plane()
        self.prepare_for_transformation(self.plane)
        final_plane = self.plane.copy().apply_complex_function(np.exp)
        cylinder = self.plane.copy().apply_function(
            lambda x_y_z : np.array([x_y_z[0], np.sin(x_y_z[1]), -np.cos(x_y_z[1])])
        )
        title = TexMobject("x \\to e^x")
        title.add_background_rectangle()
        title.scale(1.5)
        title.next_to(ORIGIN, RIGHT)
        title.to_edge(UP, buff = MED_SMALL_BUFF)
        self.add_foreground_mobjects(title)

        self.play(Transform(
            self.plane, cylinder, 
            run_time = 3,
            path_arc_axis = RIGHT,
            path_arc = np.pi,
        ))
        self.play(Rotate(
            self.plane, -np.pi/3, UP, 
            run_time = 5
        ))
        self.play(Transform(self.plane, final_plane, run_time = 3))
        self.wait(3)

class Thumbnail(Scene):
    def construct(self):
        formula = TexMobject("e^", "{\\pi i}", "=", "-1")
        formula[1].set_color(GREEN_B)
        formula[3].set_color(YELLOW)
        formula.scale(4)
        formula.to_edge(UP, buff = LARGE_BUFF)
        self.add(formula)

        via = TextMobject("via")
        via.scale(2)
        groups = TextMobject("Group theory")
        groups.scale(3)
        groups.to_edge(DOWN)
        via.move_to(VGroup(formula, groups))
        self.add(via, groups)



      






























