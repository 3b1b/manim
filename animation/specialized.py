from __future__ import absolute_import

import numpy as np
import re

from constants import *

from mobject.mobject import Group
from animation.transform import ApplyMethod
from animation.transform import ReplacementTransform
from animation.creation import FadeIn
from animation.creation import FadeOut
from animation.composition import AnimationGroup
from animation.composition import LaggedStart
from mobject.svg.drawings import Car
from mobject.types.vectorized_mobject import VGroup
from mobject.geometry import Circle
from utils.config_ops import digest_config


class MoveCar(ApplyMethod):
    CONFIG = {
        "moving_forward": True,
    }

    def __init__(self, car, target_point, **kwargs):
        assert isinstance(car, Car)
        ApplyMethod.__init__(self, car.move_to, target_point, **kwargs)
        displacement = self.target_mobject.get_right() - self.starting_mobject.get_right()
        distance = np.linalg.norm(displacement)
        if not self.moving_forward:
            distance *= -1
        tire_radius = car.get_tires()[0].get_width() / 2
        self.total_tire_radians = -distance / tire_radius

    def update_mobject(self, alpha):
        ApplyMethod.update_mobject(self, alpha)
        if alpha == 0:
            return
        radians = alpha * self.total_tire_radians
        for tire in self.mobject.get_tires():
            tire.rotate_in_place(radians)


class Broadcast(LaggedStart):
    CONFIG = {
        "small_radius": 0.0,
        "big_radius": 5,
        "n_circles": 5,
        "start_stroke_width": 8,
        "color": WHITE,
        "remover": True,
        "lag_ratio": 0.7,
        "run_time": 3,
        "remover": True,
    }

    def __init__(self, focal_point, **kwargs):
        digest_config(self, kwargs)
        circles = VGroup()
        for x in range(self.n_circles):
            circle = Circle(
                radius=self.big_radius,
                stroke_color=BLACK,
                stroke_width=0,
            )
            circle.move_to(focal_point)
            circle.save_state()
            circle.scale_to_fit_width(self.small_radius * 2)
            circle.set_stroke(self.color, self.start_stroke_width)
            circles.add(circle)
        LaggedStart.__init__(
            self, ApplyMethod, circles,
            lambda c: (c.restore,),
            **kwargs
        )

class TransformEquation(AnimationGroup):
    """
    When writing the regex, parentheses and + in the equation must be double
    escaped. LaTeX characters must be quadruple escaped (e.g. \\\\le).
    """
    def mob_from_char(self, eq, tex_string, target):
        index = 0
        for char in tex_string:
            if char == target:
                return eq.submobjects[0].submobjects[index]
            else:
                index += 1
        raise Exception

    def mob_size(self, regex, regex_index, subgroup=False):
        if regex[regex_index] == ' ':
            return 0
        elif regex[regex_index] == '^':
            return 0
        elif regex[regex_index:].startswith('\\log'):
            return 3
        else:
            return 1

    def char_size(self, regex, regex_index, subgroup=False):
        if regex[regex_index:regex_index+2] == '\\\\':
            # handle tex
            # TODO: use re.search for ' ' or '\\'
            return regex[regex_index:].find(' ')
        elif regex[regex_index] == '\\':
            if subgroup:
                # handle tex
                # TODO: use re.search for ' ' or '\\' (or EOL)
                return regex[regex_index:].find(' ')
            else:
                return 2
        elif regex[regex_index] == '^':
            return 1
        return 1

    def append_mob(self, eq, mobs, regex, regex_index, mob_index, subgroup=False):
        num_mobs = self.mob_size(regex, regex_index, subgroup=subgroup)
        num_chars = self.char_size(regex, regex_index, subgroup=subgroup)
        for i in range(num_mobs):
            mobs.append(eq.submobjects[0].submobjects[mob_index + i])
        return num_mobs, num_chars

    def split_by_regex(self, eq, regex):
        match = re.match(regex, eq.tex_string)
        if not match:
            print "{} does not match {}".format(regex, eq.tex_string)
            import ipdb; ipdb.set_trace(context=7)
            assert(False)
        if match.group(0) != eq.tex_string:
            import ipdb; ipdb.set_trace(context=7)
            assert(False)
        regex_index = 0
        mob_index = 0
        group_index = 1
        group = VGroup()
        mobs = []
        while True:
            if mob_index == len(eq.submobjects[0].submobjects):
                if mobs:
                    group.submobjects.append(VGroup(*mobs))
                break
            group_match = re.match("^\([^)]*\)", regex[regex_index:])
            if group_match:
                # handle group
                if mobs:
                    group.submobjects.append(VGroup(*mobs))
                    mobs = []
                submobs = []
                group_regex_index = 0
                while group_regex_index < len(match.group(group_index)):
                    num_mobs, num_chars = self.append_mob(eq, submobs, match.group(group_index), group_regex_index, mob_index, subgroup=True)
                    mob_index += num_mobs
                    group_regex_index += num_chars
                regex_index += len(group_match.group(0))
                group_index += 1
                group.submobjects.append(VGroup(*submobs))
            else:
                # add mob to list
                num_mobs, num_chars = self.append_mob(eq, mobs, regex, regex_index, mob_index)
                mob_index += num_mobs
                regex_index += num_chars
        return group


    def __init__(self, eq1, eq2, regex, regex2=None, map_list=None, align_char=None):
        # align equations
        if align_char:
            difference_vec = \
                self.mob_from_char(eq1, eq1.tex_string, align_char).get_center() - \
                self.mob_from_char(eq2, eq2.tex_string, align_char).get_center()
        else:
            difference_vec = eq1.get_center() - eq2.get_center()
        eq2.shift(difference_vec)

        if regex2 is None:
            g1 = self.split_by_regex(eq1, regex)
            g2 = self.split_by_regex(eq2, regex)
            assert(len(g1.submobjects) == len(g2.submobjects))
            trans = ReplacementTransform(g1, g2)
            AnimationGroup.__init__(self, trans)
        else:
            assert(map_list)
            g1 = self.split_by_regex(eq1, regex)
            g2 = self.split_by_regex(eq2, regex2)
            self.g1 = g1
            self.g2 = g2
            G1 = VGroup()
            G2 = VGroup()
            F1 = Group()
            F2 = Group()
            g1_nodes = set(pair[0] for pair in map_list)
            g2_nodes = set(pair[1] for pair in map_list)
            if len(g1_nodes) <= len(g2_nodes):
                map_list.sort(key=lambda x: x[0])
                i = 0
                while i < len(map_list):
                    # import ipdb; ipdb.set_trace(context=5)
                    l1 = [g1.submobjects[map_list[i][0]]]
                    l2 = [g2.submobjects[map_list[i][1]]]
                    i += 1
                    while i < len(map_list) and map_list[i][0] == map_list[i-1][0]:
                        l2.append(g2.submobjects[map_list[i][1]])
                        i += 1
                    G1.submobjects.append(VGroup(*l1))
                    G2.submobjects.append(VGroup(*l2))
            for i in range(len(g1.submobjects)):
                if i not in g1_nodes:
                    F1.submobjects.append(g1.submobjects[i])
            for i in range(len(g2.submobjects)):
                if i not in g2_nodes:
                    F2.submobjects.append(g2.submobjects[i])
            self.g1 = g1
            self.g2 = g2
            trans   = ReplacementTransform(G1, G2)
            fadeout = FadeOut(F1)
            fadein  = FadeIn(F2)
            AnimationGroup.__init__(self, trans, fadeout, fadein)
