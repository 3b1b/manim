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

    def get_storke_color(self):
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
        handles1 = points[:-1]
        handles2 = points[1:]
        self.set_anchors_and_handles(points, handles1, handles2)
        return self

    def set_points_smoothly(self, points):
        if self.is_closed():
            points = np.append(
                points,
                [points[0], points[1]],
                axis = 0
            )
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
        #This is the b as in Ax = b, where we are solving for x,
        #and A is represented using diag.  However, think of entries
        #to x and b as being points in space, not numbers
        b = np.zeros((2*num_handles, self.dim))
        b[1::2] = 2*points[1:]
        b[0] = points[0]
        b[-1] = points[-1]

        handle_pairs = np.zeros((2*num_handles, self.dim))
        for i in range(self.dim):
            handle_pairs[:,i] = linalg.solve_banded(
                (l, u), diag, b[:,i]
            )
        handles1 = handle_pairs[0::2]
        handles2 = handle_pairs[1::2]
        if self.is_closed():
            #Ignore last point that was artificially added
            #to smooth out the closing.
            #TODO, is the the best say to handle this?
            handles1[0] = handles1[-1]
            points = points[:-1]
            handles1 = handles1[:-1]
            handles2 = handles2[:-1]

        self.set_anchors_and_handles(points, handles1, handles2)


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
        pass

    def point_from_proportion(self, alpha):
        pass
















