import re

from .mobject import Mobject

from helpers import *

class VMobject(Mobject):
    CONFIG = {
        "fill_color"       : None,
        "fill_opacity"     : 0.0,
        "stroke_color"     : None,
        #Indicates that it will not be displayed, but
        #that it should count in parent mobject's path
        "is_subpath"       : False,
        "close_new_points" : False,
        "mark_paths_closed" : False,
        "considered_smooth" : True,
        "propogate_style_to_family" : False,
    }

    ## Colors
    def init_colors(self):
        self.set_style_data(
           stroke_color = self.stroke_color or self.color,
           stroke_width = self.stroke_width,
           fill_color = self.fill_color or self.color, 
           fill_opacity = self.fill_opacity,
           family = self.propogate_style_to_family
        )
        return self

    def set_family_attr(self, attr, value):
        for mob in self.submobject_family():
            setattr(mob, attr, value)

    def set_style_data(self, 
                       stroke_color = None, 
                       stroke_width = None,
                       fill_color = None, 
                       fill_opacity = None,
                       family = True):
        if stroke_color is not None:
            self.stroke_rgb = color_to_rgb(stroke_color)
        if fill_color is not None:
            self.fill_rgb = color_to_rgb(fill_color)
        if stroke_width is not None:
            self.stroke_width = stroke_width
        if fill_opacity is not None:
            self.fill_opacity = fill_opacity
        if family:
            kwargs = locals()
            kwargs.pop("self")
            for mob in self.submobjects:
                mob.set_style_data(**kwargs)
        return self

    def set_fill(self, color = None, opacity = None, family = True):
        probably_meant_to_change_opacity = reduce(op.and_, [
            color is not None,
            opacity is None,
            self.fill_opacity == 0
        ])
        if probably_meant_to_change_opacity:
            opacity = 1
        return self.set_style_data(
            fill_color = color, 
            fill_opacity = opacity, 
            family = family
        )

    def set_stroke(self, color = None, width = None, family = True):
        return self.set_style_data(
            stroke_color = color, 
            stroke_width = width, 
            family = family
        )

    def highlight(self, color, family = True):
        self.set_style_data(
            stroke_color = color, 
            fill_color = color,
            family = family
        )
        return self

    def fade(self, darkness = 0.5):
        for submob in self.submobject_family():
            submob.set_stroke(
                width = (1-darkness)*submob.get_stroke_width(),
                family = False
            )
            submob.set_fill(
                opacity = (1-darkness),
                family = False
            )
        return self

    def get_fill_color(self):
        try:
            self.fill_rgb = np.clip(self.fill_rgb, 0, 1)
            return Color(rgb = self.fill_rgb)
        except:
            return Color(WHITE)

    def get_fill_opacity(self):
        return self.fill_opacity

    def get_stroke_color(self):
        try:
            self.stroke_rgb = np.clip(self.stroke_rgb, 0, 1)
            return Color(rgb = self.stroke_rgb)
        except:
            return Color(WHITE)

    def get_stroke_width(self):
        return self.stroke_width

    def get_color(self):
        if self.fill_opacity == 0:
            return self.get_stroke_color()
        return self.get_fill_color()

    ## Drawing
    def start_at(self, point):
        if len(self.points) == 0:
            self.points = np.zeros((1, 3))
        self.points[0] = point
        return self

    def add_control_points(self, control_points):
        assert(len(control_points) % 3 == 0)
        self.points = np.append(
            self.points,
            control_points,
            axis = 0
        )
        return self

    def is_closed(self):
        return is_closed(self.points)

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
        points = np.array(points)
        self.set_anchors_and_handles(points, *[
            interpolate(points[:-1], points[1:], alpha)
            for alpha in 1./3, 2./3
        ])
        return self

    def set_points_smoothly(self, points):
        if len(points) <= 1:
            return self
        h1, h2 = get_smooth_handle_points(points)
        self.set_anchors_and_handles(points, h1, h2)
        return self

    def set_points(self, points):
        self.points = np.array(points)
        return self

    def set_anchor_points(self, points, mode = "smooth"):
        if not isinstance(points, np.ndarray):
            points = np.array(points)
        if self.close_new_points and not is_closed(points):
            points = np.append(points, [points[0]], axis = 0)
        if mode == "smooth":
            self.set_points_smoothly(points)
        elif mode == "corners":
            self.set_points_as_corners(points)
        else:
            raise Exception("Unknown mode")
        return self

    def change_anchor_mode(self, mode):
        for submob in self.family_members_with_points():
            anchors, h1, h2 = submob.get_anchors_and_handles()
            submob.set_anchor_points(anchors, mode = mode)
        return self

    def make_smooth(self):
        self.considered_smooth = True
        return self.change_anchor_mode("smooth")

    def make_jagged(self):
        return self.change_anchor_mode("corners")

    def add_subpath(self, points):
        """
        A VMobject is meant to represnt
        a single "path", in the svg sense of the word.
        However, one such path may really consit of separate
        continuous components if there is a move_to command.

        These other portions of the path will be treated as submobjects,
        but will be tracked in a separate special list for when
        it comes time to display.
        """
        subpath_mobject = self.copy() ##Really helps to be of the same class
        subpath_mobject.submobjects = []
        subpath_mobject.is_subpath = True
        subpath_mobject.set_points(points)
        self.add(subpath_mobject)
        return subpath_mobject

    def append_vectorized_mobject(self, vectorized_mobject):
        new_points = list(vectorized_mobject.points)
        if len(new_points) == 0:
            return
        if self.get_num_points() == 0:
            self.start_at(new_points[0])
            self.add_control_points(new_points[1:])
        else:
            self.add_control_points(2*[new_points[0]] + new_points)
        return self

    def get_subpath_mobjects(self):
        return filter(
            lambda m : hasattr(m, 'is_subpath') and m.is_subpath,
            self.submobjects
        )

    def apply_function(self, function, maintain_smoothness = False):
        Mobject.apply_function(self, function)
        if maintain_smoothness and self.considered_smooth:
            self.make_smooth()
        return self


    ## Information about line

    def component_curves(self):
        for n in range(self.get_num_anchor_points()-1):
            yield self.get_nth_curve(n)

    def get_nth_curve(self, n):
        return bezier(self.points[3*n:3*n+4])

    def get_num_anchor_points(self):
        return (len(self.points) - 1)/3 + 1

    def point_from_proportion(self, alpha):
        num_cubics = self.get_num_anchor_points()-1
        interpoint_alpha = num_cubics*(alpha % (1./num_cubics))
        index = min(3*int(alpha*num_cubics), 3*num_cubics)
        cubic = bezier(self.points[index:index+4])
        return cubic(interpoint_alpha)

    def get_anchors_and_handles(self):
        return [
            self.points[i::3]
            for i in range(3)
        ]

    def get_anchors(self):
        return self.points[::3]

    def get_points_defining_boundary(self):
        return self.get_anchors()

        
    ## Alignment

    def align_points(self, mobject):
        Mobject.align_points(self, mobject)
        is_subpath = self.is_subpath or mobject.is_subpath
        self.is_subpath = mobject.is_subpath = is_subpath
        mark_closed = self.mark_paths_closed and mobject.mark_paths_closed
        self.mark_paths_closed = mobject.mark_paths_closed = mark_closed
        return self

    def align_points_with_larger(self, larger_mobject):
        assert(isinstance(larger_mobject, VMobject))
        self.insert_n_anchor_points(
            larger_mobject.get_num_anchor_points()-\
            self.get_num_anchor_points()
        )
        return self

    def insert_n_anchor_points(self, n):
        curr = self.get_num_anchor_points()
        if curr == 0:
            self.points = np.zeros((1, 3))
            n = n-1
        if curr == 1:
            self.points = np.repeat(self.points, 3*n+1, axis = 0)
            return self
        points = np.array([self.points[0]])
        num_curves = curr-1
        #Curves in self are buckets, and we need to know 
        #how many new anchor points to put into each one.  
        #Each element of index_allocation is like a bucket, 
        #and its value tells you the appropriate index of 
        #the smaller curve.
        index_allocation = (np.arange(curr+n-1) * num_curves)/(curr+n-1)
        for index in range(num_curves):
            curr_bezier_points = self.points[3*index:3*index+4]
            num_inter_curves = sum(index_allocation == index)
            alphas = np.arange(0, num_inter_curves+1)/float(num_inter_curves)
            for a, b in zip(alphas, alphas[1:]):
                new_points = partial_bezier_points(
                    curr_bezier_points, a, b
                )
                points = np.append(
                    points, new_points[1:], axis = 0
                )
        self.set_points(points)
        return self

    def get_point_mobject(self, center = None):
        if center is None:
            center = self.get_center()
        return VectorizedPoint(center)

    def repeat_submobject(self, submobject):
        if submobject.is_subpath:
            return VectorizedPoint(submobject.points[0])
        return submobject.copy()

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
            if alpha == 1.0:
                # print getattr(mobject2, attr)
                setattr(self, attr, getattr(mobject2, attr))

    def pointwise_become_partial(self, mobject, a, b):
        assert(isinstance(mobject, VMobject))
        #Partial curve includes three portions:
        #-A middle section, which matches the curve exactly
        #-A start, which is some ending portion of an inner cubic
        #-An end, which is the starting portion of a later inner cubic
        if a <= 0 and b >= 1:
            self.set_points(mobject.points)
            self.mark_paths_closed = mobject.mark_paths_closed
            return self
        self.mark_paths_closed = False
        num_cubics = mobject.get_num_anchor_points()-1
        lower_index = int(a*num_cubics)
        upper_index = int(b*num_cubics)
        points = np.array(
            mobject.points[3*lower_index:3*upper_index+4]
        )
        if len(points) > 1:
            a_residue = (num_cubics*a)%1
            b_residue = (num_cubics*b)%1
            if b == 1:
                b_residue = 1
            points[:4] = partial_bezier_points(
                points[:4], a_residue, 1
            )
            points[-4:] = partial_bezier_points(
                points[-4:], 0, b_residue
            )
        self.set_points(points)
        return self

class VGroup(VMobject):
    #Alternate name to improve readability during use
    pass 

class VectorizedPoint(VMobject):
    CONFIG = {
        "color" : BLACK,
        "fill_opacity" : 0,
        "stroke_width" : 0,
        "artificial_width" : 0.01,
        "artificial_height" : 0.01,
    }
    def __init__(self, location = ORIGIN, **kwargs):
        VMobject.__init__(self, **kwargs)
        self.set_points(np.array([location]))

    def get_width(self):
        return self.artificial_width

    def get_height(self):
        return self.artificial_height






