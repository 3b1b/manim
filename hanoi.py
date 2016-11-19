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
        run_all_at_once = (total_run_time is not None)
        if run_all_at_once:
            num_rollovers = self.get_num_rollovers()
            run_time_per_anim = float(total_run_time)/(num_rollovers+1)
        moving_dot = Dot(
            self.counting_dot_starting_position,
            radius = self.count_dot_starting_radius,
            color = self.power_colors[0],
        )
        moving_dot.generate_target()
        moving_dot.set_fill(opacity = 0)

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
            if run_all_at_once:
                denom = float(num_rollovers+1)
                start_t = place/denom
                def get_modified_rate_func(anim):
                    return lambda t : anim.original_rate_func(
                        start_t + t/denom
                    )
                for anim in added_anims:
                    if not hasattr(anim, "original_rate_func"):
                        anim.original_rate_func = anim.rate_func
                    anim.rate_func = get_modified_rate_func(anim)
            self.play(
                MoveToTarget(moving_dot), 
                *added_anims, 
                run_time = run_time_per_anim
            )
            self.curr_configurations[place].add(moving_dot)
            if not run_all_at_once:
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
        "middle_peg_bottom" : 0.5*DOWN,
        "disk_height" : 0.4,
        "disk_min_width" : 1,
        "disk_max_width" : 3,
        "default_disk_run_time_off_peg" : 1,
        "default_disk_run_time_on_peg" : 2,
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
        peg.move_to(self.middle_peg_bottom, DOWN)
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

    def move_disks_to_peg(self, disk_indices, next_peg_index, run_time = None, stay_on_peg = True, added_anims = []):
        if run_time is None:
            if stay_on_peg is True:
                run_time = self.default_disk_run_time_on_peg
            else:
                run_time = self.default_disk_run_time_off_peg
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

def get_base_b_tex_mob(number, base, n_digits):
    assert(number < base**n_digits)
    curr_digit = n_digits - 1
    zero = TexMobject("0")
    zero_width = zero.get_width()
    zero_height = zero.get_height()
    result = VGroup()
    for place in range(n_digits):
        remainder = number%base
        digit_mob = TexMobject(str(remainder))
        digit_mob.scale_to_fit_height(zero_height)
        digit_mob.shift(place*(zero_width+SMALL_BUFF)*LEFT)
        result.add(digit_mob)
        number = (number - remainder)/base
    return result.center()


def get_binary_tex_mob(number, n_bits = 4):
    return get_base_b_tex_mob(number, 2, n_bits)

def get_ternary_tex_mob(number, n_trits = 4):
    return get_base_b_tex_mob(number, 3, n_trits)


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

        bubble = keith.get_bubble("speech", width = 7)
        bubble.write("01101011 $\\Rightarrow$ Towers of Hanoi")
        zero_width = bubble.content[0].get_width()
        one_width = bubble.content[1].get_width()        
        for mob in bubble.content[:8]:
            if abs(mob.get_width() - zero_width) < 0.01:
                mob.highlight(GREEN)
            else:
                mob.highlight(YELLOW)

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
        self.show_self_similarity()

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
        self.start_dot = self.curr_configurations[0][0]

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
        for x in range(8):
            self.increment(total_run_time = 1)
        self.dither()
        for x in range(8):
            self.increment(total_run_time = 1.5)

    def show_self_similarity(self):
        cover_rect = Rectangle()
        cover_rect.scale_to_fit_width(2*SPACE_WIDTH)
        cover_rect.scale_to_fit_height(2*SPACE_HEIGHT)
        cover_rect.set_stroke(width = 0)
        cover_rect.set_fill(BLACK, opacity = 0.85)
        big_dot = self.curr_configurations[-1][0].copy()
        self.play(
            FadeIn(cover_rect),
            Animation(big_dot)
        )
        self.play(
            big_dot.center,
            big_dot.scale_to_fit_height, 2*SPACE_HEIGHT-2,
            big_dot.to_edge, LEFT,
            run_time = 5
        )

class BinaryCountingAtEveryScale(Scene):
    CONFIG = {
        "num_bits" : 4,
        "show_title" : False,
    }
    def construct(self):
        title = TextMobject("Count to %d (which is %s in binary)"%(
            2**self.num_bits-1, bin(2**self.num_bits-1)[2:]
        ))
        title.to_edge(UP)
        if self.show_title:
            self.add(title)

        bit_mobs = [
            get_binary_tex_mob(n, self.num_bits)
            for n in range(2**self.num_bits)
        ]
        curr_bits = bit_mobs[0]

        lower_brace = Brace(VGroup(*curr_bits[1:]))
        do_a_thing = lower_brace.get_text("Do a thing")
        VGroup(lower_brace, do_a_thing).highlight(YELLOW)
        upper_brace = Brace(curr_bits, UP)
        roll_over = upper_brace.get_text("Roll over")
        VGroup(upper_brace, roll_over).highlight(MAROON_B)
        again = TextMobject("again")
        again.next_to(do_a_thing, RIGHT, 2*SMALL_BUFF)
        again.highlight(YELLOW)

        self.add(curr_bits, lower_brace, do_a_thing)

        def get_run_through(mobs):
            return Succession(*[
                Transform(
                    curr_bits, mob, 
                    rate_func = squish_rate_func(smooth, 0, 0.5)
                )
                for mob in mobs
            ], run_time = 1)

        for bit_mob in bit_mobs:
            curr_bits.align_data(bit_mob)
            bit_mob.highlight(YELLOW)
            bit_mob[0].highlight(MAROON_B)
        self.play(get_run_through(bit_mobs[1:2**(self.num_bits-1)]))
        self.play(*map(FadeIn, [upper_brace, roll_over]))
        self.play(Transform(
            VGroup(*reversed(list(curr_bits))),
            VGroup(*reversed(list(bit_mobs[2**(self.num_bits-1)]))),
            submobject_mode = "lagged_start",
            lag_factor = self.num_bits
        ))
        self.dither()
        self.play(
            get_run_through(bit_mobs[2**(self.num_bits-1)+1:]),
            Write(again)
        )
        self.dither()

class BinaryCountingAtSmallestScale(BinaryCountingAtEveryScale):
    CONFIG = {
        "num_bits" : 2,
        "show_title" : True,
    }

class BinaryCountingAtMediumScale(BinaryCountingAtEveryScale):
    CONFIG = {
        "num_bits" : 4,
        "show_title" : True,
    }

class BinaryCountingAtLargeScale(BinaryCountingAtEveryScale):
    CONFIG = {
        "num_bits" : 8,
        "show_title" : True,
    }

class IntroduceSolveByCounting(TowersOfHanoiScene):
    CONFIG = {
        "num_disks" : 4
    }
    def construct(self):
        self.initialize_bit_mobs()
        for disk in self.disks:
            disk.original_fill_color = disk.get_color()
        braces = [
            Brace(VGroup(*self.curr_bit_mob[-n:]))
            for n in range(1, self.num_disks + 1)
        ]
        word_list = [
            brace.get_text(text)
            for brace, text in zip(braces, [
                "Only flip last bit",
                "Roll over once",
                "Roll over twice",
                "Roll over three times",
            ])
        ]
        brace = braces[0].copy()
        words = word_list[0].copy()

        ##First increment
        self.play(self.get_increment_animation())
        self.play(
            GrowFromCenter(brace),
            Write(words, run_time = 1)
        )
        disk = self.disks[0]
        last_bit = self.curr_bit_mob[-1]
        last_bit.save_state()
        self.play(
            disk.set_fill, YELLOW,
            disk[1].set_fill, BLACK,
            last_bit.set_fill, YELLOW,
        )
        self.dither()
        self.move_disk(0, run_time = 2)
        self.play(
            last_bit.restore,
            disk.set_fill, disk.original_fill_color,
            self.disks[0][1].set_fill, BLACK
        )

        ##Second increment
        self.play(
            self.get_increment_animation(),
            Transform(words, word_list[1]),
            Transform(brace, braces[1]),
        )
        disk = self.disks[1]
        twos_bit = self.curr_bit_mob[-2]
        twos_bit.save_state()
        self.play(
            disk.set_fill, MAROON_B,
            disk[1].set_fill, BLACK,
            twos_bit.set_fill, MAROON_B,
        )
        self.move_disk(1, run_time = 2)
        self.dither()
        self.move_disk_to_peg(1, 1, stay_on_peg = False)
        cross = TexMobject("\\times")
        cross.replace(disk)
        cross.set_fill(RED, opacity = 0.5)
        self.play(FadeIn(cross))
        self.dither()
        self.move_disk_to_peg(
            1, 2, stay_on_peg = False, 
            added_anims = [FadeOut(cross)]
        )
        self.play(
            disk.set_fill, disk.original_fill_color,
            disk[1].set_fill, BLACK,
            twos_bit.restore,
            Transform(brace, braces[0]),
            Transform(words, word_list[0]),
        )
        self.move_disk(
            0, 
            added_anims = [self.get_increment_animation()],
            run_time = 2
        )
        self.dither()

        ##Fourth increment
        self.play(
            Transform(brace, braces[2]),
            Transform(words, word_list[2]),
        )
        self.play(self.get_increment_animation())
        disk = self.disks[2]
        fours_bit = self.curr_bit_mob[-3]
        fours_bit.save_state()
        self.play(
            disk.set_fill, RED,
            disk[1].set_fill, BLACK,
            fours_bit.set_fill, RED
        )
        self.move_disk(2, run_time = 2)
        self.play(
            disk.set_fill, disk.original_fill_color,
            disk[1].set_fill, BLACK,
            fours_bit.restore,
            FadeOut(brace),
            FadeOut(words)
        )
        self.dither()
        for disk_index in 0, 1, 0:
            self.move_disk(
                disk_index, 
                added_anims = [self.get_increment_animation()]
            )
        self.dither()

        ##Eighth incremement
        brace = braces[3]
        words = word_list[3]
        self.play(
            self.get_increment_animation(),
            GrowFromCenter(brace),
            Write(words, run_time = 1)
        )
        disk = self.disks[3]
        eights_bit = self.curr_bit_mob[0]
        eights_bit.save_state()
        self.play(
            disk.set_fill, GREEN,
            disk[1].set_fill, BLACK,
            eights_bit.set_fill, GREEN
        )
        self.move_disk(3, run_time = 2)
        self.play(
            disk.set_fill, disk.original_fill_color,
            disk[1].set_fill, BLACK,
            eights_bit.restore,
        )
        self.play(*map(FadeOut, [brace, words]))
        for disk_index in get_ruler_sequence(2):
            self.move_disk(
                disk_index,
                stay_on_peg = False,
                added_anims = [self.get_increment_animation()]
            )
        self.dither()

    def initialize_bit_mobs(self):
        bit_mobs = VGroup(*[
            get_binary_tex_mob(n, self.num_disks)
            for n in range(2**(self.num_disks))
        ])
        bit_mobs.scale(2)
        for bit_mob in bit_mobs:
            for bit, disk in zip(bit_mob, reversed(list(self.disks))):
                bit.highlight(disk.get_color())
        bit_mobs.next_to(self.peg_labels, DOWN)
        self.bit_mobs_iter = it.cycle(bit_mobs)
        self.curr_bit_mob = self.bit_mobs_iter.next()

        self.add(self.curr_bit_mob)

    def get_increment_animation(self):
        return Succession(
            Transform(self.curr_bit_mob, self.bit_mobs_iter.next()),
            Animation(self.curr_bit_mob)
        )

class SolveSixDisksByCounting(IntroduceSolveByCounting):
    CONFIG = {
        "num_disks" : 6,
        "stay_on_peg" : False,
        "run_time_per_move" : 1,
    }
    def construct(self):
        self.initialize_bit_mobs()
        for disk_index in get_ruler_sequence(self.num_disks-1):
            self.move_disk(
                disk_index,
                stay_on_peg = self.stay_on_peg,
                run_time = self.run_time_per_move,
                added_anims = [self.get_increment_animation()],
            )
        self.dither()

class RecursionTime(Scene):
    def construct(self):
        keith = Keith().shift(2*DOWN+3*LEFT)
        morty = Mortimer().shift(2*DOWN+3*RIGHT)
        keith.make_eye_contact(morty)

        keith_kick = keith.copy().change_mode("dance_kick")
        keith_kick.scale_in_place(1.3)
        keith_kick.shift(0.5*LEFT)
        keith_kick.look_at(morty.eyes)
        keith_hooray = keith.copy().change_mode("hooray")

        self.add(keith, morty)

        bubble = keith.get_bubble("speech", height = 2)
        bubble.write("Recursion time!!!")
        VGroup(bubble, bubble.content).shift(UP)

        self.play(
            Transform(keith, keith_kick),
            morty.change_mode, "happy",
            ShowCreation(bubble),
            Write(bubble.content, run_time = 1)
        )
        self.play(
            morty.change_mode, "hooray",
            Transform(keith, keith_hooray),
            bubble.content.gradient_highlight, BLUE_A, BLUE_E
        )
        self.play(Blink(morty))
        self.dither()

class Eyes(VMobject):
    CONFIG = {
        "height" : 0.3,
        "thing_looked_at" : None,
        "mode" : "plain",
    }
    def __init__(self, mobject, **kwargs):
        VMobject.__init__(self, **kwargs)
        self.mobject = mobject
        self.submobjects = self.get_eyes().submobjects

    def get_eyes(self, mode = None, thing_to_look_at = None):
        mode = mode or self.mode
        if thing_to_look_at is None:
            thing_to_look_at = self.thing_looked_at

        pi = Randolph(mode = mode)
        eyes = VGroup(pi.eyes, pi.pupils)
        eyes.scale_to_fit_height(self.height)
        if self.submobjects:
            eyes.move_to(self, DOWN)
        else:
            eyes.move_to(self.mobject.get_top(), DOWN)
        if thing_to_look_at is not None:
            pi.look_at(thing_to_look_at)
        return eyes

    def change_mode_anim(self, mode, **kwargs):
        self.mode = mode
        return Transform(self, self.get_eyes(mode = mode), **kwargs)

    def look_at_anim(self, point_or_mobject, **kwargs):
        self.thing_looked_at = point_or_mobject
        return Transform(
            self, self.get_eyes(thing_to_look_at = point_or_mobject), 
            **kwargs
        )

    def blink_anim(self):
        target = self.copy()
        bottom_y = self.get_bottom()[1]
        for submob in target:
            submob.apply_function(
                lambda p : [p[0], bottom_y, p[2]]
            )
        return Transform(
            self, target, 
            rate_func = squish_rate_func(there_and_back)
        )

class RecursiveSolution(TowersOfHanoiScene):
    CONFIG = {
        "num_disks" : 4,
        "middle_peg_bottom" : 2*DOWN,
    }
    def construct(self):
        # VGroup(*self.get_mobjects()).shift(1.5*DOWN)
        big_disk = self.disks[-1]
        self.eyes = Eyes(big_disk)
        title = TextMobject("Move 4-tower")
        sub_steps = TextMobject(
            "Move 3-tower,",
            "Move disk 3,",
            "Move 3-tower",
        )
        sub_steps[1].highlight(GREEN)
        sub_step_brace = Brace(sub_steps, UP)
        sub_sub_steps = TextMobject(
            "Move 2-tower,",
            "Move disk 2,",
            "Move 2-tower",
        )
        sub_sub_steps[1].highlight(RED)
        sub_sub_steps_brace = Brace(sub_sub_steps, UP)
        steps = VGroup(
            title, sub_step_brace, sub_steps, 
            sub_sub_steps_brace, sub_sub_steps
        )
        steps.arrange_submobjects(DOWN)
        steps.scale(0.7)
        steps.to_edge(UP)
        VGroup(sub_sub_steps_brace, sub_sub_steps).next_to(sub_steps[-1], DOWN)

        self.add(title)

        ##Big disk is frustrated
        self.play(
            FadeIn(self.eyes),
            big_disk.set_fill, GREEN,
            big_disk.label.set_fill, BLACK,
        )
        big_disk.add(self.eyes)        
        self.blink()
        self.dither()
        self.change_mode("angry")
        for x in range(2):
            self.dither()
            self.shake(big_disk)
            self.blink()
            self.dither()
        self.change_mode("plain")
        self.look_at(self.peg_labels[2])
        self.look_at(self.disks[0])
        self.blink()

        #Subtower move
        self.move_subtower_to_peg(3, 1, run_time = 2, added_anims = [
            self.eyes.look_at_anim(self.pegs[1]),
            FadeIn(sub_step_brace),
            Write(sub_steps[0], run_time = 1)
        ])
        self.dither()
        self.move_disk_to_peg(0, 0, run_time = 2, added_anims = [
            self.eyes.look_at_anim(self.pegs[0].get_top())
        ])
        self.shake(big_disk)
        self.move_disk_to_peg(0, 2, run_time = 2, added_anims = [
            self.eyes.look_at_anim(self.pegs[2].get_bottom())
        ])
        self.change_mode("angry")
        self.move_disk_to_peg(0, 1, run_time = 2, added_anims = [
            self.eyes.look_at_anim(self.disks[1].get_top())
        ])
        self.blink()

        #Final moves for big case
        self.move_disk(3, run_time = 2, added_anims = [
            Write(sub_steps[1])
        ])
        self.look_at(self.disks[1])
        self.blink()
        bubble = SpeechBubble()
        bubble.write("I'm set!")
        bubble.resize_to_content()
        bubble.pin_to(big_disk)
        bubble.add_content(bubble.content)
        bubble.set_fill(BLACK, opacity = 0.7)
        self.play(
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.dither()
        self.blink()
        self.play(*map(FadeOut, [bubble, bubble.content]))
        big_disk.remove(self.eyes)
        self.move_subtower_to_peg(3, 2, run_time = 2, added_anims = [
            self.eyes.look_at_anim(self.pegs[2].get_top()),
            Write(sub_steps[2])
        ])
        self.play(FadeOut(self.eyes))
        self.dither()

        #Highlight subproblem
        self.play(
            VGroup(*self.disks[:3]).move_to, self.pegs[1], DOWN
        )
        self.disk_tracker = [set([]), set([0, 1, 2]), set([3])]
        arc = Arc(-5*np.pi/6, start_angle = 5*np.pi/6)
        arc.add_tip()
        arc.highlight(YELLOW)
        arc.scale_to_fit_width(
            VGroup(*self.pegs[1:]).get_width()*0.8
        )
        arc.next_to(self.disks[0], UP+RIGHT, buff = SMALL_BUFF)
        q_mark = TextMobject("?")
        q_mark.next_to(arc, UP)
        self.play(
            ShowCreation(arc),
            Write(q_mark),
            sub_steps[-1].highlight, YELLOW
        )
        self.dither()
        self.play(
            GrowFromCenter(sub_sub_steps_brace),
            *map(FadeOut, [arc, q_mark])
        )

        #Disk 2 frustration
        big_disk = self.disks[2]
        self.eyes.move_to(big_disk.get_top(), DOWN)
        self.play(
            FadeIn(self.eyes),
            big_disk.set_fill, RED,
            big_disk.label.set_fill, BLACK
        )
        big_disk.add(self.eyes)
        self.change_mode("sad")
        self.look_at(self.pegs[1].get_top())
        self.shake(big_disk)
        self.blink()

        #Move sub-sub-tower
        self.move_subtower_to_peg(2, 0, run_time = 2, added_anims = [
            self.eyes.look_at_anim(self.pegs[0].get_bottom()),
            Write(sub_sub_steps[0])
        ])
        self.blink()
        self.move_disk_to_peg(2, 2, run_time = 2, added_anims = [
            Write(sub_sub_steps[1])
        ])
        self.look_at(self.disks[0])
        big_disk.remove(self.eyes)
        self.move_subtower_to_peg(2, 2, run_time = 2, added_anims = [
            self.eyes.look_at_anim(self.pegs[2].get_top()),
            Write(sub_sub_steps[2])
        ])
        self.blink()
        self.look_at(self.disks[-1])

        #Move eyes
        self.play(FadeOut(self.eyes))
        self.eyes.move_to(self.disks[1].get_top(), DOWN)
        self.play(FadeIn(self.eyes))
        self.blink()
        self.play(FadeOut(self.eyes))
        self.eyes.move_to(self.disks[3].get_top(), DOWN)
        self.play(FadeIn(self.eyes))

        #Show process one last time
        big_disk = self.disks[3]
        big_disk.add(self.eyes)
        self.move_subtower_to_peg(3, 1, run_time = 2, added_anims = [
            self.eyes.look_at_anim(self.pegs[0])
        ])
        self.move_disk_to_peg(3, 0, run_time = 2)
        big_disk.remove(self.eyes)
        self.move_subtower_to_peg(3, 0, run_time = 2, added_anims = [
            self.eyes.look_at_anim(self.pegs[0].get_top())
        ])
        self.blink()

    def shake(self, mobject, direction = UP, added_anims = []):
        self.play(
            mobject.shift, 0.2*direction, rate_func = wiggle,
            *added_anims
        )

    def blink(self):
        self.play(self.eyes.blink_anim())

    def look_at(self, point_or_mobject):
        self.play(self.eyes.look_at_anim(point_or_mobject))

    def change_mode(self, mode):
        self.play(self.eyes.change_mode_anim(mode))

class CodeThisUp(Scene):
    def construct(self):
        keith = Keith()
        keith.shift(2*DOWN+3*LEFT)
        morty = Mortimer()
        morty.shift(2*DOWN+3*RIGHT)
        keith.make_eye_contact(morty)
        point = 2*UP+3*RIGHT
        bubble = keith.get_bubble("speech", width = 4.5, height = 3)
        bubble.write("This is the \\\\ most efficient")
        self.add(morty, keith)

        self.play(
            keith.change_mode, "speaking",
            keith.look_at, point
        )
        self.play(
            morty.change_mode, "pondering",
            morty.look_at, point
        )
        self.play(Blink(keith))
        self.dither(2)
        self.play(Blink(morty))
        self.dither()
        self.play(
            keith.change_mode, "hooray",
            keith.look_at, morty.eyes
        )
        self.play(Blink(keith))
        self.dither()
        self.play(
            keith.change_mode, "speaking",
            keith.look_at, morty.eyes,
            ShowCreation(bubble),
            Write(bubble.content),
            morty.change_mode, "happy",
            morty.look_at, keith.eyes,
        )
        self.dither()
        self.play(Blink(morty))
        self.dither()

class HanoiSolutionCode(Scene):
    def construct(self):
        pass

class WhyDoesBinaryAchieveThis(Scene):
    def construct(self):
        keith = Keith()
        keith.shift(2*DOWN+3*LEFT)
        morty = Mortimer()
        morty.shift(2*DOWN+3*RIGHT)
        keith.make_eye_contact(morty)
        bubble = morty.get_bubble("speech", width = 5, height = 3)
        bubble.write("""
            Why does counting
            in binary work?
        """)
        self.add(morty, keith)

        self.play(
            morty.change_mode, "confused",
            morty.look_at, keith.eyes,
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.play(keith.change_mode, "happy")
        self.dither()
        self.play(Blink(morty))
        self.dither()

class LargeScaleHanoiDecomposition(TowersOfHanoiScene):
    CONFIG = {
        "num_disks" : 8,
        "peg_height" : 3.5,
        "middle_peg_bottom" : 2*DOWN,
        "disk_max_width" : 4,
    }
    def construct(self):
        self.move_subtower_to_peg(7, 1, stay_on_peg = False)
        self.dither()
        self.move_disk(7, stay_on_peg = False)
        self.dither()
        self.move_subtower_to_peg(7, 2, stay_on_peg = False)
        self.dither()

class SolveTwoDisksByCounting(SolveSixDisksByCounting):
    CONFIG = {
        "num_disks" : 2,
        "stay_on_peg" : False,
        "run_time_per_move" : 1,
        "disk_max_width" : 1.5,
    }
    def construct(self):
        self.initialize_bit_mobs()
        for disk_index in 0, 1, 0:
            self.move_disk(
                disk_index, 
                stay_on_peg = False,
                added_anims = [self.get_increment_animation()]
            )
            self.dither()

class ShowFourDiskFourBitsParallel(IntroduceSolveByCounting):
    CONFIG = {
        "num_disks" : 4,
        "small_run_time" : 0.2,
    }
    def construct(self):
        self.initialize_bit_mobs()
        self.subtask()
        self.dither()
        self.move_disk(
            self.num_disks-1, 
            stay_on_peg = False,
            added_anims = [
                self.get_increment_animation()
            ]
        )
        self.dither()
        self.subtask()
        self.dither()

    def subtask(self):
        for disk_index in get_ruler_sequence(self.num_disks-2):
            self.move_disk(
                disk_index, 
                run_time = self.small_run_time, 
                stay_on_peg = False,
                added_anims = [
                    self.get_increment_animation()
                ]
            )

class ShowSixDiskSixBitsParallel(ShowFourDiskFourBitsParallel):
    CONFIG = {
        "num_disks" : 6,
        "small_run_time" : 0.05
    }

class CoolRight(Scene):
    def construct(self):
        morty = Mortimer()
        morty.shift(2*DOWN)
        bubble = SpeechBubble()
        bubble.write("Cool! right?")
        bubble.resize_to_content()
        bubble.pin_to(morty)

        self.play(
            morty.change_mode, "surprised",
            morty.look, OUT,
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.play(Blink(morty))
        self.dither()
        curr_content = bubble.content
        bubble.write("It gets \\\\ better...")
        self.play(
            Transform(curr_content, bubble.content),
            morty.change_mode, "hooray",
            morty.look, OUT
        )
        self.dither()
        self.play(Blink(morty))
        self.dither()

############ Part 2 ############

class MentionLastVideo(Scene):
    def construct(self):
        keith = Keith()
        keith.shift(2*DOWN+3*LEFT)
        morty = Mortimer()
        morty.shift(2*DOWN+3*RIGHT)
        keith.make_eye_contact(morty)
        point = 2*UP

        name = TextMobject("""
            Keith Schwarz
            (Computer Scientist)
        """)
        name.to_corner(UP+LEFT)
        arrow = Arrow(name.get_bottom(), keith.get_top())

        self.add(morty, keith)
        self.play(
            keith.change_mode, "raise_right_hand",
            keith.look_at, point,
            morty.change_mode, "pondering",
            morty.look_at, point
        )
        self.play(Blink(keith))
        self.play(Write(name))
        self.play(ShowCreation(arrow))
        self.play(Blink(morty))
        self.dither(2)
        self.play(
            morty.change_mode, "confused",
            morty.look_at, point
        )
        self.play(Blink(keith))
        self.dither(2)
        self.play(
            morty.change_mode, "surprised"
        )
        self.dither()

class IntroduceConstrainedTowersOfHanoi(ConstrainedTowersOfHanoiScene):
    CONFIG = {
        "middle_peg_bottom" : 2*DOWN,
    }
    def construct(self):
        title = TextMobject("Constrained", "Towers of Hanoi")
        title.highlight_by_tex("Constrained", YELLOW)
        title.to_edge(UP)

        self.play(Write(title))
        self.add_arcs()
        self.disks.save_state()
        for index in 0, 0, 1, 0:
            self.move_disk(index)
            self.dither()
        self.dither()

        self.play(self.disks.restore)
        self.disk_tracker = [set(range(self.num_disks)), set([]), set([])]
        self.dither()
        self.move_disk_to_peg(0, 1)
        self.move_disk_to_peg(1, 2)
        self.play(ShowCreation(self.big_curved_arrow))
        cross = TexMobject("\\times")
        cross.scale(2)
        cross.set_fill(RED)
        cross.move_to(self.big_curved_arrow.get_top())
        big_cross = cross.copy()
        big_cross.replace(self.disks[1])
        big_cross.set_fill(opacity = 0.5)
        self.play(FadeIn(cross))
        self.play(FadeIn(big_cross))
        self.dither()


    def add_arcs(self):
        arc = Arc(start_angle = np.pi/6, angle = 2*np.pi/3)
        curved_arrow1 = VGroup(arc, arc.copy().flip())
        curved_arrow2 = curved_arrow1.copy()
        curved_arrows = [curved_arrow1, curved_arrow2]
        for curved_arrow in curved_arrows:
            for arc in curved_arrow:
                arc.add_tip(tip_length = 0.15)
                arc.highlight(YELLOW)
        peg_sets = (self.pegs[:2], self.pegs[1:])
        for curved_arrow, pegs in zip(curved_arrows, peg_sets):
            peg_group = VGroup(*pegs)
            curved_arrow.scale_to_fit_width(0.7*peg_group.get_width())
            curved_arrow.next_to(peg_group, UP)

        self.play(ShowCreation(curved_arrow1))
        self.play(ShowCreation(curved_arrow2))
        self.dither()

        big_curved_arrow = Arc(start_angle = 5*np.pi/6, angle = -2*np.pi/3)
        big_curved_arrow.scale_to_fit_width(0.9*self.pegs.get_width())
        big_curved_arrow.next_to(self.pegs, UP)
        big_curved_arrow.add_tip(tip_length = 0.4)
        big_curved_arrow.highlight(WHITE)
        self.big_curved_arrow = big_curved_arrow

class StillRecruse(Scene):
    def construct(self):
        keith = Keith()
        keith.shift(2*DOWN+3*LEFT)
        morty = Mortimer()
        morty.shift(2*DOWN+3*RIGHT)
        keith.make_eye_contact(morty)
        point = 2*UP+3*RIGHT
        bubble = keith.get_bubble("speech", width = 4.5, height = 3)
        bubble.write("You can still\\\\ use recursion")
        self.add(morty, keith)

        self.play(
            keith.change_mode, "speaking",
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.play(morty.change_mode, "hooray")
        self.play(Blink(keith))
        self.dither()
        self.play(Blink(morty))
        self.dither()

class RecursiveSolutionToConstrained(RecursiveSolution):
    CONFIG = {
        "middle_peg_bottom" : 2*DOWN,
        "num_disks" : 4,
    }
    def construct(self):
        big_disk = self.disks[-1]
        self.eyes = Eyes(big_disk)

        #Define steps breakdown text
        title = TextMobject("Move 4-tower")
        subdivisions = [
            TextMobject(
                "\\tiny Move %d-tower,"%d,
                "Move disk %d,"%d,
                "\\, Move %d-tower, \\,"%d,
                "Move disk %d,"%d,
                "Move %d-tower"%d,
            ).highlight_by_tex("Move disk %d,"%d, color)
            for d, color in (3, GREEN), (2, RED), (1, BLUE_C)
        ]
        sub_steps, sub_sub_steps = subdivisions[:2]
        for steps in subdivisions:
            steps.scale_to_fit_width(2*SPACE_WIDTH-1)
        subdivisions.append(
            TextMobject("\\tiny Move disk 0, Move disk 0").highlight(BLUE)
        )
        braces = [
            Brace(steps, UP)
            for steps in subdivisions
        ]
        sub_steps_brace, sub_sub_steps_brace = braces[:2]
        steps = VGroup(title, *it.chain(*zip(
            braces, subdivisions
        )))
        steps.arrange_submobjects(DOWN)
        steps.to_edge(UP)

        steps_to_fade = VGroup(
            title, sub_steps_brace,
            *list(sub_steps[:2]) + list(sub_steps[3:])
        )
        self.add(title)

        #Initially move big disk
        self.play(
            FadeIn(self.eyes),
            big_disk.set_fill, GREEN,
            big_disk.label.set_fill, BLACK
        )
        big_disk.add(self.eyes)
        big_disk.save_state()
        self.blink()
        self.look_at(self.pegs[2])
        self.move_disk_to_peg(self.num_disks-1, 2, stay_on_peg = False)
        self.look_at(self.pegs[0])
        self.blink()
        self.play(big_disk.restore, path_arc = np.pi/3)
        self.disk_tracker = [set(range(self.num_disks)), set([]), set([])]
        self.look_at(self.pegs[0].get_top())
        self.change_mode("angry")
        self.shake(big_disk)
        self.dither()

        #Talk about tower blocking
        tower = VGroup(*self.disks[:self.num_disks-1])
        blocking = TextMobject("Still\\\\", "Blocking")
        blocking.highlight(RED)
        blocking.to_edge(LEFT)
        blocking.shift(2*UP)
        arrow = Arrow(blocking.get_bottom(), tower.get_top(), buff = SMALL_BUFF)
        new_arrow = Arrow(blocking.get_bottom(), self.pegs[1], buff = SMALL_BUFF)
        VGroup(arrow, new_arrow).highlight(RED)

        self.play(
            Write(blocking[1]),
            ShowCreation(arrow)
        )
        self.shake(tower, RIGHT, added_anims = [Animation(big_disk)])
        self.blink()
        self.shake(big_disk)
        self.dither()
        self.move_subtower_to_peg(self.num_disks-1, 1, added_anims = [
            Transform(arrow, new_arrow),
            self.eyes.look_at_anim(self.pegs[1])
        ])
        self.play(Write(blocking[0]))
        self.shake(big_disk, RIGHT)
        self.dither()
        self.blink()
        self.dither()
        self.play(FadeIn(sub_steps_brace))
        self.move_subtower_to_peg(self.num_disks-1, 2, added_anims = [
            FadeOut(blocking),
            FadeOut(arrow),
            self.eyes.change_mode_anim("plain", thing_to_look_at = self.pegs[2]),
            Write(sub_steps[0], run_time = 1),
        ])
        self.blink()

        #Proceed through actual process
        self.move_disk_to_peg(self.num_disks-1, 1, added_anims = [
            Write(sub_steps[1], run_time = 1),
        ])
        self.dither()
        self.move_subtower_to_peg(self.num_disks-1, 0, added_anims = [
            self.eyes.look_at_anim(self.pegs[0]),
            Write(sub_steps[2], run_time = 1),
        ])
        self.blink()
        self.move_disk_to_peg(self.num_disks-1, 2, added_anims = [
            Write(sub_steps[3], run_time = 1),
        ])
        self.dither()
        big_disk.remove(self.eyes)
        self.move_subtower_to_peg(self.num_disks-1, 2, added_anims = [
            self.eyes.look_at_anim(self.pegs[2].get_top()),
            Write(sub_steps[4], run_time = 1),
        ])
        self.blink()
        self.play(FadeOut(self.eyes))

        #Ask about subproblem
        sub_sub_steps_brace.highlight(WHITE)
        self.move_subtower_to_peg(self.num_disks-1, 0, added_anims = [
            steps_to_fade.fade, 0.7,
            sub_steps[2].highlight, WHITE,
            sub_steps[2].scale_in_place, 1.2,
            FadeIn(sub_sub_steps_brace)
        ])
        num_disks = self.num_disks-1
        big_disk = self.disks[num_disks-1]
        self.eyes.move_to(big_disk.get_top(), DOWN)
        self.play(
            FadeIn(self.eyes),
            big_disk.set_fill, RED,
            big_disk.label.set_fill, BLACK,
        )
        big_disk.add(self.eyes)        
        self.blink()

        #Solve subproblem
        self.move_subtower_to_peg(num_disks-1, 2, added_anims = [
            self.eyes.look_at_anim(self.pegs[2]),
            Write(sub_sub_steps[0], run_time = 1)
        ])
        self.blink()
        self.move_disk_to_peg(num_disks-1, 1, added_anims = [
            Write(sub_sub_steps[1], run_time = 1)
        ])
        self.dither()
        self.move_subtower_to_peg(num_disks-1, 0, added_anims = [
            self.eyes.look_at_anim(self.pegs[0]),
            Write(sub_sub_steps[2], run_time = 1)
        ])
        self.blink()
        self.move_disk_to_peg(num_disks-1, 2, added_anims = [
            Write(sub_sub_steps[3], run_time = 1)
        ])
        self.dither()
        big_disk.remove(self.eyes)
        self.move_subtower_to_peg(num_disks-1, 2, added_anims = [
            self.eyes.look_at_anim(self.pegs[2].get_top()),
            Write(sub_sub_steps[4], run_time = 1)
        ])
        self.dither()

        #Show smallest subdivisions
        smaller_subdivision = VGroup(
            *list(subdivisions[2:]) + \
            list(braces[2:])
        )
        last_subdivisions = [VGroup(braces[-1], subdivisions[-1])]
        for vect in LEFT, RIGHT:
            group = last_subdivisions[0].copy()
            group.to_edge(vect)
            steps.add(group)
            smaller_subdivision.add(group)
            last_subdivisions.append(group)
        smaller_subdivision.set_fill(opacity = 0)
        self.play(
            steps.shift, 
            (SPACE_HEIGHT-sub_sub_steps.get_top()[1]-MED_BUFF)*UP,
            self.eyes.look_at_anim(steps)
        )
        self.play(ApplyMethod(
            VGroup(VGroup(braces[-2], subdivisions[-2])).set_fill, None, 1,
            run_time = 3,
            submobject_mode = "lagged_start",
        ))
        self.blink()
        for mob in last_subdivisions:
            self.play(
                ApplyMethod(mob.set_fill, None, 1),
                self.eyes.look_at_anim(mob)
            )
        self.blink()
        self.play(FadeOut(self.eyes))
        self.dither()

        #final movements
        movements = [
            (0, 1),
            (0, 0),
            (1, 1),
            (0, 1),
            (0, 2),
            (1, 0),
            (0, 1),
            (0, 0),
        ]
        for disk_index, peg_index in movements:
            self.move_disk_to_peg(
                disk_index, peg_index, 
                stay_on_peg = False
            )
        self.dither()

class SimpleConstrainedBreakdown(TowersOfHanoiScene):
    CONFIG = {
        "num_disks" : 4
    }
    def construct(self):
        self.move_subtower_to_peg(self.num_disks-1, 2)
        self.dither()
        self.move_disk(self.num_disks-1)
        self.dither()
        self.move_subtower_to_peg(self.num_disks-1, 0)
        self.dither()
        self.move_disk(self.num_disks-1)
        self.dither()
        self.move_subtower_to_peg(self.num_disks-1, 2)
        self.dither()

class SolveConstrainedByCounting(ConstrainedTowersOfHanoiScene):
    CONFIG = {
        "num_disks" : 5,
        "ternary_mob_scale_factor" : 2,
    }
    def construct(self):
        ternary_mobs = VGroup()
        for num in range(3**self.num_disks):
            ternary_mob = get_ternary_tex_mob(num, self.num_disks)
            ternary_mob.scale(self.ternary_mob_scale_factor)
            ternary_mob.gradient_highlight(*self.disk_start_and_end_colors)
            ternary_mobs.add(ternary_mob)
        ternary_mobs.next_to(self.peg_labels, DOWN)
        self.ternary_mob_iter = it.cycle(ternary_mobs)
        self.curr_ternary_mob = self.ternary_mob_iter.next()
        self.add(self.curr_ternary_mob)

        for index in get_ternary_ruler_sequence(self.num_disks-1):
            self.move_disk(index, stay_on_peg = False, added_anims = [
                self.increment_animation()
            ])

    def increment_animation(self):
        return Succession(
            Transform(
                self.curr_ternary_mob, self.ternary_mob_iter.next(),
                submobject_mode = "lagged_start",
                path_arc = np.pi/6,
            ),
            Animation(self.curr_ternary_mob),
        )

class CompareNumberSystems(Scene):
    def construct(self):
        base_ten = TextMobject("Base ten")
        base_ten.to_corner(UP+LEFT).shift(RIGHT)
        binary = TextMobject("Binary")
        binary.to_corner(UP+RIGHT).shift(LEFT)
        ternary = TextMobject("Ternary")
        ternary.to_edge(UP)
        ternary.highlight(YELLOW)
        titles = [base_ten, binary, ternary]

        zero_to_nine = TextMobject("""
            0, 1, 2, 3, 4,
            5, 6, 7, 8, 9
        """)
        zero_to_nine.next_to(base_ten, DOWN, buff = LARGE_BUFF)
        zero_one = TextMobject("0, 1")
        zero_one.next_to(binary, DOWN, buff = LARGE_BUFF)
        zero_one_two = TextMobject("0, 1, 2")
        zero_one_two.next_to(ternary, DOWN, buff = LARGE_BUFF)
        zero_one_two.gradient_highlight(BLUE, GREEN)

        symbols = [zero_to_nine, zero_one, zero_one_two]
        names = ["Digits", "Bits", "Trits?"]
        for mob, text in zip(symbols, names):
            mob.brace = Brace(mob)
            mob.name = mob.brace.get_text(text)
        zero_one_two.name.gradient_highlight(BLUE, GREEN)

        keith = Keith()
        keith.shift(2*DOWN+3*LEFT)
        keith.look_at(zero_one_two)

        for title, symbol in zip(titles, symbols):
            self.play(FadeIn(title))
            added_anims = []
            if title is not ternary:
                added_anims += [
                    FadeIn(symbol.brace),
                    FadeIn(symbol.name)
                ]
            self.play(Write(symbol, run_time = 2), *added_anims)
            self.dither()
        self.play(FadeIn(keith))
        self.play(keith.change_mode, "confused")
        self.play(keith.look_at, zero_to_nine)
        self.play(keith.look_at, zero_one)
        self.play(
            GrowFromCenter(zero_one_two.brace),
            Write(zero_one_two.name),
            keith.look_at, zero_one_two,
        )
        self.play(keith.change_mode, "sassy")
        self.play(Blink(keith))
        self.dither()


class CountInTernary(CountingScene):
    CONFIG = {
        "base" : 3,
        "counting_dot_starting_position" : (SPACE_WIDTH-1)*RIGHT + (SPACE_HEIGHT-1)*UP,
        "count_dot_starting_radius" : 0.5,
        "dot_configuration_height" : 1,
        "ones_configuration_location" : UP+2*RIGHT,
        "num_scale_factor" : 2,
        "num_start_location" : DOWN+RIGHT,
    }
    def construct(self):
        for x in range(27):
            self.increment()
        self.dither()























