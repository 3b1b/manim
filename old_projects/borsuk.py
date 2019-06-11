from manimlib.imports import *
from functools import reduce

class Jewel(VMobject):
    CONFIG = {
        "color" : WHITE,
        "fill_opacity" : 0.75,
        "stroke_width" : 0,
        "height" : 0.5,
        "num_equator_points" : 5,
        "sun_vect" : OUT+LEFT+UP,
    }
    def generate_points(self):
        for vect in OUT, IN:
            compass_vects = list(compass_directions(self.num_equator_points))
            if vect is IN:
                compass_vects.reverse()
            for vect_pair in adjacent_pairs(compass_vects):
                self.add(Polygon(vect, *vect_pair))
        self.set_height(self.height)
        self.rotate(-np.pi/2-np.pi/24, RIGHT)        
        self.rotate(-np.pi/12, UP)
        self.submobjects.sort(
            key=lambda m: -m1.get_center()[2]
        )
        return self

class Necklace(VMobject):
    CONFIG = {
        "width" : FRAME_WIDTH - 1,
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
        jewels.arrange(buff = self.jewel_buff)
        jewels.set_width(self.width)
        jewels.center()
        j_to_j_dist = (jewels[1].get_center()-jewels[0].get_center())[0]

        chain = Line(
            jewels[0].get_center() + j_to_j_dist*LEFT/2, 
            jewels[-1].get_center() + j_to_j_dist*RIGHT/2, 
            color = self.chain_color,
        )
        self.add(chain, *jewels)
        self.chain = chain
        self.jewels = jewels

################

class FromPreviousTopologyVideo(Scene):
    def construct(self):
        rect = Rectangle(height = 9, width = 16)
        rect.set_height(FRAME_HEIGHT-2)
        title = TextMobject("From original ``Who cares about topology'' video")
        title.to_edge(UP)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait()

class CheckOutMathologer(PiCreatureScene):
    CONFIG = {
        "logo_height" : 1.5,
        "screen_height" : 5,
        "channel_name" : "Mathologer",
        "logo_file" : "mathologer_logo",
        "logo_color" : None,
    }
    def construct(self):
        logo = self.get_logo()
        name = TextMobject(self.channel_name)
        name.next_to(logo, RIGHT)

        rect = Rectangle(height = 9, width = 16)
        rect.set_height(self.screen_height)
        rect.next_to(logo, DOWN)
        rect.to_edge(LEFT)

        self.play(
            self.get_logo_intro_animation(logo),
            self.pi_creature.change_mode, "hooray",
        )
        self.play(
            ShowCreation(rect),
            Write(name)
        )
        self.wait(2)
        self.change_mode("happy")
        self.wait(2)

    def get_logo(self):
        logo = ImageMobject(self.logo_file)
        logo.set_height(self.logo_height)
        logo.to_corner(UP+LEFT)
        if self.logo_color is not None:
            logo.set_color(self.logo_color)
            logo.stroke_width = 1
        return logo

    def get_logo_intro_animation(self, logo):
        logo.save_state()
        logo.shift(DOWN)
        logo.set_color(BLACK)
        return ApplyMethod(logo.restore)

class IntroduceStolenNecklaceProblem(ThreeDScene):
    CONFIG = {
        "jewel_colors" : [BLUE, GREEN, WHITE, RED],
        "num_per_jewel" : [8, 10, 4, 6],
        "num_shuffles" : 1,
        "necklace_center" : UP,
        "random_seed" : 2,
        "forced_binary_choices" : (0, 1, 0, 1, 0),
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
        thieves.arrange(RIGHT, buff = 4*LARGE_BUFF)
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
        enumeration_labels.arrange(RIGHT, buff = LARGE_BUFF)
        enumeration_labels.to_edge(UP)

        self.play(
            FadeIn(
                necklace,
                lag_ratio = 0.5,
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
        for jewel_type in jewel_types:
            self.play(
                jewel_type.shift, 0.2*UP,
                rate_func = wiggle
            )
        self.wait()
        for x in range(self.num_shuffles):
            self.shuffle_jewels(jewels)
        self.play(FadeOut(self.title))
        for jewel_type, label in zip(jewel_types, enumeration_labels):
            jewel_type.submobjects.sort(
                key=lambda m: m1.get
            )
            jewel_type.save_state()
            jewel_type.generate_target()
            jewel_type.target.arrange()
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
                half_label.arrange()
                half_labels.add(half_label)
            half_labels.arrange(DOWN)
            half_labels.set_height(thief.get_height())
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
        self.wait()

        for type_index, jewel_type in enumerate(jewel_types):
            jewel_type.save_state()
            jewel_type_copy = jewel_type.copy()
            n_jewels = len(jewel_type)
            halves = [
                VGroup(*jewel_type_copy[:n_jewels/2]),
                VGroup(*jewel_type_copy[n_jewels/2:]),
            ]
            for half, thief, vect in zip(halves, thieves, [RIGHT, LEFT]):
                half.arrange(DOWN)
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
        self.wait()
        self.play(*[
            jewel_type.restore
            for jewel_type in jewel_types
        ])
        self.play(*it.chain(*[
            [thief.change_mode, "confused", thief.look_at, necklace]
            for thief in thieves
        ]))

    def divvy_with_n_cuts(
        self, 
        with_thieves = True, 
        highlight_groups = True,
        show_matching_after_divvying = True,
        ):
        necklace = self.necklace
        jewel_types = self.jewel_types
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
                list(map(Animation, group))
                for group in strand_groups
            ])
        )
        for group in strand_groups:
            group.save_state()
        self.play(
            strand_groups[0].shift, UP/2.,
            strand_groups[1].shift, DOWN/2.,
        )
        if with_thieves:
            self.play(*it.chain(*[
                [thief.change_mode, "happy", thief.look_at, self.necklace]
                for thief in self.thieves
            ]))
            self.play(Blink(self.thieves[1]))
        else:
            self.wait()

        if highlight_groups:
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
                self.wait()
                self.play(FadeOut(box))

        self.wait()
        if show_matching_after_divvying:
            for jewel_type in jewel_types:
                self.play(
                    *[
                        ApplyMethod(jewel.scale_in_place, 1.5)
                        for jewel in jewel_type
                    ],
                    rate_func = there_and_back,
                    run_time = 2
                )
            self.wait()
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

    def get_necklace(self, **kwargs):
        colors = reduce(op.add, [
            num*[color]
            for num, color in zip(self.num_per_jewel, self.jewel_colors)
        ])
        self.necklace = Necklace(*colors, **kwargs)
        self.necklace.shift(self.necklace_center)
        return self.necklace

    def get_jewels_organized_by_type(self, jewels):
        return [
            VGroup(*[m for m in jewels if m.get_color() == color])
            for color in map(Color, self.jewel_colors)
        ]

    def shuffle_jewels(self, jewels, run_time = 2, path_arc = np.pi/2, **kwargs):
        shuffled_indices = list(range(len(jewels)))
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
        type_numbers = list(map(jewel_to_type_number, jewels))

        n_types = len(jewel_types)
        for slice_indices in it.combinations(list(range(1, len(jewels))), n_types):
            slice_indices = [0] + list(slice_indices) + [len(jewels)]
            if self.forced_binary_choices is not None:
                all_binary_choices = [self.forced_binary_choices]
            else:
                all_binary_choices = it.product(*[list(range(2))]*(n_types+1))
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

class ThingToProve(PiCreatureScene):
    def construct(self):
        arrow = Arrow(UP, DOWN)
        top_words = TextMobject("$n$ jewel types")
        top_words.next_to(arrow, UP)
        bottom_words = TextMobject("""
            Fair division possible
            with $n$ cuts
        """)
        bottom_words.next_to(arrow, DOWN)

        self.play(
            Write(top_words, run_time = 2),
            self.pi_creature.change_mode, "raise_right_hand"
        )
        self.play(ShowCreation(arrow))
        self.play(
            Write(bottom_words, run_time = 2),
            self.pi_creature.change_mode, "pondering"
        )
        self.wait(3)

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
            Minimize sharding,
            allocate resources evenly
        """)
        self.change_student_modes(*["pondering"]*3)
        self.wait(2)

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
            self.divvy_with_n_cuts(
                show_matching_after_divvying = False
            )

class NowForTheTopology(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("Now for the \\\\ topology")
        self.change_student_modes(*["hooray"]*3)
        self.wait(3)

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
        words.set_color(self.color)
        words.set_width(FRAME_WIDTH-1)
        words.to_edge(DOWN)
        self.play(Write(words))
        self.wait(2)

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
        self.wait(2)

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
        self.draw_arrow()
        self.add_example_coordinates()
        self.wander_continuously()

    def draw_arrow(self):
        square = Square(
            side_length = self.corner_square_width,
            stroke_color = WHITE,
            stroke_width = 0,
        )
        square.to_corner(UP+LEFT, buff = 0)

        arrow = Arrow(
            square.get_right(), 
            self.coords_to_point(*self.example_point_coords)
        )

        self.play(ShowCreation(arrow))

    def add_example_coordinates(self):
        dot = Dot(self.coords_to_point(*self.example_point_coords))
        dot.set_color(YELLOW)
        tex = TexMobject("(25^\\circ\\text{C}, 101 \\text{ kPa})")
        tex.next_to(dot, UP+RIGHT, buff = SMALL_BUFF)

        self.play(ShowCreation(dot))
        self.play(Write(tex))
        self.wait()
        self.play(FadeOut(tex))

    def wander_continuously(self):
        path = VMobject().set_points_smoothly([
            ORIGIN, 2*UP+RIGHT, 2*DOWN+RIGHT,
            5*RIGHT, 4*RIGHT+UP, 3*RIGHT+2*DOWN,
            DOWN+LEFT, 2*RIGHT
        ])
        point = self.coords_to_point(*self.example_point_coords)
        path.shift(point)

        path.set_color(GREEN)

        self.play(ShowCreation(path, run_time = 10, rate_func=linear))
        self.wait()

class AlternateSphereSquishing(ExternallyAnimatedScene):
    pass

class AlternateAntipodalCollision(ExternallyAnimatedScene):
    pass

class AskWhy(TeacherStudentsScene):
    def construct(self):
        self.student_says("But...why?")
        self.change_student_modes("pondering", None, "thinking")
        self.play(self.get_teacher().change_mode, "happy")
        self.wait(3)

class PointOutVSauce(CheckOutMathologer):
    CONFIG = {
        "channel_name" : "",
        "logo_file" : "Vsauce_logo",
        "logo_height" : 1,
        "logo_color" : GREY,
    }
    def get_logo(self):
        logo = SVGMobject(file_name = self.logo_file)
        logo.set_height(self.logo_height)
        logo.to_corner(UP+LEFT)
        logo.set_stroke(width = 0)
        logo.set_fill(GREEN)
        logo.sort()
        return logo

    def get_logo_intro_animation(self, logo):
        return DrawBorderThenFill(
            logo,
            run_time = 2,
        )

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
        dots.set_color(MAROON_B)
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
        v_line = DashedLine(FRAME_Y_RADIUS*UP, FRAME_Y_RADIUS*DOWN)
        v_line.shift(dots.get_center()[0]*RIGHT)
        self.play(ShowCreation(v_line))
        self.wait()
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
        dots.set_color(MAROON_B)
        dot_movement = self.get_arc_walk_dot_movement(tilted_eq, dots)
        dot_movement.update(0)

        self.play(ReplacementTransform(equator.copy(), tilted_eq))
        self.wait()
        self.play(FadeIn(dots))
        self.play(dot_movement)

        proportion = tilted_eq.collision_point_proportion
        self.play(self.get_arc_walk_dot_movement(
            tilted_eq, dots,
            rate_func = lambda t : 2*proportion*smooth(t)
        ))
        v_line = DashedLine(FRAME_Y_RADIUS*UP, FRAME_Y_RADIUS*DOWN)
        v_line.shift(dots.get_center()[0]*RIGHT)
        self.play(ShowCreation(v_line))
        self.wait()
        self.play(FadeOut(v_line))
        self.play(*list(map(FadeOut, [tilted_eq, dots])))

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
            Transform(equator, arc, rate_func=linear)
            for arc in target_arcs
        ])
        dots_transform = Succession(*[
            Transform(dots, target, rate_func=linear)
            for target in target_dots
        ])

        self.play(
            ShowCreation(transverse_curve, lag_ratio = 0),
            equator_transform,
            dots_transform,
            run_time = 10,
            rate_func=linear,
        )
        self.wait(2)

    def walk_transverse_curve(self):
        transverse_curve = self.get_transverse_curve(self.great_arc_images)
        dots = self.first_dots

        def dot_update(dots, alpha):
            for dot, curve in zip(dots, transverse_curve):
                dot.move_to(curve.point_from_proportion(alpha))
            return dots

        for x in range(2):
            self.play(
                UpdateFromAlphaFunc(dots, dot_update),
                run_time = 4
            )
        self.play(
            UpdateFromAlphaFunc(dots, dot_update),
            run_time = 4,
            rate_func = lambda t : 0.455*smooth(t)
        )
        self.play(
            dots.set_color, YELLOW,
            dots.scale_in_place, 1.2,
            rate_func = there_and_back
        )
        self.wait()

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
        curves.set_color(YELLOW)
        curves[0].set_color(RED)
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
            for i in (0, 1)
        ]))
        full_curve = VMobject(close_new_points = True)
        full_curve.set_points_smoothly(points + [points[0]])
        full_curve.set_color(MAROON_B)
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

class MentionGenerality(TeacherStudentsScene, ThreeDScene):
    def construct(self):
        necklace = Necklace(width = FRAME_X_RADIUS)
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
            FadeIn(necklace, run_time = 2, lag_ratio = 0.5),
            Write(arrow),
            *[
                ApplyMethod(pi.look_at, arrow)
                for pi in self.get_pi_creatures()
            ]
        )
        self.change_student_modes("pondering", "erm", "confused")
        self.wait()
        self.play(*[
            ApplyMethod(pi.look_at, arrow)
            for pi in self.get_pi_creatures()
        ])
        self.play(Write(formula))
        self.wait(3)

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
                sphere_def[index][subindex].set_color(color)

        point_ex = TextMobject(
            "For example, ", 
            "(", "0.41", ", ", "-0.58", ", ", "0.71", ")",
            arg_separator = ""
        )
        for index, color in zip([2, 4, 6], self.colors):
            point_ex[index].set_color(color)
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
        self.wait()
        self.play(
            Animation(sphere_def[1].copy(), remover = True),
            Write(sphere_def),
        )
        self.wait()

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
        self.wait()

    def get_coords(self):
        coords = TexMobject(
            "(", "0.41", ", ", "-0.58", ", ", "0.71", ")",
            arg_separator = ""
        )
        for index, color in zip([1, 3, 5], self.colors):
            coords[index].set_color(color)
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
            coords[index].set_color(color)
            coords[index-1].set_color(self.sign_color)
        return coords

class GeneralizeBorsukUlam(Scene):
    CONFIG = {
        "n_dims" : 3,
        "boundary_colors" : [GREEN_B, BLUE],
        "output_boundary_color" : [MAROON_B, YELLOW],
        "negative_color" : RED,
    }
    def setup(self):
        self.colors = color_gradient(self.boundary_colors, self.n_dims)

    def construct(self):
        sphere_set = self.get_sphere_set()
        arrow = Arrow(LEFT, RIGHT)
        f = TexMobject("f")
        output_space = self.get_output_space()
        equation = self.get_equation()

        sphere_set.to_corner(UP+LEFT)
        arrow.next_to(sphere_set, RIGHT)
        f.next_to(arrow, UP)
        output_space.next_to(arrow, RIGHT)
        equation.next_to(sphere_set, DOWN, buff = LARGE_BUFF)
        equation.to_edge(RIGHT)
        lhs = VGroup(*equation[:2])
        eq = equation[2]
        rhs = VGroup(*equation[3:])

        self.play(FadeIn(sphere_set))
        self.wait()
        self.play(
            ShowCreation(arrow),
            Write(f)
        )
        self.play(Write(output_space))
        self.wait()
        self.play(FadeIn(lhs))
        self.play(
            ReplacementTransform(lhs.copy(), rhs),
            Write(eq)
        )
        self.wait()

    def get_condition(self):
        squares = list(map(TexMobject, [
            "x_%d^2"%d
            for d in range(1, 1+self.n_dims)
        ]))
        for square, color in zip(squares, self.colors):
            square[0].set_color(color)
            square[-1].set_color(color)
        plusses = [TexMobject("+") for x in range(self.n_dims-1)]
        plusses += [TexMobject("=1")]
        condition = VGroup(*it.chain(*list(zip(squares, plusses))))
        condition.arrange(RIGHT)

        return condition

    def get_tuple(self):
        mid_parts = list(it.chain(*[
            ["x_%d"%d, ","]
            for d in range(1, self.n_dims)
        ]))
        tup = TexMobject(*["("] + mid_parts + ["x_%d"%self.n_dims, ")"])
        for index, color in zip(it.count(1, 2), self.colors):
            tup[index].set_color(color)

        return tup

    def get_negative_tuple(self):
        mid_parts = list(it.chain(*[
            ["-", "x_%d"%d, ","]
            for d in range(1, self.n_dims)
        ]))
        tup = TexMobject(*["("] + mid_parts + ["-", "x_%d"%self.n_dims, ")"])
        for index, color in zip(it.count(1, 3), self.colors):
            tup[index].set_color(self.negative_color)
            tup[index+1].set_color(color)

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
        #     tup[index].set_color(color)

        # return tup

    def get_equation(self):
        tup = self.get_tuple()
        neg_tup = self.get_negative_tuple()
        f1, f2 = [TexMobject("f") for x in range(2)]
        equals = TexMobject("=")
        equation = VGroup(f1, tup, equals, f2, neg_tup)
        equation.arrange(RIGHT, buff = SMALL_BUFF)

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

# class FiveDBorsukUlam(GeneralizeBorsukUlam):
#     CONFIG = {
#         "n_dims" : 5,
#     }

class MentionMakingNecklaceProblemContinuous(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            Translate this into
            a continuous problem.
        """)
        self.change_student_modes("confused", "pondering", "erm")
        self.wait(3)

class MakeTwoJewelCaseContinuous(IntroduceStolenNecklaceProblem):
    CONFIG = {
        "jewel_colors" : [BLUE, GREEN],
        "num_per_jewel" : [8, 10],
        "random_seed" : 2,
        "forced_binary_choices" : (0, 1, 0),
        "show_matching_after_divvying" : True,
        "necklace_center" : ORIGIN,
        "necklace_width" : FRAME_WIDTH - 3,
        "random_seed" : 0,
        "num_continuous_division_searches" : 4,
    }
    def construct(self):
        random.seed(self.random_seed)
        self.introduce_necklace()
        self.divvy_with_n_cuts()
        self.identify_necklace_with_unit_interval()
        self.color_necklace()
        self.find_continuous_fair_division()
        self.show_continuous_fair_division()
        self.set_color_continuous_groups()
        self.mention_equivalence_to_discrete_case()
        self.shift_divide_off_tick_marks()

    def introduce_necklace(self):
        self.get_necklace(
            width = self.necklace_width,
        )
        self.play(FadeIn(
            self.necklace,
            lag_ratio = 0.5
        ))
        self.shuffle_jewels(self.necklace.jewels)
        jewel_types = self.get_jewels_organized_by_type(
            self.necklace.jewels
        )
        self.wait()
        self.count_jewel_types(jewel_types)
        self.wait()

        self.jewel_types = jewel_types

    def count_jewel_types(self, jewel_types):
        enumeration_labels = VGroup()
        for jewel_type in jewel_types:
            num_mob = TexMobject(str(len(jewel_type)))
            jewel_copy = jewel_type[0].copy()
            # jewel_copy.set_height(num_mob.get_height())
            jewel_copy.next_to(num_mob)
            label = VGroup(num_mob, jewel_copy)
            enumeration_labels.add(label)
        enumeration_labels.arrange(RIGHT, buff = LARGE_BUFF)
        enumeration_labels.to_edge(UP)

        for jewel_type, label in zip(jewel_types, enumeration_labels):
            jewel_type.sort_submobjects()
         
            jewel_type.save_state()
            jewel_type.generate_target()
            jewel_type.target.arrange()
            jewel_type.target.move_to(2*UP)
            self.play(
                MoveToTarget(jewel_type), 
                Write(label)
            )
            self.play(jewel_type.restore)

    def divvy_with_n_cuts(self):
        IntroduceStolenNecklaceProblem.divvy_with_n_cuts(
            self, 
            with_thieves = False, 
            highlight_groups = False,
            show_matching_after_divvying = True,
        )

    def identify_necklace_with_unit_interval(self):
        interval = UnitInterval(
            tick_frequency = 1./sum(self.num_per_jewel),
            tick_size = 0.2,
            numbers_with_elongated_ticks = [],
        )
        interval.stretch_to_fit_width(self.necklace.get_width())
        interval.move_to(self.necklace)
        tick_marks = interval.tick_marks
        tick_marks.set_stroke(WHITE, width = 2)

        brace = Brace(interval)
        brace_text = brace.get_text("Length = 1")

        self.play(
            GrowFromCenter(brace),
            Write(brace_text)
        )
        self.wait()
        self.play(
            ShowCreation(interval.tick_marks),
        )
        self.wait()

        self.tick_marks = interval.tick_marks
        self.length_brace = VGroup(brace, brace_text)

    def color_necklace(self):
        example_index = len(self.necklace.jewels)/2
        jewels = self.necklace.jewels
        chain = self.necklace.chain
        self.remove(self.necklace)
        self.add(chain, jewels)

        jewels.submobjects.sort(
            key=lambda m: m.get_center()[0]
        )
        remaining_indices = list(range(len(jewels)))
        remaining_indices.remove(example_index)

        example_segment = self.color_necklace_by_indices(example_index)
        remaining_segments = self.color_necklace_by_indices(*remaining_indices)
        self.remove(chain)
        segments = VGroup(example_segment[0], *remaining_segments)
        segments.submobjects.sort(
            key=lambda m: m.get_center()[0]
        )
        segment_types = VGroup(*[
            VGroup(*[m for m in segments if m.get_color() == Color(color)])
            for color in self.jewel_colors
        ])

        for group in segment_types:
            length_tex = TexMobject("\\frac{%d}{%d}"%(
                len(group),
                len(jewels)
             ))
            length_tex.next_to(group, UP)
            length_tex.shift(UP)
            self.play(
                group.shift, UP,
                Write(length_tex, run_time = 1),
            )
            self.wait()
            self.play(
                group.shift, DOWN,
                FadeOut(length_tex)
            )
        self.play(FadeOut(self.length_brace))

        self.segments = segments

    def color_necklace_by_indices(self, *indices):
        chain = self.necklace.chain
        jewels = VGroup(*[
            self.necklace.jewels[i]
            for i in indices
        ])
        n_jewels = len(self.necklace.jewels)

        segments = VGroup(*[
            Line(
                chain.point_from_proportion(index/float(n_jewels)),
                chain.point_from_proportion((index+1)/float(n_jewels)),
                color = jewel.get_color()
            )
            for index, jewel in zip(indices, jewels)
        ])
        for jewel in jewels:
            jewel.save_state()

        self.play(jewels.shift, jewels.get_height()*UP)
        self.play(ReplacementTransform(
            jewels, segments,
            lag_ratio = 0.5,
            run_time = 2
        ))
        self.wait()
        return segments

    def find_continuous_fair_division(self):
        chain = self.necklace.chain
        n_jewels = len(self.necklace.jewels)

        slice_indices, ignore = self.find_slice_indices(
            self.necklace.jewels,
            self.jewel_types
        )
        cut_proportions = [
            sorted([random.random(), random.random()])
            for x in range(self.num_continuous_division_searches)
        ]
        cut_proportions.append([
            float(i)/n_jewels
            for i in slice_indices[1:-1]
        ])
        cut_points = [
            list(map(chain.point_from_proportion, pair))
            for pair in cut_proportions
        ]
        v_lines = VGroup(*[DashedLine(UP, DOWN) for x in range(2)])

        for line, point in zip(v_lines, cut_points[0]):
            line.move_to(point)

        self.play(ShowCreation(v_lines))
        self.wait()
        for target_points in cut_points[1:]:
            self.play(*[
                ApplyMethod(line.move_to, point)
                for line, point in zip(v_lines, target_points)
            ])
            self.wait()

        self.slice_indices = slice_indices
        self.v_lines = v_lines

    def show_continuous_fair_division(self):
        slice_indices = self.slice_indices

        groups = [
            VGroup(
                VGroup(*self.segments[i1:i2]),
                VGroup(*self.tick_marks[i1:i2]),
            )
            for i1, i2 in zip(slice_indices, slice_indices[1:])
        ]
        groups[-1].add(self.tick_marks[-1])
        vects = [[UP, DOWN][i] for i in self.forced_binary_choices]

        self.play(*[
            ApplyMethod(group.shift, 0.5*vect)
            for group, vect in zip(groups, vects)
        ])
        self.wait()

        self.groups = groups

    def set_color_continuous_groups(self):
        top_group = VGroup(self.groups[0], self.groups[2])
        bottom_group = self.groups[1]
        boxes = VGroup()
        for group in top_group, bottom_group:
            box = Rectangle(
                width = FRAME_WIDTH-2,
                height = group.get_height()+SMALL_BUFF,
                stroke_width = 0,
                fill_color = WHITE,
                fill_opacity = 0.25,
            )
            box.shift(group.get_center()[1]*UP)
            boxes.add(box)

        weight_description = VGroup(*[
            VGroup(
                TexMobject("\\frac{%d}{%d}"%(
                    len(jewel_type)/2, len(self.segments)
                )),
                Jewel(color = jewel_type[0].get_color())
            ).arrange()
            for jewel_type in self.jewel_types
        ])
        weight_description.arrange(buff = LARGE_BUFF)
        weight_description.next_to(boxes, UP, aligned_edge = LEFT)

        self.play(FadeIn(boxes))
        self.play(Write(weight_description))
        self.wait()

        self.set_color_box = boxes
        self.weight_description = weight_description

    def mention_equivalence_to_discrete_case(self):
        morty = Mortimer()
        morty.flip()
        morty.to_edge(DOWN)
        morty.shift(LEFT)
        self.play(FadeIn(morty))
        self.play(PiCreatureSays(
            morty, 
            """This is equivalent to
            the discrete case. """,
            bubble_kwargs = {
                "height" : 3, 
                "direction" : LEFT,
            }
        ))
        self.play(Blink(morty))
        self.wait()
        self.play(*list(map(FadeOut, [
            morty, morty.bubble, morty.bubble.content
        ])))
        
    def shift_divide_off_tick_marks(self):
        groups = self.groups
        slice_indices = self.slice_indices
        v_lines = self.v_lines

        left_segment = groups[1][0][0]
        left_tick = groups[1][1][0]
        right_segment = groups[-1][0][0]
        right_tick = groups[-1][1][0]

        segment_width = left_segment.get_width()

        for mob in left_segment, right_segment:
            mob.parts = VGroup(
                mob.copy().pointwise_become_partial(mob, 0, 0.5),
                mob.copy().pointwise_become_partial(mob, 0.5, 1),
            )
            self.remove(mob)
            self.add(mob.parts)
        restorers = [left_segment.parts, left_tick, right_segment.parts, right_tick]
        for mob in restorers:
            mob.save_state()

        emerald_segments = VGroup(*[
            segment
            for segment in list(groups[0][0])+list(groups[2][0])
            if segment.get_color() == Color(self.jewel_colors[1])
            if segment is not right_segment
        ])
        emerald_segments.add(
            left_segment.parts[0],
            right_segment.parts[1],
        )
        emerald_segments.sort()

        self.play(v_lines.shift, segment_width*RIGHT/2)
        self.play(*[
            ApplyMethod(mob.shift, vect)
            for mob, vect in [
                (left_segment.parts[0], UP),
                (left_tick, UP),
                (right_segment.parts[0], DOWN),
                (right_tick, DOWN),
            ]
        ])
        self.wait()

        words = TextMobject("Cut part way through segment")
        words.to_edge(RIGHT)
        words.shift(2*UP)
        arrow1 = Arrow(words.get_bottom(), left_segment.parts[0].get_right())
        arrow2 = Arrow(words.get_bottom(), right_segment.parts[1].get_left())
        VGroup(words, arrow1, arrow2).set_color(RED)

        self.play(Write(words), ShowCreation(arrow1))
        self.wait()

        emerald_segments.save_state()
        emerald_segments.generate_target()
        emerald_segments.target.arrange()
        emerald_segments.target.move_to(2*DOWN)
        brace = Brace(emerald_segments.target, DOWN)
        label = VGroup(
            TexMobject("5\\left( 1/18 \\right)"),
            Jewel(color = self.jewel_colors[1])
        ).arrange()
        label.next_to(brace, DOWN)
        self.play(MoveToTarget(emerald_segments))
        self.play(GrowFromCenter(brace))
        self.play(Write(label))
        self.wait()
        broken_pair = VGroup(*emerald_segments[2:4])
        broken_pair.save_state()
        self.play(broken_pair.shift, 0.5*UP)
        vect = broken_pair[1].get_left()-broken_pair[1].get_right()
        self.play(
            broken_pair[0].shift, -vect/2,
            broken_pair[1].shift, vect/2,
        )
        self.wait()
        self.play(broken_pair.space_out_submobjects)
        self.play(broken_pair.restore)
        self.wait()
        self.play(
            emerald_segments.restore,
            *list(map(FadeOut, [brace, label]))
        )

        self.wait()
        self.play(ShowCreation(arrow2))
        self.wait()
        self.play(*list(map(FadeOut, [words, arrow1, arrow2])))

        for line in v_lines:
            self.play(line.shift, segment_width*LEFT/2)
        self.play(*[mob.restore for mob in restorers])
        self.remove(left_segment.parts, right_segment.parts)
        self.add(left_segment, right_segment)

class ThinkAboutTheChoices(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            Think about the choices
            behind a division...
        """)
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = FRAME_X_RADIUS*RIGHT+FRAME_Y_RADIUS*DOWN
        )
        self.wait(3)

class ChoicesInNecklaceCutting(ReconfigurableScene):
    CONFIG = {
        "num_continuous_division_searches" : 4,
        "denoms" : [6, 3, 2],
        "necklace_center" : DOWN,
        "thief_box_offset" : 1.2,
    }
    def construct(self):
        self.add_necklace()
        self.choose_places_to_cut()
        self.show_three_numbers_adding_to_one()
        self.make_binary_choice()

    def add_necklace(self):
        width, colors, num_per_color = [
            MakeTwoJewelCaseContinuous.CONFIG[key]
            for key in [
                "necklace_width", "jewel_colors", "num_per_jewel"
            ]
        ]
        color_list = list(it.chain(*[
            num*[color] 
            for num, color in zip(num_per_color, colors)
        ]))
        random.shuffle(color_list)

        interval = UnitInterval(
            tick_frequency = 1./sum(num_per_color),
            tick_size = 0.2,
            numbers_with_elongated_ticks = [],
        )
        interval.stretch_to_fit_width(width)
        interval.shift(self.necklace_center)
        tick_marks = interval.tick_marks
        tick_marks.set_stroke(WHITE, width = 2)

        segments = VGroup()
        for l_tick, r_tick, color in zip(tick_marks, tick_marks[1:], color_list):
            segment = Line(
                l_tick.get_center(),
                r_tick.get_center(),
                color = color
            )
            segments.add(segment)

        self.necklace = VGroup(segments, tick_marks)
        self.add(self.necklace)

        self.interval = interval        

    def choose_places_to_cut(self):
        v_lines = VGroup(*[DashedLine(UP, DOWN) for x in range(2)])
        final_num_pair = np.cumsum([1./d for d in self.denoms[:2]])

        num_pairs = [
            sorted([random.random(), random.random()])
            for x in range(self.num_continuous_division_searches)
        ] + [final_num_pair]

        point_pairs = [
            list(map(self.interval.number_to_point, num_pair))
            for num_pair in num_pairs
        ]
        
        for line, point in zip(v_lines, point_pairs[0]):
            line.move_to(point)
        self.play(ShowCreation(v_lines))
        for point_pair in point_pairs[1:]:
            self.wait()
            self.play(*[
                ApplyMethod(line.move_to, point)
                for line, point in zip(v_lines, point_pair)
            ])
        self.wait()

        self.division_points = list(it.chain(
            [self.interval.get_left()],
            point_pairs[-1],
            [self.interval.get_right()]
        ))

        self.v_lines = v_lines

    def show_three_numbers_adding_to_one(self):
        points = self.division_points
        braces = [
            Brace(Line(p1+SMALL_BUFF*RIGHT/2, p2+SMALL_BUFF*LEFT/2))
            for p1, p2 in zip(points, points[1:])
        ]
        for char, denom, brace in zip("abc", self.denoms, braces):
            brace.label = brace.get_text("$%s$"%char)
            brace.concrete_label = brace.get_text("$\\frac{1}{%d}$"%denom)
            VGroup(
                brace.label,
                brace.concrete_label
            ).set_color(YELLOW)

        words = TextMobject(
            "1) Choose", "$a$, $b$, $c$", "so that", "$a+b+c = 1$"
        )
        words[1].set_color(YELLOW)
        words[3].set_color(YELLOW)
        words.to_corner(UP+LEFT)

        self.play(*it.chain(*[
            [GrowFromCenter(brace), Write(brace.label)]
            for brace in braces
        ]))
        self.play(Write(words))
        self.wait(2)
        self.play(*[
            ReplacementTransform(brace.label, brace.concrete_label)
            for brace in braces
        ])
        self.wait()
        self.wiggle_v_lines()
        self.wait()
        self.transition_to_alt_config(denoms = [3, 3, 3])
        self.wait()
        self.play(*list(map(FadeOut, list(braces) + [
            brace.concrete_label for brace in braces
        ])))

        self.choice_one_words = words

    def make_binary_choice(self):
        groups = self.get_groups()
        boxes, labels = self.get_boxes_and_labels()
        arrow_pairs, curr_arrows = self.get_choice_arrow_pairs(groups)
        words = TextMobject("2) Make a binary choice for each segment")
        words.next_to(
            self.choice_one_words, DOWN, 
            buff = MED_LARGE_BUFF, 
            aligned_edge = LEFT
        )

        self.play(Write(words))
        self.play(*list(map(FadeIn, [boxes, labels])))
        for binary_choices in it.product(*[[0, 1]]*3):
            self.play(*[
                ApplyMethod(group.move_to, group.target_points[choice])
                for group, choice in zip(groups, binary_choices)
            ] + [
                Transform(
                    curr_arrow, arrow_pair[choice],
                    path_arc = np.pi
                )
                for curr_arrow, arrow_pair, choice in zip(
                    curr_arrows, arrow_pairs, binary_choices
                )
            ])
            self.wait()

    ######

    def get_groups(self, indices = None):
        segments, tick_marks = self.necklace
        if indices is None:
            n_segments = len(segments)
            indices = [0, n_segments/6, n_segments/2, n_segments]

        groups = [
            VGroup(
                VGroup(*segments[i1:i2]),
                VGroup(*tick_marks[i1:i2]),
            )
            for i1, i2 in zip(indices, indices[1:])
        ]
        for group, index in zip(groups, indices[1:]):
            group[1].add(tick_marks[index].copy())
        groups[-1][1].add(tick_marks[-1])

        for group in groups:
            group.target_points = [
                group.get_center() + self.thief_box_offset*vect
                for vect in (UP, DOWN)
            ]

        return groups

    def get_boxes_and_labels(self):
        box = Rectangle(
            height = self.necklace.get_height()+SMALL_BUFF,
            width = self.necklace.get_width()+2*SMALL_BUFF,
            stroke_width = 0,
            fill_color = WHITE,
            fill_opacity = 0.25
        )
        box.move_to(self.necklace)

        boxes = VGroup(*[
            box.copy().shift(self.thief_box_offset*vect)
            for vect in (UP, DOWN)
        ])
        labels = VGroup(*[
            TextMobject(
                "Thief %d"%(i+1)
            ).next_to(box, UP, aligned_edge = RIGHT)
            for i, box in enumerate(boxes)
        ])
        return boxes, labels

    def get_choice_arrow_pairs(self, groups):
        arrow = TexMobject("\\uparrow")
        arrow_pairs = [
            [arrow.copy(), arrow.copy().rotate(np.pi)]
            for group in groups
        ]
        pre_arrow_points = [
            VectorizedPoint(group.get_center())
            for group in groups
        ]
        for point, arrow_pair in zip(pre_arrow_points, arrow_pairs):
            for arrow, color in zip(arrow_pair, [GREEN, RED]):
                arrow.set_color(color)
                arrow.move_to(point.get_center())
        return arrow_pairs, pre_arrow_points

    def wiggle_v_lines(self):
        self.play(
            *it.chain(*[
                [
                    line.rotate_in_place, np.pi/12, vect,
                    line.set_color, RED
                ]
                for line, vect in zip(self.v_lines, [OUT, IN])
            ]),
            rate_func = wiggle
        )

class CompareThisToSphereChoice(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            Compare this to choosing
            a point on the sphere.
        """)
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = FRAME_X_RADIUS*RIGHT+FRAME_Y_RADIUS*DOWN
        )
        self.wait(3)

class SimpleRotatingSphereWithPoint(ExternallyAnimatedScene):
    pass

class ChoicesForSpherePoint(GeneralizeBorsukUlam):
    def construct(self):
        self.add_sphere_set()
        self.initialize_words()
        self.play(Write(self.choice_one_words))
        self.wait()
        self.show_example_choices()
        self.show_binary_choices()

    def get_tuple(self):
        tup = TexMobject("(x, y, z)")
        for i, color in zip([1, 3, 5], self.colors):
            tup[i].set_color(color)
        return tup

    def get_condition(self):
        condition = TexMobject("x^2+y^2+z^2 = 1")
        for i, color in zip([0, 3, 6], self.colors):
            VGroup(*condition[i:i+2]).set_color(color)
        return condition

    def add_sphere_set(self):
        sphere_set = self.get_sphere_set()
        sphere_set.scale(0.7)
        sphere_set.to_edge(RIGHT)
        sphere_set.shift(UP)

        self.add(sphere_set)
        self.sphere_set = sphere_set

    def initialize_words(self):
        choice_one_words = TextMobject(
            "1) Choose", "$x^2$, $y^2$, $z^2$",
            "so that", "$x^2+y^2+z^2 = 1$"
        )
        for i in 1, 3:
            for j, color in zip([0, 3, 6], self.colors):
                VGroup(*choice_one_words[i][j:j+2]).set_color(color)
        choice_one_words.to_corner(UP+LEFT)

        choice_two_words = TextMobject(
            "2) Make a binary choice for each one"
        )
        choice_two_words.next_to(
            choice_one_words, DOWN, 
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT
        )

        self.choice_one_words = choice_one_words
        self.choice_two_words = choice_two_words

    def show_example_choices(self):
        choices = VGroup(*[
            TexMobject(*tex).set_color(color)
            for color, tex in zip(self.colors, [
                ("x", "^2 = ", "1/6"),
                ("y", "^2 = ", "1/3"),
                ("z", "^2 = ", "1/2"),
            ])
        ])
        choices.arrange(
            DOWN, 
            buff = LARGE_BUFF,
            aligned_edge = LEFT
        )
        choices.set_height(FRAME_Y_RADIUS)
        choices.to_edge(LEFT)
        choices.shift(DOWN)

        self.play(FadeIn(
            choices,
            run_time = 2,
            lag_ratio = 0.5
        ))
        self.wait()

        self.choices = choices

    def show_binary_choices(self):
        for choice in self.choices:
            var_tex = choice.expression_parts[0]
            frac_tex = choice.expression_parts[2]
            sqrts = VGroup(*[
                TexMobject(
                    var_tex + "=" + sign + \
                    "\\sqrt{%s}"%frac_tex)
                for sign in ["+", "-"]
            ])
            for sqrt in sqrts:
                sqrt.scale(0.6)
            sqrts.arrange(DOWN)
            sqrts.next_to(choice, RIGHT, buff = LARGE_BUFF)
            sqrts.set_color(choice.get_color())

            arrows = VGroup(*[
                Arrow(
                    choice.get_right(), sqrt.get_left(), 
                    color = WHITE,
                    tip_length = 0.1,
                    buff = SMALL_BUFF
                )
                for sqrt in sqrts
            ])

            self.play(ShowCreation(arrows))
            self.play(FadeIn(sqrts, lag_ratio = 0.5))
        self.play(Write(self.choice_two_words))
        self.wait()

class NecklaceDivisionSphereAssociation(ChoicesInNecklaceCutting):
    CONFIG = {
        "xyz_colors" : color_gradient([GREEN_B, BLUE], 3),
        "necklace_center" : DOWN,
        "thief_box_offset" : 1.6,
        "denoms" : [6, 3, 2],
    }
    def construct(self):
        self.add_necklace()
        self.add_sphere_point_label()
        self.choose_places_to_cut()
        self.add_braces()
        self.add_boxes_and_labels()
        self.show_binary_choice_association()
        self.ask_about_antipodal_pairs()

    def add_sphere_point_label(self):
        label = TextMobject(
            "$(x, y, z)$",
            "such that",
            "$x^2 + y^2 + z^2 = 1$"
        )
        for i, j_list in (0, [1, 3, 5]), (2, [0, 3, 6]):
            for j, color in zip(j_list, self.xyz_colors):
                label[i][j].set_color(color)
        label.to_corner(UP+RIGHT)

        ghost_sphere_point = VectorizedPoint()
        ghost_sphere_point.to_corner(UP+LEFT, buff = LARGE_BUFF)
        ghost_sphere_point.shift(2*RIGHT)

        arrow = Arrow(
            label.get_left(), ghost_sphere_point,
            color = WHITE
        )

        self.add(label, arrow)

        self.sphere_point_label = label

    def add_braces(self):
        points = self.division_points
        braces = [
            Brace(
                Line(p1+SMALL_BUFF*RIGHT/2, p2+SMALL_BUFF*LEFT/2),
                UP
            )
            for p1, p2 in zip(points, points[1:])
        ]
        for char, brace, color, denom in zip("xyz", braces, self.xyz_colors, self.denoms):
            brace.label = brace.get_text(
                "$%s^2$"%char, "$= 1/%d$"%denom,
                buff = SMALL_BUFF
            )
            brace.label.set_color(color)
            if brace.label.get_right()[0] > brace.get_right()[0]:
                brace.label.next_to(
                    brace, UP, buff = SMALL_BUFF,
                    aligned_edge = RIGHT
                )

        self.play(*it.chain(
            list(map(GrowFromCenter, braces)),
            [Write(brace.label) for brace in braces]
        ))
        self.wait()

        self.braces = braces

    def add_boxes_and_labels(self):
        boxes, labels = self.get_boxes_and_labels()
        self.play(*list(map(FadeIn, [boxes, labels])))
        self.wait()

    def show_binary_choice_association(self):
        groups = self.get_groups()
        self.swapping_anims = []
        final_choices = [1, 0, 1]
        quads = list(zip(self.braces, self.denoms, groups, final_choices))
        for brace, denom, group, final_choice in quads:
            char = brace.label.args[0][1]
            choices = [
                TexMobject(
                    char, "=", sign, "\\sqrt{\\frac{1}{%d}}"%denom
                )
                for sign in ("+", "-")
            ]
            for choice, color in zip(choices, [GREEN, RED]):
                # choice[0].set_color(brace.label.get_color())
                choice[2].set_color(color)
                choice.scale(0.8)
                choice.move_to(group)
                if choice.get_width() > 0.8*group.get_width():
                    choice.next_to(group.get_right(), LEFT, buff = MED_SMALL_BUFF)
            original_choices = [m.copy() for m in choices]

            self.play(
                ReplacementTransform(
                    VGroup(brace.label[0], brace, brace.label[1]), 
                    choices[0]
                ),
                group.move_to, group.target_points[0]
            )
            self.wait()
            self.play(
                Transform(*choices),
                group.move_to, group.target_points[1]
            )
            self.wait()
            if final_choice == 0:
                self.play(
                    Transform(choices[0], original_choices[0]),
                    group.move_to, group.target_points[0]
                )
            self.swapping_anims += [
                Transform(choices[0], original_choices[1-final_choice]),
                group.move_to, group.target_points[1-final_choice]
            ]

    def ask_about_antipodal_pairs(self):
        question = TextMobject("What do antipodal points signify?")
        question.move_to(self.sphere_point_label, LEFT)
        question.set_color(MAROON_B)
        antipodal_tex = TexMobject(
            "(x, y, z) \\rightarrow (-x, -y, -z)"
        )
        antipodal_tex.next_to(question, DOWN, aligned_edge = LEFT)

        self.play(FadeOut(self.sphere_point_label))
        self.play(FadeIn(question))
        self.wait()
        self.play(Write(antipodal_tex))
        self.wait()
        self.wiggle_v_lines()
        self.wait()
        self.play(*self.swapping_anims)
        self.wait()

class SimpleRotatingSphereWithAntipodes(ExternallyAnimatedScene):
    pass

class TotalLengthOfEachJewelEquals(NecklaceDivisionSphereAssociation, ThreeDScene):
    CONFIG = {
        "random_seed" : 1,
        "thief_box_offset" : 1.2,
    }
    def construct(self):
        random.seed(self.random_seed)
        self.add_necklace()
        self.add_boxes_and_labels()
        self.find_fair_division()
        self.demonstrate_fair_division()
        self.perform_antipodal_swap()

    def find_fair_division(self):
        segments, tick_marks = self.necklace
        segments.sort()
        segment_colors = [
            segment.get_color()
            for segment in segments
        ]
        indices = self.get_fair_division_indices(segment_colors)
        groups = self.get_groups(
            [0] + list(np.array(indices)+1) + [len(segments)]
        )
        self.add(*groups)
        binary_choice = [0, 1, 0]

        v_lines = VGroup(*[DashedLine(UP, DOWN) for x in range(2)])
        v_lines.move_to(self.necklace)
        self.play(ShowCreation(v_lines))
        self.play(*[
            ApplyMethod(line.move_to, segments[index].get_right())
            for line, index in zip(v_lines, indices)
        ])
        self.wait()
        self.play(*[
            ApplyMethod(group.move_to, group.target_points[choice])
            for group, choice in zip(groups, binary_choice)
        ])
        self.wait()

        self.groups = groups
        self.v_lines = v_lines

    def get_fair_division_indices(self, colors):
        colors = np.array(list(colors))
        color_types = list(map(Color, set([c.get_hex_l() for c in colors])))
        type_to_count = dict([
            (color, sum(colors == color))
            for color in color_types
        ])
        for i1, i2 in it.combinations(list(range(1, len(colors)-1)), 2):
            bools = [
                sum(colors[i1:i2] == color) == type_to_count[color]/2
                for color in color_types
            ]
            if np.all(bools):
                return i1, i2
        raise Exception("No fair division found")

    def demonstrate_fair_division(self):
        segments, tick_marks = self.necklace
        color_types = list(map(Color, set([
            segment.get_color().get_hex_l()
            for segment in segments
        ])))
        top_segments = VGroup(*it.chain(
            self.groups[0][0],
            self.groups[2][0],
        ))
        bottom_segments = self.groups[1][0]
        for color in color_types:
            monochrome_groups = [
                VGroup(*[segment for segment in segment_group if segment.get_color() == color])
                for segment_group in (top_segments, bottom_segments)
            ]
            labels = VGroup()
            for i, group in enumerate(monochrome_groups):
                group.save_state()
                group.generate_target()
                group.target.arrange(buff = SMALL_BUFF)
                brace = Brace(group.target, UP)
                label = VGroup(
                    TextMobject("Thief %d"%(i+1)),
                    Jewel(color = group[0].get_color())
                )
                label.arrange()
                label.next_to(brace, UP)
                full_group = VGroup(group.target, brace, label)
                vect = LEFT if i == 0 else RIGHT
                full_group.next_to(ORIGIN, vect, buff = MED_LARGE_BUFF)
                full_group.to_edge(UP)
                labels.add(VGroup(brace, label))
            equals = TexMobject("=")
            equals.next_to(monochrome_groups[0].target, RIGHT)
            labels[-1].add(equals)

            for group, label in zip(monochrome_groups, labels):
                self.play(
                    MoveToTarget(group),
                    FadeIn(label),
                )
                self.wait()
            self.play(
                FadeOut(labels),
                *[group.restore for group in monochrome_groups]
            )
        self.wait()

    def perform_antipodal_swap(self):
        binary_choices_list = [(1, 0, 1), (0, 1, 0)]
        for binary_choices in binary_choices_list:
            self.play(*[
                ApplyMethod(
                    group.move_to,
                    group.target_points[choice]
                )
                for group, choice in zip(self.groups, binary_choices)
            ])
            self.wait()

class ExclaimBorsukUlam(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Borsuk-Ulam!",
            target_mode = "hooray"
        )
        self.play(*[
            ApplyMethod(pi.change_mode, "hooray")
            for pi in self.get_pi_creatures()
        ])
        self.wait(3)

class ShowFunctionDiagram(TotalLengthOfEachJewelEquals, ReconfigurableScene):
    CONFIG = {
        "necklace_center" : ORIGIN,
        "camera_class" : ThreeDCamera,
        "thief_box_offset" : 0.3,
        "make_up_fair_division_indices" : False,
    }
    def construct(self):
        self.add_necklace()
        self.add_number_pair()
        self.swap_necklace_allocation()
        self.add_sphere_arrow()

    def add_necklace(self):
        random.seed(self.random_seed)
        ChoicesInNecklaceCutting.add_necklace(self)
        self.necklace.set_width(FRAME_X_RADIUS-1)
        self.necklace.to_edge(UP, buff = LARGE_BUFF)
        self.necklace.to_edge(LEFT, buff = SMALL_BUFF)
        self.add(self.necklace)

        self.find_fair_division()

    def add_number_pair(self):
        plane_classes = [
            JewelPairPlane(
                skip_animations = True, 
                thief_number = x
            )
            for x in (1, 2)
        ]
        t1_plane, t2_plane = planes = VGroup(*[
            VGroup(*plane_class.get_top_level_mobjects())
            for plane_class in plane_classes
        ])
        planes.set_width(FRAME_X_RADIUS)
        planes.to_edge(RIGHT)
        self.example_coords = plane_classes[0].example_coords[0]

        arrow = Arrow(
            self.necklace.get_corner(DOWN+RIGHT), 
            self.example_coords,
            color = YELLOW
        )

        self.play(ShowCreation(arrow))
        self.play(Write(t1_plane), Animation(arrow))
        self.wait()
        clean_state = VGroup(*self.mobjects).family_members_with_points()
        self.clear()
        self.add(*clean_state)
        self.transition_to_alt_config(
            make_up_fair_division_indices = True
        )
        self.wait()
        t1_plane.save_state()
        self.play(
            Transform(*planes, path_arc = np.pi),
            Animation(arrow)
        )
        self.wait(2)
        self.play(
            ApplyMethod(t1_plane.restore, path_arc = np.pi),
            Animation(arrow)
        )
        self.wait()

    def swap_necklace_allocation(self):
        for choices in [(1, 0, 1), (0, 1, 0)]:
            self.play(*[
                ApplyMethod(group.move_to, group.target_points[i])
                for group, i in zip(self.groups, choices)
            ])
            self.wait()

    def add_sphere_arrow(self):
        up_down_arrow = TexMobject("\\updownarrow")
        up_down_arrow.scale(1.5)
        up_down_arrow.set_color(YELLOW)
        up_down_arrow.next_to(self.necklace, DOWN, buff = LARGE_BUFF)

        to_plane_arrow = Arrow(
            up_down_arrow.get_bottom() + DOWN+RIGHT,
            self.example_coords,
            color = YELLOW
        )

        self.play(Write(up_down_arrow))
        self.wait()
        self.play(ShowCreation(to_plane_arrow))
        self.wait()

    def get_fair_division_indices(self, *args):
        if self.make_up_fair_division_indices:
            return [9, 14]
        else:
            return TotalLengthOfEachJewelEquals.get_fair_division_indices(self, *args)

class JewelPairPlane(GraphScene):
    CONFIG = {
        "camera_class" : ThreeDCamera,
        "x_labeled_nums" : [],
        "y_labeled_nums" : [],
        "thief_number" : 1,
        "colors" : [BLUE, GREEN],
    }
    def construct(self):
        self.setup_axes()
        point = self.coords_to_point(4, 5)
        dot = Dot(point, color = WHITE)
        coord_pair = TexMobject(
            "\\big(", 
            "\\text{Thief %d }"%self.thief_number, "X", ",", 
            "\\text{Thief %d }"%self.thief_number, "X", 
            "\\big)"
        )
        # coord_pair.scale(1.5)
        to_replace = [coord_pair[i] for i in [2, 5]]
        for mob, color in zip(to_replace, self.colors):
            jewel = Jewel(color = color)
            jewel.replace(mob)
            coord_pair.remove(mob)
            coord_pair.add(jewel)
        coord_pair.next_to(dot, UP+RIGHT, buff = 0)

        self.example_coords = VGroup(dot, coord_pair)
        self.add(self.example_coords)

class WhatThisMappingActuallyLooksLikeWords(Scene):
    def construct(self):
        words = TextMobject("What this mapping actually looks like")
        words.set_width(FRAME_WIDTH-1)
        words.to_edge(DOWN)

        self.play(Write(words))
        self.wait()

class WhatAboutGeneralCase(TeacherStudentsScene):
    def construct(self):
        self.student_says("""
            What about when
            there's more than 2 jewels?
        """)
        self.change_student_modes("confused", None, "sassy")
        self.wait()
        self.play(self.get_teacher().change_mode, "thinking")
        self.wait()
        self.teacher_says(
            """Use Borsuk-Ulam for
            higher-dimensional spheres """, 
            target_mode = "hooray"
        )
        self.change_student_modes(*["confused"]*3)
        self.wait(2)

class Simple3DSpace(ExternallyAnimatedScene):
    pass

class FourDBorsukUlam(GeneralizeBorsukUlam, PiCreatureScene):
    CONFIG = {
        "n_dims" : 4,
        "use_morty" : False,
    }
    def setup(self):
        GeneralizeBorsukUlam.setup(self)
        PiCreatureScene.setup(self)
        self.pi_creature.to_corner(DOWN+LEFT, buff = MED_SMALL_BUFF)

    def construct(self):
        sphere_set = self.get_sphere_set()
        arrow = Arrow(LEFT, RIGHT)
        f = TexMobject("f")
        output_space = self.get_output_space()
        equation = self.get_equation()

        sphere_set.to_corner(UP+LEFT)
        arrow.next_to(sphere_set, RIGHT)
        f.next_to(arrow, UP)
        output_space.next_to(arrow, RIGHT)
        equation.next_to(sphere_set, DOWN, buff = LARGE_BUFF)
        equation.to_edge(RIGHT)
        lhs = VGroup(*equation[:2])
        eq = equation[2]
        rhs = VGroup(*equation[3:])

        brace = Brace(Line(ORIGIN, 5*RIGHT))
        brace.to_edge(RIGHT)
        brace_text = brace.get_text("Triplets of numbers")
        brace_text.shift_onto_screen()

        self.play(FadeIn(sphere_set))
        self.change_mode("confused")
        self.wait()
        self.play(
            ShowCreation(arrow),
            Write(f)
        )
        self.play(Write(output_space))
        self.wait()
        self.change_mode("maybe")
        self.wait(2)
        self.change_mode("pondering")
        self.wait()
        self.play(
            GrowFromCenter(brace),
            Write(brace_text)
        )
        self.wait()
        self.play(*list(map(FadeOut, [brace, brace_text])))
        self.wait()
        self.play(
            FadeIn(lhs),
            self.pi_creature.change_mode, "raise_right_hand"
        )
        self.play(
            ReplacementTransform(lhs.copy(), rhs),
            Write(eq)
        )
        self.wait(2)

    def get_sphere_set(self):
        sphere_set = GeneralizeBorsukUlam.get_sphere_set(self)
        brace = Brace(sphere_set)
        text = brace.get_text("Hypersphere in 4D")
        sphere_set.add(brace, text)
        return sphere_set

class CircleToSphereToQMarks(Scene):
    def construct(self):
        pi_groups = VGroup()
        modes = ["happy", "pondering", "pleading"]
        shapes = [
            Circle(color = BLUE, radius = 0.5), 
            VectorizedPoint(), 
            TexMobject("???")
        ]
        for d, mode, shape in zip(it.count(2), modes, shapes):
            randy = Randolph(mode = mode)
            randy.scale(0.7)
            bubble = randy.get_bubble(
                height = 3, width = 4,
                direction = LEFT
            )
            bubble.pin_to(randy)
            bubble.position_mobject_inside(shape)
            title = TextMobject("%dD"%d)
            title.next_to(randy, UP)
            arrow = Arrow(LEFT, RIGHT)
            arrow.next_to(randy.get_corner(UP+RIGHT))
            pi_groups.add(VGroup(
                randy, bubble, shape, title, arrow
            ))

        pi_groups[-1].remove(pi_groups[-1][-1])
        pi_groups.arrange(buff = -1)
        for mob in pi_groups:
            self.play(FadeIn(mob))
        self.wait(2)
        self.play(pi_groups[-1][0].change_mode, "thinking")
        self.wait(2)

class BorsukPatreonThanks(PatreonThanks):
    CONFIG = {
        "specific_patrons" : [
            "Ali  Yahya",
            "Meshal  Alshammari",
            "CrypticSwarm    ",
            "Ankit   Agarwal",
            "Yu  Jun",
            "Shelby  Doolittle",
            "Dave    Nicponski",
            "Damion  Kistler",
            "Juan    Benet",
            "Othman  Alikhan",
            "Justin Helps",
            "Markus  Persson",
            "Dan Buchoff",
            "Derek   Dai",
            "Joseph  John Cox",
            "Luc Ritchie",
            "Guido   Gambardella",
            "Jerry   Ling",
            "Mark    Govea",
            "Vecht",
            "Jonathan    Eppele",
            "Shimin Kuang",
            "Rish    Kundalia",
            "Achille Brighton",
            "Kirk    Werklund",
            "Ripta   Pasay",
            "Felipe  Diniz",
        ]
    }

class MortyLookingAtRectangle(Scene):
    def construct(self):
        morty = Mortimer()
        morty.to_corner(DOWN+RIGHT)
        url = TextMobject("www.thegreatcoursesplus.com/3blue1brown")
        url.scale(0.75)
        url.to_corner(UP+LEFT)
        rect = Rectangle(height = 9, width = 16)
        rect.set_height(5)
        rect.next_to(url, DOWN)
        rect.shift_onto_screen()
        url.save_state()
        url.next_to(morty.get_corner(UP+LEFT), UP)
        url.shift_onto_screen()

        self.add(morty)
        self.play(
            morty.change_mode, "raise_right_hand",
            morty.look_at, url,
        )
        self.play(Write(url))
        self.play(Blink(morty))
        self.wait()
        self.play(
            url.restore,
            morty.change_mode, "happy"
        )
        self.play(ShowCreation(rect))
        self.wait()
        self.play(Blink(morty))
        for mode in ["pondering", "hooray", "happy", "pondering", "happy"]:
            self.play(morty.change_mode, mode)
            self.wait(2)
            self.play(Blink(morty))
            self.wait(2)

class RotatingThreeDSphereProjection(Scene):
    CONFIG = {
        "camera_class" : ThreeDCamera,
    }
    def construct(self):
        sphere = VGroup(*[
            Circle(radius = np.sin(t)).shift(np.cos(t)*OUT)
            for t in np.linspace(0, np.pi, 20)
        ])
        sphere.set_stroke(BLUE, width = 2)
        # sphere.set_fill(BLUE, opacity = 0.1)

        self.play(Rotating(
            sphere, axis = RIGHT+OUT,
            run_time = 10
        ))
        self.repeat_frames(4)

class FourDSphereProjectTo4D(ExternallyAnimatedScene):
    pass


class Test(Scene):
    CONFIG = {
        "camera_class" : ThreeDCamera,
    }
    def construct(self):
        randy = Randolph()
        necklace = Necklace()
        necklace.insert_n_curves(20)
        # necklace.apply_function(
        #     lambda (x, y, z) : x*RIGHT + (y + 0.1*x**2)*UP
        # )
        necklace.set_width(randy.get_width() + 1)
        necklace.move_to(randy)

        self.add(randy, necklace)













