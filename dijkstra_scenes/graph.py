from big_ol_pile_of_manim_imports import *
from collections import OrderedDict as OrderedDict
from collections import defaultdict as defaultdict
import numpy.linalg as la
from dijkstra_scenes.node import Node as Node
from dijkstra_scenes.edge import Edge as Edge

class Graph(Group):
    CONFIG = {
        "stroke_width": 1,
    }
    def __init__(self, nodes, edges, labels=None):
        for node in nodes:
            assert(type(node) == tuple)
            assert(len(node) == 3)
            assert(np.allclose(node, np.round(node, 2)))
        for edge in edges:
            assert(type(edge) == tuple)
            assert(len(edge) == 2)
            assert(type(edge[0]) == type(edge[1]) == tuple)
            assert(len(edge[0]) == len(edge[1]) == 3)

        # self.nodes is a dictionary mapping (x, y) -> Node
        # self.edges is a dictionary mapping ((x1, y1), (x2, y2)) -> Edge
        self.nodes = {}
        self.edges = {}
        submobjects = []

        # add nodes
        for location in nodes:
            node = Node(location, labels=labels, **self.CONFIG)
            self.nodes[self.make_key(location)] = node
            submobjects.append(node)

        # add edges
        for edge in edges:
            (u, v) = (edge[0], edge[1])
            u = self.nodes[self.make_key(u)]
            v = self.nodes[self.make_key(v)]
            edge = Edge(u, v, **self.CONFIG)
            self.edges[(self.make_key(u.get_center()),
                        self.make_key(v.get_center()))] = edge
            submobjects.append(edge)

        Group.__init__(self, *submobjects)

    """
    converts a point to a dictionary key
    """
    def make_key(self, point):
        if type(point) == np.ndarray or \
           type(point) == tuple and len(point) == 3:
            return tuple(np.round(point, 2))
        elif type(point) == tuple and len(point) == 2:
            # round edge endpoints
            return (self.make_key(point[0]),
                    self.make_key(point[1]))

    def shrink_nodes(self, *points, **kwargs):
        return self.enlarge_nodes(*points, shrink=True)

    """
    enlarges node, shrinks adjacent edges
    """
    def enlarge_nodes(self, *points, **kwargs):
        # enlarge nodes
        anims = [self.nodes[self.make_key(point)].enlarge(**kwargs) for point in points]

        # shrink edges
        seen = set()
        for point in points:
            for pair in self.get_adjacent_edges(self.nodes[self.make_key(point)] \
                            .location):
                if pair in seen: continue
                edge = self.edges[self.make_key(pair)]
                if edge.get_weight():
                    new_edge = Edge(edge.start_node, edge.end_node,
                                    weight=edge.get_weight().copy(),
                                    **self.CONFIG)
                else:
                    new_edge = Edge(edge.start_node, edge.end_node,
                                    **self.CONFIG)
                anims.append(ReplacementTransform(edge, new_edge, parent=self))
                self.edges[self.make_key(pair)] = new_edge
                seen.add(pair)
        return anims

    def remove_node_label(self, point, label):
        node = self.nodes[self.make_key(point)]
        assert(label in node.labels)
        # remove label
        return node.remove_label(label)

    def shrink_node(self, point):
        anims = []
        node = self.nodes[self.make_key(point)]
        if len(node.labels) == 0:
            anims.extend(self.shrink_nodes(point))
        return anims

    def remove_node_labels(self, *labels):
        anims = []
        # remove labels
        for label in labels:
            anims.extend(self.nodes[self.make_key(label[0])].remove_label(label[1]))

        # shrink nodes
        points = [label[0] for label in labels \
                  if len(self.nodes[self.make_key(label[0])].labels) == 0]
        anims.extend(self.enlarge_nodes(*points, shrink=True))
        return anims

    def set_node_labels(self, *labels):
        anims = []

        # enlarge small nodes
        points = []
        for label in labels:
            if len(self.nodes[self.make_key(label[0])].labels) == 0 and \
                    label[0] not in points:
                points.append(label[0])
        anims.extend(self.enlarge_nodes(*points))

        ## label all nodes
        labels_dict = defaultdict(list)
        for point, name, label in labels:
            labels_dict[point].append((name, label))
        for point in labels_dict:
            anims.extend(self.nodes[self.make_key(point)].set_labels(*labels_dict[point]))
        return anims

    """
    scales node, sets label, and scales adjacent edges
    """
    def set_node_label(self, point, name, label):
        anims = []
        node = self.nodes[self.make_key(point)]
        if len(node.labels) == 0:
            anims.extend(self.enlarge_nodes(point))
        anims.extend(node.set_label(name, label))
        return anims

    def get_node_label(self, point, name):
        try:
            return self.nodes[self.make_key(point)].labels[name]
        except KeyError:
            sys.stderr.write("node at {} has no label {}".format(point, name))
            exit(1)

    def node_has_label(self, node, label):
        return label in self.nodes[node].labels

    def set_edge_weight(self, edge, weight):
        return self.edges[self.make_key(edge)].set_weight(weight)

    def get_edge_weight(self, edge):
        weight = self.edges[self.make_key(edge)].get_weight()
        if weight:
            return weight.number

    def get_edge(self, edge):
        return self.edges[self.make_key(edge)]

    def get_node(self, node):
        return self.nodes[self.make_key(node)]

    def get_nodes(self):
        return self.nodes.keys()

    def get_edges(self):
        return self.edges.keys()

    def get_adjacent_nodes(self, point):
        adjacent_nodes = []
        for edge in self.get_adjacent_edges(point):
            (u, v) = edge
            if u == point:
                adjacent_nodes.append(v)
            else:
                adjacent_nodes.append(u)
        return adjacent_nodes

    def get_adjacent_edges(self, point):
        adjacent_edges = []
        for edge in self.edges.keys():
            (u, v) = edge
            if np.allclose(u, point) or np.allclose(v, point):
                if edge not in adjacent_edges:
                    adjacent_edges.append(edge) 
        return adjacent_edges

    def get_opposite_node(self, edge, node):
        return self.edges[edge].opposite(node)
