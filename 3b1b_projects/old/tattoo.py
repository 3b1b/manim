from manimlib.imports import *


class TrigRepresentationsScene(Scene):
    CONFIG = {
        "unit_length" : 1.5,
        "arc_radius" : 0.5,
        "axes_color" : WHITE,
        "circle_color" : RED,
        "theta_color" : YELLOW,
        "theta_height" : 0.3,
        "theta_value" : np.pi/5,
        "x_line_colors" : MAROON_B,
        "y_line_colors" : BLUE,
    }
    def setup(self):
        self.init_axes()
        self.init_circle()
        self.init_theta_group()

    def init_axes(self):
        self.axes = Axes(
            unit_size = self.unit_length,
        )
        self.axes.set_color(self.axes_color)
        self.add(self.axes)

    def init_circle(self):
        self.circle = Circle(
            radius = self.unit_length,
            color = self.circle_color
        )
        self.add(self.circle)

    def init_theta_group(self):
        self.theta_group = self.get_theta_group()
        self.add(self.theta_group)

    def add_trig_lines(self, *funcs, **kwargs):
        lines = VGroup(*[
            self.get_trig_line(func, **kwargs)
            for func in funcs
        ])
        self.add(*lines)

    def get_theta_group(self):
        arc = Arc(
            self.theta_value, 
            radius = self.arc_radius,
            color = self.theta_color,
        )
        theta = TexMobject("\\theta")
        theta.shift(1.5*arc.point_from_proportion(0.5))
        theta.set_color(self.theta_color)
        theta.set_height(self.theta_height)
        line = Line(ORIGIN, self.get_circle_point())
        dot = Dot(line.get_end(), radius = 0.05)
        return VGroup(line, arc, theta, dot)

    def get_circle_point(self):
        return rotate_vector(self.unit_length*RIGHT, self.theta_value)

    def get_trig_line(self, func_name = "sin", color = None):
        assert(func_name in ["sin", "tan", "sec", "cos", "cot", "csc"])
        is_co = func_name in ["cos", "cot", "csc"]
        if color is None:
            if is_co:
                color = self.y_line_colors 
            else:
                color = self.x_line_colors

        #Establish start point
        if func_name in ["sin", "cos", "tan", "cot"]:
            start_point = self.get_circle_point()
        else:
            start_point = ORIGIN

        #Establish end point
        if func_name is "sin":
            end_point = start_point[0]*RIGHT
        elif func_name is "cos":
            end_point = start_point[1]*UP
        elif func_name in ["tan", "sec"]:
            end_point = (1./np.cos(self.theta_value))*self.unit_length*RIGHT
        elif func_name in ["cot", "csc"]:
            end_point = (1./np.sin(self.theta_value))*self.unit_length*UP
        return Line(start_point, end_point, color = color)

class Introduce(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Something different today!",
            target_mode = "hooray",
            run_time = 2
        )
        self.change_student_modes("thinking", "happy", "sassy")
        self.random_blink(2)

class ReactionsToTattoo(PiCreatureScene):
    def construct(self):
        modes = [
            "horrified",
            "hesitant",
            "pondering",
            "thinking",
            "sassy",
        ]
        tattoo_on_math = TextMobject("Tattoo on \\\\ math")
        tattoo_on_math.to_edge(UP)
        self.wait(2)
        for mode in modes:
            self.play(
                self.pi_creature.change_mode, mode,
                self.pi_creature.look, UP+RIGHT
            )
            self.wait(2)
        self.play(
            Write(tattoo_on_math),
            self.pi_creature.change_mode, "hooray",
            self.pi_creature.look, UP
        )
        self.wait()
        self.change_mode("happy")
        self.wait(2)


    def create_pi_creature(self):
        randy = Randolph()
        randy.next_to(ORIGIN, DOWN)
        return randy

class IntroduceCSC(TrigRepresentationsScene):
    def construct(self):
        self.clear()
        Cam_S_C = TextMobject("Cam", "S.", "C.")
        CSC = TextMobject("C", "S", "C", arg_separator = "")
        csc_of_theta = TextMobject("c", "s", "c", "(\\theta)", arg_separator = "")
        csc, of_theta = VGroup(*csc_of_theta[:3]), csc_of_theta[-1]
        of_theta[1].set_color(YELLOW)
        CSC.move_to(csc, DOWN)

        csc_line = self.get_trig_line("csc")
        csc_line.set_stroke(width = 8)
        cot_line = self.get_trig_line("cot")
        cot_line.set_color(WHITE)
        brace = Brace(csc_line, LEFT)

        self.play(Write(Cam_S_C))
        self.wait()
        self.play(Transform(Cam_S_C, CSC))
        self.wait()
        self.play(Transform(Cam_S_C, csc))
        self.remove(Cam_S_C)
        self.add(csc)
        self.play(Write(of_theta))
        self.wait(2)

        csc_of_theta.add_to_back(BackgroundRectangle(csc))
        self.play(
            ShowCreation(self.axes),
            ShowCreation(self.circle),
            GrowFromCenter(brace),            
            csc_of_theta.rotate, np.pi/2,
            csc_of_theta.next_to, brace, LEFT,
            path_arc = np.pi/2,
        )
        self.play(Write(self.theta_group, run_time = 1))
        self.play(ShowCreation(cot_line))
        self.play(
            ShowCreation(csc_line),
            csc.set_color, csc_line.get_color(),
        )
        self.wait(3)

class TeachObscureTrigFunctions(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "$\\sec(\\theta)$, ",
            "$\\csc(\\theta)$, ",
            "$\\cot(\\theta)$",
        )
        content = self.teacher.bubble.content.copy()
        self.change_student_modes(*["confused"]*3)
        self.student_says(
            "But why?",
            target_mode = "pleading",
            added_anims = [content.to_corner, UP+RIGHT]
        )
        self.wait()
        self.play(self.get_teacher().change_mode, "pondering")
        self.wait(3)

class CanYouExplainTheTattoo(TeacherStudentsScene):
    def construct(self):
        self.student_says("""
            Wait, can you explain
            the actual tattoo here?
        """)
        self.random_blink()
        self.play(self.get_teacher().change_mode, "hooray")
        self.wait()

class ExplainTrigFunctionDistances(TrigRepresentationsScene, PiCreatureScene):
    CONFIG = {
        "use_morty" : False,
        "alt_theta_val" : 2*np.pi/5,
    }
    def setup(self):
        PiCreatureScene.setup(self)
        TrigRepresentationsScene.setup(self)

    def construct(self):
        self.introduce_angle()
        self.show_sine_and_cosine()
        self.show_tangent_and_cotangent()
        self.show_secant_and_cosecant()
        self.explain_cosecant()
        self.summarize_full_group()

    def introduce_angle(self):
        self.remove(self.circle)
        self.remove(self.theta_group)
        line, arc, theta, dot = self.theta_group
        line.rotate(-self.theta_value)
        brace = Brace(line, UP, buff = SMALL_BUFF)
        one = brace.get_text("1", buff = SMALL_BUFF)
        VGroup(line, brace, one).rotate(self.theta_value)
        one.rotate_in_place(-self.theta_value)
        self.circle.rotate(self.theta_value)

        words = TextMobject("Corresponding point")
        words.next_to(dot, UP+RIGHT, buff = 1.5*LARGE_BUFF)
        words.shift_onto_screen()
        arrow = Arrow(words.get_bottom(), dot, buff = SMALL_BUFF)

        self.play(
            ShowCreation(line),
            ShowCreation(arc),
        )
        self.play(Write(theta))
        self.play(self.pi_creature.change_mode, "pondering")
        self.play(
            ShowCreation(self.circle),
            Rotating(line, rate_func = smooth, in_place = False),
            run_time = 2
        )
        self.play(
            Write(words),
            ShowCreation(arrow),
            ShowCreation(dot)
        )
        self.wait()
        self.play(
            GrowFromCenter(brace),
            Write(one)
        )
        self.wait(2)
        self.play(*list(map(FadeOut, [
            words, arrow, brace, one
        ])))
        self.radial_line_label = VGroup(brace, one)

    def show_sine_and_cosine(self):
        sin_line, sin_brace, sin_text = sin_group = self.get_line_brace_text("sin")
        cos_line, cos_brace, cos_text = cos_group = self.get_line_brace_text("cos")

        self.play(ShowCreation(sin_line))
        self.play(
            GrowFromCenter(sin_brace),
            Write(sin_text),
        )
        self.play(self.pi_creature.change_mode, "happy")
        self.play(ShowCreation(cos_line))
        self.play(
            GrowFromCenter(cos_brace),
            Write(cos_text),
        )
        self.wait()
        self.change_mode("well")

        mover = VGroup(
            sin_group,
            cos_group,
            self.theta_group,
        )
        thetas = np.linspace(self.theta_value, self.alt_theta_val, 100)
        targets = []
        for theta in thetas:
            self.theta_value = theta
            targets.append(VGroup(
                self.get_line_brace_text("sin"),
                self.get_line_brace_text("cos"),
                self.get_theta_group()
            ))
        self.play(Succession(
            *[
                Transform(mover, target, rate_func=linear)
                for target in targets
            ],
            run_time = 5, 
            rate_func = there_and_back
        ))
        self.theta_value = thetas[0]

        self.change_mode("happy")
        self.wait()
        self.sin_group, self.cos_group = sin_group, cos_group

    def show_tangent_and_cotangent(self):
        tan_group = self.get_line_brace_text("tan")
        cot_group = self.get_line_brace_text("cot")
        tan_text = tan_group[-1]
        cot_text = cot_group[-1]
        line = Line(UP, DOWN).scale(FRAME_Y_RADIUS)
        line.rotate(self.theta_value)
        line.move_to(self.theta_group[-1])
        line.set_stroke(width = 2)

        sin_tex = "{\\sin(\\theta)}"
        cos_tex = "{\\cos(\\theta)}"
        tan_frac = TexMobject("= \\frac" + sin_tex + cos_tex)
        cot_frac = TexMobject("= \\frac" + cos_tex + sin_tex)
        tan_frac.to_corner(UP+LEFT)
        tan_frac.shift(2*RIGHT)
        cot_frac.next_to(tan_frac, DOWN)


        self.change_mode("pondering")
        for frac, text in (tan_frac, tan_text), (cot_frac, cot_text):
            VGroup(frac[5], frac[-2]).set_color(YELLOW)
            frac.scale_in_place(0.7)
            text.save_state()
            text.next_to(frac, LEFT)
            self.play(Write(VGroup(text, frac)))
            self.wait()
        self.change_mode("confused")
        self.wait()
        self.play(*list(map(FadeOut, [
            tan_frac, cot_frac, self.sin_group, self.cos_group
        ])))
        self.wait()

        self.play(
            self.theta_group[-1].set_color, YELLOW,
            ShowCreation(line),
            self.pi_creature.change_mode, 'pondering'
        )
        small_lines = VGroup()
        for group in tan_group, cot_group:
            small_line, brace, text = group
            self.play(
                ShowCreation(small_line),
                GrowFromCenter(brace),
                text.restore,
            )
            self.wait()
            small_lines.add(small_line)
        self.play(FadeOut(line), Animation(small_lines))

        mover = VGroup(
            tan_group,
            cot_group,
            self.theta_group,
        )
        thetas = np.linspace(self.theta_value, self.alt_theta_val, 100)
        targets = []
        for theta in thetas:
            self.theta_value = theta
            targets.append(VGroup(
                self.get_line_brace_text("tan"),
                self.get_line_brace_text("cot"),
                self.get_theta_group()
            ))
        self.play(Succession(
            *[
                Transform(mover, target, rate_func=linear)
                for target in targets
            ], 
            run_time = 5, 
            rate_func = there_and_back
        ))
        self.theta_value = thetas[0]

        self.change_mode("happy")
        self.wait(2)

        self.tangent_line = self.get_tangent_line()
        self.add(self.tangent_line)
        self.play(*it.chain(*[
            list(map(FadeOut, [tan_group, cot_group])),
            [Animation(self.theta_group[-1])]
        ]))

    def show_secant_and_cosecant(self):
        sec_group = self.get_line_brace_text("sec")
        csc_group = self.get_line_brace_text("csc")
        sec_line, sec_brace, sec_text = sec_group
        csc_line, csc_brace, csc_text = csc_group

        sec_frac = TexMobject("= \\frac{1}{\\cos(\\theta)}")
        sec_frac.to_corner(UP+LEFT).shift(2*RIGHT)
        csc_frac = TexMobject("= \\frac{1}{\\sin(\\theta)}")
        csc_frac.next_to(sec_frac, DOWN)

        sec_dot, csc_dot = [
            Dot(line.get_end(), color = line.get_color())
            for line in (sec_line, csc_line)
        ]
        sec_group.add(sec_dot)
        csc_group.add(csc_dot)

        for text, frac in (sec_text, sec_frac), (csc_text, csc_frac):
            frac[-2].set_color(YELLOW)
            frac.scale_in_place(0.7)
            text.save_state()
            text.next_to(frac, LEFT)
            frac.add_to_back(text.copy())
            self.play(
                Write(frac),
                self.pi_creature.change_mode, "erm"
            )
            self.wait()
        self.wait()
        for group in sec_group, csc_group:
            line, brace, text, dot = group
            dot.save_state()
            dot.move_to(text)
            dot.set_fill(opacity = 0)
            self.play(dot.restore)
            self.wait()
            self.play(
                ShowCreation(line),
                GrowFromCenter(brace),
                text.restore,
                self.pi_creature.change_mode, "pondering"
            )
            self.wait()

        mover = VGroup(
            sec_group,
            csc_group,
            self.theta_group,
            self.tangent_line,
        )
        thetas = np.linspace(self.theta_value, self.alt_theta_val, 100)
        targets = []
        for theta in thetas:
            self.theta_value = theta
            new_sec_group = self.get_line_brace_text("sec")
            new_csc_group = self.get_line_brace_text("csc")
            for group in new_sec_group, new_csc_group:
                line = group[0]
                group.add(
                    Dot(line.get_end(), color = line.get_color())
                )
            targets.append(VGroup(
                new_sec_group,
                new_csc_group,
                self.get_theta_group(),
                self.get_tangent_line(),
            ))
        self.play(Succession(
            *[
                Transform(mover, target, rate_func=linear)
                for target in targets
            ], 
            run_time = 5, 
            rate_func = there_and_back
        ))
        self.theta_value = thetas[0]

        self.change_mode("confused")
        self.wait(2)

        self.play(*list(map(FadeOut, [
            sec_group, sec_frac
        ])))
        self.csc_group = csc_group
        self.csc_frac =csc_frac

    def explain_cosecant(self):
        sin_group = self.get_line_brace_text("sin")
        sin_line, sin_brace, sin_text = sin_group
        csc_line, csc_brace, csc_text, csc_dot = self.csc_group
        csc_subgroup = VGroup(csc_brace, csc_text)

        arc_theta = VGroup(*self.theta_group[1:3]).copy()
        arc_theta.rotate(-np.pi/2)
        arc_theta.shift(csc_line.get_end())
        arc_theta[1].rotate_in_place(np.pi/2)

        radial_line = self.theta_group[0]

        tri1 = Polygon(
            ORIGIN, radial_line.get_end(), sin_line.get_end(),
            color = GREEN,
            stroke_width = 8,
        )
        tri2 = Polygon(
            csc_line.get_end(), ORIGIN, radial_line.get_end(),
            color = GREEN,
            stroke_width = 8,
        )

        opp_over_hyp = TexMobject(
            "\\frac{\\text{Opposite}}{\\text{Hypotenuse}} ="
        )
        frac1 = TexMobject("\\frac{\\sin(\\theta)}{1}")
        frac1.next_to(opp_over_hyp)
        frac1[-4].set_color(YELLOW)
        frac2 = TexMobject("= \\frac{1}{\\csc(\\theta)}")
        frac2.next_to(frac1)
        frac2[-2].set_color(YELLOW)
        frac_group = VGroup(opp_over_hyp, frac1, frac2)
        frac_group.set_width(FRAME_X_RADIUS-1)
        frac_group.next_to(ORIGIN, RIGHT).to_edge(UP)

        question = TextMobject("Why is this $\\theta$?")
        question.set_color(YELLOW)
        question.to_corner(UP+RIGHT)
        arrow = Arrow(question.get_bottom(), arc_theta)

        one_brace, one = self.radial_line_label
        one.move_to(one_brace.get_center_of_mass())

        self.play(ShowCreation(tri1))
        self.play(
            ApplyMethod(tri1.rotate_in_place, np.pi/12, rate_func = wiggle),
            self.pi_creature.change_mode, "thinking"
        )
        self.wait()
        tri1.save_state()
        self.play(Transform(tri1, tri2, path_arc = np.pi/2))
        self.play(Write(arc_theta))
        self.play(ApplyMethod(
            tri1.rotate_in_place, np.pi/12, 
            rate_func = wiggle
        ))
        self.wait(2)
        self.play(
            Write(question),
            ShowCreation(arrow),
            self.pi_creature.change_mode, "confused"
        )
        self.wait(2)
        self.play(*list(map(FadeOut, [question, arrow])))


        self.play(Write(opp_over_hyp))
        self.wait()
        csc_subgroup.save_state()
        self.play(
            tri1.restore,
            csc_subgroup.fade, 0.7
        )
        self.play(
            ShowCreation(sin_line),
            GrowFromCenter(sin_brace),
            Write(sin_text)
        )
        self.wait()
        self.play(Write(one))
        self.wait()
        self.play(Write(frac1))
        self.wait()
        self.play(
            Transform(tri1, tri2),
            FadeOut(sin_group)
        )
        self.play(
            radial_line.rotate_in_place, np.pi/12,
            rate_func = wiggle
        )
        self.wait()
        self.play(csc_subgroup.restore)
        self.wait()
        self.play(Write(frac2))
        self.change_mode("happy")
        self.play(FadeOut(opp_over_hyp))
        self.reciprocate(frac1, frac2)
        self.play(*list(map(FadeOut, [
            one, self.csc_group, tri1,
            frac1, frac2, self.csc_frac,
            arc_theta
        ])))

    def reciprocate(self, frac1, frac2):
        # Not general, meant only for these definitions:
        # frac1 = TexMobject("\\frac{\\sin(\\theta)}{1}")
        # frac2 = TexMobject("= \\frac{1}{\\csc(\\theta)}")
        num1 = VGroup(*frac1[:6])
        dem1 = frac1[-1]
        num2 = frac2[1]
        dem2 = VGroup(*frac2[-6:])
        group = VGroup(frac1, frac2)

        self.play(
            group.scale, 1/0.7,
            group.to_corner, UP+RIGHT,
        )
        self.play(
            num1.move_to, dem1,
            dem1.move_to, num1,
            num2.move_to, dem2,
            dem2.move_to, num2,
            path_arc = np.pi
        )
        self.wait()
        self.play(
            dem2.move_to, frac2[2],
            VGroup(*frac2[1:3]).set_fill, BLACK, 0
        )
        self.wait()

    def summarize_full_group(self):
        scale_factor = 1.5
        theta_subgroup = VGroup(self.theta_group[0], self.theta_group[-1])
        self.play(*it.chain(*[
            [mob.scale, scale_factor]
            for mob in [
                self.circle, self.axes, 
                theta_subgroup, self.tangent_line
            ]
        ]))
        self.unit_length *= scale_factor

        to_fade = VGroup()
        for func_name in ["sin", "tan", "sec", "cos", "cot", "csc"]:
            line, brace, text = self.get_line_brace_text(func_name)
            if func_name in ["sin", "cos"]:
                angle = line.get_angle()
                if np.cos(angle) < 0:
                    angle += np.pi
                if func_name is "sin":
                    target = line.get_center()+0.2*LEFT+0.1*DOWN
                else:
                    target = VGroup(brace, line).get_center_of_mass()
                text.scale(0.75)
                text.rotate(angle)
                text.move_to(target)
                line.set_stroke(width = 6)
                self.play(
                    ShowCreation(line),
                    Write(text, run_time = 1)
                )
            else:
                self.play(
                    ShowCreation(line),
                    GrowFromCenter(brace),
                    Write(text, run_time = 1)
                )
            if func_name in ["sec", "csc", "cot"]:
                to_fade.add(*self.get_mobjects_from_last_animation())
            if func_name is "sec":
                self.wait()
        self.wait()
        self.change_mode("surprised")
        self.wait(2)
        self.remove(self.tangent_line)
        self.play(
            FadeOut(to_fade),
            self.pi_creature.change_mode, "sassy"
        )
        self.wait(2)

    def get_line_brace_text(self, func_name = "sin"):
        line = self.get_trig_line(func_name)
        angle = line.get_angle()
        vect = rotate_vector(UP, angle)
        vect = np.round(vect, 1)
        if (vect[1] < 0) ^ (func_name is "sec"):
            vect = -vect
            angle += np.pi
        brace = Brace(
            Line(
                line.get_length()*LEFT/2,
                line.get_length()*RIGHT/2,
            ), 
            UP
        )
        brace.rotate(angle)
        brace.shift(line.get_center())
        brace.set_color(line.get_color())
        text = TexMobject("\\%s(\\theta)"%func_name)
        text.scale(0.75)
        text[-2].set_color(self.theta_color)
        text.add_background_rectangle()
        text.next_to(brace.get_center_of_mass(), vect, buff = 1.2*MED_SMALL_BUFF)
        return VGroup(line, brace, text)

    def get_tangent_line(self):
        return Line(
            self.unit_length*(1./np.sin(self.theta_value))*UP,
            self.unit_length*(1./np.cos(self.theta_value))*RIGHT,
            color = GREY
        )

class RenameAllInTermsOfSine(Scene):
    def construct(self):
        texs = [
            "\\sin(\\theta)",
            "\\cos(\\theta)",
            "\\tan(\\theta)",
            "\\csc(\\theta)",
            "\\sec(\\theta)",
            "\\cot(\\theta)",
        ]
        shift_vals = [
            4*LEFT+3*UP,
            4*LEFT+UP,
            4*LEFT+DOWN,
            4*RIGHT+3*UP,
            4*RIGHT+UP,
            4*RIGHT+DOWN,
        ]
        equivs = [
            "",
            "= \\sin(90^\\circ - \\theta)",
            "= \\frac{\\sin(\\theta)}{\\sin(90^\\circ - \\theta)}",
            "= \\frac{1}{\\sin(\\theta)}",
            "= \\frac{1}{\\sin(90^\\circ - \\theta)}",
            "= \\frac{\\sin(90^\\circ - \\theta)}{\\sin(\\theta)}",
        ]
        mobs = VGroup(*list(map(TexMobject, texs)))
        sin, cos, tan = mobs[:3]
        sin.target_color = YELLOW
        cos.target_color = GREEN
        tan.target_color = RED

        rhs_mobs = VGroup(*list(map(TexMobject, equivs)))
        rhs_mobs.submobjects[0] = VectorizedPoint()
        for mob, shift_val in zip(mobs, shift_vals):
            mob.shift(shift_val)
        self.play(Write(mobs))
        self.wait()
        for mob, rhs_mob in zip(mobs, rhs_mobs):
            rhs_mob.next_to(mob)
            rhs_mob.set_color(sin.target_color)
            mob.save_state()
            mob.generate_target()
            VGroup(mob.target, rhs_mob).move_to(mob)
        sin.target.set_color(sin.target_color)
        self.play(*it.chain(*[
            list(map(MoveToTarget, mobs)),
            [Write(rhs_mobs)]
        ]))
        self.wait(2)

        anims = []
        for mob, rhs_mob in list(zip(mobs, rhs_mobs))[1:3]:
            anims += [
                FadeOut(rhs_mob),
                mob.restore,
                mob.set_color, mob.target_color,
            ]
        self.play(*anims)
        self.wait()

        new_rhs_mobs = [
            TexMobject("=\\frac{1}{\\%s(\\theta)}"%s).set_color(color)
            for s, color in [
                ("cos", cos.target_color),
                ("tan", tan.target_color),
            ]
        ]
        anims = []
        for mob, rhs, new_rhs in zip(mobs[-2:], rhs_mobs[-2:], new_rhs_mobs):
            new_rhs.next_to(mob)
            VGroup(mob.target, new_rhs).move_to(
                VGroup(mob, rhs)
            )
            anims += [
                MoveToTarget(mob),
                Transform(rhs, new_rhs)
            ]
        self.play(*anims)
        self.wait(2)

class MisMatchOfCoPrefix(TeacherStudentsScene):
    def construct(self):
        eq1 = TexMobject(
            "\\text{secant}(\\theta) = \\frac{1}{\\text{cosine}(\\theta)}"
        )
        eq2 = TexMobject(
            "\\text{cosecant}(\\theta) = \\frac{1}{\\text{sine}(\\theta)}"
        )
        eq1.to_corner(UP+LEFT)
        eq1.to_edge(LEFT)
        eq2.next_to(eq1, DOWN, buff = LARGE_BUFF)
        eqs = VGroup(eq1, eq2)

        self.play(
            self.get_teacher().change_mode, "speaking",
            Write(eqs),
            *[
                ApplyMethod(pi.look_at, eqs)
                for pi in self.get_students()
            ]
        )
        self.random_blink()
        self.play(
            VGroup(*eq1[-9:-7]).set_color, YELLOW,
            VGroup(*eq2[:2]).set_color, YELLOW,
            *[
                ApplyMethod(pi.change_mode, "confused")
                for pi in self.get_students()
            ]
        )
        self.random_blink(2)

class Credit(Scene):
    def construct(self):
        morty = Mortimer()
        morty.next_to(ORIGIN, DOWN)
        morty.to_edge(RIGHT)

        headphones = Headphones(height = 1)
        headphones.move_to(morty.eyes, aligned_edge = DOWN)
        headphones.shift(0.1*DOWN)

        url = TextMobject("www.audibletrial.com/3blue1brown")
        url.scale(0.8)
        url.to_corner(UP+RIGHT, buff = LARGE_BUFF)

        book = ImageMobject("zen_and_motorcycles")
        book.set_height(5)
        book.to_edge(DOWN, buff = LARGE_BUFF)
        border = Rectangle(color = WHITE)
        border.replace(book, stretch = True)

        self.play(PiCreatureSays(
            morty, "Book recommendation!",
            target_mode = "surprised"
        ))
        self.play(Blink(morty))
        self.play(
            FadeIn(headphones),
            morty.change_mode, "thinking",
            FadeOut(morty.bubble),
            FadeOut(morty.bubble.content),
        )
        self.play(Write(url))
        self.play(morty.change_mode, "happy")
        self.wait(2)
        self.play(Blink(morty))
        self.wait(2)
        self.play(
            morty.change_mode, "raise_right_hand",
            morty.look_at, url
        )
        self.wait(2)
        self.play(
            morty.change_mode, "happy",
            morty.look_at, book
        )
        self.play(FadeIn(book))
        self.play(ShowCreation(border))
        self.wait(2)
        self.play(Blink(morty))
        self.wait()
        self.play(
            morty.change_mode, "thinking",
            morty.look_at, book
        )
        self.wait(2)
        self.play(Blink(morty))
        self.wait(4)
        self.play(Blink(morty))






























