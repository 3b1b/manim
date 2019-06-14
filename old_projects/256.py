from manimlib.imports import *

from old_projects.crypto import sha256_tex_mob, bit_string_to_mobject, BitcoinLogo

def get_google_logo():
    result = SVGMobject(
        file_name = "google_logo",
        height = 0.75
    )
    blue, red, yellow, green = [
        "#4885ed", "#db3236", "#f4c20d", "#3cba54"
    ]
    colors = [red, yellow, blue, green, red, blue]
    result.set_color_by_gradient(*colors)
    return result

class LastVideo(Scene):
    def construct(self):
        title = TextMobject("Crypto", "currencies", arg_separator = "")
        title[0].set_color(YELLOW)
        title.scale(1.5)
        title.to_edge(UP)
        screen_rect = ScreenRectangle(height = 6)
        screen_rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(screen_rect))
        self.wait()

class BreakUp2To256(PiCreatureScene):
    def construct(self):
        self.initialize_bits()
        self.add_number()
        self.break_up_as_powers_of_two()
        self.break_up_as_four_billions()
        self.reorganize_four_billions()

    def initialize_bits(self):
        bits = bit_string_to_mobject("")
        bits.to_corner(UP+LEFT)
        one = TexMobject("1")[0]
        one.replace(bits[0], dim_to_match = 1)
        self.add(bits)
        self.add_foreground_mobject(VGroup(*bits[-15:]))
        self.number = 0
        self.bits = bits
        self.one = one
        self.zero = bits[0].copy()

    def add_number(self):
        brace = Brace(self.bits, RIGHT)

        number, possibilities = expression = TextMobject(
            "$2^{256}$", "possibilities"
        )
        number.set_color(YELLOW)
        expression.next_to(brace, RIGHT)

        words = TextMobject("Seems big...I guess...")
        words.next_to(self.pi_creature.get_corner(UP+LEFT), UP)

        self.play(
            self.pi_creature.change, "raise_right_hand",
            GrowFromCenter(brace),
            Write(expression, run_time = 1)
        )
        self.wait()
        self.play(
            self.pi_creature.change, "maybe",
            Write(words)
        )
        self.wait(2)
        self.play(
            self.pi_creature.change, "happy",
            FadeOut(words)
        )
        self.wait()

        self.expression = expression
        self.bits_brace = brace

    def break_up_as_powers_of_two(self):
        bits = self.bits
        bits.generate_target()
        subgroups = [
            VGroup(*bits.target[32*i:32*(i+1)])
            for i in range(8)
        ]
        subexpressions = VGroup()
        for i, subgroup in enumerate(subgroups):
            subgroup.shift(i*MED_LARGE_BUFF*DOWN)
            subexpression = TextMobject(
                "$2^{32}$", "possibilities"
            )
            subexpression[0].set_color(GREEN)
            subexpression.next_to(subgroup, RIGHT)
            subexpressions.add(subexpression)

        self.play(
            FadeOut(self.bits_brace),
            ReplacementTransform(
                VGroup(self.expression),
                subexpressions
            ),
            MoveToTarget(bits)
        )
        self.play(self.pi_creature.change, "pondering")
        self.wait()


        self.subexpressions = subexpressions

    def break_up_as_four_billions(self):
        new_subexpressions = VGroup()
        for subexpression in self.subexpressions:
            new_subexpression = TextMobject(
                "4 Billion", "possibilities"
            )
            new_subexpression[0].set_color(YELLOW)
            new_subexpression.move_to(subexpression, LEFT)
            new_subexpressions.add(new_subexpression)

        self.play(
            Transform(
                self.subexpressions, new_subexpressions,
                run_time = 2,
                lag_ratio = 0.5,
            ),
            FadeOut(self.pi_creature)
        )
        self.wait(3)

    def reorganize_four_billions(self):
        target = VGroup(*[
            TextMobject(
                "$\\big($", "4 Billion", "$\\big)$",
                arg_separator = ""
            )
            for x in range(8)
        ])
        target.arrange(RIGHT, buff = SMALL_BUFF)
        target.to_edge(UP)
        target.set_width(FRAME_WIDTH - LARGE_BUFF)
        parens = VGroup(*it.chain(*[
            [t[0], t[2]] for t in target
        ]))
        target_four_billions = VGroup(*[t[1] for t in target])
        target_four_billions.set_color(YELLOW)
        four_billions, to_fade = [
            VGroup(*[se[i] for se in self.subexpressions])
            for i in range(2)
        ]

        self.play(
            self.bits.to_corner, DOWN+LEFT,
            Transform(four_billions, target_four_billions),
            LaggedStartMap(FadeIn, parens),
            FadeOut(to_fade)
        )
        self.wait()

    ######

    def wait(self, time = 1):
        self.play(Animation(self.bits, run_time = time))

    def update_frame(self, *args, **kwargs):
        self.number += 1
        new_bit_string = bin(self.number)[2:]
        for i, bit in enumerate(reversed(new_bit_string)):
            index = -i-1
            bit_mob = self.bits[index]
            if bit == "0":
                new_mob = self.zero.copy()
            else:
                new_mob = self.one.copy()
            new_mob.replace(bit_mob, dim_to_match = 1)
            Transform(bit_mob, new_mob).update(1)
        Scene.update_frame(self, *args, **kwargs)

class ShowTwoTo32(Scene):
    def construct(self):
        mob = TexMobject("2^{32} = 4{,}294{,}967{,}296")
        mob.scale(1.5)
        self.add(mob)
        self.wait()

class MainBreakdown(Scene):
    CONFIG = {
        "n_group_rows" : 8,
        "n_group_cols" : 8,
    }
    def construct(self):
        self.add_four_billions()
        self.gpu_packed_computer()
        self.kilo_google()
        self.half_all_people_on_earth()
        self.four_billion_earths()
        self.four_billion_galxies()
        self.show_time_scale()
        self.show_probability()

    def add_four_billions(self):
        top_line = VGroup()
        four_billions = VGroup()
        for x in range(8):
            mob = TextMobject(
                "$\\big($", "4 Billion", "$\\big)$",
                arg_separator = ""
            )
            top_line.add(mob)
            four_billions.add(mob[1])
        top_line.arrange(RIGHT, buff = SMALL_BUFF)
        top_line.set_width(FRAME_WIDTH - LARGE_BUFF)
        top_line.to_edge(UP)
        four_billions.set_color(YELLOW)
        self.add(top_line)

        self.top_line = top_line
        self.four_billions = four_billions

    def gpu_packed_computer(self):
        self.show_gpu()
        self.cram_computer_with_gpus()

    def show_gpu(self):
        gpu = SVGMobject(
            file_name = "gpu",
            height = 1,
            fill_color = LIGHT_GREY,
        )
        name = TextMobject("Graphics", "Processing", "Unit")
        for word in name:
            word[0].set_color(BLUE)
        name.to_edge(LEFT)
        gpu.next_to(name, UP)

        hash_names = VGroup(*[
            TextMobject("hash")
            for x in range(10)
        ])
        hash_names.arrange(DOWN, buff = MED_SMALL_BUFF)
        hash_names.next_to(name, RIGHT, buff = 2)

        paths = VGroup()
        for hash_name in hash_names:
            hash_name.add_background_rectangle(opacity = 0.5)
            path = VMobject()
            start_point = name.get_right() + SMALL_BUFF*RIGHT
            end_point = start_point + (4+hash_name.get_width())*RIGHT
            path.set_points([
                start_point, 
                start_point+RIGHT,
                hash_name.get_left()+LEFT,
                hash_name.get_left(),
                hash_name.get_left(),
                hash_name.get_right(),
                hash_name.get_right(),
                hash_name.get_right() + RIGHT,
                end_point + LEFT,
                end_point,
            ])
            paths.add(path)
        paths.set_stroke(width = 3)
        paths.set_color_by_gradient(BLUE, GREEN)
        def get_passing_flash():
            return ShowPassingFlash(
                paths,
                lag_ratio = 0,
                time_width = 0.7,
                run_time = 2,
            )
        rate_words = TextMobject(
            "$<$ 1 Billion", "Hashes/sec"
        )
        rate_words.next_to(name, DOWN)

        self.play(FadeIn(name))
        self.play(DrawBorderThenFill(gpu))
        self.play(
            get_passing_flash(),
            FadeIn(hash_names)
        )
        for x in range(2):
            self.play(
                get_passing_flash(),
                Animation(hash_names)
            )
        self.play(
            Write(rate_words, run_time = 2),
            get_passing_flash(),
            Animation(hash_names)
        )
        self.play(get_passing_flash(), Animation(hash_names))
        self.play(*list(map(FadeOut, [name, hash_names])))

        self.gpu = gpu
        self.rate_words = rate_words

    def cram_computer_with_gpus(self):
        gpu = self.gpu
        gpus = VGroup(gpu, *[gpu.copy() for x in range(5)])

        rate_words = self.rate_words
        four_billion = self.four_billions[0]

        laptop = Laptop()
        laptop.next_to(rate_words, RIGHT)
        laptop.to_edge(RIGHT)
        new_rate_words = TextMobject("4 Billion", "Hashes/sec")
        new_rate_words.move_to(rate_words)
        new_rate_words[0].set_color(BLUE)

        hps, h_line, target_laptop = self.get_fraction(
            0, TextMobject("H/s"), Laptop()
        )
        hps.scale_in_place(0.7)

        self.play(FadeIn(laptop))
        self.play(
            gpus.arrange, RIGHT, SMALL_BUFF,
            gpus.next_to, rate_words, UP,
            gpus.to_edge, LEFT
        )
        self.play(
            Transform(
                four_billion.copy(), new_rate_words[0],
                remover = True,
            ),
            Transform(rate_words, new_rate_words)
        )
        self.wait()
        self.play(
            LaggedStartMap(
                ApplyFunction, gpus,
                lambda g : (
                    lambda m : m.scale(0.01).move_to(laptop),
                    g
                ),
                remover = True
            )
        )
        self.wait()
        self.play(
            Transform(
                rate_words[0], four_billion.copy().set_color(BLUE),
                remover = True,
            ),
            four_billion.set_color, BLUE,
            Transform(rate_words[1], hps),
        )
        self.play(
            Transform(laptop, target_laptop),
            ShowCreation(h_line),
        )
        self.wait()

    def kilo_google(self):
        self.create_four_billion_copies(1, Laptop())
        google = self.get_google_logo()
        google.next_to(
            self.group_of_four_billion_things, UP,
            buff = LARGE_BUFF,
            aligned_edge = LEFT
        )
        google.shift(RIGHT)
        millions = TextMobject("$\\sim$ Millions of servers")
        millions.next_to(google, RIGHT)
        plus_plus = TexMobject("++")
        plus_plus.next_to(google, RIGHT, SMALL_BUFF)
        plus_plus.set_stroke(width = 2)
        kilo = TextMobject("Kilo")
        kilo.scale(1.5)
        kilo.next_to(google[-1], LEFT, SMALL_BUFF, DOWN)
        kilogoogle = VGroup(kilo, google, plus_plus)

        four_billion = self.four_billions[1]
        laptop, h_line, target_kilogoogle = self.get_fraction(
            1, Laptop(), self.get_kilogoogle()
        )

        self.revert_to_original_skipping_status()
        self.play(DrawBorderThenFill(google))
        self.wait(2)
        self.play(Write(millions))
        self.wait(2)
        self.play(LaggedStartMap(
            Indicate, self.group_of_four_billion_things,
            run_time = 4,
            rate_func = there_and_back,
            lag_ratio = 0.25,
        ))
        self.play(FadeOut(millions), FadeIn(plus_plus))
        self.play(Write(kilo))
        self.wait()
        self.play(
            four_billion.restore,
            FadeOut(self.group_of_four_billion_things)
        )
        self.play(
            Transform(kilogoogle, target_kilogoogle),
            FadeIn(laptop),
            FadeIn(h_line),
        )
        self.wait()

    def half_all_people_on_earth(self):
        earth = self.get_earth()
        people = TextMobject("7.3 Billion people")
        people.next_to(earth, RIGHT)
        group = VGroup(earth, people)
        group.next_to(self.four_billions, DOWN, MED_LARGE_BUFF)
        group.shift(RIGHT)

        kg, h_line, target_earth = self.get_fraction(
            2, self.get_kilogoogle(), self.get_earth(), 
        )

        self.play(
            GrowFromCenter(earth),
            Write(people)
        )
        self.wait()
        self.create_four_billion_copies(2, self.get_kilogoogle())
        self.wait()
        self.play(
            self.four_billions[2].restore,
            Transform(earth, target_earth),
            FadeIn(h_line),
            FadeIn(kg),
            FadeOut(self.group_of_four_billion_things),
            FadeOut(people)
        )
        self.wait()

    def four_billion_earths(self):
        self.create_four_billion_copies(
            3, self.get_earth()
        )
        milky_way = ImageMobject("milky_way")
        milky_way.set_height(3)
        milky_way.to_edge(LEFT, buff = 0)
        milky_way.shift(DOWN)

        n_stars_estimate = TextMobject("100 to 400 \\\\ billion stars")
        n_stars_estimate.next_to(milky_way, RIGHT)
        n_stars_estimate.shift(UP)

        earth, h_line, denom = self.get_fraction(
            3, self.get_earth(), self.get_galaxy()
        )

        self.revert_to_original_skipping_status()
        self.play(FadeIn(milky_way))
        self.play(Write(n_stars_estimate))
        self.wait()
        self.play(LaggedStartMap(
            Indicate, self.group_of_four_billion_things,
            rate_func = there_and_back,
            lag_ratio = 0.2,
            run_time = 3,
        ))
        self.wait()
        self.play(
            ReplacementTransform(
                self.group_of_four_billion_things,
                VGroup(earth)
            ),
            ShowCreation(h_line),
            FadeIn(denom),
            self.four_billions[3].restore,
            FadeOut(milky_way),
            FadeOut(n_stars_estimate),
        )
        self.wait()

    def four_billion_galxies(self):
        self.create_four_billion_copies(4, self.get_galaxy())
        num, h_line, denom = fraction = self.get_fraction(
            4, self.get_galaxy(), TextMobject("GGSC").set_color(BLUE)
        )

        name = TextMobject(
            "Giga", "Galactic \\\\", " Super", " Computer",
            arg_separator = ""
        )
        for word in name:
            word[0].set_color(BLUE)
        name.next_to(self.group_of_four_billion_things, UP)

        self.play(Write(name))
        self.wait()
        self.play(
            self.four_billions[4].restore,
            ReplacementTransform(
                self.group_of_four_billion_things, VGroup(num),
                run_time = 2,
                lag_ratio = 0.5
            ),
            ShowCreation(h_line),
            ReplacementTransform(
                name, denom
            ),
        )
        self.wait()

    def show_time_scale(self):
        fb1, fb2 = self.four_billions[5:7]
        seconds_to_years = TextMobject("seconds $\\approx$ 126.8 years")
        seconds_to_years.shift(LEFT)
        years_to_eons = TextMobject(
            "$\\times$ 126.8 years", "$\\approx$ 507 Billion years", 
        )
        years_to_eons.next_to(
            seconds_to_years, DOWN, 
            aligned_edge = LEFT,
        )
        universe_lifetimes = TextMobject("$\\approx 37 \\times$ Age of universe")
        universe_lifetimes.next_to(
            years_to_eons[1], DOWN, 
            aligned_edge = LEFT
        )

        for fb, words in (fb1, seconds_to_years), (fb2, years_to_eons):
            self.play(
                fb.scale, 1.3,
                fb.next_to, words, LEFT, 
                fb.set_color, BLUE,
                Write(words)
            )
            self.wait()
        self.play(Write(universe_lifetimes))
        self.wait()

    def show_probability(self):
        four_billion = self.four_billions[7]
        words = TextMobject(
            "1 in ", "4 Billion\\\\",
            "chance of success"
        )
        words.next_to(four_billion, DOWN, buff = MED_LARGE_BUFF)
        words.to_edge(RIGHT)
        words[1].set_color(BLUE)

        self.play(
            Write(VGroup(*words[::2])),
            Transform(four_billion, words[1])
        )
        self.wait()


    ############

    def create_four_billion_copies(self, index, mobject):
        four_billion = self.four_billions[index]
        four_billion.set_color(BLUE)
        four_billion.save_state()

        group = VGroup(*[
            VGroup(*[
                mobject.copy().set_height(0.25)
                for x in range(self.n_group_rows)
            ]).arrange(DOWN, buff = SMALL_BUFF)
            for y in range(self.n_group_cols-1)
        ])
        dots = TexMobject("\\dots")
        group.add(dots)
        group.add(*[group[0].copy() for x in range(2)])
        group.arrange(RIGHT, buff = SMALL_BUFF)
        group.set_height(FRAME_Y_RADIUS)
        max_width = 1.25*FRAME_X_RADIUS
        if group.get_width() > max_width:
            group.set_width(max_width)
        group.to_corner(DOWN+RIGHT)
        group = VGroup(*it.chain(*group))

        brace = Brace(group, LEFT)

        self.play(
            four_billion.scale, 2,
            four_billion.next_to, brace, LEFT,
            GrowFromCenter(brace),
            LaggedStartMap(
                FadeIn, group,
                run_time = 3,
                lag_ratio = 0.2
            )
        )
        self.wait()

        group.add_to_back(brace)
        self.group_of_four_billion_things = group

    def get_fraction(self, index, numerator, denominator):
        four_billion = self.four_billions[index]
        if hasattr(four_billion, "saved_state"):
            four_billion = four_billion.saved_state

        space = LARGE_BUFF
        h_line = Line(LEFT, RIGHT)
        h_line.set_width(four_billion.get_width())
        h_line.next_to(four_billion, DOWN, space)
        for mob in numerator, denominator:
            mob.set_height(0.75*space)
            max_width = h_line.get_width()
            if mob.get_width() > max_width:
                mob.set_width(max_width)
        numerator.next_to(h_line, UP, SMALL_BUFF)
        denominator.next_to(h_line, DOWN, SMALL_BUFF)
        fraction = VGroup(numerator, h_line, denominator)

        return fraction

    def get_google_logo(self):
        return get_google_logo()

    def get_kilogoogle(self):
        G = self.get_google_logo()[-1]
        kilo = TextMobject("K")
        kilo.scale(1.5)
        kilo.next_to(G[-1], LEFT, SMALL_BUFF, DOWN)
        plus_plus = TexMobject("++")
        plus_plus.set_stroke(width = 1)
        plus_plus.next_to(G, RIGHT, SMALL_BUFF)
        return VGroup(kilo, G, plus_plus)

    def get_earth(self):
        earth = SVGMobject(
            file_name = "earth",
            height = 1.5,
            fill_color = BLACK,
        )
        circle = Circle(
            stroke_width = 3,
            stroke_color = GREEN,
            fill_opacity = 1,
            fill_color = BLUE_C,
        )
        circle.replace(earth)
        earth.add_to_back(circle)
        return earth

    def get_galaxy(self):
        return SVGMobject(
            file_name = "galaxy",
            fill_opacity = 0,
            stroke_width = 3,
            stroke_color = WHITE,
            height = 1,
        )
        
class WriteTWoTo160(Scene):
    def construct(self):
        mob = TextMobject("$2^{160}$ ", "Hashes/sec")
        mob[0].set_color(BLUE)
        mob.scale(2)
        self.play(Write(mob))
        self.wait()

class StateOfBitcoin(TeacherStudentsScene):
    def construct(self):
        title = TextMobject("Total", "B", "mining")
        title.to_edge(UP)
        bitcoin_logo = BitcoinLogo()
        bitcoin_logo.set_height(0.5)
        bitcoin_logo.move_to(title[1])
        title.remove(title[1])

        rate = TextMobject(
            "5 Billion Billion", 
            "$\\frac{\\text{Hashes}}{\\text{Second}}$"
        )
        rate.next_to(title, DOWN, MED_LARGE_BUFF)

        google = get_google_logo()
        kilo = TextMobject("Kilo")
        kilo.scale(1.5)
        kilo.next_to(google[-1], LEFT, SMALL_BUFF, DOWN)
        third = TexMobject("1 \\over 3")
        third.next_to(kilo, LEFT)
        kilogoogle = VGroup(*it.chain(third, kilo, google))
        kilogoogle.sort()
        kilogoogle.next_to(rate, DOWN, MED_LARGE_BUFF)

        rate.save_state()
        rate.shift(DOWN)
        rate.set_fill(opacity = 0)

        all_text = VGroup(title, bitcoin_logo, rate, kilogoogle)

        gpu = SVGMobject(
            file_name = "gpu",
            height = 1,
            fill_color = LIGHT_GREY,
        )
        gpu.shift(0.5*FRAME_X_RADIUS*RIGHT)
        gpu_name = TextMobject("GPU")
        gpu_name.set_color(BLUE)
        gpu_name.next_to(gpu, UP)
        gpu_group = VGroup(gpu, gpu_name)
        gpu_group.to_edge(UP)
        cross = Cross(gpu_group)
        gpu_group.add(cross)

        asic = TextMobject(
            "Application", "Specific\\\\", "Integrated", "Circuit"
        )
        for word in asic:
            word[0].set_color(YELLOW)
        asic.move_to(gpu)
        asic.to_edge(UP)
        asic.shift(LEFT)
        circuit = SVGMobject(
            file_name = "circuit",
            height = asic.get_height(),
            fill_color = WHITE,
        )
        random.shuffle(circuit.submobjects)
        circuit.set_color_by_gradient(WHITE, GREY)
        circuit.next_to(asic, RIGHT)
        asic_rate = TextMobject("Trillion hashes/sec")
        asic_rate.next_to(asic, DOWN, MED_LARGE_BUFF)
        asic_rate.set_color(GREEN)

        self.play(
            Write(title),
            DrawBorderThenFill(bitcoin_logo)
        )
        self.play(
            self.teacher.change, "raise_right_hand",
            rate.restore,
        )
        self.change_student_modes(*["pondering"]*3)
        self.play(LaggedStartMap(FadeIn, kilogoogle))
        self.change_student_modes(*["surprised"]*3)
        self.wait()
        self.change_student_modes(
            *["plain"]*3,
            added_anims = [
                all_text.to_edge, LEFT,
                self.teacher.change_mode, "happy"
            ],
            look_at_arg = gpu
        )
        self.play(
            Write(gpu_name),
            DrawBorderThenFill(gpu)
        )
        self.play(ShowCreation(cross))
        self.wait()
        self.play(
            Write(asic),
            gpu_group.to_edge, DOWN,
            self.teacher.change, "raise_right_hand",
        )

        self.change_student_modes(
            *["pondering"]*3,
            added_anims = [Write(asic_rate)]
        )
        self.play(LaggedStartMap(
            FadeIn, circuit,
            run_time = 3,
            lag_ratio = 0.2,
        ))
        self.wait()

class QAndA(PiCreatureScene):
    def construct(self):
        self.pi_creature.center().to_edge(DOWN)
        self.show_powers_of_two()

        num_subscriber_words = TexMobject(
            "> 2^{18} = 262{,}144", "\\text{ subscribers}"
        )
        num_subscriber_words.to_edge(UP)
        num_subscriber_words.shift(RIGHT)
        num_subscriber_words.set_color_by_tex("subscribers", RED)

        q_and_a = TextMobject("Q\\&A")
        q_and_a.next_to(self.pi_creature.get_corner(UP+LEFT), UP)
        q_and_a.save_state()
        q_and_a.shift(DOWN)
        q_and_a.set_fill(opacity = 0)

        reddit = TextMobject("reddit.com/r/3blue1brown")
        reddit.next_to(num_subscriber_words, DOWN, LARGE_BUFF)
        twitter = TextMobject("@3blue1brown")
        twitter.set_color(BLUE_C)
        twitter.next_to(reddit, DOWN)

        self.play(Write(num_subscriber_words))
        self.play(self.pi_creature.change, "gracious", num_subscriber_words)
        self.wait()
        self.play(
            q_and_a.restore,
            self.pi_creature.change, "raise_right_hand",
        )
        self.wait()
        self.play(Write(reddit))
        self.wait()
        self.play(
            FadeIn(twitter),
            self.pi_creature.change_mode, "shruggie"
        )
        self.wait(2)

    def show_powers_of_two(self):
        rows = 16
        cols = 64
        dots = VGroup(*[
            VGroup(*[
                Dot() for x in range(rows)
            ]).arrange(DOWN, buff = SMALL_BUFF)
            for y in range(cols)
        ]).arrange(RIGHT, buff = SMALL_BUFF)
        dots.set_width(FRAME_WIDTH - 2*LARGE_BUFF)
        dots.next_to(self.pi_creature, UP)
        dots = VGroup(*it.chain(*dots))
        top = dots.get_top()
        dots.sort(
            lambda p : get_norm(p-top)
        )

        powers_of_two = VGroup(*[
            Integer(2**i)
            for i in range(int(np.log2(rows*cols))+1)
        ])

        curr_power = powers_of_two[0]
        curr_power.to_edge(UP)
        self.play(
            Write(curr_power),
            FadeIn(dots[0])
        )
        for i, power_of_two in enumerate(powers_of_two):
            if i == 0:
                continue
            power_of_two.to_edge(UP)
            self.play(
                FadeIn(VGroup(*dots[2**(i-1) : 2**i])),
                Transform(
                    curr_power, power_of_two,
                    rate_func = squish_rate_func(smooth, 0, 0.5)
                )
            )
        self.wait()
        self.play(
            FadeOut(dots),
            FadeOut(powers_of_two)
        )

class Thumbnail(Scene):
    def construct(self):
        num = TexMobject("2^{256}")
        num.set_height(2)
        num.set_color(BLUE_C)
        num.set_stroke(BLUE_B, 3)
        num.shift(MED_SMALL_BUFF*UP)
        num.add_background_rectangle(opacity = 1)
        num.background_rectangle.scale_in_place(1.5)
        self.add(num)

        background_num_str = "115792089237316195423570985008687907853269984665640564039457584007913129639936"
        n_chars = len(background_num_str)
        new_str = ""
        for i, char in enumerate(background_num_str):
            new_str += char
            # if i%3 == 1:
            #     new_str += "{,}"
            if i%(n_chars/4) == 0:
                new_str += " \\\\ "
        background_num = TexMobject(new_str)
        background_num.set_width(FRAME_WIDTH - LARGE_BUFF)
        background_num.set_fill(opacity = 0.2)

        secure = TextMobject("Secure?")
        secure.scale(4)
        secure.shift(FRAME_Y_RADIUS*DOWN/2)
        secure.set_color(RED)
        secure.set_stroke(RED_A, 3)

        lock = SVGMobject(
            file_name = "shield_locked",
            fill_color = WHITE,
        )
        lock.set_height(6)

        self.add(background_num, num)























