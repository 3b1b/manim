from manimlib.imports import *
import json


class IntroduceIMO(Scene):
    CONFIG = {
        "num_countries": 130,
        "use_real_images": True,
        # "use_real_images": False,
        "include_labels": False,
        "camera_config": {"background_color": DARKER_GREY},
        "random_seed": 6,
    }

    def construct(self):
        self.add_title()
        self.show_flags()
        self.show_students()
        self.move_title()
        self.isolate_usa()

    def add_title(self):
        title = TextMobject(
            "International ", "Mathematical ", "Olympiad",
        )
        title.scale(1.25)
        logo = ImageMobject("imo_logo")
        logo.set_height(1)

        group = Group(logo, title)
        group.arrange(RIGHT)
        group.to_edge(UP, buff=MED_SMALL_BUFF)

        self.add(title, logo)
        self.title = title
        self.logo = logo

    def show_flags(self):
        flags = self.get_flags()
        flags.set_height(6)
        flags.to_edge(DOWN)
        random_flags = Group(*flags)
        random_flags.shuffle()

        self.play(
            LaggedStartMap(
                FadeInFromDown, random_flags,
                run_time=2,
                lag_ratio=0.03,
            )
        )
        self.remove(random_flags)
        self.add(flags)
        self.wait()

        self.flags = flags

    def show_students(self):
        flags = self.flags

        student_groups = VGroup()
        all_students = VGroup()
        for flag in flags:
            group = self.get_students(flag)
            student_groups.add(group)
            for student in group:
                student.preimage = VectorizedPoint()
                student.preimage.move_to(flag)
                all_students.add(student)
        all_students.shuffle()

        student_groups.generate_target()
        student_groups.target.arrange_in_grid(
            n_rows=10,
            buff=SMALL_BUFF,
        )
        student_groups.target[-9:].align_to(student_groups.target[0], LEFT)
        student_groups.target.match_height(flags)
        student_groups.target.match_y(flags)
        student_groups.target.to_edge(RIGHT, buff=1)

        self.play(LaggedStart(
            *[
                ReplacementTransform(
                    student.preimage, student
                )
                for student in all_students
            ],
            run_time=2,
            lag_ratio=0.2,
        ))
        self.wait()
        self.play(
            MoveToTarget(student_groups),
            flags.space_out_submobjects, 0.8,
            flags.to_edge, LEFT, MED_SMALL_BUFF,
        )
        self.wait()

        self.student_groups = student_groups

    def move_title(self):
        title = self.title
        logo = self.logo

        new_title = TextMobject("IMO")
        new_title.match_height(title)

        logo.generate_target()
        group = Group(logo.target, new_title)
        group.arrange(RIGHT, buff=SMALL_BUFF)
        group.match_y(title)
        group.match_x(self.student_groups, UP)

        title.generate_target()
        for word, letter in zip(title.target, new_title[0]):
            for nl in word:
                nl.move_to(letter)
            word.set_opacity(0)
            word[0].set_opacity(1)
            word[0].become(letter)

        self.play(
            MoveToTarget(title),
            MoveToTarget(logo),
        )
        self.wait()

    def isolate_usa(self):
        flags = self.flags
        student_groups = self.student_groups

        us_flag = flags[0]
        random_flags = Group(*flags[1:])
        random_flags.shuffle()

        old_height = us_flag.get_height()
        us_flag.label.set_width(0.8 * us_flag.get_width())
        us_flag.label.next_to(
            us_flag, DOWN,
            buff=0.2 * us_flag.get_height(),
        )
        us_flag.label.set_opacity(0)
        us_flag.add(us_flag.label)
        us_flag.generate_target()
        us_flag.target.scale(1 / old_height)
        us_flag.target.to_corner(UL)
        us_flag.target[1].set_opacity(1)

        self.remove(us_flag)
        self.play(
            LaggedStart(
                *[
                    FadeOutAndShift(flag, DOWN)
                    for flag in random_flags
                ],
                lag_ratio=0.05,
                run_time=1.5
            ),
            MoveToTarget(us_flag),
            student_groups[1:].set_opacity, 0.1,
        )
        self.wait()

    #
    def get_students(self, flag):
        dots = VGroup(*[Dot() for x in range(6)])
        dots.arrange_in_grid(n_cols=2, buff=SMALL_BUFF)
        dots.match_height(flag)
        dots.next_to(flag, RIGHT, SMALL_BUFF)
        if isinstance(flag, ImageMobject):
            rgba = random.choice(random.choice(flag.pixel_array))
            if np.all(rgba < 100):
                rgba = interpolate(rgba, 256 * np.ones(len(rgba)), 0.5)
            color = rgba_to_color(rgba / 256)
        else:
            color = random_bright_color()
        dots.set_color(color)
        return dots

    def get_flags(self):
        with open(os.path.join("assets", "imo_countries.json")) as fp:
            countries = json.load(fp)
        with open(os.path.join("assets", "country_codes.json")) as fp:
            code_map = json.load(fp)

        images = Group()
        for country in countries:
            country = country.upper()
            if country not in code_map:
                continue
            short_code = code_map[country].lower()
            try:
                image = ImageMobject(os.path.join("flags", short_code))
                image.set_width(1)
                label = VGroup(*[TextMobject(l) for l in country])
                label.arrange(RIGHT, buff=0.05, aligned_edge=DOWN)
                label.set_height(0.25)
                if not self.use_real_images:
                    rect = SurroundingRectangle(image, buff=0)
                    rect.set_stroke(WHITE, 1)
                    image = rect
                image.label = label
                images.add(image)
            except OSError:
                pass
        # images.remove(*images[self.num_countries:])
        n_rows = 10
        images.arrange_in_grid(
            n_rows=n_rows,
            buff=1.25,
        )
        images[-(len(images) % n_rows):].align_to(images[0], LEFT)
        sf = 1.7
        images.stretch(sf, 0)
        for i, image in enumerate(images):
            image.set_height(1)
            image.stretch(1 / sf, 0)
            image.label.next_to(image, DOWN, SMALL_BUFF)
            if self.include_labels:
                image.add(image.label)

        images.set_width(FRAME_WIDTH - 1)
        if images.get_height() > FRAME_HEIGHT - 1:
            images.set_height(FRAME_HEIGHT - 1)
        images.center()
        return images


class ShowTest(Scene):
    def construct(self):
        test = self.get_test()
        test.generate_target()
        test.target.to_edge(UP)

        # Time label
        time_labels = VGroup(
            TextMobject("Day 1", ": 4.5 hours"),
            TextMobject("Day 2", ": 4.5 hours"),
        )
        time_labels.scale(1.5)
        day_labels = VGroup()
        hour_labels = VGroup()
        for label, page in zip(time_labels, test.target):
            label.next_to(page, DOWN)
            label[0].save_state()
            label[0].next_to(page, DOWN)
            label[1][1:].set_color(YELLOW)
            day_labels.add(label[0])
            hour_labels.add(label[1])

        # Problem desciptions
        problem_rects = self.get_problem_rects(test.target[0])
        proof_words = VGroup()
        for rect in problem_rects:
            word = TextMobject("Proof")
            word.scale(2)
            word.next_to(rect, RIGHT, buff=3)
            word.set_color(BLUE)
            proof_words.add(word)

        proof_words.space_out_submobjects(2)

        proof_arrows = VGroup()
        for rect, word in zip(problem_rects, proof_words):
            arrow = Arrow(word.get_left(), rect.get_right())
            arrow.match_color(word)
            proof_arrows.add(arrow)

        scores = VGroup()
        for word in proof_words:
            score = VGroup(TexMobject("/"), Integer(0))
            score.arrange(RIGHT, buff=SMALL_BUFF)
            score.scale(2)
            score.next_to(word, RIGHT, buff=1.5)
            scores.add(score)

        # Introduce test
        self.play(
            LaggedStart(
                FadeInFrom(test[0], 2 * RIGHT),
                FadeInFrom(test[1], 2 * LEFT),
                lag_ratio=0.3,
            )
        )
        self.wait()
        self.play(
            MoveToTarget(test, lag_ratio=0.2),
            FadeInFrom(day_labels, UP, lag_ratio=0.2),
        )
        self.wait()
        self.play(
            *map(Restore, day_labels),
            FadeInFrom(hour_labels, LEFT),
        )
        self.wait()

        # Discuss problems
        self.play(
            FadeOut(test[1]),
            FadeOut(time_labels[1]),
            LaggedStartMap(ShowCreation, problem_rects),
            run_time=1,
        )
        self.play(
            LaggedStart(*[
                FadeInFrom(word, LEFT)
                for word in proof_words
            ]),
            LaggedStart(*[
                GrowArrow(arrow)
                for arrow in proof_arrows
            ]),
        )
        self.wait()
        self.play(FadeIn(scores))
        self.play(
            LaggedStart(*[
                ChangeDecimalToValue(score[1], 7)
                for score in scores
            ], lag_ratio=0, rate_func=rush_into)
        )
        self.wait()

    def get_test(self):
        group = Group(
            ImageMobject("imo_2011_p1"),
            ImageMobject("imo_2011_p2"),
        )
        group.set_height(6)
        group.arrange(RIGHT, buff=LARGE_BUFF)
        for page in group:
            rect = SurroundingRectangle(page, buff=0.01)
            rect.set_stroke(WHITE, 1)
            page.add(rect)
            # page.pixel_array[:, :, :3] = 255 - page.pixel_array[:, :, :3]
        return group

    def get_problem_rects(self, page):
        pw = page.get_width()
        rects = VGroup(*[Rectangle() for x in range(3)])
        rects.set_stroke(width=2)
        rects.set_color_by_gradient([BLUE_E, BLUE_C, BLUE_D])

        rects.set_width(pw * 0.75)
        for factor, rect in zip([0.095, 0.16, 0.1], rects):
            rect.set_height(factor * pw, stretch=True)
        rects.arrange(DOWN, buff=0.08)
        rects.move_to(page)
        rects.shift(0.09 * pw * DOWN)
        return rects


class USProcess(IntroduceIMO):
    CONFIG = {
    }

    def construct(self):
        self.add_flag_and_label()
        self.show_tests()
        self.show_imo()

    def add_flag_and_label(self):
        flag = ImageMobject("flags/us")
        flag.set_height(1)
        flag.to_corner(UL)
        label = VGroup(*map(TextMobject, "USA"))
        label.arrange(RIGHT, buff=0.05, aligned_edge=DOWN)
        label.set_width(0.8 * flag.get_width())
        label.next_to(flag, DOWN, buff=0.2 * flag.get_height())

        self.add(flag, label)

        self.flag = flag

    def show_tests(self):
        tests = VGroup(
            self.get_test(
                ["American ", "Mathematics ", "Content"],
                n_questions=25,
                time_string="75 minutes",
                hours=1.25,
                n_students=100000,
            ),
            self.get_test(
                ["American ", "Invitational ", "Math ", "Exam"],
                n_questions=15,
                time_string="3 hours",
                hours=3,
                n_students=3500,
            ),
            self.get_test(
                ["U", "S", "A ", "Math ", "Olympiad"],
                n_questions=6,
                time_string="$2 \\times 4.5$ hours",
                hours=4.5,
                n_students=500,
            ),
            self.get_test(
                ["Mathematical ", "Olympiad ", "Program"],
                n_questions=None,
                time_string="3 weeks",
                hours=None,
                n_students=60
            )
        )
        amc, aime, usamo, mop = tests

        amc.to_corner(UR)
        top_point = amc.get_top()
        last_arrow = VectorizedPoint()
        last_arrow.to_corner(DL)
        next_anims = []

        for test in tests:
            test.move_to(top_point, UP)
            test.shift_onto_screen()
            self.play(
                Write(test.name),
                *next_anims,
                run_time=1,
            )
            self.wait()
            self.animate_name_abbreviation(test)
            self.wait()

            if isinstance(test.nq_label[0], Integer):
                int_mob = test.nq_label[0]
                n = int_mob.get_value()
                int_mob.set_value(0)
                self.play(
                    ChangeDecimalToValue(int_mob, n),
                    FadeIn(test.nq_label[1:])
                )
            else:
                self.play(FadeIn(test.nq_label))

            self.play(
                FadeIn(test.t_label)
            )
            self.wait()

            test.generate_target()
            test.target.scale(0.575)
            test.target.next_to(last_arrow, RIGHT, buff=SMALL_BUFF)
            test.target.shift_onto_screen()

            next_anims = [
                MoveToTarget(test),
                GrowArrow(last_arrow),
            ]
            last_arrow = Vector(0.5 * RIGHT)
            last_arrow.set_color(WHITE)
            last_arrow.next_to(test.target, RIGHT, SMALL_BUFF)
        self.play(*next_anims)

        self.tests = tests

    def show_imo(self):
        tests = self.tests
        logo = ImageMobject("imo_logo")
        logo.set_height(1)
        name = TextMobject("IMO")
        name.scale(2)
        group = Group(logo, name)
        group.arrange(RIGHT)
        group.to_corner(UR)
        group.shift(2 * LEFT)

        students = VGroup(*[
            PiCreature()
            for x in range(6)
        ])
        students.arrange_in_grid(n_cols=3, buff=LARGE_BUFF)
        students.set_height(2)
        students.next_to(group, DOWN)
        colors = it.cycle([RED, LIGHT_GREY, BLUE])
        for student, color in zip(students, colors):
            student.set_color(color)
            student.save_state()
            student.move_to(tests[-1])
            student.fade(1)

        self.play(FadeInFromDown(group))
        self.play(
            LaggedStartMap(
                Restore, students,
                run_time=3,
                lag_ratio=0.3,
            )
        )
        self.play(
            LaggedStart(*[
                ApplyMethod(student.change, "hooray")
                for student in students
            ])
        )
        for x in range(3):
            self.play(Blink(random.choice(students)))
        self.wait()

    #
    def animate_name_abbreviation(self, test):
        name = test.name
        short_name = test.short_name
        short_name.move_to(name, LEFT)
        name.generate_target()
        for p1, p2 in zip(name.target, short_name):
            for letter in p1:
                letter.move_to(p2[0])
                letter.set_opacity(0)
            p1[0].set_opacity(1)
        self.add(test.rect, test.name, test.ns_label)
        self.play(
            FadeIn(test.rect),
            MoveToTarget(name),
            FadeIn(test.ns_label),
        )

        test.remove(name)
        test.add(short_name)
        self.remove(name)
        self.add(short_name)

    def get_test(self, name_parts, n_questions, time_string, hours, n_students):
        T_COLOR = GREEN_B
        Q_COLOR = YELLOW

        name = TextMobject(*name_parts)
        short_name = TextMobject(*[np[0] for np in name_parts])
        if n_questions:
            nq_label = VGroup(
                Integer(n_questions),
                TextMobject("questions")
            )
            nq_label.arrange(RIGHT)
        else:
            nq_label = TextMobject("Lots of training")
        nq_label.set_color(Q_COLOR)

        if time_string:
            t_label = TextMobject(time_string)
            t_label.set_color(T_COLOR)
        else:
            t_label = Integer(0).set_opacity(0)

        clock = Clock()
        clock.hour_hand.set_opacity(0)
        clock.minute_hand.set_opacity(0)
        clock.set_stroke(WHITE, 2)
        if hours:
            sector = Sector(
                start_angle=TAU / 4,
                angle=-TAU * (hours / 12),
                outer_radius=clock.get_width() / 2,
                arc_center=clock.get_center()
            )
            sector.set_fill(T_COLOR, 0.5)
            sector.set_stroke(T_COLOR, 2)
            clock.add(sector)
            if hours == 4.5:
                plus = TexMobject("+").scale(2)
                plus.next_to(clock, RIGHT)
                clock_copy = clock.copy()
                clock_copy.next_to(plus, RIGHT)
                clock.add(plus, clock_copy)
        else:
            clock.set_opacity(0)
        clock.set_height(1)
        clock.next_to(t_label, RIGHT, buff=MED_LARGE_BUFF)
        t_label.add(clock)

        ns_label = TextMobject("$\\sim${:,} students".format(n_students))

        result = VGroup(
            name,
            nq_label,
            t_label,
            ns_label,
        )
        result.arrange(
            DOWN,
            buff=MED_LARGE_BUFF,
            aligned_edge=LEFT,
        )
        rect = SurroundingRectangle(result, buff=MED_SMALL_BUFF)
        rect.set_width(
            result[1:].get_width() + MED_LARGE_BUFF,
            about_edge=LEFT,
            stretch=True,
        )
        rect.set_stroke(WHITE, 2)
        rect.set_fill(BLACK, 1)
        result.add_to_back(rect)

        result.name = name
        result.short_name = short_name
        result.nq_label = nq_label
        result.t_label = t_label
        result.ns_label = ns_label
        result.rect = rect
        result.clock = clock

        return result


class WindmillScene(Scene):
    CONFIG = {
        "dot_config": {
            "fill_color": LIGHT_GREY,
            "radius": 0.05,
            "background_stroke_width": 1,
            "background_stroke_color": BLACK,
        },
        "windmill_style": {
            "stroke_color": RED,
            "stroke_width": 2,
            "background_stroke_width": 3,
            "background_stroke_color": BLACK,
        },
        "windmill_length": FRAME_WIDTH + FRAME_HEIGHT,
        # "windmill_rotation_speed": 0.25,
        "windmill_rotation_speed": 0.5,
    }

    def get_random_point_set(self, n_points=11, width=6, height=6):
        return np.array([
            [
                -width / 2 + np.random.random() * width,
                -height / 2 + np.random.random() * height,
                0
            ]
            for n in range(n_points)
        ])

    def get_dots(self, points):
        return VGroup(*[
            Dot(point, **self.dot_config)
            for point in points
        ])

    def get_windmill(self, points, pivot=None, theta=TAU / 4):
        line = Line(LEFT, RIGHT)
        line.set_length(self.windmill_length)
        line.set_angle(theta)
        line.set_style(**self.windmill_style)

        line.point_set = points

        if pivot is not None:
            line.pivot = pivot
        else:
            line.pivot = points[0]

        line.rot_speed = self.windmill_rotation_speed

        line.add_updater(lambda l: l.move_to(l.pivot))
        return line

    def get_pivot_dot(self, windmill, color=YELLOW):
        pivot_dot = Dot(color=YELLOW)
        pivot_dot.add_updater(lambda d: d.move_to(windmill.pivot))
        return pivot_dot

    def next_pivot_and_angle(self, windmill):
        curr_angle = windmill.get_angle()
        pivot = windmill.pivot
        non_pivots = list(filter(
            lambda p: not np.all(p == pivot),
            windmill.point_set
        ))

        angles = np.array([
            -(angle_of_vector(point - pivot) - curr_angle) % PI
            for point in non_pivots
        ])
        angles[angles < 1e-6] = np.inf
        index = np.argmin(angles)
        return non_pivots[index], angles[index]

    def rotate_to_next_pivot(self, windmill, max_time=None, added_anims=None):
        """
        Returns animations to play following the contact
        """
        new_pivot, angle = self.next_pivot_and_angle(windmill)
        change_pivot_at_end = True

        if added_anims is None:
            added_anims = []

        run_time = angle / windmill.rot_speed
        if max_time is not None and run_time > max_time:
            ratio = max_time / run_time
            rate_func = (lambda t: ratio * t)
            run_time = max_time
            change_pivot_at_end = False
        else:
            rate_func = linear

        self.play(
            Rotate(
                windmill,
                -angle,
                run_time=run_time,
                rate_func=rate_func,
            ),
            *added_anims,
        )

        if change_pivot_at_end:
            windmill.pivot = new_pivot

    def let_windmill_run(self, windmill, time):
        start_time = self.get_time()
        end_time = start_time + time
        curr_time = start_time
        while curr_time < end_time:
            self.rotate_to_next_pivot(
                windmill,
                max_time=(end_time - curr_time)
            )
            curr_time = self.get_time()


class WindmillTest(WindmillScene):
    def construct(self):
        points = self.get_random_point_set()
        # points = np.array(list(sorted(points, key=lambda p: p[0])))

        dots = self.get_dots(points)
        windmill = self.get_windmill(points)
        pivot_dot = self.get_pivot_dot(windmill)

        self.add(windmill)
        self.add(dots)
        self.add(pivot_dot)

        self.let_windmill_run(windmill, 10)
