from manimlib.imports import *
from active_projects.eop.reusable_imports import *


class BrickRowScene(PiCreatureScene):


    def split_tallies(self, row, direction = DOWN):
        # Split all tally symbols at once and move the copies
        # either horizontally on top of the brick row
        # or diagonally into the bricks

        self.tallies_copy = self.tallies.copy()
        self.add_foreground_mobject(self.tallies_copy)

        tally_targets_left = [
            rect.get_center() + 0.25 * rect.get_width() * LEFT 
            for rect in row.rects
        ]

        tally_targets_right = [
            rect.get_center() + 0.25 * rect.get_width() * RIGHT 
            for rect in row.rects
        ]

        if np.all(direction == LEFT) or np.all(direction == RIGHT):

            tally_y_pos = self.tallies[0].anchor[1]
            for target in tally_targets_left:
                target[1] = tally_y_pos
            for target in tally_targets_right:
                target[1] = tally_y_pos

        for (i, tally) in enumerate(self.tallies):

            target_left = tally_targets_left[i]
            new_tally_left = TallyStack(tally.nb_heads + 1, tally.nb_tails)
            new_tally_left.move_anchor_to(target_left)
            v = target_left - tally.anchor
            
            self.play(
                tally.move_anchor_to, target_left,
            )
            tally.anchor = target_left
            self.play(Transform(tally, new_tally_left))
            
            tally_copy = self.tallies_copy[i]

            target_right = tally_targets_right[i]
            new_tally_right = TallyStack(tally.nb_heads, tally.nb_tails + 1)
            new_tally_right.move_anchor_to(target_right)
            v = target_right - tally_copy.anchor
            
            self.play(tally_copy.move_anchor_to, target_right)
            tally_copy.anchor = target_right
            self.play(Transform(tally_copy, new_tally_right))

            tally_copy.nb_heads = new_tally_right.nb_heads
            tally_copy.nb_tails = new_tally_right.nb_tails
            tally.nb_heads = new_tally_left.nb_heads
            tally.nb_tails = new_tally_left.nb_tails




    def tally_split_animations(self, row, direction = DOWN):
        # Just creates the animations and returns them
        # Execution can be timed afterwards
        # Returns two lists: first all those going left, then those to the right

        self.tallies_copy = self.tallies.copy()
        self.add_foreground_mobject(self.tallies_copy)

        tally_targets_left = [
            rect.get_center() + 0.25 * rect.get_width() * LEFT 
            for rect in row.rects
        ]

        tally_targets_right = [
            rect.get_center() + 0.25 * rect.get_width() * RIGHT 
            for rect in row.rects
        ]

        if np.all(direction == LEFT) or np.all(direction == RIGHT):

            tally_y_pos = self.tallies[0].anchor[1]
            for target in tally_targets_left:
                target[1] = tally_y_pos
            for target in tally_targets_right:
                target[1] = tally_y_pos


        anims1 = []

        for (i, tally) in enumerate(self.tallies):

            new_tally_left = TallyStack(tally.nb_heads + 1, tally.nb_tails)
            target_left = tally_targets_left[i]
            new_tally_left.move_to(target_left)

            anims1.append(Transform(tally, new_tally_left))
            
            tally.anchor = target_left
            tally.nb_heads = new_tally_left.nb_heads
            tally.nb_tails = new_tally_left.nb_tails
            

        anims2 = []

        for (i, tally) in enumerate(self.tallies_copy):

            new_tally_right = TallyStack(tally.nb_heads, tally.nb_tails + 1)
            target_right = tally_targets_right[i]
            new_tally_right.move_to(target_right)
            
            anims2.append(Transform(tally, new_tally_right))

            tally.anchor = target_right
            tally.nb_heads = new_tally_right.nb_heads
            tally.nb_tails = new_tally_right.nb_tails

        return anims1, anims2



    def split_tallies_at_once(self, row, direction = DOWN):
        anims1, anims2 = self.tally_split_animations(row, direction = direction)
        self.play(*(anims1 + anims2))

    def split_tallies_in_two_steps(self, row, direction = DOWN):
        # First all those to the left, then those to the right
        anims1, anims2 = self.tally_split_animations(row, direction = direction)
        self.play(*anims1)
        self.wait(0.3)
        self.play(*anims2)




    def merge_rects_by_subdiv(self, row):

        half_merged_row = row.copy()
        half_merged_row.subdiv_level += 1
        half_merged_row.generate_points()
        half_merged_row.move_to(row)

        self.play(FadeIn(half_merged_row))
        self.remove(row)
        return half_merged_row




    def merge_tallies(self, row, target_pos = UP):
        
        r = row.subdiv_level
        
        if np.all(target_pos == DOWN):
            tally_targets = [
                rect.get_center()
                for rect in row.get_rects_for_level(r)
            ]
        elif np.all(target_pos == UP):
            y_pos = row.get_center()[1] + 1.2 * 0.5 * row.get_height()
            for target in tally_targets:
                target[1] = y_pos
        else:
            raise Exception("Invalid target position (either UP or DOWN)")

        anims = []
        for (tally, target) in zip(self.tallies[1:], tally_targets[1:-1]):
            anims.append(tally.move_anchor_to)
            anims.append(target)

        for (tally, target) in zip(self.tallies_copy[:-1], tally_targets[1:-1]):
            anims.append(tally.move_anchor_to)
            anims.append(target)

        self.play(*anims)
        # update anchors
        for (tally, target) in zip(self.tallies[1:], tally_targets[1:-1]):
            tally.anchor = target
        for (tally, target) in zip(self.tallies_copy[:-1], tally_targets[1:-1]):
            tally.anchor = target

        self.remove(self.tallies_copy)
        self.tallies.add(self.tallies_copy[-1])


    def merge_rects_by_coloring(self, row):

        merged_row = row.copy()
        merged_row.coloring_level += 1
        merged_row.generate_points()
        merged_row.move_to(row)

        self.play(FadeIn(merged_row))
        self.remove(row)
        return merged_row



    def move_tallies_on_top(self, row):
        self.play(
            self.tallies.shift, 1.2 * 0.5 * row.height * UP
        )
        for tally in self.tallies:
            tally.anchor += 1.2 * 0.5 * row.height * UP

    def create_pi_creature(self):
        randy = CoinFlippingPiCreature(color = MAROON_E)
        return randy





        

    def construct(self):
        self.force_skipping()
        
        randy = self.get_primary_pi_creature()
        randy = randy.scale(0.5).move_to(3*DOWN + 6*LEFT)
        #self.add(randy)
        self.row = BrickRow(0, height = 2, width = 10)
        self.wait()

        self.play(FadeIn(self.row))

        self.wait()


        # move in all kinds of sequences
        coin_seqs = VGroup()
        for i in range(20):
            n = np.random.randint(1,10)
            seq = [np.random.choice(["H", "T"]) for j in range(n)]
            coin_seq = CoinSequence(seq).scale(1.5)
            loc = np.random.uniform(low = -10, high = 10) * RIGHT
            loc += np.random.uniform(low = -6, high = 6) * UP
            coin_seq.move_to(loc)
            
            coin_seq.target = coin_seq.copy().scale(0.3).move_to(0.4 * loc)
            coin_seq.target.fade(1)
            coin_seqs.add(coin_seq)

        self.play(
            LaggedStartMap(
                Succession, coin_seqs, lambda m: (FadeIn(m, run_time = 0.1), MoveToTarget(m)),
                run_time = 5,
                lag_ratio = 0.5
            )
        )
        
        # # # # # # # #
        # FIRST  FLIP #
        # # # # # # # #


        self.play(FlipCoin(randy))

        self.play(SplitRectsInBrickWall(self.row))
        self.row = self.merge_rects_by_subdiv(self.row)
        self.row = self.merge_rects_by_coloring(self.row)
        #
        # put tallies on top

        single_flip_labels = VGroup(UprightHeads(), UprightTails())
        for (label, rect) in zip(single_flip_labels, self.row.rects):
            label.next_to(rect, UP)
            self.play(FadeIn(label))
            self.wait()

        self.wait()


        # # # # # # # #
        # SECOND FLIP #
        # # # # # # # #

        self.play(FlipCoin(randy))
        self.wait()

        self.play(
            SplitRectsInBrickWall(self.row)
        )
        self.wait()


        # split sequences
        single_flip_labels_copy = single_flip_labels.copy()
        self.add(single_flip_labels_copy)

        
        v = self.row.get_outcome_centers_for_level(2)[0] - single_flip_labels[0].get_center()
        self.play(
            single_flip_labels.shift, v
        )
        new_heads = VGroup(UprightHeads(), UprightHeads())
        for i in range(2):
            new_heads[i].move_to(single_flip_labels[i])
            new_heads[i].shift(COIN_SEQUENCE_SPACING * DOWN)
        self.play(FadeIn(new_heads))

        v = self.row.get_outcome_centers_for_level(2)[-1] - single_flip_labels_copy[-1].get_center()
        self.play(
            single_flip_labels_copy.shift, v
        )
        new_tails = VGroup(UprightTails(), UprightTails())
        for i in range(2):
            new_tails[i].move_to(single_flip_labels_copy[i])
            new_tails[i].shift(COIN_SEQUENCE_SPACING * DOWN)
        self.play(FadeIn(new_tails))

        self.add_foreground_mobject(single_flip_labels)
        self.add_foreground_mobject(new_heads)
        self.add_foreground_mobject(single_flip_labels_copy)
        self.add_foreground_mobject(new_tails)

        # get individual outcomes
        outcomes = self.row.get_outcome_rects_for_level(2, with_labels = False,
            inset = True)
        grouped_outcomes = VGroup(outcomes[0], outcomes[1:3], outcomes[3])

        decimal_tallies = VGroup()
        # introduce notion of tallies
        rects = self.row.get_rects_for_level(2)

        rect = rects[0]
        tally = DecimalTally(2,0)
        tally.next_to(rect, UP)
        decimal_tallies.add(tally)
        self.play(
            FadeIn(tally),
            FadeIn(grouped_outcomes[0])
        )
        self.wait()

        rect = rects[1]
        tally = DecimalTally(1,1)
        tally.next_to(rect, UP)
        decimal_tallies.add(tally)
        self.play(
            FadeIn(tally),
            FadeOut(grouped_outcomes[0]),
            FadeIn(grouped_outcomes[1])
        )
        self.wait()

        rect = rects[2]
        tally = DecimalTally(0,2)
        tally.next_to(rect, UP)
        decimal_tallies.add(tally)
        self.play(
            FadeIn(tally),
            FadeOut(grouped_outcomes[1]),
            FadeIn(grouped_outcomes[2])
        )
        self.wait()

        self.play(
            FadeOut(grouped_outcomes[2])
        )
        self.wait()

        self.wait()
        self.play(
            FadeOut(single_flip_labels),
            FadeOut(new_heads),
            FadeOut(single_flip_labels_copy),
            FadeOut(new_tails)
        )
        self.wait()

        self.tallies = VGroup()
        for (i, rect) in enumerate(self.row.get_rects_for_level(2)):
            tally = TallyStack(2-i, i, show_decimals = False)
            tally.move_to(rect)
            self.tallies.add(tally)


        self.play(FadeIn(self.tallies))
        self.wait()


        anims = []
        for (decimal_tally, tally_stack) in zip(decimal_tallies, self.tallies):
            anims.append(ApplyFunction(
                tally_stack.position_decimal_tally, decimal_tally
            ))
        
        self.play(*anims)
        self.wait()


        # replace the original decimal tallies with
        # the ones that belong to the TallyStacks
        for (decimal_tally, tally_stack) in zip(decimal_tallies, self.tallies):
            self.remove(decimal_tally)
            tally_stack.position_decimal_tally(tally_stack.decimal_tally)
            tally_stack.add(tally_stack.decimal_tally)
        
        self.add_foreground_mobject(self.tallies)
        self.row = self.merge_rects_by_subdiv(self.row)
        self.wait()
        self.row = self.merge_rects_by_coloring(self.row)
        self.wait()
        

        # # # # # # # # # # # # #
        # CALLBACK TO SEQUENCES #
        # # # # # # # # # # # # #

        outcomes = self.row.get_outcome_rects_for_level(2, with_labels = True,
            inset = True)
        subdivs = self.row.get_sequence_subdivs_for_level(2)
        self.play(
            FadeIn(outcomes),
            FadeIn(subdivs),
            FadeOut(self.tallies)
        )

        self.wait()

        rect_to_dice = self.row.get_outcome_rects_for_level(2, with_labels = False,
            inset = False)[1]
        N = 10
        dice_width = rect_to_dice.get_width()/N
        dice_height = rect_to_dice.get_height()/N
        prototype_dice = Rectangle(
            width = dice_width,
            height = dice_height,
            stroke_width = 2,
            stroke_color = WHITE,
            fill_color = WHITE,
            fill_opacity = 0
        )
        prototype_dice.align_to(rect_to_dice, direction = UP)
        prototype_dice.align_to(rect_to_dice, direction = LEFT)
        all_dice = VGroup()
        for i in range(N):
            for j in range(N):
                dice_copy = prototype_dice.copy()
                dice_copy.shift(j * dice_width * RIGHT + i * dice_height * DOWN)
                all_dice.add(dice_copy)

        self.play(
            LaggedStartMap(FadeIn, all_dice),
            FadeOut(outcomes[1])
        )
        self.wait()

        table = Ellipse(width = 1.5, height = 1)
        table.set_fill(color = GREEN_E, opacity = 1)
        table.next_to(rect_to_dice, UP)
        self.add(table)
        coin1 = UprightHeads(radius = 0.1)
        coin2 = UprightTails(radius = 0.1)

        def get_random_point_in_ellipse(ellipse):
            width = ellipse.get_width()
            height = ellipse.get_height()
            x = y = 1
            while x**2 + y**2 > 0.9:
                x = np.random.uniform(-1,1)
                y = np.random.uniform(-1,1)            
            x *= width/2
            y *= height/2
            return ellipse.get_center() + x * RIGHT + y * UP


        for dice in all_dice:
            p1 = get_random_point_in_ellipse(table)
            p2 = get_random_point_in_ellipse(table)
            coin1.move_to(p1)
            coin2.move_to(p2)
            self.add(coin1, coin2)
            self.play(
                ApplyMethod(dice.set_fill, {"opacity" : 0.5},
                    rate_func = there_and_back,
                    run_time = 0.05)
            )

        self.wait()

        self.play(
            FadeOut(outcomes),
            FadeOut(subdivs),
            FadeOut(all_dice),
            FadeOut(table),
            FadeOut(coin1),
            FadeOut(coin2),
            FadeIn(self.tallies)
        )

        self.wait()

        # # # # # # # #
        # THIRD  FLIP #
        # # # # # # # #

        # move row up, leave a copy without tallies below
        new_row = self.row.copy()
        self.clear()
        self.add(randy, self.row, self.tallies)
        self.bring_to_back(new_row)
        self.play(
            self.row.shift, 2.5 * UP,
            self.tallies.shift, 2.5 * UP,
        )

        old_row = self.row
        self.row = new_row

        self.play(FlipCoin(randy))

        self.wait()

        self.play(
            SplitRectsInBrickWall(self.row)
        )
        self.wait()

        self.split_tallies_in_two_steps(self.row)
        self.wait()

        self.add_foreground_mobject(self.tallies)
        self.add_foreground_mobject(self.tallies_copy)


        

        self.remove(new_row)
        new_row = self.row



        self.clear()
        self.add(randy, self.row, old_row)
        self.add_foreground_mobject(self.tallies)
        self.add_foreground_mobject(self.tallies_copy)
        

        self.play(
            self.row.fade, 0.7,
            old_row.fade, 0.7,
            FadeOut(self.tallies),
            FadeOut(self.tallies_copy),
        )

        
        # # # # # # # # # # # # # # # # #
        # SHOW SPLITTING  WITH OUTCOMES #
        # # # # # # # # # # # # # # # # #

        # # show individual outcomes
        # old_outcomes = old_row.get_outcome_rects_for_level(2, with_labels = True)
        # old_outcomes_copy = old_outcomes.copy()
        # new_outcomes = self.row.get_outcome_rects_for_level(3, with_labels = True)
        
        # self.play(
        #     FadeIn(old_outcomes[0]),
        #     FadeIn(old_outcomes_copy[0]),
        # )

        # self.wait()

        # self.play(
        #     Transform(old_outcomes_copy[0], new_outcomes[1])
        # )

        # self.wait()

        # self.play(
        #     FadeIn(old_outcomes[1:3]),
        #     FadeIn(old_outcomes_copy[1:3]),
        # )

        # self.wait()

        # self.play(
        #     Transform(old_outcomes_copy[1:3], new_outcomes[2:4])
        # )

        # self.wait()

        # self.row = self.merge_rects_by_subdiv(self.row)
        # self.wait()

        # self.play(
        #     FadeOut(old_row),
        #     FadeOut(old_outcomes[0:3]),
        #     FadeOut(new_outcomes[1:4]),
        #     self.row.fade,0,
        #     FadeIn(self.tallies[1]),
        #     FadeIn(self.tallies_copy[0]),
        # )

        # # rest of the new row
        # self.play(
        #     FadeIn(self.tallies[:1]),
        #     FadeIn(self.tallies[2:]),
        #     FadeIn(self.tallies_copy[1:])
        # )

        # self.wait()

        # self.merge_tallies(self.row, target_pos = DOWN)
        # self.add_foreground_mobject(self.tallies)
        # self.row = self.merge_rects_by_coloring(self.row)
        # self.wait()


        # # # # # # # # # # # # # # # #
        # SHOW SPLITTING WITH TALLIES #
        # # # # # # # # # # # # # # # #

        tally_left = TallyStack(2,0)
        tally_left.move_to(old_row.rects[0])
        tally_right = TallyStack(1,1)
        tally_right.move_to(old_row.rects[1])

        rect_left = old_row.rects[0].copy()
        rect_right = old_row.rects[1].copy()

        self.play(
            FadeIn(rect_left),
            FadeIn(rect_right),
            FadeIn(tally_left),
            FadeIn(tally_right)
        )

        rect_left.target = rect_left.copy()
        rect_left.target.stretch(0.5,0)
        left_target_pos = self.row.get_outcome_centers_for_level(3)[1]
        left_v = left_target_pos - rect_left.get_center()
        rect_left.target.move_to(left_target_pos)

        rect_right.target = rect_right.copy()
        rect_right.target.stretch(0.5,0)
        right_target_pos = 0.5 * (self.row.get_outcome_centers_for_level(3)[2] + self.row.get_outcome_centers_for_level(3)[3])
        right_v = right_target_pos - rect_right.get_center()
        rect_right.target.move_to(right_target_pos)

        self.play(
            MoveToTarget(rect_left),
            tally_left.move_to, left_target_pos
        )
        #tally_left.anchor += left_v
        
        self.wait()

        new_tally_left = TallyStack(2,1)
        #new_tally_left.move_anchor_to(tally_left.anchor)
        new_tally_left.move_to(tally_left)
        
        self.play(
            Transform(tally_left, new_tally_left)
        )

        self.play(
            MoveToTarget(rect_right),
            tally_right.move_to, right_target_pos
        )
        #tally_right.anchor += right_v
        
        self.wait()
        new_tally_right = TallyStack(2,1)
        #new_tally_right.move_anchor_to(tally_right.anchor)
        new_tally_right.move_to(tally_right)

        self.play(
            Transform(tally_right, new_tally_right)
        )

        self.wait()

        self.row = self.merge_rects_by_subdiv(self.row)
        self.wait()

        self.play(
            FadeOut(old_row),
            self.row.fade,0,
            FadeOut(new_tally_left),
            FadeOut(new_tally_right),
            FadeIn(self.tallies[1]),
            FadeIn(self.tallies_copy[0]),
        )

        # rest of the new row
        self.play(
            FadeIn(self.tallies[:1]),
            FadeIn(self.tallies[2:]),
            FadeIn(self.tallies_copy[1:])
        )

        self.wait()

        self.merge_tallies(self.row, target_pos = DOWN)
        self.add_foreground_mobject(self.tallies)
        self.row = self.merge_rects_by_coloring(self.row)
        self.wait()

        
        # show the 8 individual outcomes
        outcomes = self.row.get_outcome_rects_for_level(3,
            with_labels = True,
            inset = True)
        self.play(FadeOut(self.tallies))
        self.wait()
        self.play(LaggedStartMap(
            FadeIn, outcomes,
            #rate_func = there_and_back_with_pause,
            run_time = 5))
        self.wait()

        braces = VGroup(*[Brace(rect, UP) for rect in self.row.rects])
        counts = [choose(3, i) for i in range(4)]
        probs = VGroup(*[TexMobject("{" + str(k) + "\over 8}") for k in counts])
        for (brace, prob) in zip(braces, probs):
            prob.next_to(brace, UP)


        self.play(
            LaggedStartMap(ShowCreation, braces),
            LaggedStartMap(Write, probs)
        )
        self.wait()
        self.play(LaggedStartMap(
            FadeOut, outcomes,
            #rate_func = there_and_back_with_pause,
            run_time = 5),
        )
        self.play(
            FadeIn(self.tallies)
        )
        self.wait()

        self.play(
            FadeOut(braces),
            FadeOut(probs)
        )
        self.wait()
 

        # put visuals for other probability distribtuions here

        # back to three coin flips, show all 8 outcomes
        run_time = 5
        self.play(
            LaggedStartMap(FadeIn, outcomes,
                #rate_func = there_and_back_with_pause,
                run_time = run_time),
            FadeOut(self.tallies,
                run_time = run_time)
        )
        self.wait()
        self.play(
            LaggedStartMap(FadeOut, outcomes,
                #rate_func = there_and_back_with_pause,
                run_time = 5),
            FadeIn(self.tallies,
                run_time = run_time)
        )




        # # # # # # # #
        # FOURTH FLIP #
        # # # # # # # #



        
        previous_row = self.row.copy()
        self.add(previous_row)

        v = 1.25 * self.row.height * UP
        self.play(
            previous_row.shift, v,
            self.tallies.shift, v,
        )
        self.add_foreground_mobject(self.tallies)

        self.play(
            SplitRectsInBrickWall(self.row)
        )
        self.wait()

        self.row = self.merge_rects_by_subdiv(self.row)
        

        self.revert_to_original_skipping_status()

        self.wait()

        n = 3 # level to split
        k = 1 # tally to split

        # show individual outcomes
        outcomes = previous_row.get_outcome_rects_for_level(n,
            with_labels = False,
            inset = True
        )
        grouped_outcomes = VGroup()
        index = 0
        for i in range(n + 1):
            size = choose(n,i)
            grouped_outcomes.add(VGroup(outcomes[index:index + size]))
            index += size


        grouped_outcomes_copy = grouped_outcomes.copy()

        original_grouped_outcomes = grouped_outcomes.copy()
        # for later reference

        self.play(
            LaggedStartMap(FadeIn, grouped_outcomes),
            LaggedStartMap(FadeIn, grouped_outcomes_copy),
        )
        self.wait()

        # show how the outcomes in one tally split into two copies
        # going into the neighboring tallies

        #self.revert_to_original_skipping_status()

        target_outcomes = self.row.get_outcome_rects_for_level(n + 1,
            with_labels = False,
            inset = True
        )
        grouped_target_outcomes = VGroup()
        index = 0
        old_tally_sizes = [choose(n,i) for i in range(n + 1)]
        new_tally_sizes = [choose(n + 1,i) for i in range(n + 2)]
                
        for i in range(n + 2):
            size = new_tally_sizes[i]
            grouped_target_outcomes.add(VGroup(target_outcomes[index:index + size]))
            index += size

        old_tally_sizes.append(0) # makes the edge cases work properly
        
        # split all tallies
        for i in range(n + 1):
            self.play(
                Transform(grouped_outcomes[i][0],
                    grouped_target_outcomes[i][0][old_tally_sizes[i - 1]:]
                ),
                Transform(grouped_outcomes_copy[i][0],
                    grouped_target_outcomes[i + 1][0][:old_tally_sizes[i]]
                )
            )
        return
        
        self.wait()

        # fade in new tallies
        new_rects = self.row.get_rects_for_level(4)
        new_tallies = VGroup(*[
            TallyStack(n + 1 - i, i).move_to(rect) for (i, rect) in enumerate(new_rects)
        ])
        self.play(FadeIn(new_tallies))
        self.add_foreground_mobject(new_tallies[1])
        # remove outcomes and sizes except for one tally
        anims = []
        for i in range(n + 1):
            if i != k - 1:
                anims.append(FadeOut(grouped_outcomes_copy[i]))
            if i != k:
                anims.append(FadeOut(grouped_outcomes[i]))
                anims.append(FadeOut(new_tallies[i]))

        #anims.append(FadeOut(self.tallies[0]))
        #anims.append(FadeOut(self.tallies[2:]))
        anims.append(FadeOut(new_tallies[-1]))

        self.play(*anims)

        self.wait()

        self.play(
            Transform(grouped_outcomes_copy[k - 1], original_grouped_outcomes[k - 1])
        )

        self.play(
            Transform(grouped_outcomes[k], original_grouped_outcomes[k])
        )

        new_rects = self.row.get_rects_for_level(n + 1)

        self.play(
            Transform(grouped_outcomes[k][0],grouped_target_outcomes[k][0][old_tally_sizes[k - 1]:]),
            Transform(grouped_outcomes_copy[k - 1][0],grouped_target_outcomes[k][0][:old_tally_sizes[k - 1]]),
        )

        self.play(
            FadeOut(previous_row),
            FadeOut(self.tallies),
        )

        self.row = self.merge_rects_by_coloring(self.row)

        self.play(
            FadeIn(new_tallies[0]),
            FadeIn(new_tallies[2:]),
        )




        # # # # # # # # # #
        # EVEN MORE FLIPS #
        # # # # # # # # # #

        self.play(FadeOut(new_tallies))
        self.clear()
        self.row = BrickRow(3)
        self.add(randy, self.row)       
        

        for i in range(3):

            self.play(FlipCoin(randy))

            self.wait()

            previous_row = self.row.copy()

            self.play(previous_row.shift, 1.25 * self.row.height * UP)

            self.play(
                SplitRectsInBrickWall(self.row)
            )
            self.wait()
            self.row = self.merge_rects_by_subdiv(self.row)
            self.wait()
            self.row = self.merge_rects_by_coloring(self.row)
            self.wait()

            self.play(FadeOut(previous_row))






class ShowProbsInBrickRow3(BrickRowScene):

    def construct(self):

        randy = self.get_primary_pi_creature()
        randy = randy.scale(0.5).move_to(3*DOWN + 6*LEFT)
        #self.add(randy)
        self.row = BrickRow(3, height = 2, width = 10)
        self.wait()

        self.add(self.row)

        tallies = VGroup()
        for (i, rect) in enumerate(self.row.get_rects_for_level(3)):
            tally = TallyStack(3-i, i, show_decimals = False)
            tally.move_to(rect)
            tallies.add(tally)

        self.add(tallies)
        self.wait(6)

        braces = VGroup(*[Brace(rect, UP) for rect in self.row.rects])
        counts = [choose(3, i) for i in range(4)]
        probs = VGroup(*[TexMobject("{" + str(k) + "\over 8}") for k in counts])
        for (brace, prob) in zip(braces, probs):
            prob.next_to(brace, UP)

        self.wait()
        self.play(
            LaggedStartMap(ShowCreation, braces, run_time = 3),
            LaggedStartMap(Write, probs, run_time = 3)
        )
        self.wait()

        self.play(FadeOut(braces),FadeOut(probs))




class ShowOutcomesInBrickRow4(BrickRowScene):

    def construct(self):

        randy = self.get_primary_pi_creature()
        randy = randy.scale(0.5).move_to(3*DOWN + 6*LEFT)
        #self.add(randy)
        self.row = BrickRow(3, height = 2, width = 10)
        
        previous_row = self.row.copy()
        v = 1.25 * self.row.height * UP
        self.play(
            previous_row.shift, v,
        )

        self.add(self.row)
        self.add(previous_row)

                


        self.wait()
        previous_outcomes = previous_row.get_outcome_rects_for_level(3,
            with_labels = True, inset = True)

        previous_outcomes_copy = previous_outcomes.copy()



        self.play(
            LaggedStartMap(FadeIn, previous_outcomes),
            LaggedStartMap(FadeIn, previous_outcomes_copy),
        )
        
        self.wait()

        new_outcomes = self.row.get_outcome_rects_for_level(4,
            with_labels = True, inset = True)
        # remove each last coin


        new_outcomes_left = VGroup(
            new_outcomes[0],
            new_outcomes[2],
            new_outcomes[3],
            new_outcomes[4],
            new_outcomes[8],
            new_outcomes[9],
            new_outcomes[10],
            new_outcomes[14]
        )
        new_outcomes_right = VGroup(
            new_outcomes[1],
            new_outcomes[5],
            new_outcomes[6],
            new_outcomes[7],
            new_outcomes[11],
            new_outcomes[12],
            new_outcomes[13],
            new_outcomes[15]
        )
        heads_labels = VGroup(*[outcome.label[-1] for outcome in new_outcomes_left])
        tails_labels = VGroup(*[outcome.label[-1] for outcome in new_outcomes_right])
        heads_labels.save_state()
        tails_labels.save_state()
        for outcome in new_outcomes:
            outcome.label[-1].fade(1)

        run_time = 0.5
        self.play(Transform(previous_outcomes[0], new_outcomes_left[0], run_time = run_time))
        self.play(Transform(previous_outcomes[1:4], new_outcomes_left[1:4], run_time = run_time))
        self.play(Transform(previous_outcomes[4:7], new_outcomes_left[4:7], run_time = run_time))
        self.play(Transform(previous_outcomes[7], new_outcomes_left[7], run_time = run_time))


        self.play(heads_labels.restore)


        self.play(Transform(previous_outcomes_copy[0], new_outcomes_right[0], run_time = run_time))
        self.play(Transform(previous_outcomes_copy[1:4], new_outcomes_right[1:4], run_time = run_time))
        self.play(Transform(previous_outcomes_copy[4:7], new_outcomes_right[4:7], run_time = run_time))
        self.play(Transform(previous_outcomes_copy[7], new_outcomes_right[7], run_time = run_time))


        self.play(tails_labels.restore)


        self.wait()

        anims = [FadeOut(previous_outcomes),FadeOut(previous_outcomes_copy)]

        for outcome in new_outcomes_left:
            anims.append(FadeOut(outcome.label[-1]))
        for outcome in new_outcomes_right:
            anims.append(FadeOut(outcome.label[-1]))

        self.play(*anims)

        self.wait()





class SplitTalliesIntoBrickRow4(BrickRowScene):

    def construct(self):

        randy = self.get_primary_pi_creature()
        randy = randy.scale(0.5).move_to(3*DOWN + 6*LEFT)
        #self.add(randy)
        self.row = BrickRow(3, height = 2, width = 10)
        
        previous_row = self.row.copy()
        v = 1.25 * self.row.height * UP
        self.play(
            previous_row.shift, v,
        )

        tallies = VGroup()
        for (i, rect) in enumerate(previous_row.get_rects_for_level(3)):
            tally = TallyStack(3-i, i, show_decimals = True)
            tally.move_to(rect)
            tallies.add(tally)

        moving_tallies_left = tallies.copy()
        moving_tallies_right = tallies.copy()

        self.add(self.row, previous_row)
        self.add_foreground_mobject(tallies)
        self.add_foreground_mobject(moving_tallies_left)
        self.add_foreground_mobject(moving_tallies_right)


        self.play(SplitRectsInBrickWall(self.row))

        anims = []
        for (tally, rect) in zip(moving_tallies_left, previous_row.rects):
            anims.append(tally.move_to)
            anims.append(rect.get_center() + rect.get_width() * 0.25 * LEFT)

        self.play(*anims)

        new_tallies_left = VGroup()
        for (i, tally) in enumerate(moving_tallies_left):
            new_tally = TallyStack(4-i,i, with_labels = True)
            new_tally.move_to(tally)
            new_tallies_left.add(new_tally)

        self.play(Transform(moving_tallies_left, new_tallies_left))

        anims = []
        for (tally, rect) in zip(moving_tallies_right, previous_row.rects):
            anims.append(tally.move_to)
            anims.append(rect.get_center() + rect.get_width() * 0.25 * RIGHT)

        self.play(*anims)

        new_tallies_right = VGroup()
        for (i, tally) in enumerate(moving_tallies_right):
            new_tally = TallyStack(3-i,i+1, with_labels = True)
            new_tally.move_to(tally)
            new_tallies_right.add(new_tally)

        self.play(Transform(moving_tallies_right, new_tallies_right))


        hypothetical_new_row = BrickRow(4, height = 2, width = 10)
        anims = []
        for (tally, rect) in zip(moving_tallies_left[1:], hypothetical_new_row.rects[1:-1]):
            anims.append(tally.move_to)
            anims.append(rect)
        for (tally, rect) in zip(moving_tallies_right[:-1], hypothetical_new_row.rects[1:-1]):
            anims.append(tally.move_to)
            anims.append(rect)
        self.play(*anims)
        self.wait()
        self.row = self.merge_rects_by_subdiv(self.row)
        self.wait()
        self.row = self.merge_rects_by_coloring(self.row)
        self.wait()





