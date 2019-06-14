from manimlib.imports import *

import displayer as disp

from hilbert.curves import \
    TransformOverIncreasingOrders, FlowSnake, HilbertCurve, \
    SnakeCurve


from constants import *



def get_grid():
    return Grid(64, 64)

def get_freq_line():
    return UnitInterval().shift(2*DOWN) ##Change?

def get_mathy_and_bubble():
    mathy = Mathematician()
    mathy.to_edge(DOWN).shift(4*LEFT)
    bubble = SpeechBubble(initial_width = 8)
    bubble.pin_to(mathy)
    return mathy, bubble

class AboutSpaceFillingCurves(TransformOverIncreasingOrders):
    @staticmethod
    def args_to_string():
        return ""

    @staticmethod
    def string_to_args(arg_str):
        return ()

    def construct(self):
        self.bubble = ThoughtBubble().ingest_submobjects()
        self.bubble.scale(1.5)

        TransformOverIncreasingOrders.construct(self, FlowSnake, 7)
        self.play(Transform(self.curve, self.bubble))
        self.show_infinite_objects()
        self.pose_question()
        self.wait()

    def show_infinite_objects(self):
        sigma, summand, equals, result = TexMobject([
            "\\sum_{n = 1}^{\\infty}",
            "\\dfrac{1}{n^2}",
            "=",
            "\\dfrac{\pi^2}{6}"
        ]).split()
        alt_summand = TexMobject("n").replace(summand)
        alt_result = TexMobject("-\\dfrac{1}{12}").replace(result)

        rationals, other_equals, naturals = TexMobject([
            "|\\mathds{Q}|",
            "=",
            "|\\mathds{N}|"
        ]).scale(2).split()
        infinity = TexMobject("\\infty").scale(2)
        local_mobjects = list(filter(
            lambda m : isinstance(m, Mobject),
            list(locals().values()),
        ))
        for mob in local_mobjects:    
            mob.sort_points(get_norm)

        self.play(ShimmerIn(infinity))
        self.wait()
        self.play(
            ShimmerIn(summand),
            ShimmerIn(equals),
            ShimmerIn(result),
            DelayByOrder(Transform(infinity, sigma))
        )
        self.wait()
        self.play(
            Transform(summand, alt_summand),
            Transform(result, alt_result),
        )
        self.wait()
        self.remove(infinity)
        self.play(*[
            CounterclockwiseTransform(
                Mobject(summand, equals, result, sigma),
                Mobject(rationals, other_equals, naturals)
            )
        ])
        self.wait()
        self.clear()
        self.add(self.bubble)

    def pose_question(self):
        infinity, rightarrow, N = TexMobject([
            "\\infty", "\\rightarrow", "N"
        ]).scale(2).split()
        question_mark = TextMobject("?").scale(2)

        self.add(question_mark)
        self.wait()
        self.play(*[
            ShimmerIn(mob)
            for mob in (infinity, rightarrow, N)
        ] + [
            ApplyMethod(question_mark.next_to, rightarrow, UP),
        ])
        self.wait()



class PostponePhilosophizing(Scene):
    def construct(self):
        abstract, arrow, concrete = TextMobject([
            "Abstract", " $\\rightarrow$ ", "Concrete"
        ]).scale(2).split()

        self.add(abstract, arrow, concrete)
        self.wait()
        self.play(*[
            ApplyMethod(
                word1.replace, word2,
                path_func = path_along_arc(np.pi/2)
            )
            for word1, word2 in it.permutations([abstract, concrete])
        ])
        self.wait()


class GrowHilbertWithName(Scene):
    def construct(self):
        curve = HilbertCurve(order = 1)
        words = TextMobject("``Hilbert Curve''")
        words.to_edge(UP, buff = 0.2)
        self.play(
            ShimmerIn(words),
            Transform(curve, HilbertCurve(order = 2)),
            run_time = 2
        )
        for n in range(3, 8):
            self.play(
                Transform(curve, HilbertCurve(order = n)),
                run_time = 5. /n
            )


class SectionOne(Scene):
    def construct(self):
        self.add(TextMobject("Section 1: Seeing with your ears"))
        self.wait()

class WriteSomeSoftware(Scene):
    pass #Done viea screen capture, written here for organization



class ImageToSound(Scene):
    def construct(self):
        string = Vibrate(color = BLUE_D, run_time = 5)
        picture = ImageMobject("lion", invert = False)
        picture.scale(0.8)
        picture_copy = picture.copy()
        picture.sort_points(get_norm)
        string.mobject.sort_points(lambda p : -get_norm(p))

        self.add(picture)
        self.wait()
        self.play(Transform(
            picture, string.mobject,
            run_time = 3,
            rate_func = rush_into
        ))
        self.remove(picture)
        self.play(string)

        for mob in picture_copy, string.mobject:
            mob.sort_points(lambda p : get_norm(p)%1)

        self.play(Transform(
            string.mobject, picture_copy,
            run_time = 5,
            rate_func = rush_from
        ))

class LinksInDescription(Scene):
    def construct(self):
        text = TextMobject("""
            See links in the description for more on
            sight via sound.
        """)
        self.play(ShimmerIn(text))
        self.play(ShowCreation(Arrow(text, 3*DOWN)))
        self.wait(2)


class ImageDataIsTwoDimensional(Scene):
    def construct(self):
        image = ImageMobject("lion", invert = False)
        image.scale(0.5)
        image.shift(2*LEFT)

        self.add(image)
        for vect, num in zip([DOWN, RIGHT], [1, 2]):
            brace = Brace(image, vect)
            words_mob = TextMobject("Dimension %d"%num)
            words_mob.next_to(image, vect, buff = 1)
            self.play(
                Transform(Point(brace.get_center()), brace),
                ShimmerIn(words_mob), 
                run_time = 2
            )
        self.wait()


class SoundDataIsOneDimensional(Scene):
    def construct(self):
        overtones = 5
        floor = 2*DOWN
        main_string = Vibrate(color = BLUE_D)
        component_strings = [
            Vibrate(
                num_periods = k+1,
                overtones = 1,
                color = color,
                center = 2*DOWN + UP*k
            )
            for k, color in zip(
                list(range(overtones)),
                Color(BLUE_E).range_to(WHITE, overtones)
            )
        ]
        dots = [
            Dot(
                string.mobject.get_center(),
                color = string.mobject.get_color()
            )
            for string in component_strings
        ]

        freq_line = get_freq_line()
        freq_line.shift(floor)
        freq_line.sort_points(get_norm)
        brace = Brace(freq_line, UP)
        words = TextMobject("Range of frequency values")
        words.next_to(brace, UP)


        self.play(*[
            TransformAnimations(
                main_string.copy(),
                string,
                run_time = 5
            )
            for string in component_strings
        ])
        self.clear()
        self.play(*[
            TransformAnimations(
                string,
                Animation(dot)
            )
            for string, dot in zip(component_strings, dots)
        ])
        self.clear()
        self.play(
            ShowCreation(freq_line),
            GrowFromCenter(brace),
            ShimmerIn(words),
            *[
                Transform(
                    dot,
                    dot.copy().scale(2).rotate(-np.pi/2).shift(floor),
                    path_func = path_along_arc(np.pi/3)
                )
                for dot in dots
            ]
        )
        self.wait(0.5)

class GridOfPixels(Scene):
    def construct(self):
        low_res = ImageMobject("low_resolution_lion", invert = False)
        high_res = ImageMobject("Lion", invert = False)
        grid = get_grid().scale(0.8)
        for mob in low_res, high_res:
            mob.replace(grid, stretch = True)
        side_brace = Brace(low_res, LEFT)
        top_brace = Brace(low_res, UP)
        top_words = TextMobject("256 Px", size = "\\normal")
        side_words = top_words.copy().rotate(np.pi/2)
        top_words.next_to(top_brace, UP)
        side_words.next_to(side_brace, LEFT)

        self.add(high_res)
        self.wait()
        self.play(DelayByOrder(Transform(high_res, low_res)))
        self.wait()
        self.play(
            GrowFromCenter(top_brace),
            GrowFromCenter(side_brace),
            ShimmerIn(top_words),
            ShimmerIn(side_words)
        )
        self.wait()
        for mob in grid, high_res:
            mob.sort_points(get_norm)
        self.play(DelayByOrder(Transform(high_res, grid)))
        self.wait()


class ShowFrequencySpace(Scene):
    def construct(self):
        freq_line = get_freq_line()

        self.add(freq_line)
        self.wait()
        for tex, vect in zip(["20 Hz", "20{,}000 Hz"], [LEFT, RIGHT]):
            tex_mob = TextMobject(tex)
            tex_mob.to_edge(vect)
            tex_mob.shift(UP)
            arrow = Arrow(tex_mob, freq_line.get_edge_center(vect))
            self.play(
                ShimmerIn(tex_mob),
                ShowCreation(arrow)
            )
        self.wait()



class AssociatePixelWithFrequency(Scene):
    def construct(self):
        big_grid_dim = 20.
        small_grid_dim = 6.
        big_grid = Grid(64, 64, height = big_grid_dim, width = big_grid_dim)
        big_grid.to_corner(UP+RIGHT, buff = 2)
        small_grid = big_grid.copy()
        small_grid.scale(small_grid_dim/big_grid_dim)
        small_grid.center()
        pixel = MobjectFromRegion(
            region_from_polygon_vertices(*0.2*np.array([
                RIGHT+DOWN,
                RIGHT+UP,
                LEFT+UP,
                LEFT+DOWN
            ]))
        )
        pixel.set_color(WHITE)
        pixel_width = big_grid.width/big_grid.columns
        pixel.set_width(pixel_width)
        pixel.to_corner(UP+RIGHT, buff = 2)
        pixel.shift(5*pixel_width*(2*LEFT+DOWN))

        freq_line = get_freq_line()
        dot = Dot()
        dot.shift(freq_line.get_center() + 2*RIGHT)
        string = Line(LEFT, RIGHT, color = GREEN)
        arrow = Arrow(dot, string.get_center())
        vibration_config = {
            "overtones"      : 1,
            "spatial_period" : 2,
        }
        vibration, loud_vibration, quiet_vibration = [
            Vibrate(string.copy(), amplitude = a, **vibration_config)
            for a in [0.5, 1., 0.25]
        ]

        self.add(small_grid)
        self.wait()
        self.play(
            Transform(small_grid, big_grid)
        )
        self.play(FadeIn(pixel))
        self.wait()
        self.play(
            FadeOut(small_grid),            
            ShowCreation(freq_line)
        )
        self.remove(small_grid)
        self.play(
            Transform(pixel, dot),
        )
        self.wait()
        self.play(ShowCreation(arrow))
        self.play(loud_vibration)
        self.play(
            TransformAnimations(loud_vibration, quiet_vibration),            
            ApplyMethod(dot.fade, 0.9)
        )
        self.clear()
        self.add(freq_line, dot, arrow)
        self.play(quiet_vibration)


class ListenToAllPixels(Scene):
    def construct(self):
        grid = get_grid()
        grid.sort_points(get_norm)        
        freq_line = get_freq_line()
        freq_line.sort_points(lambda p : p[0])
        red, blue = Color(RED), Color(BLUE)
        freq_line.set_color_by_gradient(red, blue)

        colors = [
            Color(rgb = interpolate(
                np.array(red.rgb),
                np.array(blue.rgb),
                alpha
            ))
            for alpha in np.arange(4)/3.
        ]
        string = Line(3*LEFT, 3*RIGHT, color = colors[1])
        vibration = Vibrate(string)
        vibration_copy = vibration.copy()
        vibration_copy.mobject.stroke_width = 1
        sub_vibrations = [
            Vibrate(
                string.copy().shift((n-1)*UP).set_color(colors[n]),
                overtones = 1,
                spatial_period = 6./(n+1),
                temporal_period = 1./(n+1),
                amplitude = 0.5/(n+1)
            )
            for n in range(4)
        ]
        words = TexMobject("&\\vdots \\\\ \\text{thousands }& \\text{of frequencies} \\\\ &\\vdots")
        words.to_edge(UP, buff = 0.1)

        self.add(grid)
        self.wait()
        self.play(DelayByOrder(ApplyMethod(
            grid.set_color_by_gradient, red, blue
        )))
        self.play(Transform(grid, freq_line))
        self.wait()
        self.play(
            ShimmerIn(
                words,
                rate_func = squish_rate_func(smooth, 0, 0.2)
            ),
            *sub_vibrations,
            run_time = 5
        )
        self.play(
            *[
                TransformAnimations(
                    sub_vib, vibration
                )
                for sub_vib in sub_vibrations
            ]+[FadeOut(words)]
        )
        self.clear()
        self.add(freq_line)
        self.play(vibration)


class LayAsideSpeculation(Scene):
    def construct(self):
        words = TextMobject("Would this actually work?")
        grid = get_grid()
        grid.set_width(6)
        grid.to_edge(LEFT)
        freq_line = get_freq_line()
        freq_line.set_width(6)
        freq_line.center().to_edge(RIGHT)
        mapping = Mobject(
            grid, freq_line, Arrow(grid, freq_line)
        )
        mapping.ingest_submobjects()
        lower_left = Point().to_corner(DOWN+LEFT, buff = 0)
        lower_right = Point().to_corner(DOWN+RIGHT, buff = 0)

        self.add(words)
        self.wait()
        self.play(
            Transform(words, lower_right),
            Transform(lower_left, mapping)
        )
        self.wait()


class RandomMapping(Scene):
    def construct(self):
        grid = get_grid()
        grid.set_width(6)
        grid.to_edge(LEFT)
        freq_line = get_freq_line()
        freq_line.set_width(6)
        freq_line.center().to_edge(RIGHT)
        # for mob in grid, freq_line:
        #     indices = np.arange(mob.get_num_points())
        #     random.shuffle(indices)
        #     mob.points = mob.points[indices]
        stars = Stars(stroke_width = grid.stroke_width)

        self.add(grid)
        targets = [stars, freq_line]
        alphas = [not_quite_there(rush_into), rush_from]
        for target, rate_func in zip(targets, alphas):
            self.play(Transform(
                grid, target,
                run_time = 3,
                rate_func = rate_func,
                path_func = path_along_arc(-np.pi/2)
            ))
        self.wait()
        


class DataScrambledAnyway(Scene):
    def construct(self):
        self.add(TextMobject("Data is scrambled anyway, right?"))
        self.wait()
        

class LeverageExistingIntuitions(Scene):
    def construct(self):
        self.add(TextMobject("Leverage existing intuitions"))
        self.wait()




class ThinkInTermsOfReverseMapping(Scene):
    def construct(self):
        grid = get_grid()
        grid.set_width(6)
        grid.to_edge(LEFT)
        freq_line = get_freq_line()
        freq_line.set_width(6)
        freq_line.center().to_edge(RIGHT)
        arrow =  Arrow(grid, freq_line)

        color1, color2 = YELLOW_C, RED
        square_length = 0.01
        dot1 = Dot(color = color1)
        dot1.shift(3*RIGHT)
        dot2 = Dot(color = color2)
        dot2.shift(3.1*RIGHT)
        arrow1 = Arrow(2*RIGHT+UP, dot1, color = color1, buff = 0.1)
        arrow2 = Arrow(4*RIGHT+UP, dot2, color = color2, buff = 0.1)
        dot3, arrow3 = [
            mob.copy().shift(5*LEFT+UP)
            for mob in (dot1, arrow1)
        ]
        dot4, arrow4 = [
            mob.copy().shift(5*LEFT+0.9*UP)
            for mob in (dot2, arrow2)
        ]

        self.add(grid, freq_line, arrow)
        self.wait()
        self.play(ApplyMethod(
            arrow.rotate, np.pi, 
            path_func = clockwise_path()
        ))
        self.wait()
        self.play(ShowCreation(arrow1))
        self.add(dot1)
        self.play(ShowCreation(arrow2))
        self.add(dot2)
        self.wait()
        self.remove(arrow1, arrow2)
        self.play(
            Transform(dot1, dot3),
            Transform(dot2, dot4)
        )
        self.play(
            ApplyMethod(grid.fade, 0.8),
            Animation(Mobject(dot3, dot4))
        )
        self.play(ShowCreation(arrow3))
        self.play(ShowCreation(arrow4))
        self.wait()


class WeaveLineThroughPixels(Scene):
    @staticmethod
    def args_to_string(order):
        return str(order)
        
    @staticmethod
    def string_to_args(order_str):
        return int(order_str)

    def construct(self, order):
        start_color, end_color = RED, GREEN
        curve = HilbertCurve(order = order)
        line = Line(5*LEFT, 5*RIGHT)
        for mob in curve, line:
            mob.set_color_by_gradient(start_color, end_color)
        freq_line = get_freq_line()
        freq_line.replace(line, stretch = True)

        unit = 6./(2**order) #sidelength of pixel
        up = unit*UP
        right = unit*RIGHT
        lower_left = 3*(LEFT+DOWN)
        squares = Mobject(*[
            Square(
                side_length = unit, 
                color = WHITE
            ).shift(x*right+y*up)
            for x, y in it.product(list(range(2**order)), list(range(2**order)))
        ])
        squares.center()
        targets = Mobject()
        for square in squares.submobjects:
            center = square.get_center()
            distances = np.apply_along_axis(
                lambda p : get_norm(p-center),
                1,
                curve.points
            )
            index_along_curve = np.argmin(distances)
            fraction_along_curve = index_along_curve/float(curve.get_num_points())
            target = square.copy().center().scale(0.8/(2**order))
            line_index = int(fraction_along_curve*line.get_num_points())
            target.shift(line.points[line_index])
            targets.add(target)


        self.add(squares)
        self.play(ShowCreation(
            curve,
            run_time = 5, 
            rate_func=linear
        ))
        self.wait()
        self.play(
            Transform(curve, line),
            Transform(squares, targets),
            run_time = 3
        )
        self.wait()
        self.play(ShowCreation(freq_line))
        self.wait()


class WellPlayedGameOfSnake(Scene):
    def construct(self):
        grid = Grid(16, 16).fade()
        snake_curve = SnakeCurve(order = 4)
        words = TextMobject("``Snake Curve''")
        words.next_to(grid, UP)

        self.add(grid)
        self.play(ShowCreation(
            snake_curve,
            run_time = 7, 
            rate_func=linear
        ))
        self.wait()
        self.play(ShimmerIn(words))
        self.wait()


class TellMathematicianFriend(Scene):
    def construct(self):
        mathy, bubble = get_mathy_and_bubble()
        squiggle_mouth = mathy.mouth.copy()
        squiggle_mouth.apply_function(
            lambda x_y_z : (x_y_z[0], x_y_z[1]+0.02*np.sin(50*x_y_z[0]), x_y_z[2])
        )
        bubble.ingest_submobjects()        
        bubble.write("Why not use a Hilbert curve \\textinterrobang ")
        words1 = bubble.content
        bubble.write("So, it's not one curve but an infinite family of curves \\dots")
        words2 = bubble.content
        bubble.write("Well, no, it \\emph{is} just one thing, but I need \\\\ \
                      to tell you about a certain infinite family first.")
        words3 =  bubble.content
        description = TextMobject("Mathematician friend", size = "\\small")
        description.next_to(mathy, buff = 2)
        arrow = Arrow(description, mathy)

        self.add(mathy)
        self.play(
            ShowCreation(arrow),
            ShimmerIn(description)
        )
        self.wait()
        point = Point(bubble.get_tip())
        self.play(
            Transform(point, bubble),
        )
        self.remove(point)
        self.add(bubble)
        self.play(ShimmerIn(words1))
        self.wait()
        self.remove(description, arrow)
        self.play(
            Transform(mathy.mouth, squiggle_mouth),
            ApplyMethod(mathy.arm.wag, 0.2*RIGHT, LEFT),
        )
        self.remove(words1)
        self.add(words2)
        self.wait(2)
        self.remove(words2)
        self.add(words3)
        self.wait(2)
        self.play(
            ApplyPointwiseFunction(
                lambda p : 15*p/get_norm(p),
                bubble
            ),
            ApplyMethod(mathy.shift, 5*(DOWN+LEFT)),
            FadeOut(words3),
            run_time = 3
        )


class Order1PseudoHilbertCurve(Scene):
    def construct(self):
        words, s = TextMobject(["Pseudo-Hilbert Curve", "s"]).split()
        pre_words = TextMobject("Order 1")
        pre_words.next_to(words, LEFT, buff = 0.5)
        s.next_to(words, RIGHT, buff = 0.05, aligned_edge = DOWN)
        cluster = Mobject(pre_words, words, s)
        cluster.center()
        cluster.scale(0.7)
        cluster.to_edge(UP, buff = 0.3)
        cluster.set_color(GREEN)
        grid1 = Grid(1, 1)
        grid2 = Grid(2, 2)
        curve = HilbertCurve(order = 1)

        self.add(words, s)
        self.wait()
        self.play(Transform(
            s, pre_words, 
            path_func = path_along_arc(-np.pi/3)
        ))
        self.wait()
        self.play(ShowCreation(grid1))
        self.wait()
        self.play(ShowCreation(grid2))
        self.wait()
        kwargs = {
            "run_time" : 5,
            "rate_func" : None
        }
        self.play(ShowCreation(curve, **kwargs))
        self.wait()

class Order2PseudoHilbertCurve(Scene):
    def construct(self):
        words = TextMobject("Order 2 Pseudo-Hilbert Curve")
        words.to_edge(UP, buff = 0.3)
        words.set_color(GREEN)
        grid2 = Grid(2, 2)
        grid4 = Grid(4, 4, stroke_width = 2)
        # order_1_curve = HilbertCurve(order = 1)
        # squaggle_curve = order_1_curve.copy().apply_function(
        #     lambda (x, y, z) : (x + np.cos(3*y), y + np.sin(3*x), z)
        # )
        # squaggle_curve.show()
        mini_curves = [
            HilbertCurve(order = 1).scale(0.5).shift(1.5*vect)
            for vect in [
                LEFT+DOWN,
                LEFT+UP,
                RIGHT+UP,
                RIGHT+DOWN
            ]
        ]
        last_curve = mini_curves[0]
        naive_curve = Mobject(last_curve)
        for mini_curve in mini_curves[1:]:
            line = Line(last_curve.points[-1], mini_curve.points[0])
            naive_curve.add(line, mini_curve)
            last_curve = mini_curve
        naive_curve.ingest_submobjects()
        naive_curve.set_color_by_gradient(RED, GREEN)
        order_2_curve = HilbertCurve(order = 2)

        self.add(words, grid2)
        self.wait()
        self.play(ShowCreation(grid4))
        self.play(*[
            ShowCreation(mini_curve)
            for mini_curve in mini_curves
        ])
        self.wait()
        self.play(ShowCreation(naive_curve, run_time = 5))
        self.remove(*mini_curves)
        self.wait()
        self.play(Transform(naive_curve, order_2_curve))
        self.wait()


class Order3PseudoHilbertCurve(Scene):
    def construct(self):
        words = TextMobject("Order 3 Pseudo-Hilbert Curve")
        words.set_color(GREEN)
        words.to_edge(UP)
        grid4 = Mobject(
            Grid(2, 2),
            Grid(4, 4, stroke_width = 2)
        )
        grid8 = Grid(8, 8, stroke_width = 1)
        order_3_curve = HilbertCurve(order = 3)
        mini_curves = [
            HilbertCurve(order = 2).scale(0.5).shift(1.5*vect)
            for vect in [
                LEFT+DOWN,
                LEFT+UP,
                RIGHT+UP,
                RIGHT+DOWN
            ]
        ]

        self.add(words, grid4)
        self.wait()
        self.play(ShowCreation(grid8))
        self.wait()
        self.play(*list(map(GrowFromCenter, mini_curves)))
        self.wait()
        self.clear()
        self.add(words, grid8, *mini_curves)
        self.play(*[
            ApplyMethod(curve.rotate_in_place, np.pi, axis)
            for curve, axis in [
                (mini_curves[0], UP+RIGHT),
                (mini_curves[3], UP+LEFT)
            ]
        ])
        self.play(ShowCreation(order_3_curve, run_time = 5))
        self.wait()

class GrowToOrder8PseudoHilbertCurve(Scene):
    def construct(self):
        self.curve = HilbertCurve(order = 1)
        self.add(self.curve)
        self.wait()
        while self.curve.order < 8:
            self.increase_order()


    def increase_order(self):
        mini_curves = [
            self.curve.copy().scale(0.5).shift(1.5*vect)
            for vect in [
                LEFT+DOWN,
                LEFT+UP,
                RIGHT+UP,
                RIGHT+DOWN
            ]
        ]
        self.remove(self.curve)
        self.play(
            Transform(self.curve.copy(), mini_curves[0])
        )
        self.play(*[
            GrowFromCenter(mini_curve)
            for mini_curve in mini_curves[1:]
        ])
        self.wait()
        self.clear()
        self.add(*mini_curves)
        self.play(*[
            ApplyMethod(curve.rotate_in_place, np.pi, axis)
            for curve, axis in [
                (mini_curves[0], UP+RIGHT),
                (mini_curves[3], UP+LEFT)
            ]
        ])
        self.curve = HilbertCurve(order = self.curve.order+1)
        self.play(ShowCreation(self.curve, run_time = 2))
        self.remove(*mini_curves)
        self.wait()


class UseOrder8(Scene):
    def construct(self):
        mathy, bubble = get_mathy_and_bubble()
        bubble.write("For a 256x256 pixel array...")
        words = TextMobject("Order 8 Pseudo-Hilbert Curve")
        words.set_color(GREEN)
        words.to_edge(UP, buff = 0.3)
        curve = HilbertCurve(order = 8)

        self.add(mathy, bubble)
        self.play(ShimmerIn(bubble.content))
        self.wait()
        self.clear()
        self.add(words)
        self.play(ShowCreation(
            curve, run_time = 7, rate_func=linear
        ))
        self.wait()



class HilbertBetterThanSnakeQ(Scene):
    def construct(self):
        hilbert_curves, snake_curves = [
            [
                CurveClass(order = n)
                for n in range(2, 7)
            ]
            for CurveClass in (HilbertCurve, SnakeCurve)
        ]
        for curve in hilbert_curves+snake_curves:
            curve.scale(0.8)
        for curve in hilbert_curves:
            curve.to_edge(LEFT)
        for curve in snake_curves:
            curve.to_edge(RIGHT)
        greater_than = TexMobject(">")
        question_mark = TextMobject("?")
        question_mark.next_to(greater_than, UP)

        self.add(greater_than, question_mark)
        hilbert_curve = hilbert_curves[0]
        snake_curve = snake_curves[0]
        for new_hc, new_sc in zip(hilbert_curves[1:], snake_curves[1:]):
            self.play(*[
                Transform(hilbert_curve, new_hc),
                Transform(snake_curve, new_sc)
            ])
            self.wait()


class ImagineItWorks(Scene):
    def construct(self):
        self.add(TextMobject("Imagine your project succeeds..."))
        self.wait()


class RandyWithHeadphones(Scene):
    def construct(self):
        headphones = ImageMobject("Headphones.png")
        headphones.scale(0.1)
        headphones.stretch(2, 0)
        headphones.shift(1.2*UP+0.05*LEFT)
        headphones.set_color(GREY)
        randy = Randolph()

        self.add(randy, headphones)
        self.wait(2)
        self.play(ApplyMethod(randy.blink))
        self.wait(4)


class IncreaseResolution(Scene):
    def construct(self):
        grids = [
            Grid(
                2**order, 2**order,
                stroke_width = 1
            ).shift(0.3*DOWN)
            for order in (6, 7)
        ]
        grid = grids[0]
        side_brace = Brace(grid, LEFT)
        top_brace = Brace(grid, UP)
        top_words = TextMobject("256")
        new_top_words = TextMobject("512")
        side_words = top_words.copy()
        new_side_words = new_top_words.copy()
        for words in top_words, new_top_words:
            words.next_to(top_brace, UP, buff = 0.1)
        for words in side_words, new_side_words:
            words.next_to(side_brace, LEFT)

        self.add(grid)
        self.play(
            GrowFromCenter(side_brace),
            GrowFromCenter(top_brace),
            ShimmerIn(top_words),
            ShimmerIn(side_words)
        )
        self.wait()
        self.play(
            DelayByOrder(Transform(*grids)),
            Transform(top_words, new_top_words),
            Transform(side_words, new_side_words)
        )
        self.wait()


class IncreasingResolutionWithSnakeCurve(Scene):
    def construct(self):
        start_curve = SnakeCurve(order = 6)
        end_curve = SnakeCurve(order = 7)
        start_dots, end_dots = [
            Mobject(*[
                Dot(
                    curve.points[int(x*curve.get_num_points())],
                    color = color
                )
                for x, color in [
                    (0.202, GREEN),
                    (0.48, BLUE),
                    (0.7, RED)
                ]
            ])
            for curve in (start_curve, end_curve)
        ]
        self.add(start_curve)
        self.wait()
        self.play(
            ShowCreation(start_dots, run_time = 2),
            ApplyMethod(start_curve.fade)
        )
        end_curve.fade()
        self.play(
            Transform(start_curve, end_curve),
            Transform(start_dots, end_dots)
        )
        self.wait()


class TrackSpecificCurvePoint(Scene):
    CURVE_CLASS = None #Fillin
    def construct(self):
        line = get_freq_line().center()
        line.sort_points(lambda p : p[0])
        curves = [
            self.CURVE_CLASS(order = order)
            for order in range(3, 10)
        ]
        alpha = 0.48
        dot = Dot(UP)
        start_dot = Dot(0.1*LEFT)
        dots = [
            Dot(curve.points[alpha*curve.get_num_points()])
            for curve in curves
        ]

        self.play(ShowCreation(line))
        self.play(Transform(dot, start_dot))
        self.wait()
        for new_dot, curve in zip(dots, curves):
            self.play(
                Transform(line, curve),
                Transform(dot, new_dot)
            )
            self.wait()


class TrackSpecificSnakeCurvePoint(TrackSpecificCurvePoint):
    CURVE_CLASS = SnakeCurve


class NeedToRelearn(Scene):
    def construct(self):
        top_words = TextMobject("Different pixel-frequency association")
        bottom_words = TextMobject("Need to relearn sight-via-sound")
        top_words.shift(UP)
        bottom_words.shift(DOWN)
        arrow = Arrow(top_words, bottom_words)

        self.play(ShimmerIn(top_words))
        self.wait()
        self.play(ShowCreation(arrow))
        self.play(ShimmerIn(bottom_words))
        self.wait()


class TrackSpecificHilbertCurvePoint(TrackSpecificCurvePoint):
    CURVE_CLASS = HilbertCurve



