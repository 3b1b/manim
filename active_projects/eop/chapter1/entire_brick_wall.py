
from manimlib.imports import *
from active_projects.eop.reusable_imports import *
from active_projects.eop.chapter1.brick_row_scene import BrickRowScene

class EntireBrickWall(BrickRowScene, MovingCameraScene):

    def setup(self):
        super(BrickRowScene, self).setup()
        super(PiCreatureScene, self).setup()


    def construct(self):

        self.remove(self.get_primary_pi_creature())

        row_height = 0.3
        nb_rows = 20
        start_point = 3 * UP + 1 * LEFT
        
        rows = VMobject()
        rows.add(BrickRow(0, height = row_height))
        rows.move_to(start_point)
        self.add(rows)
            
        zero_counter = Integer(0).next_to(start_point + 0.5 * rows[0].width * RIGHT)
        nb_flips_text = TextMobject("\# of flips")
        nb_flips_text.next_to(zero_counter, RIGHT, buff = LARGE_BUFF)
        self.add(zero_counter, nb_flips_text)
        flip_counters = VGroup(zero_counter)

        for i in range(1, nb_rows + 1):
            rows.add(rows[-1].copy())
            self.bring_to_back(rows[-1])
            anims = [
                rows[-1].shift, row_height * DOWN,
                Animation(rows[-2])
            ]
            
            if i % 5 == 0:
                counter = Integer(i)
                counter.next_to(rows[-1].get_right() + row_height * DOWN, RIGHT)
                flip_counters.add(counter)
                anims.append(FadeIn(counter))

            self.play(*anims)

            self.play(SplitRectsInBrickWall(rows[-1]))
            rows.submobjects[-1] = self.merge_rects_by_subdiv(rows[-1])
            rows.submobjects[-1] = self.merge_rects_by_coloring(rows[-1])


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
            LaggedStartMap(FadeIn, tails_counters),
            FadeIn(nb_tails_text)
        )

        # remove any hidden brick rows
        self.clear()
        self.add(nb_flips_text)

        mobs_to_shift = VGroup(
            rows, flip_counters, tails_counters, nb_tails_text, 
        )
        self.play(mobs_to_shift.shift, 3 * UP)

        last_row_rect = SurroundingRectangle(rows[-1], buff = 0)
        last_row_rect.set_stroke(color = YELLOW, width = 6)

        rows.save_state()
        self.play(
            rows.fade, 0.9,
            ShowCreation(last_row_rect)
        )

        def highlighted_brick(row = 20, nb_tails = 10):
            brick_copy = rows[row].rects[nb_tails].copy()
            brick_copy.set_fill(color = YELLOW, opacity = 0.8)
            prob_percentage = float(choose(row, nb_tails)) / 2**row * 100
            brick_label = DecimalNumber(prob_percentage,
                unit = "\%", num_decimal_places = 1, color = BLACK)
            brick_label.move_to(brick_copy)
            brick_label.set_height(0.8 * brick_copy.get_height())
            return VGroup(brick_copy, brick_label)

        highlighted_bricks = [
            highlighted_brick(row = 20, nb_tails = i)
            for i in range(20)
        ]
        self.wait()
        self.play(
            FadeIn(highlighted_bricks[10])
        )
        self.wait()
        self.play(
            FadeOut(highlighted_bricks[10]),
            FadeIn(highlighted_bricks[9]),
            FadeIn(highlighted_bricks[11]),
        )
        self.wait()
        self.play(
            FadeOut(highlighted_bricks[9]),
            FadeOut(highlighted_bricks[11]),
            FadeIn(highlighted_bricks[8]),
            FadeIn(highlighted_bricks[12]),
        )
        self.wait()
        self.play(
            FadeOut(highlighted_bricks[8]),
            FadeOut(highlighted_bricks[12]),
            FadeOut(last_row_rect),
            rows.restore,
        )
        self.wait()
        new_frame = self.camera_frame.copy()
        new_frame.scale(0.0001).move_to(rows.get_corner(DR))

        self.play(
            Transform(self.camera_frame, new_frame,
                run_time = 9,
                rate_func = exponential_decay
            )
        )





















