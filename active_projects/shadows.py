from big_ol_pile_of_manim_imports import *


# Helpers
def get_shadow(mobject, opacity=0.5):
    result = mobject.deepcopy()
    result.apply_function(lambda p: [p[0], p[1], 0])
    result.set_fill(BLACK, opacity=opacity)
    result.set_stroke(BLACK, 0)
    result.set_shade_in_3d(False)
    return result


def get_boundary_points(shadow, n_points=20):
    points = shadow.get_points_defining_boundary()
    return np.array([
        points[np.argmax(np.dot(points, vect.T))]
        for vect in compass_directions(n_points)
    ])


def get_area(planar_mobject):
    boundary = get_boundary_points(planar_mobject, 100)
    xs = boundary[:, 0]
    ys = boundary[:, 1]
    dxs = np.append(xs[-1], xs[:-1]) - xs
    dys = np.append(ys[-1], ys[:-1]) - ys
    return abs(sum([
        0.5 * (x * dy - y * dx)
        for x, dx, y, dy in zip(xs, dxs, ys, dys)
    ]))


def get_xy_plane_projection_point(p1, p2):
    """
    Draw a line from source to p1 to p2.  Where does it
    intersect the xy plane?
    """
    vect = p2 - p1
    return p1 - (p1[2] / vect[2]) * vect


# Scenes


class ShowShadows(ThreeDScene):
    CONFIG = {
        "object_center": [0, 0, 3],
        "area_label_center": [0, -1.5, 0],
        "surface_area": 6.0,
        "num_reorientations": 10,
        "camera_config": {
            "light_source_start_point": 10 * OUT,
            "frame_center": [0, 0, 0.5],
        }
    }

    def setup(self):
        self.add_plane()
        self.set_camera_orientation(
            phi=60 * DEGREES,
            theta=-90 * DEGREES,
        )
        # self.begin_ambient_camera_rotation(0.02)
        self.setup_orientation_trackers()
        self.setup_object_and_shadow()
        self.add_shadow_area_label()
        self.add_surface_area_label()

    def add_plane(self):
        plane = self.plane = Rectangle(
            width=FRAME_WIDTH,
            height=24.2,
            stroke_width=0,
            fill_color=WHITE,
            fill_opacity=0.5,
        )
        grid = NumberPlane(
            color=LIGHT_GREY,
            secondary_color=DARK_GREY,
            y_radius=int(plane.get_height() / 2),
            stroke_width=1,
            secondary_line_ratio=0,
        )
        plane.add(grid)
        plane.add(VectorizedPoint(10 * IN))
        plane.set_shade_in_3d(True, z_index_as_group=True)
        self.add(plane)

    def setup_orientation_trackers(self):
        # Euler angles
        self.alpha_tracker = ValueTracker(0)
        self.beta_tracker = ValueTracker(0)
        self.gamma_tracker = ValueTracker(0)

    def setup_object_and_shadow(self):
        self.obj3d = updating_mobject_from_func(self.get_reoriented_object)
        self.shadow = updating_mobject_from_func(lambda: get_shadow(self.obj3d))

    def add_shadow_area_label(self):
        text = TextMobject("Shadow area: ")
        decimal = DecimalNumber(0)
        label = VGroup(text, decimal)
        label.arrange_submobjects(RIGHT)
        label.scale(1.5)
        label.move_to(self.area_label_center)
        self.shadow_area_label = label
        continual_update = ContinualChangingDecimal(
            decimal, lambda a: get_area(self.shadow)
        )

        self.add(label)
        self.add(continual_update)

    def add_surface_area_label(self):
        text = TextMobject("Surface area: ")
        decimal = DecimalNumber(self.surface_area)
        label = VGroup(text, decimal)
        label.arrange_submobjects(RIGHT)
        label.scale(1.25)
        label.next_to(self.obj3d, RIGHT, MED_LARGE_BUFF)
        self.surface_area_label = label
        self.add_fixed_orientation_mobjects(label)

    def construct(self):
        obj3d = self.obj3d.copy()
        obj3d.clear_updaters()
        temp_shadow = updating_mobject_from_func(lambda: get_shadow(obj3d))
        self.add(temp_shadow)
        self.play(LaggedStart(DrawBorderThenFill, obj3d))
        self.remove(obj3d, temp_shadow)
        self.add(self.obj3d, self.shadow)
        for n in range(self.num_reorientations):
            self.randomly_reorient()
            self.wait()

    def randomly_reorient(self, run_time=3):
        a, b, c = TAU * np.random.random(3)
        self.play(
            self.alpha_tracker.set_value, a,
            self.beta_tracker.set_value, b,
            self.gamma_tracker.set_value, c,
            run_time=run_time
        )

    #
    def get_object(self):
        cube = Cube()
        cube.set_height(1)
        # cube.set_width(2, stretch=True)
        cube.set_stroke(WHITE, 0.5)
        return cube

    def get_reoriented_object(self):
        obj3d = self.get_object()
        angles = [
            self.alpha_tracker.get_value(),
            self.beta_tracker.get_value(),
            self.gamma_tracker.get_value(),
        ]
        vects = [OUT, RIGHT, OUT]

        center = self.object_center
        obj3d.move_to(center)
        for angle, vect in zip(angles, vects):
            obj3d.rotate(angle, vect, about_point=center)
        return obj3d


class ShowInfinitelyFarLightSource(ShowShadows):
    CONFIG = {
        "num_reorientations": 1,
        "camera_center": [0, 0, 1]
    }

    def construct(self):
        self.force_skipping()
        ShowShadows.construct(self)
        self.revert_to_original_skipping_status()

        self.add_light_source_based_shadow_updater()
        self.add_light()
        self.move_light_around()
        self.show_vertical_lines()

    def add_light(self):
        light = self.light = self.get_light()
        light_source = self.camera.light_source
        light.move_to(light_source)
        light_source.add_updater(lambda m: m.move_to(light))
        self.add(light_source)
        self.add_fixed_orientation_mobjects(light)

    def move_light_around(self):
        light = self.light
        self.play(
            light.move_to, 5 * OUT + DOWN,
            run_time=3
        )
        self.play(Rotating(
            light, angle=TAU, about_point=5 * OUT,
            rate_func=smooth, run_time=3
        ))
        self.play(
            light.move_to, 30 * OUT,
            run_time=3,
        )
        self.remove(light)

    def show_vertical_lines(self):
        lines = self.get_vertical_lines()
        self.play(LaggedStart(ShowCreation, lines))
        lines.add_updater(lambda m: m.become(self.get_vertical_lines()))
        self.wait()
        for x in range(5):
            self.randomly_reorient()

    def add_light_source_based_shadow_updater(self):
        shadow = self.shadow
        light_source = self.camera.light_source
        obj3d = self.obj3d
        center = obj3d.get_center()
        right = center + RIGHT
        up = center + UP

        def update(shadow):
            lsp = light_source.get_center()
            proj_center, proj_right, proj_up = [
                get_xy_plane_projection_point(lsp, point)
                for point in [center, right, up]
            ]
            matrix = np.array([
                proj_right - proj_center,
                proj_up - proj_center
            ]).T
            shadow.apply_matrix(matrix)
            shadow.move_to(proj_center)
            return shadow
        shadow.add_updater(update)

    def get_light(self):
        n_rings = 40
        radii = np.linspace(0, 2, n_rings)
        rings = VGroup(*[
            Annulus(inner_radius=r1, outer_radius=r2)
            for r1, r2 in zip(radii, radii[1:])
        ])
        opacities = np.linspace(1, 0, n_rings)**1.5
        for opacity, ring in zip(opacities, rings):
            ring.set_fill(YELLOW, opacity)
            ring.set_stroke(YELLOW, width=0.1, opacity=opacity)
        return rings

    def get_vertical_lines(self):
        shadow = self.shadow
        points = get_boundary_points(shadow, 10)
        half_points = [(p1 + p2) / 2 for p1, p2 in adjacent_pairs(points)]
        points = np.append(points, half_points, axis=0)
        light_source = self.light.get_center()
        lines = VGroup(*[
            DashedLine(light_source, point)
            for point in points
        ])
        lines.set_shade_in_3d(True)
        for line in lines:
            line.remove(*line[:int(0.8 * len(line))])
            line[-10:].set_shade_in_3d(False)
            line.set_stroke(YELLOW, 1)
        return lines


class CylinderShadows(ShowShadows):
    CONFIG = {
        "surface_area": 2 * PI + 2 * PI * 2
    }

    def get_object(self):
        height = 2
        cylinder = ParametricSurface(
            lambda u, v: np.array([
                np.cos(TAU * v),
                np.sin(TAU * v),
                height * (1 - u)
            ]),
            resolution=(6, 32)
        )
        # circle = Circle(radius=1)
        circle = ParametricSurface(
            lambda u, v: np.array([
                (v + 0.01) * np.cos(TAU * u),
                (v + 0.01) * np.sin(TAU * u),
                0,
            ]),
            resolution=(16, 8)
        )
        # circle.set_fill(GREEN, opacity=0.5)
        for surface in cylinder, circle:
            surface.set_fill_by_checkerboard(GREEN, GREEN_E, opacity=1.0)
            # surface.set_fill(GREEN, opacity=0.5)
        cylinder.add(circle)
        cylinder.add(circle.copy().flip().move_to(height * OUT))
        cylinder.set_shade_in_3d(True)
        cylinder.set_stroke(width=0)
        cylinder.scale(1.003)
        return cylinder


class PrismShadows(ShowShadows):
    CONFIG = {
        "surface_area": 3 * np.sqrt(3) / 2 + 3 * (np.sqrt(3) * 2),
        "object_center": [0, 0, 3],
        "area_label_center": [0, -2.25, 0],
    }

    def get_object(self):
        height = 2
        prism = VGroup()
        triangle = RegularPolygon(3)
        verts = triangle.get_anchors()[:3]
        rects = [
            Polygon(v1, v2, v2 + height * OUT, v1 + height * OUT)
            for v1, v2 in adjacent_pairs(verts)
        ]
        prism.add(triangle, *rects)
        prism.add(triangle.copy().shift(height * OUT))
        triangle.reverse_points()
        prism.set_shade_in_3d(True)
        prism.set_fill(PINK, 0.8)
        prism.set_stroke(WHITE, 1)
        return prism
