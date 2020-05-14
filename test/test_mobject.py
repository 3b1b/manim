import copy
import random

import unittest
import numpy as np

from manimlib.mobject.mobject import Mobject

def __func__(mob):
    mob.name = "lambda"
def __dt_func__(mob, dt):
    mob.name = str(dt)

class MObjectTest(unittest.TestCase):
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
    # ---------- Positioning Tests ---------- #
    # ---------- Coloring Tests ---------- #
    # ---------- Mobject Comparision Tests ---------- #
