
from big_ol_pile_of_manim_imports import *
from active_projects.eop.reusable_imports import *

class GenericMorphBrickRowIntoHistogram(Scene):

    CONFIG = {
        "level" : 3,
        "bar_width" : 2.0,
        "bar_anchor_height" : -3.0,
        "show_tallies" : False,
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
                tally.next_to(brick, UP)
                self.add(tally)
                tallies.add(tally)
                brick.set_stroke(width = 3)

        self.remove(self.row.subdivs, self.row.border)

        anims = []
        for brick in self.row.rects:
            anims.append(brick.rotate)
            anims.append(TAU/4)
        
        if self.show_tallies:
            anims.append(FadeOut(tallies))
        self.play(*anims)

        
        anims = []
        for (i,brick) in enumerate(self.row.rects):
            anims.append(brick.next_to)
            anims.append(self.bar_anchors[i])
            anims.append({"direction" : UP, "buff" : 0})
        self.play(*anims)

        self.bars.create_outline()

        anims = []
        for bar in self.bars.submobjects:
            anims.append(bar.set_stroke)
            anims.append({"width" : 0})
        anims.append(FadeIn(self.bars.outline))
        self.play(*anims)



class MorphBrickRowIntoHistogram3(GenericMorphBrickRowIntoHistogram):
    
    CONFIG = {
        "level" : 3,
        "prob_denominator" : 8,
        "bar_width" : 2.0,
        "bar_anchor_height" : -3.0,
        "show_tallies" : True
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
        
        self.play(
            FadeIn(x_axis),
            FadeIn(x_labels),
            FadeIn(nb_tails_label)
        )



        # draw y-guides

        y_guides = VMobject()
        for i in range(1,self.prob_denominator + 1):
            y_guide = Line(5 * LEFT, 5 * RIGHT, stroke_color = GRAY)
            y_guide.move_to(self.bar_anchor_height * UP + i * float(self.row.width) / self.prob_denominator * UP)
            y_guide_label = TexMobject("{" + str(i) + "\over " + str(self.prob_denominator) + "}", color = GRAY)
            y_guide_label.scale(0.7)
            y_guide_label.next_to(y_guide, LEFT)
            y_guide.add(y_guide_label)
            y_guides.add(y_guide)

        self.bring_to_back(y_guides)
        self.play(FadeIn(y_guides), Animation(self.bars))


        total_area_text = TextMobject("total area = 1", color = YELLOW)
        total_area_rect = SurroundingRectangle(total_area_text,
            buff = MED_SMALL_BUFF,
            fill_opacity = 0.5,
            fill_color = BLACK,
            stroke_color = YELLOW
        )

        self.play(
            Write(total_area_text),
            ShowCreation(total_area_rect)
        )

        prob_dist_text = TextMobject("probability distribution", color = YELLOW)
        prob_dist_text.to_corner(UP, buff = LARGE_BUFF)
        prob_dist_rect = SurroundingRectangle(prob_dist_text,
            buff = MED_SMALL_BUFF,
            stroke_color = YELLOW
        )

        self.play(
            Write(prob_dist_text),
            ShowCreation(prob_dist_rect)
        )



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

        nb_tails_label = TextMobject("\# of heads")
        nb_tails_label.next_to(x_labels[-1], RIGHT, MED_LARGE_BUFF)
        
        self.play(
            FadeIn(x_axis),
            FadeIn(x_labels),
            FadeIn(nb_tails_label)
        )

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
            y_guide_label = DecimalNumber(i, num_decimal_points = 2, color = GRAY)
            y_guide_label.scale(0.7)
            y_guide_label.next_to(y_guide, LEFT)
            y_guide.add(y_guide_label)
            y_guides.add(y_guide)

        self.bring_to_back(y_guides)
        self.play(FadeIn(y_guides), Animation(self.bars))

        histogram_width = self.bars.get_width()
        histogram_height = self.bars.get_height()

        # scale to fit screen
        self.scale_x = 10.0/(len(self.bars) * self.bar_width)
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
