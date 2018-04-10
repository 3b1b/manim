from big_ol_pile_of_manim_imports import *

NAME_WITH_SPACES = "Prime Meridian"
DIAMETER = 3.0
RADIUS = DIAMETER / 2
LETTER_SCALE = 1

class NameAnimationScene(Scene):

    def construct(self):

        name = ''.join(NAME_WITH_SPACES.split(' '))
        letters = list(name)
        nb_letters = len(letters)
        randy = PiCreature()
        randy.move_to(ORIGIN).scale_to_fit_height(0.5 * DIAMETER)
        randy.set_color(BLUE_E)
        randy.look_at(UP + RIGHT)
        self.add(randy)
        dtheta = TAU/nb_letters
        angles = np.arange(TAU/4,-3 * TAU / 4,-dtheta)
        name_mob = VGroup()
        for (letter, angle) in zip(letters, angles):
            letter_mob = TextMobject(letter).scale(LETTER_SCALE)
            pos = RADIUS * np.cos(angle) * RIGHT + RADIUS * np.sin(angle) * UP
            letter_mob.move_to(pos)
            name_mob.add(letter_mob)

        pos2 = RADIUS * np.cos(angles[2]) * RIGHT + RADIUS * np.sin(angles[2]) * UP

        self.play(
            LaggedStart(Write, name_mob, run_time = 3),
            ApplyMethod(randy.look_at, pos2, run_time = 3)
        )

        for i in range(2,nb_letters + 2):

            group = []

            for (j,letter_mob) in enumerate(name_mob.submobjects):

                new_angle = TAU / 4 - i * j * dtheta
                new_pos = RADIUS * np.cos(new_angle) * RIGHT + RADIUS * np.sin(new_angle) * UP
                letter_mob.target = letter_mob.copy().move_to(new_pos)
                anim = MoveToTarget(letter_mob, path_arc = - j * dtheta)
                group.append(anim)

            self.play(
                AnimationGroup(*group, run_time = 3),
                ApplyMethod(randy.look_at,name_mob.submobjects[2], run_time = 3)
            )
            self.wait(0.5)


        thank_you = TextMobject("Thank You!").next_to(randy, DOWN)
        new_randy = randy.copy()
        new_randy.change("hooray")
        new_randy.set_color(BLUE_E)
        new_randy.look_at(ORIGIN)
        self.play(
            Transform(name_mob, thank_you),
            Transform(randy, new_randy)
        )












