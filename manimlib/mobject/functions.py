from manimlib.constants import *
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.config_ops import digest_config
import math


class ParametricFunction(VMobject):
    CONFIG = {
        "t_min": 0,
        "t_max": 1,
        "step_size": 0.01,  # Use "auto" (lowercase) for automatic step size
        "dt": 1e-8,
        # TODO, be smarter about figuring these out?
        "discontinuities": [],
        "tol_point": 1e5,
        "tol_del_mult": 1e-2
    }

    def __init__(self, function=None, **kwargs):
        # either get a function from __init__ or from CONFIG
        self.function = function or self.function
        VMobject.__init__(self, **kwargs)

    def get_function(self):
        return self.function

    def get_point_from_function(self, t):
        return self.function(t)

    def get_step_size(self, t=None):
        if self.step_size == "auto":
            """
            for x between -1 to 1, return 0.01
            else, return log10(x) (rounded)
            e.g.: 10.5 -> 0.1 ; 1040 -> 10
            """
            if t == 0:
                scale = 0
            else:
                scale = math.log10(abs(t))
                if scale < 0:
                    scale = 0

                scale = math.floor(scale)

            scale -= 2
            return math.pow(10, scale)
        else:
            return self.step_size

    """
    tol_point is the tolerance level for the coordinates of points.
        If either the x coordinate or y coordinate are greater than
        the tolerance then that point is considered a discontinuity.
        This treats infinite discontinuities.
    
    tol_del_mult is a bit more complicated.
        A function is continuous if for any specified change in the
        function you can find a change in the input that gives rise
        to a change in the function less than the specified change.
        To test if the function is continuous, we test if the change
        in the function at different resolutions for changes in x
        get smaller as the change gets smaller, or if the changes
        become constant. If they get smaller, the function is 
        continuous at the point, if they level off then it is
        discontinuous.
        This treats break discontinuities.
    """
    
    def point_is_finite(self, point):
        x,y = point[:2]
        mag = np.sqrt(x**2 + y**2)
        return mag <= self.tol_point
    
    def get_discontinuities(self):
        disconts = []
        for t in np.arange(self.t_min-2*self.step_size, self.t_max+2*self.step_size, self.step_size):
            p1 = self.function(t)
            x1,y1 = p1[:2]
            if not self.point_is_finite(p1):
                disconts.append(t)
                continue

            ss1 = self.get_step_size(t)
            ss2 = ss1/2
            ss3 = ss1/10
            
            t2 = t + ss1
            t3 = t + ss2
            t4 = t + ss3
            
            p2 = self.function(t2)
            p3 = self.function(t3)
            p4 = self.function(t4)
            
            def calc_delta_mag(p1, p2):
              delta = p2-p1
              return np.sqrt(delta.dot(delta))
            
            d1 = calc_delta_mag(p1,p2)
            d2 = calc_delta_mag(p1,p3)
            d3 = calc_delta_mag(p1,p4)
            #Seeing delta at different resulotions
            
            if np.abs(d2-d1)<self.tol_del_mult*ss2 or np.abs(d3-d1)<self.tol_del_mult*ss3:
              disconts.append(t)
            
        return disconts

    def generate_points(self):
        t_min, t_max = self.t_min, self.t_max
        dt = self.dt
        
        self.discontinuities = self.get_discontinuities()
        discontinuities = np.array(list(self.discontinuities))
        
        boundary_times = [
            self.t_min, self.t_max,
            *(discontinuities - dt),
            *(discontinuities + dt),
        ]
        boundary_times.sort()
        for t1, t2 in zip(boundary_times[0::2], boundary_times[1::2]):
            t_range = list(np.arange(t1, t2, self.get_step_size(t1)))
            if t_range[-1] != t2:
                t_range.append(t2)
            points_l = []
            for t in t_range:
                point = self.function(t)
                if self.point_is_finite(point):
                    points_l.append(point)
            points = np.array(points_l)
            if len(points) > 0:
                self.start_new_path(points[0])
                self.add_points_as_corners(points[1:])
        self.make_smooth()
        return self


class FunctionGraph(ParametricFunction):
    CONFIG = {
        "color": YELLOW,
        "x_min": -FRAME_X_RADIUS,
        "x_max": FRAME_X_RADIUS,
    }

    def __init__(self, function, **kwargs):
        digest_config(self, kwargs)
        self.parametric_function = \
            lambda t: np.array([t, function(t), 0])
        ParametricFunction.__init__(
            self,
            self.parametric_function,
            t_min=self.x_min,
            t_max=self.x_max,
            **kwargs
        )
        self.function = function

    def get_function(self):
        return self.function

    def get_point_from_function(self, x):
        return self.parametric_function(x)
