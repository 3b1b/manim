from manimlib.imports import *

class NumberLineScene(Scene):
    def construct(self, **number_line_config):
        self.number_line = NumberLine(**number_line_config)
        self.displayed_numbers = self.number_line.default_numbers_to_display()
        self.number_mobs = self.number_line.get_number_mobjects(*self.displayed_numbers)
        self.add(self.number_line, *self.number_mobs)

    def zoom_in_on(self, number, zoom_factor, run_time = 2.0):
        unit_length_to_spatial_width = self.number_line.unit_length_to_spatial_width*zoom_factor
        radius = FRAME_X_RADIUS/unit_length_to_spatial_width
        tick_frequency = 10**(np.floor(np.log10(radius)))
        left_tick = tick_frequency*(np.ceil((number-radius)/tick_frequency))
        new_number_line = NumberLine(
            numerical_radius = radius,
            unit_length_to_spatial_width = unit_length_to_spatial_width,
            tick_frequency = tick_frequency,
            leftmost_tick = left_tick,
            number_at_center = number
        )
        new_displayed_numbers = new_number_line.default_numbers_to_display()
        new_number_mobs = new_number_line.get_number_mobjects(*new_displayed_numbers)

        transforms = []
        additional_mobjects = []
        squished_new_line = new_number_line.copy()
        squished_new_line.scale(1.0/zoom_factor)
        squished_new_line.shift(self.number_line.number_to_point(number))
        squished_new_line.points[:,1] = self.number_line.number_to_point(0)[1]
        transforms.append(Transform(squished_new_line, new_number_line))
        for mob, num in zip(new_number_mobs, new_displayed_numbers):
            point = Point(self.number_line.number_to_point(num))
            point.shift(new_number_line.get_vertical_number_offset())
            transforms.append(Transform(point, mob))
        for mob in self.mobjects:
            if mob == self.number_line:
                new_mob = mob.copy()
                new_mob.shift(-self.number_line.number_to_point(number))
                new_mob.stretch(zoom_factor, 0)
                transforms.append(Transform(mob, new_mob))
                continue
            mob_center = mob.get_center()
            number_under_center = self.number_line.point_to_number(mob_center)
            new_point = new_number_line.number_to_point(number_under_center)
            new_point += mob_center[1]*UP
            if mob in self.number_mobs:
                transforms.append(Transform(mob, Point(new_point)))
            else:
                transforms.append(ApplyMethod(mob.shift, new_point - mob_center))
                additional_mobjects.append(mob)
        line_to_hide_pixelation = Line(
            self.number_line.get_left(),
            self.number_line.get_right(),
            color = self.number_line.get_color()
        )
        self.add(line_to_hide_pixelation)
        self.play(*transforms, run_time = run_time)
        self.clear()
        self.number_line = new_number_line
        self.displayed_numbers = new_displayed_numbers
        self.number_mobs = new_number_mobs
        self.add(self.number_line, *self.number_mobs)
        self.add(*additional_mobjects)

    def show_multiplication(self, num, **kwargs):
        if "path_func" not in kwargs:
            if num > 0:
                kwargs["path_func"] = straight_path
            else:
                kwargs["path_func"] = counterclockwise_path()
        self.play(*[
            ApplyMethod(self.number_line.stretch, num, 0, **kwargs)
        ]+[
            ApplyMethod(mob.shift, (num-1)*mob.get_center()[0]*RIGHT, **kwargs)
            for mob in self.number_mobs
        ])
