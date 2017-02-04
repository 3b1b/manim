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

class Necklace(VMobject):
    CONFIG = {
        "width" : 2*SPACE_WIDTH - 1,
        "jewel_buff" : MED_SMALL_BUFF,
        "chain_color" : GREY,
        "default_colors" : [(4, BLUE), (6, WHITE), (4, GREEN)]
    }
    def __init__(self, *colors, **kwargs):
        digest_config(self, kwargs, locals())
        if len(colors) == 0:
            self.colors = self.get_default_colors()
        VMobject.__init__(self, **kwargs)

    def get_default_colors(self):
        result = list(it.chain(*[
            num*[color]
            for num, color in self.default_colors
        ]))
        random.shuffle(result)
        return result

    def generate_points(self):
        jewels = VGroup(*[
            Jewel(color = color)
            for color in self.colors
        ])
        jewels.arrange_submobjects(buff = self.jewel_buff)
        jewels.scale_to_fit_width(self.width)
        jewels.center()

        chain = Line(
            jewels[0].get_center(), 
            jewels[-1].get_center(), 
            color = self.chain_color,
        )
        self.add(chain, *jewels)
        self.chain = chain
        self.jewels = jewels

################

class CheckOutMathologer(PiCreatureScene):
    CONFIG = {
        "logo_height" : 1.5,
        "screen_height" : 5,
        "channel_name" : "Mathologer",
        "logo_file" : "mathologer_logo",
        "logo_color" : None,
    }
    def construct(self):
        logo = ImageMobject(self.logo_file)
        logo.scale_to_fit_height(self.logo_height)
        logo.to_corner(UP+LEFT)
        if self.logo_color is not None:
            logo.highlight(self.logo_color)
            logo.stroke_width = 1
        name = TextMobject(self.channel_name)
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
        "necklace_center" : UP,
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
                color = necklace.chain.get_color()
            )
            strand.add(*group)
            strand_groups[choice].add(strand)
            self.add(strand)

        self.play(ShowCreation(v_lines))
        self.play(
            FadeOut(necklace.chain),
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
            FadeIn(necklace.chain),
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
        self.necklace = Necklace(*colors)
        self.necklace.shift(self.necklace_center)
        return self.necklace

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
        self.wander_continuously()

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
        self.play(FadeOut(tex))

    def wander_continuously(self):
        path = VMobject().set_points_smoothly([
            ORIGIN, 2*UP+RIGHT, 2*DOWN+RIGHT,
            5*RIGHT, 4*RIGHT+UP, 3*RIGHT+2*DOWN,
            DOWN+LEFT, 2*RIGHT
        ])
        point = self.coords_to_point(*self.example_point_coords)
        path.shift(point)

        path.highlight(GREEN)

        self.play(ShowCreation(path, run_time = 10, rate_func = None))
        self.dither()

class AlternateSphereSquishing(ExternallyAnimatedScene):
    pass

class AlternateAntipodalCollision(ExternallyAnimatedScene):
    pass

class AskWhy(TeacherStudentsScene):
    def construct(self):
        self.student_says("But...why?")
        self.change_student_modes("pondering", None, "thinking")
        self.play(self.get_teacher().change_mode, "happy")
        self.dither(3)

class PointOutVSauce(CheckOutMathologer):
    CONFIG = {
        "channel_name" : "",
        "logo_file" : "Vsauce_logo",
        "logo_height" : 1,
        "logo_color" : GREY,
    }

class WalkEquatorPostTransform(GraphScene):
    CONFIG = {
        "x_labeled_nums" : [],
        "y_labeled_nums" : [],
        "graph_origin" : 2.5*DOWN + 2*LEFT,
        "curved_arrow_color" : WHITE,
        "curved_arrow_radius" : 3,
        "num_great_arcs" : 10,
    }
    def construct(self):
        self.setup_axes()
        self.add_curved_arrow()
        self.great_arc_images = self.get_great_arc_images()

        self.walk_equator()
        self.walk_tilted_equator()
        self.draw_transverse_curve()
        self.walk_transverse_curve()

    def add_curved_arrow(self):
        arc = Arc(
            start_angle = 2*np.pi/3, angle = -np.pi/2, 
            radius = self.curved_arrow_radius,
            color = self.curved_arrow_color
        )
        arc.add_tip()
        arc.move_to(self.coords_to_point(0, 7))

        self.add(arc)

    def walk_equator(self):
        equator = self.great_arc_images[0]
        dots = VGroup(Dot(), Dot())
        dots.highlight(MAROON_B)
        dot_movement = self.get_arc_walk_dot_movement(equator, dots)
        dot_movement.update(0)

        self.play(ShowCreation(equator, run_time = 3))
        self.play(FadeIn(dots[0]))
        dots[1].set_fill(opacity = 0)
        self.play(dot_movement)
        self.play(dots[1].set_fill, None, 1)
        self.play(dot_movement)
        self.play(dot_movement)

        proportion = equator.collision_point_proportion
        self.play(self.get_arc_walk_dot_movement(
            equator, dots,
            rate_func = lambda t : 2*proportion*smooth(t)
        ))
        v_line = DashedLine(SPACE_HEIGHT*UP, SPACE_HEIGHT*DOWN)
        v_line.shift(dots.get_center()[0]*RIGHT)
        self.play(ShowCreation(v_line))
        self.dither()
        self.play(FadeOut(v_line))

        dots.save_state()
        equator.save_state()
        self.play(
            equator.fade,
            dots.fade
        )

        self.first_dots = dots

    def walk_tilted_equator(self):
        equator = self.great_arc_images[0]
        tilted_eq = self.great_arc_images[1]

        dots = VGroup(Dot(), Dot())
        dots.highlight(MAROON_B)
        dot_movement = self.get_arc_walk_dot_movement(tilted_eq, dots)
        dot_movement.update(0)

        self.play(ReplacementTransform(equator.copy(), tilted_eq))
        self.dither()
        self.play(FadeIn(dots))
        self.play(dot_movement)

        proportion = tilted_eq.collision_point_proportion
        self.play(self.get_arc_walk_dot_movement(
            tilted_eq, dots,
            rate_func = lambda t : 2*proportion*smooth(t)
        ))
        v_line = DashedLine(SPACE_HEIGHT*UP, SPACE_HEIGHT*DOWN)
        v_line.shift(dots.get_center()[0]*RIGHT)
        self.play(ShowCreation(v_line))
        self.dither()
        self.play(FadeOut(v_line))
        self.play(*map(FadeOut, [tilted_eq, dots]))

    def draw_transverse_curve(self):
        transverse_curve = self.get_transverse_curve(self.great_arc_images)
        dots = self.first_dots
        equator = self.great_arc_images[0]

        self.play(dots.restore)
        equator.restore()
        self.great_arc_images.fade()

        target_arcs = list(self.great_arc_images[1:])
        target_dots = []
        for arc in target_arcs:
            new_dots = dots.copy()
            for dot, point in zip(new_dots, arc.x_collision_points):
                dot.move_to(point)
            target_dots.append(new_dots)

        alt_eq = equator.copy()
        alt_eq.points = np.array(list(reversed(alt_eq.points)))
        alt_dots = dots.copy()
        alt_dots.submobjects.reverse()
        target_arcs += [alt_eq, alt_eq.copy()]
        target_dots += [alt_dots, alt_dots.copy()]

        equator_transform = Succession(*[
            Transform(equator, arc, rate_func = None)
            for arc in target_arcs
        ])
        dots_transform = Succession(*[
            Transform(dots, target, rate_func = None)
            for target in target_dots
        ])

        self.play(
            ShowCreation(transverse_curve, submobject_mode = "all_at_once"),
            equator_transform,
            dots_transform,
            run_time = 10,
            rate_func = None,
        )
        self.dither(2)

    def walk_transverse_curve(self):
        transverse_curve = self.get_transverse_curve(self.great_arc_images)
        dots = self.first_dots

        def dot_update(dots, alpha):
            for dot, curve in zip(dots, transverse_curve):
                dot.move_to(curve.point_from_proportion(alpha))
            return dots

        for x in range(3):
            self.play(
                UpdateFromAlphaFunc(dots, dot_update),
                run_time = 4
            )
        self.dither()

    #######

    def get_arc_walk_dot_movement(self, arc, dots, **kwargs):
        def dot_update(dots, alpha):
            dots[0].move_to(arc.point_from_proportion(0.5*alpha))
            dots[1].move_to(arc.point_from_proportion(0.5+0.5*alpha))
            return dots
        if "run_time" not in kwargs:
            kwargs["run_time"] = 5
        return UpdateFromAlphaFunc(dots, dot_update, **kwargs)

    def sphere_to_plane(self, point):
        x, y, z = point
        return np.array([
            x - 2*x*z + y + 1,
            y+0.5*y*np.cos(z*np.pi),
            0
        ])

    def sphere_point(self, portion_around_equator, equator_tilt = 0):
        theta = portion_around_equator*2*np.pi
        point = np.cos(theta)*RIGHT + np.sin(theta)*UP
        phi = equator_tilt*np.pi
        return rotate_vector(point, phi, RIGHT)

    def get_great_arc_images(self):
        curves = VGroup(*[
            ParametricFunction(
                lambda t : self.sphere_point(t, s)
            ).apply_function(self.sphere_to_plane)
            for s in np.arange(0, 1, 1./self.num_great_arcs)
            # for s in [0]
        ])
        curves.highlight(YELLOW)
        curves[0].highlight(RED)
        for curve in curves:
            antipodal_x_diff = lambda x : \
                curve.point_from_proportion(x+0.5)[0]-\
                curve.point_from_proportion(x)[0]
            last_x = 0                
            last_sign = np.sign(antipodal_x_diff(last_x))
            for x in np.linspace(0, 0.5, 100):
                sign = np.sign(antipodal_x_diff(x))
                if sign != last_sign:
                    mean = np.mean([last_x, x])
                    curve.x_collision_points = [
                        curve.point_from_proportion(mean),
                        curve.point_from_proportion(mean+0.5),
                    ]
                    curve.collision_point_proportion = mean
                    break
                last_x = x
                last_sign = sign
        return curves

    def get_transverse_curve(self, gerat_arc_images):
        points = list(it.chain(*[
            [
                curve.x_collision_points[i]
                for curve in gerat_arc_images
            ]
            for i in 0, 1
        ]))
        full_curve = VMobject(close_new_points = True)
        full_curve.set_points_smoothly(points + [points[0]])
        full_curve.highlight(MAROON_B)
        first_half = full_curve.copy().pointwise_become_partial(
            full_curve, 0, 0.5
        )
        second_half = first_half.copy().rotate_in_place(np.pi, RIGHT)
        broken_curve = VGroup(first_half, second_half)
        return broken_curve


class WalkAroundEquatorPreimage(ExternallyAnimatedScene):
    pass

class WalkTiltedEquatorPreimage(ExternallyAnimatedScene):
    pass

class FormLoopTransverseToEquator(ExternallyAnimatedScene):
    pass

class AntipodalWalkAroundTransverseLoop(ExternallyAnimatedScene):
    pass

class MentionGenerality(TeacherStudentsScene):
    CONFIG = {
        "camera_class" : ShadingCamera,
    }
    def construct(self):
        necklace = Necklace(width = SPACE_WIDTH)
        necklace.shift(2*UP)
        necklace.to_edge(RIGHT)
        arrow = TexMobject("\\Leftrightarrow")
        arrow.scale(2)
        arrow.next_to(necklace, LEFT)
        q_marks = TexMobject("???")
        q_marks.next_to(arrow, UP)
        arrow.add(q_marks)

        formula = TexMobject("f(\\textbf{x}) = f(-\\textbf{x})")
        formula.next_to(self.get_students(), UP, buff = LARGE_BUFF)
        formula.to_edge(LEFT, buff = LARGE_BUFF)

        self.play(
            self.teacher.change_mode, "raise_right_hand",
            self.teacher.look_at, arrow
        )
        self.play(
            FadeIn(necklace, run_time = 2, submobject_mode = "lagged_start"),
            Write(arrow),
            *[
                ApplyMethod(pi.look_at, arrow)
                for pi in self.get_everyone()
            ]
        )
        self.change_student_modes("pondering", "erm", "confused")
        self.dither()
        self.play(*[
            ApplyMethod(pi.look_at, arrow)
            for pi in self.get_everyone()
        ])
        self.play(Write(formula))
        self.dither(3)

class SimpleSphere(ExternallyAnimatedScene):
    pass

class PointsIn3D(Scene):
    CONFIG = {
        # "colors" : [RED, GREEN, BLUE],
        "colors" : color_gradient([GREEN, BLUE], 3),
    }
    def construct(self):
        sphere_def = TextMobject(
            "\\doublespacing Sphere in 3D: All", "$(x_1, x_2, x_3)$\\\\", 
            "such that", "$x_1^2 + x_2^2 + x_3^2 = 1$",
            alignment = "",
        )
        sphere_def.next_to(ORIGIN, DOWN)
        for index, subindex_list in (1, [1, 2, 4, 5, 7, 8]), (3, [0, 2, 4, 6, 8, 10]):
            colors = np.repeat(self.colors, 2)
            for subindex, color in zip(subindex_list, colors):
                sphere_def[index][subindex].highlight(color)

        point_ex = TextMobject(
            "For example, ", 
            "(", "0.41", ", ", "-0.58", ", ", "0.71", ")",
            arg_separator = ""
        )
        for index, color in zip([2, 4, 6], self.colors):
            point_ex[index].highlight(color)
        point_ex.scale(0.8)
        point_ex.next_to(
            sphere_def[1], UP+RIGHT,
            buff = 1.5*LARGE_BUFF
        )
        point_ex.shift_onto_screen()
        arrow = Arrow(sphere_def[1].get_top(), point_ex.get_bottom())

        self.play(Write(sphere_def[1]))
        self.play(ShowCreation(arrow))
        self.play(Write(point_ex))
        self.dither()
        self.play(
            Animation(sphere_def[1].copy(), remover = True),
            Write(sphere_def),
        )
        self.dither()

class AntipodalPairToBeGivenCoordinates(ExternallyAnimatedScene):
    pass

class WritePointCoordinates(Scene):
    CONFIG = {
        "colors" : color_gradient([GREEN, BLUE], 3),
        "corner" : DOWN+RIGHT,
    }
    def construct(self):
        coords = self.get_coords()
        arrow = Arrow(
            -self.corner, self.corner, 
            stroke_width = 8,
            color = MAROON_B
        )
        x_component = self.corner[0]*RIGHT
        y_component = self.corner[1]*UP
        arrow.next_to(
            coords.get_edge_center(y_component), 
            y_component, 
            aligned_edge = -x_component,
            buff = MED_SMALL_BUFF
        )

        group = VGroup(coords, arrow)
        group.scale(2)        
        group.to_corner(self.corner)


        self.play(FadeIn(coords))
        self.play(ShowCreation(arrow))
        self.dither()

    def get_coords(self):
        coords = TexMobject(
            "(", "0.41", ", ", "-0.58", ", ", "0.71", ")",
            arg_separator = ""
        )
        for index, color in zip([1, 3, 5], self.colors):
            coords[index].highlight(color)
        return coords

class WriteAntipodalCoordinates(WritePointCoordinates):
    CONFIG = {
        "corner" : UP+LEFT,
        "sign_color" : RED,
    }

    def get_coords(self):
        coords = TexMobject(
            "(", "-", "0.41", ", ", "+", "0.58", ", ", "-", "0.71", ")",
            arg_separator = ""
        )
        for index, color in zip([2, 5, 8], self.colors):
            coords[index].highlight(color)
            coords[index-1].highlight(self.sign_color)
        return coords

class GeneralizeBorsukUlam(Scene):
    CONFIG = {
        "n_dims" : 3,
        "boundary_colors" : [GREEN, BLUE],
        "output_boundary_color" : [MAROON_B, YELLOW],
        "negative_color" : RED,
    }
    def construct(self):
        self.colors = color_gradient(self.boundary_colors, self.n_dims)

        sphere_set = self.get_sphere_set()
        arrow = Arrow(LEFT, RIGHT)
        f = TexMobject("f")
        output_space = self.get_output_space()
        equation = self.get_equation()

        sphere_set.to_corner(UP+LEFT)
        arrow.next_to(sphere_set, RIGHT)
        f.next_to(arrow, UP)
        output_space.next_to(arrow, RIGHT)
        equation.to_edge(RIGHT)
        lhs = VGroup(*equation[:2])
        eq = equation[2]
        rhs = VGroup(*equation[3:])

        self.play(FadeIn(sphere_set))
        self.dither()
        self.play(
            ShowCreation(arrow),
            Write(f)
        )
        self.play(Write(output_space))
        self.dither()
        self.play(FadeIn(lhs))
        self.play(
            ReplacementTransform(lhs.copy(), rhs),
            Write(eq)
        )
        self.dither()

    def get_condition(self):
        squares = map(TexMobject, [
            "x_%d^2"%d
            for d in range(1, 1+self.n_dims)
        ])
        for square, color in zip(squares, self.colors):
            square[0].highlight(color)
            square[-1].highlight(color)
        plusses = [TexMobject("+") for x in range(self.n_dims-1)]
        plusses += [TexMobject("=1")]
        condition = VGroup(*it.chain(*zip(squares, plusses)))
        condition.arrange_submobjects(RIGHT)

        return condition

    def get_tuple(self):
        mid_parts = list(it.chain(*[
            ["x_%d"%d, ","]
            for d in range(1, self.n_dims)
        ]))
        tup = TexMobject(*["("] + mid_parts + ["x_%d"%self.n_dims, ")"])
        for index, color in zip(it.count(1, 2), self.colors):
            tup[index].highlight(color)

        return tup

    def get_negative_tuple(self):
        mid_parts = list(it.chain(*[
            ["-", "x_%d"%d, ","]
            for d in range(1, self.n_dims)
        ]))
        tup = TexMobject(*["("] + mid_parts + ["-", "x_%d"%self.n_dims, ")"])
        for index, color in zip(it.count(1, 3), self.colors):
            tup[index].highlight(self.negative_color)
            tup[index+1].highlight(color)

        return tup

    def get_output_space(self):
        return TextMobject("%dD space"%(self.n_dims-1))
        # n_dims = self.n_dims-1
        # colors = color_gradient(self.output_boundary_color, n_dims)
        # mid_parts = list(it.chain(*[
        #     ["y_%d"%d, ","]
        #     for d in range(1, n_dims)
        # ]))
        # tup = TexMobject(*["("] + mid_parts + ["y_%d"%n_dims, ")"])
        # for index, color in zip(it.count(1, 2), colors):
        #     tup[index].highlight(color)

        # return tup

    def get_equation(self):
        tup = self.get_tuple()
        neg_tup = self.get_negative_tuple()
        f1, f2 = [TexMobject("f") for x in range(2)]
        equals = TexMobject("=")
        equation = VGroup(f1, tup, equals, f2, neg_tup)
        equation.arrange_submobjects(RIGHT, buff = SMALL_BUFF)

        return equation

    def get_sphere_set(self):
        tup = self.get_tuple()
        such_that = TextMobject("such that")
        such_that.next_to(tup, RIGHT)
        condition = self.get_condition()
        condition.next_to(
            tup, DOWN, 
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT
        )
        group = VGroup(tup, such_that, condition)
        l_brace = Brace(group, LEFT)
        r_brace = Brace(group, RIGHT)
        group.add(l_brace, r_brace)

        return group

class FourDBorsukUlam(GeneralizeBorsukUlam):
    CONFIG = {
        "n_dims" : 4,
    }

class FiveDBorsukUlam(GeneralizeBorsukUlam):
    CONFIG = {
        "n_dims" : 5,
    }




















