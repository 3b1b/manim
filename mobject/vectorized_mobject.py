from scipy import linalg

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
        for index, array in zip(it.count(1), arrays):
            self.points[index::3] = array
        return self.points

    def get_anchors_and_handles(self):
        return [
            self.points[i::3]
            for i in range(3)
        ]

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
        num_handles = len(points) - 1
        #Must solve 2*num_handles equations to get the handles.
        #l and u are the number of lower an upper diagonal rows
        #in the matrix to solve.
        l, u = 2, 1    
        #diag is a representation of the matrix in diagonal form
        #See https://www.particleincell.com/2012/bezier-splines/
        #for how to arive at these equations
        diag = np.zeros((l+u+1, 2*num_handles))
        diag[0,1::2] = -1
        diag[0,2::2] = 1
        diag[1,0::2] = 2
        diag[1,1::2] = 1
        diag[2,1:-2:2] = -2
        diag[3,0:-3:2] = 1
        diag[2,-2] = 1
        diag[1,-1] = -2
        #This is the b as in Ax = b, where we are solving for x,
        #and A is represented using diag.  However, think of entries
        #to x and b as being points in space, not numbers
        b = np.zeros((2*num_handles, self.dim))
        b[1::2] = 2*points[1:]
        b[0] = points[0]
        b[-1] = points[-1]
        solve_func = lambda b : linalg.solve_banded(
            (l, u), diag, b
        )
        if self.is_closed():
            #Get equations to relate first and last points
            matrix = diag_to_matrix((l, u), diag)
            #last row handles second derivative
            matrix[-1, [0, 1]] = matrix[0, [0, 1]]
            #first row handles first derivative
            matrix[0,:] = np.zeros(matrix.shape[1])
            matrix[0,[0, -1]] = [1, 1]
            b[0] = 2*points[0]
            b[-1] = np.zeros(self.dim)
            solve_func = lambda b : linalg.solve(matrix, b)
        handle_pairs = np.zeros((2*num_handles, self.dim))
        for i in range(self.dim):
            handle_pairs[:,i] = solve_func(b[:,i])
        handles1 = handle_pairs[0::2]
        handles2 = handle_pairs[1::2]
        self.set_anchors_and_handles(points, handles1, handles2)
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

    ## Information about line

    def get_num_points(self):
        return (len(self.points) - 1)/3 + 1

    def point_from_proportion(self, alpha):
        num_cubics = self.get_num_points()-1
        interpoint_alpha = num_cubics*(alpha % (1./num_cubics))
        index = 3*int(alpha*num_cubics)
        cubic = bezier(self.points[index:index+4])
        return cubic(interpoint_alpha)


    ## Alignment
    def align_points_with_larger(self, larger_mobject):
        assert(isinstance(larger_mobject, VectorizedMobject))
        anchors, handles1, handles2 = self.get_anchors_and_handles()
        old_n = len(anchors)
        new_n = larger_mobject.get_num_points()
        #Buff up list of anchor points to appropriate length
        new_anchors = anchors[old_n*np.arange(new_n)/new_n]
        #At first, handles are on anchor points 
        #the [2:] is because start has no handles
        new_points = new_anchors.repeat(3, axis = 0)[2:]
        #These indices indicate the spots between genuinely
        #different anchor points in new_points list
        indices = 3*(np.arange(old_n) * new_n / old_n)[1:]
        new_points[indices+1] = handles1
        new_points[indices+2] = handles2
        self.set_points(new_points, mode = "handles_included")
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









