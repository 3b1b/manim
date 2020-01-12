from manimlib.imports import *
       

class IllustrateAreaModelBayes(Scene):

    def construct(self):

        color_A = YELLOW
        color_not_A = YELLOW_E
        color_B = MAROON
        color_not_B = MAROON_E
        opacity_B = 0.7


        # show independent events

        sample_space_width = sample_space_height = 3
        p_of_A = 0.7
        p_of_not_A = 1 - p_of_A
        p_of_B = 0.8
        p_of_not_B = 1 - p_of_B


        rect_A = Rectangle(
            width = p_of_A * sample_space_width,
            height = 1 * sample_space_height,
            stroke_width = 0,
            fill_color = color_A,
            fill_opacity = 1.0
        ).move_to(3 * RIGHT + 1.5 * UP)

        rect_not_A = Rectangle(
            width = p_of_not_A * sample_space_width,
            height = 1 * sample_space_height,
            stroke_width = 0,
            fill_color = color_not_A,
            fill_opacity = 1.0
        ).next_to(rect_A, RIGHT, buff = 0)

        brace_A = Brace(rect_A, DOWN)
        label_A = TexMobject("P(A)").next_to(brace_A, DOWN).scale(0.7)
        brace_not_A = Brace(rect_not_A, DOWN)
        label_not_A = TexMobject("P(\\text{not }A)").next_to(brace_not_A, DOWN).scale(0.7)

        # self.play(
        #     LaggedStartMap(FadeIn, VGroup(rect_A, rect_not_A))
        # )
        # self.play(
        #     ShowCreation(brace_A),
        #     Write(label_A),
        # )



        rect_B = Rectangle(
            width = 1 * sample_space_width,
            height = p_of_B * sample_space_height,
            stroke_width = 0,
            fill_color = color_B,
            fill_opacity = opacity_B
        )
        rect_not_B = Rectangle(
            width = 1 * sample_space_width,
            height = p_of_not_B * sample_space_height,
            stroke_width = 0,
            fill_color = color_not_B,
            fill_opacity = opacity_B
        ).next_to(rect_B, UP, buff = 0)

        VGroup(rect_B, rect_not_B).move_to(VGroup(rect_A, rect_not_A))

        brace_B = Brace(rect_B, LEFT)
        label_B = TexMobject("P(B)").next_to(brace_B, LEFT).scale(0.7)
        brace_not_B = Brace(rect_not_B, LEFT)
        label_not_B = TexMobject("P(\\text{not }B)").next_to(brace_not_B, LEFT).scale(0.7)

        # self.play(
        #     LaggedStartMap(FadeIn, VGroup(rect_B, rect_not_B))
        # )
        # self.play(
        #     ShowCreation(brace_B),
        #     Write(label_B),
        # )

        rect_A_and_B = Rectangle(
            width = p_of_A * sample_space_width,
            height = p_of_B * sample_space_height,
            stroke_width = 3,
            fill_opacity = 0.0
        ).align_to(rect_A, DOWN).align_to(rect_A,LEFT)
        label_A_and_B = TexMobject("P(A\\text{ and }B)").scale(0.7)
        label_A_and_B.move_to(rect_A_and_B)

        # self.play(
        #     ShowCreation(rect_A_and_B)
        # )

        indep_formula = TexMobject("P(A\\text{ and }B)", "=", "P(A)", "\cdot", "P(B)")
        indep_formula = indep_formula.scale(0.7)
        label_p_of_b = indep_formula.get_part_by_tex("P(B)")

        label_A_and_B_copy = label_A_and_B.copy()
        label_A_copy = label_A.copy()
        label_B_copy = label_B.copy()
        # self.add(label_A_and_B_copy, label_A_copy, label_B_copy)

        # self.play(Transform(label_A_and_B_copy, indep_formula[0]))
        # self.play(FadeIn(indep_formula[1]))
        # self.play(Transform(label_A_copy, indep_formula[2]))
        # self.play(FadeIn(indep_formula[3]))
        # self.play(Transform(label_B_copy, indep_formula[4]))

        #self.wait()

        label_A_and_B_copy = indep_formula[0]
        label_A_copy = indep_formula[2]
        label_B_copy = indep_formula[4]

        # show conditional prob

        rect_A_and_B.set_fill(color = RED, opacity = 0.5)
        rect_A_and_not_B = Rectangle(
            width = p_of_A * sample_space_width,
            height = p_of_not_B * sample_space_height,
            stroke_width = 0,
            fill_color = color_not_B,
            fill_opacity = opacity_B
        ).next_to(rect_A_and_B, UP, buff = 0)
        
        rect_not_A_and_B = Rectangle(
            width = p_of_not_A * sample_space_width,
            height = p_of_B * sample_space_height,
            stroke_width = 0,
            fill_color = color_B,
            fill_opacity = opacity_B
        ).next_to(rect_A_and_B, RIGHT, buff = 0)

        rect_not_A_and_not_B = Rectangle(
            width = p_of_not_A * sample_space_width,
            height = p_of_not_B * sample_space_height,
            stroke_width = 0,
            fill_color = color_not_B,
            fill_opacity = opacity_B
        ).next_to(rect_not_A_and_B, UP, buff = 0)


        indep_formula.next_to(rect_not_A, LEFT, buff = 5)
        #indep_formula.shift(UP)

        self.play(Write(indep_formula))

        self.play(
            FadeIn(VGroup(
                rect_A, rect_not_A, brace_A, label_A, brace_B, label_B,
                rect_A_and_not_B, rect_not_A_and_B, rect_not_A_and_not_B,
                rect_A_and_B,
                label_A_and_B,
            ))
        )

        self.wait()


        p_of_B_knowing_A = 0.6
        rect_A_and_B.target = Rectangle(
            width = p_of_A * sample_space_width,
            height = p_of_B_knowing_A * sample_space_height,
            stroke_width = 3,
            fill_color = color_B,
            fill_opacity = opacity_B
        ).align_to(rect_A_and_B, DOWN).align_to(rect_A_and_B, LEFT)

        rect_A_and_not_B.target = Rectangle(
            width = p_of_A * sample_space_width,
            height = (1 - p_of_B_knowing_A) * sample_space_height,
            stroke_width = 0,
            fill_color = color_not_B,
            fill_opacity = opacity_B
        ).next_to(rect_A_and_B.target, UP, buff = 0)

        brace_B.target = Brace(rect_A_and_B.target, LEFT)
        label_B.target = TexMobject("P(B\mid A)").scale(0.7).next_to(brace_B.target, LEFT)


        self.play(
            MoveToTarget(rect_A_and_B),
            MoveToTarget(rect_A_and_not_B),
            MoveToTarget(brace_B),
            MoveToTarget(label_B),
            label_A_and_B.move_to,rect_A_and_B.target
        )
        label_B_knowing_A = label_B

        #self.play(FadeOut(label_B_copy))
        self.remove(indep_formula.get_part_by_tex("P(B)"))
        indep_formula.remove(indep_formula.get_part_by_tex("P(B)"))
        label_B_knowing_A_copy = label_B_knowing_A.copy()
        self.add(label_B_knowing_A_copy)

        self.play(
            label_B_knowing_A_copy.next_to, indep_formula.get_part_by_tex("\cdot"), RIGHT,
        )

        # solve formula for P(B|A)

        rearranged_formula = TexMobject("P(B\mid A)", "=", "{P(A\\text{ and }B) \over P(A)}")
        rearranged_formula.move_to(indep_formula)

        self.wait()


        self.play(
            # in some places get_part_by_tex does not find the correct part
            # so I picked out fitting indices
            label_B_knowing_A_copy.move_to, rearranged_formula.get_part_by_tex("P(B\mid A)"),
            label_A_copy.move_to, rearranged_formula[-1][10],
            label_A_and_B_copy.move_to, rearranged_formula[-1][3],
            indep_formula.get_part_by_tex("=").move_to, rearranged_formula.get_part_by_tex("="),
            Transform(indep_formula.get_part_by_tex("\cdot"), rearranged_formula[2][8]),
        )

        rect = SurroundingRectangle(rearranged_formula, buff = 0.5 * MED_LARGE_BUFF)
        self.play(ShowCreation(rect))


        self.wait()


