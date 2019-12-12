from manimlib.imports import *
from active_projects.eop.reusable_imports import *
from active_projects.eop.combinations import *
from active_projects.eop.independence import *

import itertools as it

class RandyFlipsAndStacks(Scene):

    def construct(self):

        randy = CoinFlippingPiCreature(color = MAROON_E)
        randy.scale(0.5).to_edge(LEFT + DOWN)

        heads = tails = 0
        tally = TallyStack(heads, tails, anchor = ORIGIN)

        nb_flips = 10

        flips = np.random.randint(2, size = nb_flips)

        for i in range(nb_flips):

            self.play(FlipCoin(randy))
            self.wait(0.5)

            flip = flips[i]
            if flip == 0:
                heads += 1
            elif flip == 1:
                tails += 1
            else:
                raise Exception("That side does not exist on this coin")

            new_tally = TallyStack(heads, tails, anchor = ORIGIN)

            if tally.nb_heads == 0 and new_tally.nb_heads == 1:
                self.play(FadeIn(new_tally.heads_stack))
            elif tally.nb_tails == 0 and new_tally.nb_tails == 1:
                self.play(FadeIn(new_tally.tails_stack))
            else:
                self.play(Transform(tally, new_tally))

            tally = new_tally



class TwoDiceTableScene(Scene):

    def construct(self):

        table = TwoDiceTable(cell_size = 1)

        table.center()
        self.add(table)





class VisualCovariance(Scene):


    def construct(self):

        size = 4
        square = Square(side_length = size)
        n_points = 30
        cloud = VGroup(*[
            Dot((x + 0.8*y) * RIGHT + y * UP).set_fill(WHITE, 1)
            for x, y in zip(
                np.random.normal(0, 1, n_points),
                np.random.normal(0, 1, n_points)
            )
        ])
        self.add_foreground_mobject(cloud)

        x_axis = Vector(8*RIGHT, color = WHITE).move_to(2.5*DOWN)
        y_axis = Vector(5*UP, color = WHITE).move_to(4*LEFT)

        self.add(x_axis, y_axis)


        random_pairs = [ (p1, p2) for (p1, p2) in
            it.combinations(cloud, 2)
        ]
        np.random.shuffle(random_pairs)



        for (p1, p2) in random_pairs:
            c1, c2 = p1.get_center(), p2.get_center()
            x1, y1, x2, y2 = c1[0], c1[1], c2[0], c2[1]
            if x1 >= x2:
                continue
            if y2 > y1:
                # make a red rect
                color = RED
                opacity = 0.1
               
            elif y2 < y1:
                # make a blue rect
                color = BLUE
                opacity = 0.2

            rect = Rectangle(width = x2 - x1, height = abs(y2 - y1))
            rect.set_fill(color = color, opacity = opacity)
            rect.set_stroke(width = 0)
            rect.move_to((c1+c2)/2)

            self.play(FadeIn(rect), run_time = 0.05)




class BinaryChoices(Scene):

    def construct(self):

        example1 = BinaryOption(UprightHeads(), UprightTails())
        example2 = BinaryOption(Male(), Female())
        example3 = BinaryOption(Checkmark(), Xmark())

        example2.next_to(example1, DOWN, buff = MED_LARGE_BUFF)
        example3.next_to(example2, DOWN, buff = MED_LARGE_BUFF)

        all = VGroup(example1, example2, example3)
        all = all.scale(2)

        self.play(
            LaggedStartMap(FadeIn, all)
        )
