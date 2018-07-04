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
    def __init__(self, nodes, edges, labels=None, scale_factor=1, **kwargs):
        # typechecking
        for node in nodes:
            Node.assert_primitive(node)
        for edge in edges:
            Edge.assert_primitive(edge)

        # mobject init
        self.CONFIG.update(kwargs)
        kwargs = self.CONFIG
        Group.__init__(self, **kwargs)

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
            (u, v) = (edge[0], edge[1])
            u = self.nodes[u]
            v = self.nodes[v]
            if labels is not None and (u.key,v.key) in labels:
                edge = Edge(u, v, labels=labels[(u.key,v.key)], scale_factor=scale_factor, **kwargs)
            else:
                edge = Edge(u, v, scale_factor=scale_factor, **kwargs)
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
        anims = [self.nodes[point].enlarge(**kwargs) for point in points]

        # shrink edges
        seen = set()
        for point in points:
            for pair in self.get_adjacent_edges(point):
                if pair in seen: continue
                edge = self.edges[pair]
                if edge.get_weight():
                    new_edge = Edge(edge.start_node, edge.end_node,
                                    labels=[("weight", edge.get_weight().copy())],
                                    **self.CONFIG)
                else:
                    new_edge = Edge(edge.start_node, edge.end_node,
                                    **self.CONFIG)
                anims.append(ReplacementTransform(edge, new_edge, parent=self))
                self.edges[pair] = new_edge
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
        for point, label in labels:
            Node.assert_primitive(point)
        anims = []
        # remove labels
        for label in labels:
            anims.extend(self.nodes[label[0]].remove_label(label[1]))

        # shrink nodes
        points = [label[0] for label in labels \
                  if len(self.nodes[label[0]].labels) == 0]
        anims.extend(self.enlarge_nodes(*points, shrink=True))
        return anims

    def set_node_labels(self, *labels):
        for point, name, label in labels:
            Node.assert_primitive(point)
        anims = []

        # enlarge small nodes
        points = []
        for label in labels:
            if len(self.nodes[label[0]].labels) == 0 and \
                    label[0] not in points:
                points.append(label[0])
        anims.extend(self.enlarge_nodes(*points))

        # label all nodes
        labels_dict = defaultdict(list)
        for point, name, label in labels:
            labels_dict[point].append((name, label))
        for point in labels_dict:
            anims.extend(self.nodes[point].set_labels(*labels_dict[point]))
        return anims

    def get_node_label(self, point, name):
        Node.assert_primitive(point)
        try:
            return self.nodes[point].labels[name]
        except KeyError:
            sys.stderr.write("node at {} has no label {}".format(point, name))
            exit(1)

    def node_has_label(self, point, label):
        Node.assert_primitive(point)
        return label in self.nodes[point].labels

    def set_edge_weight(self, pair, weight):
        Edge.assert_primitive(pair)
        return self.edges[pair].set_weight(weight)

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

    def get_adjacent_edges(self, point):
        Node.assert_primitive(point)
        adjacent_edges = []
        for edge in self.edges.keys():
            (u, v) = edge
            if np.allclose(u, point) or np.allclose(v, point):
                if edge not in adjacent_edges:
                    adjacent_edges.append(edge) 
        return adjacent_edges

    def get_opposite_node(self, pair, point):
        Node.assert_primitive(point)
        Edge.assert_primitive(pair)
        return self.edges[pair].opposite(point)
