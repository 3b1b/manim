import copy
import math
import random

import unittest
import numpy as np

from manimlib.constants import *
from manimlib.mobject.mobject import Mobject
import test.mobject_generator as mob_gen

def __func__(mob):
    mob.name = "lambda"
def __dt_func__(mob, dt):
    mob.name = str(dt)
def __x_func__(mob):
    mob.set_x(mob.get_x() + 1)

class MobjectTest(unittest.TestCase):
    def test_to_string(self):
        obj = Mobject()
        self.assertEqual(str(obj), "Mobject")
        obj = Mobject(name="dummy")
        self.assertEqual(str(obj), "dummy")

    # ---------- Edit Submobjects Tests ---------- #
    def test_add_self_fails(self):
        obj = Mobject()
        with self.assertRaises(Exception):
            obj.add(obj)

    def test_add_returns_self(self):
        obj = Mobject()
        self.assertEqual(obj, obj.add())

    def test_add_submobjects_singly(self):
        a, b, c, obj = Mobject(), Mobject(), Mobject(), Mobject()
        self.assertListEqual([], obj.submobjects)
        obj.add(a)
        self.assertListEqual([a], obj.submobjects)
        obj.add(b)
        self.assertListEqual([a, b], obj.submobjects)
        obj.add(c)
        self.assertListEqual([a, b, c], obj.submobjects)

    def test_add_submobjects_multiply(self):
        a, b, c, obj = Mobject(), Mobject(), Mobject(), Mobject()
        self.assertListEqual([], obj.submobjects)
        obj.add(a, b, c)
        self.assertListEqual([a, b, c], obj.submobjects)

    def test_add_exsisting_submobjects(self):
        a, b, c, obj = Mobject(), Mobject(), Mobject(), Mobject()
        obj.add(a, b, c)
        obj.add(b)
        self.assertListEqual([a, c, b], obj.submobjects)

    def test_add_self_to_back_fails(self):
        obj = Mobject()
        with self.assertRaises(Exception):
            obj.add_to_back(obj)

    def test_add_to_back_returns_self(self):
        obj = Mobject()
        self.assertEqual(obj, obj.add_to_back())

    # add to back is actually add to front...
    def test_add_to_back_singly(self):
        a, b, c, obj = Mobject(), Mobject(), Mobject(), Mobject()
        self.assertListEqual([], obj.submobjects)
        obj.add_to_back(a)
        self.assertListEqual([a], obj.submobjects)
        obj.add_to_back(b)
        self.assertListEqual([b, a], obj.submobjects)
        obj.add_to_back(c)
        self.assertListEqual([c, b, a], obj.submobjects)

    def test_add_to_back_multiply(self):
        a, b, c, obj = Mobject(), Mobject(), Mobject(), Mobject()
        self.assertListEqual([], obj.submobjects)
        obj.add_to_back(a, b, c)
        self.assertListEqual([a, b, c], obj.submobjects)

    def test_add_to_back_exsisting_submobject(self):
        a, b, c, obj = Mobject(), Mobject(), Mobject(), Mobject()
        obj.add(a, b, c)
        obj.add_to_back(b)
        self.assertListEqual([b, a, c], obj.submobjects)

    def test_remove_returns_self(self):
        obj = Mobject()
        self.assertEqual(obj, obj.remove())

    def test_remove_singly(self):
        a, b, c, obj = Mobject(), Mobject(), Mobject(), Mobject()
        obj.add(a, b, c)
        self.assertListEqual([a, b, c], obj.submobjects)
        obj.remove(a)
        self.assertListEqual([b, c], obj.submobjects)
        obj.remove(b)
        self.assertListEqual([c], obj.submobjects)
        obj.remove(c)
        self.assertListEqual([], obj.submobjects)

    def test_remove_multiply(self):
        a, b, c, obj = Mobject(), Mobject(), Mobject(), Mobject()
        obj.add(a, b, c)
        self.assertListEqual([a, b, c], obj.submobjects)
        obj.remove(a, b)
        self.assertListEqual([c], obj.submobjects)

    def test_remove_not_submobject(self):
        a, b, c, obj = Mobject(), Mobject(), Mobject(), Mobject()
        obj.add(a, b)
        obj.remove(c)
        self.assertListEqual([a, b], obj.submobjects)

    def test_get_array_attrs(self):
        obj = Mobject()
        self.assertEqual(["points"], obj.get_array_attrs())

    # ---------- Drawing Tests ---------- #

    # ---------- Update Tests ---------- #
    def test_update_returns_self(self):
        obj = Mobject()
        self.assertEqual(obj, obj.update())
    
    def test_update_suspended(self):
        obj = Mobject(name="obj")
        obj.updating_suspended = True
        obj.add_updater(__func__)
        obj.update()
        self.assertEqual("obj", str(obj))

    def test_update_dt(self):
        obj = Mobject()
        obj.add_updater(__dt_func__)
        obj.update(dt=0.1)
        self.assertEqual("0.1", str(obj))

    def test_update_no_dt(self):
        obj = Mobject()
        obj.add_updater(__func__)
        obj.update()
        self.assertEqual("lambda", obj.name)

    def test_update_children(self):
        a, b, c, obj = Mobject(), Mobject(), Mobject(), Mobject()
        a.add_updater(__func__)
        b.add_updater(__func__)
        c.add_updater(__func__)
        obj.add(a, b, c)
        obj.update()
        for sub in obj.submobjects:
            self.assertEqual("lambda", str(sub))

    def test_get_updaters(self):
        obj = Mobject()
        obj.add_updater(__func__)
        obj.add_updater(__func__)
        obj.add_updater(__func__)
        self.assertListEqual([__func__, __func__, __func__], obj.get_updaters())

    def test_get_dt_updaters(self):
        obj = Mobject()
        obj.add_updater(__func__)
        obj.add_updater(__dt_func__)
        obj.add_updater(__func__)
        self.assertListEqual([__dt_func__], obj.get_time_based_updaters())

    def test_has_dt_updater(self):
        obj = Mobject()
        obj.add_updater(__dt_func__)
        self.assertTrue(obj.has_time_based_updater())

    def test_has_no_dt_updater(self):
        obj = Mobject()
        obj.add_updater(__func__)
        self.assertFalse(obj.has_time_based_updater())

    def test_get_family_updater(self):
        a, b, c, obj = Mobject(), Mobject(), Mobject(), Mobject()
        obj.add(a, b, c)
        obj.add_updater(__func__)
        a.add_updater(__func__)
        b.add_updater(__func__)
        c.add_updater(__func__)
        self.assertListEqual([__func__, __func__, __func__, __func__], obj.get_family_updaters())

    def test_add_updater_returns_self(self):
        obj = Mobject()
        self.assertEqual(obj, obj.add_updater(__func__))

    def test_add_updater(self):
        obj = Mobject()
        self.assertListEqual([], obj.updaters)
        obj.add_updater(__func__)
        self.assertListEqual([__func__], obj.updaters)
        obj.add_updater(__dt_func__)
        self.assertListEqual([__func__, __dt_func__], obj.updaters)

    def test_add_updater_by_index(self):
        obj = Mobject()
        self.assertListEqual([], obj.updaters)
        obj.add_updater(__func__, 0)
        self.assertListEqual([__func__], obj.updaters)
        obj.add_updater(__dt_func__, 0)
        self.assertListEqual([__dt_func__, __func__], obj.updaters)
        obj.add_updater(__dt_func__, 1)
        self.assertListEqual([__dt_func__, __dt_func__, __func__], obj.updaters)

    def test_remove_updater_returns_self(self):
        obj = Mobject()
        self.assertEqual(obj, obj.remove_updater(__func__))

    def test_remove_updater(self):
        obj = Mobject()
        obj.add_updater(__func__)
        obj.add_updater(__dt_func__)
        obj.add_updater(__func__)
        self.assertListEqual([__func__, __dt_func__, __func__], obj.updaters)
        obj.remove_updater(__func__)
        self.assertListEqual([__dt_func__], obj.updaters)

    def test_remove_no_updater(self):
        obj = Mobject()
        obj.add_updater(__func__)
        self.assertListEqual([__func__], obj.updaters)
        obj.remove_updater(__dt_func__)
        self.assertListEqual([__func__], obj.updaters)

    def test_clear_updaters_returns_self(self):
        obj = Mobject()
        self.assertEqual(obj, obj.clear_updaters())

    def test_clear_updaters(self):
        obj = Mobject()
        obj.add_updater(__func__)
        obj.add_updater(__dt_func__)
        obj.add_updater(__func__)
        self.assertListEqual([__func__, __dt_func__, __func__], obj.updaters)
        obj.clear_updaters()
        self.assertListEqual([], obj.updaters)

    def test_clear_updaters_in_children(self):
        a, b, c, obj = Mobject(), Mobject(), Mobject(), Mobject()
        obj.add(a, b, c)
        obj.add_updater(__func__)
        a.add_updater(__func__)
        b.add_updater(__func__)
        c.add_updater(__func__)
        self.assertListEqual([__func__, __func__, __func__, __func__], obj.get_family_updaters())
        obj.clear_updaters()
        self.assertListEqual([], obj.get_family_updaters())

    def test_match_updaters_returns_self(self):
        obj1, obj2 = Mobject(), Mobject()
        self.assertEqual(obj1, obj1.match_updaters(obj2))

    def test_match_updater_1(self):
        a, b = Mobject(), Mobject()
        a.add_updater(__func__)
        a.add_updater(__dt_func__)
        self.assertListEqual([__func__, __dt_func__], a.updaters)
        self.assertListEqual([], b.updaters)
        b.match_updaters(a)
        self.assertListEqual([__func__, __dt_func__], a.updaters)
        self.assertListEqual([__func__, __dt_func__], b.updaters)

    def test_match_updater_2(self):
        a, b = Mobject(), Mobject()
        a.add_updater(__func__)
        a.add_updater(__dt_func__)
        self.assertListEqual([__func__, __dt_func__], a.updaters)
        self.assertListEqual([], b.updaters)
        a.match_updaters(b)
        self.assertListEqual([], a.updaters)
        self.assertListEqual([], b.updaters)

    def test_suspend_update(self):
        a, b, c = Mobject(), Mobject(), Mobject()
        a.add(b)
        a.updating_suspended = True
        b.updating_suspended = True
        c.updating_suspended = False
        a.suspend_updating()
        c.suspend_updating()
        self.assertTrue(a.updating_suspended)
        self.assertTrue(b.updating_suspended)
        self.assertTrue(c.updating_suspended)

    def test_resume_update(self):
        a, b, c = Mobject(), Mobject(), Mobject()
        a.add(b)
        a.updating_suspended = True
        b.updating_suspended = True
        c.updating_suspended = False
        a.resume_updating()
        c.resume_updating()
        self.assertFalse(a.updating_suspended)
        self.assertFalse(b.updating_suspended)
        self.assertFalse(c.updating_suspended)

    # ---------- Transformation Tests ---------- #
    def test_apply_to_family(self):
        obj = Mobject()
        obj.points = np.zeros((1, 3))
        self.assertEqual(0, obj.get_x())
        self.assertEqual(0, obj.get_y())
        self.assertEqual(0, obj.get_z())
        obj.apply_to_family(__x_func__)
        self.assertEqual(1, obj.get_x())
        self.assertEqual(0, obj.get_y())
        self.assertEqual(0, obj.get_z())

    def test_shift_returns_self(self):
        obj = Mobject()
        obj.points = np.array([[0, 0, 0]])
        self.assertEqual(obj, obj.shift(np.array([0, 0, 0])))

    def test_shift(self):
        a = random.Random().randint(-1000, 1000)
        b = random.Random().randint(-1000, 1000)
        c = random.Random().randint(-1000, 1000)
        x = random.Random().randint(-1000, 1000)
        y = random.Random().randint(-1000, 1000)
        z = random.Random().randint(-1000, 1000)
        obj = Mobject()
        obj.points = np.array([[x, y, z]])
        obj.shift(np.array([a, b, c]))
        np.testing.assert_array_equal(obj.points,
                np.array([[x + a, y + b, z + c]]))

    def test_shift_by_zero_property(self):
        gen = mob_gen.MobjectGenerator(max_depth = 0)
        obj = gen.next()
        og = obj.points
        obj.shift(np.zeros((1, 3)))
        np.testing.assert_array_equal(og, obj.points)

    def test_shift_negative_property(self):
        gen = mob_gen.MobjectGenerator(max_depth=0)
        obj = gen.next()
        og = copy.deepcopy(obj)
        obj.shift(np.full((1, 3), random.Random().randrange(-1000, -1)))
        np.testing.assert_array_less(obj.get_all_points(), og.get_all_points())

    def test_shift_positive_property(self):
        gen = mob_gen.MobjectGenerator(max_depth=0)
        obj = gen.next()
        og = copy.deepcopy(obj)
        obj.shift(np.full((1, 3), random.Random().randrange(1, 1000)))
        np.testing.assert_array_less(og.get_all_points(), obj.get_all_points())

    def test_scale_returns_self(self):
        obj = Mobject()
        obj.points = np.array([0, 0, 0])
        self.assertEqual(obj, obj.scale(1, about_point=np.array([0, 0, 0])))

    def test_scale(self):
        s = random.Random().randint(-1000, 1000)
        x = random.Random().randint(-1000, 1000)
        y = random.Random().randint(-1000, 1000)
        z = random.Random().randint(-1000, 1000)
        obj = Mobject()
        obj.points = np. array([[x, y, z]])
        obj.scale(s, about_point=np.array([0, 0, 0]))
        np.testing.assert_array_equal(obj.points,
                np.array([[x * s, y * s, z * s]]))

    def test_scale_property(self):
        gen = mob_gen.MobjectGenerator(max_depth=0)
        obj = gen.next()
        og = copy.deepcopy(obj)
        obj.scale(10)
        np.testing.assert_array_less(
                np.absolute(og.get_all_points()),
                np.absolute(obj.get_all_points()))

    def test_rotate_returns_self(self):
        a = random.Random().randint(-1000, 1000)
        x = random.Random().randint(-1000, 1000)
        y = random.Random().randint(-1000, 1000)
        z = random.Random().randint(-1000, 1000)
        obj = Mobject()
        obj.points = np.array([x, y, z])
        self.assertEqual(obj, obj.rotate(a, about_point=np.array([0, 0, 0])))

    def test_rotate(self):
        a = random.Random().randint(-1000, 1000)
        x = random.Random().randint(-1000, 1000)
        y = random.Random().randint(-1000, 1000)
        z = random.Random().randint(-1000, 1000)
        obj = Mobject()
        obj.points = np.array([[x, y, z]])
        obj.rotate(a, axis=np.array([0, 0, 1]), about_point=np.array([0, 0, 0]))
        np.testing.assert_array_equal(obj.points, np.array([[
            x * math.cos(a) - y * math.sin(a),
            x * math.sin(a) + y * math.cos(a),
            z]]))

    def test_stretch_returns_self(self):
        obj = Mobject()
        obj.points = np.zeros((1, 3))
        self.assertEqual(obj, obj.stretch(1, 0))

    def test_stretch_factor_1(self):
        obj = Mobject()
        obj.points = np.array([[1.0, 1.0, 1.0]])
        obj.stretch(1, 0)
        obj.stretch(1, 1)
        obj.stretch(1, 2)
        np.testing.assert_array_equal(obj.points, np.array([[1, 1, 1]]))
        
    def test_stretch_origin(self):
        obj = Mobject()
        obj.points = np.array([[0.0, 0.0, 0.0]])
        f = random.Random().randint(-1000, 1000)
        obj.stretch(f, 0)
        obj.stretch(f, 1)
        obj.stretch(f, 2)
        np.testing.assert_array_equal(obj.points, np.zeros((1, 3)))
        
    def test_stretch_factor_random(self):
        obj = Mobject()
        obj.points = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        f = random.Random().randint(-1000, 1000)
        obj.stretch(f, 0)
        obj.stretch(f, 1)
        obj.stretch(f, 2)
        f /= 2
        np.testing.assert_array_almost_equal(obj.points,
                np.array([[-f, -f, -f], [f, f, f]]),
                decimal=0)
        
    # ---------- Positioning Tests ---------- #
    def test_center_returns_self(self):
        obj = Mobject()
        obj.points = np.zeros((1, obj.dim))
        self.assertEqual(obj, obj.center())

    def test_center(self):
        x = random.Random().randint(-1000, 1000)
        y = random.Random().randint(-1000, 1000)
        z = random.Random().randint(-1000, 1000)
        obj = Mobject()
        obj.points = np.array([[x, y, z]])
        obj.center()
        np.testing.assert_array_equal(obj.points, np.zeros((1, 3)))

    def test_center_negative_bound_object(self):
        gen = mob_gen.MobjectGenerator(upper_bound=-1)
        obj = gen.next()
        og = copy.deepcopy(obj)
        obj.center()
        np.testing.assert_array_less(og.get_all_points(), obj.get_all_points())

    def test_center_positive_bound_object(self):
        gen = mob_gen.MobjectGenerator(lower_bound=1)
        obj = gen.next()
        og = copy.deepcopy(obj)
        obj.center()
        np.testing.assert_array_less(obj.get_all_points(), og.get_all_points())

    def test_align_on_border_returns_self(self):
        obj = Mobject()
        obj.points = np.zeros((1, 3))
        self.assertEqual(obj, obj.align_on_border(np.zeros(3)))

    def test_align_on_border(self):
        obj = Mobject()
        obj.points = np.zeros((1, 3))
        obj.align_on_border(np.array([0, 1, 0]))
        np.testing.assert_array_equal(obj.points, np.array([[
            0,
            FRAME_Y_RADIUS - DEFAULT_MOBJECT_TO_EDGE_BUFFER,
            0]]))

        obj.align_on_border(np.array([1, 0, 0]))
        np.testing.assert_array_equal(obj.points, np.array([[
            FRAME_X_RADIUS - DEFAULT_MOBJECT_TO_EDGE_BUFFER,
            FRAME_Y_RADIUS - DEFAULT_MOBJECT_TO_EDGE_BUFFER,
            0]]))

    # need more next to tests for branch coverage
    def test_next_to_returns_self(self):
        a, b = Mobject(), Mobject()
        a.points = np.array([[-1, 0, 0]])
        b.points = np.array([[1, 0, 0]])
        self.assertEqual(a, a.next_to(b))

    def test_next_to(self):
        a, b = Mobject(), Mobject()
        a.points = np.array([[-1, 0, 0]])
        b.points = np.array([[1, 0, 0]])
        a.next_to(b)
        np.testing.assert_array_equal(a.points,
                b.points + RIGHT * DEFAULT_MOBJECT_TO_MOBJECT_BUFFER)

    def test_shift_onto_screen_returns_self(self):
        obj = Mobject()
        obj.points = np.zeros((1, 3))
        self.assertEqual(obj, obj.shift_onto_screen())

    def test_shift_onto_screen_one(self):
        obj = Mobject()
        obj.points = np.zeros((1, 3))
        obj.shift_onto_screen()
        np.testing.assert_array_equal(obj.points, np.zeros((1, 3)))

    def test_shift_onto_screen_two(self):
        obj = Mobject()
        obj.points = np.array([[FRAME_X_RADIUS*2, 0, 0]])
        obj.shift_onto_screen()
        np.testing.assert_array_equal(obj.points, np.array([[
            FRAME_X_RADIUS - DEFAULT_MOBJECT_TO_EDGE_BUFFER, 0, 0]]))

    def test_is_off_screen_false(self):
        obj = Mobject()
        obj.points = np.zeros((1, 3))
        self.assertFalse(obj.is_off_screen())

    def test_is_off_screen_right(self):
        obj = Mobject()
        obj.points = np.array([[FRAME_X_RADIUS*2, 0, 0]])
        self.assertTrue(obj.is_off_screen())

    def test_is_off_screen_left(self):
        obj = Mobject()
        obj.points = np.array([[-FRAME_X_RADIUS*2, 0, 0]])
        self.assertTrue(obj.is_off_screen())

    def test_is_off_screen_up(self):
        obj = Mobject()
        obj.points = np.array([[0, FRAME_Y_RADIUS*2, 0]])
        self.assertTrue(obj.is_off_screen())

    def test_is_off_screen_down(self):
        obj = Mobject()
        obj.points = np.array([[0, -FRAME_Y_RADIUS*2, 0]])
        self.assertTrue(obj.is_off_screen())

    # ---------- Coloring Tests ---------- #
    # ---------- Mobject Comparision Tests ---------- #
