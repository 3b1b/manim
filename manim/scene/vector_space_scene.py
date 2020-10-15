"""A scene suitable for vector spaces."""

__all__ = ["VectorScene", "LinearTransformationScene"]


import numpy as np

from .. import config
from ..constants import *
from ..animation.animation import Animation
from ..animation.creation import ShowCreation
from ..animation.creation import Write
from ..animation.fading import FadeOut
from ..animation.growing import GrowArrow
from ..animation.transform import ApplyFunction
from ..animation.transform import ApplyPointwiseFunction
from ..animation.transform import Transform
from ..mobject.coordinate_systems import Axes
from ..mobject.coordinate_systems import NumberPlane
from ..mobject.geometry import Arrow
from ..mobject.geometry import Dot
from ..mobject.geometry import Line
from ..mobject.geometry import Rectangle
from ..mobject.geometry import Vector
from ..mobject.matrix import Matrix
from ..mobject.matrix import VECTOR_LABEL_SCALE_FACTOR
from ..mobject.matrix import vector_coordinate_label
from ..mobject.mobject import Mobject
from ..mobject.svg.tex_mobject import MathTex
from ..mobject.svg.tex_mobject import Tex
from ..mobject.types.vectorized_mobject import VGroup
from ..mobject.types.vectorized_mobject import VMobject
from ..scene.scene import Scene
from ..utils.color import GREEN_C, RED_C, BLUE_D, WHITE, YELLOW, GREY, LIGHT_GREY
from ..utils.rate_functions import rush_from
from ..utils.rate_functions import rush_into
from ..utils.space_ops import angle_of_vector
from ..utils.space_ops import get_norm

X_COLOR = GREEN_C
Y_COLOR = RED_C
Z_COLOR = BLUE_D


# TODO: Much of this scene type seems dependent on the coordinate system chosen.
# That is, being centered at the origin with grid units corresponding to the
# arbitrary space units.  Change it!
#
# Also, methods I would have thought of as getters, like coords_to_vector, are
# actually doing a lot of animating.
class VectorScene(Scene):
    CONFIG = {"basis_vector_stroke_width": 6}

    def add_plane(self, animate=False, **kwargs):
        """
        Adds a NumberPlane object to the background.

        Parameters
        ----------
        animate : bool, optional
            Whether or not to animate the addition of the plane via ShowCreation.
        **kwargs
            Any valid keyword arguments accepted by NumberPlane.

        Returns
        -------
        NumberPlane
            The NumberPlane object.
        """
        plane = NumberPlane(**kwargs)
        if animate:
            self.play(ShowCreation(plane, lag_ratio=0.5))
        self.add(plane)
        return plane

    def add_axes(self, animate=False, color=WHITE, **kwargs):
        """
        Adds a pair of Axes to the Scene.

        Parameters
        ----------
        animate : bool, optional
            Whether or not to animate the addition of the axes through ShowCreation.
        color : bool, optional
            The color of the axes. Defaults to WHITE.
        """
        axes = Axes(color=color, tick_frequency=1)
        if animate:
            self.play(ShowCreation(axes))
        self.add(axes)
        return axes

    def lock_in_faded_grid(self, dimness=0.7, axes_dimness=0.5):
        """
        This method freezes the NumberPlane and Axes that were already
        in the background, and adds new, manipulatable ones to the foreground.

        Parameters
        ----------
        dimness : int, float, optional
            The required dimness of the NumberPlane

        axes_dimness : int, float, optional
            The required dimness of the Axes.
        """
        plane = self.add_plane()
        axes = plane.get_axes()
        plane.fade(dimness)
        axes.set_color(WHITE)
        axes.fade(axes_dimness)
        self.add(axes)

        self.renderer.update_frame()
        self.renderer.camera = Camera(self.renderer.get_frame())
        self.clear()

    def get_vector(self, numerical_vector, **kwargs):
        """
        Returns an arrow on the Plane given an input numerical vector.

        Parameters
        ----------
        numerical_vector : np.array, list, tuple
            The Vector to plot.
        **kwargs
            Any valid keyword argument of Arrow.

        Returns
        -------
        Arrow
            The Arrow representing the Vector.
        """
        return Arrow(
            self.plane.coords_to_point(0, 0),
            self.plane.coords_to_point(*numerical_vector[:2]),
            buff=0,
            **kwargs,
        )

    def add_vector(self, vector, color=YELLOW, animate=True, **kwargs):
        """
        Returns the Vector after adding it to the Plane.

        Parameters
        ----------
        vector : Arrow, list, tuple, np.array
            It can be a pre-made graphical vector, or the
            coordinates of one.

        color : str
            The string of the hex color of the vector.
            This is only taken into consideration if
            'vector' is not an Arrow. Defaults to YELLOW.

        animate : bool
            Whether or not to animate the addition of the vector
            by using GrowArrow

        **kwargs
            Any valid keyword argument of Arrow.
            These are only considered if vector is not
            an Arrow.

        Returns
        -------
        Arrow
            The arrow representing the vector.
        """
        if not isinstance(vector, Arrow):
            vector = Vector(vector, color=color, **kwargs)
        if animate:
            self.play(GrowArrow(vector))
        self.add(vector)
        return vector

    def write_vector_coordinates(self, vector, **kwargs):
        """
        Returns a column matrix indicating the vector coordinates,
        after writing them to the screen.

        Parameters
        ----------
        vector : :class:`.Arrow`
            The arrow representing the vector.

        **kwargs
            Any valid keyword arguments of :meth:`~.matrix.vector_coordinate_label`:

            integer_labels : :class:`bool`
                Whether or not to round the coordinates to integers. Default: ``True``.
            n_dim : :class:`int`
                The number of dimensions of the vector. Default: ``2``.
            color
                The color of the label. Default: ``WHITE``.

        Returns
        -------
        :class:`.Matrix`
            The column matrix representing the vector.
        """
        coords = vector_coordinate_label(vector, **kwargs)
        self.play(Write(coords))
        return coords

    def get_basis_vectors(self, i_hat_color=X_COLOR, j_hat_color=Y_COLOR):
        """
        Returns a VGroup of the Basis Vectors (1,0) and (0,1)

        Parameters
        ----------
        i_hat_color : str
            The hex colour to use for the basis vector in the x direction

        j_hat_color : str
            The hex colour to use for the basis vector in the y direction

        Returns
        -------
        VGroup
            VGroup of the Vector Mobjects representing the basis vectors.
        """
        return VGroup(
            *[
                Vector(vect, color=color, stroke_width=self.basis_vector_stroke_width)
                for vect, color in [([1, 0], i_hat_color), ([0, 1], j_hat_color)]
            ]
        )

    def get_basis_vector_labels(self, **kwargs):
        """
        Returns naming labels for the basis vectors.

        Parameters
        ----------
        **kwargs
            Any valid keyword arguments of get_vector_label:
                vector,
                label (str,MathTex)
                at_tip (bool=False),
                direction (str="left"),
                rotate (bool),
                color (str),
                label_scale_factor=VECTOR_LABEL_SCALE_FACTOR (int, float),
        """
        i_hat, j_hat = self.get_basis_vectors()
        return VGroup(
            *[
                self.get_vector_label(
                    vect, label, color=color, label_scale_factor=1, **kwargs
                )
                for vect, label, color in [
                    (i_hat, "\\hat{\\imath}", X_COLOR),
                    (j_hat, "\\hat{\\jmath}", Y_COLOR),
                ]
            ]
        )

    def get_vector_label(
        self,
        vector,
        label,
        at_tip=False,
        direction="left",
        rotate=False,
        color=None,
        label_scale_factor=VECTOR_LABEL_SCALE_FACTOR,
    ):
        """
        Returns naming labels for the passed vector.

        Parameters
        ----------
        vector : Vector
            Vector Object for which to get the label.

        at_tip : bool
            Whether or not to place the label at the tip of the vector.

        direction : {"left"}
            If the label should be on the "left" or right of the vector.
        rotate : bool
            Whether or not to rotate it to align it with the vector.
        color : str
            The color to give the label.
        label_scale_factor (Union[int,float])
            How much to scale the label by.

        Returns
        -------
        MathTex
            The MathTex of the label.
        """
        if not isinstance(label, MathTex):
            if len(label) == 1:
                label = "\\vec{\\textbf{%s}}" % label
            label = MathTex(label)
            if color is None:
                color = vector.get_color()
            label.set_color(color)
        label.scale(label_scale_factor)
        label.add_background_rectangle()

        if at_tip:
            vect = vector.get_vector()
            vect /= get_norm(vect)
            label.next_to(vector.get_end(), vect, buff=SMALL_BUFF)
        else:
            angle = vector.get_angle()
            if not rotate:
                label.rotate(-angle, about_point=ORIGIN)
            if direction == "left":
                label.shift(-label.get_bottom() + 0.1 * UP)
            else:
                label.shift(-label.get_top() + 0.1 * DOWN)
            label.rotate(angle, about_point=ORIGIN)
            label.shift((vector.get_end() - vector.get_start()) / 2)
        return label

    def label_vector(self, vector, label, animate=True, **kwargs):
        """
        Shortcut method for creating, and animating the addition of
        a label for the vector.

        Parameters
        ----------
        vector : Vector
            The vector for which the label must be added.

        label : MathTex, str
            The MathTex/string of the label.

        animate : bool, optional
            Whether or not to animate the labelling w/ Write

        **kwargs
            Any valid keyword argument of get_vector_label

        Returns
        -------
        :class:`~.MathTex`
            The MathTex of the label.
        """
        label = self.get_vector_label(vector, label, **kwargs)
        if animate:
            self.play(Write(label, run_time=1))
        self.add(label)
        return label

    def position_x_coordinate(
        self, x_coord, x_line, vector
    ):  # TODO Write DocStrings for this.
        x_coord.next_to(x_line, -np.sign(vector[1]) * UP)
        x_coord.set_color(X_COLOR)
        return x_coord

    def position_y_coordinate(
        self, y_coord, y_line, vector
    ):  # TODO Write DocStrings for this.
        y_coord.next_to(y_line, np.sign(vector[0]) * RIGHT)
        y_coord.set_color(Y_COLOR)
        return y_coord

    def coords_to_vector(self, vector, coords_start=2 * RIGHT + 2 * UP, clean_up=True):
        """
        This method writes the vector as a column matrix (henceforth called the label),
        takes the values in it one by one, and form the corresponding
        lines that make up the x and y components of the vector. Then, an
        Vector() based vector is created between the lines on the Screen.

        Parameters
        ----------
        vector : np.ndarray, list, tuple
            The vector to show.

        coords_start : np.ndarray,list,tuple, optional
            The starting point of the location of
            the label of the vector that shows it
            numerically.
            Defaults to 2 * RIGHT + 2 * UP or (2,2)

        clean_up : bool, optional
            Whether or not to remove whatever
            this method did after it's done.

        """
        starting_mobjects = list(self.mobjects)
        array = Matrix(vector)
        array.shift(coords_start)
        arrow = Vector(vector)
        x_line = Line(ORIGIN, vector[0] * RIGHT)
        y_line = Line(x_line.get_end(), arrow.get_end())
        x_line.set_color(X_COLOR)
        y_line.set_color(Y_COLOR)
        x_coord, y_coord = array.get_mob_matrix().flatten()

        self.play(Write(array, run_time=1))
        self.wait()
        self.play(
            ApplyFunction(
                lambda x: self.position_x_coordinate(x, x_line, vector), x_coord
            )
        )
        self.play(ShowCreation(x_line))
        self.play(
            ApplyFunction(
                lambda y: self.position_y_coordinate(y, y_line, vector), y_coord
            ),
            FadeOut(array.get_brackets()),
        )
        y_coord, brackets = self.mobjects_from_last_animation
        self.play(ShowCreation(y_line))
        self.play(ShowCreation(arrow))
        self.wait()
        if clean_up:
            self.clear()
            self.add(*starting_mobjects)

    def vector_to_coords(self, vector, integer_labels=True, clean_up=True):
        """
        This method displays vector as a Vector() based vector, and then shows
        the corresponding lines that make up the x and y components of the vector.
        Then, a column matrix (henceforth called the label) is created near the
        head of the Vector.

        Parameters
        ----------
        vector : np.ndarray, list, tuple
            The vector to show.

        integer_label : bool, optional
            Whether or not to round the value displayed.
            in the vector's label to the nearest integer

        clean_up : bool, optional
            Whether or not to remove whatever
            this method did after it's done.

        """
        starting_mobjects = list(self.mobjects)
        show_creation = False
        if isinstance(vector, Arrow):
            arrow = vector
            vector = arrow.get_end()[:2]
        else:
            arrow = Vector(vector)
            show_creation = True
        array = vector_coordinate_label(arrow, integer_labels=integer_labels)
        x_line = Line(ORIGIN, vector[0] * RIGHT)
        y_line = Line(x_line.get_end(), arrow.get_end())
        x_line.set_color(X_COLOR)
        y_line.set_color(Y_COLOR)
        x_coord, y_coord = array.get_mob_matrix().flatten()
        x_coord_start = self.position_x_coordinate(x_coord.copy(), x_line, vector)
        y_coord_start = self.position_y_coordinate(y_coord.copy(), y_line, vector)
        brackets = array.get_brackets()

        if show_creation:
            self.play(ShowCreation(arrow))
        self.play(ShowCreation(x_line), Write(x_coord_start), run_time=1)
        self.play(ShowCreation(y_line), Write(y_coord_start), run_time=1)
        self.wait()
        self.play(
            Transform(x_coord_start, x_coord, lag_ratio=0),
            Transform(y_coord_start, y_coord, lag_ratio=0),
            Write(brackets, run_time=1),
        )
        self.wait()

        self.remove(x_coord_start, y_coord_start, brackets)
        self.add(array)
        if clean_up:
            self.clear()
            self.add(*starting_mobjects)
        return array, x_line, y_line

    def show_ghost_movement(self, vector):
        """
        This method plays an animation that partially shows the entire plane moving
        in the direction of a particular vector. This is useful when you wish to
        convey the idea of mentally moving the entire plane in a direction, without
        actually moving the plane.

        Parameters
        ----------
        vector : Arrow, list, tuple, np.ndarray
            The vector which indicates the direction of movement.
        """
        if isinstance(vector, Arrow):
            vector = vector.get_end() - vector.get_start()
        elif len(vector) == 2:
            vector = np.append(np.array(vector), 0.0)
        x_max = int(config["frame_x_radius"] + abs(vector[0]))
        y_max = int(config["frame_y_radius"] + abs(vector[1]))
        dots = VMobject(
            *[
                Dot(x * RIGHT + y * UP)
                for x in range(-x_max, x_max)
                for y in range(-y_max, y_max)
            ]
        )
        dots.set_fill(BLACK, opacity=0)
        dots_halfway = dots.copy().shift(vector / 2).set_fill(WHITE, 1)
        dots_end = dots.copy().shift(vector)

        self.play(Transform(dots, dots_halfway, rate_func=rush_into))
        self.play(Transform(dots, dots_end, rate_func=rush_from))
        self.remove(dots)


class LinearTransformationScene(VectorScene):
    """
    This scene contains special methods that make it
    especially suitable for showing Linear Transformations.
    """

    CONFIG = {
        "include_background_plane": True,
        "include_foreground_plane": True,
        "background_plane_kwargs": {
            "color": GREY,
            "axis_config": {
                "stroke_color": LIGHT_GREY,
            },
            "axis_config": {
                "color": GREY,
            },
            "background_line_style": {
                "stroke_color": GREY,
                "stroke_width": 1,
            },
        },
        "show_coordinates": False,
        "show_basis_vectors": True,
        "basis_vector_stroke_width": 6,
        "i_hat_color": X_COLOR,
        "j_hat_color": Y_COLOR,
        "leave_ghost_vectors": False,
        "t_matrix": [[3, 0], [1, 2]],
    }

    def __init__(self, **kwargs):
        VectorScene.__init__(self, **kwargs)
        self.foreground_plane_kwargs = {
            "x_max": config["frame_width"] / 2,
            "x_min": -config["frame_width"] / 2,
            "y_max": config["frame_width"] / 2,
            "y_min": -config["frame_width"] / 2,
            "faded_line_ratio": 0,
        }

    def setup(self):
        # The has_already_setup attr is to not break all the old Scenes
        if hasattr(self, "has_already_setup"):
            return
        self.has_already_setup = True
        self.background_mobjects = []
        self.foreground_mobjects = []
        self.transformable_mobjects = []
        self.moving_vectors = []
        self.transformable_labels = []
        self.moving_mobjects = []

        self.t_matrix = np.array(self.t_matrix)
        self.background_plane = NumberPlane(**self.background_plane_kwargs)

        if self.show_coordinates:
            self.background_plane.add_coordinates()
        if self.include_background_plane:
            self.add_background_mobject(self.background_plane)
        if self.include_foreground_plane:
            self.plane = NumberPlane(**self.foreground_plane_kwargs)
            self.add_transformable_mobject(self.plane)
        if self.show_basis_vectors:
            self.basis_vectors = self.get_basis_vectors(
                i_hat_color=self.i_hat_color,
                j_hat_color=self.j_hat_color,
            )
            self.moving_vectors += list(self.basis_vectors)
            self.i_hat, self.j_hat = self.basis_vectors
            self.add(self.basis_vectors)

    def add_special_mobjects(self, mob_list, *mobs_to_add):
        """
        Adds mobjects to a separate list that can be tracked,
        if these mobjects have some extra importance.

        Parameters
        ----------
        mob_list : list
            The special list to which you want to add
            these mobjects.

        *mobs_to_add : Mobject
            The mobjects to add.

        """
        for mobject in mobs_to_add:
            if mobject not in mob_list:
                mob_list.append(mobject)
                self.add(mobject)

    def add_background_mobject(self, *mobjects):
        """
        Adds the mobjects to the special list
        self.background_mobjects.

        Parameters
        ----------
        *mobjects : Mobject
            The mobjects to add to the list.
        """
        self.add_special_mobjects(self.background_mobjects, *mobjects)

    # TODO, this conflicts with Scene.add_fore
    def add_foreground_mobject(self, *mobjects):
        """
        Adds the mobjects to the special list
        self.foreground_mobjects.

        Parameters
        ----------
        *mobjects : Mobject
            The mobjects to add to the list
        """
        self.add_special_mobjects(self.foreground_mobjects, *mobjects)

    def add_transformable_mobject(self, *mobjects):
        """
        Adds the mobjects to the special list
        self.transformable_mobjects.

        Parameters
        ----------
        *mobjects : Mobject
            The mobjects to add to the list.
        """
        self.add_special_mobjects(self.transformable_mobjects, *mobjects)

    def add_moving_mobject(self, mobject, target_mobject=None):
        """
        Adds the mobject to the special list
        self.moving_mobject, and adds a property
        to the mobject called mobject.target, which
        keeps track of what the mobject will move to
        or become etc.

        Parameters
        ----------
        mobject : Mobject
            The mobjects to add to the list

        target_mobject : Mobject, optional
            What the moving_mobject goes to, etc.
        """
        mobject.target = target_mobject
        self.add_special_mobjects(self.moving_mobjects, mobject)

    def get_unit_square(self, color=YELLOW, opacity=0.3, stroke_width=3):
        """
        Returns a unit square for the current NumberPlane.

        Parameters
        ----------
        color : str, optional
            The string of the hex color code of the color wanted.

        opacity : float, int, optional
            The opacity of the square

        stroke_width : int, float, optional
            The stroke_width in pixels of the border of the square

        Returns
        -------
        Square
        """
        square = self.square = Rectangle(
            color=color,
            width=self.plane.get_x_unit_size(),
            height=self.plane.get_y_unit_size(),
            stroke_color=color,
            stroke_width=stroke_width,
            fill_color=color,
            fill_opacity=opacity,
        )
        square.move_to(self.plane.coords_to_point(0, 0), DL)
        return square

    def add_unit_square(self, animate=False, **kwargs):
        """
        Adds a unit square to the scene via
        self.get_unit_square.

        Parameters
        ----------
        animate (bool)
            Whether or not to animate the addition
            with DrawBorderThenFill.
        **kwargs
            Any valid keyword arguments of
            self.get_unit_square()

        Returns
        -------
        Square
            The unit square.
        """
        square = self.get_unit_square(**kwargs)
        if animate:
            self.play(
                DrawBorderThenFill(square), Animation(Group(*self.moving_vectors))
            )
        self.add_transformable_mobject(square)
        self.bring_to_front(*self.moving_vectors)
        self.square = square
        return self

    def add_vector(self, vector, color=YELLOW, **kwargs):
        """
        Adds a vector to the scene, and puts it in the special
        list self.moving_vectors.

        Parameters
        ----------
        vector : Arrow,list,tuple,np.ndarray
            It can be a pre-made graphical vector, or the
            coordinates of one.

        color : str
            The string of the hex color of the vector.
            This is only taken into consideration if
            'vector' is not an Arrow. Defaults to YELLOW.

        **kwargs
            Any valid keyword argument of VectorScene.add_vector.

        Returns
        -------
        Arrow
            The arrow representing the vector.
        """
        vector = VectorScene.add_vector(self, vector, color=color, **kwargs)
        self.moving_vectors.append(vector)
        return vector

    def write_vector_coordinates(self, vector, **kwargs):
        """
        Returns a column matrix indicating the vector coordinates,
        after writing them to the screen, and adding them to the
        special list self.foreground_mobjects

        Parameters
        ----------
        vector : Arrow
            The arrow representing the vector.

        **kwargs
            Any valid keyword arguments of VectorScene.write_vector_coordinates

        Returns
        -------
        Matrix
            The column matrix representing the vector.
        """
        coords = VectorScene.write_vector_coordinates(self, vector, **kwargs)
        self.add_foreground_mobject(coords)
        return coords

    def add_transformable_label(
        self, vector, label, transformation_name="L", new_label=None, **kwargs
    ):
        """
        Method for creating, and animating the addition of
        a transformable label for the vector.

        Parameters
        ----------
        vector : Vector
            The vector for which the label must be added.

        label : Union[:class:`~.MathTex`, :class:`str`]
            The MathTex/string of the label.

        transformation_name : Union[:class:`str`, :class:`~.MathTex`], optional
            The name to give the transformation as a label.

        new_label : Union[:class:`str`, :class:`~.MathTex`], optional
            What the label should display after a Linear Transformation

        **kwargs
            Any valid keyword argument of get_vector_label

        Returns
        -------
        :class:`~.MathTex`
            The MathTex of the label.
        """
        label_mob = self.label_vector(vector, label, **kwargs)
        if new_label:
            label_mob.target_text = new_label
        else:
            label_mob.target_text = "%s(%s)" % (
                transformation_name,
                label_mob.get_tex_string(),
            )
        label_mob.vector = vector
        label_mob.kwargs = kwargs
        if "animate" in label_mob.kwargs:
            label_mob.kwargs.pop("animate")
        self.transformable_labels.append(label_mob)
        return label_mob

    def add_title(self, title, scale_factor=1.5, animate=False):
        """
        Adds a title, after scaling it, adding a background rectangle,
        moving it to the top and adding it to foreground_mobjects adding
        it as a local variable of self. Returns the Scene.

        Parameters
        ----------
        title : Union[:class:`str`, :class:`~.MathTex`, :class:`~.Tex`]
            What the title should be.

        scale_factor : int, float, optional
            How much the title should be scaled by.

        animate : bool
            Whether or not to animate the addition.

        Returns
        -------
        LinearTransformationScene
            The scene with the title added to it.
        """
        if not isinstance(title, Mobject):
            title = Tex(title).scale(scale_factor)
        title.to_edge(UP)
        title.add_background_rectangle()
        if animate:
            self.play(Write(title))
        self.add_foreground_mobject(title)
        self.title = title
        return self

    def get_matrix_transformation(self, matrix):
        """
        Returns a function corresponding to the linear
        transformation represented by the matrix passed.

        Parameters
        ----------
        matrix : np.ndarray, list, tuple
            The matrix.
        """
        return self.get_transposed_matrix_transformation(np.array(matrix).T)

    def get_transposed_matrix_transformation(self, transposed_matrix):
        """
        Returns a function corresponding to the linear
        transformation represented by the transposed
        matrix passed.

        Parameters
        ----------
        matrix : np.ndarray, list, tuple
            The matrix.
        """
        transposed_matrix = np.array(transposed_matrix)
        if transposed_matrix.shape == (2, 2):
            new_matrix = np.identity(3)
            new_matrix[:2, :2] = transposed_matrix
            transposed_matrix = new_matrix
        elif transposed_matrix.shape != (3, 3):
            raise ValueError("Matrix has bad dimensions")
        return lambda point: np.dot(point, transposed_matrix)

    def get_piece_movement(self, pieces):
        """
        This method returns an animation that moves an arbitrary
        mobject in "pieces" to its corresponding .target value.
        If self.leave_ghost_vectors is True, ghosts of the original
        positions/mobjects are left on screen

        Parameters
        ----------
        pieces : list, tuple, np.array
            The pieces for which the movement must be shown.

        Returns
        -------
        Animation
            The animation of the movement.
        """
        start = VGroup(*pieces)
        target = VGroup(*[mob.target for mob in pieces])
        if self.leave_ghost_vectors:
            self.add(start.copy().fade(0.7))
        return Transform(start, target, lag_ratio=0)

    def get_moving_mobject_movement(self, func):
        """
        This method returns an animation that moves a mobject
        in "self.moving_mobjects"  to its corresponding .target value.
        func is a function that determines where the .target goes.

        Parameters
        ----------

        func : function
            The function that determines where the .target of
            the moving mobject goes.

        Returns
        -------
        Animation
            The animation of the movement.
        """
        for m in self.moving_mobjects:
            if m.target is None:
                m.target = m.copy()
            target_point = func(m.get_center())
            m.target.move_to(target_point)
        return self.get_piece_movement(self.moving_mobjects)

    def get_vector_movement(self, func):
        """
        This method returns an animation that moves a mobject
        in "self.moving_vectors"  to its corresponding .target value.
        func is a function that determines where the .target goes.

        Parameters
        ----------

        func : function
            The function that determines where the .target of
            the moving mobject goes.

        Returns
        -------
        Animation
            The animation of the movement.
        """
        for v in self.moving_vectors:
            v.target = Vector(func(v.get_end()), color=v.get_color())
            norm = get_norm(v.target.get_end())
            if norm < 0.1:
                v.target.get_tip().scale_in_place(norm)
        return self.get_piece_movement(self.moving_vectors)

    def get_transformable_label_movement(self):
        """
        This method returns an animation that moves all labels
        in "self.transformable_labels" to its corresponding .target .

        Returns
        -------
        Animation
            The animation of the movement.
        """
        for l in self.transformable_labels:
            l.target = self.get_vector_label(l.vector.target, l.target_text, **l.kwargs)
        return self.get_piece_movement(self.transformable_labels)

    def apply_matrix(self, matrix, **kwargs):
        """
        Applies the transformation represented by the
        given matrix to the number plane, and each vector/similar
        mobject on it.

        Parameters
        ----------
        matrix : np.ndarray, list, tuple
            The matrix.
        **kwargs
            Any valid keyword argument of self.apply_transposed_matrix()
        """
        self.apply_transposed_matrix(np.array(matrix).T, **kwargs)

    def apply_inverse(self, matrix, **kwargs):
        """
        This method applies the linear transformation
        represented by the inverse of the passed matrix
        to the number plane, and each vector/similar mobject on it.

        Parameters
        ----------
        matrix : np.ndarray, list, tuple
            The matrix whose inverse is to be applied.
        **kwargs
            Any valid keyword argument of self.apply_matrix()
        """
        self.apply_matrix(np.linalg.inv(matrix), **kwargs)

    def apply_transposed_matrix(self, transposed_matrix, **kwargs):
        """
        Applies the transformation represented by the
        given transposed matrix to the number plane,
        and each vector/similar mobject on it.

        Parameters
        ----------
        matrix : np.ndarray, list, tuple
            The matrix.
        **kwargs
            Any valid keyword argument of self.apply_function()
        """
        func = self.get_transposed_matrix_transformation(transposed_matrix)
        if "path_arc" not in kwargs:
            net_rotation = np.mean(
                [angle_of_vector(func(RIGHT)), angle_of_vector(func(UP)) - np.pi / 2]
            )
            kwargs["path_arc"] = net_rotation
        self.apply_function(func, **kwargs)

    def apply_inverse_transpose(self, t_matrix, **kwargs):
        """
        Applies the inverse of the transformation represented
        by the given transposed matrix to the number plane and each
        vector/similar mobject on it.

        Parameters
        ----------
        matrix : np.ndarray, list, tuple
            The matrix.
        **kwargs
            Any valid keyword argument of self.apply_transposed_matrix()
        """
        t_inv = np.linalg.inv(np.array(t_matrix).T).T
        self.apply_transposed_matrix(t_inv, **kwargs)

    def apply_nonlinear_transformation(self, function, **kwargs):
        """
        Applies the non-linear transformation represented
        by the given function to the number plane and each
        vector/similar mobject on it.

        Parameters
        ----------
        function : Function
            The function.
        **kwargs
            Any valid keyword argument of self.apply_function()
        """
        self.plane.prepare_for_nonlinear_transform()
        self.apply_function(function, **kwargs)

    def apply_function(self, function, added_anims=[], **kwargs):
        """
        Applies the given function to each of the mobjects in
        self.transformable_mobjects, and plays the animation showing
        this.

        Parameters
        ----------
        function : Function
            The function that affects each point
            of each mobject in self.transformable_mobjects.

        added_anims : list, optional
            Any other animations that need to be played
            simulataneously with this.

        **kwargs
            Any valid keyword argument of a self.play() call.
        """
        if "run_time" not in kwargs:
            kwargs["run_time"] = 3
        anims = (
            [
                ApplyPointwiseFunction(function, t_mob)
                for t_mob in self.transformable_mobjects
            ]
            + [
                self.get_vector_movement(function),
                self.get_transformable_label_movement(),
                self.get_moving_mobject_movement(function),
            ]
            + [Animation(f_mob) for f_mob in self.foreground_mobjects]
            + added_anims
        )
        self.play(*anims, **kwargs)
