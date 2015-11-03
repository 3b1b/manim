from topics import *
from animation import *


def half_plane():
    plane = NumberPlane(
        x_radius = SPACE_WIDTH/2,
        x_unit_to_spatial_width  = 0.5,
        y_unit_to_spatial_height = 0.5,
        density = 2*DEFAULT_POINT_DENSITY_1D,
    )
    plane.add_coordinates(
        x_vals = range(-6, 7, 2),
        y_vals = range(-6, 7, 2)
    )
    return plane

class SingleVariableFunction(Scene):
    args_list = [
        (lambda x : x**2 - 3, "ShiftedSquare", True),
        (lambda x : x**2 - 3, "ShiftedSquare", False),
    ]

    @staticmethod
    def args_to_string(func, name, separate_lines):
        return name + ("SeparateLines" if separate_lines else "")

    def construct(self, func, name, separate_lines):
        base_line = NumberLine(color = "grey")
        moving_line = NumberLine(
            tick_frequency = 1, 
            density = 3*DEFAULT_POINT_DENSITY_1D
        )
        base_line.add_numbers()
        def point_function((x, y, z)):
            return (func(x), y, z)
        target = moving_line.copy().apply_function(point_function)

        transform_config = {
            "run_time" : 3,
            "interpolation_function" : path_along_arc(np.pi/4)
        }

        if separate_lines:
            numbers = moving_line.get_number_mobjects(*range(-7, 7))
            negative_numbers = []
            for number in numbers:
                number.highlight(GREEN_E)
                number.shift(-2*moving_line.get_vertical_number_offset())
                center = number.get_center()
                target_num = number.copy()
                target_num.shift(point_function(center) - center)
                target.add(target_num)
                if center[0] < -0.5:
                    negative_numbers.append(number)
            moving_line.add(*numbers)
            base_line.shift(DOWN)
            target.shift(DOWN)
            moving_line.shift(UP)

        self.add(base_line, moving_line)
        self.dither(3)
        self.play(Transform(moving_line, target, **transform_config))
        if separate_lines:
            self.play(*[
                ApplyMethod(mob.shift, 0.4*UP)
                for mob in negative_numbers
            ])
        self.dither(3)


class LineToPlaneFunction(Scene):
    args_list = [
        (lambda x : (np.cos(x), 0.5*x*np.sin(x)), "Swirl", {}),
        (lambda x : (np.cos(x), 0.5*x*np.sin(x)), "Swirl", {
            "0" : 0, 
            "\\frac{\\pi}{2}" : np.pi/2, 
            "\\pi" : np.pi
        })        
    ]

    @staticmethod
    def args_to_string(func, name, numbers_to_follow):
        return name + ("FollowingNumbers" if numbers_to_follow else "")

    def construct(self, func, name, numbers_to_follow):
        line = NumberLine(
            unit_length_to_spatial_width = 0.5,
            tick_frequency = 1,
            number_at_center = 6,
            numerical_radius = 6,
            numbers_with_elongated_ticks = [0, 12],
            density = 3*DEFAULT_POINT_DENSITY_1D
        )
        line.to_edge(LEFT)
        line_copy = line.copy()
        line.add_numbers(*range(0, 14, 2))
        divider = Line(SPACE_HEIGHT*UP, SPACE_HEIGHT*DOWN)
        plane = half_plane()
        plane.shift(0.5*SPACE_WIDTH*RIGHT)
        self.add(line, divider, plane)

        def point_function(point):
            x, y = func(line.point_to_number(point))
            return plane.num_pair_to_point((x, y))

        target = line_copy.copy().apply_function(point_function)
        target.highlight()
        anim_config = {"run_time" : 3}
        anims = [Transform(line_copy, target, **anim_config)]

        colors = iter([BLUE_B, GREEN_D, RED_D])
        for tex, number in numbers_to_follow.items():
            center = line.number_to_point(number)
            dot = Dot(center, color = colors.next())
            anims.append(ApplyMethod(
                dot.shift, 
                point_function(center) - center, 
                **anim_config 
            ))
            label = TexMobject(tex)
            label.shift(center + 2*UP)
            arrow = Arrow(label, dot)
            self.add(label)
            self.play(ShowCreation(arrow), ShowCreation(dot))
            self.dither()
            self.remove(arrow, label)


        self.dither(2)
        self.play(*anims)
        self.dither()

class PlaneToPlaneFunctionSeparatePlanes(Scene):
    args_list = [
        (lambda (x, y) : (x**2+y**2, x**2-y**2), "Quadratic")
    ]
    @staticmethod
    def args_to_string(func, name):
        return name

    def construct(self, func, name):
        shift_factor = 0.55
        in_plane  = half_plane().shift(shift_factor*SPACE_WIDTH*LEFT)
        out_plane = half_plane().shift(shift_factor*SPACE_WIDTH*RIGHT)
        divider = Line(SPACE_HEIGHT*UP, SPACE_HEIGHT*DOWN)
        self.add(in_plane, out_plane, divider)

        plane_copy = in_plane.copy()
        plane_copy.sub_mobjects = []

        def point_function(point):
            result = np.array(func((point*2 + 2*shift_factor*SPACE_WIDTH*RIGHT)[:2]))
            result = np.append(result/2, [0])
            return result + shift_factor*SPACE_WIDTH*RIGHT

        target = plane_copy.copy().apply_function(point_function)
        target.highlight(GREEN_B)

        anim_config = {"run_time" : 5}

        self.dither()
        self.play(Transform(plane_copy, target, **anim_config))
        self.dither()

class PlaneToPlaneFunction(Scene):
    args_list = [
        (lambda (x, y) : (x**2+y**2, x**2-y**2), "Quadratic")
    ]
    @staticmethod
    def args_to_string(func, name):
        return name

    def construct(self, func, name):
        plane = NumberPlane()
        background = NumberPlane(color = "grey")
        background.add_coordinates()
        anim_config = {"run_time" : 3}

        def point_function(point):
            return np.append(func(point[:2]), [0])

        self.add(background, plane)
        self.dither(2)
        self.play(ApplyPointwiseFunction(point_function, plane, **anim_config))
        self.dither(3)































