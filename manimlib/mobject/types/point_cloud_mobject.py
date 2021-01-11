from manimlib.constants import *
from manimlib.mobject.mobject import Mobject
from manimlib.utils.bezier import interpolate
from manimlib.utils.color import color_gradient
from manimlib.utils.color import color_to_rgba
from manimlib.utils.color import rgba_to_color
from manimlib.utils.iterables import resize_preserving_order


class PMobject(Mobject):
    def reset_points(self):
        self.rgbas = np.zeros((0, 4))
        self.points = np.zeros((0, 3))
        return self

    def get_array_attrs(self):
        return Mobject.get_array_attrs(self) + ["rgbas"]

    def set_points(self, points):
        self.points = points
        self.rgbas = resize_preserving_order(self.rgbas, len(points))
        return self

    def add_points(self, points, rgbas=None, color=None, alpha=1):
        """
        points must be a Nx3 numpy array, as must rgbas if it is not None
        """
        if not isinstance(points, np.ndarray):
            points = np.array(points)
        num_new_points = len(points)
        self.points = np.vstack([self.points, points])
        if rgbas is None:
            color = Color(color) if color else self.color
            rgbas = np.repeat(
                [color_to_rgba(color, alpha)],
                num_new_points,
                axis=0
            )
        elif len(rgbas) != len(points):
            raise Exception("points and rgbas must have same shape")
        self.rgbas = np.vstack([self.rgbas, rgbas])
        return self

    def set_color(self, color, family=True):
        rgba = color_to_rgba(color)
        mobs = self.family_members_with_points() if family else [self]
        for mob in mobs:
            mob.rgbas[:, :] = rgba
        return self

    def set_opacity(self, opacity, family=True):
        mobs = self.family_members_with_points() if family else [self]
        for mob in mobs:
            mob.rgbas[:, 3] = opacity
        return self

    def get_color(self):
        return rgba_to_color(self.rgbas[0, :])

    def get_all_rgbas(self):
        return self.get_merged_array("rgbas")

    # def set_color_by_gradient(self, start_color, end_color):
    def set_color_by_gradient(self, *colors):
        self.rgbas = np.array(list(map(
            color_to_rgba,
            color_gradient(colors, len(self.points))
        )))
        return self

        start_rgba, end_rgba = list(map(color_to_rgba, [start_color, end_color]))
        for mob in self.family_members_with_points():
            num_points = mob.get_num_points()
            mob.rgbas = np.array([
                interpolate(start_rgba, end_rgba, alpha)
                for alpha in np.arange(num_points) / float(num_points)
            ])
        return self

    def set_colors_by_radial_gradient(self, center=None, radius=1, inner_color=WHITE, outer_color=BLACK):
        start_rgba, end_rgba = list(map(color_to_rgba, [start_color, end_color]))
        if center is None:
            center = self.get_center()
        for mob in self.family_members_with_points():
            num_points = mob.get_num_points()
            t = min(1, np.abs(mob.get_center() - center) / radius)

            mob.rgbas = np.array(
                [interpolate(start_rgba, end_rgba, t)] * num_points
            )
        return self

    def match_colors(self, pmobject):
        self.rgbas[:] = resize_preserving_order(pmobject.rgbas, len(self.points))
        return self

    def filter_out(self, condition):
        for mob in self.family_members_with_points():
            to_eliminate = ~np.apply_along_axis(condition, 1, mob.points)
            mob.points = mob.points[to_eliminate]
            mob.rgbas = mob.rgbas[to_eliminate]
        return self

    def thin_out(self, factor=5):
        """
        Removes all but every nth point for n = factor
        """
        for mob in self.family_members_with_points():
            num_points = self.get_num_points()
            mob.apply_over_attr_arrays(
                lambda arr: arr[
                    np.arange(0, num_points, factor)
                ]
            )
        return self

    def sort_points(self, function=lambda p: p[0]):
        """
        function is any map from R^3 to R
        """
        for mob in self.family_members_with_points():
            indices = np.argsort(
                np.apply_along_axis(function, 1, mob.points)
            )
            mob.apply_over_attr_arrays(lambda arr: arr[indices])
        return self

    def ingest_submobjects(self):
        attrs = self.get_array_attrs()
        arrays = list(map(self.get_merged_array, attrs))
        for attr, array in zip(attrs, arrays):
            setattr(self, attr, array)
        self.set_submobjects([])
        return self

    def point_from_proportion(self, alpha):
        index = alpha * (self.get_num_points() - 1)
        return self.points[index]

    # Alignment
    def interpolate_color(self, mobject1, mobject2, alpha):
        self.rgbas = interpolate(mobject1.rgbas, mobject2.rgbas, alpha)
        return self

    def pointwise_become_partial(self, pmobject, a, b):
        lower_index = int(a * pmobject.get_num_points())
        upper_index = int(b * pmobject.get_num_points())
        for attr in self.get_array_attrs():
            full_array = getattr(pmobject, attr)
            partial_array = full_array[lower_index:upper_index]
            setattr(self, attr, partial_array)


class PGroup(PMobject):
    def __init__(self, *pmobs, **kwargs):
        if not all([isinstance(m, PMobject) for m in pmobs]):
            raise Exception("All submobjects must be of type PMobject")
        super().__init__(**kwargs)
        self.add(*pmobs)


class Point(PMobject):
    CONFIG = {
        "color": BLACK,
    }

    def __init__(self, location=ORIGIN, **kwargs):
        PMobject.__init__(self, **kwargs)
        self.add_points([location])
