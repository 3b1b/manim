from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from scene import Scene
from camera import Camera, ShadingCamera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

from eoc.graph_scene import GraphScene

class Jewel(VMobject):
    CONFIG = {
        "color" : WHITE,
        "fill_opacity" : 0.75,
        "stroke_width" : 0,
        "propogate_style_to_family" : True,
        "height" : 0.5,
        "num_equator_points" : 5,
        "sun_vect" : OUT+LEFT+UP,
    }
    def generate_points(self):
        for vect in OUT, IN:
            compass_vects = list(compass_directions(self.num_equator_points))
            if vect is IN:
                compass_vects.reverse()
            for vect_pair in adjascent_pairs(compass_vects):
                self.add(Polygon(vect, *vect_pair))
        self.scale_to_fit_height(self.height)
        self.rotate(-np.pi/2-np.pi/24, RIGHT)        
        self.rotate(-np.pi/12, UP)
        self.submobjects.sort(lambda m1, m2 : cmp(-m1.get_center()[2], -m2.get_center()[2]))
        return self

################

class CheckOutMathologer(PiCreatureScene):
    CONFIG = {
        "logo_height" : 1.5,
        "screen_height" : 5
    }
    def construct(self):
        logo = ImageMobject("Mathologer_logo")
        logo.scale_to_fit_height(self.logo_height)
        logo.to_corner(UP+LEFT)
        name = TextMobject("Mathologer")
        name.next_to(logo, RIGHT)

        rect = Rectangle(height = 9, width = 16)
        rect.scale_to_fit_height(self.screen_height)
        rect.next_to(logo, DOWN)
        rect.to_edge(LEFT)

        logo.save_state()
        logo.shift(DOWN)
        logo.highlight(BLACK)
        self.play(
            logo.restore,
            self.pi_creature.change_mode, "hooray",
        )
        self.play(
            ShowCreation(rect),
            Write(name)
        )
        self.dither(2)
        self.change_mode("happy")
        self.dither(2)

class IntroduceStolenNecklaceProblem(Scene):
    CONFIG = {
        "camera_class" : ShadingCamera,
        "jewel_colors" : [BLUE, GREEN, WHITE, RED],
        "num_per_jewel" : [8, 10, 4, 6],
        "num_shuffles" : 1,
        "random_seed" : 2,
        "forced_binary_choices" : (0, 1, 0, 1, 0),
        "show_matching_after_divvying" : True,
    }
    def construct(self):
        random.seed(self.random_seed)
        self.add_thieves()
        self.write_title()
        self.introduce_necklace()
        self.divvy_by_cutting_all()
        self.divvy_with_n_cuts()
        self.shuffle_jewels(self.necklace.jewels)
        self.divvy_with_n_cuts()

    def add_thieves(self):
        thieves = VGroup(
            Randolph(),
            Mortimer()
        )
        thieves.arrange_submobjects(RIGHT, buff = 4*LARGE_BUFF)
        thieves.to_edge(DOWN)
        thieves[0].make_eye_contact(thieves[1])

        self.add(thieves)
        self.thieves = thieves

    def write_title(self):
        title = TextMobject("Stolen necklace problem")
        title.to_edge(UP)
        self.play(
            Write(title),
            *[
                ApplyMethod(pi.look_at, title)
                for pi in self.thieves
            ]
        )
        self.title = title

    def introduce_necklace(self):
        necklace = self.get_necklace()
        jewels = necklace.jewels
        jewel_types = self.get_jewels_organized_by_type(jewels)

        enumeration_labels = VGroup()
        for jewel_type in jewel_types:
            num_mob = TexMobject(str(len(jewel_type)))
            jewel_copy = jewel_type[0].copy().scale(2)
            jewel_copy.next_to(num_mob)
            label = VGroup(num_mob, jewel_copy)
            enumeration_labels.add(label)
        enumeration_labels.arrange_submobjects(RIGHT, buff = LARGE_BUFF)
        enumeration_labels.to_edge(UP)

        self.play(
            FadeIn(
                necklace,
                submobject_mode = "lagged_start",
                run_time = 3
            ),
            *it.chain(*[
                [pi.change_mode, "conniving", pi.look_at, necklace]
                for pi in self.thieves
            ])
        )
        self.play(*[
            ApplyMethod(
                jewel.rotate_in_place, np.pi/6, UP, 
                rate_func = there_and_back
            )
            for jewel in jewels
        ])
        self.play(Blink(self.thieves[0]))
        self.dither()
        for x in range(self.num_shuffles):
            self.shuffle_jewels(jewels)
        self.play(FadeOut(self.title))
        for jewel_type, label in zip(jewel_types, enumeration_labels):
            jewel_type.submobjects.sort(lambda m1, m2: cmp(m1.get_center()[0], m2.get_center()[0]))
            jewel_type.save_state()
            jewel_type.generate_target()
            jewel_type.target.arrange_submobjects()
            jewel_type.target.scale(2)
            jewel_type.target.move_to(2*UP)
            self.play(
                MoveToTarget(jewel_type), 
                Write(label)
            )
            self.play(jewel_type.restore)
        self.play(Blink(self.thieves[1]))

        self.enumeration_labels = enumeration_labels
        self.jewel_types = jewel_types

    def divvy_by_cutting_all(self):
        enumeration_labels = self.enumeration_labels
        necklace = self.necklace
        jewel_types = self.jewel_types
        thieves = self.thieves

        both_half_labels = VGroup()
        for thief, vect in zip(self.thieves, [LEFT, RIGHT]):
            half_labels = VGroup()
            for label in enumeration_labels:
                tex, jewel = label
                num = int(tex.get_tex_string())
                half_label = VGroup(
                    TexMobject(str(num/2)),
                    jewel.copy()
                )
                half_label.arrange_submobjects()
                half_labels.add(half_label)
            half_labels.arrange_submobjects(DOWN)
            half_labels.scale_to_fit_height(thief.get_height())
            half_labels.next_to(
                thief, vect, 
                buff = MED_LARGE_BUFF,
                aligned_edge = DOWN
            )
            both_half_labels.add(half_labels)

        for half_labels in both_half_labels:
            self.play(ReplacementTransform(
                enumeration_labels.copy(), 
                half_labels
            ))
        self.play(*[ApplyMethod(pi.change_mode, "pondering") for pi in thieves])
        self.dither()

        for type_index, jewel_type in enumerate(jewel_types):
            jewel_type.save_state()
            jewel_type_copy = jewel_type.copy()
            n_jewels = len(jewel_type)
            halves = [
                VGroup(*jewel_type_copy[:n_jewels/2]),
                VGroup(*jewel_type_copy[n_jewels/2:]),
            ]
            for half, thief, vect in zip(halves, thieves, [RIGHT, LEFT]):
                half.arrange_submobjects(DOWN)
                half.next_to(
                    thief, vect, 
                    buff = SMALL_BUFF + type_index*half.get_width(),
                    aligned_edge = DOWN
                )
            self.play(
                Transform(jewel_type, jewel_type_copy),
                *[
                    ApplyMethod(thief.look_at, jewel_type_copy)
                    for thief in thieves
                ]
            )
        self.play(*it.chain(*[
            [thief.change_mode, "happy", thief.look_at, necklace]
            for thief in thieves
        ]))
        self.dither()
        self.play(*[
            jewel_type.restore
            for jewel_type in jewel_types
        ])
        self.play(*it.chain(*[
            [thief.change_mode, "confused", thief.look_at, necklace]
            for thief in thieves
        ]))

    def divvy_with_n_cuts(self):
        necklace = self.necklace
        jewel_types = self.jewel_types
        thieves = self.thieves
        jewels = sorted(
            necklace.jewels, 
            lambda m1, m2 : cmp(m1.get_center()[0], m2.get_center()[0])
        )
        slice_indices, binary_choices = self.find_slice_indices(jewels, jewel_types)
        subgroups = [
            VGroup(*jewels[i1:i2])
            for i1, i2 in zip(slice_indices, slice_indices[1:])
        ]
        buff = (jewels[1].get_left()[0]-jewels[0].get_right()[0])/2
        v_lines = VGroup(*[
            DashedLine(UP, DOWN).next_to(group, RIGHT, buff = buff)
            for group in subgroups[:-1]
        ])
        strand_groups = [VGroup(), VGroup()]
        for group, choice in zip(subgroups, binary_choices):
            strand = Line(
                group[0].get_center(), group[-1].get_center(),
                color = necklace.line.get_color()
            )
            strand.add(*group)
            strand_groups[choice].add(strand)
            self.add(strand)

        self.play(ShowCreation(v_lines))
        self.play(
            FadeOut(necklace.line),
            *it.chain(*[
                map(Animation, group)
                for group in strand_groups
            ])
        )
        for group in strand_groups:
            group.save_state()
        self.play(
            strand_groups[0].shift, UP/2.,
            strand_groups[1].shift, DOWN/2.,
        )
        self.play(*it.chain(*[
            [thief.change_mode, "happy", thief.look_at, self.necklace]
            for thief in thieves
        ]))
        self.play(Blink(thieves[1]))

        for group in strand_groups:
            box = Rectangle(
                width = group.get_width()+2*SMALL_BUFF,
                height = group.get_height()+2*SMALL_BUFF,
                stroke_width = 0,
                fill_color = YELLOW,
                fill_opacity = 0.3,
            )
            box.move_to(group)
            self.play(FadeIn(box))
            self.dither()
            self.play(FadeOut(box))

        self.dither()
        if self.show_matching_after_divvying:
            for jewel_type in jewel_types:
                self.play(
                    *it.chain(*[
                        [
                            jewel.scale_in_place, 2,
                            jewel.rotate_in_place, np.pi/12, UP,
                        ]
                        for jewel in jewel_type
                    ]),
                    rate_func = there_and_back,
                    run_time = 2
                )
            self.dither()
        self.play(
            FadeOut(v_lines),
            FadeIn(necklace.line),
            *[
                group.restore for group in strand_groups
            ]
        )
        self.remove(*strand_groups)
        self.add(necklace)

    ########

    def get_necklace(self):
        colors = reduce(op.add, [
            num*[color]
            for num, color in zip(self.num_per_jewel, self.jewel_colors)
        ])
        jewels = VGroup(*[
            Jewel(color = color)
            for color in colors
        ])
        jewels.arrange_submobjects()
        jewels.scale_to_fit_width(2*SPACE_WIDTH-1)
        jewels.center().shift(UP)

        necklace = VGroup()
        necklace.line = Line(
            jewels[0].get_center(), 
            jewels[-1].get_center(), 
            color = GREY
        )
        necklace.jewels = jewels
        necklace.add(necklace.line, *jewels)

        self.necklace = necklace
        return necklace

    def get_jewels_organized_by_type(self, jewels):
        return [
            VGroup(*filter(lambda m : m.get_color() == color, jewels))
            for color in map(Color, self.jewel_colors)
        ]

    def shuffle_jewels(self, jewels, run_time = 2, path_arc = np.pi/2, **kwargs):
        shuffled_indices = range(len(jewels))
        random.shuffle(shuffled_indices)
        target_group = VGroup(*[
            jewel.copy().move_to(jewels[shuffled_indices[i]])
            for i, jewel in enumerate(jewels)
        ])
        self.play(Transform(
            jewels, target_group,
            run_time = run_time,            
            path_arc = path_arc,
            **kwargs
        ))

    def find_slice_indices(self, jewels, jewel_types):

        def jewel_to_type_number(jewel):
            for i, jewel_type in enumerate(jewel_types):
                if jewel in jewel_type:
                    return i
            raise Exception("Not in any jewel_types")
        type_numbers = map(jewel_to_type_number, jewels)

        n_types = len(jewel_types)
        for slice_indices in it.combinations(range(1, len(jewels)), n_types):
            slice_indices = [0] + list(slice_indices) + [len(jewels)]
            if self.forced_binary_choices is not None:
                all_binary_choices = [self.forced_binary_choices]
            else:
                all_binary_choices = it.product(*[range(2)]*(n_types+1))
            for binary_choices in all_binary_choices:
                subsets = [
                    type_numbers[i1:i2]
                    for i1, i2 in zip(slice_indices, slice_indices[1:])
                ]
                left_sets, right_sets = [
                    [
                        subset
                        for subset, index in zip(subsets, binary_choices)
                        if index == target_index
                    ]
                    for target_index in range(2)
                ]
                flat_left_set = np.array(list(it.chain(*left_sets)))
                flat_right_set = np.array(list(it.chain(*right_sets)))


                match_array = [
                    sum(flat_left_set == n) == sum(flat_right_set == n)
                    for n in range(n_types)
                ]
                if np.all(match_array):
                    return slice_indices, binary_choices
        raise Exception("No fair division found")

class FiveJewelCase(IntroduceStolenNecklaceProblem):
    CONFIG = {
        "jewel_colors" : [BLUE, GREEN, WHITE, RED, YELLOW],
        "num_per_jewel" : [6, 4, 4, 2, 8],
        "forced_binary_choices" : (0, 1, 0, 1, 0, 1),
    }
    def construct(self):
        random.seed(self.random_seed)
        self.add(self.get_necklace())
        jewels = self.necklace.jewels
        self.shuffle_jewels(jewels, run_time = 0)
        self.jewel_types = self.get_jewels_organized_by_type(jewels)     
        self.add_title()
        self.add_thieves()
        for thief in self.thieves:
            ApplyMethod(thief.change_mode, "pondering").update(1)
            thief.look_at(self.necklace)
        self.divvy_with_n_cuts()

    def add_title(self):
        n_cuts = len(self.jewel_colors)
        title = TextMobject(
            "%d jewel types, %d cuts"%(n_cuts, n_cuts)
        )
        title.to_edge(UP)
        self.add(title)

class SixJewelCase(FiveJewelCase):
    CONFIG = {
        "jewel_colors" : [BLUE, GREEN, WHITE, RED, YELLOW, MAROON_B],
        "num_per_jewel" : [6, 4, 4, 2, 2, 6],
        "forced_binary_choices" : (0, 1, 0, 1, 0, 1, 0),
    }

class DiscussApplicability(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            Minize sharding,
            allocate resources evenly
        """)
        self.change_student_modes(*["pondering"]*3)
        self.dither(2)

class ThreeJewelCase(FiveJewelCase):
    CONFIG = {
        "jewel_colors" : [BLUE, GREEN, WHITE],
        "num_per_jewel" : [6, 4, 8],
        "forced_binary_choices" : (0, 1, 0, 1),
    }

class RepeatedShuffling(IntroduceStolenNecklaceProblem):
    CONFIG = {
        "num_shuffles" : 5,
        "random_seed" : 3,
        "show_matching_after_divvying" : False,
    }
    def construct(self):
        random.seed(self.random_seed)
        self.add(self.get_necklace())
        jewels = self.necklace.jewels
        self.jewel_types = self.get_jewels_organized_by_type(jewels)     
        self.add_thieves()
        for thief in self.thieves:
            ApplyMethod(thief.change_mode, "pondering").update(1)
            thief.look_at(self.necklace)

        for x in range(self.num_shuffles):
            self.shuffle_jewels(jewels)
            self.divvy_with_n_cuts()

class NowForTheTopology(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("Now for the \\\\ topology")
        self.change_student_modes(*["hooray"]*3)
        self.dither(3)

class ExternallyAnimatedScene(Scene):
    def construct(self):
        raise Exception("Don't actually run this class.")

class SphereOntoPlaneIn3D(ExternallyAnimatedScene):
    pass

class DiscontinuousSphereOntoPlaneIn3D(ExternallyAnimatedScene):
    pass

class WriteWords(Scene):
    CONFIG = {
        "words" : "",
        "color" : WHITE,
    }
    def construct(self):
        words = TextMobject(self.words)
        words.highlight(self.color)
        words.scale_to_fit_width(2*SPACE_WIDTH-1)
        words.to_edge(DOWN)
        self.play(Write(words))
        self.dither(2)

class WriteNotAllowed(WriteWords):
    CONFIG = {
        "words" : "Not allowed",
        "color" : RED,
    }

class NonAntipodalCollisionIn3D(ExternallyAnimatedScene):
    pass

class AntipodalCollisionIn3D(ExternallyAnimatedScene):
    pass

class WriteBorsukUlam(WriteWords):
    CONFIG = {
        "words" : "Borsuk-Ulam Theorem",
    }

class WriteAntipodal(WriteWords):
    CONFIG = {
        "words" : "``Antipodal''",
        "color" : MAROON_B,
    }

class ProjectOntoEquatorIn3D(ExternallyAnimatedScene):
    pass

class ProjectOntoEquatorWithPolesIn3D(ExternallyAnimatedScene):
    pass

class ProjectAntipodalNonCollisionIn3D(ExternallyAnimatedScene):
    pass

class ShearThenProjectnOntoEquatorPolesMissIn3D(ExternallyAnimatedScene):
    pass

class ShearThenProjectnOntoEquatorAntipodalCollisionIn3D(ExternallyAnimatedScene):
    pass

class ClassicExample(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("The classic example...")
        self.change_student_modes(*["happy"]*3)
        self.dither(2)


class AntipodalEarthPoints(ExternallyAnimatedScene):
    pass

class RotatingEarth(ExternallyAnimatedScene):
    pass

class TemperaturePressurePlane(GraphScene):
    CONFIG = {
        "x_labeled_nums" : [],
        "y_labeled_nums" : [],
        "x_axis_label" : "Temperature",
        "y_axis_label" : "Pressure",
        "graph_origin" : 2.5*DOWN + 2*LEFT,
        "corner_square_width" : 4,
        "example_point_coords" : (2, 5),
    }
    def construct(self):
        self.setup_axes()
        self.draw_corner_square()
        self.add_example_coordinates()

    def draw_corner_square(self):
        square = Square(
            side_length = self.corner_square_width,
            stroke_color = WHITE,
            stroke_width = 2
        )
        square.to_corner(UP+LEFT, buff = 0)

        arrow = Arrow(
            square.get_right(), 
            self.coords_to_point(*self.example_point_coords)
        )

        self.play(ShowCreation(square))
        self.play(ShowCreation(arrow))


    def add_example_coordinates(self):
        dot = Dot(self.coords_to_point(*self.example_point_coords))
        dot.highlight(YELLOW)
        tex = TexMobject("(25^\\circ\\text{C}, 101 \\text{ kPa})")
        tex.next_to(dot, UP+RIGHT, buff = SMALL_BUFF)

        self.play(ShowCreation(dot))
        self.play(Write(tex))
        self.dither()








































