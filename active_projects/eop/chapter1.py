from big_ol_pile_of_manim_imports import *

COIN_RADIUS = 0.3
COIN_THICKNESS = 0.4 * COIN_RADIUS
COIN_FORESHORTENING = 0.3
COIN_NB_RIDGES = 20
COIN_STROKE_WIDTH = 2

COIN_SEQUENCE_SPACING = 0.1

GRADE_COLOR_1 = COLOR_HEADS = RED
GRADE_COLOR_2 = COLOR_TAILS = BLUE



class PiCreatureCoin(VMobject):
    CONFIG = {
        "diameter": 0.8,
        "thickness": 0.2,
        "nb_ridges" : 7,
        "stroke_color": YELLOW,
        "stroke_width": 3,
        "fill_color": YELLOW,
        "fill_opacity": 0.7,
    }

    def generate_points(self):
        outer_rect = Rectangle(
            width = self.diameter,
            height = self.thickness,
            fill_color  = self.fill_color,
            fill_opacity = self.fill_opacity,
            stroke_color = self.stroke_color,
            stroke_width = 0, #self.stroke_width
        )
        self.add(outer_rect)
        PI = TAU/2
        ridge_angles = np.arange(PI/self.nb_ridges,PI,PI/self.nb_ridges)
        ridge_positions = 0.5 * self.diameter * np.array([
            np.cos(theta) for theta in ridge_angles
        ])
        ridge_color = interpolate_color(BLACK,self.stroke_color,0.5)
        for x in ridge_positions:
            ridge = Line(
                x * RIGHT + 0.5 * self.thickness * DOWN,
                x * RIGHT + 0.5 * self.thickness * UP,
                stroke_color = ridge_color,
                stroke_width = self.stroke_width
            )
            self.add(ridge)



class CoinFlippingPiCreature(PiCreature):

    def __init__(self, **kwargs):

        coin = PiCreatureCoin() # Line(ORIGIN, 0.4 * RIGHT, stroke_width = 15, color = YELLOW)
        PiCreature.__init__(self,**kwargs)
        self.coin = coin
        self.add(coin)
        right_arm = self.get_arm_copies()[1]
        coin.next_to(right_arm, RIGHT+UP, buff = 0)
        coin.shift(0.15 * self.get_width() * LEFT)

    def flip_coin_up(self):
        self.change("raise_right_hand")


class FlipUpAndDown(Animation):
    CONFIG = {
        "vector" : UP,
        "nb_turns" : 1
    }

    def update(self,t):
        self.mobject.shift(4 * t * (1 - t) * self.vector)
        self.mobject.rotate(t * self.nb_turns * TAU)


class FlipCoin(AnimationGroup):
    CONFIG = {
        "rate_func" : there_and_back
    }
    def __init__(self, pi_creature, **kwargs):
        digest_config(self, kwargs)
        pi_creature_motion = ApplyMethod(
            pi_creature.flip_coin_up,
            rate_func = self.rate_func,
            **kwargs
        )
        coin_motion = FlipUpAndDown(
            pi_creature.coin, 
            vector = UP,
            nb_turns = 5,
            rate_func = self.rate_func,
            **kwargs
        )
        AnimationGroup.__init__(self,pi_creature_motion, coin_motion)




class CoinFlippingPiCreatureScene(Scene):

    def construct(self):

        randy = CoinFlippingPiCreature()
        self.add(randy)
        self.play(FlipCoin(randy, run_time = 3))






class UprightCoin(Circle):
# For use in coin sequences
    CONFIG = {
        "radius": COIN_RADIUS,
        "stroke_width": COIN_STROKE_WIDTH,
        "stroke_color": WHITE,
        "fill_opacity": 1,
        "symbol": "\euro"
    }

    def __init__(self, **kwargs):
        Circle.__init__(self,**kwargs)
        self.symbol_mob = TextMobject(self.symbol, stroke_color = self.stroke_color)
        self.symbol_mob.scale_to_fit_height(0.5*self.get_height()).move_to(self)
        self.add(self.symbol_mob)

class UprightHeads(UprightCoin):
    CONFIG = {
        "fill_color": COLOR_HEADS,
        "symbol": "H",
    }


class UprightTails(UprightCoin):
    CONFIG = {
        "fill_color": COLOR_TAILS,
        "symbol": "T",
    }

class CoinSequence(VGroup):
    CONFIG = {
        "sequence": [],
        "spacing": COIN_SEQUENCE_SPACING
    }

    def __init__(self, sequence, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.sequence = sequence
        offset = 0
        for symbol in self.sequence:
            if symbol == "H":
                new_coin = UprightHeads()
            elif symbol == "T":
                new_coin = UprightTails()
            else:
                new_coin = UprightCoin(symbol = symbol)
            new_coin.shift(offset * RIGHT)
            self.add(new_coin)
            offset += self.spacing


class FlatCoin(UprightCoin):
# For use in coin stacks
    CONFIG = {
        "thickness": COIN_THICKNESS,
        "foreshortening": COIN_FORESHORTENING,
        "nb_ridges": COIN_NB_RIDGES
    }

    def __init__(self, **kwargs):
        UprightCoin.__init__(self, **kwargs)
        self.symbol_mob.rotate(TAU/8)
        self.stretch_in_place(self.foreshortening, 1)
        
        # draw the edge
        control_points1 = self.points[12:25].tolist()
        control_points2 = self.copy().shift(self.thickness * DOWN).points[12:25].tolist()
        edge_anchors_and_handles = control_points1
        edge_anchors_and_handles.append(edge_anchors_and_handles[-1] + self.thickness * DOWN)
        edge_anchors_and_handles.append(edge_anchors_and_handles[-1] + self.thickness * UP)
        edge_anchors_and_handles += control_points2[::-1] # list concatenation
        edge_anchors_and_handles.append(edge_anchors_and_handles[-1] + self.thickness * UP)
        edge_anchors_and_handles.append(edge_anchors_and_handles[-1] + self.thickness * DOWN)
        edge_anchors_and_handles.append(control_points1[0])
        #edge_anchors_and_handles = edge_anchors_and_handles[::-1]
        edge = VMobject()
        edge.set_points(edge_anchors_and_handles)
        edge.set_fill(
            color = self.fill_color,
            opacity = self.fill_opacity
        )
        edge.set_stroke(width = self.stroke_width)
        self.add(edge)

        # draw the ridges
        PI = TAU/2
        dtheta = PI/self.nb_ridges
        ridge_angles = np.arange(dtheta,PI,dtheta)
        # add a twist onto each coin
        ridge_angles += np.random.rand(1) * dtheta
        # crop the angles that overshoot on either side
        ridge_angles = ridge_angles[(ridge_angles > 0) * (ridge_angles < PI)]
        ridge_positions = 0.5 * 2 * self.radius * np.array([
            np.cos(theta) for theta in ridge_angles
        ])
        ridge_color = interpolate_color(self.stroke_color, self.fill_color, 0.7)
        for x in ridge_positions:
            y = -(1 - (x/self.radius)**2)**0.5 * self.foreshortening * self.radius
            ridge = Line(
                x * RIGHT + y * UP,
                x * RIGHT + y * UP + self.thickness * DOWN,
                stroke_color = ridge_color,
                stroke_width = self.stroke_width
            )
            self.add(ridge)

        # redraw the unfilled edge to cover the ridge ends
        empty_edge = edge.copy()
        empty_edge.set_fill(opacity = 0)
        self.add(empty_edge)


class FlatHeads(FlatCoin):
    CONFIG = {
        "fill_color": COLOR_HEADS,
        "symbol": "H",
    }
    

class FlatTails(FlatCoin):
    CONFIG = {
        "fill_color": COLOR_TAILS,
        "symbol": "T",
    }
    


class CoinStack(VGroup):
    CONFIG = {
        "coin_thickness": COIN_THICKNESS,
        "size": 5,
        "face": FlatCoin,
    }

    def generate_points(self):
        for n in range(self.size):
            coin = self.face(thickness = self.coin_thickness)
            coin.shift(n * self.coin_thickness * UP)
            self.add(coin)




class HeadsStack(CoinStack):
    CONFIG = { "face": FlatHeads }

class TailsStack(CoinStack):
    CONFIG = { "face": FlatTails }




class TallyStack(VGroup):

    def __init__(self,h,t,**kwargs):
        self.nb_heads = h
        self.nb_tails = t
        VGroup.__init__(self,**kwargs)

    def generate_points(self):
        stack1 = HeadsStack(size = self.nb_heads, coin_thickness = self.coin_thickness)
        stack2 = TailsStack(size = self.nb_tails, coin_thickness = self.coin_thickness)
        stack2.next_to(stack1, RIGHT, buff = SMALL_BUFF)
        self.add(stack1, stack2)



class TestScene(Scene):

    def construct(self):

        #seq = CoinSequence(["H", "T", "T", "H"])
        #self.add(seq)
        
        stack = TallyStack(4,5, coin_thickness = COIN_THICKNESS)
        self.add(stack)

        self.wait()


class AreaSplittingScene(Scene):

    def create_rect_row(self,n):
        rects_group = VGroup()
        for k in range(n+1):
            proportion = float(choose(n,k)) / 2**n
            new_rect = Rectangle(
                width = proportion * WIDTH, 
                height = HEIGHT,
                fill_color = graded_color(n,k),
                fill_opacity = 1
            )
            new_rect.next_to(rects_group,RIGHT,buff = 0)
            rects_group.add(new_rect)
        return rects_group

    def split_rect_row(self,rect_row):

        split_row = VGroup()
        for rect in rect_row.submobjects:
            half = rect.copy().stretch_in_place(0.5,0)
            left_half = half.next_to(rect.get_center(),LEFT,buff = 0)
            right_half = half.copy().next_to(rect.get_center(),RIGHT,buff = 0)
            split_row.add(left_half, right_half)
        return split_row


    def rect_center(self,n,i,j):
        if n < 0:
            raise Exception("wrong indices " + str(n) + ", " + str(i) + ", " + str(j))
        if i < 0 or i > n:
            raise Exception("wrong indices " + str(n) + ", " + str(i) + ", " + str(j))
        if j > choose(n,i) or j < 0:
            raise Exception("wrong indices " + str(n) + ", " + str(i) + ", " + str(j))

        rect = self.brick_array[n][i]
        width = rect.get_width()
        left_x = rect.get_center()[0] - width/2
        spacing = width / choose(n,i)
        x = left_x + (j+0.5) * spacing
        return np.array([x,rect.get_center()[1], rect.get_center()[2]])

    def construct(self):

        # Draw the bricks

        brick_wall = VGroup()
        rect_row = self.create_rect_row(0)
        rect_row.move_to(3.5*UP + 0*HEIGHT*DOWN)
        self.add(rect_row)
        brick_wall.add(rect_row)
        self.brick_array = [[rect_row.submobjects[0]]]

        for n in range(NB_ROWS):
            # copy and shift
            new_rect_row = rect_row.copy()
            self.add(new_rect_row)
            self.play(new_rect_row.shift,HEIGHT * DOWN)
            self.wait()

            #split
            split_row = self.split_rect_row(new_rect_row)
            self.play(FadeIn(split_row))
            self.remove(new_rect_row)
            self.wait()

            # merge
            rect_row = self.create_rect_row(n+1)
            rect_row.move_to(3.5*UP + (n+1)*HEIGHT*DOWN)
            self.play(FadeIn(rect_row))
            brick_wall.add(rect_row)
            self.remove(split_row)
            self.wait()

            # add to brick dict
            rect_array = []
            for rect in rect_row.submobjects:
                rect_array.append(rect)

            self.brick_array.append(rect_array)


        self.play(
            brick_wall.set_fill, {"opacity" : 0.2}
        )


        # Draw the branches

        for (n, rect_row_array) in enumerate(self.brick_array):
            for (i, rect) in enumerate(rect_row_array):
                pos = rect.get_center()
                tally = TallyStack(n - i, i)
                tally.move_to(pos)


                # from the left
                lines = VGroup()

                if i > 0:
                    for j in range(choose(n-1,i-1)):
                        start_pos = self.rect_center(n-1,i-1,j)
                        end_pos = self.rect_center(n,i,j)
                        lines.add(Line(start_pos,end_pos, stroke_color = GRADE_COLOR_2))
                    self.play(
                        LaggedStart(ShowCreation, lines))

                # from the right
                lines = VGroup()

                if i < n:
                    for j in range(choose(n-1,i)):
                        start_pos = self.rect_center(n-1,i,j)
                        if i != 0:
                            end_pos = self.rect_center(n,i,choose(n-1,i-1) + j)
                        else:
                            end_pos = self.rect_center(n,i,j)
                    
                        lines.add(Line(start_pos,end_pos, stroke_color = GRADE_COLOR_1))
                    self.play(
                        LaggedStart(ShowCreation, lines))



                #self.play(FadeIn(tally))






















