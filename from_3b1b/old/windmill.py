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
        "year": 2019,
        "n_flag_rows": 10,
        "reorganize_students": True,
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
            n_rows=self.n_flag_rows,
            buff=SMALL_BUFF,
        )
        # student_groups.target[-9:].align_to(student_groups.target[0], LEFT)
        student_groups.target.match_height(flags)
        student_groups.target.match_y(flags)
        student_groups.target.to_edge(RIGHT, buff=0.25)

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
        if self.reorganize_students:
            self.play(
                MoveToTarget(student_groups),
                flags.space_out_submobjects, 0.75,
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
                    FadeOut(flag, DOWN)
                    for flag in random_flags
                ],
                lag_ratio=0.05,
                run_time=1.5
            ),
            MoveToTarget(us_flag),
            student_groups[1:].fade, 0.9,
        )
        self.wait()

    #
    def get_students(self, flag):
        dots = VGroup(*[Dot() for x in range(6)])
        dots.arrange_in_grid(n_cols=2, buff=SMALL_BUFF)
        dots.match_height(flag)
        dots.next_to(flag, RIGHT, SMALL_BUFF)
        dots[flag.n_students:].set_opacity(0)

        if isinstance(flag, ImageMobject):
            rgba = random.choice(random.choice(flag.pixel_array))
            if np.all(rgba < 100):
                rgba = interpolate(rgba, 256 * np.ones(len(rgba)), 0.5)
            color = rgba_to_color(rgba / 256)
        else:
            color = random_bright_color()
        dots.set_color(color)
        dots.set_stroke(WHITE, 1, background=True)

        return dots

    def get_flags(self):
        year = self.year
        file = "{}_imo_countries.json".format(year)
        with open(os.path.join("assets", file)) as fp:
            countries_with_counts = json.load(fp)
        with open(os.path.join("assets", "country_codes.json")) as fp:
            country_codes = json.load(fp)
            country_to_code2 = dict([
                (country.lower(), code2.lower())
                for country, code2, code3 in country_codes
            ])
            country_to_code3 = dict([
                (country.lower(), code3.lower())
                for country, code2, code3 in country_codes
            ])

        images = Group()
        for country, count in countries_with_counts:
            country = country.lower()

            alt_names = [
                ("united states of america", "united states"),
                ("people's republic of china", "china"),
                ("macau", "macao"),
                ("syria", "syrian arab republic"),
                ("north macedonia", "macedonia, the former yugoslav republic of"),
                ("tanzania", "united republic of tanzania"),
                ("vietnam", "viet nam"),
                ("ivory coast", "cote d'ivoire")
            ]
            for n1, n2 in alt_names:
                if country == n1:
                    country = n2

            if country not in country_to_code2:
                print("Can't find {}".format(country))
                continue
            short_code = country_to_code2[country]
            try:
                image = ImageMobject(os.path.join("flags", short_code))
                image.set_width(1)
                label = VGroup(*[
                    TextMobject(l)
                    for l in country_to_code3[country].upper()
                ])
                label.arrange(RIGHT, buff=0.05, aligned_edge=DOWN)
                label.set_height(0.25)
                if not self.use_real_images:
                    rect = SurroundingRectangle(image, buff=0)
                    rect.set_stroke(WHITE, 1)
                    image = rect
                image.label = label
                image.n_students = count
                images.add(image)
            except OSError:
                print("Failed on {}".format(country))

        n_rows = self.n_flag_rows
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


class ShowTinyTao(IntroduceIMO):
    CONFIG = {
        "reorganize_students": False,
    }

    def construct(self):
        self.force_skipping()
        self.add_title()
        self.show_flags()
        self.show_students()
        self.revert_to_original_skipping_status()

        image = ImageMobject("TerryTaoIMO")
        label = TextMobject("Terence Tao at 12")
        label.match_width(image)
        label.next_to(image, DOWN, SMALL_BUFF)
        image.add(label)

        ausie = self.flags[17]
        image.replace(ausie)
        image.set_opacity(0)

        self.play(image.set_opacity, 1)
        self.play(
            image.set_height, 5,
            image.to_corner, DR, {"buff": MED_SMALL_BUFF},
        )
        self.wait()
        self.play(FadeOut(image))


class FootnoteToIMOIntro(Scene):
    def construct(self):
        words = TextMobject("$^*$Based on data from 2019 test")
        self.play(FadeIn(words, UP))
        self.wait()


class ShowTest(Scene):
    def construct(self):
        self.introduce_test()

    def introduce_test(self):
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

        # Problem descriptions
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
            score = VGroup(Integer(0), TexMobject("/"), Integer(7))
            score.arrange(RIGHT, buff=SMALL_BUFF)
            score.scale(2)
            score.move_to(word)
            score.to_edge(RIGHT)
            scores.add(score)
            score[0].add_updater(lambda m: m.set_color(
                interpolate_color(RED, GREEN, m.get_value() / 7)
            ))

        # Introduce test
        self.play(
            LaggedStart(
                FadeIn(test[0], 2 * RIGHT),
                FadeIn(test[1], 2 * LEFT),
                lag_ratio=0.3,
            )
        )
        self.wait()
        self.play(
            MoveToTarget(test, lag_ratio=0.2),
            FadeIn(day_labels, UP, lag_ratio=0.2),
        )
        self.wait()
        self.play(
            *map(Restore, day_labels),
            FadeIn(hour_labels, LEFT),
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
                FadeIn(word, LEFT)
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
                ChangeDecimalToValue(score[0], 7)
                for score in scores
            ], lag_ratio=0.2, rate_func=rush_into)
        )
        self.wait()

        self.scores = scores
        self.proof_arrows = proof_arrows
        self.proof_words = proof_words
        self.problem_rects = problem_rects
        self.test = test
        self.time_labels = time_labels

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


class USProcessAlt(IntroduceIMO):
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
                ["American ", "Mathematics ", "Contest"],
                n_questions=25,
                time_string="75 minutes",
                hours=1.25,
                n_students=250000,
            ),
            self.get_test(
                ["American ", "Invitational ", "Math ", "Exam"],
                n_questions=15,
                time_string="3 hours",
                hours=3,
                n_students=12000,
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
        arrows = VGroup()

        amc.to_corner(UR)
        top_point = amc.get_top()
        last_arrow = VectorizedPoint()
        last_arrow.to_corner(DL)
        next_anims = []

        self.force_skipping()
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
            arrows.add(last_arrow)
        self.play(*next_anims)

        self.revert_to_original_skipping_status()
        self.play(
            LaggedStartMap(
                FadeInFrom, tests,
                lambda m: (m, LEFT),
            ),
            LaggedStartMap(
                GrowArrow, arrows[:-1]
            ),
            lag_ratio=0.4,
        )
        self.wait()

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

        self.play(
            FadeInFromDown(group),
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


class Describe2011IMO(IntroduceIMO):
    CONFIG = {
        "year": 2011,
        "use_real_images": True,
        "n_flag_rows": 10,
        "student_data": [
            [1, "Lisa Sauermann", "de", [7, 7, 7, 7, 7, 7]],
            [2, "Jeck Lim", "sg", [7, 5, 7, 7, 7, 7]],
            [3, "Lin Chen", "cn", [7, 3, 7, 7, 7, 7]],
            [4, "Jun Jie Joseph Kuan", "sg", [7, 7, 7, 7, 7, 1]],
            [4, "David Yang", "us", [7, 7, 7, 7, 7, 1]],
            [6, "Jie Jun Ang", "sg", [7, 7, 7, 7, 7, 0]],
            [6, "Kensuke Yoshida", "jp", [7, 6, 7, 7, 7, 1]],
            [6, "Raul Sarmiento", "pe", [7, 7, 7, 7, 7, 0]],
            [6, "Nipun Pitimanaaree", "th", [7, 7, 7, 7, 7, 0]],
        ],
    }

    def construct(self):
        self.add_title()
        self.add_flags_and_students()
        self.comment_on_primality()
        self.show_top_three_scorers()

    def add_title(self):
        year = TexMobject("2011")
        logo = ImageMobject("imo_logo")
        imo = TextMobject("IMO")
        group = Group(year, logo, imo)
        group.scale(1.25)
        logo.set_height(1)
        group.arrange(RIGHT)
        group.to_corner(UR, buff=MED_SMALL_BUFF)
        group.shift(LEFT)

        self.add(group)
        self.play(FadeIn(year, RIGHT))

        self.title = group

    def add_flags_and_students(self):
        flags = self.get_flags()
        flags.space_out_submobjects(0.8)
        sf = 0.8
        flags.stretch(sf, 0)
        for flag in flags:
            flag.stretch(1 / sf, 0)
        flags.set_height(5)
        flags.to_corner(DL)

        student_groups = VGroup(*[
            self.get_students(flag)
            for flag in flags
        ])
        student_groups.arrange_in_grid(
            n_rows=self.n_flag_rows,
            buff=SMALL_BUFF,
        )
        student_groups[-1].align_to(student_groups, LEFT)
        student_groups.set_height(6)
        student_groups.next_to(self.title, DOWN)
        flags.align_to(student_groups, UP)

        all_students = VGroup(*it.chain(*[
            [
                student
                for student in group
                if student.get_fill_opacity() > 0
            ]
            for group in student_groups
        ]))

        # Counters
        student_counter = VGroup(
            Integer(0),
            TextMobject("Participants"),
        )
        student_counter.set = all_students
        student_counter.next_to(self.title, LEFT, MED_LARGE_BUFF)
        student_counter.right_edge = student_counter.get_right()

        def update_counter(counter):
            counter[0].set_value(len(counter.set))
            counter.arrange(RIGHT)
            counter[0].align_to(counter[1][0][0], DOWN)
            counter.move_to(counter.right_edge, RIGHT)

        student_counter.add_updater(update_counter)

        flag_counter = VGroup(
            Integer(0),
            TextMobject("Countries")
        )
        flag_counter.set = flags
        flag_counter.next_to(student_counter, LEFT, buff=0.75)
        flag_counter.align_to(student_counter[0], DOWN)
        flag_counter.right_edge = flag_counter.get_right()
        flag_counter.add_updater(update_counter)

        self.add(student_counter)
        self.play(
            ShowIncreasingSubsets(all_students),
            run_time=3,
        )
        self.wait()
        self.add(flag_counter)
        self.play(
            ShowIncreasingSubsets(flags),
            run_time=3,
        )
        self.wait()

        self.student_counter = student_counter
        self.flag_counter = flag_counter
        self.all_students = all_students
        self.student_groups = student_groups
        self.flags = flags

    def comment_on_primality(self):
        full_rect = FullScreenFadeRectangle(opacity=0.9)
        numbers = VGroup(
            self.title[0],
            self.student_counter[0],
            self.flag_counter[0],
        )
        lines = VGroup(*[
            Line().match_width(number).next_to(number, DOWN, SMALL_BUFF)
            for number in numbers
        ])
        lines.set_stroke(TEAL, 2)

        randy = Randolph()
        randy.to_corner(DL)
        randy.look_at(numbers)

        words = VGroup(*[
            TextMobject("Prime").next_to(line, DOWN)
            for line in reversed(lines)
        ])
        words.match_color(lines)

        self.add(full_rect, numbers)
        self.play(
            FadeIn(full_rect),
            randy.change, "sassy",
            VFadeIn(randy),
        )
        self.play(
            ShowCreation(lines),
            randy.change, "pondering",
        )
        self.play(Blink(randy))
        self.play(
            randy.change, "thinking",
            LaggedStart(*[
                FadeIn(word, UP)
                for word in words
            ], run_time=3, lag_ratio=0.5)
        )
        self.play(Blink(randy))
        self.play(
            FadeOut(randy),
            FadeOut(words),
        )
        self.play(FadeOut(full_rect), FadeOut(lines))

    def show_top_three_scorers(self):
        student_groups = self.student_groups
        all_students = self.all_students
        flags = self.flags
        student_counter = self.student_counter
        flag_counter = self.flag_counter

        student = student_groups[10][0]
        flag = flags[10]

        students_to_fade = VGroup(*filter(
            lambda s: s is not student,
            all_students
        ))
        flags_to_fade = Group(*filter(
            lambda s: s is not flag,
            flags
        ))

        grid = self.get_score_grid()
        grid.shift(3 * DOWN)
        title_row = grid.rows[0]
        top_row = grid.rows[1]

        self.play(
            LaggedStartMap(FadeOutAndShiftDown, students_to_fade),
            LaggedStartMap(FadeOutAndShiftDown, flags_to_fade),
            ChangeDecimalToValue(student_counter[0], 1),
            FadeOut(flag_counter),
            run_time=2
        )
        student_counter[1][0][-1].fade(1)
        self.play(
            Write(top_row[0]),
            ReplacementTransform(student, top_row[1][1]),
            flag.replace, top_row[1][0],
        )
        self.remove(flag)
        self.add(top_row[1])
        self.play(
            LaggedStartMap(FadeIn, title_row[2:]),
            LaggedStartMap(FadeIn, top_row[2:]),
        )
        self.wait()
        self.play(
            LaggedStart(*[
                FadeIn(row, UP)
                for row in grid.rows[2:4]
            ]),
            LaggedStart(*[
                ShowCreation(line)
                for line in grid.h_lines[:2]
            ]),
            lag_ratio=0.5,
        )
        self.wait()
        self.play(
            ShowCreationThenFadeAround(
                Group(title_row[3], grid.rows[3][3]),
            )
        )
        self.wait()
        student_counter.clear_updaters()
        self.play(
            FadeOut(self.title, UP),
            FadeOut(student_counter, UP),
            grid.rows[:4].shift, 3 * UP,
            grid.h_lines[:3].shift, 3 * UP,
        )
        remaining_rows = grid.rows[4:]
        remaining_lines = grid.h_lines[3:]
        Group(remaining_rows, remaining_lines).shift(3 * UP)
        self.play(
            LaggedStartMap(
                FadeInFrom, remaining_rows,
                lambda m: (m, UP),
            ),
            LaggedStartMap(ShowCreation, remaining_lines),
            lag_ratio=0.3,
            run_time=2,
        )
        self.wait()

    def get_score_grid(self):
        data = self.student_data

        ranks = VGroup(*[
            Integer(row[0])
            for row in data
        ])

        # Combine students with flags
        students = VGroup(*[
            TextMobject(row[1])
            for row in data
        ])
        flags = Group(*[
            ImageMobject("flags/{}.png".format(row[2])).set_height(0.3)
            for row in data
        ])
        students = Group(*[
            Group(flag.next_to(student, LEFT, buff=0.2), student)
            for flag, student in zip(flags, students)
        ])

        score_rows = VGroup(*[
            VGroup(*map(Integer, row[3]))
            for row in data
        ])
        colors = color_gradient([RED, YELLOW, GREEN], 8)
        for score_row in score_rows:
            for score in score_row:
                score.set_color(colors[score.get_value()])

        titles = VGroup(*[
            VectorizedPoint(),
            VectorizedPoint(),
            *[
                TextMobject("P{}".format(i))
                for i in range(1, 7)
            ]
        ])
        titles.arrange(RIGHT, buff=MED_LARGE_BUFF)
        titles[2:].shift(students.get_width() * RIGHT)
        rows = Group(titles, *[
            Group(rank, student, *score_row)
            for rank, flag, student, score_row in zip(
                ranks, flags, students, score_rows
            )
        ])
        rows.arrange(DOWN)
        rows.to_edge(UP)
        for row in rows:
            for i, e1, e2 in zip(it.count(), titles, row):
                if i < 2:
                    e2.align_to(e1, LEFT)
                else:
                    e2.match_x(e1)
        ranks.next_to(students, LEFT)

        h_lines = VGroup()
        for r1, r2 in zip(rows[1:], rows[2:]):
            line = Line()
            line.set_stroke(WHITE, 0.5)
            line.match_width(r2)
            line.move_to(midpoint(r1.get_bottom(), r2.get_top()))
            line.align_to(r2, LEFT)
            h_lines.add(line)

        grid = Group(rows, h_lines)
        grid.rows = rows
        grid.h_lines = h_lines

        return grid


class AskWhatsOnTest(ShowTest, MovingCameraScene):
    def construct(self):
        self.force_skipping()
        self.introduce_test()
        self.revert_to_original_skipping_status()

        self.ask_about_questions()

    def ask_about_questions(self):
        scores = self.scores
        arrows = self.proof_arrows
        proof_words = self.proof_words

        question = TextMobject("What kind \\\\ of problems?")
        question.scale(1.5)
        question.move_to(proof_words, LEFT)

        research = TextMobject("Research-lite")
        research.scale(1.5)
        research.move_to(question, LEFT)
        research.shift(MED_SMALL_BUFF * RIGHT)
        research.set_color(BLUE)

        arrows.generate_target()
        for arrow in arrows.target:
            end = arrow.get_end()
            start = arrow.get_start()
            arrow.put_start_and_end_on(
                interpolate(question.get_left(), start, 0.1),
                end
            )

        self.play(
            FadeOut(scores),
            FadeOut(proof_words),
            MoveToTarget(arrows),
            Write(question),
        )
        self.wait()
        self.play(
            FadeIn(research, DOWN),
            question.shift, 2 * UP,
        )
        self.wait()

        # Experience
        randy = Randolph(height=2)
        randy.move_to(research.get_corner(UL), DL)
        randy.shift(SMALL_BUFF * RIGHT)
        clock = Clock()
        clock.set_height(1)
        clock.next_to(randy, UR)

        self.play(
            FadeOut(question),
            FadeIn(randy),
            FadeInFromDown(clock),
        )
        self.play(
            randy.change, "pondering",
            ClockPassesTime(clock, run_time=5, hours_passed=5),
        )
        self.play(
            ClockPassesTime(clock, run_time=2, hours_passed=2),
            VFadeOut(clock),
            Blink(randy),
            VFadeOut(randy),
            LaggedStartMap(
                FadeOut,
                VGroup(
                    research,
                    *arrows,
                    *self.problem_rects,
                    self.time_labels[0]
                )
            ),
        )

        # Second part
        big_rect = FullScreenFadeRectangle()
        lil_rect = self.problem_rects[1].copy()
        lil_rect.reverse_points()
        big_rect.append_vectorized_mobject(lil_rect)
        frame = self.camera_frame
        frame.generate_target()
        frame.target.scale(0.35)
        frame.target.move_to(lil_rect)

        self.play(
            FadeInFromDown(self.test[1]),
        )
        self.wait()
        self.play(
            FadeIn(big_rect),
            MoveToTarget(frame, run_time=6),
        )
        self.wait()


class ReadQuestions(Scene):
    def construct(self):
        background = ImageMobject("AskWhatsOnTest_final_image")
        background.set_height(FRAME_HEIGHT)
        self.add(background)

        lines = SVGMobject("imo_2011_2_underline-01")
        lines.set_width(FRAME_WIDTH - 1)
        lines.move_to(0.1 * DOWN)
        lines.set_stroke(TEAL, 3)

        clump_sizes = [1, 2, 3, 2, 1, 2]
        partial_sums = list(np.cumsum(clump_sizes))
        clumps = VGroup(*[
            lines[i:j]
            for i, j in zip(
                [0] + partial_sums,
                partial_sums,
            )
        ])

        faders = []
        for clump in clumps:
            rects = VGroup()
            for line in clump:
                rect = Rectangle()
                rect.set_stroke(width=0)
                rect.set_fill(TEAL, 0.25)
                rect.set_width(line.get_width() + SMALL_BUFF)
                rect.set_height(0.35, stretch=True)
                rect.move_to(line, DOWN)
                rects.add(rect)

            self.play(
                ShowCreation(clump, run_time=2),
                FadeIn(rects),
                *faders,
            )
            self.wait()
            faders = [
                FadeOut(clump),
                FadeOut(rects),
            ]
        self.play(*faders)
        self.wait()


# Windmill scenes

class WindmillScene(Scene):
    CONFIG = {
        "dot_config": {
            "fill_color": LIGHT_GREY,
            "radius": 0.05,
            "background_stroke_width": 2,
            "background_stroke_color": BLACK,
        },
        "windmill_style": {
            "stroke_color": RED,
            "stroke_width": 2,
            "background_stroke_width": 3,
            "background_stroke_color": BLACK,
        },
        "windmill_length": 2 * FRAME_WIDTH,
        "windmill_rotation_speed": 0.25,
        # "windmill_rotation_speed": 0.5,
        # "hit_sound": "pen_click.wav",
        "hit_sound": "pen_click.wav",
        "leave_shadows": False,
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

    def get_windmill(self, points, pivot=None, angle=TAU / 4):
        line = Line(LEFT, RIGHT)
        line.set_length(self.windmill_length)
        line.set_angle(angle)
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

    def start_leaving_shadows(self):
        self.leave_shadows = True
        self.add(self.get_windmill_shadows())

    def get_windmill_shadows(self):
        if not hasattr(self, "windmill_shadows"):
            self.windmill_shadows = VGroup()
        return self.windmill_shadows

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

        # Edge case for 2 points
        tiny_indices = angles < 1e-6
        if np.all(tiny_indices):
            return non_pivots[0], PI

        angles[tiny_indices] = np.inf
        index = np.argmin(angles)
        return non_pivots[index], angles[index]

    def rotate_to_next_pivot(self, windmill, max_time=None, added_anims=None):
        """
        Returns animations to play following the contact, and total run time
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

        for anim in added_anims:
            if anim.run_time > run_time:
                anim.run_time = run_time

        self.play(
            Rotate(
                windmill,
                -angle,
                rate_func=rate_func,
                run_time=run_time,
            ),
            *added_anims,
        )

        if change_pivot_at_end:
            self.handle_pivot_change(windmill, new_pivot)

        # Return animations to play
        return [self.get_hit_flash(new_pivot)], run_time

    def handle_pivot_change(self, windmill, new_pivot):
        windmill.pivot = new_pivot
        self.add_sound(self.hit_sound)
        if self.leave_shadows:
            new_shadow = windmill.copy()
            new_shadow.fade(0.5)
            new_shadow.set_stroke(width=1)
            new_shadow.clear_updaters()
            shadows = self.get_windmill_shadows()
            shadows.add(new_shadow)

    def let_windmill_run(self, windmill, time):
        # start_time = self.get_time()
        # end_time = start_time + time
        # curr_time = start_time
        anims_from_last_hit = []
        while time > 0:
            anims_from_last_hit, last_run_time = self.rotate_to_next_pivot(
                windmill,
                max_time=time,
                added_anims=anims_from_last_hit,
            )
            time -= last_run_time
            # curr_time = self.get_time()

    def add_dot_color_updater(self, dots, windmill, **kwargs):
        for dot in dots:
            dot.add_updater(lambda d: self.update_dot_color(
                d, windmill, **kwargs
            ))

    def update_dot_color(self, dot, windmill, color1=BLUE, color2=GREY_BROWN):
        perp = rotate_vector(windmill.get_vector(), TAU / 4)
        dot_product = np.dot(perp, dot.get_center() - windmill.pivot)
        if dot_product > 0:
            dot.set_color(color1)
        # elif dot_product < 0:
        else:
            dot.set_color(color2)
        # else:
        #     dot.set_color(WHITE)

        dot.set_stroke(
            # interpolate_color(dot.get_fill_color(), WHITE, 0.5),
            WHITE,
            width=2,
            background=True
        )

    def get_hit_flash(self, point):
        flash = Flash(
            point,
            line_length=0.1,
            flash_radius=0.2,
            run_time=0.5,
            remover=True,
        )
        flash_mob = flash.mobject
        for submob in flash_mob:
            submob.reverse_points()
        return Uncreate(
            flash.mobject,
            run_time=0.25,
            lag_ratio=0,
        )

    def get_pivot_counters(self, windmill, counter_height=0.25, buff=0.2, color=WHITE):
        points = windmill.point_set
        counters = VGroup()
        for point in points:
            counter = Integer(0)
            counter.set_color(color)
            counter.set_height(counter_height)
            counter.next_to(point, UP, buff=buff)
            counter.point = point
            counter.windmill = windmill
            counter.is_pivot = False
            counter.add_updater(self.update_counter)
            counters.add(counter)
        return counters

    def update_counter(self, counter):
        dist = get_norm(counter.point - counter.windmill.pivot)
        counter.will_be_pivot = (dist < 1e-6)
        if (not counter.is_pivot) and counter.will_be_pivot:
            counter.increment_value()
        counter.is_pivot = counter.will_be_pivot

    def get_orientation_arrows(self, windmill, n_tips=20):
        tips = VGroup(*[
            ArrowTip(start_angle=0)
            for x in range(n_tips)
        ])
        tips.stretch(0.75, 1)
        tips.scale(0.5)

        tips.rotate(windmill.get_angle())
        tips.match_color(windmill)
        tips.set_stroke(BLACK, 1, background=True)
        for tip, a in zip(tips, np.linspace(0, 1, n_tips)):
            tip.shift(
                windmill.point_from_proportion(a) - tip.points[0]
            )
        return tips

    def get_left_right_colorings(self, windmill, opacity=0.3):
        rects = VGroup(VMobject(), VMobject())
        rects.const_opacity = opacity

        def update_regions(rects):
            p0, p1 = windmill.get_start_and_end()
            v = p1 - p0
            vl = rotate_vector(v, 90 * DEGREES)
            vr = rotate_vector(v, -90 * DEGREES)
            p2 = p1 + vl
            p3 = p0 + vl
            p4 = p1 + vr
            p5 = p0 + vr
            rects[0].set_points_as_corners([p0, p1, p2, p3])
            rects[1].set_points_as_corners([p0, p1, p4, p5])
            rects.set_stroke(width=0)
            rects[0].set_fill(BLUE, rects.const_opacity)
            rects[1].set_fill(GREY_BROWN, rects.const_opacity)
            return rects

        rects.add_updater(update_regions)
        return rects


class IntroduceWindmill(WindmillScene):
    CONFIG = {
        "final_run_time": 60,
        "windmill_rotation_speed": 0.5,
    }

    def construct(self):
        self.add_points()
        self.exclude_colinear()
        self.add_line()
        self.switch_pivots()
        self.continue_and_count()

    def add_points(self):
        points = self.get_random_point_set(8)
        points[-1] = midpoint(points[0], points[1])
        dots = self.get_dots(points)
        dots.set_color(YELLOW)
        dots.set_height(3)
        braces = VGroup(
            Brace(dots, LEFT),
            Brace(dots, RIGHT),
        )

        group = VGroup(dots, braces)
        group.set_height(4)
        group.center().to_edge(DOWN)

        S, eq = S_eq = TexMobject("\\mathcal{S}", "=")
        S_eq.scale(2)
        S_eq.next_to(braces, LEFT)

        self.play(
            FadeIn(S_eq),
            FadeIn(braces[0], RIGHT),
            FadeIn(braces[1], LEFT),
        )
        self.play(
            LaggedStartMap(FadeInFromLarge, dots)
        )
        self.wait()
        self.play(
            S.next_to, dots, LEFT,
            {"buff": 2, "aligned_edge": UP},
            FadeOut(braces),
            FadeOut(eq),
        )

        self.S_label = S
        self.dots = dots

    def exclude_colinear(self):
        dots = self.dots

        line = Line(dots[0].get_center(), dots[1].get_center())
        line.scale(1.5)
        line.set_stroke(WHITE)

        words = TextMobject("Not allowed!")
        words.scale(2)
        words.set_color(RED)
        words.next_to(line.get_center(), RIGHT)

        self.add(line, dots)
        self.play(
            ShowCreation(line),
            FadeIn(words, LEFT),
            dots[-1].set_color, RED,
        )
        self.wait()
        self.play(
            FadeOut(line),
            FadeOut(words),
        )
        self.play(
            FadeOut(
                dots[-1], 3 * RIGHT,
                path_arc=-PI / 4,
                rate_func=running_start,
            )
        )
        dots.remove(dots[-1])
        self.wait()

    def add_line(self):
        dots = self.dots
        points = np.array(list(map(Mobject.get_center, dots)))
        p0 = points[0]

        windmill = self.get_windmill(points, p0, angle=60 * DEGREES)
        pivot_dot = self.get_pivot_dot(windmill)

        l_label = TexMobject("\\ell")
        l_label.scale(1.5)
        p_label = TexMobject("P")

        l_label.next_to(
            p0 + 2 * normalize(windmill.get_vector()),
            RIGHT,
        )
        l_label.match_color(windmill)
        p_label.next_to(p0, RIGHT)
        p_label.match_color(pivot_dot)

        arcs = VGroup(*[
            Arc(angle=-45 * DEGREES, radius=1.5)
            for x in range(2)
        ])
        arcs[1].rotate(PI, about_point=ORIGIN)
        for arc in arcs:
            arc.add_tip(tip_length=0.2)
        arcs.rotate(windmill.get_angle())
        arcs.shift(p0)

        self.add(windmill, dots)
        self.play(
            GrowFromCenter(windmill),
            FadeIn(l_label, DL),
        )
        self.wait()
        self.play(
            TransformFromCopy(pivot_dot, p_label),
            GrowFromCenter(pivot_dot),
            dots.set_color, WHITE,
        )
        self.wait()
        self.play(*map(ShowCreation, arcs))
        self.wait()

        # Rotate to next pivot
        next_pivot, angle = self.next_pivot_and_angle(windmill)
        self.play(
            *[
                Rotate(
                    mob, -0.99 * angle,
                    about_point=p0,
                    rate_func=linear,
                )
                for mob in [windmill, arcs, l_label]
            ],
            VFadeOut(l_label),
        )
        self.add_sound(self.hit_sound)
        self.play(
            self.get_hit_flash(next_pivot)
        )
        self.wait()

        self.pivot2 = next_pivot
        self.pivot_dot = pivot_dot
        self.windmill = windmill
        self.p_label = p_label
        self.arcs = arcs

    def switch_pivots(self):
        windmill = self.windmill
        pivot2 = self.pivot2
        p_label = self.p_label
        arcs = self.arcs

        q_label = TexMobject("Q")
        q_label.set_color(YELLOW)
        q_label.next_to(pivot2, DR, buff=SMALL_BUFF)

        self.rotate_to_next_pivot(windmill)
        self.play(
            FadeIn(q_label, LEFT),
            FadeOut(p_label),
            FadeOut(arcs),
        )
        self.wait()
        flashes, run_time = self.rotate_to_next_pivot(windmill)
        self.remove(q_label)
        self.add_sound(self.hit_sound)
        self.play(*flashes)
        self.wait()
        self.let_windmill_run(windmill, 10)

    def continue_and_count(self):
        windmill = self.windmill
        pivot_dot = self.pivot_dot

        p_label = TexMobject("P")
        p_label.match_color(pivot_dot)
        p_label.next_to(pivot_dot, DR, buff=0)

        l_label = TexMobject("\\ell")
        l_label.scale(1.5)
        l_label.match_color(windmill)
        l_label.next_to(
            windmill.get_center() + -3 * normalize(windmill.get_vector()),
            DR,
            buff=SMALL_BUFF,
        )

        self.play(FadeIn(p_label, UL))
        self.play(FadeIn(l_label, LEFT))
        self.wait()

        self.add(
            windmill.copy().fade(0.75),
            pivot_dot.copy().fade(0.75),
        )
        pivot_counters = self.get_pivot_counters(windmill)
        self.add(pivot_counters)
        windmill.rot_speed *= 2

        self.let_windmill_run(windmill, self.final_run_time)


class ContrastToOtherOlympiadProblems(AskWhatsOnTest):
    def construct(self):
        self.zoom_to_other_questions()

    def zoom_to_other_questions(self):
        test = self.get_test()
        rects = self.get_all_rects()

        big_rects = VGroup()
        for rect in rects:
            big_rect = FullScreenFadeRectangle()
            rect.reverse_points()
            big_rect.append_vectorized_mobject(rect)
            big_rects.add(big_rect)

        frame = self.camera_frame
        frame.generate_target()
        frame.target.scale(0.35)
        frame.target.move_to(rects[1])
        big_rect = big_rects[1].copy()

        self.add(test)
        self.play(
            FadeIn(big_rect),
            MoveToTarget(frame, run_time=3),
        )
        self.wait()
        for i in [2, 0, 3, 5]:
            self.play(
                frame.move_to, rects[i],
                Transform(big_rect, big_rects[i])
            )
            self.wait()

    def get_all_rects(self, test):
        rects = self.get_problem_rects(test[0])
        new_rects = VGroup(rects[1], rects[0], rects[2]).copy()
        new_rects[0].stretch(0.85, 1)
        new_rects[1].stretch(0.8, 1)
        new_rects[2].stretch(0.8, 1)
        new_rects.arrange(DOWN, buff=0.08)
        new_rects.move_to(test[1])
        new_rects.align_to(rects, UP)
        rects.add(*new_rects)
        return rects


class WindmillExample30Points(WindmillScene):
    CONFIG = {
        "n_points": 30,
        "random_seed": 0,
        "run_time": 60,
        "counter_config": {
            "counter_height": 0.15,
            "buff": 0.1,
        },
    }

    def construct(self):
        points = self.get_random_point_set(self.n_points)
        points[:, 0] *= 1.5
        sorted_points = sorted(list(points), key=lambda p: p[1])
        sorted_points[4] += RIGHT

        dots = self.get_dots(points)
        windmill = self.get_windmill(points, sorted_points[5], angle=PI / 4)
        pivot_dot = self.get_pivot_dot(windmill)
        # self.add_dot_color_updater(dots, windmill)

        self.add(windmill)
        self.add(dots)
        self.add(pivot_dot)
        self.add(self.get_pivot_counters(
            windmill, **self.counter_config
        ))

        self.let_windmill_run(windmill, self.run_time)


class WindmillExample15Points(WindmillExample30Points):
    CONFIG = {
        "n_points": 15,
        "run_time": 60,
        "random_seed": 2,
        "counter_config": {
            "counter_height": 0.25,
            "buff": 0.1,
        },
    }


class TheQuestion(Scene):
    def construct(self):
        words = TextMobject(
            "Will each point be hit infinitely many times?"
        )
        words.set_width(FRAME_WIDTH - 1)
        words.to_edge(UP)

        self.add(words)


class SpiritOfIMO(PiCreatureScene):
    def construct(self):
        randy = self.pi_creature

        problems = VGroup(*[
            TextMobject("P{})".format(i))
            for i in range(1, 7)
        ])
        problems.arrange_in_grid(n_cols=2, buff=LARGE_BUFF)
        problems.scale(1.5)
        problems[3:].shift(1.5 * RIGHT)
        problems.to_corner(UR, buff=LARGE_BUFF)
        problems.shift(2 * LEFT)

        light_bulbs = VGroup()
        lights = VGroup()
        for problem in problems:
            light_bulb = Lightbulb()
            light_bulb.base = light_bulb[:3]
            light_bulb.light = light_bulb[3:]
            light_bulb.set_height(1)
            light_bulb.next_to(problem, RIGHT)
            light_bulbs.add(light_bulb)

            light = self.get_light(light_bulb.get_center())
            lights.add(light)

        self.play(
            LaggedStartMap(FadeInFromDown, problems)
        )
        self.play(
            LaggedStartMap(
                FadeIn, light_bulbs,
                run_time=1,
            ),
            LaggedStartMap(
                LaggedStartMap, lights,
                lambda l: (VFadeInThenOut, l),
                run_time=3
            ),
            randy.change, "thinking"
        )
        self.wait()
        self.pi_creature_thinks(
            "Oh, I've\\\\seen this...",
            target_mode="surprised",
        )
        self.wait(3)

    def get_light(self, point):
        radii = np.arange(0, 5, 0.1)
        result = VGroup(*[
            Annulus(
                inner_radius=r1,
                outer_radius=r2,
                arc_center=point,
                fill_opacity=(1 / (r1 + 1)**2),
                fill_color=YELLOW,
            )
            for r1, r2 in zip(radii[1:], radii[2:])
        ])
        return result


# TODO
class HowToPrepareForThis(Scene):
    def construct(self):
        pass


class HarderThanExpected(TeacherStudentsScene):
    def construct(self):
        title = TextMobject("Unusual aspect \\#2")
        title.scale(1.5)
        title.to_edge(UP)

        line = Line(LEFT, RIGHT)
        line.match_width(title)
        line.next_to(title, DOWN)

        words = TextMobject("Harder than expected")
        words.set_color(RED)
        words.scale(1.5)
        words.next_to(line, DOWN, LARGE_BUFF)

        self.play(
            FadeInFromDown(title),
            ShowCreation(line),
            self.teacher.change, "raise_right_hand",
            self.get_student_changes("pondering", "confused", "sassy")
        )
        self.wait()
        self.play(
            FadeIn(words, UP),
            self.get_student_changes(*3 * ["horrified"]),
        )
        self.wait(3)


class TraditionalDifficulty(ContrastToOtherOlympiadProblems):
    def construct(self):
        test = self.get_test()
        rects = self.get_all_rects(test)
        for rect in rects:
            rect.reverse_points()

        big_rects = VGroup(*[
            FullScreenFadeRectangle()
            for x in range(3)
        ])
        for br, r1, r2 in zip(big_rects, rects, rects[3:]):
            br.append_vectorized_mobject(r1)
            br.append_vectorized_mobject(r2)
        big_rect = big_rects[0].copy()

        p_labels = VGroup()
        for i, rect in enumerate(rects):
            p_label = TextMobject("P{}".format(i + 1))
            p_label.next_to(rect, LEFT)
            p_labels.add(p_label)

        arrow = Vector(3 * DOWN)
        arrow.next_to(test[0], RIGHT)
        arrow.match_y(rects)
        harder_words = TextMobject("Get harder")
        harder_words.scale(2)
        harder_words.next_to(arrow, RIGHT)
        harder_words.set_color(RED)

        p_words = VGroup(
            TextMobject("Doable", color=GREEN),
            TextMobject("Challenging", color=YELLOW),
            TextMobject("Brutal", color=RED),
        )
        p_words.add(*p_words.copy())
        for rect, word, label in zip(rects, p_words, p_labels):
            word.next_to(rect, UP)
            label.match_color(word)

        self.add(test[0])
        self.play(
            FadeIn(harder_words),
            GrowArrow(arrow),
            LaggedStart(*[FadeIn(p, UP) for p in p_labels[:3]]),
            LaggedStartMap(ShowCreation, rects[:3]),
        )
        self.wait()
        self.play(
            FadeIn(test[1]),
            FadeIn(p_labels[3:]),
            FadeIn(rects[3:]),
            FadeOut(harder_words),
            FadeOut(arrow),
        )
        self.wait()
        self.add(big_rect, p_labels[0], p_labels[3])
        self.play(
            FadeIn(big_rect),
            FadeOut(rects),
            FadeOut(p_labels[1:3]),
            FadeOut(p_labels[4:]),
            FadeInFromDown(p_words[0::3]),
        )
        self.wait()
        self.play(
            Transform(big_rect, big_rects[1]),
            FadeOut(p_labels[0::3]),
            FadeIn(p_labels[1::3]),
            FadeOut(p_words[0::3], DOWN),
            FadeIn(p_words[1::3], UP),
        )
        self.wait()
        self.play(
            Transform(big_rect, big_rects[2]),
            FadeOut(p_labels[1::3]),
            FadeIn(p_labels[2::3]),
            FadeOut(p_words[1::3], DOWN),
            FadeIn(p_words[2::3], UP),
        )
        self.wait()


class PerfectScoreData(Describe2011IMO):
    CONFIG = {
        "n_students": 563,
        "n_perfect_scores_per_problem": [
            345, 22, 51, 267, 170, 6,
        ],
        "full_bar_width": 7,
    }

    def construct(self):
        self.add_title()
        self.show_total_number_of_students()
        self.add_subtitle()
        self.show_data()
        self.analyze_data()

    def add_title(self):
        self.force_skipping()
        super().add_title()
        self.revert_to_original_skipping_status()
        self.title.center().to_edge(UP)

    def show_total_number_of_students(self):
        title = self.title

        bar = self.get_bar(self.n_students, ORIGIN)
        bar.next_to(title, DOWN, buff=0.3)
        counter = self.get_bar_counter(bar)
        counter_label = TextMobject("Students")
        counter_label.add_updater(
            lambda m: m.next_to(counter, RIGHT)
        )

        self.add(counter, counter_label)
        self.play(
            self.get_bar_growth_anim(bar),
            run_time=2,
        )
        self.wait()

    def add_subtitle(self):
        title = self.title

        subtitle = TextMobject(
            "Number of perfect scores on each problem:"
        )
        subtitle.scale(1.25)
        subtitle.set_color(GREEN)
        subtitle.next_to(title, DOWN, buff=LARGE_BUFF)

        problems = VGroup(*[
            TextMobject("P{})".format(i))
            for i in range(1, 7)
        ])
        problems.arrange_in_grid(n_cols=2, buff=LARGE_BUFF)
        problems[3:].shift(5 * RIGHT)
        problems.next_to(subtitle, DOWN, LARGE_BUFF)
        problems.to_edge(LEFT)

        self.play(
            FadeInFromDown(subtitle),
            LaggedStartMap(FadeInFromDown, problems),
        )

        self.problems = problems

    def show_data(self):
        problems = self.problems
        bars = VGroup(*[
            self.get_bar(n, p.get_right() + SMALL_BUFF * RIGHT)
            for n, p in zip(
                self.n_perfect_scores_per_problem,
                problems,
            )
        ])
        counters = VGroup(*map(self.get_bar_counter, bars))

        self.play(
            VFadeIn(counters),
            *[
                self.get_bar_growth_anim(bar)
                for bar in bars
            ],
        )
        counters.set_fill(WHITE, 1)
        self.wait()

        self.problem_bars = bars
        self.problem_counters = counters

    def analyze_data(self):
        problems = VGroup(*[
            VGroup(p, pb, pc)
            for p, pb, pc in zip(
                self.problems,
                self.problem_bars,
                self.problem_counters,
            )
        ])
        rects = VGroup(*[
            SurroundingRectangle(p, color=p[1].get_color())
            for p in problems
        ])

        rect = rects[1].copy()
        self.play(ShowCreation(rect))
        self.wait()
        self.play(TransformFromCopy(rect, rects[4]))
        self.wait()
        self.play(TransformFromCopy(rect, rects[2]))
        self.wait()
        self.play(
            ReplacementTransform(rect, rects[5]),
            ReplacementTransform(rects[4], rects[5]),
            ReplacementTransform(rects[2], rects[5]),
        )
        self.wait()

    #
    def get_bar(self, number, left_side):
        bar = Rectangle()
        bar.set_stroke(width=0)
        bar.set_fill(WHITE, 1)
        bar.set_height(0.25)
        bar.set_width(
            self.full_bar_width * number / self.n_students,
            stretch=True
        )
        bar.move_to(left_side, LEFT)

        def update_bar_color(bar):
            frac = bar.get_width() / self.full_bar_width
            if 0 < frac <= 0.25:
                alpha = 4 * frac
                bar.set_color(interpolate_color(RED, YELLOW, alpha))
            elif 0.25 < frac <= 0.5:
                alpha = 4 * (frac - 0.25)
                bar.set_color(interpolate_color(YELLOW, GREEN, alpha))
            else:
                alpha = 2 * (frac - 0.5)
                bar.set_color(interpolate_color(GREEN, BLUE, alpha))
        bar.add_updater(update_bar_color)
        return bar

    def get_bar_growth_anim(self, bar):
        bar.save_state()
        bar.stretch(0, 0, about_edge=LEFT)
        return Restore(
            bar,
            suspend_mobject_updating=False,
            run_time=2,
        )

    def get_bar_counter(self, bar):
        counter = Integer()
        counter.add_updater(
            lambda m: m.set_value(
                self.n_students * bar.get_width() / self.full_bar_width
            )
        )
        counter.add_updater(lambda m: m.next_to(bar, RIGHT, SMALL_BUFF))
        return counter


class SixOnSix(Describe2011IMO):
    CONFIG = {
        "student_data": [
            [1, "Lisa Sauermann", "de", [7, 7, 7, 7, 7, 7]],
            [2, "Jeck Lim", "sg", [7, 5, 7, 7, 7, 7]],
            [3, "Lin Chen", "cn", [7, 3, 7, 7, 7, 7]],
            [14, "Mina Dalirrooyfard", "ir", [7, 0, 2, 7, 7, 7]],
            [202, "Georgios Kalantzis", "gr", [7, 0, 1, 1, 2, 7]],
            [202, "Chi Hong Chow", "hk", [7, 0, 3, 1, 0, 7]],
        ],
    }

    def construct(self):
        grid = self.get_score_grid()
        grid.to_edge(DOWN, buff=LARGE_BUFF)
        for row in grid.rows:
            row[0].set_opacity(0)
        grid.h_lines.stretch(0.93, 0, about_edge=RIGHT)

        sf = 1.25
        title = TextMobject("Only 6 solved P6")
        title.scale(sf)
        title.to_edge(UP, buff=MED_SMALL_BUFF)
        subtitle = TextMobject("P2 evaded 5 of them")
        subtitle.set_color(YELLOW)
        subtitle.scale(sf)
        subtitle.next_to(title, DOWN)

        six_rect, two_rect = [
            SurroundingRectangle(VGroup(
                grid.rows[0][index],
                grid.rows[-1][index],
            ))
            for index in [7, 3]
        ]

        self.play(
            Write(title),
            LaggedStart(*[FadeIn(row, UP) for row in grid.rows]),
            LaggedStart(*[ShowCreation(line) for line in grid.h_lines]),
        )
        self.play(ShowCreation(six_rect))
        self.wait()
        self.play(
            ReplacementTransform(six_rect, two_rect),
            FadeIn(subtitle, UP)
        )
        self.wait()


class AlwaysStartSimple(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("Always start\\\\simple")
        self.change_all_student_modes("pondering")
        self.wait(3)


class TryOutSimplestExamples(WindmillScene):
    CONFIG = {
        "windmill_rotation_speed": TAU / 8,
    }

    def construct(self):
        self.two_points()
        self.add_third_point()
        self.add_fourth_point()
        self.move_starting_line()

    def two_points(self):
        points = [1.5 * LEFT, 1.5 * RIGHT]
        dots = self.dots = self.get_dots(points)
        windmill = self.windmill = self.get_windmill(points, angle=TAU / 8)
        pivot_dot = self.pivot_dot = self.get_pivot_dot(windmill)

        self.play(
            ShowCreation(windmill),
            LaggedStartMap(
                FadeInFromLarge, dots,
                scale_factor=10,
                run_time=1,
                lag_ratio=0.4,
            ),
            GrowFromCenter(pivot_dot),
        )
        self.let_windmill_run(windmill, 8)

    def add_third_point(self):
        windmill = self.windmill

        new_point = 2 * DOWN
        new_dot = self.get_dots([new_point])
        windmill.point_set.append(new_point)

        self.add(new_dot, self.pivot_dot)
        self.play(FadeInFromLarge(new_dot, scale_factor=10))
        self.let_windmill_run(windmill, 8)

    def add_fourth_point(self):
        windmill = self.windmill
        dot = self.get_dots([ORIGIN])
        dot.move_to(DOWN + 2 * RIGHT)
        words = TextMobject("Never hit!")
        words.set_color(RED)
        words.scale(0.75)
        words.move_to(0.7 * DOWN, DOWN)

        self.add(dot, self.pivot_dot)
        self.play(
            FadeInFromLarge(dot, scale_factor=10)
        )
        windmill.point_set.append(dot.get_center())
        windmill.rot_speed = TAU / 4
        self.let_windmill_run(windmill, 4)

        # Shift point
        self.play(
            dot.next_to, words, DOWN,
            FadeIn(words, RIGHT),
        )
        windmill.point_set[3] = dot.get_center()
        self.let_windmill_run(windmill, 4)
        self.wait()

        self.dots.add(dot)
        self.never_hit_words = words

    def move_starting_line(self):
        windmill = self.windmill
        dots = self.dots

        windmill.suspend_updating()
        self.play(
            windmill.move_to, dots[-1],
            FadeOut(self.never_hit_words),
        )
        windmill.pivot = dots[-1].get_center()
        windmill.resume_updating()

        counters = self.get_pivot_counters(windmill)
        self.play(
            LaggedStart(*[
                FadeIn(counter, DOWN)
                for counter in counters
            ])
        )
        self.wait()

        windmill.rot_speed = TAU / 8
        self.let_windmill_run(windmill, 16)
        highlight = windmill.copy()
        highlight.set_stroke(YELLOW, 4)
        self.play(
            ShowCreationThenDestruction(highlight),
        )
        self.let_windmill_run(windmill, 8)


class FearedCase(WindmillScene):
    CONFIG = {
        "n_points": 25,
        "windmill_rotation_speed": TAU / 16,
    }

    def construct(self):
        points = self.get_random_point_set(self.n_points)
        sorted_points = sorted(list(points), key=lambda p: p[1])

        dots = self.get_dots(points)
        windmill = self.get_windmill(
            points,
            sorted_points[self.n_points // 2],
            angle=0,
        )
        pivot_dot = self.get_pivot_dot(windmill)
        # self.add_dot_color_updater(dots, windmill)
        counters = self.get_pivot_counters(
            windmill,
            counter_height=0.15,
            buff=0.1
        )

        self.add(windmill)
        self.add(dots)
        self.add(pivot_dot)
        self.add(counters)

        self.let_windmill_run(windmill, 32)
        windmill.pivot = sorted_points[0]
        self.let_windmill_run(windmill, 32)


class WhereItStartsItEnds(WindmillScene):
    CONFIG = {
        "n_points": 11,
        "windmill_rotation_speed": TAU / 8,
        "random_seed": 1,
        "points_shift_val": 2 * LEFT,
    }

    def construct(self):
        self.show_stays_in_middle()
        self.ask_about_proof()

    def show_stays_in_middle(self):
        points = self.get_random_point_set(self.n_points)
        points += self.points_shift_val
        sorted_points = sorted(list(points), key=lambda p: p[1])
        dots = self.get_dots(points)

        windmill = self.get_windmill(
            points,
            sorted_points[self.n_points // 2],
            angle=0
        )
        pivot_dot = self.get_pivot_dot(windmill)

        sf = 1.25
        start_words = TextMobject("Starts in the ", "``middle''")
        start_words.scale(sf)
        start_words.next_to(windmill, UP, MED_SMALL_BUFF)
        start_words.to_edge(RIGHT)
        end_words = TextMobject("Stays in the ", "``middle''")
        end_words.scale(sf)
        end_words.next_to(windmill, DOWN, MED_SMALL_BUFF)
        end_words.to_edge(RIGHT)
        start_words.match_x(end_words)

        self.add(dots)
        self.play(
            ShowCreation(windmill),
            GrowFromCenter(pivot_dot),
            FadeIn(start_words, LEFT),
        )
        self.wait()
        self.start_leaving_shadows()
        self.add(windmill, dots, pivot_dot)
        half_time = PI / windmill.rot_speed
        self.let_windmill_run(windmill, time=half_time)
        self.play(FadeIn(end_words, UP))
        self.wait()
        self.let_windmill_run(windmill, time=half_time)
        self.wait()

        self.start_words = start_words
        self.end_words = end_words
        self.windmill = windmill
        self.dots = dots
        self.pivot_dot = pivot_dot

    def ask_about_proof(self):
        sf = 1.25
        middle_rects = self.get_middle_rects()
        middle_words = TextMobject("Can you formalize this?")
        middle_words.scale(sf)
        middle_words.next_to(middle_rects, DOWN, MED_LARGE_BUFF)
        middle_words.to_edge(RIGHT)
        middle_words.match_color(middle_rects)

        proof_words = TextMobject("Can you prove this?")
        proof_words.next_to(
            self.end_words.get_left(),
            DL,
            buff=2,
        )
        proof_words.shift(RIGHT)
        proof_words.scale(sf)
        proof_arrow = Arrow(
            proof_words.get_top(),
            self.end_words.get_corner(DL),
            buff=SMALL_BUFF,
        )
        proof_words2 = TextMobject("Then prove the result?")
        proof_words2.scale(sf)
        proof_words2.next_to(middle_words, DOWN, MED_LARGE_BUFF)
        proof_words2.to_edge(RIGHT)
        VGroup(proof_words, proof_words2, proof_arrow).set_color(YELLOW)

        self.play(
            Write(proof_words),
            GrowArrow(proof_arrow),
            run_time=1,
        )
        self.wait()
        self.play(
            FadeOut(proof_arrow),
            FadeOut(proof_words),
            LaggedStartMap(ShowCreation, middle_rects),
            Write(middle_words),
        )
        self.wait()
        self.play(FadeIn(proof_words2, UP))
        self.wait()
        self.let_windmill_run(self.windmill, time=10)

    def get_middle_rects(self):
        middle_rects = VGroup(*[
            SurroundingRectangle(words[1])
            for words in [
                self.start_words,
                self.end_words
            ]
        ])
        middle_rects.set_color(TEAL)
        return middle_rects


class AltWhereItStartsItEnds(WhereItStartsItEnds):
    CONFIG = {
        "n_points": 9,
        "random_seed": 3,
    }


class FormalizeMiddle(WhereItStartsItEnds):
    CONFIG = {
        "random_seed": 2,
        "points_shift_val": 3 * LEFT,
    }

    def construct(self):
        self.show_stays_in_middle()
        self.problem_solving_tip()
        self.define_colors()
        self.mention_odd_case()
        self.ask_about_numbers()

    def problem_solving_tip(self):
        mid_words = VGroup(
            self.start_words,
            self.end_words,
        )
        mid_words.save_state()

        sf = 1.25
        pst = TextMobject("Problem-solving tip:")
        pst.scale(sf)
        underline = Line(LEFT, RIGHT)
        underline.match_width(pst)
        underline.move_to(pst.get_bottom())
        pst.add(underline)
        pst.to_corner(UR)
        # pst.set_color(YELLOW)

        steps = VGroup(
            TextMobject("Vague idea"),
            TextMobject("Put numbers to it"),
            TextMobject("Ask about those numbers"),
        )
        steps.scale(sf)
        steps.arrange(DOWN, buff=LARGE_BUFF)
        steps.next_to(pst, DOWN, buff=MED_LARGE_BUFF)
        steps.shift_onto_screen()
        pst.match_x(steps)

        colors = color_gradient([BLUE, YELLOW], 3)
        for step, color in zip(steps, colors):
            step.set_color(color)

        arrows = VGroup()
        for s1, s2 in zip(steps, steps[1:]):
            arrow = Arrow(s1.get_bottom(), s2.get_top(), buff=SMALL_BUFF)
            arrows.add(arrow)

        self.play(Write(pst), run_time=1)
        self.wait()
        self.play(
            mid_words.scale, 0.75,
            mid_words.set_opacity, 0.25,
            mid_words.to_corner, DL,
            FadeInFromDown(steps[0]),
        )
        self.wait()
        for arrow, step in zip(arrows, steps[1:]):
            self.play(
                FadeIn(step, UP),
                GrowArrow(arrow),
            )
            self.wait()

        steps.generate_target()
        steps.target.scale(0.75)
        steps.target.arrange(DOWN, buff=0.2)
        steps.target.to_corner(UR)

        self.play(
            FadeOut(pst),
            MoveToTarget(steps),
            Restore(mid_words),
            FadeOut(arrows)
        )
        self.wait()

        self.tip_words = steps
        self.mid_words = mid_words

    def define_colors(self):
        windmill = self.windmill
        mid_words = self.mid_words
        tip_words = self.tip_words
        shadows = self.windmill_shadows
        self.leave_shadows = False

        full_time = TAU / windmill.rot_speed

        self.play(FadeOut(shadows))
        self.add(windmill, tip_words, mid_words, self.dots, self.pivot_dot)
        self.let_windmill_run(windmill, time=full_time / 4)
        windmill.rotate(PI)
        self.wait()

        # Show regions
        rects = self.get_left_right_colorings(windmill)
        rects.suspend_updating()
        rects.save_state()
        rects.stretch(0, 0, about_point=windmill.get_center())

        counters = VGroup(Integer(0), Integer(0))
        counters.scale(2)
        counters[0].set_stroke(BLUE, 3, background=True)
        counters[1].set_stroke(GREY_BROWN, 3, background=True)

        new_dots = self.dots.copy()
        new_dots.set_color(WHITE)
        for dot in new_dots:
            dot.scale(1.25)
        new_dots.sort(lambda p: p[0])
        k = self.n_points // 2
        dot_sets = VGroup(new_dots[:k], new_dots[-k:])

        label_sets = VGroup()
        for dot_set, direction in zip(dot_sets, [LEFT, RIGHT]):
            label_set = VGroup()
            for i, dot in zip(it.count(1), dot_set):
                label = Integer(i)
                label.set_height(0.15)
                label.next_to(dot, direction, SMALL_BUFF)
                label_set.add(label)
            label_sets.add(label_set)

        for counter, dot_set in zip(counters, dot_sets):
            counter.move_to(dot_set)
            counter.to_edge(UP)

        self.add(rects, *self.get_mobjects())
        self.play(
            Restore(rects),
            FadeIn(counters),
        )
        for counter, dot_set, label_set in zip(counters, dot_sets, label_sets):
            self.play(
                ShowIncreasingSubsets(dot_set),
                ShowIncreasingSubsets(label_set),
                ChangingDecimal(counter, lambda a: len(dot_set)),
                rate_func=linear,
            )
            self.wait()
        self.wait()

        self.remove(self.dots)
        self.dots = new_dots

        # Show orientation
        tips = self.get_orientation_arrows(windmill)

        self.play(ShowCreation(tips))
        windmill.add(tips)
        self.wait()

        self.add_dot_color_updater(new_dots, windmill)

        rects.suspend_updating()
        for rect in rects:
            self.play(rect.set_opacity, 1)
            self.play(rect.set_opacity, rects.const_opacity)
        rects.resume_updating()
        self.wait()
        self.play(
            counters.space_out_submobjects, 0.8,
            counters.next_to, mid_words, DOWN, LARGE_BUFF,
            FadeOut(label_sets),
        )
        eq = TexMobject("=")
        eq.scale(2)
        eq.move_to(counters)
        self.play(FadeIn(eq))
        self.wait()

        self.counters = counters
        self.colored_regions = rects
        rects.resume_updating()

    def mention_odd_case(self):
        dots = self.dots
        counters = self.counters

        sf = 1.0
        words = TextMobject(
            "Assume odd \\# points"
        )
        words.scale(sf)
        words.to_corner(UL)
        example = VGroup(
            TextMobject("Example:"),
            Integer(0)
        )
        example.arrange(RIGHT)
        example.scale(sf)
        example.next_to(words, DOWN)
        example.align_to(words, LEFT)

        k = self.n_points // 2
        dot_rects = VGroup()
        for i, dot in zip(it.count(1), dots):
            dot_rect = SurroundingRectangle(dot)
            dot_rect.match_color(dot)
            dot_rects.add(dot_rect)

        self.play(FadeIn(words, DOWN))
        self.wait()

        self.play(
            ShowCreationThenFadeAround(dots[k]),
            self.pivot_dot.set_color, WHITE,
        )

        self.play(FadeIn(example, UP))
        self.play(
            ShowIncreasingSubsets(dot_rects),
            ChangingDecimal(
                example[1],
                lambda a: len(dot_rects)
            ),
            rate_func=linear
        )
        self.wait()

        self.remove(dot_rects)
        self.play(
            ShowCreationThenFadeOut(dot_rects[:k]),
            ShowCreationThenFadeOut(
                SurroundingRectangle(counters[0], color=BLUE)
            ),
        )
        self.play(
            ShowCreationThenFadeOut(dot_rects[-k:]),
            ShowCreationThenFadeOut(
                SurroundingRectangle(counters[1], color=GREY_BROWN)
            ),
        )
        self.wait()
        self.play(
            FadeOut(words),
            FadeOut(example),
        )

    def ask_about_numbers(self):
        self.windmill.rot_speed *= 0.5
        self.add(self.dots, self.pivot_dot)
        self.let_windmill_run(self.windmill, 20)


class SecondColoringExample(WindmillScene):
    CONFIG = {
        "run_time": 30,
        "n_points": 9,
    }

    def construct(self):
        points = self.get_random_point_set(self.n_points)
        points += RIGHT
        sorted_points = sorted(list(points), key=lambda p: p[0])

        dots = self.get_dots(points)
        windmill = self.get_windmill(
            points,
            pivot=sorted_points[self.n_points // 2],
            angle=PI / 2
        )
        pivot_dot = self.get_pivot_dot(windmill)
        pivot_dot.set_color(WHITE)
        rects = self.get_left_right_colorings(windmill)
        self.add_dot_color_updater(dots, windmill)

        counts = VGroup(
            TextMobject("\\# Blues = 4"),
            TextMobject("\\# Browns = 4"),
        )
        counts.arrange(DOWN, aligned_edge=LEFT, buff=MED_LARGE_BUFF)
        counts.to_corner(UL)
        counts[0].set_color(interpolate_color(BLUE, WHITE, 0.25))
        counts[1].set_color(interpolate_color(GREY_BROWN, WHITE, 0.5))
        counts[0].set_stroke(BLACK, 5, background=True)
        counts[1].set_stroke(BLACK, 5, background=True)

        const_words = TextMobject("Stay constant$\\dots$why?")
        const_words.next_to(counts, RIGHT, buff=1.5, aligned_edge=UP)
        arrows = VGroup(*[
            Arrow(
                const_words.get_left(),
                count.get_right(),
                buff=SMALL_BUFF,
                max_tip_length_to_length_ratio=0.15,
                max_stroke_width_to_length_ratio=3,
            )
            for count in counts
        ])

        self.add(rects, windmill, dots, pivot_dot)
        self.add(counts, const_words, arrows)

        self.let_windmill_run(windmill, time=self.run_time)


class TalkThroughPivotChange(WindmillScene):
    CONFIG = {
        "windmill_rotation_speed": 0.2,
    }

    def construct(self):
        self.setup_windmill()
        self.ask_about_pivot_change()
        self.show_above_and_below()
        self.change_pivot()

    def setup_windmill(self):
        points = self.points = np.array([
            DR, UR, UL, DL, 0.5 * LEFT
        ])
        points *= 3
        self.dots = self.get_dots(points)
        self.windmill = self.get_windmill(points, points[-1])
        self.pivot_dot = self.get_pivot_dot(self.windmill)
        self.pivot_dot.set_color(WHITE)
        self.add_dot_color_updater(self.dots, self.windmill)
        self.rects = self.get_left_right_colorings(self.windmill)

        self.add(
            self.rects,
            self.windmill,
            self.dots,
            self.pivot_dot,
        )

    def ask_about_pivot_change(self):
        windmill = self.windmill

        new_pivot, angle = self.next_pivot_and_angle(windmill)
        words = TextMobject("Think about\\\\pivot change")
        words.next_to(new_pivot, UP, buff=2)
        words.to_edge(LEFT)
        arrow = Arrow(words.get_bottom(), new_pivot, buff=0.2)

        self.play(
            Rotate(
                windmill, -0.9 * angle,
                run_time=3,
                rate_func=linear
            ),
            Write(words, run_time=1),
            ShowCreation(arrow),
        )
        self.wait()

        self.question = words
        self.question_arrow = arrow

    def show_above_and_below(self):
        windmill = self.windmill
        vect = normalize(windmill.get_vector())
        angle = windmill.get_angle()
        tips = self.get_orientation_arrows(windmill)
        top_half = Line(windmill.get_center(), windmill.get_end())
        low_half = Line(windmill.get_center(), windmill.get_start())
        top_half.set_stroke(YELLOW, 3)
        low_half.set_stroke(PINK, 3)
        halves = VGroup(top_half, low_half)

        top_words = TextMobject("Above pivot")
        low_words = TextMobject("Below pivot")
        all_words = VGroup(top_words, low_words)
        for words, half in zip(all_words, halves):
            words.next_to(ORIGIN, DOWN)
            words.rotate(angle, about_point=ORIGIN)
            words.shift(half.point_from_proportion(0.15))
            words.match_color(half)

        self.play(ShowCreation(tips))
        self.wait()
        self.add(top_half, tips)
        self.play(
            ShowCreationThenFadeOut(top_half),
            FadeIn(top_words, -vect),
        )
        self.add(low_half, tips)
        self.play(
            ShowCreationThenFadeOut(low_half),
            FadeIn(low_words, vect),
        )
        self.wait()

        windmill.add(tips)
        self.above_below_words = all_words

    def change_pivot(self):
        windmill = self.windmill
        dots = self.dots
        arrow = self.question_arrow

        blue_rect = SurroundingRectangle(dots[3])
        blue_rect.set_color(BLUE)
        new_pivot_word = TextMobject("New pivot")
        new_pivot_word.next_to(blue_rect, LEFT)
        old_pivot_word = TextMobject("Old pivot")
        old_pivot = windmill.pivot
        old_pivot_word.next_to(
            old_pivot, LEFT,
            buff=SMALL_BUFF + MED_SMALL_BUFF
        )

        self.play(
            FadeOut(self.above_below_words),
            ReplacementTransform(
                self.question,
                new_pivot_word,
            ),
            ReplacementTransform(arrow, blue_rect),
        )
        self.wait()
        anims, time = self.rotate_to_next_pivot(windmill)
        self.play(
            *anims,
            Rotate(
                windmill,
                angle=-windmill.rot_speed,
                rate_func=linear,
            )
        )
        self.wait()
        self.play(
            TransformFromCopy(new_pivot_word, old_pivot_word),
            blue_rect.move_to, old_pivot,
        )
        self.wait(2)

        # Hit new point
        brown_rect = SurroundingRectangle(dots[1])
        brown_rect.set_color(GREY_BROWN)

        self.play(TransformFromCopy(blue_rect, brown_rect))
        self.play(
            blue_rect.move_to, windmill.pivot,
            blue_rect.set_color, GREY_BROWN,
            old_pivot_word.move_to, new_pivot_word,
            FadeOut(new_pivot_word, DL)
        )
        self.let_windmill_run(windmill, 1)
        self.wait()
        self.play(
            FadeOut(old_pivot_word),
            FadeOut(blue_rect),
            FadeOut(brown_rect),
        )
        self.let_windmill_run(windmill, 20)


class InsightNumber1(Scene):
    def construct(self):
        words = TextMobject(
            "Key insight 1: ",
            "\\# Points on either side is constant"
        )
        words[0].set_color(YELLOW)
        words.set_width(FRAME_WIDTH - 1)
        self.play(FadeInFromDown(words))
        self.wait()


class Rotate180Argument(WindmillScene):
    CONFIG = {
        "n_points": 21,
        "random_seed": 3,
    }

    def construct(self):
        self.setup_windmill()
        self.add_total_rotation_label()
        self.rotate_180()
        self.show_parallel_lines()
        self.rotate_180()
        self.rotate_180()

    def setup_windmill(self):
        n = self.n_points
        points = self.get_random_point_set(n)
        points[:, 0] *= 1.5
        points += RIGHT
        points = sorted(points, key=lambda p: p[0])
        mid_point = points[n // 2]
        points[n // 2 - 1] += 0.2 * LEFT
        self.points = points

        self.dots = self.get_dots(points)
        self.windmill = self.get_windmill(points, mid_point)
        self.pivot_dot = self.get_pivot_dot(self.windmill)
        self.pivot_dot.set_color(WHITE)
        self.add_dot_color_updater(self.dots, self.windmill)
        self.rects = self.get_left_right_colorings(self.windmill)

        p_label = TexMobject("P_0")
        p_label.next_to(mid_point, RIGHT, SMALL_BUFF)
        self.p_label = p_label

        self.add(
            self.rects,
            self.windmill,
            self.dots,
            self.pivot_dot,
            self.p_label,
        )

    def add_total_rotation_label(self):
        windmill = self.windmill

        words = TextMobject("Total rotation:")
        counter = Integer(0, unit="^\\circ")
        title = VGroup(words, counter)
        title.arrange(RIGHT)
        title.to_corner(UL)
        rot_arrow = Vector(UP)
        rot_arrow.set_color(RED)
        rot_arrow.next_to(title, DOWN)
        circle = Circle()
        circle.replace(rot_arrow, dim_to_match=1)
        circle.set_stroke(WHITE, 1)

        rot_arrow.add_updater(
            lambda m: m.set_angle(windmill.get_angle())
        )
        rot_arrow.add_updater(
            lambda m: m.move_to(circle)
        )

        def update_count(c):
            new_val = 90 - windmill.get_angle() * 360 / TAU
            while abs(new_val - c.get_value()) > 90:
                new_val += 360
            c.set_value(new_val)

        counter.add_updater(update_count)

        rect = SurroundingRectangle(
            VGroup(title, circle),
            buff=MED_LARGE_BUFF,
        )
        rect.set_fill(BLACK, 0.8)
        rect.set_stroke(WHITE, 1)
        title.shift(MED_SMALL_BUFF * LEFT)

        self.rotation_label = VGroup(
            rect, words, counter, circle, rot_arrow
        )

        self.add(self.rotation_label)

    def rotate_180(self):
        windmill = self.windmill
        self.add(self.pivot_dot)
        self.let_windmill_run(
            windmill,
            PI / windmill.rot_speed,
        )
        self.wait()

    def show_parallel_lines(self):
        points = self.points
        rotation_label = self.rotation_label
        dots = self.dots
        windmill = self.windmill

        lines = VGroup()
        for point in points:
            line = Line(DOWN, UP)
            line.set_height(2 * FRAME_HEIGHT)
            line.set_stroke(RED, 1, opacity=0.5)
            line.move_to(point)
            lines.add(line)
        lines.shuffle()

        self.add(lines, dots, rotation_label)
        self.play(
            ShowCreation(lines, lag_ratio=0.5, run_time=3)
        )
        self.wait()

        self.rects.suspend_updating()
        for rect in self.rects:
            self.play(
                rect.set_opacity, 0,
                rate_func=there_and_back,
                run_time=2
            )
        self.rects.resume_updating()
        self.wait()

        pivot_tracker = VectorizedPoint(windmill.pivot)
        pivot_tracker.save_state()

        def update_pivot(w):
            w.pivot = pivot_tracker.get_center()
        windmill.add_updater(update_pivot)

        for x in range(4):
            point = random.choice(points)
            self.play(
                pivot_tracker.move_to, point
            )
            self.wait()
        self.play(Restore(pivot_tracker))
        self.play(FadeOut(lines))
        windmill.remove_updater(update_pivot)
        self.wait()


class Rotate180ArgumentFast(Rotate180Argument):
    CONFIG = {
        "windmill_rotation_speed": 0.5,
    }


class EvenCase(Rotate180Argument):
    CONFIG = {
        "n_points": 10,
        "dot_config": {"radius": 0.075},
    }

    def construct(self):
        self.ask_about_even_number()
        self.choose_halfway_point()

        self.add_total_rotation_label()
        self.rotate_180()
        self.rotate_180()
        self.show_parallel_lines()
        self.rotate_180()
        self.rotate_180()

    def ask_about_even_number(self):
        n = self.n_points
        points = self.get_random_point_set(n)
        points[:, 0] *= 2
        points += DOWN
        points = sorted(points, key=lambda p: p[0])
        dots = self.get_dots(points)

        windmill = self.get_windmill(points, points[3])
        region_rects = self.rects = self.get_left_right_colorings(windmill)
        pivot_dot = self.get_pivot_dot(windmill)
        pivot_dot.set_color(WHITE)

        dot_rects = VGroup(*map(SurroundingRectangle, dots))

        question = TextMobject("What about an even number?")
        # question.to_corner(UL)
        question.to_edge(UP)
        counter_label = TextMobject("\\# Points", ":")
        counter = Integer(0)
        counter_group = VGroup(counter_label, counter)
        counter_group.arrange(RIGHT)
        counter.align_to(counter_label[1], DOWN)
        counter_group.next_to(question, DOWN, MED_LARGE_BUFF)
        counter_group.set_color(YELLOW)
        # counter_group.align_to(question, LEFT)

        self.add(question, counter_label)
        self.add(windmill, dots, pivot_dot)

        self.add_dot_color_updater(dots, windmill)
        self.add(region_rects, question, counter_group, windmill, dots, pivot_dot)

        self.play(
            ShowIncreasingSubsets(dot_rects),
            ChangingDecimal(counter, lambda a: len(dot_rects)),
            rate_func=linear
        )
        self.play(FadeOut(dot_rects))
        self.wait()

        # region_rects.suspend_updating()
        # self.play(
        #     FadeIn(region_rects),
        #     FadeOut(dot_rects),
        # )
        # region_rects.resume_updating()
        # self.wait()

        # Count by color
        blue_rects = dot_rects[:3]
        blue_rects.set_color(BLUE)
        brown_rects = dot_rects[4:]
        brown_rects.set_color(GREY_BROWN)
        pivot_rect = dot_rects[3]
        pivot_rect.set_color(GREY_BROWN)

        blues_label = TextMobject("\\# Blues", ":")
        blues_counter = Integer(len(blue_rects))
        blues_group = VGroup(blues_label, blues_counter)
        blues_group.set_color(BLUE)
        browns_label = TextMobject("\\# Browns", ":")
        browns_counter = Integer(len(brown_rects))
        browns_group = VGroup(browns_label, browns_counter)
        browns_group.set_color(interpolate_color(GREY_BROWN, WHITE, 0.5))
        groups = VGroup(blues_group, browns_group)
        for group in groups:
            group.arrange(RIGHT)
            group[-1].align_to(group[0][-1], DOWN)
        groups.arrange(DOWN, aligned_edge=LEFT)
        groups.next_to(counter_group, DOWN, aligned_edge=LEFT)

        self.play(
            FadeIn(blues_group, UP),
            ShowCreation(blue_rects),
        )
        self.play(
            FadeIn(browns_group, UP),
            ShowCreation(brown_rects),
        )
        self.wait()

        # Pivot counts as brown
        pivot_words = TextMobject("Pivot counts as brown")
        arrow = Vector(LEFT)
        arrow.next_to(pivot_dot, RIGHT, SMALL_BUFF)
        pivot_words.next_to(arrow, RIGHT, SMALL_BUFF)

        self.play(
            FadeIn(pivot_words, LEFT),
            ShowCreation(arrow),
        )
        self.play(
            ShowCreation(pivot_rect),
            ChangeDecimalToValue(browns_counter, len(brown_rects) + 1),
            FadeOut(pivot_dot),
        )
        self.wait()
        self.play(
            FadeOut(dot_rects),
            FadeOut(pivot_words),
            FadeOut(arrow),
        )
        self.wait()

        blues_counter.add_updater(
            lambda c: c.set_value(len(list(filter(
                lambda d: d.get_fill_color() == Color(BLUE),
                dots
            ))))
        )
        browns_counter.add_updater(
            lambda c: c.set_value(len(list(filter(
                lambda d: d.get_fill_color() == Color(GREY_BROWN),
                dots
            ))))
        )

        self.windmill = windmill
        self.dots = dots
        self.points = points
        self.question = question
        self.counter_group = VGroup(
            counter_group,
            blues_group,
            browns_group,
        )

    def choose_halfway_point(self):
        windmill = self.windmill
        points = self.points
        n = self.n_points

        p_label = TexMobject("P_0")
        p_label.next_to(points[n // 2], RIGHT, SMALL_BUFF)

        pivot_tracker = VectorizedPoint(windmill.pivot)

        def update_pivot(w):
            w.pivot = pivot_tracker.get_center()

        windmill.add_updater(update_pivot)

        self.play(
            pivot_tracker.move_to, points[n // 2],
            run_time=2
        )
        self.play(FadeIn(p_label, LEFT))
        self.wait()
        windmill.remove_updater(update_pivot)

    def add_total_rotation_label(self):
        super().add_total_rotation_label()
        self.rotation_label.scale(0.8, about_edge=UL)

        self.play(
            FadeOut(self.question),
            FadeIn(self.rotation_label),
            self.counter_group.to_edge, UP,
        )


class TwoTakeaways(TeacherStudentsScene):
    def construct(self):
        title = TextMobject("Two takeaways")
        title.scale(2)
        title.to_edge(UP)

        line = Line()
        line.match_width(title)
        line.next_to(title, DOWN, SMALL_BUFF)

        items = VGroup(*[
            TextMobject("1) Social"),
            TextMobject("2) Mathematical"),
        ])
        items.scale(1.5)
        items.arrange(DOWN, buff=MED_LARGE_BUFF, aligned_edge=LEFT)
        items.next_to(line, DOWN, buff=MED_LARGE_BUFF)

        self.play(
            ShowCreation(line),
            GrowFromPoint(title, self.hold_up_spot),
            self.teacher.change, "raise_right_hand",
        )
        self.change_all_student_modes("pondering")
        self.wait()
        for item in items:
            self.play(FadeIn(item, LEFT))
            item.big = item.copy()
            item.small = item.copy()
            item.big.scale(1.5, about_edge=LEFT)
            item.big.set_color(BLUE)
            item.small.scale(0.75, about_edge=LEFT)
            item.small.fade(0.5)
        self.play(self.teacher.change, "happy")
        self.wait()
        for i, j in [(0, 1), (1, 0)]:
            self.play(
                items[i].become, items[i].big,
                items[j].become, items[j].small,
            )
            self.wait()


class EasyToFoolYourself(PiCreatureScene):
    CONFIG = {
        "default_pi_creature_kwargs": {
            "color": GREY_BROWN,
        }
    }

    def construct(self):
        morty = self.pi_creature
        morty.to_corner(DL)

        bubble = ThoughtBubble()
        for i, part in enumerate(bubble):
            part.shift(2 * i * SMALL_BUFF * DOWN)
        bubble.pin_to(morty)

        fool_word = TextMobject("Fool")
        fool_word.scale(1.5)
        fool_arrow = Vector(LEFT)
        fool_arrow.next_to(morty, RIGHT, buff=0)
        fool_word.next_to(fool_arrow, RIGHT)

        self.add(morty)
        self.play(
            ShowCreation(bubble),
            morty.change, "pondering",
        )
        self.play(
            bubble[3].set_fill, GREEN_SCREEN, 0.5,
        )
        self.wait()
        self.play(morty.change, "thinking")
        self.play(
            FadeIn(fool_word, LEFT),
            ShowCreation(fool_arrow),
        )
        self.wait()
        self.pi_creature_says(
            "Isn't it\\\\obvious?",
            target_mode="maybe",
            added_anims=[FadeOut(bubble)]
        )
        self.wait(4)

        #
        words = TextMobject("No it's not!")
        words.scale(1.5)
        words.set_color(RED)
        words.next_to(morty.bubble, RIGHT, LARGE_BUFF)
        words.match_y(morty.bubble.content)

        self.play(
            FadeInFromLarge(words),
            morty.change, "guilty",
        )
        self.wait()

        # for i, part in enumerate(bubble):
        #     self.add(Integer(i).move_to(part))


class FailureToEmpathize(PiCreatureScene):
    def construct(self):
        randy, morty = self.pi_creatures

        # What a mess...
        big_bubble = ThoughtBubble(height=4, width=5)
        big_bubble.scale(1.75)
        big_bubble.flip(UR)
        for part in big_bubble:
            part.rotate(90 * DEGREES)
        big_bubble[:3].rotate(-30 * DEGREES)
        for i, part in enumerate(big_bubble[:3]):
            part.rotate(30 * DEGREES)
            part.shift((3 - i) * SMALL_BUFF * DOWN)
        big_bubble[0].shift(MED_SMALL_BUFF * RIGHT)
        big_bubble[:3].next_to(big_bubble[3], LEFT)
        big_bubble[:3].shift(0.3 * DOWN)
        big_bubble.set_fill(DARKER_GREY)
        big_bubble.to_corner(UR)

        equation = TexMobject(
            "\\sum_{k=1}^n (2k - 1) = n^2"
        )
        self.pi_creature_thinks(
            randy, equation,
            target_mode="confused",
            look_at_arg=equation,
        )
        randy_group = VGroup(
            randy, randy.bubble,
            randy.bubble.content
        )
        self.wait()
        self.play(
            DrawBorderThenFill(big_bubble),
            morty.change, "confused",
            randy_group.scale, 0.5,
            randy_group.move_to, big_bubble.get_bubble_center(),
            randy_group.shift, 0.5 * DOWN + RIGHT,
        )
        self.wait()
        self.play(morty.change, "maybe")
        self.wait(2)

        # Zoom out
        morty_group = VGroup(morty, big_bubble)
        ap = 5 * RIGHT + 2.5 * UP
        self.add(morty_group, randy_group)
        self.play(
            morty_group.scale, 2, {"about_point": ap},
            morty_group.fade, 1,
            randy_group.scale, 2, {"about_point": ap},
            run_time=2
        )
        self.wait()

    def create_pi_creatures(self):
        randy = Randolph()
        morty = Mortimer()
        randy.flip().to_corner(DR)
        morty.flip().to_corner(DL)

        return (randy, morty)


class DifficultyEstimateVsReality(Scene):
    def construct(self):
        axes = Axes(
            x_min=-1,
            x_max=10,
            x_axis_config={
                "include_tip": False,
            },
            y_min=-1,
            y_max=5,
        )
        axes.set_height(FRAME_HEIGHT - 1)
        axes.center()
        axes.x_axis.tick_marks.set_opacity(0)

        y_label = TextMobject("Average score")
        y_label.scale(1.25)
        y_label.rotate(90 * DEGREES)
        y_label.next_to(axes.y_axis, LEFT, SMALL_BUFF)
        y_label.shift(UP)

        estimated = [1.8, 2.6, 3, 4, 5]
        actual = [1.5, 0.5, 1, 1.2, 1.8]

        colors = [GREEN, RED]
        estimated_color, actual_color = colors

        estimated_bars = VGroup()
        actual_bars = VGroup()
        bar_pairs = VGroup()

        width = 0.25
        for a, e in zip(actual, estimated):
            bars = VGroup(
                Rectangle(width=width, height=e),
                Rectangle(width=width, height=a),
            )
            bars.set_stroke(width=1)
            bars[0].set_fill(estimated_color, 0.75)
            bars[1].set_fill(actual_color, 0.75)
            bars.arrange(RIGHT, buff=0, aligned_edge=DOWN)
            bar_pairs.add(bars)
            estimated_bars.add(bars[0])
            actual_bars.add(bars[1])

        bar_pairs.arrange(RIGHT, buff=1.5, aligned_edge=DOWN)
        bar_pairs.move_to(axes.c2p(5, 0), DOWN)
        for bp in bar_pairs:
            for bar in bp:
                bar.save_state()
                bar.stretch(0, 1, about_edge=DOWN)

        x_labels = VGroup(*[
            TextMobject("Q{}".format(i)).next_to(bp, DOWN)
            for i, bp in zip(it.count(1), bar_pairs)
        ])

        data_labels = VGroup(
            TextMobject("Estimated average"),
            TextMobject("Actual average"),
        )
        data_labels.arrange(DOWN, buff=MED_LARGE_BUFF, aligned_edge=LEFT)
        data_labels.to_edge(UP)
        for color, label in zip(colors, data_labels):
            square = Square()
            square.set_height(0.5)
            square.set_fill(color, 0.75)
            square.set_stroke(WHITE, 1)
            square.next_to(label, LEFT, SMALL_BUFF)
            label.add(square)

        self.play(Write(axes))
        self.play(Write(y_label))

        self.play(
            LaggedStartMap(
                FadeInFrom, x_labels,
                lambda m: (m, UP),
                run_time=2,
            ),
            LaggedStartMap(
                Restore,
                estimated_bars,
                run_time=3,
            ),
            FadeIn(data_labels[0]),
        )
        self.wait()
        self.play(
            LaggedStartMap(
                Restore,
                actual_bars,
                run_time=3,
            ),
            FadeIn(data_labels[1]),
        )
        self.wait()


class KeepInMindWhenTeaching(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "I don't know\\\\what you know!",
            target_mode="pleading"
        )
        self.wait(2)
        self.play(
            PiCreatureSays(
                self.students[0], "We know",
                target_mode="hooray",
            ),
            self.students[1].change, "happy",
            self.students[2].change, "happy",
        )
        self.wait(2)


class VastSpaceOfConsiderations(Scene):
    def construct(self):
        considerations = VGroup(*[
            TextMobject(phrase)
            for phrase in [
                "Define ``outer'' points",
                "Convex hulls",
                "Linear equations",
                "Sort points by when they're hit",
                "Sort points by some kind of angle?",
                "How does this permute the $n \\choose 2$ lines through pairs?",
                "Some points are hit more than others, can we quantify this?",
            ]
        ])
        considerations.arrange(DOWN, buff=MED_LARGE_BUFF, aligned_edge=LEFT)
        considerations.to_edge(LEFT)

        self.play(LaggedStart(*[
            FadeIn(mob, UP)
            for mob in considerations
        ], run_time=3, lag_ratio=0.2))


class WhatStaysConstantWrapper(Scene):
    CONFIG = {
        "camera_config": {
            "background_color": DARKER_GREY
        }
    }

    def construct(self):
        rect = ScreenRectangle()
        rect.set_height(6)
        rect.set_stroke(WHITE, 2)
        rect.set_fill(BLACK, 1)
        title1 = TextMobject("What stays constant?")
        title2 = TextMobject("Find an ", "``invariant''")
        title2[1].set_color(YELLOW)
        for title in [title1, title2]:
            title.scale(2)
            title.to_edge(UP)
        rect.next_to(title1, DOWN)

        self.add(rect)
        self.play(FadeInFromDown(title1))
        self.wait()
        self.play(
            FadeOut(title1, UP),
            FadeInFromDown(title2),
        )
        self.wait()


class CountHoles(Scene):
    def construct(self):
        labels = VGroup(
            TextMobject("Genus ", "0"),
            TextMobject("Genus ", "1"),
            TextMobject("Genus ", "2"),
        )

        labels.scale(2)
        labels.arrange(RIGHT, buff=1.5)
        labels.move_to(2 * DOWN)

        equation = TexMobject("y^2 = x^3 + ax + b")
        equation.scale(1.5)
        equation.shift(UP)
        equation.to_edge(LEFT)
        # arrow = TexMobject("\\approx").scale(2)
        arrow = Vector(2 * RIGHT)
        arrow.next_to(equation, RIGHT)

        equation_text = TextMobject("Some other problem")
        equation_text.next_to(equation, DOWN, MED_LARGE_BUFF)
        equation_text.match_width(equation)
        equation_text.set_color(YELLOW)

        self.play(LaggedStartMap(
            FadeInFromDown, labels,
            lag_ratio=0.5,
        ))
        self.wait()
        self.play(
            labels[1].shift, 4 * RIGHT,
            FadeOut(labels[0::2]),
        )
        self.play(
            FadeIn(equation, RIGHT),
            GrowArrow(arrow),
        )
        self.play(FadeIn(equation_text, UP))
        self.wait()


class LorenzTransform(Scene):
    def construct(self):
        grid = NumberPlane(
            # faded_line_ratio=0,
            # y_axis_config={
            #     "y_min": -10,
            #     "y_max": 10,
            # }
        )
        grid.scale(2)
        back_grid = grid.copy()
        back_grid.set_stroke(GREY, 0.5)
        # back_grid.set_opacity(0.5)

        c_lines = VGroup(Line(DL, UR), Line(DR, UL))
        c_lines.scale(FRAME_HEIGHT)
        c_lines.set_stroke(YELLOW, 3)

        equation = TexMobject(
            "d\\tau^2 = dt^2 - dx^2"
        )
        equation.scale(1.7)
        equation.to_corner(UL, buff=MED_SMALL_BUFF)
        equation.shift(2.75 * DOWN)
        equation.set_stroke(BLACK, 5, background=True)

        self.add(back_grid, grid, c_lines)
        self.add(equation)
        beta = 0.4
        self.play(
            grid.apply_matrix, np.array([
                [1, beta],
                [beta, 1],
            ]) / (1 - beta**2),
            run_time=2
        )
        self.wait()


class OnceACleverDiscovery(Scene):
    def construct(self):
        energy = TextMobject("energy")
        rect = SurroundingRectangle(energy)
        words = TextMobject("Once a clever discovery")
        vect = Vector(DR)
        vect.next_to(rect.get_top(), UL, SMALL_BUFF)
        words.next_to(vect.get_start(), UP)
        words.set_color(YELLOW)
        vect.set_color(YELLOW)

        self.play(
            ShowCreation(vect),
            ShowCreation(rect),
        )
        self.play(FadeInFromDown(words))
        self.wait()


class TerryTaoQuote(Scene):
    def construct(self):
        image = ImageMobject("TerryTao")
        image.set_height(4)
        name = TextMobject("Terence Tao")
        name.scale(1.5)
        name.next_to(image, DOWN, buff=0.2)
        tao = Group(image, name)
        tao.to_corner(DL, buff=MED_SMALL_BUFF)

        tiny_tao = ImageMobject("TerryTaoIMO")
        tiny_tao.match_height(image)
        tiny_tao.next_to(image, RIGHT, LARGE_BUFF)

        quote = self.get_quote()

        self.play(
            FadeInFromDown(image),
            Write(name),
        )
        self.wait()
        self.play(
            FadeIn(tiny_tao, LEFT)
        )
        self.wait()
        self.play(FadeOut(tiny_tao))

        #
        self.play(
            FadeIn(
                quote,
                lag_ratio=0.05,
                run_time=5,
                rate_func=bezier([0, 0, 1, 1])
            )
        )
        self.wait()
        story_line = Line()
        story_line.match_width(quote.story_part)
        story_line.next_to(quote.story_part, DOWN, buff=0)
        story_line.set_color(TEAL),
        self.play(
            quote.story_part.set_color, TEAL,
            ShowCreation(story_line),
            lag_ratio=0.2,
        )
        self.wait()

    def get_quote(self):
        story_words = "fables, stories, and anecdotes"
        quote = TextMobject(
            """
            \\Large
            ``Mathematical problems, or puzzles, are important to real mathematics
            (like solving real-life problems), just as fables, stories, and anecdotes
            are important to the young in understanding real life.''\\\\
            """,
            alignment="",
            arg_separator=" ",
            substrings_to_isolate=[story_words]
        )
        quote.story_part = quote.get_part_by_tex(story_words)
        quote.set_width(FRAME_WIDTH - 2.5)
        quote.to_edge(UP)

        return quote


class WindmillFairyTale(Scene):
    def construct(self):
        paths = SVGMobject(file_name="windmill_fairytale")

        paths.set_height(FRAME_HEIGHT - 1)
        paths.set_stroke(width=0)
        paths.set_fill([LIGHT_GREY, WHITE])

        for path in paths:
            path.reverse_points()

        self.play(Write(paths[0], run_time=3))
        self.wait()
        self.play(
            LaggedStart(
                FadeIn(paths[1], RIGHT),
                FadeIn(paths[2], RIGHT),
                lag_ratio=0.2,
                run_time=3,
            )
        )


class SolveAProblemOneDay(SpiritOfIMO, PiCreatureScene):
    def construct(self):
        randy = self.pi_creature
        light_bulb = Lightbulb()
        light_bulb.base = light_bulb[:3]
        light_bulb.light = light_bulb[3:]
        light_bulb.set_height(1)
        light_bulb.next_to(randy, UP, MED_LARGE_BUFF)

        light = self.get_light(light_bulb.get_center())

        bubble = ThoughtBubble()
        bubble.pin_to(randy)

        you = TextMobject("You")
        you.scale(1.5)
        arrow = Vector(LEFT)
        arrow.next_to(randy, RIGHT)
        you.next_to(arrow)

        self.play(
            ShowCreation(bubble),
            randy.change, "pondering",
        )
        self.play(
            FadeIn(you, LEFT),
            GrowArrow(arrow)
        )
        self.wait(2)
        self.play(
            FadeInFromDown(light_bulb),
            randy.change, "hooray",
        )
        self.play(
            LaggedStartMap(
                VFadeInThenOut, light,
                run_time=2
            ),
            randy.change, "thinking", light,
        )
        self.wait(2)


class QuixoteReference(Scene):
    def construct(self):
        rect = FullScreenFadeRectangle()
        rect.set_fill([DARK_GREY, GREY])

        windmill = SVGMobject("windmill")
        windmill.set_fill([GREY_BROWN, WHITE], 1)
        windmill.set_stroke(width=0)
        windmill.set_height(6)
        windmill.to_edge(RIGHT)
        # windmill.to_edge(DOWN, buff=0)

        quixote = SVGMobject("quixote")
        quixote.flip()
        quixote.set_height(4)
        quixote.to_edge(LEFT)
        quixote.set_stroke(BLACK, width=0)
        quixote.set_fill(BLACK, 1)
        quixote.align_to(windmill, DOWN)

        self.add(rect)
        # self.add(windmill)
        self.play(LaggedStart(
            DrawBorderThenFill(windmill),
            DrawBorderThenFill(
                quixote,
                stroke_width=1,
            ),
            lag_ratio=0.4,
            run_time=3
        ))
        self.wait()


class WindmillEndScreen(PatreonEndScreen):
    CONFIG = {
        "specific_patrons": [
            "Juan Benet",
            "Kurt Dicus",
            "Vassili Philippov",
            "Davie Willimoto",
            "Burt Humburg",
            "Hardik Meisheri",
            "L. Z.",
            "Matt Russell",
            "Scott Gray",
            "soekul",
            "Tihan Seale",
            "D. Sivakumar",
            "Richard Barthel",
            "Ali Yahya",
            "Arthur Zey",
            "dave nicponski",
            "Joseph Kelly",
            "Kaustuv DeBiswas",
            "kkm",
            "Lambda AI Hardware",
            "Lukas Biewald",
            "Mark Heising",
            "Nicholas Cahill",
            "Peter Mcinerney",
            "Quantopian",
            "Roy Larson",
            "Scott Walter, Ph.D.",
            "Tauba Auerbach",
            "Yana Chernobilsky",
            "Yu Jun",
            "Jordan Scales",
            "Lukas -krtek.net- Novy",
            "Britt Selvitelle",
            "David Gow",
            "J",
            "Jonathan Wilson",
            "Joseph John Cox",
            "Magnus Dahlström",
            "Randy C. Will",
            "Ryan Atallah",
            "Luc Ritchie",
            "1stViewMaths",
            "Adrian Robinson",
            "Aidan Shenkman",
            "Alex Mijalis",
            "Alexis Olson",
            "Andreas Benjamin Brössel",
            "Andrew Busey",
            "Ankalagon",
            "Antoine Bruguier",
            "Antonio Juarez",
            "Arjun Chakroborty",
            "Art Ianuzzi",
            "Austin Goodman",
            "Awoo",
            "Ayan Doss",
            "AZsorcerer",
            "Barry Fam",
            "Bernd Sing",
            "Boris Veselinovich",
            "Bradley Pirtle",
            "Brian Staroselsky",
            "Charles Southerland",
            "Charlie N",
            "Chris Connett",
            "Christian Kaiser",
            "Clark Gaebel",
            "Cooper Jones",
            "Danger Dai",
            "Daniel Pang",
            "Dave B",
            "Dave Kester",
            "David B. Hill",
            "David Clark",
            "DeathByShrimp",
            "Delton Ding",
            "Dheeraj Vepakomma",
            "eaglle",
            "Empirasign",
            "emptymachine",
            "Eric Younge",
            "Ero Carrera",
            "Eryq Ouithaqueue",
            "Federico Lebron",
            "Fernando Via Canel",
            "Gero Bone-Winkel",
            "Giovanni Filippi",
            "Hal Hildebrand",
            "Hitoshi Yamauchi",
            "Isaac Jeffrey Lee",
            "Ivan Sorokin",
            "j eduardo perez",
            "Jacob Harmon",
            "Jacob Hartmann",
            "Jacob Magnuson",
            "Jameel Syed",
            "Jason Hise",
            "Jeff Linse",
            "Jeff Straathof",
            "John C. Vesey",
            "John Griffith",
            "John Haley",
            "John V Wertheim",
            "Jonathan Eppele",
            "Jordan A Purcell",
            "Josh Kinnear",
            "Joshua Claeys",
            "Kai-Siang Ang",
            "Kanan Gill",
            "Kartik Cating-Subramanian",
            "L0j1k",
            "Lee Redden",
            "Linh Tran",
            "Ludwig Schubert",
            "Magister Mugit",
            "Mark B Bahu",
            "Martin Price",
            "Mathias Jansson",
            "Matt Langford",
            "Matt Roveto",
            "Matthew Bouchard",
            "Matthew Cocke",
            "Michael Faust",
            "Michael Hardel",
            "Mirik Gogri",
            "Mustafa Mahdi",
            "Márton Vaitkus",
            "Nero Li",
            "Nikita Lesnikov",
            "Omar Zrien",
            "Owen Campbell-Moore",
            "Patrick Lucas",
            "Peter Ehrnstrom",
            "RedAgent14",
            "rehmi post",
            "Ripta Pasay",
            "Rish Kundalia",
            "Roman Sergeychik",
            "Roobie",
            "Ryan Williams",
            "Sebastian Garcia",
            "Solara570",
            "Steven Siddals",
            "Stevie Metke",
            "Tal Einav",
            "Ted Suzman",
            "Thomas Tarler",
            "Tianyu Ge",
            "Tom Fleming",
            "Tyler VanValkenburg",
            "Valeriy Skobelev",
            "Vinicius Reis",
            "Xuanji Li",
            "Yavor Ivanov",
            "YinYangBalance.Asia",
            "Zach Cardwell",
        ],
    }


class Thumbnail(WindmillScene):
    CONFIG = {
        "dot_config": {
            "radius": 0.15,
            "stroke_width": 1,
        },
        "random_seed": 7,
        "animate": False,
    }

    def construct(self):
        points = self.get_random_point_set(11)
        points[:, 0] *= 1.7
        points += 0.5 * LEFT

        points[1] = ORIGIN
        points[10] += LEFT
        points[6] += 3 * RIGHT

        windmill = self.get_windmill(
            points, points[1],
            angle=45 * DEGREES,
        )
        dots = self.get_dots(points)
        # rects = self.get_left_right_colorings(windmill)
        pivot_dot = self.get_pivot_dot(windmill)
        pivot_dot.scale(2)
        pivot_dot.set_color(WHITE)

        new_pivot = points[5]
        new_pivot2 = points[3]

        flash = Flash(pivot_dot, flash_radius=0.5)

        wa = windmill.get_angle()
        arcs = VGroup(*[
            Arc(
                start_angle=wa + a,
                angle=90 * DEGREES,
                radius=1.5,
                stroke_width=10,
            ).add_tip(tip_length=0.7)
            for a in [0, PI]
        ])
        arcs.move_to(windmill.pivot)
        arcs.set_color([LIGHT_GREY, WHITE])

        polygon1 = Polygon(
            (FRAME_HEIGHT * UP + FRAME_WIDTH * LEFT) / 2,
            (FRAME_HEIGHT * UP + FRAME_HEIGHT * RIGHT) / 2,
            (FRAME_HEIGHT * DOWN + FRAME_HEIGHT * LEFT) / 2,
            (FRAME_HEIGHT * DOWN + FRAME_WIDTH * LEFT) / 2,
        )
        polygon1.set_color([BLUE, DARKER_GREY])
        polygon1.set_fill(opacity=0.5)
        polygon2 = Polygon(
            (FRAME_HEIGHT * UP + FRAME_WIDTH * RIGHT) / 2,
            (FRAME_HEIGHT * UP + FRAME_HEIGHT * RIGHT) / 2,
            (FRAME_HEIGHT * DOWN + FRAME_HEIGHT * LEFT) / 2,
            (FRAME_HEIGHT * DOWN + FRAME_WIDTH * RIGHT) / 2,
        )
        polygon2.set_sheen_direction(DR)
        polygon2.set_color([GREY_BROWN, BLACK])
        polygon2.set_fill(opacity=1)

        self.add(polygon1, polygon2)
        # self.add(rects[0])
        self.add(windmill, dots, pivot_dot)
        self.add(arcs)
        self.add(flash.mobject)
        self.add_dot_color_updater(dots, windmill, color2=WHITE)

        words = TextMobject("Next\\\\", "pivot")
        words2 = TextMobject("Next\\\\", "next\\\\", "pivot", alignment="")
        words.scale(2)
        words2.scale(2)
        # words.next_to(windmill.pivot, RIGHT)
        words.to_edge(UR)
        words2.to_corner(DL)

        arrow = Arrow(words[1].get_left(), new_pivot, buff=0.6)
        arrow.set_stroke(width=10)
        arrow.set_color(YELLOW)
        arrow2 = Arrow(words2[-1].get_right(), new_pivot2, buff=0.6)
        arrow2.match_style(arrow)
        arrow.rotate(
            arrow2.get_angle() + PI - arrow.get_angle(),
            about_point=new_pivot,
        )

        self.add(words, arrow)
        self.add(words2, arrow2)

        # for i, dot in enumerate(dots):
        #     self.add(Integer(i).move_to(dot))

        if self.animate:
            sorted_dots = VGroup(*dots)
            sorted_dots.sort(lambda p: np.dot(p, DR))

            self.play(
                polygon1.shift, FRAME_WIDTH * LEFT,
                polygon2.shift, FRAME_WIDTH * RIGHT,
                LaggedStart(*[
                    ApplyMethod(mob.scale, 0)
                    for mob in [sorted_dots[6], *flash.mobject, windmill, pivot_dot]
                ]),
                LaggedStart(*[
                    ApplyMethod(dot.to_edge, LEFT, {"buff": -1})
                    for dot in sorted_dots[:6]
                ]),
                LaggedStart(*[
                    ApplyMethod(dot.to_edge, RIGHT, {"buff": -1})
                    for dot in sorted_dots[7:]
                ]),
                LaggedStart(*[
                    FadeOut(word, RIGHT)
                    for word in words
                ]),
                LaggedStart(*[
                    FadeOut(word, LEFT)
                    for word in words2
                ]),
                LaggedStartMap(
                    Uncreate,
                    VGroup(arrow, arrow2, *arcs),
                ),
                run_time=3,
            )


class ThumbanailAnimated(Thumbnail):
    CONFIG = {
        "animate": True,
    }


class Thumbnail2(Scene):
    def construct(self):
        words = TextMobject("Olympics\\\\", "for\\\\", "math", alignment="")
        # words.arrange(DOWN, aligned_edge=LEFT)

        words.set_height(FRAME_HEIGHT - 1.5)
        words.to_edge(LEFT)

        logo = ImageMobject("imo_logo")
        logo.set_height(4.5)
        logo.to_corner(DR, buff=LARGE_BUFF)

        rect = FullScreenFadeRectangle()
        rect.set_fill([GREY, BLACK], 1)

        self.clear()
        self.add(rect)
        self.add(words)
        self.add(logo)
