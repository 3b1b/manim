from big_ol_pile_of_manim_imports import *


class TwoSolutionsWrapper(Scene):
    CONFIG = {
    }

    def construct(self):
        pass


class ConnectionToOptics(Scene):
    def construct(self):
        e_group, m_group = k_groups = self.get_kinematics_groups()

        self.add(k_groups)

    def get_kinematics_groups(self):
        tex_to_color_map = {
            "m_1": BLUE,
            "m_2": BLUE,
            "v_1": RED,
            "v_2": RED,
        }
        energy_eq = TexMobject(
            "\\frac{1}{2} m_1 (v_1)^2 + "
            "\\frac{1}{2} m_2 (v_2)^2 = "
            "\\text{const.}",
            tex_to_color_map=tex_to_color_map
        )
        momentum_eq = TexMobject(
            "m_1 v_1 + m_2 v_2 = \\text{const.}",
            tex_to_color_map=tex_to_color_map
        )
        energy_label = TextMobject(
            "Conservation of energy"
        )
        momentum_label = TextMobject(
            "Conservation of momentum"
        )
        energy_group = VGroup(energy_eq, energy_label)
        momentum_group = VGroup(momentum_eq, momentum_label)
        groups = VGroup(energy_group, momentum_group)
        for group in groups:
            group.arrange_submobjects(DOWN)
        groups.arrange_submobjects(DOWN, LARGE_BUFF)
        groups.to_edge(LEFT)
        return groups
