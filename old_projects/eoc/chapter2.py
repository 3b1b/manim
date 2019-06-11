from manimlib.imports import *

DISTANCE_COLOR = BLUE
TIME_COLOR = YELLOW
VELOCITY_COLOR = GREEN


#### Warning, scenes here not updated based on most recent GraphScene changes #######


class IncrementNumber(Succession):
    CONFIG = {
        "start_num" : 0,
        "changes_per_second" : 1,
        "run_time" : 11,
    }
    def __init__(self, num_mob, **kwargs):
        digest_config(self, kwargs)
        n_iterations = int(self.run_time * self.changes_per_second)
        new_num_mobs = [
            TexMobject(str(num)).move_to(num_mob, LEFT)
            for num in range(self.start_num, self.start_num+n_iterations)
        ]
        transforms = [
            Transform(
                num_mob, new_num_mob, 
                run_time = 1.0/self.changes_per_second,
                rate_func = squish_rate_func(smooth, 0, 0.5)
            )
            for new_num_mob in new_num_mobs
        ]
        Succession.__init__(
            self, *transforms, **{
                "rate_func" : None,
                "run_time" : self.run_time,
            }
        )

class IncrementTest(Scene):
    def construct(self):
        num = TexMobject("0")
        num.shift(UP)
        self.play(IncrementNumber(num))
        self.wait()



############################

class Chapter2OpeningQuote(OpeningQuote):
    CONFIG = {
        "quote" : [
            "So far as the theories of mathematics are about",
            "reality,", 
            "they are not",
            "certain;", 
            "so far as they are",
            "certain,", 
            "they are not about",
            "reality.",
        ],
        "highlighted_quote_terms" : {
            "reality," : BLUE,
            "certain;" : GREEN,
            "certain," : GREEN,
            "reality." : BLUE,
        },
        "author" : "Albert Einstein"
    }

class Introduction(TeacherStudentsScene):
    def construct(self):
        goals = TextMobject(
            "Goals: ",
            "1) Learn derivatives", 
            ", 2) Avoid paradoxes.",
            arg_separator = ""
        )
        goals[1].set_color(MAROON_B)
        goals[2].set_color(RED)
        goals[2][0].set_color(WHITE)
        goals.to_edge(UP)
        self.add(*goals[:2])

        self.student_says(
            "What is a derivative?",
            run_time = 2
        )
        self.play(self.get_teacher().change_mode, "happy")
        self.wait()
        self.teacher_says(
            "It's actually a \\\\",
            "very subtle idea",
            target_mode = "well"
        )
        self.change_student_modes(None, "pondering", "thinking")
        self.play(Write(goals[2], run_time = 2))
        self.change_student_modes("erm")
        self.student_says(
            "Instantaneous rate of change", "?",
            student_index = 0,
        )
        self.wait()

        bubble = self.get_students()[0].bubble
        phrase = bubble.content[0]
        bubble.content.remove(phrase)
        self.play(
            FadeOut(bubble),
            FadeOut(bubble.content),
            FadeOut(goals),
            phrase.center,
            phrase.scale, 1.5,
            phrase.to_edge, UP,
            *it.chain(*[
                [
                    pi.change_mode, mode,
                    pi.look_at, FRAME_Y_RADIUS*UP
                ]
                for pi, mode in zip(self.get_pi_creatures(), [
                    "speaking", "pondering", "confused", "confused",
                ])
            ])
        )
        self.wait()
        change = VGroup(*phrase[-len("change"):])
        instantaneous = VGroup(*phrase[:len("instantaneous")])
        change_brace = Brace(change)
        change_description = change_brace.get_text(
            "Requires multiple \\\\ points in time"
        )
        instantaneous_brace = Brace(instantaneous)
        instantaneous_description = instantaneous_brace.get_text(
            "One point \\\\ in time"
        )
        clock = Clock()
        clock.next_to(change_description, DOWN)
        def get_clock_anim(run_time = 3):
            return ClockPassesTime(
                clock,
                hours_passed = 0.4*run_time,
                run_time = run_time,
            )
        self.play(FadeIn(clock))
        self.play(
            change.set_color_by_gradient, BLUE, YELLOW,
            GrowFromCenter(change_brace),
            Write(change_description),
            get_clock_anim()
        )
        self.play(get_clock_anim(1))
        stopped_clock = clock.copy()
        stopped_clock.next_to(instantaneous_description, DOWN)
        self.play(
            instantaneous.set_color, BLUE,
            GrowFromCenter(instantaneous_brace),
            Transform(change_description.copy(), instantaneous_description),
            clock.copy().next_to, instantaneous_description, DOWN,
            get_clock_anim(3)
        )
        self.play(get_clock_anim(12))

class FathersOfCalculus(Scene):
    CONFIG = {
        "names" : [
            "Barrow",
            "Newton", 
            "Leibniz",
            "Cauchy",
            "Weierstrass",
        ],
        "picture_height" : 2.5,
    }
    def construct(self):
        title = TextMobject("(A few) Fathers of Calculus")
        title.to_edge(UP)
        self.add(title)

        men = Mobject()
        for name in self.names:
            image = ImageMobject(name, invert = False)
            image.set_height(self.picture_height)
            title = TextMobject(name)
            title.scale(0.8)
            title.next_to(image, DOWN)
            image.add(title)
            men.add(image)
        men.arrange(RIGHT, aligned_edge = UP)
        men.shift(DOWN)

        discover_brace = Brace(Mobject(*men[:3]), UP)
        discover = discover_brace.get_text("Discovered it")
        VGroup(discover_brace, discover).set_color(BLUE)
        rigor_brace = Brace(Mobject(*men[3:]), UP)
        rigor = rigor_brace.get_text("Made it rigorous")
        rigor.shift(0.1*DOWN)
        VGroup(rigor_brace, rigor).set_color(YELLOW)


        for man in men:
            self.play(FadeIn(man))
        self.play(
            GrowFromCenter(discover_brace),
            Write(discover, run_time = 1)
        )
        self.play(
            GrowFromCenter(rigor_brace),
            Write(rigor, run_time = 1)
        )
        self.wait()

class IntroduceCar(Scene):
    CONFIG = {
        "should_transition_to_graph" : True,
        "show_distance" : True,
        "point_A" : DOWN+4*LEFT,
        "point_B" : DOWN+5*RIGHT,
    }
    def construct(self):
        point_A, point_B = self.point_A, self.point_B
        A = Dot(point_A)
        B = Dot(point_B)
        line = Line(point_A, point_B)
        VGroup(A, B, line).set_color(WHITE)        
        for dot, tex in (A, "A"), (B, "B"):
            label = TexMobject(tex).next_to(dot, DOWN)
            dot.add(label)

        car = Car()
        self.car = car #For introduce_added_mobjects use in subclasses
        car.move_to(point_A)
        front_line = car.get_front_line()

        time_label = TextMobject("Time (in seconds):", "0")
        time_label.shift(2*UP)

        distance_brace = Brace(line, UP)
        # distance_brace.set_fill(opacity = 0.5)
        distance = distance_brace.get_text("100m")

        self.add(A, B, line, car, time_label)
        self.play(ShowCreation(front_line))
        self.play(FadeOut(front_line))
        self.introduce_added_mobjects()
        self.play(
            MoveCar(car, point_B, run_time = 10),
            IncrementNumber(time_label[1], run_time = 11),
            *self.get_added_movement_anims()
        )
        front_line = car.get_front_line()
        self.play(ShowCreation(front_line))
        self.play(FadeOut(front_line))

        if self.show_distance:
            self.play(
                GrowFromCenter(distance_brace),
                Write(distance)
            )
            self.wait()

        if self.should_transition_to_graph:
            self.play(
                car.move_to, point_A,
                FadeOut(time_label),
                FadeOut(distance_brace),
                FadeOut(distance),
            )
            graph_scene = GraphCarTrajectory(skip_animations = True)
            origin = graph_scene.graph_origin
            top = graph_scene.coords_to_point(0, 100)
            new_length = get_norm(top-origin)
            new_point_B = point_A + new_length*RIGHT
            car_line_group = VGroup(car, A, B, line)
            for mob in car_line_group:
                mob.generate_target()
            car_line_group.target = VGroup(*[
                m.target for m in car_line_group
            ])
            B = car_line_group[2]
            B.target.shift(new_point_B - point_B)
            line.target.put_start_and_end_on(
                point_A, new_point_B
            )

            car_line_group.target.rotate(np.pi/2, about_point = point_A)
            car_line_group.target.shift(graph_scene.graph_origin - point_A)
            self.play(MoveToTarget(car_line_group, path_arc = np.pi/2))
            self.wait()

    def introduce_added_mobjects(self):
        pass

    def get_added_movement_anims(self):
        return []

class GraphCarTrajectory(GraphScene):
    CONFIG = {
        "x_min" : 0,
        "x_max" : 10,
        "x_labeled_nums" : list(range(1, 11)),
        "x_axis_label" : "Time (seconds)",
        "y_min" : 0,
        "y_max" : 110,
        "y_tick_frequency" : 10,
        "y_labeled_nums" : list(range(10, 110, 10)),
        "y_axis_label" : "Distance traveled \\\\ (meters)",
        "graph_origin" : 2.5*DOWN + 5*LEFT,
        "default_graph_colors" : [DISTANCE_COLOR, VELOCITY_COLOR],
        "default_derivative_color" : VELOCITY_COLOR,
        "time_of_journey" : 10,
        "care_movement_rate_func" : smooth,
    }
    def construct(self):
        self.setup_axes(animate = False)
        graph = self.graph_sigmoid_trajectory_function()
        origin = self.coords_to_point(0, 0)

        self.introduce_graph(graph, origin)
        self.comment_on_slope(graph, origin)
        self.show_velocity_graph()
        self.ask_critically_about_velocity()

    def graph_sigmoid_trajectory_function(self, **kwargs):
        graph = self.get_graph(
            lambda t : 100*smooth(t/10.),
            **kwargs
        )
        self.s_graph = graph
        return graph

    def introduce_graph(self, graph, origin):
        h_line, v_line = [
            Line(origin, origin, color = color, stroke_width = 2)
            for color in (TIME_COLOR, DISTANCE_COLOR)
        ]
        def h_update(h_line, proportion = 1):
            end = graph.point_from_proportion(proportion)
            t_axis_point = end[0]*RIGHT + origin[1]*UP
            h_line.put_start_and_end_on(t_axis_point, end)
        def v_update(v_line, proportion = 1):
            end = graph.point_from_proportion(proportion)
            d_axis_point = origin[0]*RIGHT + end[1]*UP
            v_line.put_start_and_end_on(d_axis_point, end)

        car = Car()
        car.rotate(np.pi/2)
        car.move_to(origin)
        car_target = origin*RIGHT + graph.point_from_proportion(1)*UP


        self.add(car)
        self.play(
            ShowCreation(
                graph,
                rate_func=linear,
            ),
            MoveCar(
                car, car_target,
                rate_func = self.care_movement_rate_func
            ),
            UpdateFromFunc(h_line, h_update),
            UpdateFromFunc(v_line, v_update),
            run_time = self.time_of_journey,
        )
        self.wait()
        self.play(*list(map(FadeOut, [h_line, v_line, car])))

        #Show example vertical distance
        h_update(h_line, 0.6)
        t_dot = Dot(h_line.get_start(), color = h_line.get_color())
        t_dot.save_state()
        t_dot.move_to(self.x_axis_label_mob)
        t_dot.set_fill(opacity = 0)
        dashed_h = DashedLine(*h_line.get_start_and_end())
        dashed_h.set_color(h_line.get_color())
        brace = Brace(dashed_h, RIGHT)
        brace_text = brace.get_text("Distance traveled")
        self.play(t_dot.restore)
        self.wait()
        self.play(ShowCreation(dashed_h))
        self.play(
            GrowFromCenter(brace),
            Write(brace_text)
        )
        self.wait(2)
        self.play(*list(map(FadeOut, [t_dot, dashed_h, brace, brace_text])))

        #Name graph
        s_of_t = TexMobject("s(t)")
        s_of_t.next_to(
            graph.point_from_proportion(1), 
            DOWN+RIGHT,
            buff = SMALL_BUFF
        )
        s = s_of_t[0]
        d = TexMobject("d")
        d.move_to(s, DOWN)
        d.set_color(DISTANCE_COLOR)

        self.play(Write(s_of_t))
        self.wait()
        s.save_state()
        self.play(Transform(s, d))
        self.wait()
        self.play(s.restore)

    def comment_on_slope(self, graph, origin):
        delta_t = 1
        curr_time = 0
        ghost_line = Line(
            origin, 
            self.coords_to_point(delta_t, self.y_max)
        )
        rect = Rectangle().replace(ghost_line, stretch = True)
        rect.set_stroke(width = 0)
        rect.set_fill(TIME_COLOR, opacity = 0.3)

        change_lines = self.get_change_lines(curr_time, delta_t)
        self.play(FadeIn(rect))
        self.wait()
        self.play(Write(change_lines))
        self.wait()
        for x in range(1, 10):
            curr_time = x
            new_change_lines = self.get_change_lines(curr_time, delta_t)
            self.play(
                rect.move_to, self.coords_to_point(curr_time, 0), DOWN+LEFT,
                Transform(change_lines, new_change_lines)
            )
            if curr_time == 5:
                text = change_lines[-1].get_text(
                    "$\\frac{\\text{meters}}{\\text{second}}$"
                )
                self.play(Write(text))
                self.wait()
                self.play(FadeOut(text))
            else:
                self.wait()
        self.play(*list(map(FadeOut, [rect, change_lines])))
        self.rect = rect

    def get_change_lines(self, curr_time, delta_t = 1):
        p1 = self.input_to_graph_point(
            curr_time, self.s_graph
        )
        p2 = self.input_to_graph_point(
            curr_time+delta_t, self.s_graph
        )
        interim_point = p2[0]*RIGHT + p1[1]*UP
        delta_t_line = Line(p1, interim_point, color = TIME_COLOR)
        delta_s_line = Line(interim_point, p2, color = DISTANCE_COLOR)
        brace = Brace(delta_s_line, RIGHT, buff = SMALL_BUFF)
        return VGroup(delta_t_line, delta_s_line, brace)

    def show_velocity_graph(self):
        velocity_graph = self.get_derivative_graph(self.s_graph)

        self.play(ShowCreation(velocity_graph))
        def get_velocity_label(v_graph):
            result = self.get_graph_label(
                v_graph,
                label = "v(t)",
                direction = UP+RIGHT,
                x_val = 5,
                buff = SMALL_BUFF,
            )
            self.remove(result)
            return result
        label = get_velocity_label(velocity_graph)
        self.play(Write(label))
        self.wait()
        self.rect.move_to(self.coords_to_point(0, 0), DOWN+LEFT)
        self.play(FadeIn(self.rect))
        self.wait()
        for time, show_slope in (4.5, True), (9, False):
            self.play(
                self.rect.move_to, self.coords_to_point(time, 0), DOWN+LEFT
            )
            if show_slope:
                change_lines = self.get_change_lines(time)
                self.play(FadeIn(change_lines))
                self.wait()
                self.play(FadeOut(change_lines))
            else:
                self.wait()
        self.play(FadeOut(self.rect))

        #Change distance and velocity graphs
        self.s_graph.save_state()
        velocity_graph.save_state()
        label.save_state()
        def shallow_slope(t):
            return 100*smooth(t/10., inflection = 4)
        def steep_slope(t):
            return 100*smooth(t/10., inflection = 25)
        def double_smooth_graph_function(t):
            if t < 5:
                return 50*smooth(t/5.)
            else:
                return 50*(1+smooth((t-5)/5.))
        graph_funcs = [
            shallow_slope,
            steep_slope,
            double_smooth_graph_function,
        ]
        for graph_func in graph_funcs:
            new_graph = self.get_graph(
                graph_func,
                color = DISTANCE_COLOR,
            )
            self.remove(new_graph)
            new_velocity_graph = self.get_derivative_graph(
                graph = new_graph,
            )
            new_velocity_label = get_velocity_label(new_velocity_graph)

            self.play(Transform(self.s_graph, new_graph))
            self.play(
                Transform(velocity_graph, new_velocity_graph),
                Transform(label, new_velocity_label),
            )
            self.wait(2)
        self.play(self.s_graph.restore)
        self.play(
            velocity_graph.restore,
            label.restore,
        )
        self.wait(2)

    def ask_critically_about_velocity(self):
        morty = Mortimer().flip()
        morty.to_corner(DOWN+LEFT)
        self.play(PiCreatureSays(morty,
            "Think critically about \\\\",
            "what velocity means."
        ))
        self.play(Blink(morty))
        self.wait()

class ShowSpeedometer(IntroduceCar):
    CONFIG = {
        "num_ticks" : 8,
        "tick_length" : 0.2,
        "needle_width" : 0.1,
        "needle_height" : 0.8,
        "should_transition_to_graph" : False,
        "show_distance" : False,
        "speedometer_title_text" : "Speedometer",
    }
    def setup(self):
        start_angle = -np.pi/6
        end_angle = 7*np.pi/6
        speedometer = Arc(
            start_angle = start_angle,
            angle = end_angle-start_angle
        )
        tick_angle_range = np.linspace(end_angle, start_angle, self.num_ticks)
        for index, angle in enumerate(tick_angle_range):
            vect = rotate_vector(RIGHT, angle)
            tick = Line((1-self.tick_length)*vect, vect)
            label = TexMobject(str(10*index))
            label.set_height(self.tick_length)
            label.shift((1+self.tick_length)*vect)
            speedometer.add(tick, label)

        needle = Polygon(
            LEFT, UP, RIGHT,
            stroke_width = 0,
            fill_opacity = 1,
            fill_color = YELLOW
        )
        needle.stretch_to_fit_width(self.needle_width)
        needle.stretch_to_fit_height(self.needle_height)
        needle.rotate(end_angle-np.pi/2)
        speedometer.add(needle)
        speedometer.needle = needle

        speedometer.center_offset = speedometer.get_center()

        speedometer_title = TextMobject(self.speedometer_title_text)
        speedometer_title.to_corner(UP+LEFT)
        speedometer.next_to(speedometer_title, DOWN)

        self.speedometer = speedometer
        self.speedometer_title = speedometer_title

    def introduce_added_mobjects(self):
        speedometer = self.speedometer
        speedometer_title = self.speedometer_title

        speedometer.save_state()
        speedometer.rotate(-np.pi/2, UP)
        speedometer.set_height(self.car.get_height()/4)
        speedometer.move_to(self.car)
        speedometer.shift((self.car.get_width()/4)*RIGHT)

        self.play(speedometer.restore, run_time = 2)
        self.play(Write(speedometer_title, run_time = 1))

    def get_added_movement_anims(self, **kwargs):
        needle = self.speedometer.needle
        center = self.speedometer.get_center() - self.speedometer.center_offset
        default_kwargs = {
            "about_point" : center,
            "radians" : -np.pi/2,
            "run_time" : 10,
            "rate_func" : there_and_back,
        }
        default_kwargs.update(kwargs)
        return [Rotating(needle, **default_kwargs)]

    # def construct(self):
    #     self.add(self.speedometer)
    #     self.play(*self.get_added_movement_anims())

class VelocityInAMomentMakesNoSense(Scene):
    def construct(self):
        randy = Randolph()
        randy.next_to(ORIGIN, DOWN+LEFT)
        words = TextMobject("Velocity in \\\\ a moment")
        words.next_to(randy, UP+RIGHT)
        randy.look_at(words)
        q_marks = TextMobject("???")
        q_marks.next_to(randy, UP)

        self.play(
            randy.change_mode, "confused",
            Write(words)
        )
        self.play(Blink(randy))
        self.play(Write(q_marks))
        self.play(Blink(randy))
        self.wait()

class SnapshotOfACar(Scene):
    def construct(self):
        car = Car()
        car.scale(1.5)
        car.move_to(3*LEFT+DOWN)
        flash_box = Rectangle(
            width = FRAME_WIDTH,
            height = FRAME_HEIGHT,
            stroke_width = 0,
            fill_color = WHITE,
            fill_opacity = 1,
        )
        speed_lines = VGroup(*[
            Line(point, point+0.5*LEFT)
            for point in [
                0.5*UP+0.25*RIGHT,
                ORIGIN, 
                0.5*DOWN+0.25*RIGHT
            ]
        ])
        question = TextMobject("""
            How fast is
            this car going?
        """)

        self.play(MoveCar(
            car, RIGHT+DOWN, 
            run_time = 2,
            rate_func = rush_into
        ))
        car.get_tires().set_color(GREY)
        speed_lines.next_to(car, LEFT)
        self.add(speed_lines)
        self.play(
            flash_box.set_fill, None, 0,
            rate_func = rush_from
        )
        question.next_to(car, UP, buff = LARGE_BUFF)
        self.play(Write(question, run_time = 2))
        self.wait(2)

class CompareTwoTimes(Scene):
    CONFIG = {
        "start_distance" : 30,
        "start_time" : 4,
        "end_distance" : 50,
        "end_time" : 5,
        "fade_at_the_end" : True,
    }
    def construct(self):
        self.introduce_states()
        self.show_equation()
        if self.fade_at_the_end:
            self.fade_all_but_one_moment()

    def introduce_states(self):
        state1 = self.get_car_state(self.start_distance, self.start_time)
        state2 = self.get_car_state(self.end_distance, self.end_time)

        state1.to_corner(UP+LEFT)
        state2.to_corner(DOWN+LEFT)

        dividers = VGroup(
            Line(FRAME_X_RADIUS*LEFT, RIGHT),
            Line(RIGHT+FRAME_Y_RADIUS*UP, RIGHT+FRAME_Y_RADIUS*DOWN),
        )
        dividers.set_color(GREY)

        self.add(dividers, state1)
        self.wait()
        copied_state = state1.copy()
        self.play(copied_state.move_to, state2)
        self.play(Transform(copied_state, state2))
        self.wait(2)
        self.keeper = state1

    def show_equation(self):
        velocity = TextMobject("Velocity")
        change_over_change = TexMobject(
            "\\frac{\\text{Change in distance}}{\\text{Change in time}}"
        )
        formula = TexMobject(
            "\\frac{(%s - %s) \\text{ meters}}{(%s - %s) \\text{ seconds}}"%(
                str(self.end_distance), str(self.start_distance),
                str(self.end_time), str(self.start_time),
            )
        )
        ed_len = len(str(self.end_distance))
        sd_len = len(str(self.start_distance))
        et_len = len(str(self.end_time))
        st_len = len(str(self.start_time))
        seconds_len = len("seconds")
        VGroup(
            VGroup(*formula[1:1+ed_len]),
            VGroup(*formula[2+ed_len:2+ed_len+sd_len])
        ).set_color(DISTANCE_COLOR)
        VGroup(
            VGroup(*formula[-2-seconds_len-et_len-st_len:-2-seconds_len-st_len]),
            VGroup(*formula[-1-seconds_len-st_len:-1-seconds_len]),
        ).set_color(TIME_COLOR)

        down_arrow1 = TexMobject("\\Downarrow")
        down_arrow2 = TexMobject("\\Downarrow")
        group = VGroup(
            velocity, down_arrow1, 
            change_over_change, down_arrow2,
            formula,
        )
        group.arrange(DOWN)
        group.to_corner(UP+RIGHT)

        self.play(FadeIn(
            group, lag_ratio = 0.5,
            run_time = 3
        ))
        self.wait(3)
        self.formula = formula

    def fade_all_but_one_moment(self):
        anims = [
            ApplyMethod(mob.fade, 0.5)
            for mob in self.get_mobjects()
        ]
        anims.append(Animation(self.keeper.copy()))
        self.play(*anims)
        self.wait()

    def get_car_state(self, distance, time):
        line = Line(3*LEFT, 3*RIGHT)
        dots = list(map(Dot, line.get_start_and_end()))
        line.add(*dots)
        car = Car()
        car.move_to(line.get_start())
        car.shift((distance/10)*RIGHT)
        front_line = car.get_front_line()

        brace = Brace(VGroup(dots[0], front_line), DOWN)
        distance_label = brace.get_text(
            str(distance), " meters"
        )
        distance_label.set_color_by_tex(str(distance), DISTANCE_COLOR)
        brace.add(distance_label)
        time_label = TextMobject(
            "Time:", str(time), "seconds"
        )
        time_label.set_color_by_tex(str(time), TIME_COLOR)
        time_label.next_to(
            VGroup(line, car), UP,
            aligned_edge = LEFT
        )

        return VGroup(line, car, front_line, brace, time_label)

class VelocityAtIndividualPointsVsPairs(GraphCarTrajectory):
    CONFIG = {
        "start_time" : 6.5,
        "end_time" : 3,
        "dt" : 1.0,
    }
    def construct(self):
        self.setup_axes(animate = False)
        distance_graph = self.graph_function(lambda t : 100*smooth(t/10.))
        distance_label = self.label_graph(
            distance_graph,
            label = "s(t)",
            proportion = 1,
            direction = RIGHT,
            buff = SMALL_BUFF
        )
        velocity_graph = self.get_derivative_graph()
        self.play(ShowCreation(velocity_graph))
        velocity_label = self.label_graph(
            velocity_graph, 
            label = "v(t)",
            proportion = self.start_time/10.0, 
            direction = UP,
            buff = MED_SMALL_BUFF
        )
        velocity_graph.add(velocity_label)

        self.show_individual_times_to_velocity(velocity_graph)
        self.play(velocity_graph.fade, 0.4)
        self.show_two_times_on_distance()
        self.show_confused_pi_creature()

    def show_individual_times_to_velocity(self, velocity_graph):
        start_time = self.start_time
        end_time = self.end_time
        line = self.get_vertical_line_to_graph(start_time, velocity_graph)
        def line_update(line, alpha):
            time = interpolate(start_time, end_time, alpha)
            line.put_start_and_end_on(
                self.coords_to_point(time, 0),
                self.input_to_graph_point(time, graph = velocity_graph)
            )

        self.play(ShowCreation(line))
        self.wait()
        self.play(UpdateFromAlphaFunc(
            line, line_update,
            run_time = 4,
            rate_func = there_and_back
        ))
        self.wait()
        velocity_graph.add(line)

    def show_two_times_on_distance(self):
        line1 = self.get_vertical_line_to_graph(self.start_time-self.dt/2.0)
        line2 = self.get_vertical_line_to_graph(self.start_time+self.dt/2.0)
        p1 = line1.get_end()
        p2 = line2.get_end()
        interim_point = p2[0]*RIGHT+p1[1]*UP
        dt_line = Line(p1, interim_point, color = TIME_COLOR)
        ds_line = Line(interim_point, p2, color = DISTANCE_COLOR)
        dt_brace = Brace(dt_line, DOWN, buff = SMALL_BUFF)
        ds_brace = Brace(ds_line, RIGHT, buff = SMALL_BUFF)
        dt_text = dt_brace.get_text("Change in time", buff = SMALL_BUFF)
        ds_text = ds_brace.get_text("Change in distance", buff = SMALL_BUFF)

        self.play(ShowCreation(VGroup(line1, line2)))
        for line, brace, text in (dt_line, dt_brace, dt_text), (ds_line, ds_brace, ds_text):
            brace.set_color(line.get_color())
            text.set_color(line.get_color())
            text.add_background_rectangle()
            self.play(
                ShowCreation(line),
                GrowFromCenter(brace),
                Write(text)
            )
            self.wait()

    def show_confused_pi_creature(self):
        randy = Randolph()
        randy.to_corner(DOWN+LEFT)
        randy.shift(2*RIGHT)

        self.play(randy.change_mode, "confused")
        self.play(Blink(randy))
        self.wait(2)
        self.play(Blink(randy))
        self.play(randy.change_mode, "erm")
        self.wait()
        self.play(Blink(randy))
        self.wait(2)

class FirstRealWorld(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("First, the real world.")
        self.change_student_modes(
            "happy", "hooray", "happy"
        )
        self.wait(3)

class SidestepParadox(Scene):
    def construct(self):
        car = Car()
        car.shift(DOWN)
        show_speedometer = ShowSpeedometer(skip_animations = True)
        speedometer = show_speedometer.speedometer
        speedometer.next_to(car, UP)

        title = TextMobject(
            "Instantaneous", "rate of change"
        )
        title.to_edge(UP)
        cross = TexMobject("\\times")
        cross.replace(title[0], stretch = True)
        cross.set_fill(RED, opacity = 0.8)

        new_words = TextMobject("over a small time")
        new_words.next_to(title[1], DOWN)
        new_words.set_color(TIME_COLOR)

        self.add(title, car)
        self.play(Write(speedometer))
        self.wait()
        self.play(Write(cross))
        self.wait()
        self.play(Write(new_words))
        self.wait()

class CompareTwoVerySimilarTimes(CompareTwoTimes):
    CONFIG = {
        "start_distance" : 20,
        "start_time" : 3,
        "end_distance" : 20.21,
        "end_time" : 3.01,
        "fade_at_the_end" : False,
    }
    def construct(self):
        CompareTwoTimes.construct(self)

        formula = self.formula
        ds_symbols, dt_symbols = [
            VGroup(*[
                mob
                for mob in formula
                if mob.get_color() == Color(color)
            ])
            for color in (DISTANCE_COLOR, TIME_COLOR)
        ]
        ds_brace = Brace(ds_symbols, UP)
        ds_text = ds_brace.get_text("$ds$", buff = SMALL_BUFF)
        ds_text.set_color(DISTANCE_COLOR)
        dt_brace = Brace(dt_symbols, DOWN)
        dt_text = dt_brace.get_text("$dt$", buff = SMALL_BUFF)
        dt_text.set_color(TIME_COLOR)

        self.play(
            GrowFromCenter(dt_brace),
            Write(dt_text)
        )
        formula.add(dt_brace, dt_text)
        self.wait(2)

        formula.generate_target()
        VGroup(
            ds_brace, ds_text, formula.target
        ).move_to(formula, UP).shift(0.5*UP)
        self.play(
            MoveToTarget(formula),
            GrowFromCenter(ds_brace),
            Write(ds_text)
        )
        self.wait(2)

class DsOverDtGraphically(GraphCarTrajectory, ZoomedScene):
    CONFIG = {
        "dt" : 0.1,
        "zoom_factor" : 4,#Before being shrunk by dt
        "start_time" : 3,
        "end_time" : 7,
    }
    def construct(self):
        self.setup_axes(animate = False)
        distance_graph = self.graph_function(
            lambda t : 100*smooth(t/10.),
            animate = False,
        )
        distance_label = self.label_graph(
            distance_graph,
            label = "s(t)",
            proportion = 0.9,
            direction = UP+LEFT,
            buff = SMALL_BUFF
        )
        input_point_line = self.get_vertical_line_to_graph(
            self.start_time,
            line_kwargs = {
                "dash_length" : 0.02,
                "stroke_width" : 4,
                "color" : WHITE,
            },
        )
        def get_ds_dt_group(time):
            point1 = self.input_to_graph_point(time)
            point2 = self.input_to_graph_point(time+self.dt)
            interim_point = point2[0]*RIGHT+point1[1]*UP
            dt_line = Line(point1, interim_point, color = TIME_COLOR)
            ds_line = Line(interim_point, point2, color = DISTANCE_COLOR)
            result = VGroup()
            for line, char, vect in (dt_line, "t", DOWN), (ds_line, "s", RIGHT):
                line.scale(1./self.dt)
                brace = Brace(line, vect)
                text = brace.get_text("$d%s$"%char)
                text.next_to(brace, vect)
                text.set_color(line.get_color())
                subgroup = VGroup(line, brace, text)
                subgroup.scale(self.dt)
                result.add(subgroup)
            return result
        def align_little_rectangle_on_ds_dt_group(rect):
            rect.move_to(ds_dt_group, DOWN+RIGHT)
            rect.shift(self.dt*(DOWN+RIGHT)/4)
            return rect
        ds_dt_group = get_ds_dt_group(self.start_time)

        #Initially zoom in
        self.play(ShowCreation(input_point_line))
        self.activate_zooming()
        self.play(*list(map(FadeIn, [self.big_rectangle, self.little_rectangle])))
        self.play(
            ApplyFunction(
                align_little_rectangle_on_ds_dt_group,
                self.little_rectangle
            )
        )
        self.little_rectangle.generate_target()
        self.little_rectangle.target.scale(self.zoom_factor*self.dt)
        align_little_rectangle_on_ds_dt_group(
            self.little_rectangle.target
        )
        self.play(
            MoveToTarget(self.little_rectangle),
            run_time = 3
        )
        for subgroup in ds_dt_group:
            line, brace, text= subgroup
            self.play(ShowCreation(line))
            self.play(
                GrowFromCenter(brace),
                Write(text)
            )
            self.wait()

        #Show as function
        frac = TexMobject("\\frac{ds}{dt}")
        VGroup(*frac[:2]).set_color(DISTANCE_COLOR)
        VGroup(*frac[-2:]).set_color(TIME_COLOR)
        frac.next_to(self.input_to_graph_point(5.25), DOWN+RIGHT)
        rise_over_run = TexMobject(
            "=\\frac{\\text{rise}}{\\text{run}}"
        )
        rise_over_run.next_to(frac, RIGHT)
        of_t = TexMobject("(t)")
        of_t.next_to(frac, RIGHT, buff = SMALL_BUFF)

        dt_choice = TexMobject("dt = 0.01")
        dt_choice.set_color(TIME_COLOR)
        dt_choice.next_to(of_t, UP, aligned_edge = LEFT, buff = LARGE_BUFF)


        full_formula = TexMobject(
            "=\\frac{s(t+dt) - s(t)}{dt}"
        )
        full_formula.next_to(of_t)
        s_t_plus_dt = VGroup(*full_formula[1:8])
        s_t = VGroup(*full_formula[9:13])
        numerator = VGroup(*full_formula[1:13])
        lower_dt =  VGroup(*full_formula[-2:])
        upper_dt = VGroup(*full_formula[5:7])
        equals = full_formula[0]
        frac_line = full_formula[-3]
        s_t_plus_dt.set_color(DISTANCE_COLOR)
        s_t.set_color(DISTANCE_COLOR)
        lower_dt.set_color(TIME_COLOR)
        upper_dt.set_color(TIME_COLOR)

        velocity_graph = self.get_derivative_graph()
        t_tick_marks = VGroup(*[
            Line(
                UP, DOWN,
                color = TIME_COLOR,
                stroke_width = 3,
            ).scale(0.1).move_to(self.coords_to_point(t, 0))
            for t in np.linspace(0, 10, 75)
        ])

        v_line_at_t, v_line_at_t_plus_dt = [
            self.get_vertical_line_to_graph(
                time,
                line_class = Line,
                line_kwargs = {"color" : MAROON_B}
            )
            for time in (self.end_time, self.end_time + self.dt)
        ]


        self.play(Write(frac))
        self.play(Write(rise_over_run))
        self.wait()
        def input_point_line_update(line, alpha):
            time = interpolate(self.start_time, self.end_time, alpha)
            line.put_start_and_end_on(
                self.coords_to_point(time, 0),
                self.input_to_graph_point(time),
            )
        def ds_dt_group_update(group, alpha):
            time = interpolate(self.start_time, self.end_time, alpha)
            new_group = get_ds_dt_group(time)
            Transform(group, new_group).update(1)
        self.play(
            UpdateFromAlphaFunc(input_point_line, input_point_line_update),
            UpdateFromAlphaFunc(ds_dt_group, ds_dt_group_update),
            UpdateFromFunc(self.little_rectangle, align_little_rectangle_on_ds_dt_group),
            run_time = 6,
        )
        self.play(FadeOut(input_point_line))
        self.wait()
        self.play(FadeOut(rise_over_run))
        self.play(Write(of_t))
        self.wait(2)
        self.play(ShowCreation(velocity_graph))
        velocity_label = self.label_graph(
            velocity_graph, 
            label = "v(t)",
            proportion = 0.6,
            direction = DOWN+LEFT,
            buff = SMALL_BUFF
        )
        self.wait(2)
        self.play(Write(dt_choice))
        self.wait()
        for anim_class in FadeIn, FadeOut:
            self.play(anim_class(
                t_tick_marks, lag_ratio = 0.5,
                run_time = 2
            ))
        self.play(
            Write(equals),
            Write(numerator)
        )
        self.wait()

        self.play(ShowCreation(v_line_at_t))
        self.wait()
        self.play(ShowCreation(v_line_at_t_plus_dt))
        self.wait()
        self.play(*list(map(FadeOut, [v_line_at_t, v_line_at_t_plus_dt])))
        self.play(
            Write(frac_line),
            Write(lower_dt)
        )
        self.wait(2)

        #Show different curves
        self.disactivate_zooming()
        self.remove(ds_dt_group)

        self.graph.save_state()
        velocity_graph.save_state()
        velocity_label.save_state()
        def steep_slope(t):
            return 100*smooth(t/10., inflection = 25)
        def sin_wiggle(t):
            return (10/(2*np.pi/10.))*(np.sin(2*np.pi*t/10.) + 2*np.pi*t/10.)
        def double_smooth_graph_function(t):
            if t < 5:
                return 50*smooth(t/5.)
            else:
                return 50*(1+smooth((t-5)/5.))
        graph_funcs = [
            steep_slope,
            sin_wiggle,            
            double_smooth_graph_function,
        ]
        for graph_func in graph_funcs:
            new_graph = self.graph_function(
                graph_func,
                color = DISTANCE_COLOR,
                is_main_graph = False
            )
            self.remove(new_graph)
            new_velocity_graph = self.get_derivative_graph(
                graph = new_graph,
            )

            self.play(Transform(self.graph, new_graph))
            self.play(Transform(velocity_graph, new_velocity_graph))
            self.wait(2)
        self.play(self.graph.restore)
        self.play(
            velocity_graph.restore,
            velocity_label.restore,
        )

        #Pause and reflect
        randy = Randolph()
        randy.to_corner(DOWN+LEFT).shift(2*RIGHT)
        randy.look_at(frac_line)

        self.play(FadeIn(randy))
        self.play(randy.change_mode, "pondering")
        self.wait()
        self.play(Blink(randy))
        self.play(randy.change_mode, "thinking")
        self.wait()
        self.play(Blink(randy))
        self.wait()

class DefineTrueDerivative(Scene):
    def construct(self):
        title = TextMobject("The true derivative")
        title.to_edge(UP)

        lhs = TexMobject("\\frac{ds}{dt}(t) = ")
        VGroup(*lhs[:2]).set_color(DISTANCE_COLOR)
        VGroup(*lhs[3:5]).set_color(TIME_COLOR)
        lhs.shift(3*LEFT+UP)

        dt_rhs = self.get_fraction("dt")
        numerical_rhs_list = [
            self.get_fraction("0.%s1"%("0"*x))
            for x in range(7)
        ]
        for rhs in [dt_rhs] + numerical_rhs_list:
            rhs.next_to(lhs, RIGHT)

        brace, dt_to_zero = self.get_brace_and_text(dt_rhs)

        self.add(lhs, dt_rhs)
        self.play(Write(title))
        self.wait()
        dt_rhs.save_state()
        for num_rhs in numerical_rhs_list:
            self.play(Transform(dt_rhs, num_rhs))
        self.wait()
        self.play(dt_rhs.restore)
        self.play(
            GrowFromCenter(brace),
            Write(dt_to_zero)
        )
        self.wait()

    def get_fraction(self, dt_string):
        tex_mob = TexMobject(
            "\\frac{s(t + %s) - s(t)}{%s}"%(dt_string, dt_string)
        )
        part_lengths = [
            0,
            len("s(t+"),
            1,#1 and -1 below are purely for transformation quirks
            len(dt_string)-1,
            len(")-s(t)_"),#Underscore represents frac_line
            1,
            len(dt_string)-1,
        ]
        pl_cumsum = np.cumsum(part_lengths)
        result = VGroup(*[
            VGroup(*tex_mob[i1:i2])
            for i1, i2 in zip(pl_cumsum, pl_cumsum[1:])
        ])
        VGroup(*result[1:3]+result[4:6]).set_color(TIME_COLOR)
        return result

    def get_brace_and_text(self, deriv_frac):
        brace = Brace(VGroup(deriv_frac), DOWN)
        dt_to_zero = brace.get_text("$dt \\to 0$")
        VGroup(*dt_to_zero[:2]).set_color(TIME_COLOR)
        return brace, dt_to_zero

class SecantLineToTangentLine(GraphCarTrajectory, DefineTrueDerivative):
    CONFIG = {
        "start_time" : 6,
        "end_time" : 2,
        "alt_end_time" : 10,
        "start_dt" : 2,
        "end_dt" : 0.01,
        "secant_line_length" : 10,

    }
    def construct(self):
        self.setup_axes(animate = False)
        self.remove(self.y_axis_label_mob, self.x_axis_label_mob)
        self.add_derivative_definition(self.y_axis_label_mob)
        self.add_graph()
        self.draw_axes()
        self.show_tangent_line()
        self.best_constant_approximation_around_a_point()

    def get_ds_dt_group(self, dt, animate = False):
        points = [
            self.input_to_graph_point(time, self.graph)
            for time in (self.curr_time, self.curr_time+dt)
        ]
        dots = list(map(Dot, points))
        for dot in dots:
            dot.scale_in_place(0.5)
        secant_line = Line(*points)
        secant_line.set_color(VELOCITY_COLOR)
        secant_line.scale_in_place(
            self.secant_line_length/secant_line.get_length()
        )

        interim_point = points[1][0]*RIGHT + points[0][1]*UP
        dt_line = Line(points[0], interim_point, color = TIME_COLOR)
        ds_line = Line(interim_point, points[1], color = DISTANCE_COLOR)
        dt = TexMobject("dt")
        dt.set_color(TIME_COLOR)
        if dt.get_width() > dt_line.get_width():
            dt.scale(
                dt_line.get_width()/dt.get_width(),
                about_point = dt.get_top()
            )
        dt.next_to(dt_line, DOWN, buff = SMALL_BUFF)
        ds = TexMobject("ds")
        ds.set_color(DISTANCE_COLOR)
        if ds.get_height() > ds_line.get_height():
            ds.scale(
                ds_line.get_height()/ds.get_height(),
                about_point = ds.get_left()
            )
        ds.next_to(ds_line, RIGHT, buff = SMALL_BUFF)

        group = VGroup(
            secant_line, 
            ds_line, dt_line,
            ds, dt,
            *dots
        )
        if animate:
            self.play(
                ShowCreation(dt_line),
                Write(dt),
                ShowCreation(dots[0]),                
            )
            self.play(
                ShowCreation(ds_line),
                Write(ds),
                ShowCreation(dots[1]),                
            )
            self.play(
                ShowCreation(secant_line),
                Animation(VGroup(*dots))
            )
        return group

    def add_graph(self):
        def double_smooth_graph_function(t):
            if t < 5:
                return 50*smooth(t/5.)
            else:
                return 50*(1+smooth((t-5)/5.))
        self.graph = self.get_graph(double_smooth_graph_function)
        self.graph_label = self.get_graph_label(
            self.graph, "s(t)", 
            x_val = self.x_max, 
            direction = DOWN+RIGHT, 
            buff = SMALL_BUFF,
        )

    def add_derivative_definition(self, target_upper_left):
        deriv_frac = self.get_fraction("dt")
        lhs = TexMobject("\\frac{ds}{dt}(t)=")
        VGroup(*lhs[:2]).set_color(DISTANCE_COLOR)
        VGroup(*lhs[3:5]).set_color(TIME_COLOR)
        lhs.next_to(deriv_frac, LEFT)
        brace, text = self.get_brace_and_text(deriv_frac)
        deriv_def = VGroup(lhs, deriv_frac, brace, text)
        deriv_word = TextMobject("Derivative")        
        deriv_word.next_to(deriv_def, UP, buff = MED_LARGE_BUFF)
        deriv_def.add(deriv_word)
        rect = Rectangle(color = WHITE)
        rect.replace(deriv_def, stretch = True)
        rect.scale_in_place(1.2)
        deriv_def.add(rect)
        deriv_def.scale(0.7)
        deriv_def.move_to(target_upper_left, UP+LEFT)
        self.add(deriv_def)
        return deriv_def

    def draw_axes(self):
        self.x_axis.remove(self.x_axis_label_mob)
        self.y_axis.remove(self.y_axis_label_mob)
        self.play(Write(
            VGroup(
                self.x_axis, self.y_axis,
                self.graph, self.graph_label
            ),
            run_time = 4
        ))
        self.wait()

    def show_tangent_line(self):
        self.curr_time = self.start_time

        ds_dt_group = self.get_ds_dt_group(2, animate = True)
        self.wait()
        def update_ds_dt_group(ds_dt_group, alpha):
            new_dt = interpolate(self.start_dt, self.end_dt, alpha)
            new_group = self.get_ds_dt_group(new_dt)
            Transform(ds_dt_group, new_group).update(1)
        self.play(
            UpdateFromAlphaFunc(ds_dt_group, update_ds_dt_group),
            run_time = 15
        )
        self.wait()
        def update_as_tangent_line(ds_dt_group, alpha):
            self.curr_time = interpolate(self.start_time, self.end_time, alpha)
            new_group = self.get_ds_dt_group(self.end_dt)
            Transform(ds_dt_group, new_group).update(1)
        self.play(
            UpdateFromAlphaFunc(ds_dt_group, update_as_tangent_line),
            run_time = 8,
            rate_func = there_and_back
        )
        self.wait()
        what_dt_is_not_text = self.what_this_is_not_saying()
        self.wait()
        self.play(
            UpdateFromAlphaFunc(ds_dt_group, update_ds_dt_group),
            run_time = 8,
            rate_func = lambda t : 1-there_and_back(t)
        )
        self.wait()
        self.play(FadeOut(what_dt_is_not_text))

        v_line = self.get_vertical_line_to_graph(
            self.curr_time,
            self.graph,
            line_class = Line,
            line_kwargs = {
                "color" : MAROON_B,
                "stroke_width" : 3
            }
        )
        def v_line_update(v_line):
            v_line.put_start_and_end_on(
                self.coords_to_point(self.curr_time, 0),
                self.input_to_graph_point(self.curr_time, self.graph),
            )
            return v_line
        self.play(ShowCreation(v_line))
        self.wait()

        original_end_time = self.end_time
        for end_time in self.alt_end_time, original_end_time, self.start_time:
            self.end_time = end_time
            self.play(
                UpdateFromAlphaFunc(ds_dt_group, update_as_tangent_line),
                UpdateFromFunc(v_line, v_line_update),
                run_time = abs(self.curr_time-self.end_time),
            )
            self.start_time = end_time
        self.play(FadeOut(v_line))

    def what_this_is_not_saying(self):
        phrases = [
            TextMobject(
                "$dt$", "is", "not", s
            )
            for s in ("``infinitely small''", "0")
        ]
        for phrase in phrases:
            phrase[0].set_color(TIME_COLOR)
            phrase[2].set_color(RED)
        phrases[0].shift(DOWN+2*RIGHT)
        phrases[1].next_to(phrases[0], DOWN, aligned_edge = LEFT)

        for phrase in phrases:
            self.play(Write(phrase))
        return VGroup(*phrases)

    def best_constant_approximation_around_a_point(self):
        words = TextMobject("""
            Best constant 
            approximation
            around a point
        """)
        words.next_to(self.x_axis, UP, aligned_edge = RIGHT)
        circle = Circle(
            radius = 0.25,
            color = WHITE
        ).shift(self.input_to_graph_point(self.curr_time))

        self.play(Write(words))
        self.play(ShowCreation(circle))        
        self.wait()

class UseOfDImpliesApproaching(TeacherStudentsScene):
    def construct(self):
        statement = TextMobject("""
            Using ``$d$''
            announces that
            $dt \\to 0$
        """)
        VGroup(*statement[-4:-2]).set_color(TIME_COLOR)
        self.teacher_says(statement)
        self.change_student_modes(*["pondering"]*3)
        self.wait(4)

class LeadIntoASpecificExample(TeacherStudentsScene, SecantLineToTangentLine):
    def setup(self):
        TeacherStudentsScene.setup(self)

    def construct(self):
        dot = Dot() #Just to coordinate derivative definition
        dot.to_corner(UP+LEFT, buff = SMALL_BUFF)
        deriv_def = self.add_derivative_definition(dot)
        self.remove(deriv_def)

        self.teacher_says("An example \\\\ should help.")
        self.wait()
        self.play(
            Write(deriv_def),
            *it.chain(*[
                [pi.change_mode, "thinking", pi.look_at, dot]
                for pi in self.get_students()
            ])
        )
        self.random_blink(3)
        # self.teacher_says(
        #     """
        #     The idea of 
        #     ``approaching''
        #     actually makes 
        #     things easier
        #     """,
        #     height = 3,
        #     target_mode = "hooray"
        # )
        # self.wait(2)

class TCubedExample(SecantLineToTangentLine):
    CONFIG = {
        "y_axis_label" : "Distance",
        "y_min" : 0,
        "y_max" : 16,
        "y_tick_frequency" : 1,
        "y_labeled_nums" : list(range(0, 17, 2)),
        "x_min" : 0,
        "x_max" : 4,
        "x_labeled_nums" : list(range(1, 5)),
        "graph_origin" : 2.5*DOWN + 6*LEFT,
        "start_time" : 2,
        "end_time" : 0.5,
        "start_dt" : 0.25,
        "end_dt" : 0.001,
        "secant_line_length" : 0.01,
    }
    def construct(self):
        self.draw_graph()
        self.show_vertical_lines()
        self.bear_with_me()
        self.add_ds_dt_group()
        self.brace_for_details()
        self.show_expansion()
        self.react_to_simplicity()

    def draw_graph(self):
        self.setup_axes(animate = False)
        self.x_axis_label_mob.shift(0.5*DOWN)
        # self.y_axis_label_mob.next_to(self.y_axis, UP)
        graph = self.graph_function(lambda t : t**3, animate = True)
        self.label_graph(
            graph,
            label = "s(t) = t^3",
            proportion = 0.62,
            direction = LEFT,
            buff = SMALL_BUFF
        )
        self.wait()

    def show_vertical_lines(self):
        for t in 1, 2:
            v_line = self.get_vertical_line_to_graph(
                t, line_kwargs = {"color" : WHITE}
            )
            brace = Brace(v_line, RIGHT)
            text = TexMobject("%d^3 = %d"%(t, t**3))
            text.next_to(brace, RIGHT)
            text.shift(0.2*UP)
            group = VGroup(v_line, brace, text)
            if t == 1:
                self.play(ShowCreation(v_line))
                self.play(
                    GrowFromCenter(brace),
                    Write(text)
                )
                last_group = group
            else:
                self.play(Transform(last_group, group))
            self.wait()
        self.play(FadeOut(last_group))

    def bear_with_me(self):
        morty = Mortimer()
        morty.to_corner(DOWN+RIGHT)

        self.play(FadeIn(morty))
        self.play(PiCreatureSays(
            morty, "Bear with \\\\ me here",
            target_mode = "sassy"
        ))
        self.play(Blink(morty))
        self.wait()
        self.play(*list(map(
            FadeOut, 
            [morty, morty.bubble, morty.bubble.content]
        )))

    def add_ds_dt_group(self):
        self.curr_time = self.start_time
        self.curr_dt = self.start_dt
        ds_dt_group = self.get_ds_dt_group(dt = self.start_dt)
        v_lines = self.get_vertical_lines()

        lhs = TexMobject("\\frac{ds}{dt}(2) = ")
        lhs.next_to(ds_dt_group, UP+RIGHT, buff = MED_LARGE_BUFF)
        ds = VGroup(*lhs[:2])
        dt = VGroup(*lhs[3:5])
        ds.set_color(DISTANCE_COLOR)
        dt.set_color(TIME_COLOR)
        ds.target, dt.target = ds_dt_group[3:5]
        for mob in ds, dt:
            mob.save_state()
            mob.move_to(mob.target)

        nonzero_size = TextMobject("Nonzero size...for now")
        nonzero_size.set_color(TIME_COLOR)
        nonzero_size.next_to(dt, DOWN+2*RIGHT, buff = LARGE_BUFF)
        arrow = Arrow(nonzero_size, dt)

        rhs = TexMobject(
            "\\frac{s(2+dt) - s(2)}{dt}"
        )
        rhs.next_to(lhs[-1])
        VGroup(*rhs[4:6]).set_color(TIME_COLOR)
        VGroup(*rhs[-2:]).set_color(TIME_COLOR)
        numerator = VGroup(*rhs[:-3])
        non_numerator = VGroup(*rhs[-3:])
        numerator_non_minus = VGroup(*numerator)
        numerator_non_minus.remove(rhs[7])
        s_pair = rhs[0], rhs[8]
        lp_pair = rhs[6], rhs[11]
        for s, lp in zip(s_pair, lp_pair):
            s.target = TexMobject("3").scale(0.7)
            s.target.move_to(lp.get_corner(UP+RIGHT), LEFT)



        self.play(Write(ds_dt_group, run_time = 2))
        self.play(
            FadeIn(lhs),
            *[mob.restore for mob in (ds, dt)]
        )
        self.play(ShowCreation(v_lines[0]))
        self.wait()
        self.play(
            ShowCreation(arrow),
            Write(nonzero_size),
        )
        self.wait(2)
        self.play(*list(map(FadeOut, [arrow, nonzero_size])))
        self.play(Write(numerator))
        self.play(ShowCreation(v_lines[1]))
        self.wait()
        self.play(
            v_lines[0].set_color, YELLOW,
            rate_func = there_and_back
        )
        self.wait()
        self.play(Write(non_numerator))
        self.wait(2)
        self.play(
            *list(map(MoveToTarget, s_pair)),
            **{
                "path_arc" : -np.pi/2
            }
        )
        self.play(numerator_non_minus.shift, 0.2*LEFT)
        self.wait()

        self.vertical_lines = v_lines
        self.ds_dt_group = ds_dt_group
        self.lhs = lhs
        self.rhs = rhs

    def get_vertical_lines(self):
        return VGroup(*[
            self.get_vertical_line_to_graph(
                time,
                line_class = DashedLine,
                line_kwargs = {
                    "color" : WHITE,
                    "dash_length" : 0.05,
                }
            )
            for time in (self.start_time, self.start_time+self.start_dt)
        ])

    def brace_for_details(self):
        morty = Mortimer()
        morty.next_to(self.rhs, DOWN, buff = LARGE_BUFF)

        self.play(FadeIn(morty))
        self.play(
            morty.change_mode, "hooray",
            morty.look_at, self.rhs
        )
        self.play(Blink(morty))
        self.wait()
        self.play(
            morty.change_mode, "sassy",
            morty.look, OUT
        )
        self.play(Blink(morty))
        self.play(morty.change_mode, "pondering")
        self.wait()
        self.play(FadeOut(morty))

    def show_expansion(self):
        expression = TexMobject("""
            \\frac{
                2^3 + 
                3 (2)^2 dt
                + 3 (2)(dt)^2 + 
                (dt)^3
                - 2^3
            }{dt}
        """)
        expression.set_width(
            VGroup(self.lhs, self.rhs).get_width()
        )
        expression.next_to(
            self.lhs, DOWN, 
            aligned_edge = LEFT,
            buff = LARGE_BUFF
        )
        term_lens = [
            len("23+"),
            len("3(2)2dt"),
            len("+3(2)(dt)2+"),
            len("(dt)3"),
            len("-23"),
            len("_"),#frac bar
            len("dt"),
        ]
        terms = [
            VGroup(*expression[i1:i2])
            for i1, i2 in zip(
                [0]+list(np.cumsum(term_lens)),
                np.cumsum(term_lens)
            )
        ]

        dts = [
            VGroup(*terms[1][-2:]),
            VGroup(*terms[2][6:8]),
            VGroup(*terms[3][1:3]),
            terms[-1]
        ]
        VGroup(*dts).set_color(TIME_COLOR)

        two_cubed_terms = terms[0], terms[4]

        for term in terms:
            self.play(FadeIn(term))
            self.wait()

        #Cancel out two_cubed terms
        self.play(*it.chain(*[
            [
                tc.scale, 1.3, tc.get_corner(vect),
                tc.set_color, RED
            ]
            for tc, vect in zip(
                two_cubed_terms, 
                [DOWN+RIGHT, DOWN+LEFT]
            )
        ]))
        self.play(*list(map(FadeOut, two_cubed_terms)))
        numerator = VGroup(*terms[1:4])
        self.play(
            numerator.scale, 1.4, numerator.get_bottom(),
            terms[-1].scale, 1.4, terms[-1].get_top()
        )
        self.wait(2)

        #Cancel out dt
        #This is all way too hacky...
        faders = VGroup(
            terms[-1],            
            VGroup(*terms[1][-2:]), #"3(2)^2 dt"
            terms[2][-2], # "+3(2)(dt)2+"
            terms[3][-1], # "(dt)3"
        )
        new_exp = TexMobject("2").replace(faders[-1], dim_to_match = 1)
        self.play(
            faders.set_color, BLACK,
            FadeIn(new_exp),
            run_time = 2,
        )
        self.wait()
        terms[3].add(new_exp)
        shift_val = 0.4*DOWN
        self.play(
            FadeOut(terms[-2]),#frac_line
            terms[1].shift, shift_val + 0.45*RIGHT,
            terms[2].shift, shift_val,
            terms[3].shift, shift_val,
        )

        #Isolate dominant term
        arrow = Arrow(
            self.lhs[4].get_bottom(), terms[1][2].get_top(),
            color = WHITE,
            buff = MED_SMALL_BUFF
        )
        brace = Brace(VGroup(terms[2][0], terms[3][-1]), DOWN)
        brace_text = brace.get_text("Contains $dt$")
        VGroup(*brace_text[-2:]).set_color(TIME_COLOR)

        self.play(ShowCreation(arrow))
        self.wait()
        self.play(
            GrowFromCenter(brace), 
            Write(brace_text)
        )
        self.wait(2)

        #Shink dt
        faders = VGroup(*terms[2:4] + [brace, brace_text])        
        def ds_dt_group_update(group, alpha):
            new_dt = interpolate(self.start_dt, self.end_dt, alpha)
            new_group = self.get_ds_dt_group(new_dt)
            Transform(group, new_group).update(1)
        self.play(FadeOut(self.vertical_lines))
        self.secant_line_length = 10
        self.play(Transform(
            self.ds_dt_group,
            self.get_ds_dt_group(self.start_dt)
        ))
        self.play(
            UpdateFromAlphaFunc(self.ds_dt_group, ds_dt_group_update),
            faders.fade, 0.7,
            run_time = 5
        )
        self.wait(2)

        #Show as derivative
        deriv_term = VGroup(*terms[1][:5])
        deriv_term.generate_target()
        lhs_copy = self.lhs.copy()
        lhs_copy.generate_target()
        lhs_copy.target.shift(3*DOWN)
        #hack a little, hack a lot
        deriv_term.target.scale(1.1)
        deriv_term.target.next_to(lhs_copy.target)
        deriv_term.target.shift(0.07*DOWN)

        self.play(
            FadeOut(arrow),
            FadeOut(faders),            
            MoveToTarget(deriv_term),
            MoveToTarget(lhs_copy),
        )
        arrow = Arrow(
            self.rhs.get_bottom(), deriv_term.target.get_top(),
            buff = MED_SMALL_BUFF,
            color = WHITE
        )
        approach_text = TextMobject("As $dt \\to 0$")
        approach_text.next_to(arrow.get_center(), RIGHT)
        VGroup(*approach_text[2:4]).set_color(TIME_COLOR)
        self.play(
            ShowCreation(arrow),
            Write(approach_text)
        )
        self.wait(2)
        self.wait()

        #Ephasize slope
        v_line = self.vertical_lines[0]
        slope_text = TextMobject("Slope = $12$")
        slope_text.set_color(VELOCITY_COLOR)
        slope_text.next_to(v_line.get_end(), LEFT)
        self.play(Write(slope_text))
        self.play(
            self.ds_dt_group.rotate_in_place, np.pi/24,
            rate_func = wiggle
        )
        self.play(ShowCreation(v_line))
        self.wait()
        self.play(FadeOut(v_line))
        self.play(FadeOut(slope_text))

        #Generalize to more t
        twos = [
            self.lhs[6],
            self.rhs[2],
            self.rhs[10],
            lhs_copy[6],
            deriv_term[2]
        ]
        for two in twos:
            two.target = TexMobject("t")
            two.target.replace(two, dim_to_match = 1)
        self.play(*list(map(MoveToTarget, twos)))
        def update_as_tangent_line(group, alpha):
            self.curr_time = interpolate(self.start_time, self.end_time, alpha)
            new_group = self.get_ds_dt_group(self.end_dt)
            Transform(group, new_group).update(1)
        self.play(
            UpdateFromAlphaFunc(self.ds_dt_group, update_as_tangent_line),
            run_time = 5,
            rate_func = there_and_back
        )
        self.wait(2)

        self.lhs_copy = lhs_copy
        self.deriv_term = deriv_term
        self.approach_text = approach_text

    def react_to_simplicity(self):
        morty = Mortimer().flip().to_corner(DOWN+LEFT)

        self.play(FadeIn(morty))
        self.play(PiCreatureSays(
            morty, "That's \\\\ beautiful!",
            target_mode = "hooray"
        ))
        self.play(Blink(morty))
        self.play(
            morty.change_mode, 'happy',
            *list(map(FadeOut, [morty.bubble, morty.bubble.content]))
        )

        numerator = VGroup(*self.rhs[:12])
        denominator = VGroup(*self.rhs[-2:])
        for mob in numerator, denominator, self.approach_text, self.deriv_term:
            mob.generate_target()
            mob.target.scale_in_place(1.2)
            mob.target.set_color(MAROON_B)
            self.play(
                MoveToTarget(
                    mob, rate_func = there_and_back,
                    run_time = 1.5,
                ),
                morty.look_at, mob
            )
            self.wait()
        self.play(Blink(morty))
        self.wait()

class YouWouldntDoThisEveryTime(TeacherStudentsScene):
    def construct(self):
        self.change_student_modes(
            "pleading", "guilty", "hesitant",
            run_time = 0
        )
        self.teacher_says(
            "You wouldn't do this \\\\ every time"
        )
        self.change_student_modes(*["happy"]*3)
        self.wait(2)
        self.student_thinks(
            "$\\frac{d(t^3)}{dt} = 3t^2$",
        )
        self.wait(3)

        series = VideoSeries()
        series.set_width(FRAME_WIDTH-1)
        series.to_edge(UP)
        this_video = series[1]
        next_video = series[2]
        this_video.save_state()
        this_video.set_color(YELLOW)
        self.play(FadeIn(series, lag_ratio = 0.5))
        self.play(
            this_video.restore,
            next_video.set_color, YELLOW,
            next_video.shift, 0.5*DOWN
        )
        self.wait(2)

class ContrastConcreteDtWithLimit(Scene):
    def construct(self):
        v_line = Line(UP, DOWN).scale(FRAME_Y_RADIUS)
        self.add(v_line)

        l_title = TextMobject("""
            If $dt$ has a
            specific size.
        """)
        VGroup(*l_title[2:4]).set_color(TIME_COLOR)
        r_title = TexMobject("dt \\to 0")
        VGroup(*r_title[:2]).set_color(TIME_COLOR)
        for title, vect in (l_title, LEFT), (r_title, RIGHT):
            title.to_edge(UP)
            title.shift(FRAME_X_RADIUS*vect/2)
            self.add(title)

        l_formula = TexMobject("""
            \\frac{d(t^3)}{dt} = 
            \\frac{
                t^3+
                3t^2 \\, dt + 
                3t \\, (dt)^2 + 
                (dt)^3
                - t^3
            }{dt}
        """)
        VGroup(*it.chain(
            l_formula[6:8],
            l_formula[15:17],
            l_formula[21:23],
            l_formula[27:29],
            l_formula[35:37],
        )).set_color(TIME_COLOR)
        l_formula.set_width(FRAME_X_RADIUS-MED_LARGE_BUFF)
        l_formula.to_edge(LEFT)

        l_brace = Brace(l_formula, DOWN)
        l_text = l_brace.get_text("Messy")
        l_text.set_color(RED)

        r_formula = TexMobject(
            "\\frac{d(t^3)}{dt} = 3t^2"
        )
        VGroup(*r_formula[6:8]).set_color(TIME_COLOR)
        r_formula.shift(FRAME_X_RADIUS*RIGHT/2)
        r_brace = Brace(r_formula, DOWN)
        r_text = r_brace.get_text("Simple")
        r_text.set_color(GREEN)

        triplets = [
            (l_formula, l_brace, l_text),
            (r_formula, r_brace, r_text),
        ]
        for formula, brace, text in triplets:
            self.play(Write(formula, run_time = 1))
            self.play(
                GrowFromCenter(brace),
                Write(text)
            )
            self.wait(2)

class TimeForAnActualParadox(TeacherStudentsScene):
    def construct(self):
        words = TextMobject("``Instantaneous rate of change''")
        paradoxes = TextMobject("Paradoxes")
        arrow = Arrow(ORIGIN, DOWN, buff = 0)
        group = VGroup(words, arrow, paradoxes)
        group.arrange(DOWN)
        group.to_edge(UP)

        teacher = self.get_teacher()
        self.play(
            teacher.change_mode, "raise_right_hand",
            teacher.look_at, words,
            Write(words)
        )
        self.play(*list(map(Write, [arrow, paradoxes])))
        self.play(*it.chain(*[
            [pi.change_mode, mode, pi.look_at, words]
            for pi, mode in zip(
                self.get_students(),
                ["pondering", "happy", "hesitant"]
            )
        ]))
        self.wait(4)

class ParadoxAtTEquals0(TCubedExample):
    CONFIG = {
        "tangent_line_length" : 20,
    }
    def construct(self):
        self.draw_graph()
        self.ask_question()
        self.show_derivative_text()
        self.show_tangent_line()
        self.if_not_then_when()
        self.single_out_question()

    def draw_graph(self):
        self.setup_axes(animate = False)
        self.x_axis_label_mob.set_fill(opacity = 0)
        graph = self.graph_function(lambda t : t**3, animate = False)
        graph_x_max = 3.0
        graph.pointwise_become_partial(graph, 0, graph_x_max/self.x_max)

        origin = self.coords_to_point(0, 0)
        h_line = Line(LEFT, RIGHT, color = TIME_COLOR)
        v_line = Line(UP, DOWN, color = DISTANCE_COLOR)
        VGroup(h_line, v_line).set_stroke(width = 2)

        def h_line_update(h_line):
            point = graph.point_from_proportion(1)
            y_axis_point = origin[0]*RIGHT + point[1]*UP
            h_line.put_start_and_end_on(y_axis_point, point)
            return h_line

        def v_line_update(v_line):
            point = graph.point_from_proportion(1)
            x_axis_point =  point[0]*RIGHT + origin[1]*UP
            v_line.put_start_and_end_on(x_axis_point, point)
            return v_line

        car = Car()
        car.rotate(np.pi/2)
        car.move_to(origin)
        self.add(car)
        #Should be 0, 1, but for some reason I don't know
        #the car was lagging the graph.
        car_target_point = self.coords_to_point(0, 1.15)

        self.play(
            MoveCar(
                car, car_target_point,
                rate_func = lambda t : (t*graph_x_max)**3
            ),
            ShowCreation(graph, rate_func=linear),
            UpdateFromFunc(h_line, h_line_update),
            UpdateFromFunc(v_line, v_line_update),
            run_time = 5
        )
        self.play(*list(map(FadeOut, [h_line, v_line])))

        self.label_graph(
            graph,
            label = "s(t) = t^3",
            proportion = 0.8,
            direction = RIGHT,
            buff = SMALL_BUFF
        )
        self.wait()

        self.car = car

    def ask_question(self):
        question = TextMobject(
            "At time $t=0$,", 
            "is \\\\ the car moving?"
        )
        VGroup(*question[0][-4:-1]).set_color(RED)
        question.next_to(
            self.coords_to_point(0, 10),
            RIGHT
        )
        origin = self.coords_to_point(0, 0)
        arrow = Arrow(question.get_bottom(), origin)

        self.play(Write(question[0], run_time = 1))
        self.play(MoveCar(self.car, origin))
        self.wait()
        self.play(Write(question[1]))
        self.play(ShowCreation(arrow))
        self.wait(2)

        self.question = question

    def show_derivative_text(self):
        derivative = TexMobject(
            "\\frac{ds}{dt}(t) = 3t^2",
            "= 3(0)^2",
            "= 0",
            "\\frac{\\text{m}}{\\text{s}}",
        )
        VGroup(*derivative[0][:2]).set_color(DISTANCE_COLOR)
        VGroup(*derivative[0][3:5]).set_color(TIME_COLOR)
        derivative[1][3].set_color(RED)
        derivative[-1].scale_in_place(0.7)
        derivative.to_edge(RIGHT, buff = LARGE_BUFF)
        derivative.shift(2*UP)

        self.play(Write(derivative[0]))
        self.wait()
        self.play(FadeIn(derivative[1]))
        self.play(*list(map(FadeIn, derivative[2:])))
        self.wait(2)

        self.derivative = derivative

    def show_tangent_line(self):
        dot = Dot()
        line = Line(ORIGIN, RIGHT, color = VELOCITY_COLOR)
        line.scale(self.tangent_line_length)

        start_time = 2
        end_time = 0

        def get_time_and_point(alpha):
            time = interpolate(start_time, end_time, alpha)
            point = self.input_to_graph_point(time)
            return time, point

        def dot_update(dot, alpha):
            dot.move_to(get_time_and_point(alpha)[1])

        def line_update(line, alpha):
            time, point = get_time_and_point(alpha)
            line.rotate(
                self.angle_of_tangent(time)-line.get_angle()
            )
            line.move_to(point)

        dot_update(dot, 0)
        line_update(line, 0)
        self.play(
            ShowCreation(line),
            ShowCreation(dot)
        )
        self.play(
            UpdateFromAlphaFunc(line, line_update),
            UpdateFromAlphaFunc(dot, dot_update),            
            run_time = 4
        )
        self.wait(2)

        self.tangent_line = line

    def if_not_then_when(self):
        morty = Mortimer()
        morty.scale(0.7)
        morty.to_corner(DOWN+RIGHT)

        self.play(FadeIn(morty))
        self.play(PiCreatureSays(
            morty, "If not at $t=0$, when?",
            target_mode = "maybe"
        ))
        self.play(Blink(morty))
        self.play(MoveCar(
            self.car, self.coords_to_point(0, 1),
            rate_func = lambda t : (3*t)**3,
            run_time = 5
        ))
        self.play(
            morty.change_mode, "pondering",
            FadeOut(morty.bubble),
            FadeOut(morty.bubble.content),
        )
        self.play(MoveCar(self.car, self.coords_to_point(0, 0)))
        self.play(Blink(morty))
        self.wait(2)

        self.morty = morty

    def single_out_question(self):
        morty, question = self.morty, self.question

        #Shouldn't need this
        morty.bubble.content.set_fill(opacity = 0)
        morty.bubble.set_fill(opacity = 0)
        morty.bubble.set_stroke(width = 0)

        change_word = VGroup(*question[1][-7:-1])
        moment_word = question[0]

        brace = Brace(VGroup(*self.derivative[1:]))
        brace_text = brace.get_text("Best constant \\\\ approximation")

        self.remove(question, morty)
        pre_everything = Mobject(*self.get_mobjects())
        everything = Mobject(*pre_everything.family_members_with_points())
        everything.save_state()

        self.play(
            everything.fade, 0.8,
            question.center,
            morty.change_mode, "confused",
            morty.look_at, ORIGIN
        )
        self.play(Blink(morty))
        for word in change_word, moment_word:
            self.play(
                word.scale_in_place, 1.2,
                word.set_color, YELLOW,
                rate_func = there_and_back,
                run_time = 1.5
            )
        self.wait(2)
        self.play(
            everything.restore,
            FadeOut(question),
            morty.change_mode, "raise_right_hand",
            morty.look_at, self.derivative
        )
        self.play(
            GrowFromCenter(brace),
            FadeIn(brace_text)
        )
        self.wait()
        self.play(
            self.tangent_line.rotate_in_place, np.pi/24,
            rate_func = wiggle,
            run_time = 1
        )
        self.play(Blink(morty))
        self.wait()

class TinyMovement(ZoomedScene):
    CONFIG = {
        "distance" : 0.05,
        "distance_label" : "(0.1)^3 = 0.001",
        "time_label" : "0.1",
    }
    def construct(self):
        self.activate_zooming()
        self.show_initial_motion()
        self.show_ratios()

    def show_initial_motion(self):
        car = Car()
        car.move_to(ORIGIN)
        car_points = car.get_all_points()
        lowest_to_highest_indices = np.argsort(car_points[:,1])
        wheel_point = car_points[lowest_to_highest_indices[2]]
        target_wheel_point = wheel_point+self.distance*RIGHT

        dots = VGroup(*[
            Dot(point, radius = self.distance/10)
            for point in (wheel_point, target_wheel_point)
        ])
        brace = Brace(Line(ORIGIN, RIGHT))
        distance_label = TexMobject(self.distance_label)
        distance_label.next_to(brace, DOWN)
        distance_label.set_color(DISTANCE_COLOR)
        brace.add(distance_label)
        brace.scale(self.distance)
        brace.next_to(dots, DOWN, buff = self.distance/5)

        zoom_rect = self.little_rectangle
        zoom_rect.scale(2)
        zoom_rect.move_to(wheel_point)

        time_label = TextMobject("Time $t = $")
        time_label.next_to(car, UP, buff = LARGE_BUFF)
        start_time = TexMobject("0")
        end_time = TexMobject(self.time_label)
        for time in start_time, end_time:
            time.set_color(TIME_COLOR)
            time.next_to(time_label, RIGHT)

        self.add(car, time_label, start_time)
        self.play(
            zoom_rect.scale_in_place,
            10*self.distance / zoom_rect.get_width()
        )
        self.play(ShowCreation(dots[0]))
        self.play(Transform(start_time, end_time))
        self.play(MoveCar(car, self.distance*RIGHT))
        self.play(ShowCreation(dots[1]))
        self.play(Write(brace, run_time = 1))
        self.play(
            zoom_rect.scale, 0.5,
            zoom_rect.move_to, brace
        )
        self.wait()

    def show_ratios(self):
        ratios = [
            self.get_ratio(n)
            for n in range(1, 5)
        ]
        ratio = ratios[0]
        self.play(FadeIn(ratio))
        self.wait(2)
        for new_ratio in ratios[1:]:
            self.play(Transform(ratio, new_ratio))
            self.wait()

    def get_ratio(self, power = 1):
        dt = "0.%s1"%("0"*(power-1))
        ds_dt = "0.%s1"%("0"*(2*power-1))
        expression = TexMobject("""
            \\frac{(%s)^3 \\text{ meters}}{%s \\text{ seconds}}
            = %s \\frac{\\text{meters}}{\\text{second}}
        """%(dt, dt, ds_dt))
        expression.next_to(ORIGIN, DOWN, buff = LARGE_BUFF)
        lengths = [
            0,
            len("("),
            len(dt),
            len(")3meters_"),
            len(dt),
            len("seconds="),
            len(ds_dt),
            len("meters_second")
        ]
        result = VGroup(*[
            VGroup(*expression[i1:i2])
            for i1, i2 in zip(
                np.cumsum(lengths),
                np.cumsum(lengths)[1:],
            )
        ])
        result[1].set_color(DISTANCE_COLOR)
        result[3].set_color(TIME_COLOR)
        result[5].set_color(VELOCITY_COLOR)

        return result

class NextVideos(TeacherStudentsScene):
    def construct(self):
        series = VideoSeries()
        series.set_width(FRAME_WIDTH - 1)
        series.to_edge(UP)
        series[1].set_color(YELLOW)
        self.add(series)

        brace = Brace(VGroup(*series[2:6]))
        brace_text = brace.get_text("More derivative stuffs")


        self.play(
            GrowFromCenter(brace),
            self.get_teacher().change_mode, "raise_right_hand"
        )
        self.play(
            Write(brace_text),
            *it.chain(*[
                [pi.look_at, brace]
                for pi in self.get_students()
            ])
        )
        self.wait(2)
        self.change_student_modes(*["thinking"]*3)
        self.wait(3)

class Chapter2PatreonThanks(PatreonThanks):
    CONFIG = {
        "specific_patrons" : [
            "Meshal  Alshammari",
            "Ali Yahya",
            "CrypticSwarm    ",
            "Yu  Jun",
            "Shelby  Doolittle",
            "Dave    Nicponski",
            "Damion  Kistler",
            "Juan    Benet",
            "Othman  Alikhan",
            "Markus  Persson",
            "Dan Buchoff",
            "Derek   Dai",
            "Joseph  Cox",
            "Luc Ritchie",
            "Mark    Govea",
            "Guido   Gambardella",
            "Vecht",
            "Jonathan    Eppele",
            "Shimin Kuang",
            "Rish    Kundalia",
            "Achille Brighton",
            "Kirk    Werklund",
            "Ripta   Pasay",
            "Felipe  Diniz",
        ]
    }

class Promotion(PiCreatureScene):
    CONFIG = {
        "camera_class" : ThreeDCamera,
        "seconds_to_blink" : 5,
    }
    def construct(self):
        aops_logo = AoPSLogo()
        aops_logo.next_to(self.pi_creature, UP+LEFT)
        url = TextMobject(
            "AoPS.com/", "3blue1brown",
            arg_separator = ""
        )
        url.to_corner(UP+LEFT)
        url_rect = Rectangle(color = BLUE)
        url_rect.replace(
            url.get_part_by_tex("3blue1brown"),
            stretch = True
        )

        url_rect.stretch_in_place(1.1, dim = 1)

        rect = Rectangle(height = 9, width = 16)
        rect.set_height(4.5)
        rect.next_to(url, DOWN)
        rect.to_edge(LEFT)
        mathy = Mathematician()
        mathy.flip()
        mathy.to_corner(DOWN+RIGHT)
        morty = self.pi_creature
        morty.save_state()
        book_spot = mathy.get_corner(UP+LEFT) + UP+LEFT
        mathy.get_center = mathy.get_top

        self.play(
            self.pi_creature.change_mode, "raise_right_hand",
            *[
                DrawBorderThenFill(
                    submob,
                    run_time = 3,
                    rate_func = squish_rate_func(double_smooth, a, a+0.5)
                )
                for submob, a in zip(aops_logo, np.linspace(0, 0.5, len(aops_logo)))
            ]
        )
        self.play(Write(url))
        self.play(
            morty.change_mode, "plain",
            morty.flip,
            morty.scale, 0.7,
            morty.next_to, mathy, LEFT, LARGE_BUFF,
            morty.to_edge, DOWN,
            FadeIn(mathy),
        )
        self.play(
            PiCreatureSays(
                mathy, "",
                bubble_kwargs = {"width" : 5},
                look_at_arg = morty.eyes,
            ),
            aops_logo.shift, 1.5*UP + 0.5*RIGHT
        )
        self.change_mode("happy")
        self.wait(2)
        self.play(Blink(mathy))
        self.wait()
        self.play(
            RemovePiCreatureBubble(
                mathy, target_mode = "happy"
            ),
            aops_logo.to_corner, UP+RIGHT,
            aops_logo.shift, MED_SMALL_BUFF*DOWN,
        )
        self.play(
            mathy.look_at, morty.eyes,
            morty.look_at, mathy.eyes,
        )
        self.wait(2)
        self.play(
            Animation(VectorizedPoint(book_spot)),
            mathy.change, "raise_right_hand", book_spot,
            morty.change, "pondering",
        )
        self.wait(3)
        self.play(Blink(mathy))
        self.wait(7)
        self.play(
            ShowCreation(rect),
            morty.restore,
            morty.change, "happy", rect,
            FadeOut(mathy),
        )
        self.wait(10)
        self.play(ShowCreation(url_rect))
        self.play(
            FadeOut(url_rect),
            url.get_part_by_tex("3blue1brown").set_color, BLUE,
        )
        self.wait(3)

class Thumbnail(SecantLineToTangentLine):
    def construct(self):
        self.setup_axes(animate = False)
        self.add_graph()
        self.curr_time = 6
        ds_dt_group = self.get_ds_dt_group(1)
        self.add(ds_dt_group)
        self.remove(self.x_axis_label_mob)
        self.remove(self.y_axis_label_mob)
        VGroup(*self.get_mobjects()).fade(0.4)

        title = TextMobject("Derivative paradox")
        title.set_width(FRAME_WIDTH-1)
        title.to_edge(UP)
        title.add_background_rectangle()
        title.set_color_by_gradient(GREEN, YELLOW)

        randy = Randolph(mode = "confused")
        randy.scale(1.7)
        randy.to_corner(DOWN+LEFT)
        randy.shift(RIGHT)

        deriv = TexMobject("\\frac{ds}{dt}(t)")
        VGroup(*deriv[:2]).set_color(DISTANCE_COLOR)
        VGroup(*deriv[3:5]).set_color(TIME_COLOR)
        deriv.scale(3)
        # deriv.next_to(randy, RIGHT, buff = 2)
        deriv.to_edge(RIGHT, buff = LARGE_BUFF)
        randy.look_at(deriv)

        self.add(title, randy, deriv)






















