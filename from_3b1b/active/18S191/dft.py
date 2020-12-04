from manimlib.imports import *


class IntroduceDFT(Scene):
    def construct(self):
        # Create signal
        N = 8
        np.random.seed(2)
        signal = 3 * np.random.random(N)
        signal[signal < 0.5] = 0.5

        axes = Axes(
            (0, 8),
            (0, 2, 0.5),
            width=12,
            height=4,
        )
        axes.x_axis.add_numbers()
        axes.y_axis.add_numbers(number_config={"num_decimal_places": 1}, excluding=[0])

        vectors = VGroup(*(
            Arrow(axes.c2p(x, 0), axes.c2p(x, signal[x]), buff=0)
            for x in range(N)
        ))
        vectors.set_submobject_colors_by_gradient(BLUE, YELLOW)
        vectors.set_stroke(BLACK, 2, background=True)

        self.add(axes)
        self.play(LaggedStartMap(GrowArrow, vectors, lag_ratio=0.3))
        self.wait()

        # Label signal
        s_title = TextMobject("List of value: ", "$s$", font_size=72)
        s_title.to_edge(UP)
        self.play(FadeIn(s_title, UP))
        self.wait()

        s_labels = VGroup(*(
            TexMobject("s", f"[{x}]")
            for x in range(N)
        ))
        for label, vector in zip(s_labels, vectors):
            label.next_to(vector, UP, SMALL_BUFF)
            label.match_color(vector)
            label.add_background_rectangle()

        s_labels[0].shift(MED_SMALL_BUFF * RIGHT)

        self.play(
            LaggedStartMap(FadeIn, s_labels),
            LaggedStart(*(
                Transform(s_title[1].copy(), label[1].copy(), remover=True)
                for label in s_labels
            )),
            lag_ratio=0.3,
            run_time=2,
        )
        self.wait()

        # Show zeroth DFT element
        s_labels.generate_target()
        plusses = VGroup()
        rhs = VGroup()
        for label in s_labels.target:
            plus = TexMobject("+")
            label.next_to(plusses, RIGHT, buff=0.3)
            plus.next_to(label, buff=0.3)
            plusses.add(plus)
            rhs.add(label, plus)
        plusses[-1].scale(0)
        lhs = TexMobject("\\hat s", "[0]", "=")
        lhs.to_corner(UL)
        rhs.next_to(lhs, RIGHT)

        self.play(
            FadeOut(s_title, UP),
            Write(lhs),
            Write(plusses),
            MoveToTarget(s_labels)
        )
        self.wait()

        vectors.generate_target()
        vectors.target.rotate(-90 * DEGREES)
        vectors.target.arrange(RIGHT, buff=0)
        vectors.target.set_width(FRAME_WIDTH - 3)
        vectors.target.move_to(DOWN)
        self.play(
            FadeOut(axes),
            MoveToTarget(vectors),
        )
        self.wait()

        # Add plane
        plane = ComplexPlane(x_range=(-2, 2), y_range=(-2, 2))
        plane.set_height(5)
        plane.to_edge(DOWN)
        plane.add_coordinate_labels()
        plane.coordinate_labels[1].scale(0)

        sf = signal[0] * get_norm(plane.n2p(1) - plane.n2p(0)) / vectors[0].get_length()
        vectors.generate_target()
        for n, vector in enumerate(vectors.target):
            vector.scale(sf)
            vector.set_angle(-n * TAU / N)
            vector.shift(plane.n2p(0) - vector.get_start())

        self.add(plane, vectors)
        self.play(
            Write(plane),
            MoveToTarget(vectors),
        )

        # Write first DFT term
        lhs1 = TexMobject("\\hat s", "[1]", "=")
        lhs1.next_to(lhs, DOWN, MED_LARGE_BUFF)

        rhs1 = VGroup()
        for n, s_term, plus in zip(it.count(), rhs[0::2], rhs[1::2]):
            new_s = s_term.copy()
            new_plus = plus.copy()
            top_clump = VGroup(s_term, plus)
            zeta = TexMobject(f"\\zeta^{{{n}}}")
            zeta.add_background_rectangle()
            clump = VGroup(new_s, zeta, new_plus)
            clump.arrange(RIGHT, buff=0.15)
            clump.match_width(top_clump)
            clump.scale(1.1)
            clump.next_to(top_clump, DOWN, MED_LARGE_BUFF, LEFT)
            rhs1.add(*clump)
            for term in clump:
                term.save_state()
            new_s.replace(s_term)
            new_plus.replace(plus)
            zeta.replace(plus)
            zeta.set_opacity(0)

        lhs.unlock_triangulation()
        self.play(
            TransformFromCopy(lhs, lhs1),
            *map(Restore, rhs1),
        )
        self.wait()

        # Define zeta
        zeta = np.exp(complex(0, TAU / N))
        zeta_power_vectors = VGroup(*(
            Arrow(plane.n2p(0), plane.n2p(zeta**(-n)), buff=0)
            for n in range(N)
        ))
        zeta_power_vectors.set_fill(GREY_B)

        unit_circle = Circle(
            radius=get_norm(plane.n2p(1) - plane.n2p(0)),
        )
        unit_circle.move_to(plane)
        unit_circle.set_stroke(YELLOW, 2)

        zeta_label = TexMobject(
            "\\zeta = e^{-2\\pi i / N}"
        )
        zeta_label.to_edge(RIGHT, buff=LARGE_BUFF)

        self.play(
            vectors.set_opacity, 0.1,
            FadeIn(unit_circle),
            FadeIn(zeta_power_vectors[1]),
            Write(zeta_label),
        )
        self.wait()

        zeta_powers = rhs1[1::3].copy()
        for z_power, vect in zip(zeta_powers, zeta_power_vectors):
            z_power.generate_target()
            z_power.target.next_to(
                vect,
                np.round(vect.get_vector(), 2),
                buff=SMALL_BUFF
            )

        kw = {
            "lag_ratio": 0.5,
            "run_time": 3,
        }
        self.play(
            LaggedStartMap(MoveToTarget, zeta_powers, **kw),
            LaggedStartMap(FadeIn, zeta_power_vectors, **kw),
            Animation(zeta_power_vectors[1].copy(), remover=True),
            plane.coordinate_labels.set_opacity, 0,
        )
        self.wait()

        self.play(
            FadeOut(zeta_powers),
            FadeOut(zeta_power_vectors),
            vectors.set_opacity, 1,
            plane.coordinate_labels.set_opacity, 1,
        )
        self.wait()

        # Show cosine example
        cos_signal = np.cos(np.arange(0, TAU, TAU / N)) + 1.5
        sin_signal = np.sin(np.arange(0, TAU, TAU / N)) + 1.5
        neg_cos_signal = -np.sin(np.arange(0, TAU, TAU / N)) + 1.5

        side_axes = Axes(
            (0, 8), (0, 3),
            width=3,
            height=2,
            axis_config={"include_tip": False}
        )
        side_axes.to_edge(LEFT)
        side_axes.x_axis.add_numbers(number_config={"height": 0.2})
        side_vectors = VGroup(*(
            Arrow(
                side_axes.c2p(x, 0),
                side_axes.c2p(x, cos_signal[x]),
                buff=0,
                thickness=0.05
            )
            for x in range(N)
        ))
        side_vectors.match_style(vectors)
        side_vectors.set_stroke(background=True)

        vectors.generate_target()
        for x, vect in enumerate(vectors.target):
            vect.put_start_and_end_on(
                plane.n2p(0),
                plane.n2p(cos_signal[x] * zeta**(-x)),
            )

        self.play(
            MoveToTarget(vectors),
            FadeIn(side_axes),
            FadeIn(side_vectors),
        )
        self.wait()

        def change_signal(new_signal):
            side_vectors.generate_target()
            vectors.generate_target()
            for x, sv, v in zip(it.count(), side_vectors.target, vectors.target):
                sv.put_start_and_end_on(
                    side_axes.c2p(x, 0),
                    side_axes.c2p(x, new_signal[x]),
                )
                v.put_start_and_end_on(
                    plane.n2p(0),
                    plane.n2p(new_signal[x] * zeta**(-x)),
                )
            self.play(
                MoveToTarget(vectors),
                MoveToTarget(side_vectors),
            )

        change_signal(sin_signal)
        self.wait()
        change_signal(neg_cos_signal)
        self.wait()
        change_signal(signal)
        self.wait()

        # Write second DFT term
        lhs2 = TexMobject("\\hat s", "[2]", "=")
        lhs2.next_to(lhs1, DOWN, MED_LARGE_BUFF)

        rhs2 = rhs1.copy()
        rhs2.next_to(lhs2, RIGHT)
        for n, z_term in enumerate(rhs2[1::3]):
            new_exp = Integer(2 * n)
            new_exp.match_height(z_term[1][1])
            new_exp.move_to(z_term[1][1], DL)
            z_term[1].replace_submobject(1, new_exp)

        lhs1.unlock_triangulation()
        rhs1.unlock_triangulation()
        plane_group = VGroup(
            plane,
            vectors,
            unit_circle,
        )
        self.add(plane_group)
        self.play(
            TransformFromCopy(lhs1, lhs2),
            TransformFromCopy(rhs1, rhs2),
            plane_group.scale, 0.8, {"about_edge": DOWN},
            zeta_label.shift, DOWN,
            FadeOut(side_axes),
            FadeOut(side_vectors),
        )
        self.add(vectors)

        anims = []
        for n, vect in enumerate(vectors):
            anims.append(Rotate(
                vect,
                -n * TAU / N,
                about_point=plane.n2p(0),
            ))
        self.play(*anims)
        self.wait()

        for n in range(N):
            rhs2.generate_target()
            rhs2.target.set_opacity(0.25)
            rhs2.target[3 * n:3 * (n + 1)].set_opacity(1)

            vectors.generate_target()
            vectors.target.set_opacity(0.1)
            vectors.target[n].set_opacity(1)

            self.play(
                MoveToTarget(rhs2),
                MoveToTarget(vectors),
            )
            self.wait()
        self.play(
            vectors.set_opacity, 1,
            rhs2.set_opacity, 1,
        )
        self.wait()

        # Show general formula
        dots = TexMobject("\\vdots")
        dots.next_to(lhs2[:-1], DOWN, MED_LARGE_BUFF)

        formula = TexMobject(
            "\\hat s[\\omega] = "
            "\\sum_{n=0}^{N - 1} s[n] \\zeta^{\\omega \\cdot n}"
        )
        formula.next_to(dots, DOWN)
        formula.align_to(lhs2, LEFT)

        self.play(
            Write(dots),
            FadeIn(formula, DOWN),
        )
        self.wait()

        # Cycle through
        omega_label = VGroup(
            TexMobject("\\omega = ", font_size=72),
            Integer(2),
        )
        omega_label.arrange(RIGHT, aligned_edge=DOWN)
        omega_label.next_to(plane, LEFT, MED_LARGE_BUFF, aligned_edge=DOWN)

        self.play(FadeIn(omega_label))

        for omega in range(3, 8):
            anims = []
            for n, vect in enumerate(vectors):
                anims.append(Rotate(
                    vect,
                    -n * TAU / N,
                    about_point=plane.n2p(0),
                ))
            new_count = omega_label[1].copy()
            new_count.set_value(omega)
            self.play(
                *anims,
                FadeIn(new_count, 0.5 * UP),
                FadeOut(omega_label[1], 0.5 * UP)
            )
            omega_label.replace_submobject(1, new_count)
            self.wait()
