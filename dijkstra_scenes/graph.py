from big_ol_pile_of_manim_imports import *
from collections import OrderedDict as OrderedDict
from collections import defaultdict as defaultdict
import numpy.linalg as la
from dijkstra_scenes.node import Node as Node
from dijkstra_scenes.edge import Edge as Edge

class Graph(Group):
    CONFIG = {
        "stroke_width": 2,
        "color": BLACK,
    }
    def __init__(self, nodes, edges, labels=None, directed=False,
            scale_factor=1, gradient=None, color_map=None, **kwargs):
        # typechecking
        for node in nodes:
            Node.assert_primitive(node)
        for edge in edges:
            Edge.assert_primitive(edge[:2])

        # mobject init
        config_copy = self.CONFIG.copy()
        config_copy.update(kwargs)
        kwargs = config_copy
        Group.__init__(self, **config_copy)

        # create submobjects
        self.nodes = {}
        self.edges = {}

        # create nodes
        for point in nodes:
            if labels is not None and point in labels:
                node = Node(point, labels=labels[point], scale_factor=scale_factor, **kwargs)
            else:
                node = Node(point, scale_factor=scale_factor, **kwargs)
            self.nodes[node.key] = node
            self.add(node)

        # create edges
        for edge in edges:
            u = edge[0]
            v = edge[1]
            u = self.nodes[u]
            v = self.nodes[v]
            if color_map is not None and color_map.has_key(edge):
                kwargs["color"] = color_map[edge]
            else:
                kwargs["color"] = self.color

            if labels is not None and labels.has_key((u.key,v.key)):
                edge_labels = labels[(u.key,v.key)]
            else:
                edge_labels = None

            if directed or len(edge) == 3 and edge[2].has_key("directed") and \
                    edge[2]["directed"]:
                edge_directed = True
            else:
                edge_directed = False

            if (v.key, u.key) in edges:
                curved = True
            else:
                curved = False

            edge = Edge(
                u, v,
                directed=edge_directed,
                labels=edge_labels,
                scale_factor=scale_factor,
                curved=curved,
                **kwargs
            )

            self.edges[edge.key] = edge
            self.add(edge)

    def shrink_nodes(self, *points, **kwargs):
        map(Node.assert_primitive, points)
        return self.enlarge_nodes(*points, shrink=True)

    """
    enlarges node, shrinks adjacent edges
    """
    def enlarge_nodes(self, *points, **kwargs):
        map(Node.assert_primitive, points)

        # enlarge nodes
        anims = []
        for point in points:
            if "color_map" in kwargs and point in kwargs["color_map"]:
                color = kwargs["color_map"][point]
            else:
                color = None
            anims.append(self.nodes[point].enlarge(color=color, **kwargs))

        # shrink edges
        seen = set()
        for point in points:
            for pair in self.get_adjacent_edges(point, use_direction=False):
                if pair in seen: continue
                edge = self.edges[pair]
                curve = self.edges.has_key((pair[1], pair[0]))
                if "parent_map" in kwargs and pair in map(lambda x: x[0], kwargs["parent_map"].values()):
                    edge.is_parent = True
                    anims.extend(edge.update_endpoints(stroke_width=4, rectangular_stem_width=0.05, color=kwargs["parent_map"][point][1], curve=curve))
                    self.set_node_parent_edge(point, pair)
                else:
                    anims.extend(edge.update_endpoints(curve=curve,
                        stroke_width=2, rectangular_stem_width=0.03))
                seen.add(pair)
        return anims

    def shrink_node(self, point):
        Node.assert_primitive(point)
        anims = []
        node = self.nodes[point]
        if len(node.labels) == 0:
            anims.extend(self.shrink_nodes(point))
        return anims

    def remove_node_labels(self, *labels):
        for label in labels:
            Node.assert_primitive(label[0])
        anims = []
        color_map = {}
        # remove labels
        for label in labels:
            anims.extend(self.nodes[label[0]].remove_label(label[1]))
            if len(label) == 3 and "color" in label[2]:
                color_map[label[0]] = label[2]["color"]

        # shrink nodes
        points = [label[0] for label in labels \
                  if len(self.nodes[label[0]].labels) == 0]
        anims.extend(self.enlarge_nodes(
            *points,
            shrink=True,
            color_map=color_map
        ))
        for point in color_map:
            if point not in points:
                anims.append(self.nodes[point].change_color(color_map[point]))
        return anims

    def set_node_labels(self, *labels):
        for label in labels:
            Node.assert_primitive(label[0])

        # enlarge nodes / color nodes / set thickness
        anims = []
        to_enlarge = []
        color_map = dict()
        parent_map = dict()
        for label in labels:
            point = label[0]
            if len(self.nodes[point].labels) == 0 and point not in to_enlarge:
                to_enlarge.append(point)
            if len(label) == 4 and "color" in label[3]:
                color_map[point] = label[3]["color"]
            if len(label) == 4 and "parent_edge" in label[3]:
                if "parent_edge_color" in label[3]:
                    parent_edge_color = label[3]["parent_edge_color"]
                else:
                    parent_edge_color = None
                parent_map[point] = (label[3]["parent_edge"], parent_edge_color)
                old_parent = self.get_node_parent_edge(point)
                if old_parent is not None:
                    self.edges[old_parent].is_parent = False
                    anims.append(self.set_edge_stroke_width(old_parent, 2, 0.03, color=BLACK))
        # color enlarged nodes and adjacent edges
        anims.extend(self.enlarge_nodes(
            *to_enlarge,
            color_map=color_map,
            parent_map=parent_map
        ))
        # color remaining edges
        for point, (pair, color) in parent_map.items():
            if self.edges[pair].is_parent == False:
                self.edges[pair].is_parent = True
                anims.append(self.set_edge_stroke_width(pair, 4, 0.05, color=color))
                self.set_node_parent_edge(point, parent_map[point][0])
        # color remaining nodes
        for point in color_map:
            if point not in to_enlarge:
                anims.extend([self.nodes[point].change_color(color_map[point])])

        # label nodes
        labels_dict = defaultdict(list)
        for label in labels:
            point, name, mobject = label[:3]
            labels_dict[point].append((name, mobject))
        for point in labels_dict:
            anims.extend(self.nodes[point].set_labels(*labels_dict[point]))
        return anims

    def get_node_label(self, point, name):
        Node.assert_primitive(point)
        return self.nodes[point].get_label(name)

    def node_has_label(self, point, label):
        Node.assert_primitive(point)
        return label in self.nodes[point].labels

    def set_edge_weight(self, pair, weight, stroke_width=None):
        Edge.assert_primitive(pair)
        weight_anim = self.edges[pair].set_labels(("weight", Integer(weight)))
        if stroke_width is not None:
            line_anim = self.edges[pair].set_stroke_width(stroke_width)
            return weight_anim + [line_anim]
        return weight_anim

    def set_edge_to_parent(self, pair, stroke_width=4, color=None):
        Edge.assert_primitive(pair)
        self.edges[pair].is_parent = True
        return self.set_stroke_width(pair, stroke_width, color=color)

    def set_edge_stroke_width(self, pair, stroke_width, rectangular_stem_width,
            color=None):
        Edge.assert_primitive(pair)
        return self.edges[pair].set_stroke_width(stroke_width,
                rectangular_stem_width, color=color)

    def get_edge_weight(self, pair):
        Edge.assert_primitive(pair)
        weight = self.edges[pair].get_weight()
        if weight:
            return weight.number

    def get_edge(self, pair):
        Edge.assert_primitive(pair)
        return self.edges[pair]

    def get_node(self, point):
        Node.assert_primitive(point)
        return self.nodes[point]

    def get_nodes(self):
        return self.nodes.keys()

    def get_edges(self):
        return self.edges.keys()

    def get_adjacent_nodes(self, point):
        Node.assert_primitive(point)
        adjacent_nodes = []
        for edge in self.get_adjacent_edges(point):
            (u, v) = edge
            if u == point:
                adjacent_nodes.append(v)
            else:
                adjacent_nodes.append(u)
        return adjacent_nodes

    def get_adjacent_edges(self, point, use_direction=False):
        Node.assert_primitive(point)
        adjacent_edges = []
        for edge in self.edges.keys():
            if edge in adjacent_edges:
                continue
            (u, v) = edge
            if use_direction and self.edges[edge].directed:
                if np.allclose(u, point):
                    adjacent_edges.append(edge) 
            else:
                if np.allclose(u, point) or np.allclose(v, point):
                    adjacent_edges.append(edge) 
        return adjacent_edges

    def get_opposite_node(self, pair, point):
        Node.assert_primitive(point)
        Edge.assert_primitive(pair)
        return self.edges[pair].opposite(point)

    def set_node_parent_edge(self, point, pair):
        Node.assert_primitive(point)
        Edge.assert_primitive(pair)
        self.nodes[point].set_parent_edge(pair)

    def get_node_parent_edge(self, point):
        return self.nodes[point].get_parent_edge()

    def change_edge_color(self, pair, color):
        return self.edges[pair].change_color(color)
