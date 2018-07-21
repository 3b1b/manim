from big_ol_pile_of_manim_imports import *
from collections import OrderedDict as OrderedDict
import copy

LABELED_NODE_FACTOR = 7
UNLABELED_NODE_RADIUS = 0.1
LABELED_NODE_RADIUS = LABELED_NODE_FACTOR * UNLABELED_NODE_RADIUS
HEIGHT_RELATIVE_TO_NODE = [0, 0.23, 0.23, 0.23]

class Node(Component):
    CONFIG = {
        "fill_opacity": 0.0,
        "color": BLACK,
    }
    def __init__(self, point, labels=None, mobject=None,
            scale_factor=1, **kwargs):
        Component.__init__(self, point, labels=labels, mobject=mobject,
                scale_factor=scale_factor, **kwargs)

    def __str__(self):
        return "Node(center=({}, {}))".format(*self.mobject.get_center()[:2])
    __repr__ = __str__

    @staticmethod
    def assert_primitive(point):
        try:
            assert type(point) == np.ndarray or type(point) == tuple
            assert len(point) == 3
        except: import ipdb; ipdb.set_trace(context=7)

    def make_key(self, point):
        return point

    def create_mobject(self, point, mobject=None, labels=None, **kwargs):
        if mobject is not None:
            return mobject.move_to(point)
        else:
            if "radius" in kwargs:
                radius = kwargs["radius"]
                del kwargs["radius"]
            elif labels is not None:
                radius = LABELED_NODE_RADIUS * self.scale_factor
            else:
                radius = UNLABELED_NODE_RADIUS
            ret = Circle(radius=radius, **kwargs).move_to(point)

            if labels is not None:
                color = None
                for label in labels:
                    if len(label) == 3 and "color" in label[2]:
                        color = label[2]["color"]
                if color is not None:
                    ret.set_color(color)
            return ret

    def update(self, dic):
        ret = []
        # update labels
        labels = OrderedDict()
        for key in dic.keys():
            if key == "variable":
                labels["variable"] = dic["variable"]
            elif key == "dist":
                labels["dist"] = dic["dist"]
            elif key == "parent":
                labels["parent"] = dic["parent"]
        if labels:
            ret.extend(self.set_labels(labels))

        # set parameters from dic
        if "factor" in dic:
            factor = dic["factor"]
        elif self.mobject.radius < 0.5 and len(self.labels) > 0:
            factor = LABELED_NODE_FACTOR * self.scale_factor
        elif self.mobject.radius > 0.1 and len(self.labels) == 0:
            factor = 1. / LABELED_NODE_FACTOR
        else:
            factor = 1
        radius = self.mobject.radius * factor

        color = dic.get("color", None)
        if color is None:
            color = self.color

        # update mobject
        new_mob = self.create_mobject(
            self.key,
            radius=radius,
            color=color,
            stroke_width=self.stroke_width,
        ).move_to(self.mobject.get_center())
        ret.extend([ReplacementTransform(self.mobject, new_mob, parent=self)])
        self.mobject = new_mob

        return ret

    def enlarge(self, **kwargs):
        color = None
        if "factor" in kwargs:
            factor = kwargs["factor"]
        elif "shrink" in kwargs and kwargs["shrink"] == True:
            factor = 1./(LABELED_NODE_FACTOR * self.scale_factor)
        else:
            factor = (LABELED_NODE_FACTOR * self.scale_factor)
        if "color" in kwargs and kwargs["color"] is not None:
            color = kwargs["color"]
        else:
            color = self.get_color()
        return self.update(factor=factor, color=color)

    def get_label_scale_factor(self, label, num_labels):
        try:
            if label.get_height() > Integer(7).get_height():
                return self.scale_factor * \
                    Integer(7).get_height() / label.get_height()
            else:
                return self.scale_factor
        except:
            import ipdb; ipdb.set_trace(context=7)
    
    def get_label(self, name):
        if name in self.labels:
            return self.labels[name]
        else:
            return None

    def change_color(self, color):
        return self.update(color=color)

    """
    scales and places labels, removes new label from self.labels
    """
    def remove_label(self, label_name):
        self.remove(self.labels[label_name])
        anims = [Uncreate(self.labels[label_name])] 
        del self.labels[label_name]
        if len(self.labels) == 1:
            # there is only one old label
            for old_label in self.labels.values():
                old_label.generate_target()
                old_label.target.move_to(self.get_center())
                anims.append(MoveToTarget(old_label))
        else:
            num_labels = len(self.labels)
            vec = rotate_vector(RIGHT, np.pi / 2)
            vec *= self.mobject.get_height() / 4.5
            for old_label in self.labels.values():
                old_label.generate_target()
                old_label.target.move_to(self.get_center() + vec)
                anims.append(MoveToTarget(old_label))
                vec = rotate_vector(vec, 2 * np.pi / num_labels)
        return anims

    """
    scales and places labels, saves new label to self.labels
    """
    def set_label(self, name, label, animate=True, **kwargs):
        kwargs["animate"] = animate
        d = copy.deepcopy(self.labels)
        d[name] = label
        return self.set_labels(d, **kwargs)

    def set_labels(self, new_labels, scale_mobject=True, **kwargs):
        assert(type(new_labels) == OrderedDict)
        # make sure labels are different
        for old_label in self.labels.values():
            for new_label in new_labels.values():
                assert(id(old_label) != id(new_label))

        anims = []
        # delete labels
        for key, val in new_labels.items():
            if val is None:
                anims.append(Uncreate(self.labels[key]))
                self.remove(self.labels[key])
                del new_labels[key]
                del self.labels[key]

        # scale labels
        for label in new_labels.values():
            if type(label) == Arrow: continue # TODO
            scale_factor = self.get_label_scale_factor(label, len(new_labels))
            label.scale(scale_factor)

        # move
        if len(set(self.labels.keys() + new_labels.keys())) == 1:
            if len(new_labels) == 1:
                new_labels.values()[0].move_to(self.mobject.get_center())
            elif len(self.labels) == 1:
                key, val = self.labels.items()[0]
                new_labels[key] = val.copy().move_to(self.mobject.get_center())
            else:
                import ipdb; ipdb.set_trace(context=7)
        else:
            vec = rotate_vector(RIGHT, np.pi / 2)
            vec *= LABELED_NODE_RADIUS / 2.4 * self.scale_factor
            old_label_copies = OrderedDict()
            for name, label in self.labels.items():
                if name in new_labels:
                    new_labels[name].move_to(self.mobject.get_center() + vec)
                else:
                    old_label_copies[name] = label.copy().move_to(self.mobject.get_center() + vec)
                vec = rotate_vector(vec, 2 * np.pi / len(set(self.labels.keys() + new_labels.keys())))
            for name, label in new_labels.items():
                if name in self.labels:
                    pass
                else:
                    label.move_to(self.mobject.get_center() + vec)
                    vec = rotate_vector(vec, 2 * np.pi / len(set(self.labels.keys() + new_labels.keys())))
            for key in old_label_copies:
                if key not in new_labels:
                    new_labels[key] = old_label_copies[key]

        # animate / create
        if "animate" not in kwargs or kwargs["animate"]:
            for name in new_labels.keys():
                if name in self.labels:
                    anims.append(ReplacementTransform(self.labels[name],
                                                       new_labels[name],
                                                       parent=self))
                else:
                    anims.append(ShowCreation(new_labels[name]))
                    self.add(new_labels[name])
        else:
            for name in new_labels.keys():
                if name not in self.labels:
                    self.add(new_labels[name])
                else:
                    self.add(new_labels[name])
                    self.remove(self.labels[name])
        self.labels = new_labels
        return anims

    def set_parent_edge(self, pair):
        self.parent_edge = pair

    def get_parent_edge(self):
        if hasattr(self, "parent_edge"):
            return self.parent_edge
        else:
            return None
