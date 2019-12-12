from manimlib.imports import *

class ShowExampleTest(ExternallyAnimatedScene):
    pass

class IntroducePutnam(Scene):
    CONFIG = {
        "dont_animate" : False,
    }
    def construct(self):
        title = TextMobject("Putnam Competition")
        title.to_edge(UP, buff = MED_SMALL_BUFF)
        title.set_color(BLUE)
        six_hours = TextMobject("6", "hours")
        three_hours = TextMobject("3", "hours")
        for mob in six_hours, three_hours:
            mob.next_to(title, DOWN, MED_LARGE_BUFF)
            # mob.set_color(BLUE)
        three_hours.shift(FRAME_X_RADIUS*LEFT/2)
        three_hours_copy = three_hours.copy()
        three_hours_copy.shift(FRAME_X_RADIUS*RIGHT)

        question_groups = VGroup(*[
            VGroup(*[
                TextMobject("%s%d)"%(c, i))
                for i in range(1, 7)
            ]).arrange(DOWN, buff = MED_LARGE_BUFF)
            for c in ("A", "B")
        ]).arrange(RIGHT, buff = FRAME_X_RADIUS - MED_SMALL_BUFF)
        question_groups.to_edge(LEFT)
        question_groups.to_edge(DOWN, MED_LARGE_BUFF)
        flat_questions = VGroup(*it.chain(*question_groups))

        rects = VGroup()
        for questions in question_groups:
            rect = SurroundingRectangle(questions, buff = MED_SMALL_BUFF)
            rect.set_stroke(WHITE, 2)
            rect.stretch_to_fit_width(FRAME_X_RADIUS - 1)
            rect.move_to(questions.get_left() + MED_SMALL_BUFF*LEFT, LEFT)
            rects.add(rect)

        out_of_tens = VGroup()
        for question in flat_questions:
            out_of_ten = TexMobject("/10")
            out_of_ten.set_color(GREEN)
            out_of_ten.move_to(question)
            dist = rects[0].get_width() - 1.2
            out_of_ten.shift(dist*RIGHT)
            out_of_tens.add(out_of_ten)

        out_of_120 = TexMobject("/120")
        out_of_120.next_to(title, RIGHT, LARGE_BUFF)
        out_of_120.set_color(GREEN)

        out_of_120.generate_target()
        out_of_120.target.to_edge(RIGHT, LARGE_BUFF)
        median = TexMobject("2")
        median.next_to(out_of_120.target, LEFT, SMALL_BUFF)
        median.set_color(RED)
        median.align_to(out_of_120[-1])
        median_words = TextMobject("Typical median $\\rightarrow$")
        median_words.next_to(median, LEFT)

        difficulty_strings = [
            "Pretty hard",
            "Hard",
            "Harder",
            "Very hard",
            "Ughhh",
            "Can I go home?"
        ]
        colors = color_gradient([YELLOW, RED], len(difficulty_strings))
        difficulties = VGroup()
        for i, s, color in zip(it.count(), difficulty_strings, colors):
            for question_group in question_groups:
                question = question_group[i]
                text = TextMobject("\\dots %s \\dots"%s)
                text.scale(0.7)
                text.next_to(question, RIGHT)
                text.set_color(color)
                difficulties.add(text)


        if self.dont_animate:        
            test = VGroup()
            test.rect = rects[0]
            test.questions = question_groups[0]
            test.out_of_tens = VGroup(*out_of_tens[:6])
            test.difficulties = VGroup(*difficulties[::2])
            test.digest_mobject_attrs()
            self.test = test
            return

        self.add(title)
        self.play(Write(six_hours))
        self.play(LaggedStartMap(
            GrowFromCenter, flat_questions,
            run_time = 3,
        ))
        self.play(
            ReplacementTransform(six_hours, three_hours),
            ReplacementTransform(six_hours.copy(), three_hours_copy),
            *list(map(ShowCreation, rects))
        )
        self.wait()
        self.play(LaggedStartMap(
            DrawBorderThenFill, out_of_tens,
            run_time = 3,
            stroke_color = YELLOW
        ))
        self.wait()
        self.play(ReplacementTransform(
            out_of_tens.copy(), VGroup(out_of_120),
            lag_ratio = 0.5,
            run_time = 2,
        ))
        self.wait()
        self.play(
            title.next_to, median_words.copy(), LEFT, LARGE_BUFF,
            MoveToTarget(out_of_120),
            Write(median_words)
        )
        self.play(Write(median))
        for difficulty in difficulties:
            self.play(FadeIn(difficulty))
        self.wait()

class NatureOf5sAnd6s(TeacherStudentsScene):
    CONFIG = {
        "test_scale_val" : 0.65
    }
    def construct(self):
        test = self.get_test()

        self.students.fade(1)
        self.play(
            test.scale, self.test_scale_val,
            test.to_corner, UP+LEFT,
            FadeIn(self.teacher),
            self.get_student_changes(
                *["horrified"]*3,
                look_at_arg = test
            )
        )
        self.wait()

        mover = VGroup(
            test.questions[-1].copy(),
            test.difficulties[-1].copy(),
        )
        mover.generate_target()
        mover.target.scale(1./self.test_scale_val)
        mover.target.next_to(
            self.teacher.get_corner(UP+LEFT), UP,
        )
        new_words = TextMobject("\\dots Potentially very elegant \\dots")
        new_words.set_color(GREEN)
        new_words.set_height(mover.target[1].get_height())
        new_words.next_to(mover.target[0], RIGHT, SMALL_BUFF)

        self.play(
            MoveToTarget(mover),
            self.teacher.change, "raise_right_hand",
        )
        self.change_student_modes(*["pondering"]*3)
        self.play(Transform(mover[1], new_words))
        self.look_at((FRAME_X_RADIUS*RIGHT + FRAME_Y_RADIUS*UP)/2)
        self.wait(4)


    ###

    def get_test(self):
        prev_scene = IntroducePutnam(dont_animate = True)
        return prev_scene.test

class OtherVideoClips(Scene):
    def construct(self):
        rect = ScreenRectangle()
        rect.set_height(6.5)
        rect.center()
        rect.to_edge(DOWN)
        titles = list(map(TextMobject, [
            "Essence of calculus, chapter 1",
            "Pi hiding in prime regularities",
            "How do cryptocurrencies work?"
        ]))

        self.add(rect)
        last_title = None
        for title in titles:
            title.to_edge(UP, buff = MED_SMALL_BUFF)
            if last_title:
                self.play(ReplacementTransform(last_title, title))
            else:
                self.play(FadeIn(title))
            self.wait(3)
            last_title = title

class IntroduceTetrahedron(ExternallyAnimatedScene):
    pass

class IntroduceTetrahedronSupplement(Scene):
    def construct(self):
        title = TextMobject("4", "random$^*$ points on sphere")
        title.set_color(YELLOW)
        question = TextMobject("Probability that this tetrahedron \\\\ contains the sphere's center?")
        question.next_to(title, DOWN, MED_LARGE_BUFF)
        group = VGroup(title, question)
        group.set_width(FRAME_WIDTH-1)
        group.to_edge(DOWN)

        for n in range(1, 4):
            num = TextMobject(str(n))
            num.replace(title[0], dim_to_match = 1)
            num.set_color(YELLOW)
            self.add(num)
            self.wait(0.7)
            self.remove(num)
        self.add(title[0])
        self.play(FadeIn(title[1], lag_ratio = 0.5))
        self.wait(2)
        self.play(Write(question))
        self.wait(2)

class IntroduceTetrahedronFootnote(Scene):
    def construct(self):
        words = TextMobject("""
            $^*$Chosen independently with a \\\\
            uniform distribution on the sphere.
        """)
        words.to_corner(UP+LEFT)
        self.add(words)
        self.wait(2)

class HowDoYouStart(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "How do you even start?",
            target_mode = "raise_left_hand"
        )
        self.change_student_modes("confused", "raise_left_hand", "erm")
        self.wait()
        self.teacher_says("Try a simpler case.")
        self.change_student_modes(*["thinking"]*3)
        self.wait(2)

class TwoDCase(Scene):
    CONFIG = {
        "center" : ORIGIN,
        "random_seed" : 4,
        "radius" : 2.5,
        "center_color" : BLUE,
        "point_color" : YELLOW,
        "positive_triangle_color" : BLUE,
        "negative_triangle_color" : RED,
        "triangle_fill_opacity" : 0.25,
        "n_initial_random_choices" : 9,
        "n_p3_random_moves" : 4,
    }
    def construct(self):
        self.add_title()
        self.add_circle()
        self.choose_three_random_points()
        self.simplify_further()
        self.fix_two_points_in_place()
        self.note_special_region()
        self.draw_lines_through_center()
        self.ask_about_probability_p3_lands_in_this_arc()
        self.various_arc_sizes_for_p1_p2_placements()
        self.ask_about_average_arc_size()
        self.fix_p1_in_place()
        self.overall_probability()

    def add_title(self):
        title = TextMobject("2D Case")
        title.to_corner(UP+LEFT)
        self.add(title)
        self.set_variables_as_attrs(title)

    def add_circle(self):
        circle = Circle(radius = self.radius, color = WHITE)
        center_dot = Dot(color = self.center_color).center()
        radius = DashedLine(ORIGIN, circle.radius*RIGHT)
        VGroup(circle, center_dot, radius).shift(self.center)

        self.add(center_dot)
        self.play(ShowCreation(radius))
        self.play(
            ShowCreation(circle),
            Rotating(radius, angle = 2*np.pi, about_point = self.center),
            rate_func = smooth,
            run_time = 2,
        )
        self.play(ShowCreation(
            radius,
            rate_func = lambda t : smooth(1-t),
            remover = True
        ))
        self.wait()

        self.set_variables_as_attrs(circle, center_dot)

    def choose_three_random_points(self):
        point_mobs = self.get_point_mobs()
        point_labels = self.get_point_mob_labels()
        triangle = self.get_triangle()
        self.point_labels_update = self.get_labels_update(point_mobs, point_labels)
        self.triangle_update = self.get_triangle_update(point_mobs, triangle)
        self.update_animations = [
            self.triangle_update,
            self.point_labels_update,
        ]
        for anim in self.update_animations:
            anim.update(0)

        question = TextMobject(
            "Probability that \\\\ this triangle \\\\",
            "contains the center", "?",
            arg_separator = "",
        )
        question.set_color_by_tex("center", self.center_color)
        question.scale(0.8)
        question.to_corner(UP+RIGHT)
        self.question = question

        self.play(LaggedStartMap(DrawBorderThenFill, point_mobs))
        self.play(FadeIn(triangle))
        self.wait()
        self.play(LaggedStartMap(Write, point_labels))
        self.wait()
        self.play(Write(question))
        for x in range(self.n_initial_random_choices):
            self.change_point_mobs_randomly()
            self.wait()
        angles = self.get_point_mob_angles()
        target_angles = [5*np.pi/8, 7*np.pi/8, 0]
        self.change_point_mobs([ta - a for a, ta in zip(angles, target_angles)])
        self.wait()

    def simplify_further(self):
        morty = Mortimer().flip()
        morty.scale(0.75)
        morty.to_edge(DOWN)
        morty.shift(3.5*LEFT)

        bubble = SpeechBubble(
            direction = RIGHT,
            height = 3, width = 3
        )
        bubble.pin_to(morty)
        bubble.to_edge(LEFT, SMALL_BUFF)
        bubble.write("Simplify \\\\ more!")

        self.play(FadeIn(morty))
        self.play(
            morty.change, "hooray",
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.play(Blink(morty))
        self.wait()
        self.play(
            morty.change, "happy",
            morty.fade, 1,
            *list(map(FadeOut, [bubble, bubble.content]))
        )
        self.remove(morty)

    def fix_two_points_in_place(self):
        push_pins = VGroup()
        for point_mob in self.point_mobs[:-1]:
            push_pin = SVGMobject(file_name = "push_pin")
            push_pin.set_height(0.5)
            push_pin.move_to(point_mob.get_center(), DOWN)
            line = Line(ORIGIN, UP)
            line.set_stroke(WHITE, 2)
            line.set_height(0.1)
            line.move_to(push_pin, UP)
            line.shift(0.3*SMALL_BUFF*(2*DOWN+LEFT))
            push_pin.add(line)
            push_pin.set_fill(LIGHT_GREY)
            push_pin.save_state()
            push_pin.shift(UP)
            push_pin.fade(1)
            push_pins.add(push_pin)

        self.play(LaggedStartMap(
            ApplyMethod, push_pins,
            lambda mob : (mob.restore,)
        ))
        self.add_foreground_mobjects(push_pins)
        d_thetas = 2*np.pi*np.random.random(self.n_p3_random_moves)
        for d_theta in d_thetas:
            self.change_point_mobs([0, 0, d_theta])
            self.wait()

        self.set_variables_as_attrs(push_pins)

    def note_special_region(self):
        point_mobs = self.point_mobs
        angles = self.get_point_mob_angles()

        all_arcs = self.get_all_arcs()
        arc = all_arcs[-1]
        arc_lines = VGroup()
        for angle in angles[:2]:
            line = Line(LEFT, RIGHT).scale(SMALL_BUFF)
            line.shift(self.radius*RIGHT)
            line.rotate(angle + np.pi)
            line.shift(self.center)
            line.set_stroke(arc.get_color())
            arc_lines.add(line)

        self.play(ShowCreation(arc_lines))
        self.change_point_mobs([0, 0, angles[0]+np.pi-angles[2]])
        self.change_point_mobs(
            [0, 0, arc.angle],
            ShowCreation(arc, run_time = 2)
        )
        self.change_point_mobs([0, 0, np.pi/4 - angles[1]])
        self.change_point_mobs([0, 0, 0.99*np.pi], run_time = 4)
        self.wait()

        self.set_variables_as_attrs(all_arcs, arc, arc_lines)

    def draw_lines_through_center(self):
        point_mobs = self.point_mobs
        angles = self.get_point_mob_angles()
        all_arcs = self.all_arcs

        lines = self.get_center_lines()

        self.add_foreground_mobjects(self.center_dot)
        for line in lines:
            self.play(ShowCreation(line))
        self.play(FadeIn(all_arcs), Animation(point_mobs))
        self.remove(self.circle)
        self.wait()
        self.play(
            all_arcs.space_out_submobjects, 1.5,
            Animation(point_mobs),
            rate_func = there_and_back,
            run_time = 1.5,
        )
        self.wait()
        self.change_point_mobs(
            [0, 0, np.mean(angles[:2])+np.pi-angles[2]]
        )
        self.wait()
        for x in range(3):
            self.change_point_mobs([0, 0, np.pi/2])
        self.wait()

    def ask_about_probability_p3_lands_in_this_arc(self):
        arc = self.arc

        arrow = Vector(LEFT, color = BLUE)
        arrow.next_to(arc.get_center(), RIGHT, MED_LARGE_BUFF)
        question = TextMobject("Probability of landing \\\\ in this arc?")
        question.scale(0.8)
        question.next_to(arrow, RIGHT)
        question.shift_onto_screen()
        question.shift(SMALL_BUFF*UP)

        answer = TexMobject(
            "{\\text{Length of arc}", "\\over",
            "\\text{Circumference}}"
        )
        answer.set_color_by_tex("arc", BLUE)
        answer.scale(0.8)
        answer.next_to(arrow, RIGHT)
        equals = TexMobject("=")
        equals.rotate(np.pi/2)
        equals.next_to(answer, UP, buff = 0.35)

        self.play(FadeIn(question), GrowArrow(arrow))
        self.have_p3_jump_around_randomly(15)
        self.play(
            question.next_to, answer, UP, LARGE_BUFF,
            Write(equals),
            FadeIn(answer)
        )
        self.have_p3_jump_around_randomly(4)
        angles = self.get_point_mob_angles()
        self.change_point_mobs(
            [0, 0, 1.35*np.pi - angles[2]],
            run_time = 0,
        )
        self.wait()

        question.add(equals)
        self.arc_prob_question = question
        self.arc_prob = answer
        self.arc_size_arrow = arrow

    def various_arc_sizes_for_p1_p2_placements(self):
        arc = self.arc

        self.triangle.save_state()
        self.play(*list(map(FadeOut, [
            self.push_pins, self.triangle, self.arc_lines
        ])))
        self.update_animations.remove(self.triangle_update)
        self.update_animations += [
            self.get_center_lines_update(self.point_mobs, self.center_lines),
            self.get_arcs_update(self.all_arcs)
        ]

        #90 degree angle
        self.change_point_mobs_to_angles([np.pi/2, np.pi], run_time = 1)
        elbow = VGroup(
            Line(DOWN, DOWN+RIGHT),
            Line(DOWN+RIGHT, RIGHT),
        )
        elbow.scale(0.25)
        elbow.shift(self.center)
        ninety_degrees = TexMobject("90^\\circ")
        ninety_degrees.next_to(elbow, DOWN+RIGHT, buff = 0)
        proportion = DecimalNumber(0.25)
        proportion.set_color(self.center_color)
        # proportion.next_to(arc.point_from_proportion(0.5), DOWN, MED_LARGE_BUFF)
        proportion.next_to(self.arc_size_arrow, DOWN)
        def proportion_update_func(alpha):
            angles = self.get_point_mob_angles()
            diff = abs(angles[1]-angles[0])/(2*np.pi)
            return min(diff, 1-diff)
        proportion_update = ChangingDecimal(proportion, proportion_update_func)

        self.play(ShowCreation(elbow), FadeIn(ninety_degrees))
        self.wait()
        self.play(
            ApplyMethod(
                arc.rotate_in_place, np.pi/12,
                rate_func = wiggle,
            )
        )
        self.play(LaggedStartMap(FadeIn, proportion, run_time = 1))
        self.wait()

        #Non right angles
        angle_pairs = [
            (0.26*np.pi, 1.24*np.pi), 
            (0.73*np.pi, 0.78*np.pi),
            (0.5*np.pi, np.pi),
        ]
        self.update_animations.append(proportion_update)
        for angle_pair in angle_pairs:
            self.change_point_mobs_to_angles(
                angle_pair,
                VGroup(elbow, ninety_degrees).fade, 1,
            )
            self.remove(elbow, ninety_degrees)
            self.wait()

        self.set_variables_as_attrs(proportion, proportion_update)

    def ask_about_average_arc_size(self):
        proportion = self.proportion
        brace = Brace(proportion, DOWN, buff = SMALL_BUFF)
        average = brace.get_text("Average?", buff = SMALL_BUFF)

        self.play(
            GrowFromCenter(brace),
            Write(average)
        )
        for x in range(6):
            self.change_point_mobs_to_angles(
                2*np.pi*np.random.random(2)
            )
        self.change_point_mobs_to_angles(
            [1.2*np.pi, 0.3*np.pi]
        )
        self.wait()

        self.set_variables_as_attrs(brace, average)

    def fix_p1_in_place(self):
        push_pin = self.push_pins[0]
        P1, P2, P3 = point_mobs = self.point_mobs

        self.change_point_mobs_to_angles([0.9*np.pi])
        push_pin.move_to(P1.get_center(), DOWN)
        push_pin.save_state()
        push_pin.shift(UP)
        push_pin.fade(1)
        self.play(push_pin.restore)
        for angle in [0.89999*np.pi, -0.09999*np.pi, 0.4*np.pi]:
            self.change_point_mobs_to_angles(
                [0.9*np.pi, angle],
                run_time = 4,
            )
        self.play(FadeOut(self.average[-1]))

    def overall_probability(self):
        point_mobs = self.point_mobs
        triangle = self.triangle

        one_fourth = TexMobject("1/4")
        one_fourth.set_color(BLUE)
        one_fourth.next_to(self.question, DOWN)

        self.triangle_update.update(1)
        self.play(
            FadeIn(triangle),
            Animation(point_mobs)
        )
        self.update_animations.append(self.triangle_update)
        self.have_p3_jump_around_randomly(8, wait_time = 0.25)
        self.play(ReplacementTransform(
            self.proportion.copy(), VGroup(one_fourth)
        ))
        self.have_p3_jump_around_randomly(32, wait_time = 0.25)

    #####

    def get_point_mobs(self):
        points = np.array([
            self.center + rotate_vector(self.radius*RIGHT, theta)
            for theta in 2*np.pi*np.random.random(3)
        ])
        for index in 0, 1, 0:
            if self.points_contain_center(points):
                break
            points[index] -= self.center
            points[index] *= -1
            points[index] += self.center
        point_mobs = self.point_mobs = VGroup(*[
            Dot().move_to(point) for point in points            
        ])
        point_mobs.set_color(self.point_color)
        return point_mobs

    def get_point_mob_labels(self):
        point_labels = VGroup(*[
            TexMobject("P_%d"%(i+1))
            for i in range(len(self.point_mobs))
        ])
        point_labels.set_color(self.point_mobs.get_color())
        self.point_labels = point_labels
        return point_labels

    def get_triangle(self):
        triangle = self.triangle = RegularPolygon(n = 3)
        triangle.set_fill(WHITE, opacity = self.triangle_fill_opacity)
        return triangle

    def get_center_lines(self):
        angles = self.get_point_mob_angles()
        lines = VGroup()
        for angle in angles[:2]:
            line = DashedLine(
                self.radius*RIGHT, self.radius*LEFT
            )
            line.rotate(angle)
            line.shift(self.center)
            line.set_color(self.point_color)
            lines.add(line)
        self.center_lines = lines
        return lines

    def get_labels_update(self, point_mobs, labels):
        def update_labels(labels):
            for point_mob, label in zip(point_mobs, labels):
                label.move_to(point_mob)
                vect = point_mob.get_center() - self.center
                vect /= get_norm(vect)
                label.shift(MED_LARGE_BUFF*vect)
            return labels
        return UpdateFromFunc(labels, update_labels)

    def get_triangle_update(self, point_mobs, triangle):
        def update_triangle(triangle):
            points = [pm.get_center() for pm in point_mobs]
            triangle.set_points_as_corners(points)
            if self.points_contain_center(points):
                triangle.set_color(self.positive_triangle_color)
            else:
                triangle.set_color(self.negative_triangle_color)
            return triangle
        return UpdateFromFunc(triangle, update_triangle)

    def get_center_lines_update(self, point_mobs, center_lines):
        def update_lines(center_lines):
            for point_mob, line in zip(point_mobs, center_lines):
                point = point_mob.get_center() - self.center
                line.rotate_in_place(
                    angle_of_vector(point) - line.get_angle()
                )
                line.move_to(self.center)
            return center_lines
        return UpdateFromFunc(center_lines, update_lines)

    def get_arcs_update(self, all_arcs):
        def update_arcs(arcs):
            new_arcs = self.get_all_arcs()
            Transform(arcs, new_arcs).update(1)
            return arcs
        return UpdateFromFunc(all_arcs, update_arcs)

    def get_all_arcs(self):
        angles = self.get_point_mob_angles()
        all_arcs = VGroup()
        for da0, da1 in it.product(*[[0, np.pi]]*2):
            arc_angle = (angles[1]+da1) - (angles[0]+da0)
            arc_angle = (arc_angle+np.pi)%(2*np.pi)-np.pi
            arc = Arc(
                start_angle = angles[0]+da0,
                angle = arc_angle,
                radius = self.radius,
                stroke_width = 5,
            )
            arc.shift(self.center)
            all_arcs.add(arc)
        all_arcs.set_color_by_gradient(RED, MAROON_B, PINK, BLUE)
        self.all_arcs = all_arcs
        return all_arcs

    def points_contain_center(self, points):
        p0, p1, p2 = points
        v1 = p1 - p0
        v2 = p2 - p0
        c = self.center - p0
        M = np.matrix([v1[:2], v2[:2]]).T
        M_inv = np.linalg.inv(M)
        coords = np.dot(M_inv, c[:2])
        return np.all(coords > 0) and (np.sum(coords.flatten()) <= 1)

    def get_point_mob_theta_change_anim(self, point_mob, d_theta):
        curr_theta = angle_of_vector(point_mob.get_center() - self.center)
        d_theta = (d_theta + np.pi)%(2*np.pi) - np.pi
        new_theta = curr_theta + d_theta

        def update_point(point_mob, alpha):
            theta = interpolate(curr_theta, new_theta, alpha)
            point_mob.move_to(self.center + self.radius*(
                np.cos(theta)*RIGHT + np.sin(theta)*UP
            ))
            return point_mob
        return UpdateFromAlphaFunc(point_mob, update_point, run_time = 2)

    def change_point_mobs(self, d_thetas, *added_anims, **kwargs):
        anims = it.chain(
            self.update_animations,
            [
                self.get_point_mob_theta_change_anim(pm, dt)
                for pm, dt in zip(self.point_mobs, d_thetas)
            ],
            added_anims
        )
        self.play(*anims, **kwargs)
        for update in self.update_animations:
            update.update(1)
 
    def change_point_mobs_randomly(self, *added_anims, **kwargs):
        d_thetas = 2*np.pi*np.random.random(len(self.point_mobs))
        self.change_point_mobs(d_thetas, *added_anims, **kwargs)

    def change_point_mobs_to_angles(self, target_angles, *added_anims, **kwargs):
        angles = self.get_point_mob_angles()
        n_added_targets = len(angles) - len(target_angles)
        target_angles = list(target_angles) + list(angles[-n_added_targets:])
        self.change_point_mobs(
            [ta-a for a, ta in zip(angles, target_angles)],
            *added_anims, **kwargs
        )

    def get_point_mob_angles(self):
        point_mobs = self.point_mobs
        points = [pm.get_center() - self.center for pm in point_mobs]
        return np.array(list(map(angle_of_vector, points)))

    def have_p3_jump_around_randomly(self, n_jumps, wait_time = 0.75, run_time = 0):
        for x in range(n_jumps):
            self.change_point_mobs(
                [0, 0, 2*np.pi*random.random()],
                run_time = run_time
            )
            self.wait(wait_time)

class FixThreePointsOnSphere(ExternallyAnimatedScene):
    pass

class AddCenterLinesAndPlanesToSphere(ExternallyAnimatedScene):
    pass

class AverageSizeOfSphericalTriangleSection(ExternallyAnimatedScene):
    pass

class AverageSizeOfSphericalTriangleSectionSupplement(Scene):
    def construct(self):
        words = TextMobject(
            "Average size of \\\\", "this section", "?",
            arg_separator = ""
        )
        words.set_color_by_tex("section", GREEN)
        words.set_width(FRAME_WIDTH - 1)
        words.to_edge(DOWN)
        self.play(Write(words))
        self.wait(3)

class TryASurfaceIntegral(TeacherStudentsScene):
    def construct(self):
        self.student_says("Can you do \\\\ a surface integral?")
        self.change_student_modes("confused", "raise_left_hand", "confused")
        self.wait()
        self.teacher_says(
            "I mean...you can \\emph{try}",
            target_mode = "sassy",
        )
        self.wait(2)

class RevisitTwoDCase(TwoDCase):
    CONFIG = {
        "random_seed" : 4,
        "center" : 3*LEFT + 0.5*DOWN,
        "radius" : 2,
        "n_random_trials" : 200,
    }
    def construct(self):
        self.force_skipping()

        self.setup_circle()
        self.show_probability()
        self.add_lines_and_comment_on_them()
        self.rewrite_random_procedure()
        self.four_possibilities_for_coin_flips()

    def setup_circle(self):
        point_mobs = self.get_point_mobs()
        point_labels = self.get_point_mob_labels()
        triangle = self.get_triangle()
        circle = Circle(radius = self.radius, color = WHITE)
        center_dot = Dot(color = self.center_color)
        VGroup(circle, center_dot).shift(self.center)

        self.point_labels_update = self.get_labels_update(point_mobs, point_labels)
        self.triangle_update = self.get_triangle_update(point_mobs, triangle)
        self.update_animations = [
            self.triangle_update,
            self.point_labels_update,
        ]
        for anim in self.update_animations:
            anim.update(1)

        self.add(
            center_dot, circle, triangle, 
            point_mobs, point_labels
        )
        self.add_foreground_mobjects(center_dot)
        self.set_variables_as_attrs(circle, center_dot)

    def show_probability(self):
        title = TexMobject(
            "P(\\text{triangle contains the center})",
            "=", "1/4"
        )
        title.to_edge(UP, buff = MED_SMALL_BUFF)
        title.set_color_by_tex("1/4", BLUE)
        four = title[-1][-1]
        four_circle = Circle(color = YELLOW)
        four_circle.replace(four, dim_to_match = 1)
        four_circle.scale_in_place(1.2)

        self.n_in = 0
        self.n_out = 0
        frac = TexMobject(
            "{0", "\\over", "\\quad 0", "+", "0 \\quad}", "="
        )
        placeholders = frac.get_parts_by_tex("0")
        positions = [ORIGIN, RIGHT, LEFT]
        frac.next_to(self.circle, RIGHT, 1.5*LARGE_BUFF)

        def place_random_triangles(n, wait_time):
            for x in range(n):
                self.change_point_mobs_randomly(run_time = 0)
                contain_center = self.points_contain_center(
                    [pm.get_center() for pm in self.point_mobs]
                )
                if contain_center:
                    self.n_in += 1
                else:
                    self.n_out += 1
                nums = list(map(Integer, [self.n_in, self.n_in, self.n_out]))
                VGroup(*nums[:2]).set_color(self.positive_triangle_color)
                VGroup(*nums[2:]).set_color(self.negative_triangle_color)
                for num, placeholder, position in zip(nums, placeholders, positions):
                    num.move_to(placeholder, position)
                decimal = DecimalNumber(float(self.n_in)/(self.n_in + self.n_out))
                decimal.next_to(frac, RIGHT, SMALL_BUFF)

                self.add(decimal, *nums)
                self.wait(wait_time)
                self.remove(decimal, *nums)
            return VGroup(decimal, *nums)


        self.play(Write(title))
        self.add(frac)
        self.remove(*placeholders)
        place_random_triangles(10, 0.25)
        nums = place_random_triangles(self.n_random_trials, 0.05)
        self.add(nums)
        self.wait()
        self.play(*list(map(FadeOut, [frac, nums, title])))

    def add_lines_and_comment_on_them(self):
        center_lines = self.get_center_lines()
        center_lines.save_state()
        center_line_shadows = center_lines.copy()
        center_line_shadows.set_stroke(LIGHT_GREY, 2)
        arcs = self.get_all_arcs()

        center_lines.generate_target()
        center_lines.target.to_edge(RIGHT, buff = LARGE_BUFF)
        rect = SurroundingRectangle(center_lines.target, buff = MED_SMALL_BUFF)
        rect.set_stroke(WHITE, 2)

        words1 = TextMobject("Helpful new objects")
        words2 = TextMobject("Reframe problem around these")
        for words in words1, words2:
            words.scale(0.8)
            words.next_to(rect, UP)
            words.shift_onto_screen()

        self.play(LaggedStartMap(ShowCreation, center_lines, run_time = 1))
        self.play(
            LaggedStartMap(FadeIn, arcs, run_time = 1),
            Animation(self.point_mobs),
        )
        self.wait()
        self.add(center_line_shadows)
        self.play(MoveToTarget(center_lines))
        self.play(ShowCreation(rect), Write(words1))
        self.wait(2)
        self.play(ReplacementTransform(words1, words2))
        self.wait(2)
        self.play(
            center_lines.restore,
            center_lines.fade, 1,
            *list(map(FadeOut, [
                rect, words2, center_line_shadows,
                self.triangle, arcs,
                self.point_mobs,
                self.point_labels,
            ]))
        )
        center_lines.restore()
        self.remove(center_lines)

    def rewrite_random_procedure(self):
        point_mobs = self.point_mobs
        center_lines = self.center_lines 

        random_procedure = TextMobject("Random procedure")
        underline = Line(LEFT, RIGHT)
        underline.stretch_to_fit_width(random_procedure.get_width())
        underline.scale(1.1)
        underline.next_to(random_procedure, DOWN)
        group = VGroup(random_procedure, underline)
        group.to_corner(UP+RIGHT)

        words = VGroup(*list(map(TextMobject, [
            "Choose 3 random points",
            "Choose 2 random lines",
            "Flip coin for each line \\\\ to get $P_1$ and $P_2$",
            "Choose $P_3$ at random"
        ])))
        words.scale(0.8)
        words.arrange(DOWN, buff = MED_LARGE_BUFF)
        words.next_to(underline, DOWN)
        words[1].set_color(YELLOW)

        point_label_groups = VGroup()
        for point_mob, label in zip(self.point_mobs, self.point_labels):
            group = VGroup(point_mob, label)
            group.save_state()
            group.move_to(words[0], LEFT)
            group.fade(1)
            point_label_groups.add(group)
        self.point_label_groups = point_label_groups

        cross = Cross(words[0])
        cross.set_stroke(RED, 6)

        self.center_lines_update = self.get_center_lines_update(
            point_mobs, center_lines
        )
        self.update_animations.append(self.center_lines_update)
        self.update_animations.remove(self.triangle_update)

        #Choose random points
        self.play(
            Write(random_procedure),
            ShowCreation(underline)
        )
        self.play(FadeIn(words[0]))
        self.play(LaggedStartMap(
            ApplyMethod, point_label_groups,
            lambda mob : (mob.restore,),
        ))
        self.play(
            ShowCreation(cross), 
            point_label_groups.fade, 1,
        )
        self.wait()

        #Choose two random lines
        self.center_lines_update.update(1)
        self.play(
            FadeIn(words[1]),
            LaggedStartMap(GrowFromCenter, center_lines)
        )
        for x in range(3):
            self.change_point_mobs_randomly(run_time = 1)
        self.change_point_mobs_to_angles([0.8*np.pi, 1.3*np.pi])

        #Flip a coin for each line
        def flip_point_label_back_and_forth(point_mob, label):
            for x in range(6):
                point_mob.rotate(np.pi, about_point = self.center)
                self.point_labels_update.update(1)
                self.wait(0.5)
            self.wait(0.5)

        def choose_p1_and_p2():
            for group in point_label_groups[:2]:
                group.set_fill(self.point_color, 1)
                flip_point_label_back_and_forth(*group)

        choose_p1_and_p2()
        self.play(Write(words[2]))

        #Seems convoluted
        randy = Randolph().flip()
        randy.scale(0.5)
        randy.to_edge(DOWN)
        randy.shift(2*RIGHT)

        self.play(point_label_groups.fade, 1)
        self.change_point_mobs_randomly(run_time = 1)
        choose_p1_and_p2()
        point_label_groups.fade(1)
        self.change_point_mobs_randomly(FadeIn(randy))
        self.play(
            PiCreatureSays(
                randy, "Seems \\\\ convoluted",
                bubble_kwargs = {"height" : 2, "width" : 2},
                target_mode = "confused"
            )
        )
        choose_p1_and_p2()
        self.play(
            FadeOut(randy.bubble),
            FadeOut(randy.bubble.content),
            randy.change, "pondering",
        )
        self.play(Blink(randy))
        self.play(FadeOut(randy))

        #Choosing the third point
        self.change_point_mobs([0, 0, -np.pi/2], run_time = 0)
        p3_group = point_label_groups[2]
        p3_group.save_state()
        p3_group.move_to(words[3], LEFT)

        self.play(Write(words[3], run_time = 1))
        self.play(
            p3_group.restore,
            p3_group.set_fill, YELLOW, 1
        )
        self.wait()
        self.play(Swap(*words[2:4]))
        self.wait()

        #Once the continuous randomness is handled
        rect = SurroundingRectangle(VGroup(words[1], words[3]))
        rect.set_stroke(WHITE, 2)
        brace = Brace(words[2], DOWN)
        brace_text = brace.get_text("4 equally likely outcomes")
        brace_text.scale_in_place(0.8)

        self.play(ShowCreation(rect))
        self.play(GrowFromCenter(brace))
        self.play(Write(brace_text))
        self.wait()

        self.random_procedure_words = words

    def four_possibilities_for_coin_flips(self):
        arcs = self.all_arcs
        point_mobs = self.point_mobs
        arc = arcs[-1]
        point_label_groups = self.point_label_groups
        arc_update = self.get_arcs_update(arcs)
        arc_update.update(1)
        self.update_animations.append(arc_update)

        def second_arc_update_func(arcs):
            VGroup(*arcs[:-1]).set_stroke(width = 0)
            arcs[-1].set_stroke(PINK, 6)
            return arcs
        second_arc_update = UpdateFromFunc(arcs, second_arc_update_func)
        second_arc_update.update(1)
        self.update_animations.append(second_arc_update)
        self.update_animations.append(Animation(point_label_groups))

        def do_the_rounds():
            for index in 0, 1, 0, 1:
                point_mob = point_mobs[index]
                point_mob.generate_target()
                point_mob.target.rotate(
                    np.pi, about_point = self.center,
                )
                self.play(
                    MoveToTarget(point_mob),
                    *self.update_animations,
                    run_time = np.sqrt(2)/4 #Hacky reasons to be irrational
                )
                self.wait()

        self.revert_to_original_skipping_status()
        do_the_rounds()
        self.triangle_update.update(1)
        self.remove(arcs)
        self.update_animations.remove(arc_update)
        self.update_animations.remove(second_arc_update)
        self.play(FadeIn(self.triangle))
        self.wait()
        self.update_animations.insert(0, self.triangle_update)
        do_the_rounds()
        self.wait()
        self.change_point_mobs_randomly()
        for x in range(2):
            do_the_rounds()

class ThisIsWhereItGetsGood(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "This is where \\\\ things get good",
            target_mode = "hooray"
        )
        self.change_student_modes(*["hooray"]*3)
        self.wait(2)

class ContrastTwoRandomProcesses(TwoDCase):
    CONFIG = {
        "radius" : 1.5,
        "random_seed" : 0,
    }
    def construct(self):
        circle = Circle(color = WHITE, radius = self.radius)
        point_mobs = self.get_point_mobs()
        for point in point_mobs:
            point.scale_in_place(1.5)
            point.set_stroke(RED, 1)
        labels = self.get_point_mob_labels()
        self.get_labels_update(point_mobs, labels).update(1)
        center_lines = self.get_center_lines()
        point_label_groups = VGroup(*[
            VGroup(*pair) for pair in zip(point_mobs, labels)
        ])

        right_circles = VGroup(*[
            VGroup(circle, *point_label_groups[:i+1]).copy()
            for i in range(3)
        ])
        left_circles = VGroup(
            VGroup(circle, center_lines).copy(),
            VGroup(
                circle, center_lines, 
                point_label_groups[2]
            ).copy(),
            VGroup(
                circle, center_lines, 
                *point_label_groups[2::-1]
            ).copy(),
        )
        for circles in left_circles, right_circles:
            circles.scale(0.5)
            circles[0].to_edge(UP, buff = MED_LARGE_BUFF)
            circles[2].to_edge(DOWN, buff = MED_LARGE_BUFF)
            for c1, c2 in zip(circles, circles[1:]):
                circles.add(Arrow(c1[0], c2[0], color = GREEN))
        left_circles.shift(3*LEFT)
        right_circles.shift(3*RIGHT)

        vs = TextMobject("vs.")
        self.show_creation_of_circle_group(left_circles)
        self.play(Write(vs))
        self.show_creation_of_circle_group(right_circles)
        self.wait()

    def show_creation_of_circle_group(self, group):
        circles = group[:3]
        arrows = group[3:]

        self.play(
            ShowCreation(circles[0][0]),
            FadeIn(VGroup(*circles[0][1:])),
        )
        for c1, c2, arrow in zip(circles, circles[1:], arrows):
            self.play(
                GrowArrow(arrow),
                ApplyMethod(
                    c1.copy().shift, 
                    c2[0].get_center() - c1[0].get_center(),
                    remover = True
                )
            )
            self.add(c2)
            n = len(c2) - len(c1)
            self.play(*list(map(GrowFromCenter, c2[-n:])))

class Rewrite3DRandomProcedure(Scene):
    def construct(self):
        random_procedure = TextMobject("Random procedure")
        underline = Line(LEFT, RIGHT)
        underline.stretch_to_fit_width(random_procedure.get_width())
        underline.scale(1.1)
        underline.next_to(random_procedure, DOWN)
        group = VGroup(random_procedure, underline)
        group.to_corner(UP+LEFT)
        
        words = VGroup(*list(map(TextMobject, [
            "Choose 4 random points",
            "Choose 3 random lines",
            "Choose $P_4$ at random",
            "Flip coin for each line \\\\ to get $P_1$, $P_2$, $P_3$",
        ])))
        words.scale(0.8)
        words.arrange(DOWN, buff = MED_LARGE_BUFF)
        words.next_to(underline, DOWN)
        words[1].set_color(YELLOW)
        cross = Cross(words[0])
        cross.set_stroke(RED, 6)

        self.play(
            Write(random_procedure),
            ShowCreation(underline)
        )
        self.play(FadeIn(words[0]))
        self.play(ShowCreation(cross))
        self.wait()
        self.play(LaggedStartMap(FadeIn, words[1]))
        self.play(LaggedStartMap(FadeIn, words[2]))
        self.wait(2)
        self.play(Write(words[3]))
        self.wait(3)

class AntipodalViewOfThreeDCase(ExternallyAnimatedScene):
    pass

class ThreeDAnswer(Scene):
    def construct(self):
        words = TextMobject(
            "Probability that the tetrahedron contains center:", 
            "$\\frac{1}{8}$"
        )
        words.set_width(FRAME_WIDTH - 1)
        words.to_edge(DOWN)
        words[1].set_color(BLUE)

        self.play(Write(words))
        self.wait(2)

class FormalWriteupScreenCapture(ExternallyAnimatedScene):
    pass

class Formality(TeacherStudentsScene):
    def construct(self):
        words = TextMobject(
            "Write-up by Ralph Howard and Paul Sisson (link below)"
        )
        words.scale(0.7)
        words.to_corner(UP+LEFT, buff = MED_SMALL_BUFF)

        self.student_says(
            "How would you \\\\ write that down?",
            target_mode = "sassy"
        )
        self.change_student_modes("confused", "sassy", "erm")
        self.wait()
        self.play(
            Write(words),
            FadeOut(self.students[1].bubble),
            FadeOut(self.students[1].bubble.content),
            self.teacher.change, "raise_right_hand"
        )
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = words
        )
        self.wait(8)

class ProblemSolvingTakeaways(Scene):
    def construct(self):
        title = TextMobject("Problem solving takeaways")
        underline = Line(LEFT, RIGHT)
        underline.set_width(title.get_width()*1.1)
        underline.next_to(title, DOWN)
        group = VGroup(title, underline)
        group.to_corner(UP+LEFT)

        points = VGroup(*[
            TextMobject(string, alignment = "")
            for string in [
                "Ask a simpler version \\\\ of the question",
                "Try reframing the question \\\\ around new constructs",
            ]
        ])
        points[0].set_color(BLUE)
        points[1].set_color(YELLOW)
        points.arrange(
            DOWN, buff = LARGE_BUFF,
            aligned_edge = LEFT
        )
        points.next_to(group, DOWN, LARGE_BUFF)

        self.play(Write(title), ShowCreation(underline))
        self.wait()
        for point in points:
            self.play(Write(point))
            self.wait(3)

class BrilliantPuzzle(PiCreatureScene):
    CONFIG = {
        "random_seed" : 2,
    }
    def construct(self):
        students = self.students
        tests = VGroup()
        for student in students:
            test = self.get_test()
            test.move_to(0.75*student.get_center())
            tests.add(test)
            student.test = test
        for i, student in enumerate(students):
            student.right = students[(i+1)%len(students)]
            student.left = students[(i-1)%len(students)]
        arrows = VGroup()
        for s1, s2 in adjacent_pairs(self.students):
            arrow = Arrow(
                s1.get_center(), s2.get_center(), 
                path_arc = np.pi/2,
                buff = 0.8
            )
            arrow.tip.shift(SMALL_BUFF*arrow.get_vector())
            arrow.tip.shift(-0.1*SMALL_BUFF*arrow.tip.get_center())
            # arrow.shift(-MED_SMALL_BUFF*arrow.get_vector())
            arrow.set_color(RED)
            arrow.pointing_right = True
            arrows.add(arrow)
            s1.arrow = arrow
            arrow.student = s1

        title = TextMobject("Puzzle from Brilliant")
        title.scale(0.75)
        title.to_corner(UP+LEFT)

        question = TextMobject("Expected number of \\\\ circled students?")
        question.to_corner(UP+RIGHT)

        self.remove(students)
        self.play(Write(title))
        self.play(LaggedStartMap(GrowFromCenter, students))
        self.play(
            LaggedStartMap(Write, tests),
            LaggedStartMap(
                ApplyMethod, students,
                lambda m : (m.change, "horrified", m.test)
            )
        )
        self.wait()
        self.play(LaggedStartMap(
            ApplyMethod, students,
            lambda m : (m.change, "conniving")
        ))
        self.play(LaggedStartMap(ShowCreation, arrows))
        for x in range(2):
            self.swap_arrows_randomly(arrows)
        self.wait()
        circles = self.circle_students()
        self.play(Write(question))
        for x in range(10):
            self.swap_arrows_randomly(arrows, FadeOut(circles))
            circles = self.circle_students()
            self.wait()

    ####

    def get_test(self):
        lines = VGroup(*[Line(ORIGIN, 0.5*RIGHT) for x in range(6)])
        lines.arrange(DOWN, buff = SMALL_BUFF)
        rect = SurroundingRectangle(lines)
        rect.set_stroke(WHITE)
        lines.set_stroke(WHITE, 2)
        test = VGroup(rect, lines)
        test.set_height(0.5)
        return test

    def create_pi_creatures(self):
        self.students = VGroup(*[
            PiCreature(
                color = random.choice([BLUE_C, BLUE_D, BLUE_E, GREY_BROWN])
            ).scale(0.25).move_to(3*vect)
            for vect in compass_directions(8)
        ])
        return self.students

    def get_arrow_swap_anim(self, arrow):
        arrow.generate_target()
        if arrow.pointing_right:
            target_color = GREEN
            target_angle = np.pi - np.pi/4
        else:
            target_color = RED
            target_angle = np.pi + np.pi/4
        arrow.target.set_color(target_color)
        arrow.target.rotate(
            target_angle, 
            about_point = arrow.student.get_center()
        )
        arrow.pointing_right = not arrow.pointing_right
        return MoveToTarget(arrow, path_arc = np.pi)

    def swap_arrows_randomly(self, arrows, *added_anims):
        anims = []
        for arrow in arrows:
            if random.choice([True, False]):
                anims.append(self.get_arrow_swap_anim(arrow))
        self.play(*anims + list(added_anims))

    def circle_students(self):
        circles = VGroup()
        circled_students = list(self.students)
        for student in self.students:
            if student.arrow.pointing_right:
                to_remove = student.right
            else:
                to_remove = student.left
            if to_remove in circled_students:
                circled_students.remove(to_remove)
        for student in circled_students:
            circle = Circle(color = YELLOW)
            circle.set_height(1.2*student.get_height())
            circle.move_to(student)
            circles.add(circle)
            self.play(ShowCreation(circle))
        return circles

class ScrollThroughBrilliantCourses(ExternallyAnimatedScene):
    pass

class BrilliantProbability(ExternallyAnimatedScene):
    pass

class Promotion(PiCreatureScene):
    CONFIG = {
        "seconds_to_blink" : 5,
    }
    def construct(self):
        url = TextMobject("https://brilliant.org/3b1b/")
        url.to_corner(UP+LEFT)

        rect = Rectangle(height = 9, width = 16)
        rect.set_height(5.5)
        rect.next_to(url, DOWN)
        rect.to_edge(LEFT)

        self.play(
            Write(url),
            self.pi_creature.change, "raise_right_hand"
        )
        self.play(ShowCreation(rect))
        self.wait(2)
        self.change_mode("thinking")
        self.wait()
        self.look_at(url)
        self.wait(10)
        self.change_mode("happy")
        self.wait(10)
        self.change_mode("raise_right_hand")
        self.wait(10)

        self.remove(rect)
        self.play(
            url.next_to, self.pi_creature, UP+LEFT
        )
        url_rect = SurroundingRectangle(url)
        self.play(ShowCreation(url_rect))
        self.play(FadeOut(url_rect))
        self.wait(3)

class AddedPromoWords(Scene):
    def construct(self):
        words = TextMobject(
            "First", "$2^8$", "vistors get",
            "$(e^\\pi - \\pi)\\%$", "off"
        )
        words.set_width(FRAME_WIDTH - 1)
        words.to_edge(DOWN)
        words.set_color_by_tex("2^8", YELLOW)
        words.set_color_by_tex("pi", PINK)

        self.play(Write(words))
        self.wait()

class PatreonThanks(PatreonEndScreen):
    CONFIG = {
        "specific_patrons" : [
            "Randall Hunt",
            "Burt Humburg",
            "CrypticSwarm",
            "Juan Benet",
            "David Kedmey",
            "Marcus Schiebold",
            "Ali Yahya",
            "Mayank M. Mehrotra",
            "Lukas Biewald",
            "Yana Chernobilsky",
            "Kaustuv DeBiswas",
            "Kathryn Schmiedicke",
            "Yu Jun",
            "Dave Nicponski",
            "Damion Kistler",
            "Jordan Scales",
            "Markus Persson",
            "Egor Gumenuk",
            "Yoni Nazarathy",
            "Ryan Atallah",
            "Joseph John Cox",
            "Luc Ritchie",
            "James Park",
            "Samantha D. Suplee",
            "Delton",
            "Thomas Tarler",
            "Jake Alzapiedi",
            "Jonathan Eppele",
            "Taro Yoshioka",
            "1stViewMaths",
            "Jacob Magnuson",
            "Mark Govea",
            "Dagan Harrington",
            "Clark Gaebel",
            "Eric Chow",
            "Mathias Jansson",
            "David Clark",
            "Michael Gardner",
            "Erik Sundell",
            "Awoo",
            "Dr. David G. Stork",
            "Tianyu Ge",
            "Ted Suzman",
            "Linh Tran",
            "Andrew Busey",
            "John Haley",
            "Ankalagon",
            "Eric Lavault",
            "Boris Veselinovich",
            "Julian Pulgarin",
            "Jeff Linse",
            "Cooper Jones",
            "Ryan Dahl",
            "Robert Teed",
            "Jason Hise",
            "Meshal Alshammari",
            "Bernd Sing",
            "Mustafa Mahdi",
            "Mathew Bramson",
            "Jerry Ling",
            "Shimin Kuang",
            "Rish Kundalia",
            "Achille Brighton",
            "Ripta Pasay",
        ]
    }


























