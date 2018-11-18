#!/usr/bin/env python2
# -*- coding: utf-8 -*-


from big_ol_pile_of_manim_imports import *

NAME_WITH_SPACES = "Prime Meridian"
DIAMETER = 3.0
RADIUS = DIAMETER / 2
LETTER_SCALE = 1


class NameAnimationScene(Scene):
    CONFIG = {
        "animated_name": "Prime Meridian"
    }

    def construct(self):
        name = self.animated_name
        letter_mobs = TextMobject(name)
        nb_letters = len(letter_mobs)
        randy = PiCreature()
        randy.move_to(ORIGIN).set_height(0.5 * DIAMETER)
        randy.set_color(BLUE_E)
        randy.look_at(UP + RIGHT)
        self.add(randy)
        dtheta = TAU / nb_letters
        angles = np.arange(TAU / 4, -3 * TAU / 4, -dtheta)
        name_mob = VGroup()
        for (letter_mob, angle) in zip(letter_mobs, angles):
            letter_mob.scale(LETTER_SCALE)
            pos = RADIUS * np.cos(angle) * RIGHT + RADIUS * np.sin(angle) * UP
            letter_mob.move_to(pos)
            name_mob.add(letter_mob)

        pos2 = RADIUS * np.cos(angles[2]) * RIGHT + \
            RADIUS * np.sin(angles[2]) * UP

        times_n_label = VGroup(
            TexMobject("\\times"),
            Integer(1)
        )
        times_n_label.arrange_submobjects(RIGHT)
        times_n_label.shift(FRAME_WIDTH * RIGHT / 4)
        times_n_label.to_edge(UP)

        self.play(
            LaggedStart(FadeIn, name_mob, run_time=3),
            ApplyMethod(randy.change, "pondering", pos2, run_time=1),
            FadeIn(times_n_label)
        )

        for n in range(2, nb_letters + 2):

            group = []

            for (j, letter_mob) in enumerate(name_mob.submobjects):

                new_angle = TAU / 4 - n * j * dtheta
                new_pos = RADIUS * np.cos(new_angle) * \
                    RIGHT + RADIUS * np.sin(new_angle) * UP
                letter_mob.target = letter_mob.copy().move_to(new_pos)
                anim = MoveToTarget(letter_mob, path_arc=- j * dtheta)
                group.append(anim)
            new_n = Integer(n)
            new_n.move_to(times_n_label[1])
            self.play(
                AnimationGroup(*group, run_time=3),
                UpdateFromFunc(randy, lambda r: r.look_at(name_mob.submobjects[2])),
                FadeOut(times_n_label[1]),
                FadeIn(new_n)
            )
            times_n_label.submobjects[1] = new_n
            self.wait(0.5)

        thank_you = TextMobject("Thank You!").next_to(randy, DOWN)
        new_randy = randy.copy()
        new_randy.change("hooray")
        new_randy.set_color(BLUE_E)
        new_randy.look_at(ORIGIN)
        self.play(
            ReplacementTransform(name_mob, VGroup(*thank_you)),
            Transform(randy, new_randy)
        )
        self.play(Blink(randy))

    def __str__(self):
        return self.animated_name.replace(" ", "") + "Animation"


names = []

if __name__ == "__main__":
    for name in names:
        try:
            NameAnimationScene(
                frame_duration=PRODUCTION_QUALITY_FRAME_DURATION,
                camera_config=PRODUCTION_QUALITY_CAMERA_CONFIG,
                animated_name=name,
                write_to_movie=True,
                output_directory=os.path.join(
                    VIDEO_DIR,
                    "active_projects",
                    "name_animations",
                ),
            )
        except Exception as e:
            print("Could not animate %s: %s" % (name, e))
