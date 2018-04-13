from big_ol_pile_of_manim_imports import *
from random import *

def text_range(start,stop,step): # a range as a list of strings
    numbers = np.arange(start,stop,step)
    labels = []
    for x in numbers:
        labels.append(str(x))
    return labels


class Histogram(VMobject):

    CONFIG = {
        "start_color" : RED,
        "end_color" : BLUE,
        "x_scale" : 1.0,
        "y_scale" : 1.0,
        "x_labels" : "auto", # widths, mids, auto, none, [...]
        "y_labels" : "auto", # auto, none, [...]
        "x_min" : 0
    }

    def __init__(self, x_values, y_values, mode = "widths", **kwargs):
        # mode = "widths" : x_values means the widths of the bars
        # mode = "posts"  : x_values means the delimiters btw the bars 

        digest_config(self, kwargs)

        if mode == "widths" and len(x_values) != len(y_values):
            raise Exception("Array lengths do not match up!")
        elif mode == "posts" and len(x_values) != len(y_values) + 1:
            raise Exception("Array lengths do not match up!")


        self.y_values = y_values
        self.x_values = x_values
        self.mode = mode
        self.process_values()

        VMobject.__init__(self, **kwargs)
        

    def process_values(self):

         # preliminaries
        self.y_values = np.array(self.y_values)

        if self.mode == "widths":
            self.widths = self.x_values
            self.posts = np.cumsum(self.widths)
            self.posts = np.insert(self.posts, 0, 0)
            self.posts += self.x_min
            self.x_max = self.posts[-1]
        elif self.mode == "posts":
            self.posts = self.x_values
            self.widths = self.x_values[1:] - self.x_values[:-1]
            self.x_min = self.posts[0]
            self.x_max = self.posts[-1]
        else:
            raise Exception("Invalid mode or no mode specified!")

        self.x_mids = 0.5 * (self.posts[:-1] + self.posts[1:])

        self.widths_scaled = self.x_scale * self.widths
        self.posts_scaled = self.x_scale * self.posts
        self.x_min_scaled = self.x_scale * self.x_min
        self.x_max_scaled = self.x_scale * self.x_max

        self.y_values_scaled = self.y_scale * self.y_values



    def generate_points(self):

        self.process_values()
        for submob in self.submobjects:
            self.remove(submob)

        def empty_string_array(n):
            arr = []
            for i in range(n):
                arr.append("")
            return arr

        def num_arr_to_string_arr(arr): # converts number array to string array
            ret_arr = []
            for x in arr:
                if x == np.floor(x):
                    new_x = int(np.floor(x))
                else:
                    new_x = x
                ret_arr.append(str(new_x))
            return ret_arr

        previous_bar = ORIGIN
        self.bars = VGroup()
        self.x_labels_group = VGroup()
        self.y_labels_group = VGroup()
        outline_points = []

        if self.x_labels == "widths":
            self.x_labels = num_arr_to_string_arr(self.widths)
        elif self.x_labels == "mids":
            self.x_labels = num_arr_to_string_arr(self.x_mids)
        elif self.x_labels == "none":
            self.x_labels = empty_string_array(len(self.widths))

        if self.y_labels == "auto":
            self.y_labels = num_arr_to_string_arr(self.y_values)
        elif self.y_labels == "none":
            self.y_labels = empty_string_array(len(self.y_values))




        for (i,x) in enumerate(self.x_mids):

            bar = Rectangle(
                width = self.widths_scaled[i],
                height = self.y_values_scaled[i],
            )
            t = float(x - self.x_min)/(self.x_max - self.x_min)
            bar_color = interpolate_color(
                self.start_color,
                self.end_color,
                t
            )
            bar.set_fill(color = bar_color, opacity = 1)
            bar.set_stroke(width = 0)
            bar.next_to(previous_bar,RIGHT,buff = 0, aligned_edge = DOWN)
            
            self.bars.add(bar)

            x_label = TextMobject(self.x_labels[i])
            x_label.next_to(bar,DOWN)
            self.x_labels_group.add(x_label)

            y_label = TextMobject(self.y_labels[i])
            y_label.next_to(bar, UP)
            self.y_labels_group.add(y_label)

            if i == 0:
                # start with the lower left
                outline_points.append(bar.get_anchors()[-2])

            # upper two points of each bar
            outline_points.append(bar.get_anchors()[0])
            outline_points.append(bar.get_anchors()[1])

            previous_bar = bar
        # close the outline
            # lower right
        outline_points.append(bar.get_anchors()[2])
            # lower left
        outline_points.append(outline_points[0])

        self.outline = Polygon(*outline_points)
        self.outline.set_stroke(color = WHITE)
        self.add(self.bars, self.x_labels_group, self.y_labels_group, self.outline)

        print self.submobjects

    def get_lower_left_point(self):
        return self.bars[0].get_anchors()[-2]



class BuildUpHistogram(Animation):

    def __init__(self, hist, **kwargs):
        self.histogram = hist







class FlashThroughHistogram(Animation):
    CONFIG = {
        "cell_color" : WHITE,
        "cell_opacity" : 0.8,
        "hist_opacity" : 0.2
    }

    def __init__(self, mobject, direction = "horizontal", mode = "random", **kwargs):

        digest_config(self, kwargs)

        self.cell_height = mobject.y_scale
        self.prototype_cell = Rectangle(
            width = 1,
            height = self.cell_height,
            fill_color = self.cell_color,
            fill_opacity = self.cell_opacity,
            stroke_width = 0,
        )

        x_values = mobject.x_values
        y_values = mobject.y_values

        self.mode = mode
        self.direction = direction

        self.generate_cell_indices(x_values,y_values)
        Animation.__init__(self,mobject,**kwargs)



    def generate_cell_indices(self,x_values,y_values):

        self.cell_indices = []
        for (i,x) in enumerate(x_values):

            nb_cells = y_values[i]
            for j in range(nb_cells):
                self.cell_indices.append((i, j))

        self.reordered_cell_indices = self.cell_indices
        if self.mode == "random":
            shuffle(self.reordered_cell_indices)


    def cell_for_index(self,i,j):

        if self.direction == "vertical":
            width = self.mobject.x_scale
            height = self.mobject.y_scale
            x = (i + 0.5) * self.mobject.x_scale
            y = (j + 0.5) * self.mobject.y_scale
            center = self.mobject.get_lower_left_point() + x * RIGHT + y * UP
        
        elif self.direction == "horizontal":
            width = self.mobject.x_scale / self.mobject.y_values[i]
            height = self.mobject.y_scale * self.mobject.y_values[i]
            x = i * self.mobject.x_scale + (j + 0.5) * width
            y = height / 2
            center = self.mobject.get_lower_left_point() + x * RIGHT + y * UP

        cell = Rectangle(width = width, height = height)
        cell.move_to(center)
        return cell


    def update_mobject(self,t):

        if t == 0:
            self.mobject.add(self.prototype_cell)

        flash_nb = int(t * (len(self.cell_indices))) - 1
        (i,j) = self.reordered_cell_indices[flash_nb]
        cell = self.cell_for_index(i,j)
        self.prototype_cell.width = cell.get_width()
        self.prototype_cell.height = cell.get_height()
        self.prototype_cell.generate_points()
        self.prototype_cell.move_to(cell.get_center())

        #if t == 1:
        #   self.mobject.remove(self.prototype_cell)

















class SampleScene(Scene):

    def construct(self):

        x_values = np.array([1,2,3,4,5])
        y_values = np.array([4,3,5,2,3])

        hist1 = Histogram(
            x_values = x_values,
            y_values = y_values,
            x_scale = 0.5,
            y_scale = 0.5,
        ).shift(1*DOWN)
        self.add(hist1)
        self.wait()

        y_values2 = np.array([3,8,7,15,5])

        hist2 = Histogram(
            x_values = x_values,
            y_values = y_values2,
            x_scale = 0.5,
            y_scale = 0.5,
            x_labels = text_range(1,6,1),
        )

        v1 = hist1.get_lower_left_point()
        v2 = hist2.get_lower_left_point()
        hist2.shift(v1 - v2)
        
        # self.play(
        #   ReplacementTransform(hist1,hist2)
        # )

        self.play(
            FlashThroughHistogram(
                hist1,
                direction = "horizontal",
                mode = "linear",
                run_time = 10,
                rate_func = None,
            )
        )











