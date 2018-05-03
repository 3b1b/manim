from big_ol_pile_of_manim_imports import *
from active_projects.eop.reusable_imports import *


class BrickRowScene(PiCreatureScene):


    def split_tallies(self, direction = DOWN):
        # Split all tally symbols at once and move the copies
        # either horizontally on top of the brick row
        # or diagonally into the bricks

        self.tallies_copy = self.tallies.copy()
        self.add_foreground_mobject(self.tallies_copy)

        tally_targets_left = [
            rect.get_center() + 0.25 * rect.get_width() * LEFT 
            for rect in self.row.rects
        ]

        tally_targets_right = [
            rect.get_center() + 0.25 * rect.get_width() * RIGHT 
            for rect in self.row.rects
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




    def tally_split_animations(self, direction = DOWN):
        # Just creates the animations and returns them
        # Execution can be timed afterwards
        # Returns two lists: first all those going left, then those to the right

        self.tallies_copy = self.tallies.copy()
        self.add_foreground_mobject(self.tallies_copy)

        tally_targets_left = [
            rect.get_center() + 0.25 * rect.get_width() * LEFT 
            for rect in self.row.rects
        ]

        tally_targets_right = [
            rect.get_center() + 0.25 * rect.get_width() * RIGHT 
            for rect in self.row.rects
        ]

        if np.all(direction == LEFT) or np.all(direction == RIGHT):

            tally_y_pos = self.tallies[0].anchor[1]
            for target in tally_targets_left:
                target[1] = tally_y_pos
            for target in tally_targets_right:
                target[1] = tally_y_pos


        anims1 = []

        for (i, tally) in enumerate(self.tallies):

            target_left = tally_targets_left[i]
            v = target_left - tally.anchor
            
            anims1.append(tally.move_anchor_to)
            anims1.append(target_left)
            
            tally.anchor = target_left
            
            tally_copy = self.tallies_copy[i]

            target_right = tally_targets_right[i]
            v = target_right - tally_copy.anchor
            
            anims1.append(tally_copy.move_anchor_to)
            anims1.append(target_right)
            
            tally_copy.anchor = target_right

        anims2 = []

        for (i, tally) in enumerate(self.tallies):

            new_tally_left = TallyStack(tally.nb_heads + 1, tally.nb_tails)
            new_tally_left.move_anchor_to(tally.anchor)
            anims2.append(Transform(tally, new_tally_left))
            
            tally_copy = self.tallies_copy[i]

            new_tally_right = TallyStack(tally.nb_heads, tally.nb_tails + 1)
            new_tally_right.move_anchor_to(tally_copy.anchor)
            anims2.append(Transform(tally_copy, new_tally_right))

            tally_copy.nb_heads = new_tally_right.nb_heads
            tally_copy.nb_tails = new_tally_right.nb_tails
            tally.nb_heads = new_tally_left.nb_heads
            tally.nb_tails = new_tally_left.nb_tails

        return anims1, anims2


    def split_tallies_at_once(self, direction = DOWN):
        anims1, anims2 = self.tally_split_animations(direction = direction)
        self.play(*(anims1 + anims2))

    def split_tallies_in_two_steps(self, direction = DOWN):
        # First all thiode to the left, then those to the right
        anims1, anims2 = self.tally_split_animations(direction = direction)
        self.play(*anims1)
        self.wait(0.3)
        self.play(*anims2)




    def merge_rects_by_subdiv(self):

        half_merged_row = self.row.copy()
        half_merged_row.subdiv_level += 1
        half_merged_row.generate_points()
        half_merged_row.move_to(self.row)
        self.play(FadeIn(half_merged_row))
        self.row = half_merged_row

    def merge_tallies(self, direction = UP):

        r = self.row.subdiv_level
        tally_targets = [
            rect.get_center()
            for rect in self.row.get_rects_for_level(r)
        ]

        if np.all(direction == LEFT) or np.all(direction == RIGHT):
            y_pos = self.row.get_center()[1] + 1.2 * 0.5 * self.row.get_height()
            for target in tally_targets:
                target[1] = y_pos

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


    def merge_rects_by_coloring(self):

        merged_row = self.row.copy()
        merged_row.coloring_level += 1
        merged_row.generate_points()
        merged_row.move_to(self.row)

        self.play(FadeIn(merged_row))
        self.row = merged_row



    def move_tallies_on_top(self):
        self.play(
            self.tallies.shift, 1.2 * 0.5 * self.row.height * UP
        )
        for tally in self.tallies:
            tally.anchor += 1.2 * 0.5 * self.row.height * UP

    def create_pi_creature(self):
        randy = CoinFlippingPiCreature(color = MAROON_E)
        return randy

    def construct(self):

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
            LaggedStart(
                Succession, coin_seqs, lambda m: (FadeIn(m, run_time = 0.1), MoveToTarget(m)),
                run_time = 5,
                lag_ratio = 0.5
            )
        )
        
        self.play(FlipCoin(randy) )

        self.play(SplitRectsInBrickWall(self.row))
        self.merge_rects_by_subdiv()
        self.merge_rects_by_coloring()
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


        decimal_tallies = VGroup()
        # introduce notion of tallies
        for (i, rect) in enumerate(self.row.get_rects_for_level(2)):
            tally = DecimalTally(2-i, i)
            tally.next_to(rect, UP)
            decimal_tallies.add(tally)
            self.play(FadeIn(tally))
            self.wait()

        self.add_foreground_mobject(single_flip_labels)
        self.add_foreground_mobject(new_heads)
        self.add_foreground_mobject(single_flip_labels_copy)
        self.add_foreground_mobject(new_tails)

        # show individual outcomes
        outcomes = self.row.get_outcome_rects_for_level(2, with_labels = False)


        self.play(
            LaggedStart(FadeIn, outcomes)
        )
        self.wait()
        self.play(
            LaggedStart(FadeOut, outcomes),
        )
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
        self.merge_rects_by_subdiv()
        self.wait()
        self.merge_rects_by_coloring()
        self.wait()
        

        # # # # # # # # # # # # #
        # CALLBACK TO SEQUENCES #
        # # # # # # # # # # # # #

        outcomes = self.row.get_outcome_rects_for_level(2, with_labels = True)
        subdivs = self.row.get_sequence_subdivs_for_level(2)
        self.play(
            FadeIn(outcomes),
            FadeIn(subdivs),
            FadeOut(self.tallies)
        )

        self.wait()

        rect_to_dice = outcomes[1]
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
            LaggedStart(FadeIn, all_dice),
            FadeOut(rect_to_dice.label)
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

        # move row up, leace a copy without tallies below
        new_row = self.row.copy()
        self.bring_to_back(new_row)
        self.play(
            self.row.shift,2.5 * UP,
            self.tallies.shift,2.5 * UP,
        )

        self.play(FlipCoin(randy))

        self.wait()
        return

        self.play(
            SplitRectsInBrickWall(self.row)
        )
        self.wait()

        self.split_tallies_in_two_steps()
        self.wait()
        self.merge_rects_by_subdiv()
        self.wait()
        self.merge_tallies()
        self.merge_rects_by_coloring()
        self.wait()
        self.move_tallies_on_top()



        # show individual outcomes
        outcomes = self.row.get_outcome_rects_for_level(3, with_labels = True)
        self.play(
            LaggedStart(FadeIn, outcomes)
        )
        self.wait()
        self.play(
            LaggedStart(FadeOut, outcomes)
        )


        # # # # # # # # # # # # # #
        # # FOURTH FLIP IN DETAIL #
        # # # # # # # # # # # # # #



        # removing the tallies (boy are they sticky)
        self.play(FadeOut(self.tallies))
        self.remove(self.tallies, self.tallies_copy)
        for tally in self.tallies:
            self.remove_foreground_mobject(tally)
            self.remove(tally)
        for tally in self.tallies_copy:
            self.remove_foreground_mobject(tally)
            self.remove(tally)

        # delete all the old crap hidden behind the row
        # before we can move it
        self.remove(*self.mobjects)
        self.add(randy) #,self.decimals,self.decimal_copies)


        previous_row = self.row.copy()
        self.add(previous_row)

        v = 1.25 * self.row.height * UP
        self.play(
            previous_row.shift, v,
            #self.decimals.shift, v,
            #self.decimal_copies.shift, v
        )

        self.add(self.row)
        self.bring_to_back(self.row)
        self.row.shift(v)

        w = 1.5 * self.row.height * DOWN
        self.play(
            self.row.shift, w,
            Animation(previous_row)
        )

        self.play(
            SplitRectsInBrickWall(self.row)
        )
        self.wait()

        self.merge_rects_by_subdiv()

        self.wait()

        n = 3 # level to split
        k = 1 # tally to split

        # show individual outcomes
        outcomes = previous_row.get_outcome_rects_for_level(n, with_labels = False)
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
            LaggedStart(FadeIn, grouped_outcomes),
            LaggedStart(FadeIn, grouped_outcomes_copy),
        )
        self.wait()

        # show how the outcomes in one tally split into two copies
        # going into the neighboring tallies

        #self.revert_to_original_skipping_status()

        target_outcomes = self.row.get_outcome_rects_for_level(n + 1, with_labels = False)
        grouped_target_outcomes = VGroup()
        index = 0
        old_tally_sizes = [choose(n,i) for i in range(n + 1)]
        new_tally_sizes = [choose(n + 1,i) for i in range(n + 2)]
        for i in range(n + 2):
            size = new_tally_sizes[i]
            grouped_target_outcomes.add(VGroup(target_outcomes[index:index + size]))
            index += size

        self.play(
            Transform(grouped_outcomes[k][0],grouped_target_outcomes[k][0][old_tally_sizes[k - 1]:])
        )

        self.play(
            Transform(grouped_outcomes_copy[k][0],grouped_target_outcomes[k + 1][0][:old_tally_sizes[k]])
        )

        old_tally_sizes.append(0) # makes the edge cases work properly

        # split the other tallies
        for i in range(k) + range(k + 1, n + 1):
            self.play(
                Transform(grouped_outcomes[i][0],
                    grouped_target_outcomes[i][0][old_tally_sizes[i - 1]:]
                ),
                Transform(grouped_outcomes_copy[i][0],
                    grouped_target_outcomes[i + 1][0][:old_tally_sizes[i]]
                )
            )

        
        self.wait()

        # remove outcomes and sizes except for one tally
        anims = []
        for i in range(n + 1):
            if i != k - 1:
                anims.append(FadeOut(grouped_outcomes_copy[i]))
            if i != k:
                anims.append(FadeOut(grouped_outcomes[i]))

        self.play(*anims)

        self.wait()

        self.play(
            Transform(grouped_outcomes_copy[k - 1], original_grouped_outcomes[k - 1])
        )
        self.play(
            Transform(grouped_outcomes[k], original_grouped_outcomes[k])
        )


        new_rects = self.row.get_rects_for_level(n + 1)

        #decimals_copy = self.decimals.copy()
        #decimals_copy2 = self.decimals.copy()

        self.play(
            Transform(grouped_outcomes[k][0],grouped_target_outcomes[k][0][old_tally_sizes[k - 1]:]),
            Transform(grouped_outcomes_copy[k - 1][0],grouped_target_outcomes[k][0][:old_tally_sizes[k]]),
            #decimals_copy[k - 1].move_to, new_rects[k],
            #decimals_copy2[k].move_to, new_rects[k],
        )


        # # # # # # # #
        # FIFTH  FLIP #
        # # # # # # # #

        # self.remove(
        #     grouped_outcomes,
        #     grouped_outcomes_copy,
        #     grouped_target_outcomes,
        #     target_outcomes,
        #     outcomes,
        #     previous_row,
        #     original_grouped_outcomes)
        self.clear()
        self.add(randy, self.row)
        #self.row.shift(0.5 * UP)        
        
        #return

        self.merge_rects_by_coloring()

        self.revert_to_original_skipping_status()

        for i in range(1):

            self.play(FlipCoin(randy))

            self.wait()

            self.play(
                SplitRectsInBrickWall(self.row)
            )
            self.wait()


            #self.split_tallies_at_once(direction = LEFT)
            self.wait()
            self.merge_rects_by_subdiv()
            self.wait()
            #self.merge_tallies(direction = LEFT)
            self.merge_rects_by_coloring()
            #self.merge_decimals()
            self.wait()

