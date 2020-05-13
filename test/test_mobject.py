import copy
import random

import unittest
import numpy as np

from manimlib.mobject.mobject import Mobject

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

