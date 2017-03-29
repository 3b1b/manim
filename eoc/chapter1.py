from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from topics.objects import *
from scene import Scene
from scene.zoomed_scene import ZoomedScene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

from eoc.graph_scene import GraphScene
from topics.common_scenes import OpeningQuote, PatreonThanks

class CircleScene(PiCreatureScene):
    CONFIG = {
        "radius" : 1.5,
        "stroke_color" : WHITE,
        "fill_color" : BLUE_E,
        "fill_opacity" : 0.5,
        "radial_line_color" : MAROON_B,
        "outer_ring_color" : GREEN_E,
        "dR" : 0.1,
        "dR_color" : YELLOW,
        "unwrapped_tip" : ORIGIN,
        "include_pi_creature" : False,
        "circle_corner" : UP+LEFT
    }
    def setup(self):
        self.circle = Circle(
            radius = self.radius,
            stroke_color = self.stroke_color,
            fill_color = self.fill_color,
            fill_opacity = self.fill_opacity,
        )
        self.circle.to_corner(self.circle_corner, buff = MED_LARGE_BUFF)
        self.radius_line = Line(
            self.circle.get_center(),
            self.circle.get_right(),
            color = self.radial_line_color
        )
        self.radius_brace = Brace(self.radius_line, buff = SMALL_BUFF)
        self.radius_label = self.radius_brace.get_text("$R$", buff = SMALL_BUFF)

        self.add(
            self.circle, self.radius_line, 
            self.radius_brace, self.radius_label
        )

        self.pi_creature = self.create_pi_creature()
        if self.include_pi_creature:
            self.add(self.pi_creature)
        else:
            self.pi_creature.set_fill(opacity = 0)

    def create_pi_creature(self):
        return Mortimer().to_corner(DOWN+RIGHT)

    def introduce_circle(self, added_anims = []):
        self.remove(self.circle)
        self.play(
            ShowCreation(self.radius_line),
            GrowFromCenter(self.radius_brace),
            Write(self.radius_label),
        )
        self.circle.set_fill(opacity = 0)

        self.play(
            Rotate(
                self.radius_line, 2*np.pi-0.001, 
                about_point = self.circle.get_center(),
            ),
            ShowCreation(self.circle),
            *added_anims,
            run_time = 2
        )
        self.play(
            self.circle.set_fill, self.fill_color, self.fill_opacity,
            Animation(self.radius_line),
            Animation(self.radius_brace),
            Animation(self.radius_label),
        )

    def increase_radius(self, numerical_dr = True, run_time = 2):
        radius_mobs = VGroup(
            self.radius_line, self.radius_brace, self.radius_label
        )
        nudge_line = Line(
            self.radius_line.get_right(),
            self.radius_line.get_right() + self.dR*RIGHT,
            color = self.dR_color
        )
        nudge_arrow = Arrow(
            nudge_line.get_center() + 0.5*RIGHT+DOWN,
            nudge_line.get_center(),
            color = YELLOW,
            buff = SMALL_BUFF,
            tip_length = 0.2,
        )
        if numerical_dr:
            nudge_label = TexMobject("%.01f"%self.dR)
        else:
            nudge_label = TexMobject("dr")
        nudge_label.highlight(self.dR_color)
        nudge_label.scale(0.75)
        nudge_label.next_to(nudge_arrow.get_start(), DOWN)

        radius_mobs.add(nudge_line, nudge_arrow, nudge_label)

        outer_ring = self.get_outer_ring()

        self.play(
            FadeIn(outer_ring),            
            ShowCreation(nudge_line),
            ShowCreation(nudge_arrow),
            Write(nudge_label),
            run_time = run_time/2.
        )
        self.dither(run_time/2.)
        self.nudge_line = nudge_line
        self.nudge_arrow = nudge_arrow
        self.nudge_label = nudge_label
        self.outer_ring = outer_ring
        return outer_ring

    def get_ring(self, radius, dR, color = GREEN):
        ring = Circle(radius = radius + dR).center()
        inner_ring = Circle(radius = radius)
        inner_ring.rotate(np.pi, RIGHT)
        ring.append_vectorized_mobject(inner_ring)
        ring.set_stroke(width = 0)
        ring.set_fill(color)
        ring.move_to(self.circle)
        ring.R = radius 
        ring.dR = dR
        return ring

    def get_outer_ring(self):
        return self.get_ring(
            radius = self.radius, dR = self.dR,
            color = self.outer_ring_color
        )

    def unwrap_ring(self, ring, **kwargs):
        self.unwrap_rings(ring, **kwargs)

    def unwrap_rings(self, *rings, **kwargs):
        added_anims = kwargs.get("added_anims", [])
        rings = VGroup(*rings)
        unwrapped = VGroup(*[
            self.get_unwrapped(ring, **kwargs)
            for ring in rings
        ])
        self.play(
            rings.rotate, np.pi/2,
            rings.next_to, unwrapped.get_bottom(), UP,
            run_time = 2,
            path_arc = np.pi/2
        )
        self.play(
            Transform(rings, unwrapped, run_time = 3),
            *added_anims
        )

    def get_unwrapped(self, ring, to_edge = LEFT, **kwargs):
        R = ring.R
        R_plus_dr = ring.R + ring.dR
        n_anchors = ring.get_num_anchor_points()
        result = VMobject()
        result.set_points_as_corners([
            interpolate(np.pi*R_plus_dr*LEFT,  np.pi*R_plus_dr*RIGHT, a)
            for a in np.linspace(0, 1, n_anchors/2)
        ]+[
            interpolate(np.pi*R*RIGHT+ring.dR*UP,  np.pi*R*LEFT+ring.dR*UP, a)
            for a in np.linspace(0, 1, n_anchors/2)
        ])
        result.set_style_data(
            stroke_color = ring.get_stroke_color(),
            stroke_width = ring.get_stroke_width(),
            fill_color = ring.get_fill_color(),
            fill_opacity = ring.get_fill_opacity(),
        )
        result.move_to(self.unwrapped_tip, aligned_edge = DOWN)
        result.shift(R_plus_dr*DOWN)
        result.to_edge(to_edge)

        return result

#############

class Chapter1OpeningQuote(OpeningQuote):
    CONFIG = {
        "quote" : [
            """The art of doing mathematics is finding
            that """, "special case", 
            """that contains all the 
            germs of generality."""
        ],
        "quote_arg_separator" : " ",
        "highlighted_quote_terms" : {
            "special case" : BLUE
        },
        "author" : "David Hilbert",
    }













































