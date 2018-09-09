from colour import Color
from mobject.mobject import Mobject
from pytest import approx
from unittest.mock import call
from unittest.mock import create_autospec

import camera.camera
import constants as const
import inspect
import mobject.mobject
import numpy as np
import os
import pytest


SEED = 386735
np.random.seed(SEED)


def test_init():
    m = Mobject()

    # test default instance variables
    default_config = Mobject.CONFIG
    assert m.color == Color(default_config["color"])
    assert m.name == m.__class__.__name__
    assert m.dim == default_config["dim"]
    assert m.target == default_config["target"]
    assert m.submobjects == []

    # All submobjects must be of type Mobject
    with pytest.raises(Exception):
        m = Mobject(5)


def test_str():
    m = Mobject()
    assert str(m) == "Mobject"


def test_reset_points():
    m = Mobject()
    m.reset_points()
    assert np.all(m.points == np.zeros((0, m.dim)))


def test_add():
    m = Mobject()
    s1 = Mobject()
    s2 = Mobject()

    # All submobjects must be of type Mobject
    with pytest.raises(Exception):
        m.add(5)

    # Mobject cannot contain self
    with pytest.raises(Exception):
        m.add(m)

    m.add(s1)
    assert m.submobjects == [s1]

    # Mobject.submobjects cannot contain duplicates
    m.add(s1)
    assert m.submobjects == [s1]

    # Newly added Mobjects become the last elements of Mobject.submobjects
    m.add(s2)
    assert m.submobjects == [s1, s2]

    # Repeated additions move mobjects to the end
    m.add(s1)
    assert m.submobjects == [s2, s1]


def test_add_to_back():
    s1 = Mobject()
    s2 = Mobject()
    s3 = Mobject()
    m = Mobject(s1, s2, s3)

    # All submobjects must be of type Mobject
    with pytest.raises(Exception):
        m.add_to_back(5)

    # Mobject cannot contain self
    with pytest.raises(Exception):
        m.add_to_back(m)

    # Newly added Mobjects become the first elements of Mobject.submobjects
    s4 = Mobject()
    m.add_to_back(s4)
    assert m.submobjects == [s4, s1, s2, s3]

    m.add_to_back(s1, s2)
    assert m.submobjects == [s1, s2, s4, s3]


def test_remove():
    s1 = Mobject()
    s2 = Mobject()
    s3 = Mobject()
    m = Mobject(s1, s2, s3)

    m.remove(s2)
    assert m.submobjects == [s1, s3]

    m.remove(s1, s3)
    assert m.submobjects == []

    m.remove(s1)
    assert m.submobjects == []


def test_get_array_attrs():
    assert Mobject().get_array_attrs() == ["points"]


def test_digest_mobject_attrs():
    m = Mobject()
    a = Mobject()
    m.attr = a
    m.digest_mobject_attrs()
    assert m.submobjects == [a]

    m.attr = m
    with pytest.raises(Exception):
        m.digest_mobject_attrs()


def test_apply_over_attr_arrays():
    m = Mobject()
    for attr in m.get_array_attrs():
        setattr(m, attr, np.zeros((3, 3)))
    m.apply_over_attr_arrays(lambda x: x + 1)
    for attr in m.get_array_attrs():
        assert getattr(m, attr) == approx(np.ones((3, 3)))


def test_get_image(mocker):
    mock_get_image = mocker.patch.object(camera.camera.Camera, "get_image")
    mock_capture_mobject = mocker.patch.object(
        camera.camera.Camera,
        "capture_mobject",
    )
    m = Mobject()
    m.get_image()
    mock_capture_mobject.assert_called_once_with(m)
    mock_get_image.assert_called_once_with()


def test_show(mocker):
    mocker.patch.object(mobject.mobject.Mobject, "get_image")
    m = Mobject()
    m.show()
    expected = call(camera=None).show().call_list()
    assert m.get_image.mock_calls == expected


def test_save_image(mocker, monkeypatch):
    m = Mobject()
    mock_animations_dir = "test_dir"
    mock_path = os.path.join(mock_animations_dir, f"{str(m)}.png")
    mocker.patch.object(mobject.mobject.Mobject, "get_image")
    monkeypatch.setattr(mobject.mobject, "ANIMATIONS_DIR", mock_animations_dir)
    mocker.spy(os.path, "join")

    m.save_image()
    os.path.join.assert_called_once_with(mock_animations_dir, f"{str(m)}.png")
    expected_get_image_calls = call().save(mock_path).call_list()
    assert m.get_image.mock_calls == expected_get_image_calls


def test_copy():
    m1 = Mobject()
    for attr in m1.get_array_attrs():
        setattr(m1, attr, np.zeros((3, 3)))
    m1.submobjects = [Mobject()]
    m1.mob_attr = m1.submobjects[0]
    m1.submobjects[0].points = np.zeros((3, 3))
    m1.arr = [0]

    m2 = m1.copy()
    for attr in m2.get_array_attrs():
        setattr(m2, attr, np.ones((3, 3)))
    m2.add(Mobject())
    m2.mob_attr = None
    m2.arr[0] = 1

    # mobjects attributes, (nd)array attributes, and
    # submobjects should not be shared
    assert np.allclose(m1.points, np.zeros((3, 3)))
    assert len(m1.submobjects) == 1
    assert m1.mob_attr is not None

    # other attributes are shared
    assert m1.arr[0] == 1


def test_deepcopy():
    m1 = Mobject()
    for attr in m1.get_array_attrs():
        setattr(m1, attr, np.zeros((3, 3)))
    m1.submobjects = [Mobject()]
    m1.mob_attr = m1.submobjects[0]
    m1.submobjects[0].points = np.zeros((3, 3))
    m1.arr = [0]

    m2 = m1.deepcopy()
    for attr in m2.get_array_attrs():
        setattr(m2, attr, np.ones((3, 3)))
    m2.add(Mobject())
    m2.mob_attr = None
    m2.arr[0] = 1

    # no attributes are shared
    assert np.allclose(m1.points, np.zeros((3, 3)))
    assert len(m1.submobjects) == 1
    assert m1.mob_attr is not None
    assert m1.arr[0] == 0


def test_generate_target():
    m1 = Mobject()
    for attr in m1.get_array_attrs():
        setattr(m1, attr, np.zeros((3, 3)))
    m1.submobjects = [Mobject()]
    m1.mob_attr = m1.submobjects[0]
    m1.submobjects[0].points = np.zeros((3, 3))
    m1.arr = [0]

    # test shallow copy
    m1.generate_target()
    for attr in m1.target.get_array_attrs():
        setattr(m1.target, attr, np.ones((3, 3)))
    m1.target.add(Mobject())
    m1.target.mob_attr = None
    m1.target.arr[0] = 1
    assert np.allclose(m1.points, np.zeros((3, 3)))
    assert len(m1.submobjects) == 1
    assert m1.mob_attr is not None
    assert m1.arr[0] == 1

    # test deep copy
    m1.generate_target(use_deepcopy=True)
    m1.target = m1.deepcopy()
    for attr in m1.target.get_array_attrs():
        setattr(m1.target, attr, np.full((3, 3), 2))
    m1.target.add(Mobject())
    m1.target.mob_attr = None
    m1.target.arr[0] = 2
    assert np.allclose(m1.points, np.zeros((3, 3)))
    assert len(m1.submobjects) == 1
    assert m1.mob_attr is not None
    assert m1.arr[0] == 1


def test_update(monkeypatch):
    # patch get_num_args since it always returns 2 on Mocks
    mock_updater_1 = create_autospec(lambda x: None)
    mock_updater_2 = create_autospec(lambda x, y: None)
    mock_updater_3 = create_autospec(lambda x, y, z: None)

    def mock_get_num_args(func):
        if func == mock_updater_1:
            return 1
        elif func == mock_updater_2:
            return 2
        elif func == mock_updater_3:
            return 3
        else:
            raise Exception()

    monkeypatch.setattr(mobject.mobject, "get_num_args", mock_get_num_args)

    m = Mobject()
    m.add_updater(mock_updater_1, call_updater=False)
    m.add_updater(mock_updater_2, call_updater=False)
    assert len(m.get_updaters()) == 2
    assert len(m.get_time_based_updaters()) == 1
    m.update(1)
    mock_updater_1.assert_called_once_with(m)
    mock_updater_2.assert_called_once_with(m, 1)

    mock_updater_1.reset_mock()
    mock_updater_2.reset_mock()
    m.remove_updater(mock_updater_2)
    assert len(m.get_updaters()) == 1
    assert len(m.get_time_based_updaters()) == 0
    m.update(1)
    mock_updater_1.assert_called_once_with(m)
    mock_updater_2.assert_not_called()

    mock_updater_1.reset_mock()
    mock_updater_2.reset_mock()
    m.add_updater(mock_updater_2, call_updater=False)
    m.add_updater(mock_updater_3, call_updater=False)
    assert len(m.get_updaters()) == 3
    assert len(m.get_time_based_updaters()) == 1
    with pytest.raises(Exception):
        m.update(1)

    mock_updater_1.reset_mock()
    mock_updater_2.reset_mock()
    mock_updater_3.reset_mock()
    m.clear_updaters()
    assert len(m.get_updaters()) == 0
    assert len(m.get_time_based_updaters()) == 0


def test_apply_to_family():
    submob1 = Mobject()
    submob1.points = np.zeros((3, 3))
    submob2 = Mobject()
    submob2.points = np.zeros((3, 3))
    m = Mobject(submob1, submob2)

    def func(mob):
        mob.points = np.ones((3, 3))

    m.apply_to_family(func)
    for mob in m.family_members_with_points():
        assert mob.points == approx(np.ones((3, 3)))


def test_shift():
    submob = Mobject()
    m = Mobject(submob)
    mob_points = np.random.rand(10, 3)
    submob_points = np.random.rand(5, 3)
    m.points = mob_points
    submob.points = submob_points
    m.shift(2 * const.RIGHT - 1 * const.UP)
    assert m.points == approx(mob_points + np.array([2, -1, 0]))
    assert submob.points == approx(submob_points + np.array([2, -1, 0]))


def test_scale(mocker):
    mocker.patch.object(
        mobject.mobject.Mobject,
        "apply_points_function_about_point",
        autospec=True,
    )
    m = Mobject()
    m.scale(3)
    m.apply_points_function_about_point.assert_called_once()
    args, kwargs = m.apply_points_function_about_point.call_args
    assert args[0] is m
    assert callable(args[1])
    assert (
        inspect.getsource(args[1]).strip() ==
        "lambda points: scale_factor * points, **kwargs"
    )
    assert kwargs == {}


def test_rotate_about_origin(mocker):
    mocker.patch.object(mobject.mobject.Mobject, "rotate")
    m = Mobject()
    angle = 3 * const.PI / 4
    m.rotate_about_origin(angle)
    m.rotate.assert_called_once_with(
        angle,
        const.OUT,
        about_point=const.ORIGIN,
    )


def test_rotate(mocker):
    mock_rotation_matrix = mocker.patch("mobject.mobject.rotation_matrix")
    mocker.patch.object(
        mobject.mobject.Mobject,
        "apply_points_function_about_point",
        autospec=True,
    )
    m = Mobject()
    angle = 3 * const.PI / 4
    m.rotate(angle)
    mock_rotation_matrix.assert_called_once_with(angle, const.OUT)
    m.apply_points_function_about_point.assert_called_once()
    args, kwargs = m.apply_points_function_about_point.call_args
    assert args[0] is m
    assert callable(args[1])
    assert (
        inspect.getsource(args[1]).strip().replace("\n", " ") ==
        "lambda points: np.dot(points, rot_matrix.T),"
    )
    assert kwargs == {}


def test_flip(mocker):
    mocker.spy(mobject.mobject.Mobject, "rotate")
    m = Mobject()
    m.points = np.array([
        [1, 1, 0],
        [-1, -1, 0],
        [2, 2, 0],
        [-2, -2, 0],
    ])
    m.flip()
    m.rotate.assert_called_once_with(m, const.TAU / 2, const.UP)
    expected = np.array([[-1, 1, 0],
                         [1, -1, 0],
                         [-2, 2, 0],
                         [2, -2, 0]])
    assert(np.allclose(m.points, expected))


def test_stretch(mocker):
    mocker.spy(
        mobject.mobject.Mobject, "apply_points_function_about_point"
    )
    m = Mobject()
    m.points = np.array([
        [0, 1, 0],
        [0, 0, 0],
        [0, -1, 0],
    ])
    m.stretch(3, 1)
    m.apply_points_function_about_point.assert_called_once()
    args, kwargs = m.apply_points_function_about_point.call_args
    assert args[0] is m
    assert callable(args[1])
    assert (
        inspect.getsource(args[1]).strip() ==
        "def func(points):\n"
        "            points[:, dim] *= factor\n"
        "            return points"
    )
    assert kwargs == {}
    assert(np.allclose(m.points, [[0, 3, 0],
                                  [0, 0, 0],
                                  [0, -3, 0]]))


def test_apply_function(mocker):
    mocker.patch.object(
        mobject.mobject.Mobject,
        "apply_points_function_about_point",
        autospec=True,
    )
    mock_func = mocker.Mock()
    m = Mobject()
    m.apply_function(mock_func)
    m.apply_points_function_about_point.assert_called_once()
    args, kwargs = m.apply_points_function_about_point.call_args
    assert args[0] is m
    assert callable(args[1])
    assert (
        inspect.getsource(args[1]).strip() ==
        "lambda points: np.apply_along_axis(function, 1, points),"
    )
    assert kwargs == {"about_point": const.ORIGIN}


def test_apply_function_to_position(mocker):
    mock_get_center_return = np.random.randint(1000)
    mocker.patch.object(
        mobject.mobject.Mobject,
        'get_center',
        autospec=True,
        return_value=mock_get_center_return,
    )
    mock_func_return = np.random.randint(1000)
    mock_func = mocker.Mock(return_value=mock_func_return)
    mocker.patch.object(mobject.mobject.Mobject, 'move_to', autospec=True)
    m = Mobject()
    m.apply_function_to_position(mock_func)

    m.get_center.assert_called_once_with(m)
    mock_func.assert_called_once_with(mock_get_center_return)
    m.move_to.assert_called_once_with(m, mock_func_return)


def test_apply_function_to_submobject_positions(mocker):
    s1 = Mobject()
    s2 = Mobject()
    s3 = Mobject()
    m = Mobject(s1, s2, s3)
    mock_func = mocker.Mock()
    mocker.patch.object(mobject.mobject.Mobject, 'apply_function_to_position')
    m.apply_function_to_submobject_positions(mock_func)

    for submob in m.submobjects:
        submob.apply_function_to_position.assert_called_with(mock_func)


def test_apply_matrix():
    points = np.random.rand(10, 3)
    matrix = np.random.rand(3, 3)
    m = Mobject()
    m.points = points.copy()
    m.apply_matrix(matrix)

    expected = points.copy()
    expected -= const.ORIGIN
    expected = np.dot(points, matrix.T)
    expected += const.ORIGIN
    assert(np.allclose(m.points, expected))

    m.points = points
    about_point = np.random.rand(1, 3)

    expected = points.copy()
    expected -= about_point
    expected = np.dot(expected, matrix.T)
    expected += about_point

    m.apply_matrix(matrix, about_point=about_point)
    assert(np.allclose(m.points, expected))


def test_apply_complex_function(mocker):
    mocker.patch.object(
        mobject.mobject.Mobject,
        'apply_function',
        autospec=True,
    )
    mock_func = mocker.Mock()
    m = Mobject()
    m.apply_complex_function(mock_func)
    m.apply_function.assert_called_once()
    args, kwargs = m.apply_function.call_args
    assert(len(args) == 2)
    assert(args[0] is m)
    assert (
        inspect.getsource(args[1]).strip() ==
        "lambda x_y_z: complex_to_R3(function(complex(x_y_z[0], x_y_z[1]))),"
    )
    assert(kwargs == {})


# this is a rather odd function. the current contract is simply that wag() will
# do what is does in this version (0c3e1308cd40e12f795e0f8e753acca02874c2b3).
def test_wag():
    points = np.random.rand(10, 3)
    m = Mobject()
    m.points = points.copy()
    m.wag()

    expected = points.copy()
    alphas = np.dot(expected, np.transpose(const.DOWN))
    alphas -= min(alphas)
    alphas /= max(alphas)
    # alphas = alphas**wag_factor
    expected += np.dot(
        alphas.reshape((len(alphas), 1)),
        np.array(const.RIGHT).reshape((1, m.dim))
    )
    assert(np.allclose(m.points, expected))


def test_reverse_points():
    points = np.random.rand(10, 3)
    m = Mobject()
    m.points = points.copy()
    m.reverse_points()

    expected = points.copy()
    assert(np.allclose(m.points, np.flip(expected, axis=0)))

# def repeat():
#    def repeat_array():
# # Note, much of these are now redundant with default behavior of
# def apply_points_function_about_point():
# def rotate_in_place():
#    # redundant with default behavior of rotate now.
# def scale_in_place():
#    # Redundant with default behavior of scale now.
# def scale_about_point():
#    # Redundant with default behavior of scale now.
# def pose_at_angle():
# def center():
# def align_on_border():
# def to_corner():
# def to_edge():
# def next_to(self, mobject_or_point,
# def align_to():
# def shift_onto_screen():
# def is_off_screen():
# def stretch_about_point():
# def stretch_in_place():
# def rescale_to_fit():
# def stretch_to_fit_width():
# def stretch_to_fit_height():
# def stretch_to_fit_depth():
# def scale_to_fit_width():
# def scale_to_fit_height():
# def scale_to_fit_depth():
# def space_out_submobjects():
# def move_to(self, point_or_mobject, aligned_edge=const.ORIGIN,
# def replace():
# def surround():
# def position_endpoints_on():
# def add_background_rectangle():
# def add_background_rectangle_to_submobjects():
# def add_background_rectangle_to_family_members_with_points():
# def match_color():
# def match_dim():
# def match_width():
# def match_height():
# def match_depth():
# def set_color():
# def set_color_by_gradient():
# def set_colors_by_radial_gradient():
# def set_submobject_colors_by_gradient():
# def set_submobject_colors_by_radial_gradient():
# def to_original_color():
# # used by default for fade()ing
# def fade_to_no_recurse():
# def fade_to():
# def fade_no_recurse():
# def fade():
# def get_color():
# def save_state():
# def restore():
# def reduce_across_dimension():
#        # Note, this default means things like empty VGroups
# def nonempty_submobjects():
# def get_merged_array():
# def get_all_points():
# def get_points_defining_boundary():
# def get_num_points():
# def get_critical_point():
# def get_edge_center():
# def get_corner():
# def get_center():
# def get_center_of_mass():
# def get_boundary_point():
# def get_top():
# def get_bottom():
# def get_right():
# def get_left():
# def get_zenith():
# def get_nadir():
# def length_over_dim():
# def get_width():
# def get_height():
# def get_depth():
# def point_from_proportion():
# def __getitem__():
# def __iter__():
# def __len__():
# def get_group_class():
# def split():
# def submobject_family():
# def family_members_with_points():
# def arrange_submobjects():
# def arrange_submobjects_in_grid():
# def sort_submobjects():
# def shuffle_submobjects():
# def print_submobject_family():
# def align_data():
# def get_point_mobject():
# def align_points():
# def align_points_with_larger():
# def align_submobjects():
# def null_point_align():
# def push_self_into_submobjects():
# def add_n_more_submobjects():
# def repeat_submobject():
# def interpolate(self, mobject1, mobject2,
# def interpolate_color():
# def become_partial():
# def pointwise_become_partial():
