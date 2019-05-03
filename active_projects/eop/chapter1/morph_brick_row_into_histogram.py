
from manimlib.imports import *
from active_projects.eop.reusable_imports import *

class GenericMorphBrickRowIntoHistogram(Scene):

    CONFIG = {
        "level" : 3,
        "bar_width" : 2.0,
        "bar_anchor_height" : -3.0,
        "show_tallies" : False,
        "show_nb_flips" : True
    }

    def construct(self):

        self.row = BrickRow(self.level, height = self.bar_width, width = 10)
        self.bars = OutlineableBars(*[self.row.rects[i] for i in range(self.level + 1)])
        self.bar_anchors = [self.bar_anchor_height * UP + self.row.height * (i - 0.5 * self.level) * RIGHT for i in range(self.level + 1)]

        self.add(self.row)

        if self.show_tallies:

            tallies = VMobject()

            for (i,brick) in enumerate(self.row.rects):
                tally = TallyStack(self.level - i, i)
                tally.move_to(brick)
                self.add(tally)
                tallies.add(tally)
                brick.set_stroke(width = 3)

        if self.show_nb_flips:
            nb_flips_text = TextMobject("\# of flips: " + str(self.level))
            nb_flips_text.to_corner(UR)
            self.add(nb_flips_text)

        self.remove(self.row.subdivs, self.row.border)

        for rect in self.row.rects:
            rect.set_stroke(color = WHITE, width = 3)

        self.wait()
        self.play(
            self.row.rects.space_out_submobjects, {"factor" : 1.3},
            FadeOut(tallies)
        )
        self.wait()
        anims = []
        for brick in self.row.rects:
            anims.append(brick.rotate)
            anims.append(TAU/4)
        
        self.play(*anims)

        self.wait()

        anims = []
        for (i,brick) in enumerate(self.row.rects):
            anims.append(brick.next_to)
            anims.append(self.bar_anchors[i])
            anims.append({"direction" : UP, "buff" : 0})
        self.play(*anims)
        self.wait()

        self.bars.create_outline()
        anims = [
            ApplyMethod(rect.set_stroke, {"width" : 0})
                for rect in self.bars
        ]
        anims.append(FadeIn(self.bars.outline))
        self.play(*anims)

        self.wait()



class MorphBrickRowIntoHistogram3(GenericMorphBrickRowIntoHistogram):
    
    CONFIG = {
        "level" : 3,
        "prob_denominator" : 8,
        "bar_width" : 2.0,
        "bar_anchor_height" : -3.0,
        "show_tallies" : True,
        "show_nb_flips" : False
    }

    def construct(self):



        super(MorphBrickRowIntoHistogram3,self).construct()
        

        # draw x-axis

        x_axis = Line(ORIGIN, 10 * RIGHT, color = WHITE, buff = 0)
        x_axis.next_to(self.bars, DOWN, buff = 0)
        #x_labels = VMobject(*[TexMobject(str(i)) for i in range(4)])
        x_labels = VMobject()

        for (i, bar) in enumerate(self.bars):
            label = Integer(i)
            label.next_to(self.bar_anchors[i], DOWN)
            x_labels.add(label)

        nb_tails_label = TextMobject("\# of tails")
        nb_tails_label.next_to(x_labels[-1], RIGHT, MED_LARGE_BUFF)



        # draw y-guides

        y_guides = VMobject()
        for i in range(0,self.prob_denominator + 1):
            y_guide = Line(5 * LEFT, 5 * RIGHT, stroke_color = GRAY)
            y_guide.move_to(self.bar_anchor_height * UP + i * float(self.row.width) / self.prob_denominator * UP)
            y_guide_label = TexMobject("{" + str(i) + "\over " + str(self.prob_denominator) + "}", color = GRAY)
            y_guide_label.scale(0.7)
            y_guide_label.next_to(y_guide, LEFT)
            if i != 0:
                y_guide.add(y_guide_label)
            y_guides.add(y_guide)
        self.wait()

        self.play(
            FadeIn(y_guides),
            Animation(self.bars.outline),
            Animation(self.bars)
        )
        self.wait()

        self.play(
            FadeIn(x_axis),
            FadeIn(x_labels),
            FadeIn(nb_tails_label)
        )

        self.add_foreground_mobject(nb_tails_label)
        area_color = YELLOW

        total_area_text = TextMobject("total area =", color = area_color)
        area_decimal = DecimalNumber(0, color = area_color, num_decimal_places = 3)
        area_decimal.next_to(total_area_text, RIGHT)

        total_area_group = VGroup(total_area_text, area_decimal)
        total_area_group.move_to(2.7 * UP)
        self.wait()

        self.play(
            FadeIn(total_area_text),
        )
        self.wait()

        cumulative_areas = [0.125, 0.5, 0.875, 1]
        covering_rects = self.bars.copy()
        for (i,rect) in enumerate(covering_rects):
            rect.set_fill(color = area_color, opacity = 0.5)
            self.play(
                FadeIn(rect, rate_func = linear),
                ChangeDecimalToValue(area_decimal, cumulative_areas[i],
                    rate_func = linear)
            )
            self.wait(0.2)

        self.wait()

        total_area_rect = SurroundingRectangle(
            total_area_group,
            buff = MED_SMALL_BUFF,
            stroke_color = area_color
        )

        self.play(
            FadeOut(covering_rects),
            ShowCreation(total_area_rect)
        )
        self.wait()



class MorphBrickRowIntoHistogram20(GenericMorphBrickRowIntoHistogram):
    CONFIG = {
        "level" : 20,
        "prob_ticks" : 0.05,
        "bar_width" : 0.5,
        "bar_anchor_height" : -3.0,
        "x_ticks": 5
    }

    def construct(self):

        super(MorphBrickRowIntoHistogram20, self).construct()

        x_axis = Line(ORIGIN, 10 * RIGHT, color = WHITE, buff = 0)
        x_axis.next_to(self.bars, DOWN, buff = 0)
        #x_labels = VMobject(*[TexMobject(str(i)) for i in range(4)])
        x_labels = VMobject()
        for (i, bar) in enumerate(self.bars):
            if i % self.x_ticks != 0:
                continue
            label = Integer(i)
            label.next_to(self.bar_anchors[i], DOWN)
            x_labels.add(label)

        nb_tails_label = TextMobject("\# of tails")
        nb_tails_label.move_to(5 * RIGHT + 2.5 * DOWN)
        self.wait()

        self.play(
            FadeIn(x_axis),
            FadeIn(x_labels),
            FadeIn(nb_tails_label)
        )
        self.wait()

        # draw y-guides

        max_prob = float(choose(self.level, self.level/2)) / 2 ** self.level

        y_guides = VMobject()
        y_guide_heights = []
        prob_grid = np.arange(self.prob_ticks, 1.3 * max_prob, self.prob_ticks)
        for i in prob_grid:
            y_guide = Line(5 * LEFT, 5 * RIGHT, stroke_color = GRAY)
            y_guide_height = self.bar_anchor_height + i * float(self.row.width)
            y_guide_heights.append(y_guide_height)
            y_guide.move_to(y_guide_height * UP)
            y_guide_label = DecimalNumber(i, num_decimal_places = 2, color = GRAY)
            y_guide_label.scale(0.7)
            y_guide_label.next_to(y_guide, LEFT)
            y_guide.add(y_guide_label)
            y_guides.add(y_guide)

        self.bring_to_back(y_guides)
        self.play(FadeIn(y_guides), Animation(self.bars))
        self.wait()

        histogram_width = self.bars.get_width()
        histogram_height = self.bars.get_height()

        # scale to fit screen
        self.scale_x = 10.0/((len(self.bars) - 1) * self.bar_width)
        self.scale_y = 6.0/histogram_height


        anims = []
        for (bar, x_label) in zip(self.bars, x_labels):
            v = (self.scale_x - 1) * x_label.get_center()[0] * RIGHT
            anims.append(x_label.shift)
            anims.append(v)


        anims.append(self.bars.stretch_about_point)
        anims.append(self.scale_x)
        anims.append(0)
        anims.append(ORIGIN)
        anims.append(self.bars.outline.stretch_about_point)
        anims.append(self.scale_x)
        anims.append(0)
        anims.append(ORIGIN)

        self.play(*anims)
        self.wait()

        anims = []
        for (guide, i, h) in zip(y_guides, prob_grid, y_guide_heights):
            new_y_guide_height = self.bar_anchor_height + i * self.scale_y * float(self.row.width)
            v = (new_y_guide_height - h) * UP
            anims.append(guide.shift)
            anims.append(v)

        anims.append(self.bars.stretch_about_point)
        anims.append(self.scale_y)
        anims.append(1)
        anims.append(self.bars.get_bottom())
        anims.append(self.bars.outline.stretch_about_point)
        anims.append(self.scale_y)
        anims.append(1)
        anims.append(self.bars.get_bottom())

        self.play(*anims)
        self.wait()

class MorphBrickRowIntoHistogram100(MorphBrickRowIntoHistogram20):
    CONFIG = {
        "level" : 100,
        "x_ticks": 20,
        "prob_ticks": 0.02
    }

class MorphBrickRowIntoHistogram500(MorphBrickRowIntoHistogram20):
    CONFIG = {
        "level" : 500,
        "x_ticks": 100,
        "prob_ticks": 0.01
    }
