from big_ol_pile_of_manim_imports import *
from active_projects.eop.reusables import *

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



class TwoDiceTable(Scene):

    def construct(self):

        table = VGroup()
        cell_size = 1
        colors = color_gradient([RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE], 13)

        for i in range(1,7):
            for j in range(1,7):
                cell = Square(side_length = cell_size)
                cell.set_fill(color = colors[i+j], opacity = 0.8)
                label = Integer(i+j)
                label.move_to(cell)
                cell.add(label)
                cell.move_to(i*cell_size*RIGHT + j*cell_size*DOWN)
                table.add(cell)

        table.center()
        self.add(table)

        row1 = RowOfDice().match_width(table)
        print row1.is_subpath
        row2 = row1.copy().rotate(-TAU/4)
        print row2.is_subpath
        row1.next_to(table, UP)
        row2.next_to(table, LEFT)
        table.add(row1, row2)
        table.center()



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
            LaggedStart(FadeIn, all)
        )
