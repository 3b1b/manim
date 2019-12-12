#!/usr/bin/env python


import numpy as np
import itertools as it
from copy import deepcopy
import sys

from manimlib.imports import *
from script_wrapper import command_line_create_scene

MOVIE_PREFIX = "counting_in_binary/"
BASE_HAND_FILE = os.path.join(VIDEO_DIR, MOVIE_PREFIX, "Base.mp4")
FORCED_FRAME_DURATION = 0.02
TIME_RANGE = (0, 42)
INITIAL_PADDING = 27
NUM_GOOD_FRAMES = 1223

ALGORITHM_TEXT = [
    """
    \\begin{flushleft}
    Turn up the rightmost finger that is down.
    """, """
    Turn down all fingers to its right.
    \\end{flushleft}
    """
]
FINGER_WORDS = [
    "Thumb",
    "Index Finger",
    "Middle Finger",
    "Ring Finger",
    "Pinky",
]

COUNT_TO_FRAME_NUM = {
    0 : 0,
    1 : 27,
    2 : 76,
    3 : 110,
    4 : 163,
    5 : 189,
    6 : 226,
    7 : 264,
    8 : 318,
    9 : 356,
    10 : 384,
    11 : 423,
    12 : 457,
    13 : 513,
    14 : 528,
    15 : 590,
    16 : 620,
    17 : 671,
    18 : 691,
    19 : 740,
    20 : 781,
    21 : 810,
    22 : 855,
    23 : 881,
    24 : 940,
    25 : 970,
    26 : 1014,
    27 : 1055,
    28 : 1092,
    29 : 1143,
    30 : 1184,
    31 : 1219,
}

COUNT_TO_TIP_POS = {
    0 : [5.0, 0.5, 0.0],
    1 : [3.1, 2.5, 0.0],
    2 : [1.5, 2.3, 0.0],
    3 : [0.7, 2.0, 0.0],
    4 : [0.0, 1.0, 0.0],
}

def finger_tip_power_of_2(finger_no):
    return TexMobject(str(2**finger_no)).shift(COUNT_TO_TIP_POS[finger_no])

class Hand(ImageMobject):
    STARTING_BOTTOM_RIGHT = [4.61111111e+00,  -3.98888889e+00, 9.80454690e-16]
    def __init__(self, num, small = False, **kwargs):
        Mobject2D.__init__(self, **kwargs)
        path = os.path.join(
            VIDEO_DIR, MOVIE_PREFIX, "images", "Hand%d.png"%num
        )
        invert = False
        if not self.read_in_cached_attrs(path, invert):
            ImageMobject.__init__(self, path, invert = invert)
            center = self.get_center()
            self.center()
            self.rotate(np.pi, axis = RIGHT+UP)
            self.sort_points(lambda p : np.log(complex(*p[:2])).imag)
            self.rotate(np.pi, axis = RIGHT+UP)
            self.shift(center)
            self.cache_attrs(path, invert = False)
        self.shift(self.STARTING_BOTTOM_RIGHT-self.get_boundary_point(DOWN+RIGHT))
        if small:
            self.shrink()

    def shrink(self):
        self.scale_in_place(0.8).to_edge(DOWN, buff = 0.0)

    # def set_color_thumb(self, color = "yellow"):
    #     self.set_color(
    #         color = color,
    #         condition = lambda p : p[0] > 4.5 and p[1] > -1.5
    #     )

def get_algorithm():
    return TextMobject(ALGORITHM_TEXT)

def get_finger_colors():
    return list(Color("yellow").range_to("red", 5))

def five_char_binary(num):
    result = bin(num)[2:]
    return (5-len(result))*"0" + result

def read_reversed_binary(string):
    return sum([
        2**count if char == '1' else 0
        for count, char in zip(it.count(), string)
    ])

class LeftHand(Hand):
    def __init__(self, num, **kwargs):
        Hand.__init__(
            self,
            read_reversed_binary(five_char_binary(num)),
            **kwargs
        )
        self.rotate(np.pi, UP)
        self.shift(LEFT)

def get_hand_map(which_hand = "right"):
    if which_hand == "right":
        Class = Hand
    elif which_hand == "left":
        Class = LeftHand
    else:
        print("Bad arg, bro")
        return
    return dict([
        (num, Class(num, small=True))
        for num in range(32)
    ])

class OverHand(SceneFromVideo):
    def construct(self):
        SceneFromVideo.construct(self, BASE_HAND_FILE)
        self.frame_duration = FORCED_FRAME_DURATION
        self.frames = self.frames[:NUM_GOOD_FRAMES]


class SaveEachNumber(OverHand):
    def construct(self):
        OverHand.construct(self)
        for count in COUNT_TO_FRAME_NUM:
            path = os.path.join(
                VIDEO_DIR, MOVIE_PREFIX, "images",
                "Hand%d.png"%count
            )
            Image.fromarray(self.frames[COUNT_TO_FRAME_NUM[count]]).save(path)

    def write_to_movie(self, name = None):
        print("Why bother writing to movie...")

class ShowCounting(OverHand):
    def construct(self):
        OverHand.construct(self)
        self.frames = INITIAL_PADDING*[self.frames[0]] + self.frames
        num_frames = len(self.frames)
        self.frames = [
            disp.paint_mobject(
                self.get_counting_mob(32*count // num_frames),
                frame
            )
            for frame, count in zip(self.frames, it.count())
        ]

    def get_counting_mob(self, count):
        mob = TexMobject(str(count))
        mob.scale(2)
        mob.shift(LEFT)
        mob.to_edge(UP, buff = 0.1)
        return mob


class ShowFrameNum(OverHand):
    def construct(self):
        OverHand.construct(self)
        for frame, count in zip(self.frames, it.count()):
            print(count + "of" + len(self.frames))
            mob = Mobject(*[
                TexMobject(char).shift(0.3*x*RIGHT)
                for char, x, in zip(str(count), it.count())
            ])
            self.frames[count] = disp.paint_mobject(
                mob.to_corner(UP+LEFT),
                frame
            )

class CountTo1023(Scene):
    def construct(self):
        rh_map = get_hand_map("right")
        lh_map = get_hand_map("left")
        def get_num(count):
            return Mobject(*[
                TexMobject(char).shift(0.35*x*RIGHT)
                for char, x, in zip(str(count), it.count())
            ]).center().to_edge(UP)
        self.frames = [
            disp.paint_mobject(Mobject(
                rh_map[count%32], lh_map[count//32], get_num(count)
            ))
            for count in range(2**10)
        ]

class Introduction(Scene):
    def construct(self):
        words = TextMobject("""
            First, let's see how to count
            to 31 on just one hand...
        """)
        hand = Hand(0)
        for mob in words, hand:
            mob.sort_points(lambda p : p[0])

        self.add(words)
        self.wait()
        self.play(DelayByOrder(Transform(words, hand)))
        self.wait()


class ShowReadingRule(Scene):
    def construct(self):
        sample_counts = [6, 17, 27, 31]
        question = TextMobject("""
            How do you recognize what number a given configuration represents?
        """, size = "\\Huge").scale(0.75).to_corner(UP+LEFT)
        answer = TextMobject([
            "Think of each finger as representing a power of 2, ",
            "then add up the numbers represented by the standing fingers."
        ], size = "\\Huge").scale(0.75).to_corner(UP+LEFT).split()
        self.add(question)
        for count in sample_counts:
            hand = Hand(count, small = True)
            self.add(hand)
            self.wait()
            self.remove(hand)
        self.add(hand)
        self.wait()
        self.remove(question)
        self.add(answer[0])
        counts = list(map(finger_tip_power_of_2, list(range(5))))
        for count in counts:
            self.play(SpinInFromNothing(count, run_time = 0.3))
        self.wait()
        self.play(ShimmerIn(answer[1]))
        for count in sample_counts:
            self.clear()
            self.add(*answer)
            self.read_sample(count)

    def read_sample(self, num):
        hand = Hand(num, small = True)
        bool_arr = [c == '1' for c in five_char_binary(num)]
        counts = [4-count for count in range(5) if bool_arr[count]]
        count_mobs = list(map(finger_tip_power_of_2, counts))
        if num in [6, 27]:
            count_mobs[1].shift(0.2*DOWN + 0.2*LEFT)
        if num in [6, 17]:
            hand.shift(0.8*LEFT)
        sum_mobs = TexMobject(
            " + ".join([str(2**c) for c in counts]).split(" ") + ["=%d"%num]
        ).to_corner(UP+RIGHT).split()
        self.add(hand, *count_mobs)
        self.wait()
        self.play(*[
            Transform(count_mobs[n/2], sum_mobs[n])
            if n%2 == 0 and n/2 < len(counts)
            else FadeIn(sum_mobs[n])
            for n in range(len(sum_mobs))
        ])
        self.wait(2.0)


class ShowIncrementRule(Scene):
    def construct(self):
        #First count from 18 to 22
        def to_left(words):
            return "\\begin{flushleft}" + words + "\\end{flushleft}"
        phrases = [
            TextMobject(to_left(words), size = "\\Huge").scale(0.75).to_corner(UP+LEFT)
            for words in [
            "But while you're counting, you don't need to think about powers of 2.",
            "Can you see the pattern for incrementing?",
            "If the thumb is down, turn it up.",
            "If the thumb is up, but the forefinger is down, flip them both.",
            "If the thumb and forefinger are up, but the middle finger is down, flip all three.",
            "In general, flip all of the fingers up to the rightmost one which is down.",
            "After practicing for a minute or two, you're mind starts doing it automatically.",
            "Question: Why does this rule for incrementation work?",
            ]
        ]
        ranges = [
            (0, 14, False),
            (14, 28, False),
            (12, 13, True),
            (29, 31, True),
            (27, 29, True),
            (23, 24, True),
            (14, 20, False),
            (20, 26, False)
        ]
        oh = OverHand()
        for phrase, (start, end, pause) in zip(phrases, ranges):
            if pause:
                self.background = oh.frames[COUNT_TO_FRAME_NUM[start]]
                self.add(phrase)
                self.play(ShimmerIn(self.get_arrow_set(start)))
                self.wait()
                self.clear()
                self.reset_background()
            self.frames += [
                disp.paint_mobject(phrase, frame)
                for frame in oh.frames[COUNT_TO_FRAME_NUM[start]:COUNT_TO_FRAME_NUM[end]]
            ]
            if pause:
                self.frames += [self.frames[-1]]*int(1.0/self.frame_duration)

    def get_arrow_set(self, num):
        arrow = TexMobject("\\downarrow", size = "\\Huge")
        arrow.set_color("green")
        arrow.shift(-arrow.get_bottom())
        if num == 12:
            tips = [(4, 1, 0)]
        elif num == 29:
            tips = [
                (6, 1.5, 0),
                (3, 1.5, 0),
            ]
        elif num == 27:
            tips = [
                (5.5, 1.5, 0),
                (2.75, 3.5, 0),
                (2, 1.0, 0),
            ]
        elif num == 23:
            tips = [
                (6, 1, 0),
                (3.25, 3.5, 0),
                (2.25, 3.5, 0),
                (1.5, 0.75, 0),
            ]
        return Mobject(*[
            deepcopy(arrow).shift(tip)
            for tip in tips
        ])


class MindFindsShortcuts(Scene):
    def construct(self):
        words1 = TextMobject("""
            Before long, your mind starts to recognize certain
            patterns without needing to perform the addition.
        """, size = "\\Huge").scale(0.75).to_corner(LEFT+UP)
        words2 = TextMobject("""
            Which makes it faster to recognize other patterns...
        """, size = "\\Huge").scale(0.75).to_corner(LEFT+UP)

        hand = Hand(7).scale(0.5).center().shift(DOWN+2*LEFT)
        sum421 = TexMobject("4+2+1").shift(DOWN+2*RIGHT)
        seven = TexMobject("7").shift(DOWN+6*RIGHT)
        compound = Mobject(
            Arrow(hand, sum421),
            sum421,
            Arrow(sum421, seven)
        )
        self.add(
            words1,
            hand,
            compound,
            seven
        )
        self.wait()
        self.play(
            Transform(compound, Arrow(hand, seven).set_color("yellow")),
            ShimmerIn(TextMobject("Directly recognize").shift(1.5*DOWN+2*RIGHT))
        )
        self.wait()

        self.clear()
        hands = dict([
            (num, Hand(num).center().scale(0.5).shift(DOWN))
            for num in [23, 16, 7]
        ])
        hands[23].shift(5*LEFT)
        hands[16].shift(LEFT)
        hands[7].shift(3*RIGHT)
        for num in 7, 16:
            hands[num].add(TexMobject(str(num)).shift(hands[num].get_top()+0.5*UP))
        plus = TexMobject("+").shift(DOWN + RIGHT)
        equals = TexMobject("=").shift(DOWN + 2.5*LEFT)
        equals23 = TexMobject("=23").shift(DOWN + 5.5*RIGHT)

        self.add(words2, hands[23])
        self.wait()
        self.play(
            Transform(
                deepcopy(hands[16]).set_color("black").center().shift(hands[23].get_center()),
                hands[16]
            ),
            Transform(
                deepcopy(hands[7]).set_color("black").center().shift(hands[23].get_center()),
                hands[7]
            ),
            Animation(hands[23]),
            FadeIn(equals),
            FadeIn(plus)
        )
        self.wait()
        self.play(ShimmerIn(equals23))
        self.wait()


class CountingExampleSentence(ShowCounting):
    def construct(self):
        words = "As an example, this is me counting the number of words in this sentence on just one hand!"
        self.words = TextMobject(words.split(), size = "\\Huge").scale(0.7).to_corner(UP+LEFT, buff = 0.25).split()
        ShowCounting.construct(self)

    def get_counting_mob(self, num):
        return Mobject(*self.words[:num])

class FinishCountingExampleSentence(Scene):
    def construct(self):
        words = "As an example, this is me counting the number of words in this sentence on just one hand!"
        words = TextMobject(words, size = "\\Huge").scale(0.7).to_corner(UP+LEFT, buff = 0.25)
        hand = Hand(18)
        sixteen = TexMobject("16").shift([0, 2.25, 0])
        two = TexMobject("2").shift([3, 3.65, 0])
        eightteen = TexMobject("18").shift([1.5, 2.5, 0])
        eightteen.sort_points()
        comp = Mobject(sixteen, two)
        self.add(hand, comp, words)
        self.wait()
        self.play(Transform(comp, eightteen))
        self.wait()

class Question(Scene):
    def construct(self):
        self.add(TextMobject("Left to ponder: Why does this rule for incrementing work?"))


class TwoHandStatement(Scene):
    def construct(self):
        self.add(TextMobject(
            "With 10 fingers, you can count up to $2^{10} - 1 = 1023$..."
        ))

class WithToes(Scene):
    def construct(self):
        words = TextMobject([
            "If you were dexterous enough to use your toes as well,",
            "you could count to 1,048,575"
        ]).split()
        self.add(words[0])
        self.wait()
        self.play(ShimmerIn(words[1]))
        self.wait()


if __name__ == "__main__":
    command_line_create_scene(MOVIE_PREFIX)
