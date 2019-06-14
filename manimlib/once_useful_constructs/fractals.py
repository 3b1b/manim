from functools import reduce

from manimlib.constants import *
from manimlib.for_3b1b_videos.pi_creature import PiCreature
from manimlib.for_3b1b_videos.pi_creature import Randolph
from manimlib.for_3b1b_videos.pi_creature import get_all_pi_creature_modes
from manimlib.mobject.geometry import Circle
from manimlib.mobject.geometry import Polygon
from manimlib.mobject.geometry import RegularPolygon
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.bezier import interpolate
from manimlib.utils.color import color_gradient
from manimlib.utils.config_ops import digest_config
from manimlib.utils.space_ops import center_of_mass
from manimlib.utils.space_ops import compass_directions
from manimlib.utils.space_ops import rotate_vector
from manimlib.utils.space_ops import rotation_matrix


def rotate(points, angle=np.pi, axis=OUT):
    if axis is None:
        return points
    matrix = rotation_matrix(angle, axis)
    points = np.dot(points, np.transpose(matrix))
    return points


def fractalify(vmobject, order=3, *args, **kwargs):
    for x in range(order):
        fractalification_iteration(vmobject)
    return vmobject


def fractalification_iteration(vmobject, dimension=1.05, num_inserted_anchors_range=list(range(1, 4))):
    num_points = vmobject.get_num_points()
    if num_points > 0:
        # original_anchors = vmobject.get_anchors()
        original_anchors = [
            vmobject.point_from_proportion(x)
            for x in np.linspace(0, 1 - 1. / num_points, num_points)
        ]
        new_anchors = []
        for p1, p2, in zip(original_anchors, original_anchors[1:]):
            num_inserts = random.choice(num_inserted_anchors_range)
            inserted_points = [
                interpolate(p1, p2, alpha)
                for alpha in np.linspace(0, 1, num_inserts + 2)[1:-1]
            ]
            mass_scaling_factor = 1. / (num_inserts + 1)
            length_scaling_factor = mass_scaling_factor**(1. / dimension)
            target_length = get_norm(p1 - p2) * length_scaling_factor
            curr_length = get_norm(p1 - p2) * mass_scaling_factor
            # offset^2 + curr_length^2 = target_length^2
            offset_len = np.sqrt(target_length**2 - curr_length**2)
            unit_vect = (p1 - p2) / get_norm(p1 - p2)
            offset_unit_vect = rotate_vector(unit_vect, np.pi / 2)
            inserted_points = [
                point + u * offset_len * offset_unit_vect
                for u, point in zip(it.cycle([-1, 1]), inserted_points)
            ]
            new_anchors += [p1] + inserted_points
        new_anchors.append(original_anchors[-1])
        vmobject.set_points_as_corners(new_anchors)
    vmobject.submobjects = [
        fractalification_iteration(
            submob, dimension, num_inserted_anchors_range)
        for submob in vmobject.submobjects
    ]
    return vmobject


class SelfSimilarFractal(VMobject):
    CONFIG = {
        "order": 5,
        "num_subparts": 3,
        "height": 4,
        "colors": [RED, WHITE],
        "stroke_width": 1,
        "fill_opacity": 1,
    }

    def init_colors(self):
        VMobject.init_colors(self)
        self.set_color_by_gradient(*self.colors)

    def generate_points(self):
        order_n_self = self.get_order_n_self(self.order)
        if self.order == 0:
            self.submobjects = [order_n_self]
        else:
            self.submobjects = order_n_self.submobjects
        return self

    def get_order_n_self(self, order):
        if order == 0:
            result = self.get_seed_shape()
        else:
            lower_order = self.get_order_n_self(order - 1)
            subparts = [
                lower_order.copy()
                for x in range(self.num_subparts)
            ]
            self.arrange_subparts(*subparts)
            result = VGroup(*subparts)

        result.set_height(self.height)
        result.center()
        return result

    def get_seed_shape(self):
        raise Exception("Not implemented")

    def arrange_subparts(self, *subparts):
        raise Exception("Not implemented")


class Sierpinski(SelfSimilarFractal):
    def get_seed_shape(self):
        return Polygon(
            RIGHT, np.sqrt(3) * UP, LEFT,
        )

    def arrange_subparts(self, *subparts):
        tri1, tri2, tri3 = subparts
        tri1.move_to(tri2.get_corner(DOWN + LEFT), UP)
        tri3.move_to(tri2.get_corner(DOWN + RIGHT), UP)


class DiamondFractal(SelfSimilarFractal):
    CONFIG = {
        "num_subparts": 4,
        "height": 4,
        "colors": [GREEN_E, YELLOW],
    }

    def get_seed_shape(self):
        return RegularPolygon(n=4)

    def arrange_subparts(self, *subparts):
        # VGroup(*subparts).rotate(np.pi/4)
        for part, vect in zip(subparts, compass_directions(start_vect=UP + RIGHT)):
            part.next_to(ORIGIN, vect, buff=0)
        VGroup(*subparts).rotate(np.pi / 4, about_point=ORIGIN)


class PentagonalFractal(SelfSimilarFractal):
    CONFIG = {
        "num_subparts": 5,
        "colors": [MAROON_B, YELLOW, RED],
        "height": 6,
    }

    def get_seed_shape(self):
        return RegularPolygon(n=5, start_angle=np.pi / 2)

    def arrange_subparts(self, *subparts):
        for x, part in enumerate(subparts):
            part.shift(0.95 * part.get_height() * UP)
            part.rotate(2 * np.pi * x / 5, about_point=ORIGIN)


class PentagonalPiCreatureFractal(PentagonalFractal):
    def init_colors(self):
        SelfSimilarFractal.init_colors(self)
        internal_pis = [
            pi
            for pi in self.get_family()
            if isinstance(pi, PiCreature)
        ]
        colors = color_gradient(self.colors, len(internal_pis))
        for pi, color in zip(internal_pis, colors):
            pi.init_colors()
            pi.body.set_stroke(color, width=0.5)
            pi.set_color(color)

    def get_seed_shape(self):
        return Randolph(mode="shruggie")

    def arrange_subparts(self, *subparts):
        for part in subparts:
            part.rotate(2 * np.pi / 5, about_point=ORIGIN)
        PentagonalFractal.arrange_subparts(self, *subparts)


class PiCreatureFractal(VMobject):
    CONFIG = {
        "order": 7,
        "scale_val": 2.5,
        "start_mode": "hooray",
        "height": 6,
        "colors": [
            BLUE_D, BLUE_B, MAROON_B, MAROON_D, GREY,
            YELLOW, RED, GREY_BROWN, RED, RED_E,
        ],
        "random_seed": 0,
        "stroke_width": 0,
    }

    def init_colors(self):
        VMobject.init_colors(self)
        internal_pis = [
            pi
            for pi in self.get_family()
            if isinstance(pi, PiCreature)
        ]
        random.seed(self.random_seed)
        for pi in reversed(internal_pis):
            color = random.choice(self.colors)
            pi.set_color(color)
            pi.set_stroke(color, width=0)

    def generate_points(self):
        random.seed(self.random_seed)
        modes = get_all_pi_creature_modes()
        seed = PiCreature(mode=self.start_mode)
        seed.set_height(self.height)
        seed.to_edge(DOWN)
        creatures = [seed]
        self.add(VGroup(seed))
        for x in range(self.order):
            new_creatures = []
            for creature in creatures:
                for eye, vect in zip(creature.eyes, [LEFT, RIGHT]):
                    new_creature = PiCreature(
                        mode=random.choice(modes)
                    )
                    new_creature.set_height(
                        self.scale_val * eye.get_height()
                    )
                    new_creature.next_to(
                        eye, vect,
                        buff=0,
                        aligned_edge=DOWN
                    )
                    new_creatures.append(new_creature)
                creature.look_at(random.choice(new_creatures))
            self.add_to_back(VGroup(*new_creatures))
            creatures = new_creatures

    # def init_colors(self):
    #     VMobject.init_colors(self)
    #     self.set_color_by_gradient(*self.colors)


class WonkyHexagonFractal(SelfSimilarFractal):
    CONFIG = {
        "num_subparts": 7
    }

    def get_seed_shape(self):
        return RegularPolygon(n=6)

    def arrange_subparts(self, *subparts):
        for i, piece in enumerate(subparts):
            piece.rotate(i * np.pi / 12, about_point=ORIGIN)
        p1, p2, p3, p4, p5, p6, p7 = subparts
        center_row = VGroup(p1, p4, p7)
        center_row.arrange(RIGHT, buff=0)
        for p in p2, p3, p5, p6:
            p.set_width(p1.get_width())
        p2.move_to(p1.get_top(), DOWN + LEFT)
        p3.move_to(p1.get_bottom(), UP + LEFT)
        p5.move_to(p4.get_top(), DOWN + LEFT)
        p6.move_to(p4.get_bottom(), UP + LEFT)


class CircularFractal(SelfSimilarFractal):
    CONFIG = {
        "num_subparts": 3,
        "colors": [GREEN, BLUE, GREY]
    }

    def get_seed_shape(self):
        return Circle()

    def arrange_subparts(self, *subparts):
        if not hasattr(self, "been_here"):
            self.num_subparts = 3 + self.order
            self.been_here = True
        for i, part in enumerate(subparts):
            theta = np.pi / self.num_subparts
            part.next_to(
                ORIGIN, UP,
                buff=self.height / (2 * np.tan(theta))
            )
            part.rotate(i * 2 * np.pi / self.num_subparts, about_point=ORIGIN)
        self.num_subparts -= 1

######## Space filling curves ############


class JaggedCurvePiece(VMobject):
    def insert_n_curves(self, n):
        if self.get_num_curves() == 0:
            self.set_points(np.zeros((1, 3)))
        anchors = self.get_anchors()
        indices = np.linspace(
            0, len(anchors) - 1, n + len(anchors)
        ).astype('int')
        self.set_points_as_corners(anchors[indices])


class FractalCurve(VMobject):
    CONFIG = {
        "radius": 3,
        "order": 5,
        "colors": [RED, GREEN],
        "num_submobjects": 20,
        "monochromatic": False,
        "order_to_stroke_width_map": {
            3: 3,
            4: 2,
            5: 1,
        },
    }

    def generate_points(self):
        points = self.get_anchor_points()
        self.set_points_as_corners(points)
        if not self.monochromatic:
            alphas = np.linspace(0, 1, self.num_submobjects)
            for alpha_pair in zip(alphas, alphas[1:]):
                submobject = JaggedCurvePiece()
                submobject.pointwise_become_partial(
                    self, *alpha_pair
                )
                self.add(submobject)
            self.points = np.zeros((0, 3))

    def init_colors(self):
        VMobject.init_colors(self)
        self.set_color_by_gradient(*self.colors)
        for order in sorted(self.order_to_stroke_width_map.keys()):
            if self.order >= order:
                self.set_stroke(width=self.order_to_stroke_width_map[order])

    def get_anchor_points(self):
        raise Exception("Not implemented")


class LindenmayerCurve(FractalCurve):
    CONFIG = {
        "axiom": "A",
        "rule": {},
        "scale_factor": 2,
        "radius": 3,
        "start_step": RIGHT,
        "angle": np.pi / 2,
    }

    def expand_command_string(self, command):
        result = ""
        for letter in command:
            if letter in self.rule:
                result += self.rule[letter]
            else:
                result += letter
        return result

    def get_command_string(self):
        result = self.axiom
        for x in range(self.order):
            result = self.expand_command_string(result)
        return result

    def get_anchor_points(self):
        step = float(self.radius) * self.start_step
        step /= (self.scale_factor**self.order)
        curr = np.zeros(3)
        result = [curr]
        for letter in self.get_command_string():
            if letter == "+":
                step = rotate(step, self.angle)
            elif letter == "-":
                step = rotate(step, -self.angle)
            else:
                curr = curr + step
                result.append(curr)
        return np.array(result) - center_of_mass(result)


class SelfSimilarSpaceFillingCurve(FractalCurve):
    CONFIG = {
        "offsets": [],
        # keys must awkwardly be in string form...
        "offset_to_rotation_axis": {},
        "scale_factor": 2,
        "radius_scale_factor": 0.5,
    }

    def transform(self, points, offset):
        """
        How to transform the copy of points shifted by
        offset.  Generally meant to be extended in subclasses
        """
        copy = np.array(points)
        if str(offset) in self.offset_to_rotation_axis:
            copy = rotate(
                copy,
                axis=self.offset_to_rotation_axis[str(offset)]
            )
        copy /= self.scale_factor,
        copy += offset * self.radius * self.radius_scale_factor
        return copy

    def refine_into_subparts(self, points):
        transformed_copies = [
            self.transform(points, offset)
            for offset in self.offsets
        ]
        return reduce(
            lambda a, b: np.append(a, b, axis=0),
            transformed_copies
        )

    def get_anchor_points(self):
        points = np.zeros((1, 3))
        for count in range(self.order):
            points = self.refine_into_subparts(points)
        return points

    def generate_grid(self):
        raise Exception("Not implemented")


class HilbertCurve(SelfSimilarSpaceFillingCurve):
    CONFIG = {
        "offsets": [
            LEFT + DOWN,
            LEFT + UP,
            RIGHT + UP,
            RIGHT + DOWN,
        ],
        "offset_to_rotation_axis": {
            str(LEFT + DOWN): RIGHT + UP,
            str(RIGHT + DOWN): RIGHT + DOWN,
        },
    }


class HilbertCurve3D(SelfSimilarSpaceFillingCurve):
    CONFIG = {
        "offsets": [
            RIGHT + DOWN + IN,
            LEFT + DOWN + IN,
            LEFT + DOWN + OUT,
            RIGHT + DOWN + OUT,
            RIGHT + UP + OUT,
            LEFT + UP + OUT,
            LEFT + UP + IN,
            RIGHT + UP + IN,
        ],
        "offset_to_rotation_axis_and_angle": {
            str(RIGHT + DOWN + IN): (LEFT + UP + OUT, 2 * np.pi / 3),
            str(LEFT + DOWN + IN): (RIGHT + DOWN + IN, 2 * np.pi / 3),
            str(LEFT + DOWN + OUT): (RIGHT + DOWN + IN, 2 * np.pi / 3),
            str(RIGHT + DOWN + OUT): (UP, np.pi),
            str(RIGHT + UP + OUT): (UP, np.pi),
            str(LEFT + UP + OUT): (LEFT + DOWN + OUT, 2 * np.pi / 3),
            str(LEFT + UP + IN): (LEFT + DOWN + OUT, 2 * np.pi / 3),
            str(RIGHT + UP + IN): (RIGHT + UP + IN, 2 * np.pi / 3),
        },
    }
    # Rewrote transform method to include the rotation angle

    def transform(self, points, offset):
        copy = np.array(points)
        copy = rotate(
            copy,
            axis=self.offset_to_rotation_axis_and_angle[str(offset)][0],
            angle=self.offset_to_rotation_axis_and_angle[str(offset)][1],
        )
        copy /= self.scale_factor,
        copy += offset * self.radius * self.radius_scale_factor
        return copy


class PeanoCurve(SelfSimilarSpaceFillingCurve):
    CONFIG = {
        "colors": [PURPLE, TEAL],
        "offsets": [
            LEFT + DOWN,
            LEFT,
            LEFT + UP,
            UP,
            ORIGIN,
            DOWN,
            RIGHT + DOWN,
            RIGHT,
            RIGHT + UP,
        ],
        "offset_to_rotation_axis": {
            str(LEFT): UP,
            str(UP): RIGHT,
            str(ORIGIN): LEFT + UP,
            str(DOWN): RIGHT,
            str(RIGHT): UP,
        },
        "scale_factor": 3,
        "radius_scale_factor": 2.0 / 3,
    }


class TriangleFillingCurve(SelfSimilarSpaceFillingCurve):
    CONFIG = {
        "colors": [MAROON, YELLOW],
        "offsets": [
            LEFT / 4. + DOWN / 6.,
            ORIGIN,
            RIGHT / 4. + DOWN / 6.,
            UP / 3.,
        ],
        "offset_to_rotation_axis": {
            str(ORIGIN): RIGHT,
            str(UP / 3.): UP,
        },
        "scale_factor": 2,
        "radius_scale_factor": 1.5,
    }

# class HexagonFillingCurve(SelfSimilarSpaceFillingCurve):
#     CONFIG = {
#         "start_color" : WHITE,
#         "end_color"   : BLUE_D,
#         "axis_offset_pairs" : [
#             (None,                1.5*DOWN + 0.5*np.sqrt(3)*LEFT),
#             (UP+np.sqrt(3)*RIGHT, 1.5*DOWN + 0.5*np.sqrt(3)*RIGHT),
#             (np.sqrt(3)*UP+RIGHT, ORIGIN),
#             ((UP, RIGHT),         np.sqrt(3)*LEFT),
#             (None,                1.5*UP + 0.5*np.sqrt(3)*LEFT),
#             (None,                1.5*UP + 0.5*np.sqrt(3)*RIGHT),
#             (RIGHT,               np.sqrt(3)*RIGHT),
#         ],
#         "scale_factor" : 3,
#         "radius_scale_factor" : 2/(3*np.sqrt(3)),
#     }

#     def refine_into_subparts(self, points):
#         return SelfSimilarSpaceFillingCurve.refine_into_subparts(
#             self,
#             rotate(points, np.pi/6, IN)
#         )


class UtahFillingCurve(SelfSimilarSpaceFillingCurve):
    CONFIG = {
        "colors": [WHITE, BLUE_D],
        "axis_offset_pairs": [

        ],
        "scale_factor": 3,
        "radius_scale_factor": 2 / (3 * np.sqrt(3)),
    }


class FlowSnake(LindenmayerCurve):
    CONFIG = {
        "colors": [YELLOW, GREEN],
        "axiom": "A",
        "rule": {
            "A": "A-B--B+A++AA+B-",
            "B": "+A-BB--B-A++A+B",
        },
        "radius": 6,  # TODO, this is innaccurate
        "scale_factor": np.sqrt(7),
        "start_step": RIGHT,
        "angle": -np.pi / 3,
    }

    def __init__(self, **kwargs):
        LindenmayerCurve.__init__(self, **kwargs)
        self.rotate(-self.order * np.pi / 9, about_point=ORIGIN)


class SierpinskiCurve(LindenmayerCurve):
    CONFIG = {
        "colors": [RED, WHITE],
        "axiom": "B",
        "rule": {
            "A": "+B-A-B+",
            "B": "-A+B+A-",
        },
        "radius": 6,  # TODO, this is innaccurate
        "scale_factor": 2,
        "start_step": RIGHT,
        "angle": -np.pi / 3,
    }


class KochSnowFlake(LindenmayerCurve):
    CONFIG = {
        "colors": [BLUE_D, WHITE, BLUE_D],
        "axiom": "A--A--A--",
        "rule": {
            "A": "A+A--A+A"
        },
        "radius": 4,
        "scale_factor": 3,
        "start_step": RIGHT,
        "angle": np.pi / 3,
        "order_to_stroke_width_map": {
            3: 3,
            5: 2,
            6: 1,
        },
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        self.scale_factor = 2 * (1 + np.cos(self.angle))
        LindenmayerCurve.__init__(self, **kwargs)


class KochCurve(KochSnowFlake):
    CONFIG = {
        "axiom": "A--"
    }


class QuadraticKoch(LindenmayerCurve):
    CONFIG = {
        "colors": [YELLOW, WHITE, MAROON_B],
        "axiom": "A",
        "rule": {
            "A": "A+A-A-AA+A+A-A"
        },
        "radius": 4,
        "scale_factor": 4,
        "start_step": RIGHT,
        "angle": np.pi / 2
    }


class QuadraticKochIsland(QuadraticKoch):
    CONFIG = {
        "axiom": "A+A+A+A"
    }


class StellarCurve(LindenmayerCurve):
    CONFIG = {
        "start_color": RED,
        "end_color": BLUE_E,
        "rule": {
            "A": "+B-A-B+A-B+",
            "B": "-A+B+A-B+A-",
        },
        "scale_factor": 3,
        "angle": 2 * np.pi / 5,
    }


class SnakeCurve(FractalCurve):
    CONFIG = {
        "start_color": BLUE,
        "end_color": YELLOW,
    }

    def get_anchor_points(self):
        result = []
        resolution = 2**self.order
        step = 2.0 * self.radius / resolution
        lower_left = ORIGIN + \
            LEFT * (self.radius - step / 2) + \
            DOWN * (self.radius - step / 2)

        for y in range(resolution):
            x_range = list(range(resolution))
            if y % 2 == 0:
                x_range.reverse()
            for x in x_range:
                result.append(
                    lower_left + x * step * RIGHT + y * step * UP
                )
        return result
