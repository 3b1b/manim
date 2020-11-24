from manimlib.imports import *


def get_value_grid(n_rows=6, n_cols=6):
    random.seed(1)
    boxes = VGroup(*[Square() for x in range(n_rows * n_cols)])
    array = np.array(list(boxes)).reshape((n_rows, n_cols))
    boxes.array = array
    boxes.arrange_in_grid(n_rows, n_cols, buff=0)
    boxes.set_height(5)
    boxes.to_edge(DOWN)
    boxes.shift(UP)
    boxes.set_stroke(BLUE_D, 2)
    for box in boxes:
        value = DecimalNumber(
            np.round(random.random(), 1),
            num_decimal_places=1
        )
        box.set_fill(WHITE, opacity=0.8 * value.get_value())
        box.value = value
        value.match_height(box)
        value.scale(0.3)
        value.move_to(box)
        box.add(value)
    boxes.array[5, 1].value.set_value(0.4)  # Tweaking for examples
    return boxes


def highlight_box(box, opacity=0.5, color=PINK):
    box.set_stroke(color, opacity)
    box[1].set_stroke(BLACK, 2, background=True)
    return box


def get_box_highlight(box, color=PINK, stroke_width=8, opacity=0.25):
    highlight = SurroundingRectangle(box, buff=0)
    highlight.set_fill(color, opacity)
    highlight.set_stroke(color, stroke_width)
    return highlight


class GreedyAlgorithm(Scene):
    def construct(self):
        n_rows, n_cols = 6, 6
        boxes = get_value_grid(n_rows, n_cols)
        self.add(boxes)

        last_sum_term = boxes[0].value.copy()
        last_sum_term.to_edge(UP)
        last_sum_term.set_x(-5)
        sum_terms = VGroup()
        to_fade = VGroup()

        (i, j) = (0, 3)
        while i < n_rows:
            box = boxes.array[i, j]
            value = box.value
            box_highlight = get_box_highlight(box)
            sum_term = VGroup(
                TexMobject("+"),
                value.copy()
            )
            if i == 0:
                sum_term[0].set_opacity(0)
            sum_term.arrange(RIGHT, buff=0.2)
            sum_term.next_to(last_sum_term, RIGHT, buff=0.2)
            sum_terms.add(sum_term)
            last_sum_term = sum_term

            self.play(
                FadeIn(box_highlight),
                FadeIn(sum_term),
                *map(FadeOut, to_fade)
            )

            i += 1
            # Find new j
            if i < n_rows:
                next_boxes = VGroup()
                for nj in range(j - 1, j + 2):
                    next_boxes.add(boxes.array[i, clip(nj, 0, n_cols - 1)])

                next_highlights = VGroup()
                for nb in next_boxes:
                    next_highlights.add(get_box_highlight(nb, stroke_width=4))

                self.play(FadeIn(next_highlights))

                min_box_index = np.argmin([b.value.get_value() for b in next_boxes])
                j = j - 1 + min_box_index
                j = clip(j, 0, n_cols - 1)  # Am I doing this right?
                to_fade = next_highlights

        final_sum = VGroup(
            TexMobject("="),
            DecimalNumber(
                sum([np.round(st[1].get_value(), 1) for st in sum_terms]),
                height=sum_terms.get_height(),
                num_decimal_places=1,
            ).set_color(YELLOW)
        )
        final_sum.arrange(RIGHT, buff=0.2)
        final_sum.next_to(sum_terms, RIGHT, buff=0.2)

        self.play(Write(final_sum))
        self.wait()


class RecrusiveExhaustiveSearch(Scene):
    def construct(self):
        n_rows = 6
        n_cols = 6
        boxes = get_value_grid(n_rows, n_cols)
        self.add(boxes)

        seam = [
            (i, 3)
            for i in range(n_rows)
        ]

        def get_seam_sum(seam):
            terms = VGroup(*[boxes.array[i, j].value.copy() for (i, j) in seam])
            row = VGroup()
            for term in terms[:-1]:
                row.add(term)
                row.add(TexMobject("+"))
            row.add(terms[-1])
            row.add(TexMobject("="))
            sum_term = DecimalNumber(sum([t.get_value() for t in terms]), num_decimal_places=1)
            sum_term.match_height(terms[0])
            sum_term.set_color(YELLOW)
            row.add(sum_term)
            row.arrange(RIGHT, buff=0.15)
            row.to_edge(UP)
            return row

        def get_highlighted_seam(seam):
            return VGroup(*[
                get_box_highlight(boxes.array[i, j])
                for (i, j) in seam
            ])

        def get_all_seams(seam_starts, n_rows=n_rows, n_cols=n_cols):
            if seam_starts[0][-1][0] == n_rows - 1:
                return seam_starts
            new_seams = []
            for seam in seam_starts:
                i, j = seam[-1]
                # Adjacent j values below (i, j)
                js = []
                if j > 0:
                    js.append(j - 1)
                js.append(j)
                if j < n_cols - 1:
                    js.append(j + 1)

                for j_prime in js:
                    new_seams.append([*seam, (i + 1, j_prime)])
            return get_all_seams(new_seams, n_rows, n_cols)

        all_seams = get_all_seams([[(0, 3)]])

        curr_min_energy = np.inf
        curr_best_seam = VGroup()
        for seam in all_seams:
            ss = get_seam_sum(seam)
            hs = get_highlighted_seam(seam)

            energy = ss[-1].get_value()
            if energy < curr_min_energy:
                curr_min_energy = energy
                curr_best_seam = VGroup(ss, hs)

            self.add(ss, hs)
            self.wait(0.05)
            self.remove(ss, hs)

        self.add(curr_best_seam)
        self.wait()


class DynamicProgrammingApproachSearch(Scene):
    def construct(self):
        n_rows = 6
        n_cols = 6
        boxes = get_value_grid(n_rows, n_cols)
        boxes.to_corner(DL)
        boxes.shift(UP)
        self.add(boxes)

        new_boxes = get_value_grid(n_rows, n_cols)
        new_boxes.to_corner(DR)
        new_boxes.shift(UP)
        for box in new_boxes:
            box.set_fill(opacity=0)
            box.value.set_fill(opacity=0)
        self.add(new_boxes)

        left_title = TextMobject("Energy")
        right_title = TextMobject("Minimal energy to bottom")
        left_title.next_to(boxes, UP)
        right_title.next_to(new_boxes, UP)

        self.add(left_title, right_title)

        op_factor = 0.5

        movers = VGroup()
        for j in range(n_cols):
            box = boxes.array[n_rows - 1, j]
            new_box = new_boxes.array[n_rows - 1, j]
            new_box.generate_target()
            new_box.target.match_style(box)
            new_box.target.set_fill(TEAL, opacity=op_factor * new_box.value.get_value())
            new_box.target[1].set_fill(WHITE, 1)
            movers.add(new_box)

        self.play(LaggedStartMap(MoveToTarget, movers))
        self.wait()

        for i in range(n_rows - 2, -1, -1):
            for j in range(n_cols):
                box = boxes.array[i, j]
                new_box = new_boxes.array[i, j]
                box_highlight = get_box_highlight(box)
                new_box_highlight = get_box_highlight(new_box)
                boxes_below = [
                    new_boxes.array[i + 1, j]
                    for j in range(j - 1, j + 2)
                    if 0 <= j < n_cols
                ]
                index = np.argmin([bb.value.get_value() for bb in boxes_below])
                low_box = boxes_below[index]
                low_box_highlight = get_box_highlight(low_box, stroke_width=3)
                low_box_highlight.fade(0.5)

                new_box.value.set_value(new_box.value.get_value() + low_box.value.get_value())
                new_box.generate_target()
                new_box.target.set_fill(TEAL, opacity=op_factor * new_box.value.get_value())
                new_box.target[1].set_fill(WHITE, 1)

                self.play(
                    FadeIn(box_highlight),
                    FadeIn(new_box_highlight),
                    FadeIn(low_box_highlight),
                    MoveToTarget(new_box),
                )
                self.play(
                    FadeOut(box_highlight),
                    FadeOut(new_box_highlight),
                    FadeOut(low_box_highlight),
                )
