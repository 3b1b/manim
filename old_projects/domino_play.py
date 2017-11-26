#!/usr/bin/env python
# -*- coding: utf-8 -*-

from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from animation.continual_animation import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from topics.objects import *
from topics.probability import *
from topics.complex_numbers import *
from scene import Scene
from scene.reconfigurable_scene import ReconfigurableScene
from scene.zoomed_scene import *
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *
from topics.graph_scene import *


class SimpleVelocityGraph(GraphScene):
    CONFIG = {
        # "frame_rate" : 4000,
        # "domino_thickness" : 7.5438,
        # "domino_spacing" : 8.701314282,
        "data_files" : [
            "data07.txt",
            "data13.txt",
            # "data11.txt",
        ],
        "colors" : [WHITE, BLUE, YELLOW, GREEN, MAROON_B],
        "x_axis_label" : "$t$",
        "y_axis_label" : "$v$",
        "x_min" : 0,
        "x_max" : 1.8,
        "x_tick_frequency" : 0.1,
        "x_labeled_nums" : np.arange(0, 1.8, 0.2),
        "y_tick_frequency" : 100,
        "y_min" : 0,
        "y_max" : 1000,
        "y_labeled_nums" : range(0, 1000, 200),
        "x_axis_width" : 12,
        "graph_origin" : 2.5*DOWN + 5*LEFT,
        "trailing_average_length" : 20,
        "include_domino_thickness" : False,
    }
    def construct(self):
        self.setup_axes()
        # self.save_all_images()
        for data_file, color in zip(self.data_files, self.colors):
            self.init_data(data_file)
            self.draw_dots(color)
            self.add_label_to_last_dot(
                "%s %s %.2f"%(
                    data_file[4:6], 
                    "hard" if self.friction == "low" else "felt",
                    self.domino_spacing,
                ),
                color
            )
            self.draw_lines(color)

    def save_all_images(self):
        indices = range(1, 20)
        for i1, i2 in it.combinations(indices, 2):
            to_remove = VGroup()
            for index in i1, i2:
                index_str = ("%.2f"%float(0.01*index))[-2:]
                data_file = "data%s.txt"%index_str
                self.init_data(data_file)
                color = WHITE if self.friction == "low" else BLUE
                self.draw_dots(color)
                self.add_label_to_last_dot(
                    "%s %s %.2f"%(
                        data_file[4:6], 
                        "hard" if self.friction == "low" else "felt",
                        self.domino_spacing,
                    ),
                    color
                )
                self.draw_lines(color)
                to_remove.add(self.dots, self.lines, self.label)
            self.save_image("dominos_%d_vs_%d"%(i1, i2))
            self.remove(to_remove)

    def init_data(self, data_file):
        file_name = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "dominos",
            data_file
        )

        file = open(file_name, "r")
        frames, notes = [], []
        for line in file:
            line = line.replace("  ", ",")
            line = line.replace("\n", "")
            entries = filter(
                lambda s : s is not "",
                line.split(",")
            )
            if len(entries) == 0:
                continue

            if entries[0] == "framerate":
                frame_rate = float(entries[1])
            elif entries[0] == "domino spacing":
                domino_spacing = float(entries[1])
            elif entries[0] == "domino thickness":
                domino_thickness = float(entries[1])
            elif entries[0] == "friction":
                self.friction = entries[1]
            else:
                try:
                    frames.append(int(entries[0]))
                except:
                    continue #How to treat?
                    # frames.append(frames[-1] + (frames[-1] - frames[-2]))
                if len(entries) > 1:
                    notes.append(entries[1])
                else:
                    notes.append("")
        frames = np.array(frames)

        self.times = (frames - frames[0])/float(frame_rate)
        delta_times = self.times[1:] - self.times[:-1]
        if self.include_domino_thickness:
            distance = domino_spacing+domino_thickness
        else:
            distance = domino_spacing
        self.velocities = distance/delta_times
        self.notes = notes

        n = self.trailing_average_length
        self.velocities = np.array([
            np.mean(self.velocities[max(0, i-n):i])
            for i in range(len(self.velocities))
        ])
        self.domino_spacing = domino_spacing
        self.domino_thickness = domino_thickness

    def draw_dots(self, color = WHITE):
        dots = VGroup()
        for time, v, note in zip(self.times, self.velocities, self.notes):
            dot = Dot(color = color)
            dot.scale(0.5)
            dot.move_to(self.coords_to_point(time, v))
            self.add(dot)
            dots.add(dot)
            if note == "twist":
                dot.highlight(RED)
        self.dots = dots

    def add_label_to_last_dot(self, label, color = WHITE):
        dot = self.dots[-1]
        label = TextMobject(label)
        label.scale(0.75)
        label.next_to(dot, UP, buff = MED_SMALL_BUFF)
        label.highlight(color)
        label.shift_onto_screen()
        self.label = label
        self.add(label)

    def draw_lines(self, color = WHITE, stroke_width = 2):
        lines = VGroup()
        for d1, d2 in zip(self.dots, self.dots[1:]):
            line = Line(d1.get_center(), d2.get_center())
            lines.add(line)
        lines.set_stroke(color, stroke_width)
        self.add(lines, self.dots)
        self.lines = lines

class ShowAllSteadyStateVelocities(SimpleVelocityGraph):
    CONFIG = {
        "x_axis_label" : "\\text{Domino spacing}",
        "x_min" : 0,
        "x_max" : 40,
        "x_axis_width" : 9,
        "x_tick_frequency" : 5,
        "x_labeled_nums" : range(0, 50, 10),
        "y_min" : 0,
        "y_max" : 400,
        "y_labeled_nums" : [],
        # "y_labeled_nums" : range(200, 1400, 200),
    }
    def construct(self):
        self.setup_axes()
        for index in range(1, 20):
            index_str = ("%.2f"%float(0.01*index))[-2:]
            data_file = "data%s.txt"%index_str
            self.init_data(data_file)
            color = WHITE if self.friction == "low" else BLUE
            label = TextMobject(
                index_str,
                color = color
            )
            label.scale(0.5)
            label.highlight(color)

            dot = Dot(color = color)
            dot.scale(0.5)
            dot.move_to(self.coords_to_point(
                self.domino_spacing, self.velocities[-1] - 400
            ))
            label.next_to(
                dot, 
                random.choice([LEFT, RIGHT]), 
                SMALL_BUFF
            )
            self.add(dot)
            self.add(label)
            print index_str, self.velocities[-1], self.friction

class Test(Scene):
    def construct(self):
        shift_val = 1.5

        domino1 = Rectangle(
            width = 0.5, height = 3,
            stroke_width = 0,
            fill_color = GREEN,
            fill_opacity = 1
        )
        domino1.shift(LEFT)
        domino2 = domino1.copy()
        domino2.set_fill(BLUE_E)
        domino2.shift(shift_val*RIGHT)
        spacing = shift_val - domino2.get_width()
        dominos = VGroup(domino1, domino2)
        for domino in dominos:
            line = DashedLine(domino.get_left(), domino.get_right())
            dot = Dot(domino.get_center())
            domino.add(line, dot)

        arc1 = Arc(
            radius = domino1.get_height(),
            start_angle = np.pi/2,
            angle = -np.arcsin(spacing / domino1.get_height())
        )
        arc1.shift(domino1.get_corner(DOWN+RIGHT))
        arc2 = Arc(
            radius = domino1.get_height()/2,
            start_angle = np.pi/2,
            angle = -np.arcsin(2*spacing/domino1.get_height())
        )
        arc2.shift(domino1.get_right())
        arc2.highlight(BLUE)
        arcs = VGroup(arc1, arc2)
        for arc, vect in zip(arcs, [DOWN+RIGHT, RIGHT]):
            arc_copy = arc.copy()
            point = domino1.get_critical_point(vect)
            arc_copy.add_control_points(3*[point])
            arc_copy.set_stroke(width = 0)
            arc_copy.set_fill(
                arc.get_stroke_color(),
                0.2,
            )
            self.add(arc_copy)

        domino1_ghost = domino1.copy()
        domino1_ghost.fade(0.8)
        self.add(domino1_ghost, dominos, arcs)

        self.play(Rotate(
            domino1,
            angle = arc1.angle,
            about_point = domino1.get_corner(DOWN+RIGHT),
            rate_func = there_and_back,
            run_time = 3,
        ))
        self.play(Rotate(
            domino1,
            angle = arc2.angle,
            about_point = domino1.get_right(),
            rate_func = there_and_back,
            run_time = 3,
        ))

        print arc1.angle, arc2.angle



























