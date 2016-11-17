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
from topics.objects import *
from scene import Scene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

class CountingScene(Scene):
    CONFIG = {
        "base" : 10,
        "power_colors" : [YELLOW, MAROON_B, RED, GREEN, BLUE, PURPLE_D],
        "counting_dot_starting_position" : (SPACE_WIDTH-1)*RIGHT + (SPACE_HEIGHT-1)*UP,
        "count_dot_starting_radius" : 0.5,
        "dot_configuration_height" : 2,
        "ones_configuration_location" : UP+2*RIGHT,
        "num_scale_factor" : 2,
        "num_start_location" : 2*DOWN,
    }
    def setup(self):
        self.dots = VGroup()
        self.number = 0        
        self.number_mob = VGroup(TexMobject(str(self.number)))
        self.number_mob.scale(self.num_scale_factor)
        self.number_mob.shift(self.num_start_location)
        self.digit_width = self.number_mob.get_width()

        self.initialize_configurations()
        self.arrows = VGroup()
        self.add(self.number_mob)

    def get_template_configuration(self):
        #This should probably be replaced for non-base-10 counting scenes
        down_right = (0.5)*RIGHT + (np.sqrt(3)/2)*DOWN
        result = []
        for down_right_steps in range(5):
            for left_steps in range(down_right_steps):
                result.append(
                    down_right_steps*down_right + left_steps*LEFT
                )
        return reversed(result[:self.base])

    def get_dot_template(self):
        #This should be replaced for non-base-10 counting scenes
        down_right = (0.5)*RIGHT + (np.sqrt(3)/2)*DOWN
        dots = VGroup(*[
            Dot(
                point, 
                radius = 0.25,
                fill_opacity = 0,
                stroke_width = 2,
                stroke_color = WHITE,
            )
            for point in self.get_template_configuration()
        ])
        dots.scale_to_fit_height(self.dot_configuration_height)
        return dots

    def initialize_configurations(self):
        self.dot_templates = []
        self.dot_template_iterators = []
        self.curr_configurations = []

    def add_configuration(self):
        new_template = self.get_dot_template()
        new_template.move_to(self.ones_configuration_location)
        left_vect = (new_template.get_width()+LARGE_BUFF)*LEFT
        new_template.shift(
            left_vect*len(self.dot_templates)
        )
        self.dot_templates.append(new_template)
        self.dot_template_iterators.append(
            it.cycle(new_template)
        )
        self.curr_configurations.append(VGroup())

    def count(self, max_val, run_time_per_anim = 1):
        for x in range(max_val):
            self.increment(run_time_per_anim)

    def increment(self, run_time_per_anim = 1, added_anims = [], total_run_time = None):
        if total_run_time is not None:
            num_rollovers = self.get_num_rollovers()
            run_time_per_anim = float(total_run_time)/(num_rollovers+1)
        moving_dot = Dot(
            self.counting_dot_starting_position,
            radius = self.count_dot_starting_radius,
            color = self.power_colors[0],
        )
        moving_dot.generate_target()
        moving_dot.set_fill(opacity = 0)
        kwargs = {
            "run_time" : run_time_per_anim
        }

        continue_rolling_over = True
        first_move = True
        place = 0
        while continue_rolling_over:              
            if first_move:
                added_anims = list(
                    self.get_digit_increment_animations()+\
                    added_anims
                )
                first_move = False
            moving_dot.target.replace(
                self.dot_template_iterators[place].next()
            )
            self.play(MoveToTarget(moving_dot), *added_anims, **kwargs)
            self.curr_configurations[place].add(moving_dot)
            added_anims = []


            if len(self.curr_configurations[place].split()) == self.base:
                full_configuration = self.curr_configurations[place]
                self.curr_configurations[place] = VGroup()
                place += 1
                center = full_configuration.get_center_of_mass()
                radius = 0.6*max(
                    full_configuration.get_width(),
                    full_configuration.get_height(),
                )
                circle = Circle(
                    radius = radius,
                    stroke_width = 0,
                    fill_color = self.power_colors[place],
                    fill_opacity = 0.5,
                )
                circle.move_to(center)
                moving_dot = VGroup(circle, full_configuration)
                moving_dot.generate_target()
                moving_dot[0].set_fill(opacity = 0)
            else:
                continue_rolling_over = False

    def get_digit_increment_animations(self):
        result = []
        self.number += 1
        new_number_mob = self.get_number_mob(self.number)
        new_number_mob.move_to(self.number_mob, RIGHT)
        if self.is_perfect_power():
            self.add_configuration()
            place = len(new_number_mob.split())-1
            result.append(FadeIn(self.dot_templates[place]))
            arrow = Arrow(
                new_number_mob[place].get_top(),
                self.dot_templates[place].get_bottom(),
                color = self.power_colors[place]
            )
            self.arrows.add(arrow)
            result.append(ShowCreation(arrow))
        result.append(Transform(
            self.number_mob, new_number_mob,
            submobject_mode = "lagged_start"
        ))
        return result

    def get_number_mob(self, num):
        result = VGroup()
        place = 0
        while num > 0:
            digit = TexMobject(str(num % self.base))
            if place >= len(self.power_colors):
                self.power_colors += self.power_colors
            digit.highlight(self.power_colors[place])
            digit.scale(self.num_scale_factor)
            digit.move_to(result, RIGHT)
            digit.shift(place*(self.digit_width+SMALL_BUFF)*LEFT)
            result.add(digit)
            num /= self.base
            place += 1
        return result

    def is_perfect_power(self):
        number = self.number
        while number > 1:
            if number%self.base != 0:
                return False
            number /= self.base
        return True

    def get_num_rollovers(self):
        next_number = self.number + 1
        result = 0
        while next_number%self.base == 0:
            result += 1
            next_number /= self.base
        return result

class BinaryCountingScene(CountingScene):
    CONFIG = {
        "base" : 2,
        "dot_configuration_height" : 1,
        "ones_configuration_location" : UP+5*RIGHT
    }
    def get_template_configuration(self):
        return [ORIGIN, UP]

class CountInDecimal(CountingScene):
    def construct(self):
        for x in range(11):
            self.increment()
        for x in range(85):
            self.increment(0.25)
        for x in range(20):
            self.increment()

class CountInTernary(CountingScene):
    CONFIG = {
        "base" : 3,
        "dot_configuration_height" : 1,
        "ones_configuration_location" : UP+4*RIGHT
    }
    def construct(self):
        self.count(27)

    # def get_template_configuration(self):
    #     return [ORIGIN, UP]

class CountInBinaryTo256(BinaryCountingScene):
    def construct(self):
        self.count(256, 0.25)

class TowersOfHanoiScene(Scene):
    CONFIG = {
        "disk_start_and_end_colors" : [BLUE_E, BLUE_A],
        "num_disks" : 5,
        "peg_width" : 0.25,
        "peg_height" : 2.5,
        "disk_height" : 0.4,
        "disk_min_width" : 1,
        "disk_max_width" : 3,
    }
    def setup(self):
        self.add_pegs()
        self.add_disks()

    def add_pegs(self):
        peg = Rectangle(
            height = self.peg_height,
            width = self.peg_width, 
            stroke_width = 0,
            fill_color = GREY_BROWN,
            fill_opacity = 1,
        )
        peg.shift(UP)
        self.pegs = VGroup(*[
            peg.copy().shift(vect)
            for vect in 4*LEFT, ORIGIN, 4*RIGHT
        ])
        self.peg_labels = VGroup(*[
            TexMobject(char).next_to(peg, DOWN)
            for char, peg in zip("ABC", self.pegs)
        ])
        self.add(self.pegs, self.peg_labels)

    def add_disks(self):
        self.disks = VGroup(*[
            Rectangle(
                height = self.disk_height,
                width = width,
                fill_color = color,
                fill_opacity = 0.8,
                stroke_width = 0,
            )
            for width, color in zip(
                np.linspace(
                    self.disk_min_width, 
                    self.disk_max_width,
                    self.num_disks
                ),
                color_gradient(
                    self.disk_start_and_end_colors,
                    self.num_disks
                )
            )
        ])
        for number, disk in enumerate(self.disks):
            label = TexMobject(str(number))
            label.highlight(BLACK)
            label.scale_to_fit_height(self.disk_height/2)
            label.move_to(disk)
            disk.add(label)
            disk.label = label
        self.reset_disks(run_time = 0)

        self.add(self.disks)

    def reset_disks(self, **kwargs):
        self.disks.generate_target()
        self.disks.target.arrange_submobjects(DOWN, buff = 0)
        self.disks.target.move_to(self.pegs[0], DOWN)
        self.play(
            MoveToTarget(self.disks), 
            **kwargs
        )
        self.disk_tracker = [
            set(range(self.num_disks)),
            set([]),
            set([])
        ]

    def disk_index_to_peg_index(self, disk_index):
        for index, disk_set in enumerate(self.disk_tracker):
            if disk_index in disk_set:
                return index
        raise Exception("Somehow this disk wasn't accounted for...")

    def min_disk_index_on_peg(self, peg_index):
        disk_index_set = self.disk_tracker[peg_index]
        if disk_index_set:
            return min(self.disk_tracker[peg_index])
        else:
            return self.num_disks

    def bottom_point_for_next_disk(self, peg_index):
        min_disk_index = self.min_disk_index_on_peg(peg_index)
        if min_disk_index >= self.num_disks:
            return self.pegs[peg_index].get_bottom()
        else:
            return self.disks[min_disk_index].get_top()


    def get_next_disk_0_peg(self):
        curr_peg_index = self.disk_index_to_peg_index(0)
        return (curr_peg_index+1)%3

    def get_available_peg(self, disk_index):
        if disk_index == 0:
            return self.get_next_disk_0_peg()
        for index in range(len(list(self.pegs))):
            if self.min_disk_index_on_peg(index) > disk_index:
                return index
        raise Exception("Tower's of Honoi rule broken: No available disks")

    def move_disk(self, disk_index, **kwargs):
        next_peg_index = self.get_available_peg(disk_index)
        self.move_disk_to_peg(disk_index, next_peg_index, **kwargs)

    def move_subtower_to_peg(self, num_disks, next_peg_index, **kwargs):
        disk_indices = range(num_disks)
        peg_indices = map(self.disk_index_to_peg_index, disk_indices)
        if len(set(peg_indices)) != 1:
            warnings.warn("These disks don't make up a tower right now")
        self.move_disks_to_peg(disk_indices, next_peg_index, **kwargs)

    def move_disk_to_peg(self, disk_index, next_peg_index, **kwargs):
        self.move_disks_to_peg([disk_index], next_peg_index, **kwargs)

    def move_disks_to_peg(self, disk_indices, next_peg_index, run_time = 1, stay_on_peg = True, added_anims = []):
        disks = VGroup(*[self.disks[index] for index in disk_indices])
        max_disk_index = max(disk_indices)
        next_peg = self.pegs[next_peg_index]        
        curr_peg_index = self.disk_index_to_peg_index(max_disk_index)
        curr_peg = self.pegs[curr_peg_index]
        if self.min_disk_index_on_peg(curr_peg_index) != max_disk_index:
            warnings.warn("Tower's of Hanoi rule broken: disk has crap on top of it")
        target_bottom_point = self.bottom_point_for_next_disk(next_peg_index)
        path_arc = np.sign(curr_peg_index-next_peg_index)*np.pi/3
        if stay_on_peg:
            self.play(
                Succession(
                    ApplyMethod(disks.next_to, curr_peg, UP, 0),
                    ApplyMethod(disks.next_to, next_peg, UP, 0, path_arc = path_arc),
                    ApplyMethod(disks.move_to, target_bottom_point, DOWN),
                ),
                *added_anims,
                run_time = run_time,
                rate_func = lambda t : smooth(t, 2)
            )
        else:
            self.play(
                ApplyMethod(disks.move_to, target_bottom_point, DOWN),
                *added_anims,
                path_arc = path_arc*2,
                run_time = run_time,
                rate_func = lambda t : smooth(t, 2)
            )
        for disk_index in disk_indices:
            self.disk_tracker[curr_peg_index].remove(disk_index)
            self.disk_tracker[next_peg_index].add(disk_index)

class ConstrainedTowersOfHanoiScene(TowersOfHanoiScene):
    def get_next_disk_0_peg(self):
        if not hasattr(self, "total_disk_0_movements"):
            self.total_disk_0_movements = 0
        curr_peg_index = self.disk_index_to_peg_index(0)        
        if (self.total_disk_0_movements/2)%2 == 0:
            result = curr_peg_index + 1
        else:
            result = curr_peg_index - 1
        self.total_disk_0_movements += 1
        return result

def get_ruler_sequence(order = 4):
    if order == -1:
        return []
    else:
        smaller = get_ruler_sequence(order - 1)
        return smaller + [order] + smaller

def get_ternary_ruler_sequence(order = 4):
    if order == -1:
        return []
    else:
        smaller = get_ternary_ruler_sequence(order-1)
        return smaller+[order]+smaller+[order]+smaller

class SolveHanoi(TowersOfHanoiScene):
    def construct(self):
        self.dither()
        for x in get_ruler_sequence(self.num_disks-1):
            self.move_disk(x, stay_on_peg = False)
        self.dither()

class SolveConstrainedHanoi(ConstrainedTowersOfHanoiScene):
    def construct(self):
        self.dither()
        for x in get_ternary_ruler_sequence(self.num_disks-1):
            self.move_disk(x, run_time = 0.5, stay_on_peg = False)
        self.dither()

class Keith(PiCreature):
    CONFIG = {
        "color" : GREEN_D
    }
        
def get_binary_tex_mobs(num_list):
    result = VGroup()
    zero_width = TexMobject("0").get_width()
    nudge = zero_width + SMALL_BUFF
    for num in num_list:
        bin_string = bin(num)[2:]#Strip off the "0b" prefix
        bits = VGroup(*map(TexMobject, bin_string))
        for n, bit in enumerate(bits):
            bit.shift(n*nudge*RIGHT)
        bits.move_to(ORIGIN, RIGHT)
        result.add(bits)
    return result


####################

class IntroduceKeith(Scene):
    def construct(self):
        morty = Mortimer(mode = "happy")
        keith = Keith(mode = "dance_kick")
        keith_image = ImageMobject("keith_schwarz", invert = False)
        # keith_image = Rectangle()
        keith_image.scale_to_fit_height(2*SPACE_HEIGHT - 2)
        keith_image.next_to(ORIGIN, LEFT)
        keith.move_to(keith_image, DOWN+RIGHT)
        morty.next_to(keith, buff = LARGE_BUFF, aligned_edge = DOWN)
        morty.make_eye_contact(keith)
        randy = Randolph().next_to(keith, LEFT, LARGE_BUFF, aligned_edge = DOWN)
        randy.shift_onto_screen()

        bubble = keith.get_bubble("speech")
        bubble.write("Check this out...")
        bubble.resize_to_content()
        bubble.pin_to(keith)
        VGroup(bubble, bubble.content).shift(DOWN)

        randy.bubble = randy.get_bubble("speech", height = 3)
        randy.bubble.write("Wait, what's \\\\ Towers of Hanoi?")

        title = TextMobject("Keith Schwarz (Computer scientist)")
        title.to_edge(UP)

        self.add(keith_image, morty)
        self.play(Write(title))
        self.play(FadeIn(keith, run_time = 2))
        self.play(FadeOut(keith_image), Animation(keith))
        self.play(Blink(morty))
        self.play(
            keith.change_mode, "speaking",
            keith.scale_to_fit_height, morty.get_height(),
            keith.next_to, morty, LEFT, LARGE_BUFF,
            run_time = 1.5
        )
        self.play(
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.play(
            morty.change_mode, "pondering",
            morty.look_at, bubble
        )
        self.play(Blink(keith))
        self.dither()
        self.play(FadeIn(randy))
        self.play(
            randy.change_mode, "confused",
            randy.look_at, keith.eyes,
            keith.change_mode, "plain",
            keith.look_at, randy.eyes,
            morty.change_mode, "plain",
            morty.look_at, randy.eyes,
            FadeOut(bubble),
            FadeOut(bubble.content),
            ShowCreation(randy.bubble),
            Write(randy.bubble.content)
        )
        self.play(Blink(keith))
        self.play(
            keith.change_mode, "hooray",
            keith.look_at, randy.eyes
        )
        self.dither()

class IntroduceTowersOfHanoi(TowersOfHanoiScene):
    def construct(self):
        self.clear()
        self.add_title()
        self.show_setup()
        self.note_disk_labels()
        self.show_more_disk_possibility()
        self.move_full_tower()
        self.move_single_disk()
        self.cannot_move_disk_onto_smaller_disk()

    def add_title(self):
        title = TextMobject("Towers of Hanoi")
        title.to_edge(UP)
        self.add(title)
        self.title = title

    def show_setup(self):
        self.pegs.save_state()
        bottom = self.pegs.get_bottom()
        self.pegs.stretch_to_fit_height(0)
        self.pegs.move_to(bottom)
        self.play(
            ApplyMethod(
                self.pegs.restore, 
                submobject_mode = "lagged_start",
                run_time = 2
            ),
            Write(self.peg_labels)
        )
        self.dither()
        self.bring_in_disks()
        self.dither()

    def bring_in_disks(self):
        peg = self.pegs[0]
        disk_groups = VGroup()
        for disk in self.disks:
            top = Circle(radius = disk.get_width()/2)
            inner = Circle(radius = self.peg_width/2)
            inner.flip()
            top.add_subpath(inner.points)
            top.set_stroke(width = 0)
            top.set_fill(disk.get_color())
            top.rotate(np.pi/2, RIGHT)
            top.move_to(disk, UP)
            bottom = top.copy()
            bottom.move_to(disk, DOWN)
            group = VGroup(disk, top, bottom)
            group.truly_original_state = group.copy()
            group.next_to(peg, UP, 0)
            group.rotate_in_place(-np.pi/24, RIGHT)
            group.save_state()
            group.rotate_in_place(-11*np.pi/24, RIGHT)
            disk.set_fill(opacity = 0)
            disk_groups.add(group)
        disk_groups.arrange_submobjects()
        disk_groups.next_to(self.peg_labels, DOWN)
        
        self.play(FadeIn(
            disk_groups, 
            run_time = 2, 
            submobject_mode = "lagged_start"
        ))
        for group in reversed(list(disk_groups)):
            self.play(group.restore)
            self.play(Transform(group, group.truly_original_state))
        self.remove(disk_groups)
        self.add(self.disks)

    def note_disk_labels(self):
        labels = [disk.label for disk in self.disks]
        last = VGroup().save_state()
        for label in labels:
            label.save_state()
            self.play(
                label.scale_in_place, 2,
                label.highlight, YELLOW,
                last.restore,
                run_time = 0.5
            )
            last = label
        self.play(last.restore)
        self.dither()

    def show_more_disk_possibility(self):
        original_num_disks = self.num_disks
        original_disk_height = self.disk_height
        original_disks = self.disks
        original_disks_copy = original_disks.copy()

        #Hacky
        self.num_disks = 10
        self.disk_height = 0.3
        self.add_disks()
        new_disks = self.disks
        self.disks = original_disks
        self.remove(new_disks)

        self.play(Transform(self.disks, new_disks))
        self.dither()
        self.play(Transform(self.disks, original_disks_copy))

        self.remove(self.disks)
        self.disks = original_disks_copy
        self.add(self.disks)
        self.dither()

        self.num_disks = original_num_disks
        self.disk_height = original_disk_height

    def move_full_tower(self):
        self.move_subtower_to_peg(self.num_disks, 1, run_time = 2)
        self.dither()
        self.reset_disks(run_time = 1, submobject_mode = "lagged_start")
        self.dither()

    def move_single_disk(self):
        for x in 0, 1, 0:
            self.move_disk(x)
        self.dither()

    def cannot_move_disk_onto_smaller_disk(self):
        also_not_allowed = TextMobject("Not allowed")
        also_not_allowed.to_edge(UP)
        also_not_allowed.highlight(RED)
        cross = TexMobject("\\times")
        cross.set_fill(RED, opacity = 0.5)

        disk = self.disks[2]
        disk.save_state()
        self.move_disks_to_peg([2], 2, added_anims = [
            Transform(self.title, also_not_allowed, run_time = 1)
        ])
        cross.replace(disk)
        self.play(FadeIn(cross))
        self.dither()
        self.play(
            FadeOut(cross),
            FadeOut(self.title),
            disk.restore
        )
        self.dither()

class ExampleFirstMoves(TowersOfHanoiScene):
    def construct(self):
        ruler_sequence = get_ruler_sequence(4)
        cross = TexMobject("\\times")
        cross.set_fill(RED, 0.7)

        self.dither()
        self.play(
            self.disks[0].set_fill, YELLOW,
            self.disks[0].label.highlight, BLACK
        )
        self.dither()
        self.move_disk(0)
        self.dither()
        self.play(
            self.disks[1].set_fill, YELLOW_D,
            self.disks[1].label.highlight, BLACK
        )
        self.move_disk_to_peg(1, 1)
        cross.replace(self.disks[1])
        self.play(FadeIn(cross))
        self.dither()
        self.move_disk_to_peg(1, 2, added_anims = [FadeOut(cross)])
        self.dither()
        for x in ruler_sequence[2:9]:
            self.move_disk(x)
        for x in ruler_sequence[9:]:
            self.move_disk(x, run_time = 0.5, stay_on_peg = False)
        self.dither()

class KeithShowingBinary(Scene):
    def construct(self):
        keith = Keith()
        morty = Mortimer()
        morty.to_corner(DOWN+RIGHT)
        keith.next_to(morty, LEFT, buff = 2*LARGE_BUFF)
        randy = Randolph()
        randy.next_to(keith, LEFT, buff = 2*LARGE_BUFF)
        randy.bubble = randy.get_bubble("speech")
        randy.bubble.set_fill(BLACK, opacity = 1)
        randy.bubble.write("Hold on...how does \\\\ binary work again?")

        binary_tex_mobs = get_binary_tex_mobs(range(16))
        binary_tex_mobs.shift(keith.get_corner(UP+LEFT))
        binary_tex_mobs.shift(0.5*(UP+RIGHT))
        bits_list = binary_tex_mobs.split()
        bits = bits_list.pop(0)

        def get_bit_flip():
            return Transform(
                bits, bits_list.pop(0),
                rate_func = squish_rate_func(smooth, 0, 0.7)
            )

        self.play(
            keith.change_mode, "wave_1",
            keith.look_at, bits,
            morty.look_at, bits,
            Write(bits)
        )
        for x in range(2):
            self.play(get_bit_flip())
        self.play(
            morty.change_mode, "pondering",
            morty.look_at, bits,
            get_bit_flip()
        )
        while bits_list:
            added_anims = []
            if random.random() < 0.2:
                if random.random() < 0.5:
                    added_anims.append(Blink(keith))
                else:
                    added_anims.append(Blink(morty))
            self.play(get_bit_flip(), *added_anims)
        self.dither()
        self.play(
            FadeIn(randy),
            morty.change_mode, "plain",
            morty.look_at, randy.eyes,
            keith.change_mode, "plain",
            keith.look_at, randy.eyes,
        )
        self.play(
            randy.change_mode, "confused",
            ShowCreation(randy.bubble),
            Write(randy.bubble.content)
        )
        self.play(Blink(randy))
        self.dither()
        self.play(morty.change_mode, "hooray")
        self.play(Blink(morty))
        self.dither()

class FocusOnRhythm(Scene):
    def construct(self):
        title = TextMobject("Focus on rhythm")
        title.scale(1.5)
        letters = list(reversed(title[-6:]))
        self.play(Write(title, run_time = 1))
        sequence = get_ruler_sequence(5)
        for x in sequence:
            movers = VGroup(*letters[:x+1])
            self.play(
                movers.shift, 0.2*DOWN,
                rate_func = there_and_back,
                run_time = 0.25
            )

class IntroduceBase10(Scene):
    def construct(self):
        self.expand_example_number()
        self.list_digits()

    def expand_example_number(self):
        title = TextMobject("``Base 10''")
        title.to_edge(UP)
        number = TexMobject("137")
        number.next_to(title, DOWN)
        number.shift(2*LEFT)

        colors = [RED, MAROON_B, YELLOW]
        expansion = TexMobject(
            "1(100) + ",
            "3(10) + ",
            "7"
        )
        expansion.next_to(number, DOWN, buff = LARGE_BUFF, aligned_edge = RIGHT)        
        arrows = VGroup()
        number.generate_target()

        for color, digit, term in zip(colors, number.target, expansion):
            digit.highlight(color)
            term.highlight(color)
            arrow = Arrow(digit, term.get_top())
            arrow.highlight(color)
            arrows.add(arrow)
        expansion.save_state()
        for digit, term in zip(number, expansion):
            Transform(term, digit).update(1)

        self.play(
            MoveToTarget(number),
            ShowCreation(arrows),
            ApplyMethod(
                expansion.restore, submobject_mode = "lagged_start"),
            run_time = 2
        )
        self.play(Write(title))
        self.dither()
        self.title = title

    def list_digits(self):
        digits = TextMobject("""
            0, 1, 2, 3, 4,
            5, 6, 7, 8, 9
        """)
        digits.next_to(self.title, DOWN, buff = LARGE_BUFF)
        digits.shift(2*RIGHT)
        self.play(Write(digits, lag_factor = 5))
        self.dither()

class RhythmOfDecimalCounting(CountingScene):
    CONFIG = {
        "ones_configuration_location" : 2*UP+2*RIGHT,
        "num_start_location" : DOWN
    }
    def construct(self):
        for x in range(10):
            self.increment()
        brace = Brace(self.number_mob)
        two_digits = brace.get_text("Two digits")
        one_brace = Brace(self.number_mob[-1])
        tens_place = one_brace.get_text("Ten's place")
        ten_group = self.curr_configurations[1][0]

        self.play(
            GrowFromCenter(brace),
            Write(two_digits, run_time = 1)
        )
        self.dither(2)
        self.play(
            Transform(brace, one_brace),
            Transform(two_digits, tens_place)
        )
        self.dither()
        ten_group.save_state()
        self.play(
            ten_group.scale_in_place, 7,
            ten_group.shift, 2*(DOWN+LEFT),
        )
        self.dither()
        self.play(
            ten_group.restore,
            *map(FadeOut, [brace, two_digits])
        )

        for x in range(89):
            self.increment(run_time_per_anim = 0.25)
        self.increment(run_time_per_anim = 1)
        self.dither()

        hundred_group = self.curr_configurations[2][0]
        hundred_group.save_state()
        self.play(
            hundred_group.scale, 14,
            hundred_group.to_corner, DOWN+LEFT
        )
        self.dither()
        self.play(hundred_group.restore)
        self.dither()
        groups = [
            VGroup(*pair)
            for pair in zip(self.dot_templates, self.curr_configurations)
        ]
        self.play(
            groups[2].to_edge, RIGHT,
            MaintainPositionRelativeTo(groups[1], groups[2]),
            MaintainPositionRelativeTo(groups[0], groups[2]),
            self.number_mob.to_edge, RIGHT, LARGE_BUFF,
            FadeOut(self.arrows)
        )

class DecimalCountingAtHundredsScale(CountingScene):
    CONFIG = {
        "power_colors" : [RED, GREEN, BLUE, PURPLE_D],
        "counting_dot_starting_position" : (SPACE_WIDTH+1)*RIGHT + (SPACE_HEIGHT-2)*UP,
        "ones_configuration_location" : 2*UP+5.7*RIGHT,
        "num_start_location" : DOWN + 3*RIGHT
    }
    def construct(self):
        added_zeros = TexMobject("00")
        added_zeros.scale(self.num_scale_factor)
        added_zeros.next_to(self.number_mob, RIGHT, SMALL_BUFF, aligned_edge = DOWN)
        added_zeros.gradient_highlight(MAROON_B, YELLOW)
        self.add(added_zeros)
        self.increment(run_time_per_anim = 0)

        VGroup(self.number_mob, added_zeros).to_edge(RIGHT, buff = LARGE_BUFF)
        VGroup(self.dot_templates[0], self.curr_configurations[0]).to_edge(RIGHT)
        Transform(
            self.arrows[0], 
            Arrow(self.number_mob, self.dot_templates[0], color = self.power_colors[0])
        ).update(1)

        for x in range(10):
            this_range = range(8) if x == 0 else range(9)
            for y in this_range:
                self.increment(run_time_per_anim = 0.25)
            self.increment(run_time_per_anim = 1)

class IntroduceBinaryCounting(BinaryCountingScene):
    CONFIG = {
        "ones_configuration_location" : UP+5*RIGHT,
        "num_start_location" : DOWN+2*RIGHT
    }
    def construct(self):
        self.introduce_name()
        self.initial_counting()
        self.rhtyhm_of_counting()

    def introduce_name(self):
        title = TextMobject("Binary (base 2):", "0, 1")
        title.to_edge(UP)
        self.add(title)
        self.number_mob.set_fill(opacity = 0)

        brace = Brace(title[1], buff = SMALL_BUFF)
        bits = TextMobject("bi", "ts", arg_separator = "")
        bits.submobjects.insert(1, VectorizedPoint(bits.get_center()))
        binary_digits = TextMobject("bi", "nary digi", "ts", arg_separator = "")
        for mob in bits, binary_digits:
            mob.next_to(brace, DOWN, buff = SMALL_BUFF)
        VGroup(brace, bits, binary_digits).highlight(BLUE)
        binary_digits[1].highlight(BLUE_E)
        self.play(
            GrowFromCenter(brace),
            Write(bits)
        )
        self.dither()
        bits.save_state()
        self.play(Transform(bits, binary_digits))
        self.dither()
        self.play(bits.restore)
        self.dither()


        # for x in range(16):
        #     self.increment(0.5)

    def initial_counting(self):
        randy = Randolph().to_corner(DOWN+LEFT)
        bubble = randy.get_bubble("thought", height = 3.4, width = 5)
        bubble.write(
            "Not ten, not ten \\\\",
            "\\quad not ten, not ten..."
        )

        self.play(self.number_mob.set_fill, self.power_colors[0], 1)
        self.increment()
        self.dither()

        ##Up to 10
        self.increment()
        brace = Brace(self.number_mob[1])
        twos_place = brace.get_text("Two's place")
        self.play(
            GrowFromCenter(brace),
            Write(twos_place)
        )
        self.play(
            FadeIn(randy),
            ShowCreation(bubble)
        )
        self.play(
            randy.change_mode, "hesitant",
            randy.look_at, self.number_mob,
            Write(bubble.content)
        )
        self.dither()
        curr_content = bubble.content
        bubble.write("$1 \\! \\cdot \\! 2+$", "$0$")
        bubble.content[0][0].highlight(self.power_colors[1])
        self.play(
            Transform(curr_content, bubble.content),
            randy.change_mode, "pondering",
            randy.look_at, self.number_mob
        )
        self.remove(curr_content)
        self.add(bubble.content)

        #Up to 11
        zero = bubble.content[-1]
        zero.highlight(self.power_colors[0])
        one = TexMobject("1").replace(zero, dim_to_match = 1)
        one.highlight(zero.get_color())
        self.play(Blink(randy))
        self.increment(added_anims = [Transform(zero, one)])
        self.dither()

        #Up to 100
        curr_content = bubble.content
        bubble.write(
            "$1 \\!\\cdot\\! 4 + $",
            "$0 \\!\\cdot\\! 2 + $",
            "$0$",
        )
        for piece, color in zip(bubble.content.submobjects, self.power_colors):
            piece[0].highlight(color)
        self.increment(added_anims = [Transform(curr_content, bubble.content)])
        four_brace = Brace(self.number_mob[-1])
        fours_place = four_brace.get_text("Four's place")
        self.play(
            Transform(brace, four_brace),
            Transform(twos_place, fours_place),
        )
        self.play(Blink(randy))
        self.play(*map(FadeOut, [bubble, curr_content]))

        #Up to 1000
        for x in range(4):
            self.increment()
        brace.target = Brace(self.number_mob[-1])
        twos_place.target = brace.get_text("Eight's place")
        self.play(
            randy.change_mode, "happy",
            randy.look_at, self.number_mob,
            *map(MoveToTarget, [brace, twos_place])
        )
        for x in range(7):
            self.increment(total_run_time = 1)
        self.randy = randy

    def rhtyhm_of_counting(self):
        randy = self.randy
        # randy = Randolph()
        self.increment(total_run_time = 1, added_anims = [
            randy.change_mode, "wave_1"
        ])
        randy.target = randy.copy().change_mode("wave_2")
        arm_movement = MoveToTarget(randy, rate_func = there_and_back)
        self.play(arm_movement)

        for x in range(8):
            self.increment(total_run_time = 1, added_anims = [arm_movement])




























