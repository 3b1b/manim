from manimlib.imports import *
from old_projects.eola.chapter0 import UpcomingSeriesOfVidoes

import random


def plane_wave_homotopy(x, y, z, t):
    norm = get_norm([x, y])
    tau = interpolate(5, -5, t) + norm/FRAME_X_RADIUS
    alpha = sigmoid(tau)
    return [x, y + 0.5*np.sin(2*np.pi*alpha)-t*SMALL_BUFF/2, z]

class Physicist(PiCreature):
    CONFIG = {
        "color" : PINK,
    }

class ComputerScientist(PiCreature):
    CONFIG = {
        "color" : PURPLE_E,
        "flip_at_start" : True,
    }    

class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject(
            "``The introduction of numbers as \\\\ coordinates is an act of violence.''",
        )
        words.to_edge(UP)    
        for mob in words.submobjects[27:27+11]:
            mob.set_color(GREEN)
        author = TextMobject("-Hermann Weyl")
        author.set_color(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(FadeIn(words))
        self.wait(1)
        self.play(Write(author, run_time = 4))
        self.wait()


class DifferentConceptions(Scene):
    def construct(self):
        physy = Physicist()
        mathy = Mathematician(mode = "pondering")        
        compy = ComputerScientist()
        creatures = [physy, compy, mathy]
        physy.title = TextMobject("Physics student").to_corner(DOWN+LEFT)
        compy.title = TextMobject("CS student").to_corner(DOWN+RIGHT)
        mathy.title = TextMobject("Mathematician").to_edge(DOWN)
        names = VMobject(physy.title, mathy.title, compy.title)
        names.arrange(RIGHT, buff = 1)
        names.to_corner(DOWN+LEFT)
        for pi in creatures:
            pi.next_to(pi.title, UP)

        vector, symbol, coordinates = self.intro_vector()
        for pi in creatures:
            self.play(
                Write(pi.title),
                FadeIn(pi),
                run_time = 1
            )
        self.wait(2)
        self.remove(symbol, coordinates)
        self.physics_conception(creatures, vector)
        self.cs_conception(creatures)
        self.handle_mathy(creatures)

    def intro_vector(self):
        plane = NumberPlane()
        labels = VMobject(*plane.get_coordinate_labels())
        vector = Vector(RIGHT+2*UP, color = YELLOW)
        coordinates = vector_coordinate_label(vector)
        symbol = TexMobject("\\vec{\\textbf{v}}")
        symbol.shift(0.5*(RIGHT+UP))

        self.play(ShowCreation(
            plane, 
            lag_ratio=1,
            run_time = 3
        ))
        self.play(ShowCreation(
            vector,
        ))
        self.play(
            Write(labels),
            Write(coordinates),
            Write(symbol)
        )
        self.wait(2)
        self.play(
            FadeOut(plane),
            FadeOut(labels),
            ApplyMethod(vector.shift, 4*LEFT+UP),
            ApplyMethod(coordinates.shift, 2.5*RIGHT+0.5*DOWN),
            ApplyMethod(symbol.shift, 0.5*(UP+LEFT))
        )
        self.remove(plane, labels)
        return vector, symbol, coordinates

    def physics_conception(self, creatures, original_vector):
        self.fade_all_but(creatures, 0)
        physy, compy, mathy = creatures

        vector = Vector(2*RIGHT)
        vector.next_to(physy, UP+RIGHT)
        brace = Brace(vector, DOWN)
        length = TextMobject("Length")
        length.next_to(brace, DOWN)
        group = VMobject(vector, brace, length)
        group.rotate_in_place(np.pi/6)
        vector.get_center = lambda : vector.get_start()        

        direction = TextMobject("Direction")
        direction.next_to(vector, RIGHT)
        direction.shift(UP)

        two_dimensional = TextMobject("Two-dimensional")
        three_dimensional = TextMobject("Three-dimensional")
        two_dimensional.to_corner(UP+RIGHT)
        three_dimensional.to_corner(UP+RIGHT)

        random_vectors = VMobject(*[
            Vector(
                random.uniform(-2, 2)*RIGHT + \
                random.uniform(-2, 2)*UP
            ).shift(
                random.uniform(0, 4)*RIGHT + \
                random.uniform(-1, 2)*UP
            ).set_color(random_color())
            for x in range(5)
        ])

        self.play(
            Transform(original_vector, vector),
            ApplyMethod(physy.change_mode, "speaking")
        )
        self.remove(original_vector)
        self.add(vector )
        self.wait()
        self.play(
            GrowFromCenter(brace),
            Write(length),
            run_time = 1
        )
        self.wait()
        self.remove(brace, length)
        self.play(
            Rotate(vector, np.pi/3, in_place = True),
            Write(direction),
            run_time = 1
        )
        for angle in -2*np.pi/3, np.pi/3:
            self.play(Rotate(
                vector, angle,
                in_place = True,
                run_time = 1
            ))
        self.play(ApplyMethod(physy.change_mode, "plain")) 
        self.remove(direction)
        for point in 2*UP, 4*RIGHT, ORIGIN:
            self.play(ApplyMethod(vector.move_to, point))
        self.wait()
        self.play(
            Write(two_dimensional),
            ApplyMethod(physy.change_mode, "pondering"),
            ShowCreation(random_vectors, lag_ratio = 0.5),
            run_time = 1 
        )
        self.wait(2)
        self.remove(random_vectors, vector)
        self.play(Transform(two_dimensional, three_dimensional))
        self.wait(5)
        self.remove(two_dimensional)
        self.restore_creatures(creatures)

    def cs_conception(self, creatures):
        self.fade_all_but(creatures, 1)
        physy, compy, mathy = creatures

        title = TextMobject("Vectors $\\Leftrightarrow$ lists of numbers")
        title.to_edge(UP)

        vectors = VMobject(*list(map(matrix_to_mobject, [
            [2, 1],
            [5, 0, 0, -3],
            [2.3, -7.1, 0.1],
        ])))
        vectors.arrange(RIGHT, buff = 1)
        vectors.to_edge(LEFT)

        self.play(
            ApplyMethod(compy.change_mode, "sassy"),
            Write(title, run_time = 1)
        )
        self.play(Write(vectors))
        self.wait()
        self.play(ApplyMethod(compy.change_mode, "pondering"))
        self.house_example(vectors, title)
        self.restore_creatures(creatures)


    def house_example(self, starter_mobject, title):
        house = SVGMobject("house")
        house.set_stroke(width = 0)
        house.set_fill(BLUE_C, opacity = 1)
        house.set_height(3)
        house.center()
        square_footage_words = TextMobject("Square footage:")
        price_words = TextMobject("Price: ")
        square_footage = TexMobject("2{,}600\\text{ ft}^2")
        price = TextMobject("\\$300{,}000")

        house.to_edge(LEFT).shift(UP)
        square_footage_words.next_to(house, RIGHT)
        square_footage_words.shift(0.5*UP)
        square_footage_words.set_color(RED)
        price_words.next_to(square_footage_words, DOWN, aligned_edge = LEFT)
        price_words.set_color(GREEN)
        square_footage.next_to(square_footage_words)
        square_footage.set_color(RED)
        price.next_to(price_words)
        price.set_color(GREEN)

        vector = Matrix([square_footage.copy(), price.copy()])
        vector.next_to(house, RIGHT).shift(0.25*UP)
        new_square_footage, new_price = vector.get_mob_matrix().flatten()
        not_equals = TexMobject("\\ne")
        not_equals.next_to(vector)
        alt_vector = Matrix([
            TextMobject("300{,}000\\text{ ft}^2").set_color(RED),
            TextMobject("\\$2{,}600").set_color(GREEN)
        ])
        alt_vector.next_to(not_equals)

        brace = Brace(vector, RIGHT)
        two_dimensional = TextMobject("2 dimensional")
        two_dimensional.next_to(brace)
        brackets = vector.get_brackets()

        self.play(Transform(starter_mobject, house))
        self.remove(starter_mobject)
        self.add(house)
        self.add(square_footage_words)
        self.play(Write(square_footage, run_time = 2))
        self.add(price_words)
        self.play(Write(price, run_time = 2))
        self.wait()
        self.play(
            FadeOut(square_footage_words), FadeOut(price_words),
            Transform(square_footage, new_square_footage),
            Transform(price, new_price),
            Write(brackets),
            run_time = 1
        )
        self.remove(square_footage_words, price_words)
        self.wait()
        self.play(
            Write(not_equals),
            Write(alt_vector),
            run_time = 1
        )
        self.wait()
        self.play(FadeOut(not_equals), FadeOut(alt_vector))
        self.remove(not_equals, alt_vector)
        self.wait()
        self.play(
            GrowFromCenter(brace),
            Write(two_dimensional),
            run_time = 1
        )
        self.wait()

        everything = VMobject(
            house, square_footage, price, brackets, brace, 
            two_dimensional, title
        )
        self.play(ApplyMethod(everything.shift, FRAME_WIDTH*LEFT))
        self.remove(everything)


    def handle_mathy(self, creatures):
        self.fade_all_but(creatures, 2)
        physy, compy, mathy = creatures

        v_color = YELLOW 
        w_color = BLUE
        sum_color = GREEN

        v_arrow = Vector([1, 1])
        w_arrow = Vector([2, 1])
        w_arrow.shift(v_arrow.get_end())
        sum_arrow = Vector(w_arrow.get_end())
        arrows = VMobject(v_arrow, w_arrow, sum_arrow)
        arrows.scale(0.7)
        arrows.to_edge(LEFT, buff = 2)

        v_array = matrix_to_mobject([3, -5])
        w_array = matrix_to_mobject([2, 1])
        sum_array = matrix_to_mobject(["3+2", "-5+1"])
        arrays = VMobject(
            v_array, TexMobject("+"), w_array, TexMobject("="), sum_array
        )
        arrays.arrange(RIGHT)
        arrays.scale(0.75)
        arrays.to_edge(RIGHT).shift(UP)

        v_sym = TexMobject("\\vec{\\textbf{v}}")
        w_sym = TexMobject("\\vec{\\textbf{w}}")
        syms = VMobject(v_sym, TexMobject("+"), w_sym)
        syms.arrange(RIGHT)
        syms.center().shift(2*UP)

        statement = TextMobject("We'll ignore him \\\\ for now")
        statement.set_color(PINK)
        statement.set_width(arrays.get_width())
        statement.next_to(arrays, DOWN, buff = 1.5)
        circle = Circle()
        circle.shift(syms.get_bottom())

        VMobject(v_arrow, v_array, v_sym).set_color(v_color)
        VMobject(w_arrow, w_array, w_sym).set_color(w_color)
        VMobject(sum_arrow, sum_array).set_color(sum_color)

        self.play(
            Write(syms), Write(arrays),
            ShowCreation(arrows),
            ApplyMethod(mathy.change_mode, "pondering"),
            run_time = 2
        )
        self.play(Blink(mathy))
        self.add_scaling(arrows, syms, arrays)
        self.play(Write(statement))
        self.play(ApplyMethod(mathy.change_mode, "sad"))
        self.wait()
        self.play(
            ShowCreation(circle),
            ApplyMethod(mathy.change_mode, "plain")
        )
        self.wait()


    def add_scaling(self, arrows, syms, arrays):
        s_arrows = VMobject(
            TexMobject("2"), Vector([1, 1]).set_color(YELLOW), 
            TexMobject("="), Vector([2, 2]).set_color(WHITE)
        )
        s_arrows.arrange(RIGHT)
        s_arrows.scale(0.75)
        s_arrows.next_to(arrows, DOWN)

        s_arrays = VMobject(
            TexMobject("2"), 
            matrix_to_mobject([3, -5]).set_color(YELLOW),
            TextMobject("="),
            matrix_to_mobject(["2(3)", "2(-5)"])
        )
        s_arrays.arrange(RIGHT)
        s_arrays.scale(0.75)
        s_arrays.next_to(arrays, DOWN)

        s_syms = TexMobject(["2", "\\vec{\\textbf{v}}"])
        s_syms.split()[-1].set_color(YELLOW)
        s_syms.next_to(syms, DOWN)

        self.play(
            Write(s_arrows), Write(s_arrays), Write(s_syms),
            run_time = 2
        )
        self.wait()



    def fade_all_but(self, creatures, index):
        self.play(*[
            FadeOut(VMobject(pi, pi.title))
            for pi in creatures[:index] + creatures[index+1:]
        ])

    def restore_creatures(self, creatures):
        self.play(*[
            ApplyFunction(lambda m : m.change_mode("plain").set_color(m.color), pi)
            for pi in creatures
        ] + [
            ApplyMethod(pi.title.set_fill, WHITE, 1.0)
            for pi in creatures
        ])


class ThreeDVectorField(Scene):
    pass


class HelpsToHaveOneThought(Scene):
    def construct(self):
        morty = Mortimer()
        morty.to_corner(DOWN+RIGHT)
        morty.look(DOWN+LEFT)
        new_morty = morty.copy().change_mode("speaking")  
        new_morty.look(DOWN+LEFT)      

        randys = VMobject(*[
            Randolph(color = color).scale(0.8)
            for color in (BLUE_D, BLUE_C, BLUE_E)
        ])
        randys.arrange(RIGHT)
        randys.to_corner(DOWN+LEFT)
        randy = randys.split()[1]

        speech_bubble = morty.get_bubble(SpeechBubble)
        words = TextMobject("Think of some vector...")
        speech_bubble.position_mobject_inside(words)
        thought_bubble = randy.get_bubble()
        arrow = Vector([2, 1]).scale(0.7)
        or_word = TextMobject("or")
        array = Matrix([2, 1]).scale(0.5)
        q_mark = TextMobject("?")
        thought = VMobject(arrow, or_word, array, q_mark)
        thought.arrange(RIGHT, buff = 0.2)
        thought_bubble.position_mobject_inside(thought)
        thought_bubble.set_fill(BLACK, opacity = 1)


        self.add(morty, randys)
        self.play(
            ShowCreation(speech_bubble),
            Transform(morty, new_morty),
            Write(words)
        )
        self.wait(2)
        self.play(
            FadeOut(speech_bubble),
            FadeOut(words),
            ApplyMethod(randy.change_mode, "pondering"),
            ShowCreation(thought_bubble),
            Write(thought)
        )
        self.wait(2)


class HowIWantYouToThinkAboutVectors(Scene):
    def construct(self):
        vector = Vector([-2, 3])
        plane = NumberPlane()
        axis_labels = plane.get_axis_labels()
        other_vectors = VMobject(*list(map(Vector, [
            [1, 2], [2, -1], [4, 0]
        ])))
        colors = [GREEN_B, MAROON_B, PINK]
        for v, color in zip(other_vectors.split(), colors):
            v.set_color(color)
        shift_val = 4*RIGHT+DOWN

        dot = Dot(radius = 0.1)
        dot.set_color(RED)
        tail_word = TextMobject("Tail")
        tail_word.shift(0.5*DOWN+2.5*LEFT)
        line = Line(tail_word, dot)

        self.play(ShowCreation(vector))
        self.wait(2)
        self.play(
            ShowCreation(plane, lag_ratio=0.5),
            Animation(vector)
        )
        self.play(Write(axis_labels, run_time = 1))
        self.wait()
        self.play(
            GrowFromCenter(dot),
            ShowCreation(line),
            Write(tail_word, run_time = 1)
        )
        self.wait()
        self.play(
            FadeOut(tail_word),
            ApplyMethod(VMobject(dot, line).scale, 0.01) 
        )
        self.remove(tail_word, line, dot)
        self.wait()

        self.play(ApplyMethod(
            vector.shift, shift_val,
            path_arc = 3*np.pi/2,
            run_time = 3
        ))
        self.play(ApplyMethod(
            vector.shift, -shift_val,
            rate_func = rush_into,
            run_time = 0.5
        ))
        self.wait(3)

        self.play(ShowCreation(
            other_vectors, 
            run_time = 3
        ))
        self.wait(3)

        x_axis, y_axis = plane.get_axes().split()
        x_label = axis_labels.split()[0]
        x_axis = x_axis.copy()
        x_label = x_label.copy()
        everything = VMobject(*self.mobjects)
        self.play(
            FadeOut(everything),
            Animation(x_axis), Animation(x_label)
        )


class ListsOfNumbersAddOn(Scene):
    def construct(self):
        arrays = VMobject(*list(map(matrix_to_mobject, [
            [-2, 3], [1, 2], [2, -1], [4, 0]
        ])))
        arrays.arrange(buff = 0.4)
        arrays.scale(2)
        self.play(Write(arrays))
        self.wait(2)


class CoordinateSystemWalkthrough(VectorScene):
    def construct(self):
        self.introduce_coordinate_plane()
        self.show_vector_coordinates()
        self.coords_to_vector([3, -1])
        self.vector_to_coords([-2, -1.5], integer_labels = False)

    def introduce_coordinate_plane(self):
        plane = NumberPlane()
        x_axis, y_axis = plane.get_axes().copy().split()
        x_label, y_label = plane.get_axis_labels().split()
        number_line = NumberLine(tick_frequency = 1)
        x_tick_marks = number_line.get_tick_marks()
        y_tick_marks = x_tick_marks.copy().rotate(np.pi/2)
        tick_marks = VMobject(x_tick_marks, y_tick_marks)
        tick_marks.set_color(WHITE)
        plane_lines = [m for m in plane.get_family() if isinstance(m, Line)]
        origin_words = TextMobject("Origin")
        origin_words.shift(2*UP+2*LEFT)
        dot = Dot(radius = 0.1).set_color(RED)
        line = Line(origin_words.get_bottom(), dot.get_corner(UP+LEFT))

        unit_brace = Brace(Line(RIGHT, 2*RIGHT))
        one = TexMobject("1").next_to(unit_brace, DOWN)

        self.add(x_axis, x_label)
        self.wait()
        self.play(ShowCreation(y_axis))
        self.play(Write(y_label, run_time = 1))
        self.wait(2)
        self.play(
            Write(origin_words),
            GrowFromCenter(dot),
            ShowCreation(line),
            run_time = 1
        )
        self.wait(2)
        self.play(
            FadeOut(VMobject(origin_words, dot, line))
        )
        self.remove(origin_words, dot, line)
        self.wait()
        self.play(
            ShowCreation(tick_marks)
        )
        self.play(
            GrowFromCenter(unit_brace),
            Write(one, run_time = 1)            
        )
        self.wait(2)
        self.remove(unit_brace, one)
        self.play(
            *list(map(GrowFromCenter, plane_lines)) + [
            Animation(x_axis), Animation(y_axis)
        ])
        self.wait()
        self.play(
            FadeOut(plane),
            Animation(VMobject(x_axis, y_axis, tick_marks))
        )
        self.remove(plane)
        self.add(tick_marks)

    def show_vector_coordinates(self):
        starting_mobjects = list(self.mobjects)

        vector = Vector([-2, 3])
        x_line = Line(ORIGIN, -2*RIGHT)
        y_line = Line(-2*RIGHT, -2*RIGHT+3*UP)
        x_line.set_color(X_COLOR)
        y_line.set_color(Y_COLOR)

        array = vector_coordinate_label(vector)
        x_label, y_label = array.get_mob_matrix().flatten()
        x_label_copy = x_label.copy()
        x_label_copy.set_color(X_COLOR)
        y_label_copy = y_label.copy()
        y_label_copy.set_color(Y_COLOR)

        point = Dot(4*LEFT+2*UP)
        point_word = TextMobject("(-4, 2) as \\\\ a point")
        point_word.scale(0.7)
        point_word.next_to(point, DOWN)
        point.add(point_word)

        self.play(ShowCreation(vector))
        self.play(Write(array))
        self.wait(2)
        self.play(ApplyMethod(x_label_copy.next_to, x_line, DOWN))
        self.play(ShowCreation(x_line))
        self.wait(2)
        self.play(ApplyMethod(y_label_copy.next_to, y_line, LEFT))
        self.play(ShowCreation(y_line))
        self.wait(2)
        self.play(FadeIn(point))
        self.wait()
        self.play(ApplyFunction(
            lambda m : m.scale_in_place(1.25).set_color(YELLOW),
            array.get_brackets(),
            rate_func = there_and_back
        ))
        self.wait()
        self.play(FadeOut(point))
        self.remove(point)
        self.wait()
        self.clear()
        self.add(*starting_mobjects)

class LabeledThreeDVector(Scene):
    pass

class WriteZ(Scene):
    def construct(self):
        z = TexMobject("z").set_color(Z_COLOR)
        z.set_height(4)
        self.play(Write(z, run_time = 2))
        self.wait(3)


class Write3DVector(Scene):
    def construct(self):
        array = Matrix([2, 1, 3]).scale(2)
        x, y, z = array.get_mob_matrix().flatten()
        brackets = array.get_brackets()
        x.set_color(X_COLOR)
        y.set_color(Y_COLOR)
        z.set_color(Z_COLOR)

        self.add(brackets)
        for mob in x, y, z:
            self.play(Write(mob), run_time = 2)
        self.wait()


class VectorAddition(VectorScene):
    def construct(self):
        self.add_plane()
        vects = self.define_addition()
        # vects = map(Vector, [[1, 2], [3, -1], [4, 1]])
        self.ask_why(*vects)
        self.answer_why(*vects)

    def define_addition(self):
        v1 = self.add_vector([1, 2])
        v2 = self.add_vector([3, -1], color = MAROON_B)
        l1 = self.label_vector(v1, "v")
        l2 = self.label_vector(v2, "w")
        self.wait()
        self.play(ApplyMethod(v2.shift, v1.get_end()))
        self.wait()
        v_sum = self.add_vector(v2.get_end(), color = PINK)
        sum_tex = "\\vec{\\textbf{v}} + \\vec{\\textbf{w}}"
        self.label_vector(v_sum, sum_tex, rotate = True)
        self.wait(3)
        return v1, v2, v_sum

    def ask_why(self, v1, v2, v_sum):
        why = TextMobject("Why?")
        why_not_this = TextMobject("Why not \\\\ this?")
        new_v2 = v2.copy().shift(-v2.get_start())
        new_v_sum = v_sum.copy()
        alt_vect_sum = new_v2.get_end() - v1.get_end()
        new_v_sum.shift(-new_v_sum.get_start())
        new_v_sum.rotate(
            angle_of_vector(alt_vect_sum) - new_v_sum.get_angle()
        )
        new_v_sum.scale(get_norm(alt_vect_sum)/new_v_sum.get_length())
        new_v_sum.shift(v1.get_end())
        new_v_sum.submobjects.reverse()#No idea why I have to do this
        original_v_sum = v_sum.copy()

        why.next_to(v2, RIGHT)
        why_not_this.next_to(new_v_sum, RIGHT)
        why_not_this.shift(0.5*UP)

        self.play(Write(why, run_time = 1))
        self.wait(2)
        self.play(
            Transform(v2, new_v2),
            Transform(v_sum, new_v_sum),            
            Transform(why, why_not_this)
        )
        self.wait(2)
        self.play(
            FadeOut(why),
            Transform(v_sum, original_v_sum)
        )
        self.remove(why)
        self.wait()

    def answer_why(self, v1, v2, v_sum):
        randy = Randolph(color = PINK)
        randy.shift(-randy.get_bottom())
        self.remove(v1, v2, v_sum)
        for v in v1, v2, v_sum:
            self.add(v)
            self.show_ghost_movement(v)
            self.remove(v)
        self.add(v1, v2 )
        self.wait()
        self.play(ApplyMethod(randy.scale, 0.3))
        self.play(ApplyMethod(randy.shift, v1.get_end()))
        self.wait()
        self.play(ApplyMethod(v2.shift, v1.get_end()))
        self.play(ApplyMethod(randy.move_to, v2.get_end()))
        self.wait()
        self.remove(randy)
        randy.move_to(ORIGIN)
        self.play(FadeIn(v_sum))
        self.play(ApplyMethod(randy.shift, v_sum.get_end()))
        self.wait()


class AddingNumbersOnNumberLine(Scene):
    def construct(self):
        number_line = NumberLine()
        number_line.add_numbers()
        two_vect = Vector([2, 0])
        five_vect = Vector([5, 0], color = MAROON_B)
        seven_vect = Vector([7, 0], color = PINK)
        five_vect.shift(two_vect.get_end())
        seven_vect.shift(0.5*DOWN)
        vects = [two_vect, five_vect, seven_vect]

        two, five, seven = list(map(TexMobject, ["2", "5", "7"]))
        two.next_to(two_vect, UP)
        five.next_to(five_vect, UP)
        seven.next_to(seven_vect, DOWN)
        nums = [two, five, seven]

        sum_mob = TexMobject("2 + 5").shift(3*UP)

        self.play(ShowCreation(number_line))
        self.wait()
        self.play(Write(sum_mob, run_time = 2))
        self.wait()
        for vect, num in zip(vects, nums):
            self.play(
                ShowCreation(vect),
                Write(num, run_time = 1)
            )
            self.wait()


class VectorAdditionNumerically(VectorScene):
    def construct(self):
        plus = TexMobject("+")
        equals = TexMobject("=")
        randy = Randolph()
        randy.set_height(1)
        randy.shift(-randy.get_bottom())

        axes = self.add_axes()
        x_axis, y_axis = axes.split()

        v1 = self.add_vector([1, 2])
        coords1, x_line1, y_line1 = self.vector_to_coords(v1, clean_up = False)
        self.play(ApplyFunction(
            lambda m : m.next_to(y_axis, RIGHT).to_edge(UP),
            coords1
        ))
        plus.next_to(coords1, RIGHT)

        v2 = self.add_vector([3, -1], color = MAROON_B)
        coords2, x_line2, y_line2 = self.vector_to_coords(v2, clean_up = False)
        self.wait()
        self.play(
            ApplyMethod(coords2.next_to, plus, RIGHT),
            Write(plus, run_time = 1), 
            *[
                ApplyMethod(mob.shift, v1.get_end())
                for mob in (v2, x_line2, y_line2)
            ]
        )
        equals.next_to(coords2, RIGHT)
        self.wait()

        self.play(FadeIn(randy))
        for step in [RIGHT, 2*UP, 3*RIGHT, DOWN]:
            self.play(ApplyMethod(randy.shift, step, run_time = 1.5))
        self.wait()
        self.play(ApplyMethod(randy.shift, -randy.get_bottom()))

        self.play(ApplyMethod(x_line2.shift, 2*DOWN))
        self.play(ApplyMethod(y_line1.shift, 3*RIGHT))
        for step in [4*RIGHT, 2*UP, DOWN]:
            self.play(ApplyMethod(randy.shift, step))
        self.play(FadeOut(randy))
        self.remove(randy)
        one_brace = Brace(x_line1)
        three_brace = Brace(x_line2)
        one = TexMobject("1").next_to(one_brace, DOWN)
        three = TexMobject("3").next_to(three_brace, DOWN)
        self.play(
            GrowFromCenter(one_brace),
            GrowFromCenter(three_brace),
            Write(one),
            Write(three),
            run_time = 1
        )
        self.wait()

        two_brace = Brace(y_line1, RIGHT)
        two = TexMobject("2").next_to(two_brace, RIGHT)
        new_y_line = Line(4*RIGHT, 4*RIGHT+UP, color = Y_COLOR)
        two_minus_one_brace = Brace(new_y_line, RIGHT)
        two_minus_one = TexMobject("2+(-1)").next_to(two_minus_one_brace, RIGHT)
        self.play(
            GrowFromCenter(two_brace),
            Write(two, run_time = 1)
        )
        self.wait()
        self.play(
            Transform(two_brace, two_minus_one_brace),
            Transform(two, two_minus_one),
            Transform(y_line1, new_y_line),
            Transform(y_line2, new_y_line)
        )
        self.wait()
        self.add_vector(v2.get_end(), color = PINK )

        sum_coords = Matrix(["1+3", "2+(-1)"])
        sum_coords.set_height(coords1.get_height())
        sum_coords.next_to(equals, RIGHT)
        brackets = sum_coords.get_brackets()
        x1, y1 = coords1.get_mob_matrix().flatten()
        x2, y2 = coords2.get_mob_matrix().flatten()
        sum_x, sum_y = sum_coords.get_mob_matrix().flatten()
        sum_x_start = VMobject(x1, x2).copy()
        sum_y_start = VMobject(y1, y2).copy()
        self.play(
            Write(brackets),
            Write(equals),
            Transform(sum_x_start, sum_x),
            run_time = 1
        )
        self.play(Transform(sum_y_start, sum_y))
        self.wait(2)

        starters = [x1, y1, x2, y2, sum_x_start, sum_y_start]
        variables = list(map(TexMobject, [
            "x_1", "y_1", "x_2", "y_2", "x_1+y_1", "x_2+y_2"
        ]))
        for i, (var, starter) in enumerate(zip(variables, starters)):
            if i%2 == 0:
                var.set_color(X_COLOR)
            else:
                var.set_color(Y_COLOR)
            var.scale(VECTOR_LABEL_SCALE_FACTOR)
            var.move_to(starter)
        self.play(
            Transform(
                VMobject(*starters[:4]), 
                VMobject(*variables[:4])
            ),
            FadeOut(sum_x_start), 
            FadeOut(sum_y_start)
        )
        sum_x_end, sum_y_end = variables[-2:]
        self.wait(2)
        self.play(
            Transform(VMobject(x1, x2).copy(), sum_x_end)
        )
        self.play(
            Transform(VMobject(y1, y2).copy(), sum_y_end)
        )
        self.wait(3)

class MultiplicationByANumberIntro(Scene):
    def construct(self):
        v = TexMobject("\\vec{\\textbf{v}}")
        v.set_color(YELLOW)
        nums = list(map(TexMobject, ["2", "\\dfrac{1}{3}", "-1.8"]))
        for mob in [v] + nums:
            mob.scale(1.5)

        self.play(Write(v, run_time = 1))
        last = None
        for num in nums:
            num.next_to(v, LEFT)
            if last:
                self.play(Transform(last, num))
            else:
                self.play(FadeIn(num))
                last = num
            self.wait()

class ShowScalarMultiplication(VectorScene):
    def construct(self):
        plane = self.add_plane()
        v = self.add_vector([3, 1])
        label = self.label_vector(v, "v", add_to_vector = False)

        self.scale_vector(v, 2, label)
        self.scale_vector(v, 1./3, label, factor_tex = "\\dfrac{1}{3}")
        self.scale_vector(v, -1.8, label)
        self.remove(label)
        self.describe_scalars(v, plane)


    def scale_vector(self, v, factor, v_label, 
                     v_name = "v", factor_tex = None):
        starting_mobjects = list(self.mobjects)

        if factor_tex is None:
            factor_tex = str(factor)
        scaled_vector = self.add_vector(
            factor*v.get_end(), animate = False
        )
        self.remove(scaled_vector)
        label_tex = "%s\\vec{\\textbf{%s}}"%(factor_tex, v_name)
        label = self.label_vector(
            scaled_vector, label_tex, animate = False,
            add_to_vector = False
        )
        self.remove(label)
        factor_mob = TexMobject(factor_tex)
        if factor_mob.get_height() > 1:
            factor_mob.set_height(0.9)
        if factor_mob.get_width() > 1:
            factor_mob.set_width(0.9)
        factor_mob.shift(1.5*RIGHT+2.5*UP)

        num_factor_parts = len(factor_mob.split())
        factor_mob_parts_in_label = label.split()[:num_factor_parts]
        label_remainder_parts = label.split()[num_factor_parts:]
        factor_in_label = VMobject(*factor_mob_parts_in_label)
        label_remainder = VMobject(*label_remainder_parts)


        self.play(Write(factor_mob, run_time = 1))
        self.wait()
        self.play(
            ApplyMethod(v.copy().set_color, DARK_GREY),
            ApplyMethod(v_label.copy().set_color, DARK_GREY),
            Transform(factor_mob, factor_in_label),
            Transform(v.copy(), scaled_vector),
            Transform(v_label.copy(), label_remainder),
        )
        self.wait(2)

        self.clear()
        self.add(*starting_mobjects)

    def describe_scalars(self, v, plane):
        axes = plane.get_axes()
        long_v = Vector(2*v.get_end())
        long_minus_v = Vector(-2*v.get_end())
        original_v = v.copy()
        scaling_word = TextMobject("``Scaling''").to_corner(UP+LEFT)
        scaling_word.shift(2*RIGHT)
        scalars = VMobject(*list(map(TexMobject, [
            "2,", "\\dfrac{1}{3},", "-1.8,", "\\dots"
        ])))
        scalars.arrange(RIGHT, buff = 0.4)
        scalars.next_to(scaling_word, DOWN, aligned_edge = LEFT)
        scalars_word = TextMobject("``Scalars''")
        scalars_word.next_to(scalars, DOWN, aligned_edge = LEFT)

        self.remove(plane)
        self.add(axes)
        self.play(
            Write(scaling_word),
            Transform(v, long_v),
            run_time = 1.5
        )
        self.play(Transform(v, long_minus_v, run_time = 3))
        self.play(Write(scalars))
        self.wait()
        self.play(Write(scalars_word))
        self.play(Transform(v, original_v), run_time = 3)
        self.wait(2)

class ScalingNumerically(VectorScene):
    def construct(self):
        two_dot = TexMobject("2\\cdot")
        equals = TexMobject("=")
        self.add_axes()
        v = self.add_vector([3, 1])
        v_coords, vx_line, vy_line = self.vector_to_coords(v, clean_up = False)
        self.play(ApplyMethod(v_coords.to_edge, UP))
        two_dot.next_to(v_coords, LEFT)
        equals.next_to(v_coords, RIGHT)
        two_v = self.add_vector([6, 2], animate = False)
        self.remove(two_v)
        self.play(
            Transform(v.copy(), two_v), 
            Write(two_dot, run_time = 1)
        )
        two_v_coords, two_v_x_line, two_v_y_line = self.vector_to_coords(
            two_v, clean_up = False
        )
        self.play(
            ApplyMethod(two_v_coords.next_to, equals, RIGHT),
            Write(equals, run_time = 1)
        )
        self.wait(2)

        x, y = v_coords.get_mob_matrix().flatten()
        two_v_elems = two_v_coords.get_mob_matrix().flatten()
        x_sym, y_sym = list(map(TexMobject, ["x", "y"]))
        two_x_sym, two_y_sym = list(map(TexMobject, ["2x", "2y"]))
        VMobject(x_sym, two_x_sym).set_color(X_COLOR)
        VMobject(y_sym, two_y_sym).set_color(Y_COLOR)
        syms = [x_sym, y_sym, two_x_sym, two_y_sym]
        VMobject(*syms).scale(VECTOR_LABEL_SCALE_FACTOR)
        for sym, num in zip(syms, [x, y] + list(two_v_elems)):
            sym.move_to(num)
        self.play(
            Transform(x, x_sym),
            Transform(y, y_sym),
            FadeOut(VMobject(*two_v_elems))
        )
        self.wait()
        self.play(
            Transform(
                VMobject(two_dot.copy(), x.copy()),
                two_x_sym
            ),
            Transform(
                VMobject(two_dot.copy(), y.copy() ),
                two_y_sym
            )
        )
        self.wait(2)



class FollowingVideos(UpcomingSeriesOfVidoes):
    def construct(self):
        v_sum = VMobject(
            Vector([1, 1], color = YELLOW),
            Vector([3, 1], color = BLUE).shift(RIGHT+UP),
            Vector([4, 2], color = GREEN),
        )
        scalar_multiplication = VMobject(
            TexMobject("2 \\cdot "),
            Vector([1, 1]),
            TexMobject("="),
            Vector([2, 2], color = WHITE)
        )
        scalar_multiplication.arrange(RIGHT)
        both = VMobject(v_sum, scalar_multiplication)
        both.arrange(RIGHT, buff = 1)
        both.shift(2*DOWN)
        self.add(both)

        UpcomingSeriesOfVidoes.construct(self)
        last_video = self.mobjects[-1]
        self.play(ApplyMethod(last_video.set_color, YELLOW))
        self.wait()
        everything = VMobject(*self.mobjects)
        everything.remove(last_video)
        big_last_video = last_video.copy()
        big_last_video.center()
        big_last_video.set_height(2.5*FRAME_Y_RADIUS)
        big_last_video.set_fill(opacity = 0)
        self.play(
            ApplyMethod(everything.shift, FRAME_WIDTH*LEFT),
            Transform(last_video, big_last_video),
            run_time = 2
        )



class ItDoesntMatterWhich(Scene):
    def construct(self):
        physy = Physicist()
        compy = ComputerScientist()
        physy.title = TextMobject("Physics student").to_corner(DOWN+LEFT)
        compy.title = TextMobject("CS student").to_corner(DOWN+RIGHT)
        for pi in physy, compy:
            pi.next_to(pi.title, UP)
            self.add(pi, pi.title)
        compy_speech = compy.get_bubble(SpeechBubble)
        physy_speech = physy.get_bubble(SpeechBubble)
        arrow = Vector([2, 1])
        array = matrix_to_mobject([2, 1])
        goes_to = TexMobject("\\Rightarrow")
        physy_statement = VMobject(arrow, goes_to, array)
        physy_statement.arrange(RIGHT)
        compy_statement = physy_statement.copy()
        compy_statement.arrange(LEFT)
        physy_speech.position_mobject_inside(physy_statement)
        compy_speech.position_mobject_inside(compy_statement)

        new_arrow = Vector([2, 1])
        x_line = Line(ORIGIN, 2*RIGHT, color = X_COLOR)
        y_line = Line(2*RIGHT, 2*RIGHT+UP, color = Y_COLOR)
        x_mob = TexMobject("2").next_to(x_line, DOWN)
        y_mob = TexMobject("1").next_to(y_line, RIGHT)
        new_arrow.add(x_line, y_line, x_mob, y_mob)
        back_and_forth = VMobject(
            new_arrow,
            TexMobject("\\Leftrightarrow"),
            matrix_to_mobject([2, 1])
        )
        back_and_forth.arrange(LEFT).center()


        self.wait()
        self.play(
            ApplyMethod(physy.change_mode, "speaking"),
            ShowCreation(physy_speech),
            Write(physy_statement),
            run_time = 1
        )
        self.play(Blink(compy))
        self.play(
            ApplyMethod(physy.change_mode, "sassy"),
            ApplyMethod(compy.change_mode, "speaking"),
            FadeOut(physy_speech),
            ShowCreation(compy_speech),
            Transform(physy_statement, compy_statement, path_arc = np.pi)
        )
        self.wait(2)
        self.play(
            ApplyMethod(physy.change_mode, "pondering"),
            ApplyMethod(compy.change_mode, "pondering"),
            Transform(compy_speech, VectorizedPoint(compy_speech.get_tip())),
            Transform(physy_statement, back_and_forth)
        )
        self.wait()


class DataAnalyst(Scene):
    def construct(self):
        plane = NumberPlane()
        ellipse = ParametricFunction(
            lambda x : 2*np.cos(x)*(UP+RIGHT) + np.sin(x)*(UP+LEFT),
            color = PINK, 
            t_max = 2*np.pi
        )
        ellipse_points = [
            ellipse.point_from_proportion(x)
            for x in np.arange(0, 1, 1./20)
        ]
        string_vects = [
            matrix_to_mobject(("%.02f %.02f"%tuple(ep[:2])).split())
            for ep in ellipse_points
        ]
        string_vects_matrix = Matrix(
            np.array(string_vects).reshape((4, 5))
        )
        string_vects = string_vects_matrix.get_mob_matrix().flatten()
        string_vects = VMobject(*string_vects)

        vects = VMobject(*list(map(Vector, ellipse_points)))

        self.play(Write(string_vects))
        self.wait(2)
        self.play(
            FadeIn(plane),
            Transform(string_vects, vects)
        )
        self.remove(string_vects)
        self.add(vects)
        self.wait()
        self.play(
            ApplyMethod(plane.fade, 0.7),
            ApplyMethod(vects.set_color, DARK_GREY),
            ShowCreation(ellipse)
        )
        self.wait(3)


class ManipulateSpace(LinearTransformationScene):
    CONFIG = {
        "include_background_plane" : False,
        "show_basis_vectors" : False,
    }

    def construct(self):
        matrix_rule = TexMobject("""
            \\left[
                \\begin{array}{c}
                    x \\\\ y
                \\end{array}
            \\right]
            \\rightarrow
            \\left[
                \\begin{array}{c}
                    2x + y \\\\ y + 2x
                \\end{array}
            \\right]
        """)

        self.setup()
        pi_creature = PiCreature(color = PINK).scale(0.5)
        pi_creature.shift(-pi_creature.get_corner(DOWN+LEFT))
        self.plane.prepare_for_nonlinear_transform()

        self.play(ShowCreation(
            self.plane,
            run_time = 2
        ))
        self.play(FadeIn(pi_creature))
        self.play(Blink(pi_creature))
        self.plane.add(pi_creature)
        self.play(Homotopy(plane_wave_homotopy, self.plane, run_time = 3))
        self.wait(2)
        self.apply_matrix([[2, 1], [1, 2]])
        self.wait()
        self.play(
            FadeOut(self.plane),
            Write(matrix_rule),
            run_time = 2
        )
        self.wait()

class CodingMathyAnimation(Scene):
    pass

class NextVideo(Scene):
    def construct(self):
        title = TextMobject("Next video: Linear combinations, span, and bases")
        title.to_edge(UP)
        rect = Rectangle(width = 16, height = 9, color = BLUE)
        rect.set_height(6)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait()    


































