from __future__ import annotations

import math

import numpy as np

from manimlib.constants import BLUE, BLUE_D, BLUE_E, GREY_A, BLACK
from manimlib.constants import IN, ORIGIN, OUT, RIGHT
from manimlib.constants import PI, TAU
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.types.surface import SGroup
from manimlib.mobject.types.surface import Surface
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.geometry import Polygon
from manimlib.mobject.geometry import Square
from manimlib.utils.bezier import interpolate
from manimlib.utils.iterables import adjacent_pairs
from manimlib.utils.space_ops import compass_directions
from manimlib.utils.space_ops import get_norm
from manimlib.utils.space_ops import z_to_vector

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Tuple, TypeVar
    from manimlib.typing import ManimColor, Vect3

    T = TypeVar("T", bound=Mobject)


class SurfaceMesh(VGroup):
    def __init__(
        self,
        uv_surface: Surface,
        resolution: Tuple[int, int] = (21, 11),
        stroke_width: float = 1,
        stroke_color: ManimColor = GREY_A,
        normal_nudge: float = 1e-2,
        flat_stroke: bool = False,
        depth_test: bool = True,
        joint_type: str = 'no_joint',
        **kwargs
    ):
        self.uv_surface = uv_surface
        self.resolution = resolution
        self.normal_nudge = normal_nudge
        self.flat_stroke = flat_stroke

        super().__init__(
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            depth_test=depth_test,
            joint_type=joint_type,
            **kwargs
        )

    def init_points(self) -> None:
        uv_surface = self.uv_surface

        full_nu, full_nv = uv_surface.resolution
        part_nu, part_nv = self.resolution
        # 'indices' are treated as floats. Later, there will be
        # an interpolation between the floor and ceiling of these
        # indices
        u_indices = np.linspace(0, full_nu - 1, part_nu)
        v_indices = np.linspace(0, full_nv - 1, part_nv)

        points, du_points, dv_points = uv_surface.get_surface_points_and_nudged_points()
        normals = uv_surface.get_unit_normals()
        nudge = self.normal_nudge
        nudged_points = points + nudge * normals

        for ui in u_indices:
            path = VMobject()
            low_ui = full_nv * int(math.floor(ui))
            high_ui = full_nv * int(math.ceil(ui))
            path.set_points_smoothly(interpolate(
                nudged_points[low_ui:low_ui + full_nv],
                nudged_points[high_ui:high_ui + full_nv],
                ui % 1
            ))
            self.add(path)
        for vi in v_indices:
            path = VMobject()
            path.set_points_smoothly(interpolate(
                nudged_points[int(math.floor(vi))::full_nv],
                nudged_points[int(math.ceil(vi))::full_nv],
                vi % 1
            ))
            self.add(path)


# 3D shapes

class Sphere(Surface):
    def __init__(
        self,
        u_range: Tuple[float, float] = (0, TAU),
        v_range: Tuple[float, float] = (0, PI),
        resolution: Tuple[int, int] = (101, 51),
        radius: float = 1.0,
        **kwargs,
    ):
        self.radius = radius
        super().__init__(
            u_range=u_range,
            v_range=v_range,
            resolution=resolution,
            **kwargs
        )

    def uv_func(self, u: float, v: float) -> np.ndarray:
        return self.radius * np.array([
            math.cos(u) * math.sin(v),
            math.sin(u) * math.sin(v),
            -math.cos(v)
        ])


class Torus(Surface):
    def __init__(
        self,
        u_range: Tuple[float, float] = (0, TAU),
        v_range: Tuple[float, float] = (0, TAU),
        r1: float = 3.0,
        r2: float = 1.0,
        **kwargs,
    ):
        self.r1 = r1
        self.r2 = r2
        super().__init__(
            u_range=u_range,
            v_range=v_range,
            **kwargs,
        )

    def uv_func(self, u: float, v: float) -> np.ndarray:
        P = np.array([math.cos(u), math.sin(u), 0])
        return (self.r1 - self.r2 * math.cos(v)) * P - self.r2 * math.sin(v) * OUT


class Cylinder(Surface):
    def __init__(
        self,
        u_range: Tuple[float, float] = (0, TAU),
        v_range: Tuple[float, float] = (-1, 1),
        resolution: Tuple[int, int] = (101, 11),
        height: float = 2,
        radius: float = 1,
        axis: Vect3 = OUT,
        **kwargs,
    ):
        self.height = height
        self.radius = radius
        self.axis = axis
        super().__init__(
            u_range=u_range,
            v_range=v_range,
            resolution=resolution,
            **kwargs
        )


    def init_points(self):
        super().init_points()
        self.scale(self.radius)
        self.set_depth(self.height, stretch=True)
        self.apply_matrix(z_to_vector(self.axis))
        return self

    def uv_func(self, u: float, v: float) -> np.ndarray:
        return np.array([np.cos(u), np.sin(u), v])


class Line3D(Cylinder):
    def __init__(
        self,
        start: Vect3,
        end: Vect3,
        width: float = 0.05,
        resolution: Tuple[int, int] = (21, 25),
        **kwargs
    ):
        axis = end - start
        super().__init__(
            height=get_norm(axis),
            radius=width / 2,
            axis=axis,
            **kwargs
        )
        self.shift((start + end) / 2)


class Disk3D(Surface):
    def __init__(
        self,
        radius: float = 1,
        u_range: Tuple[float, float] = (0, 1),
        v_range: Tuple[float, float] = (0, TAU),
        resolution: Tuple[int, int] = (2, 100),
        **kwargs
    ):
        super().__init__(
            u_range=u_range,
            v_range=v_range,
            resolution=resolution,
            **kwargs,
        )
        self.scale(radius)

    def uv_func(self, u: float, v: float) -> np.ndarray:
        return np.array([
            u * math.cos(v),
            u * math.sin(v),
            0
        ])


class Square3D(Surface):
    def __init__(
        self,
        side_length: float = 2.0,
        u_range: Tuple[float, float] = (-1, 1),
        v_range: Tuple[float, float] = (-1, 1),
        resolution: Tuple[int, int] = (2, 2),
        **kwargs,
    ):
        super().__init__(
            u_range=u_range, 
            v_range=v_range, 
            resolution=resolution, 
            **kwargs
        )
        self.scale(side_length / 2)

    def uv_func(self, u: float, v: float) -> np.ndarray:
        return np.array([u, v, 0])


def square_to_cube_faces(square: T) -> list[T]:
    radius = square.get_height() / 2
    square.move_to(radius * OUT)
    result = [square.copy()]
    result.extend([
        square.copy().rotate(PI / 2, axis=vect, about_point=ORIGIN)
        for vect in compass_directions(4)
    ])
    result.append(square.copy().rotate(PI, RIGHT, about_point=ORIGIN))
    return result


class Cube(SGroup):
    def __init__(
        self,
        color: ManimColor = BLUE,
        opacity: float = 1,
        gloss: float = 0.5,
        square_resolution: Tuple[int, int] = (2, 2),
        side_length: float = 2,
        **kwargs,
    ):
        face = Square3D(
            resolution=square_resolution,
            side_length=side_length,
            color=color,
            opacity=opacity,
        )
        super().__init__(
            *square_to_cube_faces(face),
            gloss=gloss,
            **kwargs
        )


class Prism(Cube):
    def __init__(
        self,
        width: float = 3.0,
        height: float = 2.0,
        depth: float = 1.0,
        **kwargs
    ):
        super().__init__(**kwargs)
        for dim, value in enumerate([width, height, depth]):
            self.rescale_to_fit(value, dim, stretch=True)


class VGroup3D(VGroup):
    def __init__(
        self,
        *vmobjects: VMobject,
        depth_test: bool = True,
        gloss: float = 0.2,
        shadow: float = 0.2,
        reflectiveness: float = 0.2,
        joint_type: str = "no_joint",
        **kwargs
    ):
        super().__init__(*vmobjects, **kwargs)
        self.set_gloss(gloss)
        self.set_shadow(shadow)
        self.set_reflectiveness(reflectiveness)
        self.set_joint_type(joint_type)
        if depth_test:
            self.apply_depth_test()


class VCube(VGroup3D):
    def __init__(
        self,
        side_length: float = 2.0,
        fill_color: ManimColor = BLUE_D,
        fill_opacity: float = 1,
        stroke_width: float = 0,
        **kwargs
    ):
        style = dict(
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            stroke_width=stroke_width,
            **kwargs
        )
        face = Square(side_length=side_length, **style)
        super().__init__(*square_to_cube_faces(face), **style)


class VPrism(VCube):
    def __init__(
        self,
        width: float = 3.0,
        height: float = 2.0,
        depth: float = 1.0,
        **kwargs
    ):
        super().__init__(**kwargs)
        for dim, value in enumerate([width, height, depth]):
            self.rescale_to_fit(value, dim, stretch=True)


class Dodecahedron(VGroup3D):
    def __init__(
        self,
        fill_color: ManimColor = BLUE_E,
        fill_opacity: float = 1,
        stroke_color: ManimColor = BLUE_E,
        stroke_width: float = 1,
        reflectiveness: float = 0.2,
        **kwargs,
    ):
        style = dict(
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            reflectiveness=reflectiveness,
            **kwargs
        )

        # Start by creating two of the pentagons, meeting
        # back to back on the positive x-axis
        phi = (1 + math.sqrt(5)) / 2
        x, y, z = np.identity(3)
        pentagon1 = Polygon(
            np.array([phi, 1 / phi, 0]),
            np.array([1, 1, 1]),
            np.array([1 / phi, 0, phi]),
            np.array([1, -1, 1]),
            np.array([phi, -1 / phi, 0]),
            **style
        )
        pentagon2 = pentagon1.copy().stretch(-1, 2, about_point=ORIGIN)
        pentagon2.reverse_points()
        x_pair = VGroup(pentagon1, pentagon2)
        z_pair = x_pair.copy().apply_matrix(np.array([z, -x, -y]).T)
        y_pair = x_pair.copy().apply_matrix(np.array([y, z, x]).T)

        pentagons = [*x_pair, *y_pair, *z_pair]
        for pentagon in list(pentagons):
            pc = pentagon.copy()
            pc.apply_function(lambda p: -p)
            pc.reverse_points()
            pentagons.append(pc)

        super().__init__(*pentagons, **style)

        # # Rotate those two pentagons by all the axis permuations to fill
        # # out the dodecahedron
        # Id = np.identity(3)
        # for i in range(3):
        #     perm = [j % 3 for j in range(i, i + 3)]
        #     for b in [1, -1]:
        #         matrix = b * np.array([Id[0][perm], Id[1][perm], Id[2][perm]])
        #         self.add(pentagon1.copy().apply_matrix(matrix, about_point=ORIGIN))
        #         self.add(pentagon2.copy().apply_matrix(matrix, about_point=ORIGIN))


class Prismify(VGroup3D):
    def __init__(self, vmobject, depth=1.0, direction=IN, **kwargs):
        # At the moment, this assume stright edges
        vect = depth * direction
        pieces = [vmobject.copy()]
        points = vmobject.get_anchors()
        for p1, p2 in adjacent_pairs(points):
            wall = VMobject()
            wall.match_style(vmobject)
            wall.set_points_as_corners([p1, p2, p2 + vect, p1 + vect])
            pieces.append(wall)
        top = vmobject.copy()
        top.shift(vect)
        top.reverse_points()
        pieces.append(top)
        super().__init__(*pieces, **kwargs)
