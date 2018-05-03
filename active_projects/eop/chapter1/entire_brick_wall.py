
from big_ol_pile_of_manim_imports import *
from active_projects.eop.reusables import *


class EntireBrickWall(Scene):

    def construct(self):

        row_height = 0.3
        nb_rows = 20
        start_point = 3 * UP + 1 * LEFT
        
        rows = VMobject()
        rows.add(BrickRow(0, height = row_height))
        rows[0].move_to(start_point)
        self.add(rows)

        zero_counter = Integer(0).next_to(start_point + 0.5 * rows[0].width * RIGHT)
        nb_flips_text = TextMobject("\# of flips")
        nb_flips_text.next_to(zero_counter, RIGHT, buff = LARGE_BUFF)
        self.add(zero_counter, nb_flips_text)

        for i in range(1,nb_rows + 1):
            rows.add(BrickRow(i, height = row_height))
            rows[-1].move_to(start_point + (i - 1) * row_height * DOWN)
            self.bring_to_back(rows[-1])
            anims = [
                rows[-1].shift, row_height * DOWN,
                Animation(rows[-2])
            ]
            
            if i % 5 == 0:
                counter = Integer(i)
                counter.next_to(rows[-1].get_right() + row_height * DOWN, RIGHT)
                anims.append(FadeIn(counter))

            self.play(*anims)

        # draw indices under the last row for the number of tails
        tails_counters = VGroup()
        for (i, rect) in enumerate(rows[-1].rects):
            if i < 6 or i > 14:
                continue
            if i == 6:
                counter = TexMobject("\dots", color = COLOR_TAILS)
                counter.next_to(rect, DOWN, buff = 1.5 * MED_SMALL_BUFF)
            elif i == 14:
                counter = TexMobject("\dots", color = COLOR_TAILS)
                counter.next_to(rect, DOWN, buff = 1.5 * MED_SMALL_BUFF)
                counter.shift(0.2 * RIGHT)
            else:
                counter = Integer(i, color = COLOR_TAILS)
                counter.next_to(rect, DOWN)
            tails_counters.add(counter)

        nb_tails_text = TextMobject("\# of tails", color = COLOR_TAILS)
        nb_tails_text.next_to(tails_counters[-1], RIGHT, buff = LARGE_BUFF)

        self.play(
            LaggedStart(FadeIn, tails_counters),
            FadeIn(nb_tails_text)
        )

        special_brick_copy = rows[-1].rects[13].copy()
        self.play(
            rows.fade, 0.9,
            FadeIn(special_brick_copy)
        )


