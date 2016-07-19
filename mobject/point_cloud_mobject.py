from .mobject import Mobject
from helpers import *

class PMobject(Mobject):
    def init_points(self):
        self.rgbs = np.zeros((0, 3))
        self.points = np.zeros((0, 3))
        return self

    def get_array_attrs(self):
        return Mobject.get_array_attrs(self) + ["rgbs"]

    def add_points(self, points, rgbs = None, color = None):
        """
        points must be a Nx3 numpy array, as must rgbs if it is not None
        """
        if not isinstance(points, np.ndarray):
            points = np.array(points)
        num_new_points = points.shape[0]
        self.points = np.append(self.points, points, axis = 0)
        if rgbs is None:
            color = Color(color) if color else self.color
            rgbs = np.array([color.get_rgb()] * num_new_points)
        elif rgbs.shape != points.shape:
            raise Exception("points and rgbs must have same shape")
        self.rgbs = np.append(self.rgbs, rgbs, axis = 0)
        return self

    def highlight(self, color = YELLOW_C, condition = None):
        rgb = Color(color).get_rgb()
        for mob in self.family_members_with_points():
            if condition:
                to_change = np.apply_along_axis(condition, 1, mob.points)
                mob.rgbs[to_change, :] = rgb
            else:
                mob.rgbs[:,:] = rgb
        return self

    def gradient_highlight(self, start_color, end_color):
        start_rgb, end_rgb = [
            np.array(Color(color).get_rgb())
            for color in start_color, end_color
        ]
        for mob in self.family_members_with_points():
            num_points = mob.get_num_points()
            mob.rgbs = np.array([
                interpolate(start_rgb, end_rgb, alpha)
                for alpha in np.arange(num_points)/float(num_points)
            ])
        return self


    def match_colors(self, mobject):
        Mobject.align_data(self, mobject)
        self.rgbs = np.array(mobject.rgbs)
        return self

    def filter_out(self, condition):
        for mob in self.family_members_with_points():
            to_eliminate = ~np.apply_along_axis(condition, 1, mob.points)
            mob.points = mob.points[to_eliminate]
            mob.rgbs = mob.rgbs[to_eliminate]
        return self

    def thin_out(self, factor = 5):
        """
        Removes all but every nth point for n = factor
        """
        for mob in self.family_members_with_points():
            num_points = self.get_num_points()
            mob.apply_over_attr_arrays(
                lambda arr : arr[
                    np.arange(0, num_points, factor)
                ]
            )
        return self

    def sort_points(self, function = lambda p : p[0]):
        """
        function is any map from R^3 to R
        """
        for mob in self.family_members_with_points():
            indices = np.argsort(
                np.apply_along_axis(function, 1, mob.points)
            )
            mob.apply_over_attr_arrays(lambda arr : arr[indices])
        return self

    def fade_to(self, color, alpha):
        self.rgbs = interpolate(self.rgbs, np.array(Color(color).rgb), alpha)
        for mob in self.submobjects:
            mob.fade_to(color, alpha)
        return self

    def get_all_rgbs(self):
        return self.get_merged_array("rgbs")

    def ingest_submobjects(self):
        attrs = self.get_array_attrs()
        arrays = map(self.get_merged_array, attrs)
        for attr, array in zip(attrs, arrays):
            setattr(self, attr, array)
        self.submobjects = []
        return self

    def get_color(self):
        return Color(rgb = self.rgbs[0, :])

    def point_from_proportion(self, alpha):
        index = alpha*(self.get_num_points()-1)
        return self.points[index]

    # Alignment
    def align_points_with_larger(self, larger_mobject):
        assert(isinstance(larger_mobject, PMobject))
        self.apply_over_attr_arrays(
            lambda a : streth_array_to_length(
                a, larger_mobject.get_num_points()
            )
        )

    def get_point_mobject(self, center = None):
        if center is None:
            center = self.get_center()
        return Point(center)

    def interpolate_color(self, mobject1, mobject2, alpha):
        self.rgbs = interpolate(
            mobject1.rgbs, mobject2.rgbs, alpha
        )

    def pointwise_become_partial(self, mobject, a, b):
        lower_index, upper_index = [
            int(x * mobject.get_num_points())
            for x in a, b
        ]
        for attr in self.get_array_attrs():
            full_array = getattr(mobject, attr)
            partial_array = full_array[lower_index:upper_index]
            setattr(self, attr, partial_array) 


#TODO, Make the two implementations bellow non-redundant
class Mobject1D(PMobject):
    CONFIG = {
        "density" : DEFAULT_POINT_DENSITY_1D,
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        self.epsilon = 1.0 / self.density        
        Mobject.__init__(self, **kwargs)


    def add_line(self, start, end, color = None):
        start, end = map(np.array, [start, end])
        length = np.linalg.norm(end - start)
        if length == 0:
            points = [start]
        else:
            epsilon = self.epsilon/length
            points = [
                interpolate(start, end, t)
                for t in np.arange(0, 1, epsilon)
            ]
        self.add_points(points, color = color)

class Mobject2D(PMobject):
    CONFIG = {
        "density" : DEFAULT_POINT_DENSITY_2D,
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        self.epsilon = 1.0 / self.density  
        Mobject.__init__(self, **kwargs)



class Point(PMobject):
    CONFIG = {
        "color" : BLACK,
    }
    def __init__(self, location = ORIGIN, **kwargs):
        PMobject.__init__(self, **kwargs)
        self.add_points([location])

