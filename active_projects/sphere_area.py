from big_ol_pile_of_manim_imports import *
from active_projects.shadows import *


class AskAboutShadowRelation(SpecialThreeDScene):
    def construct(self):
        self.show_surface_area()
        self.show_area_of_shadow()
        self.show_light_source()
        self.show_four_circles()

    def show_surface_area(self):
        sphere = self.get_sphere()
        sphere.set_fill(BLUE_E, opacity=0.5)
        sphere.add_updater(
            lambda s, dt: s.rotate(0.1 * dt, axis=OUT)
        )
        pieces = sphere.deepcopy()
        pieces.space_out_submobjects(1.5)
        pieces.shift(IN)
        pieces.set_color(GREEN)

        # radial_line = Line(ORIGIN, sphere.get_right())
        # R_label = TexMobject("R")
        # R_label.set_color(BLUE)
        # R_label.rotate(90 * DEGREES, RIGHT)
        # R_label.next_to(radial_line, OUT, SMALL_BUFF)

        sa_equation = TexMobject(
            "\\text{Surface area} = 4\\pi R^2",
            tex_to_color_map={"R": BLUE}
        )
        sa_equation.scale(1.5)
        sa_equation.to_edge(UP)

        self.set_camera_to_default_position()
        self.add_fixed_in_frame_mobjects(sa_equation)
        self.play(
            Write(sphere, run_time=1),
            FadeInFromDown(sa_equation),
            # ShowCreation(radial_line),
            # FadeInFrom(R_label, IN),
        )
        self.play(
            Transform(
                sphere, pieces,
                rate_func=there_and_back_with_pause,
                run_time=2
            )
        )
        self.play(LaggedStart(
            UpdateFromAlphaFunc, sphere,
            lambda mob: (mob, lambda m, a: m.set_fill(
                color=interpolate_color(BLUE_E, YELLOW, a),
                opacity=interpolate(0.5, 1, a)
            )),
            rate_func=there_and_back,
            lag_ratio=0.2,
        ))
        self.play(self.camera.frame_center.shift, 2 * LEFT)
        self.wait(2)

        self.sphere = sphere
        self.sa_equation = sa_equation

    def show_area_of_shadow(self):
        pass

    def show_light_source(self):
        pass

    def show_four_circles(self):
        pass
