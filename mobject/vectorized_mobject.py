

from .mobject import Mobject

from helpers import *

class VectorizedMobject(Mobject):
    CONFIG = {
        "closed" : False,
        "fill_color" : BLACK,
        "fill_opacity" : 0.0
    }

    ## Colors
    def init_colors(self):
        self.set_stroke_color(self.color)
        self.set_fill_color(self.fill_color)
        return self

    def set_fill_color(self, color):
        self.fill_rgb = color_to_rgb(color)
        return self

    def set_stroke_color(self, color):
        self.stroke_rgb = color_to_rgb(color)

    def highlight(self, color):
        self.set_fill_color(color)
        self.set_stroke_color(color)
        return self

    def get_fill_color(self):
        return Color(rgb = self.fill_rgb)

    def get_fill_opacity(self):
        return self.fill_opacity

    def get_stroke_color(self):
        return Color(rgb = self.stroke_rgb)

    #TODO, get color?  Specify if stroke or fill
    #is the predominant color attribute?

    ## Drawing
    def init_points(self):
        ##Default to starting at origin
        self.points = np.zeros((1, self.dim))
        return self
    
    def start_at(self, point):
        self.points[0] = point
        return self

    def close(self):
        self.closed = True
        return self

    def open(self):
        self.closed = False
        return self

    def is_closed(self):
        return self.closed

    def add_point(self, handle1, handle2, point):
        self.points = np.append(
            self.points,
            [handle1, handle2, point],
            axis = 0
        )
        return self

    def set_anchors_and_handles(self, anchors, handles1, handles2):
        assert(len(anchors) == len(handles1)+1)
        assert(len(anchors) == len(handles2)+1)
        total_len = 3*(len(anchors)-1) + 1
        self.points = np.zeros((total_len, self.dim))
        self.points[0] = anchors[0]
        arrays = [handles1, handles2, anchors[1:]]
        for index, array in enumerate(arrays):
            self.points[index+1::3] = array
        return self.points

    def set_points_as_corners(self, points):
        if len(points) <= 1:
            return self
        points = self.close_if_needed(points)
        handles1 = points[:-1]
        handles2 = points[1:]
        self.set_anchors_and_handles(points, handles1, handles2)
        return self

    def set_points_smoothly(self, points):
        if len(points) <= 1:
            return self
        points = self.close_if_needed(points)
        h1, h2 = get_smooth_handle_points(points, self.is_closed())
        self.set_anchors_and_handles(points, h1, h2)
        return self

    def close_if_needed(self, points):
        if self.is_closed() and not np.all(points[0] == points[-1]):
            points = np.append(
                points,
                [points[0]],
                axis = 0
            )
        return points

    def set_points(self, points, mode = "smooth"):
        points = np.array(points)
        if mode == "smooth":
            self.set_points_smoothly(points)
        elif mode == "corners":
            self.set_points_as_corners(points)
        elif mode == "handles_included":
            self.points = points
        else:
            raise Exception("Unknown mode")
        return self

    def change_mode(self, mode):
        anchors, h1, h2 = self.get_anchors_and_handles()
        self.set_points(anchors, mode = mode)
        return self

    def make_smooth(self):
        return self.change_mode("smooth")

    def make_jagged(self):
        return self.change_mode("corners")

    ## Information about line

    def component_curves_iter(self):
        for i in range(0, len(self.points)-1, 3):
            yield bezier(self.points[i:i+4])

    def get_num_points(self):
        return (len(self.points) - 1)/3 + 1

    def point_from_proportion(self, alpha):
        num_cubics = self.get_num_points()-1
        interpoint_alpha = num_cubics*(alpha % (1./num_cubics))
        index = 3*int(alpha*num_cubics)
        cubic = bezier(self.points[index:index+4])
        return cubic(interpoint_alpha)

    def get_anchors_and_handles(self):
        return [
            self.points[i::3]
            for i in range(3)
        ]

    ## Alignment
    # def align_points_with_larger(self, larger_mobject):
    #     assert(isinstance(larger_mobject, VectorizedMobject))
    #     anchors, handles1, handles2 = self.get_anchors_and_handles()
    #     old_n = len(anchors)
    #     new_n = larger_mobject.get_num_points()
    #     #Buff up list of anchor points to appropriate length
    #     new_anchors = anchors[old_n*np.arange(new_n)/new_n]
    #     #At first, handles are on anchor points 
    #     #the [2:] is because start has no handles
    #     new_points = new_anchors.repeat(3, axis = 0)[2:]
    #     #These indices indicate the spots between genuinely
    #     #different anchor points in new_points list
    #     indices = 3*(np.arange(old_n) * new_n / old_n)[1:]
    #     new_points[indices+1] = handles1
    #     new_points[indices+2] = handles2
    #     self.set_points(new_points, mode = "handles_included")
    #     return self

    def align_points_with_larger(self, larger_mobject):
        assert(isinstance(larger_mobject, VectorizedMobject))
        points = np.array([self.points[0]])
        target_len = larger_mobject.get_num_points()-1
        num_curves = self.get_num_points()-1
        #curves are buckets, and we need to know how many new
        #anchor points to put into each one
        index_allocation = (np.arange(target_len) * num_curves)/target_len
        for index, curve in enumerate(self.component_curves_iter()):
            num_inter_points = sum(index_allocation == index)
            step = 1./num_inter_points
            alphas = np.arange(0, 1+step, step)
            new_anchors = np.array(map(curve, alphas))
            h1, h2 = get_smooth_handle_points(new_anchors)
            new_points = np.array(
                zip(h1, h2, new_anchors[1:])
            )
            new_points = new_points.reshape((new_points.size/3, 3))
            points = np.append(points, new_points, 0)
        self.set_points(points, "handles_included")
        return self

    def get_point_mobject(self):
        return VectorizedPoint(self.get_center())

    def interpolate_color(self, mobject1, mobject2, alpha):
        attrs = [
            "stroke_rgb", 
            "stroke_width",            
            "fill_rgb", 
            "fill_opacity",
        ]
        for attr in attrs:
            setattr(self, attr, interpolate(
                getattr(mobject1, attr),
                getattr(mobject2, attr),
                alpha
            ))


class VectorizedPoint(VectorizedMobject):
    CONFIG = {
        "color" : BLACK,
    }
    def __init__(self, location = ORIGIN, **kwargs):
        VectorizedMobject.__init__(self, **kwargs)
        self.set_points([location])









