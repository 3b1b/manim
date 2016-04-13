import re

from .mobject import Mobject

from helpers import *

class VectorizedMobject(Mobject):
    CONFIG = {
        "fill_color"   : BLACK,
        "fill_opacity" : 0.0,
        #Indicates that it will not be displayed, but
        #that it should count in parent mobject's path
        "is_subpath"   : False, 
    }
    def __init__(self, *args, **kwargs):
        self.subpath_mobjects = []
        Mobject.__init__(self, *args, **kwargs)

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

    def add_point(self, handle1, handle2, point):
        self.points = np.append(
            self.points,
            [handle1, handle2, point],
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
        handles1 = points[:-1]
        handles2 = points[1:]
        self.set_anchors_and_handles(points, handles1, handles2)
        return self

    def set_points_smoothly(self, points):
        if len(points) <= 1:
            return self
        h1, h2 = get_smooth_handle_points(points)
        self.set_anchors_and_handles(points, h1, h2)
        return self

    def set_points(self, points):
        self.points = points
        return self

    def set_anchor_points(self, points, mode = "smooth"):
        if not isinstance(points, np.ndarray):
            points = np.array(points)
        if self.closed and not is_closed(points):
            points = np.append(points, [points[0]], axis = 0)
        if mode == "smooth":
            self.set_points_smoothly(points)
        elif mode == "corners":
            self.set_points_as_corners(points)
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

    def add_subpath(self, points):
        """
        A VectorizedMobject is meant to represnt
        a single "path", in the svg sense of the word.
        However, one such path may really consit of separate
        continuous components if there is a move_to command.

        These other portions of the path will be treated as submobjects,
        but will be tracked in a separate special list for when
        it comes time to display.
        """
        subpath_mobject = VectorizedMobject(
            is_subpath = True
        )
        subpath_mobject.set_points(points)
        self.subpath_mobjects.append(subpath_mobject)
        self.add(subpath_mobject)
        return self

    ## Information about line

    def component_curves(self):
        for n in range(self.get_num_points()-1):
            yield self.get_nth_curve(n)

    def get_nth_curve(self, n):
        return bezier(self.points[3*n:3*n+4])

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

    def align_points_with_larger(self, larger_mobject):
        assert(isinstance(larger_mobject, VectorizedMobject))
        points = np.array([self.points[0]])
        target_len = larger_mobject.get_num_points()-1
        num_curves = self.get_num_points()-1
        #curves are buckets, and we need to know how many new
        #anchor points to put into each one
        index_allocation = (np.arange(target_len) * num_curves)/target_len
        for index, curve in enumerate(self.component_curves()):
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
        self.closed = mobject1.is_closed() and mobject2.is_closed()


    def become_partial(self, mobject, a, b):
        assert(isinstance(mobject, VectorizedMobject))        
        #Partial curve includes three portions:
        #-A middle section, which matches the curve exactly
        #-A start, which is some ending portion of an inner cubic
        #-An end, which is the starting portion of a later inner cubic
        self.open()
        if a <= 0 and b >= 1:
            if mobject.is_closed():
                self.close()
            self.set_points(mobject.points, "handles_included")
            return self
        num_cubics = mobject.get_num_points()-1
        lower_index = int(a*num_cubics)
        upper_index = int(b*num_cubics)
        points = np.array(
            mobject.points[3*lower_index:3*upper_index+4]
        )
        if len(points) > 1:
            #This is a kind of neat-but-dense algorithm 
            #for how to interpolate the handle points
            a_residue = (num_cubics*a)%1
            points[:4] = [
                bezier(points[i:4])(a_residue)
                for i in range(4)
            ]
            b_residue = (num_cubics*b)%1
            points[-4:] = [
                bezier(points[-4:len(points)-3+i])(b_residue)
                for i in range(4)
            ]
        self.set_points(points, "handles_included")
        return self


class VectorizedPoint(VectorizedMobject):
    CONFIG = {
        "color" : BLACK,
    }
    def __init__(self, location = ORIGIN, **kwargs):
        VectorizedMobject.__init__(self, **kwargs)
        self.set_points([location])

class VectorizedMobjectFromSVGPathstring(VectorizedMobject):
    def __init__(self, path_string, **kwargs):
        digest_locals(self)
        VectorizedMobject.__init__(self, **kwargs)

    def generate_points(self):
        path_commands = [
            "M", #moveto
            "L", #lineto
            "H", #horizontal lineto
            "V", #vertical lineto
            "C", #curveto
            "S", #smooth curveto
            "Q", #quadratic Bezier curve
            "T", #smooth quadratic Bezier curveto
            "A", #elliptical Arc
            "Z", #closepath
        ]
        pattern = "[%s]"%("".join(path_commands))
        pairs = zip(
            re.findall(pattern, self.pathstring),
            re.split(pattern, self.path_string)
        )
        for command, coord_string in pairs:
            pass
            #TODO







