from manimlib.imports import *
from old_projects.sphere_area import *


class MadAtMathologer(PiCreatureScene):
    def create_pi_creature(self):
        return Mortimer().to_corner(DR)

    def construct(self):
        morty = self.pi_creature
        self.play(morty.change, "angry")
        self.wait(3)
        self.play(morty.change, "heistant")
        self.wait(2)
        self.play(morty.change, "shruggie")
        self.wait(3)


class JustTheIntegral(Scene):
    def construct(self):
        tex = TexMobject("\\int_0^{\\pi / 2} \\cos(\\theta)d\\theta")
        tex.scale(2)
        self.add(tex)


class SphereVideoWrapper(Scene):
    def construct(self):
        title = TextMobject("Surface area of a sphere")
        title.scale(1.5)
        title.to_edge(UP)
        rect = ScreenRectangle(height=6)
        rect.next_to(title, DOWN)
        self.add(title)
        self.play(ShowCreation(rect))
        self.wait()


class SphereRings(SecondProof):
    CONFIG = {
        "sphere_config": {
            "resolution": (60, 60),
        },
    }

    def construct(self):
        self.setup_shapes()
        self.grow_rings()
        self.show_one_ring()
        self.show_radial_line()
        self.show_thickness()
        self.flash_through_rings()

    def grow_rings(self):
        sphere = self.sphere
        rings = self.rings
        north_rings = rings[:len(rings) // 2]
        sphere.set_fill(opacity=0)
        sphere.set_stroke(WHITE, 0.5, opacity=0.5)
        southern_mesh = VGroup(*[
            face.copy() for face in sphere
            if face.get_center()[2] < 0
        ])
        southern_mesh.set_stroke(WHITE, 0.1, 0.5)

        self.play(Write(sphere))
        self.wait()
        self.play(
            FadeOut(sphere),
            FadeIn(southern_mesh),
            FadeIn(north_rings),
        )
        self.wait(4)

        self.north_rings = north_rings
        self.southern_mesh = southern_mesh

    def show_one_ring(self):
        north_rings = self.north_rings
        index = len(north_rings) // 2
        ring = north_rings[index]
        to_fade = VGroup(*[
            nr for nr in north_rings
            if nr is not ring
        ])

        north_rings.save_state()

        circle = Circle()
        circle.set_stroke(PINK, 5)
        circle.set_width(ring.get_width())
        circle.move_to(ring, IN)

        thickness = ring.get_depth() * np.sqrt(2)
        brace = Brace(Line(ORIGIN, 0.2 * RIGHT), UP)
        brace.set_width(thickness)
        brace.rotate(90 * DEGREES, RIGHT)
        brace.rotate(45 * DEGREES, UP)
        brace.move_to(1.5 * (RIGHT + OUT))
        brace.set_stroke(WHITE, 1)
        word = TextMobject("Thickness")
        word.rotate(90 * DEGREES, RIGHT)
        word.next_to(brace, RIGHT + OUT, buff=0)

        self.play(
            to_fade.set_fill, {"opacity": 0.2},
            to_fade.set_stroke, {"opacity": 0.0},
        )
        self.move_camera(
            phi=0, theta=-90 * DEGREES,
            run_time=2,
        )
        self.stop_ambient_camera_rotation()
        self.play(ShowCreation(circle))
        self.play(FadeOut(circle))
        self.move_camera(
            phi=70 * DEGREES,
            theta=-100 * DEGREES,
            run_time=2,
        )
        self.begin_ambient_camera_rotation(0.02)
        self.play(
            GrowFromCenter(brace),
            Write(word),
        )
        self.wait(2)
        self.play(FadeOut(VGroup(brace, word)))

        self.circum_circle = circle
        self.thickness_label = VGroup(brace, word)
        self.ring = ring

    def show_radial_line(self):
        ring = self.ring

        point = ring.get_corner(RIGHT + IN)
        R_line = Line(ORIGIN, point)
        xy_line = Line(ORIGIN, self.sphere.get_right())
        theta = np.arccos(np.dot(
            normalize(R_line.get_vector()),
            normalize(xy_line.get_vector())
        ))
        arc = Arc(angle=theta, radius=0.5)
        arc.rotate(90 * DEGREES, RIGHT, about_point=ORIGIN)

        theta = TexMobject("\\theta")
        theta.rotate(90 * DEGREES, RIGHT)
        theta.next_to(arc, RIGHT)
        theta.shift(SMALL_BUFF * (LEFT + OUT))

        R_label = TexMobject("R")
        R_label.rotate(90 * DEGREES, RIGHT)
        R_label.next_to(
            R_line.get_center(), OUT + LEFT,
            buff=SMALL_BUFF
        )
        VGroup(R_label, R_line).set_color(YELLOW)

        z_axis_point = np.array(point)
        z_axis_point[:2] = 0
        r_line = DashedLine(z_axis_point, point)
        r_line.set_color(RED)
        r_label = TexMobject("R\\cos(\\theta)")
        r_label.rotate(90 * DEGREES, RIGHT)
        r_label.scale(0.7)
        r_label.match_color(r_line)
        r_label.set_stroke(width=0, background=True)
        r_label.next_to(r_line, OUT, 0.5 * SMALL_BUFF)

        VGroup(
            R_label, xy_line, arc, R_label,
            r_line, r_label,
        ).set_shade_in_3d(True)

        # self.stop_ambient_camera_rotation()
        self.move_camera(
            phi=85 * DEGREES,
            theta=-100 * DEGREES,
            added_anims=[
                ring.set_fill, {"opacity": 0.5},
                ring.set_stroke, {"opacity": 0.1},
                ShowCreation(R_line),
                FadeInFrom(R_label, IN),
            ]
        )
        self.wait()
        self.play(
            FadeIn(xy_line),
            ShowCreation(arc),
            Write(theta),
        )
        self.wait()
        self.play(
            ShowCreation(r_line),
            FadeInFrom(r_label, IN),
        )
        self.wait()
        self.move_camera(
            phi=70 * DEGREES,
            theta=-110 * DEGREES,
            run_time=3
        )
        self.wait(2)

    def show_thickness(self):
        brace, word = self.thickness_label
        R_dtheta = TexMobject("R \\, d\\theta")
        R_dtheta.rotate(90 * DEGREES, RIGHT)
        R_dtheta.move_to(word, LEFT)

        self.play(
            GrowFromCenter(brace),
            Write(R_dtheta)
        )
        self.wait(3)

    def flash_through_rings(self):
        rings = self.north_rings.copy()
        rings.fade(1)
        rings.sort(lambda p: p[2])

        for x in range(8):
            self.play(LaggedStartMap(
                ApplyMethod, rings,
                lambda m: (m.set_fill, PINK, 0.5),
                rate_func=there_and_back,
                lag_ratio=0.1,
                run_time=2,
            ))


class IntegralSymbols(Scene):
    def construct(self):
        int_sign = TexMobject("\\displaystyle \\int")
        int_sign.set_height(1.5)
        int_sign.move_to(5 * LEFT)

        circumference, times, thickness = ctt = TextMobject(
            "circumference", "$\\times$", "thickness"
        )
        circumference.set_color(MAROON_B)
        ctt.next_to(int_sign, RIGHT, SMALL_BUFF)
        area_brace = Brace(ctt, DOWN)
        area_text = area_brace.get_text("Area of a ring")

        all_rings = TextMobject("All rings")
        all_rings.scale(0.5)
        all_rings.next_to(int_sign, DOWN, SMALL_BUFF)
        all_rings.shift(SMALL_BUFF * LEFT)

        circum_formula = TexMobject(
            "2\\pi", "R\\cos(\\theta)",
        )
        circum_formula[1].set_color(RED)
        circum_formula.move_to(circumference)
        circum_brace = Brace(circum_formula, UP)

        R_dtheta = TexMobject("R \\, d\\theta")
        R_dtheta.move_to(thickness, LEFT)
        R_dtheta_brace = Brace(R_dtheta, UP)

        zero, pi_halves = bounds = TexMobject("0", "\\pi / 2")
        bounds.scale(0.5)
        zero.move_to(all_rings)
        pi_halves.next_to(int_sign, UP, SMALL_BUFF)
        pi_halves.shift(SMALL_BUFF * RIGHT)

        self.add(int_sign)
        self.play(
            GrowFromCenter(area_brace),
            FadeInFrom(area_text, UP),
        )
        self.wait()
        self.play(FadeInFromDown(circumference))
        self.play(
            FadeInFromDown(thickness),
            Write(times)
        )
        self.play(Write(all_rings))
        self.wait()

        self.play(
            circumference.next_to, circum_brace, UP, MED_SMALL_BUFF,
            circumference.shift, SMALL_BUFF * UR,
            GrowFromCenter(circum_brace),
        )
        self.play(FadeInFrom(circum_formula, UP))
        self.wait()
        self.play(
            thickness.next_to, circumference, RIGHT, MED_SMALL_BUFF,
            GrowFromCenter(R_dtheta_brace),
            area_brace.stretch, 0.84, 0, {"about_edge": LEFT},
            MaintainPositionRelativeTo(area_text, area_brace),
        )
        self.play(FadeInFrom(R_dtheta, UP))
        self.wait()
        self.play(ReplacementTransform(all_rings, bounds))
        self.wait()

        # RHS
        rhs = TexMobject(
            "\\displaystyle =", "2\\pi R^2", "\\int_0^{\\pi / 2}",
            "\\cos(\\theta)", "d\\theta",
        )
        rhs.set_color_by_tex("cos", RED)
        rhs.next_to(R_dtheta, RIGHT)
        int_brace = Brace(rhs[2:], DOWN)
        q_marks = int_brace.get_text("???")
        one = TexMobject("1")
        one.move_to(q_marks)

        self.play(FadeInFrom(rhs, 4 * LEFT))
        self.wait()
        self.play(ShowCreationThenFadeAround(rhs[1]))
        self.wait()
        self.play(ShowCreationThenFadeAround(rhs[2:]))
        self.wait()
        self.play(
            GrowFromCenter(int_brace),
            LaggedStartMap(
                FadeInFrom, q_marks,
                lambda m: (m, UP),
            )
        )
        self.wait()
        self.play(ReplacementTransform(q_marks, one))
        self.wait()


class ShamelessPlug(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "But why $4\\pi R^2$?",
            target_mode="maybe"
        )
        self.change_student_modes(
            "erm", "maybe", "happy",
            added_anims=[self.teacher.change, "happy"]
        )
        self.wait(3)
