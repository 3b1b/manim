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
        "digit_place_colors" : [YELLOW, MAROON_B, RED, GREEN, BLUE, PURPLE_D],
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
        self.max_place = 0
        self.number_mob = VGroup(TexMobject(str(self.number)))
        self.number_mob.scale(self.num_scale_factor)
        self.number_mob.shift(self.num_start_location)

        self.dot_templates = []
        self.dot_template_iterators = []
        self.curr_configurations = []

        self.arrows = VGroup()

        self.add(self.number_mob)

    def get_template_configuration(self, place):
        #This should probably be replaced for non-base-10 counting scenes
        down_right = (0.5)*RIGHT + (np.sqrt(3)/2)*DOWN
        result = []
        for down_right_steps in range(5):
            for left_steps in range(down_right_steps):
                result.append(
                    down_right_steps*down_right + left_steps*LEFT
                )
        return reversed(result[:self.get_place_max(place)])

    def get_dot_template(self, place):
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
            for point in self.get_template_configuration(place)
        ])
        dots.scale_to_fit_height(self.dot_configuration_height)
        return dots

    def add_configuration(self):
        new_template = self.get_dot_template(len(self.dot_templates))
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

    def increment(self, run_time_per_anim = 1):
        moving_dot = Dot(
            self.counting_dot_starting_position,
            radius = self.count_dot_starting_radius,
            color = self.digit_place_colors[0],
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
            added_anims = []                
            if first_move:
                added_anims += self.get_digit_increment_animations()
                first_move = False
            moving_dot.target.replace(
                self.dot_template_iterators[place].next()
            )
            self.play(MoveToTarget(moving_dot), *added_anims, **kwargs)
            self.curr_configurations[place].add(moving_dot)


            if len(self.curr_configurations[place].split()) == self.get_place_max(place):
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
                    fill_color = self.digit_place_colors[place],
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
        is_next_digit = self.is_next_digit()
        if is_next_digit: self.max_place += 1
        new_number_mob = self.get_number_mob(self.number)
        new_number_mob.move_to(self.number_mob, RIGHT)
        if is_next_digit:
            self.add_configuration()
            place = len(new_number_mob.split())-1
            result.append(FadeIn(self.dot_templates[place]))
            arrow = Arrow(
                new_number_mob[place].get_top(),
                self.dot_templates[place].get_bottom(),
                color = self.digit_place_colors[place]
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
        max_place = self.max_place
        while place < max_place:
            digit = TexMobject(str(self.get_place_num(num, place)))
            if place >= len(self.digit_place_colors):
                self.digit_place_colors += self.digit_place_colors
            digit.highlight(self.digit_place_colors[place])
            digit.scale(self.num_scale_factor)
            digit.next_to(result, LEFT, buff = SMALL_BUFF, aligned_edge = DOWN)
            result.add(digit)
            place += 1
        return result

    def is_next_digit(self):
        return False
    def get_place_num(self, num, place):
        return 0
    def get_place_max(self, place):
        return 0

class PowerCounter(CountingScene):
    def is_next_digit(self):
        number = self.number
        while number > 1:
            if number%self.base != 0:
                return False
            number /= self.base
        return True
    def get_place_max(self, place):
        return self.base
    def get_place_num(self, num, place):
        return (num / (self.base ** place)) % self.base

class CountInDecimal(PowerCounter):
    CONFIG = {
        "base" : 10,
    }
    def construct(self):
        for x in range(11):
            self.increment()
        for x in range(85):
            self.increment(0.25)
        for x in range(20):
            self.increment()

class CountInTernary(PowerCounter):
    CONFIG = {
        "base" : 3,
        "dot_configuration_height" : 1,
        "ones_configuration_location" : UP+4*RIGHT
    }
    def construct(self):
        self.count(27)

    # def get_template_configuration(self):
    #     return [ORIGIN, UP]

class CountInBinaryTo256(PowerCounter):
    CONFIG = {
        "base" : 2,
        "dot_configuration_height" : 1,
        "ones_configuration_location" : UP+5*RIGHT
    }
    def construct(self):
        self.count(128, 0.3)

    def get_template_configuration(self):
        return [ORIGIN, UP]

class FactorialBase(CountingScene):
    CONFIG = {
        "dot_configuration_height" : 1,
        "ones_configuration_location" : UP+4*RIGHT
    }
    def construct(self):
        self.count(30, 0.4)
    def is_next_digit(self):
        return self.number == self.factorial(self.max_place + 1)
    def get_place_max(self, place):
        return place + 2
    def get_place_num(self, num, place):
        return (num / self.factorial(place + 1)) % self.get_place_max(place)
    def factorial(self, n):
        if (n == 1): return 1
        else: return n * self.factorial(n - 1)

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
                fill_opacity = 1,
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
        self.move_disks_to_peg([disk_index], next_peg_index, **kwargs)

    def move_subtower_to_peg(self, num_disks, next_peg_index, **kwargs):
        disk_indices = range(num_disks)
        peg_indices = map(self.disk_index_to_peg_index, disk_indices)
        if len(set(peg_indices)) != 1:
            warnings.warn("These disks don't make up a tower right now")
        self.move_disks_to_peg(disk_indices, next_peg_index, **kwargs)

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

        bubble = keith.get_bubble("speech")
        bubble.write("Check this out...")
        bubble.resize_to_content()
        bubble.pin_to(keith)
        VGroup(bubble, bubble.content).shift(DOWN)

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

class IntroduceTowersOfHanoi(TowersOfHanoiScene):
    def construct(self):
        self.clear()
        self.add_title()
        self.show_setup()
        self.note_disk_labels()
        self.show_more_disk_possibility()
        self.move_full_tower()
        self.move_single_disk()
        self.cannot_move_disk_with_crap_on_top()
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
        )
        self.play(Write(self.peg_labels))
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
            group = VGroup(disk, top)
            group.original_location = group.get_center()
            group.next_to(peg, UP, 0)
            group.save_state()
            group.rotate_in_place(-np.pi/2, RIGHT)
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
            self.play(group.move_to, group.original_location)
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

        self.num_disks = original_num_disks
        self.disk_height = original_disk_height

    def move_full_tower(self):
        self.move_subtower_to_peg(self.num_disks, 1)
        self.dither()
        self.reset_disks(run_time = 1, submobject_mode = "lagged_start")
        self.dither()

    def move_single_disk(self):
        for x in 0, 1, 0:
            self.move_disk(x)
        self.dither()

    def cannot_move_disk_with_crap_on_top(self):
        not_allowed = TextMobject("Not allowed")
        not_allowed.to_edge(UP)
        not_allowed.highlight(RED)
        cross = TexMobject("\\times")
        cross.set_fill(RED, opacity = 0.5)

        disk = self.disks[3]
        disk.save_state()
        self.move_disks_to_peg([3], 1, added_anims = [
            Transform(self.title, not_allowed)
        ])
        cross.replace(disk, stretch = False)
        self.play(FadeIn(cross))
        self.dither()
        self.play(
            FadeOut(cross),
            disk.restore
        )

    def cannot_move_disk_onto_smaller_disk(self):
        also_not_allowed = TextMobject("Also not allowed")
        also_not_allowed.to_edge(UP)
        also_not_allowed.highlight(RED)
        cross = TexMobject("\\times")
        cross.set_fill(RED, opacity = 0.5)

        disk = self.disks[2]
        disk.save_state()
        self.move_disks_to_peg([2], 2, added_anims = [
            Transform(self.title, also_not_allowed)
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

        































