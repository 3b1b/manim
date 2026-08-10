from __future__ import annotations

import numpy as np

from manimlib.constants import BLACK
from manimlib.constants import DL, DR, UL, UR
from manimlib.mobject.mobject import Mobject
from manimlib.utils.color import color_to_rgba
from manimlib.renderer.uniform_block import COMMON_UNIFORMS
from manimlib.renderer.uniform_block import uniform_block_dtype

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable, Sequence
    from manimlib.mobject.coordinate_systems import CoordinateSystem
    from manimlib.typing import ManimColor, Self, Vect3


# How many colors the escape time of a point is spread across, see float_to_color
N_MANDELBROT_COLORS = 9
MANDELBROT_COLORS = [
    "#00065c", "#061e7e", "#0c37a0", "#205abc", "#4287d3",
    "#D9EDE4", "#F0F9E4", "#BA9F6A", "#573706",
]
# One per root, so the highest degree a NewtonFractal draws is the number of these
NEWTON_ROOT_COLORS = ["#440154", "#3b528b", "#21908c", "#5dc963", "#29abca"]
MAX_DEGREE = len(NEWTON_ROOT_COLORS)


def roots_to_coefficients(roots: Iterable[complex]) -> np.ndarray:
    """The polynomial with these roots and a leading coefficient of one, lowest power first"""
    return np.polynomial.polynomial.polyfromroots(np.array(list(roots), dtype=complex))


def coefficients_to_roots(coefs: Iterable[complex]) -> np.ndarray:
    """The roots of a polynomial given lowest power first"""
    coefs = np.trim_zeros(np.array(list(coefs), dtype=complex), "b")
    if len(coefs) < 2:
        return np.zeros(0, dtype=complex)
    return np.roots(coefs[::-1])


def as_complex_pairs(values: Iterable[complex], length: int) -> np.ndarray:
    """
    Complex numbers as the rows of an array a uniform block has room for, which holds four
    floats to a row whatever it is asked for, see uniform_block_dtype.
    """
    result = np.zeros((length, 4))
    numbers = [complex(value) for value in values][:length]
    result[:len(numbers), 0] = [number.real for number in numbers]
    result[:len(numbers), 1] = [number.imag for number in numbers]
    return result


def as_color_rows(colors: Sequence[ManimColor], length: int, opacity: float = 1.0):
    """Colors as the rows of such an array, the last of them repeated to fill it"""
    if len(colors) == 0:
        colors = [BLACK]
    filled = list(colors[:length]) + (length - len(colors)) * [colors[-1]]
    return np.array([color_to_rgba(color, opacity) for color in filled])


class PlaneFractal(Mobject):
    """
    A fractal drawn a pixel at a time by its shader, over a rectangle covering a plane.

    Only the four corners are held and the fragment shader does all the work, so a subclass is
    mostly the uniforms its shader reads. Where a pixel sits on the plane comes from
    scale_factor and offset rather than from where the rectangle ended up, so the picture
    follows the plane it was built for even once both have moved.
    """
    data_dtype: np.dtype = np.dtype([
        ('point', np.float32, (3,)),
    ])
    # The four corners are expanded into the two triangles covering them by the vertex
    # shader, six of the vertices drawn doing that and the rest collapsing
    verts_per_record: int = 6

    def __init__(self, plane: CoordinateSystem, **kwargs):
        super().__init__(**kwargs)
        self.plane = plane
        self.match_plane(plane)

    def init_data(self) -> None:
        super().init_data(length=4)
        self.data["point"] = [UL, DL, UR, DR]

    def match_plane(self, plane: CoordinateSystem) -> Self:
        """Covers the plane, and reads a pixel's place on screen as a place on it"""
        self.set_scale_factor(plane.get_x_unit_size())
        self.set_offset(plane.n2p(0))
        self.replace(plane, stretch=True)
        return self

    def set_scale_factor(self, scale_factor: float) -> Self:
        self.set_uniform(scale_factor=scale_factor)
        return self

    def set_offset(self, offset: Vect3) -> Self:
        self.set_uniform(offset=offset)
        return self

    def set_n_steps(self, n_steps: int) -> Self:
        self.set_uniform(n_steps=float(n_steps))
        return self

    def set_color(self, color, opacity=None, recurse=True) -> Self:
        """
        Nothing: a fractal's colors say what a point converged to or how long it took, and
        there is no color per point either, the data being nothing but the four corners.
        """
        return self


class MandelbrotFractal(PlaneFractal):
    """
    The Mandelbrot set: which starting points c leave the iteration z -> z^2 + c bounded,
    each colored by how long it took to escape, and left black if it never did.
    """
    shader_file: str = "mandelbrot_fractal.wgsl"
    uniform_dtype: np.dtype = uniform_block_dtype(
        *COMMON_UNIFORMS,
        ("scale_factor", 1),
        ("offset", 3),
        ("parameter", 2),
        ("opacity", 1),
        ("n_steps", 1),
        ("mandelbrot", 1),
        ("colors", 4, N_MANDELBROT_COLORS),
    )

    def __init__(
        self,
        plane: CoordinateSystem,
        colors: Sequence[ManimColor] = MANDELBROT_COLORS,
        n_steps: int = 300,
        parameter: complex = 0j,
        opacity: float = 1.0,
        mandelbrot: bool = True,
        **kwargs
    ):
        super().__init__(plane, **kwargs)
        self.set_colors(colors)
        self.set_n_steps(n_steps)
        self.set_parameter(parameter)
        self.set_opacity(opacity)
        self.set_uniform(mandelbrot=float(mandelbrot))

    def set_colors(self, colors: Sequence[ManimColor]) -> Self:
        self.set_uniform(colors=as_color_rows(colors, N_MANDELBROT_COLORS))
        return self

    def set_parameter(self, c: complex) -> Self:
        """The c held fixed while the pixel is the orbit's start, so only a Julia set uses it"""
        self.set_uniform(parameter=[complex(c).real, complex(c).imag])
        return self

    def set_opacity(self, opacity: float, recurse: bool = True) -> Self:
        self.set_uniform(opacity=opacity)
        return self


class JuliaFractal(MandelbrotFractal):
    """
    The Julia set of z -> z^2 + c for one fixed c: which starting points stay bounded, where
    the Mandelbrot set asks which values of c do.
    """

    def __init__(
        self,
        plane: CoordinateSystem,
        parameter: complex = 0j,
        n_steps: int = 100,
        **kwargs
    ):
        super().__init__(
            plane, parameter=parameter, n_steps=n_steps, mandelbrot=False, **kwargs
        )

    def set_c(self, c: complex) -> Self:
        return self.set_parameter(c)


class NewtonFractal(PlaneFractal):
    """
    Newton's method run from every pixel of a plane, each colored by which root it converged
    on. The boundaries between those basins are the fractal.

    Each root is colored by where it sits in the list of them, so which basin comes out which
    color depends on the order the roots are in. Say roots to choose that order; say coefs
    instead and the order is whatever solving for them produced.
    """
    shader_file: str = "newton_fractal.wgsl"
    uniform_dtype: np.dtype = uniform_block_dtype(
        *COMMON_UNIFORMS,
        ("scale_factor", 1),
        ("offset", 3),
        ("n_roots", 1),
        ("n_steps", 1),
        ("julia_highlight", 1),
        ("saturation_factor", 1),
        ("black_for_cycles", 1),
        ("is_parameter_space", 1),
        # One more coefficient than the degree, and one root and one color for each
        ("coefs", 4, MAX_DEGREE + 1),
        ("roots", 4, MAX_DEGREE),
        ("colors", 4, MAX_DEGREE),
    )

    def __init__(
        self,
        plane: CoordinateSystem,
        coefs: Sequence[complex] = (-1.0, 0.0, 0.0, 1.0),
        roots: Sequence[complex] | None = None,
        colors: Sequence[ManimColor] = NEWTON_ROOT_COLORS,
        n_steps: int = 30,
        julia_highlight: float = 0.0,
        saturation_factor: float = 0.0,
        opacity: float = 1.0,
        black_for_cycles: bool = False,
        is_parameter_space: bool = False,
        **kwargs
    ):
        super().__init__(plane, **kwargs)
        self.set_colors(colors)
        if roots is None:
            self.set_coefs(coefs)
        else:
            self.set_roots(roots)
        self.set_n_steps(n_steps)
        self.set_julia_highlight(julia_highlight)
        self.set_saturation_factor(saturation_factor)
        self.set_opacity(opacity)
        self.set_uniform(
            black_for_cycles=float(black_for_cycles),
            is_parameter_space=float(is_parameter_space),
        )

    def set_coefs(self, coefs: Sequence[complex], reset_roots: bool = True) -> Self:
        self.coefs = list(coefs)
        self.set_uniform(coefs=as_complex_pairs(self.coefs, MAX_DEGREE + 1))
        if reset_roots:
            self.set_roots(coefficients_to_roots(self.coefs), False)
        return self

    def set_roots(self, roots: Sequence[complex], reset_coefs: bool = True) -> Self:
        self.roots = list(roots)
        self.set_uniform(
            roots=as_complex_pairs(self.roots, MAX_DEGREE),
            n_roots=float(min(len(self.roots), MAX_DEGREE)),
        )
        if reset_coefs:
            self.set_coefs(roots_to_coefficients(self.roots), False)
        return self

    def set_colors(self, colors: Sequence[ManimColor]) -> Self:
        self.set_uniform(colors=as_color_rows(colors, MAX_DEGREE))
        return self

    def set_julia_highlight(self, radius: float) -> Self:
        """
        How far around each pixel to look for the basin boundary, which above zero shows
        only that boundary and leaves the middle of each basin transparent.
        """
        self.set_uniform(julia_highlight=radius)
        return self

    def set_saturation_factor(self, saturation_factor: float) -> Self:
        """How much to brighten what took longer to settle, showing a basin's own structure"""
        self.set_uniform(saturation_factor=float(saturation_factor))
        return self

    def set_opacities(self, *opacities: float) -> Self:
        colors = self.uniforms["colors"].copy()
        colors[:len(opacities), 3] = opacities
        self.set_uniform(colors=colors)
        return self

    def set_opacity(self, opacity: float, recurse: bool = True) -> Self:
        return self.set_opacities(*MAX_DEGREE * [opacity])


class MetaNewtonFractal(NewtonFractal):
    """
    Which cubics Newton's method finds a root of at all: two of the three roots are held
    fixed and the pixel is the third, so what is drawn is a map over polynomials rather than
    over starting points. The method always sets off from the center of the three.
    """

    def __init__(
        self,
        plane: CoordinateSystem,
        fixed_roots: Sequence[complex] = (-1, 1),
        n_steps: int = 300,
        black_for_cycles: bool = True,
        **kwargs
    ):
        super().__init__(
            plane,
            n_steps=n_steps,
            black_for_cycles=black_for_cycles,
            is_parameter_space=True,
            **kwargs
        )
        self.set_fixed_roots(fixed_roots)

    def set_fixed_roots(self, roots: Sequence[complex]) -> Self:
        super().set_roots(roots, reset_coefs=False)
        # The pixel stands for the third root, which no uniform holds
        self.set_uniform(n_roots=3.0)
        return self
