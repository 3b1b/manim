"""Mobjects used to represent mathematical graphs (think graph theory, not plotting)."""

__all__ = [
    "Graph",
]

from ..utils.color import BLACK
from .types.vectorized_mobject import VMobject
from .geometry import Dot, Line, LabeledDot
from .svg.tex_mobject import MathTex

from typing import Hashable, Union, List, Tuple

from copy import copy
import networkx as nx
import numpy as np


def _determine_graph_layout(
    nx_graph: nx.classes.graph.Graph,
    layout: Union[str, dict] = "spring",
    layout_scale: float = 2,
    layout_config: Union[dict, None] = None,
    partitions: Union[List[List[Hashable]], None] = None,
    root_vertex: Union[Hashable, None] = None,
) -> dict:
    automatic_layouts = {
        "circular": nx.layout.circular_layout,
        "kamada_kawai": nx.layout.kamada_kawai_layout,
        "planar": nx.layout.planar_layout,
        "random": nx.layout.random_layout,
        "shell": nx.layout.shell_layout,
        "spectral": nx.layout.spectral_layout,
        "partite": nx.layout.multipartite_layout,
        "tree": _tree_layout,
        "spiral": nx.layout.spiral_layout,
        "spring": nx.layout.spring_layout,
    }

    custom_layouts = ["random", "partite", "tree"]

    if layout_config is None:
        layout_config = {}

    if isinstance(layout, dict):
        return layout
    elif layout in automatic_layouts and layout not in custom_layouts:
        auto_layout = automatic_layouts[layout](
            nx_graph, scale=layout_scale, **layout_config
        )
        return dict([(k, np.append(v, [0])) for k, v in auto_layout.items()])
    elif layout == "tree":
        return _tree_layout(
            nx_graph,
            root_vertex=root_vertex,
            scale=layout_scale,
        )
    elif layout == "partite":
        if partitions is None or len(partitions) == 0:
            raise ValueError(
                "The partite layout requires the 'partitions' parameter to contain the partition of the vertices"
            )
        partition_count = len(partitions)
        for i in range(partition_count):
            for v in partitions[i]:
                if nx_graph.nodes[v] is None:
                    raise ValueError(
                        "The partition must contain arrays of vertices in the graph"
                    )
                nx_graph.nodes[v]["subset"] = i
        # Add missing vertices to their own side
        for v in nx_graph.nodes:
            if "subset" not in nx_graph.nodes[v]:
                nx_graph.nodes[v]["subset"] = partition_count

        auto_layout = automatic_layouts["partite"](
            nx_graph, scale=layout_scale, **layout_config
        )
        return dict([(k, np.append(v, [0])) for k, v in auto_layout.items()])
    elif layout == "random":
        # the random layout places coordinates in [0, 1)
        # we need to rescale manually afterwards...
        auto_layout = automatic_layouts["random"](nx_graph, **layout_config)
        for k, v in auto_layout.items():
            auto_layout[k] = 2 * layout_scale * (v - np.array([0.5, 0.5]))
        return dict([(k, np.append(v, [0])) for k, v in auto_layout.items()])
    else:
        raise ValueError(
            f"The layout '{layout}' is neither a recognized automatic layout, "
            "nor a vertex placement dictionary."
        )


def _tree_layout(
    G: nx.classes.graph.Graph,
    root_vertex: Union[Hashable, None],
    scale: float,
) -> dict:
    result = {root_vertex: np.array([0, 0, 0])}

    if not nx.is_tree(G):
        raise ValueError("The tree layout must be used with trees")
    if root_vertex is None:
        raise ValueError("The tree layout requires the root_vertex parameter")

    def _recursive_position_for_row(
        G: nx.classes.graph.Graph,
        result: dict,
        two_rows_before: List[Hashable],
        last_row: List[Hashable],
        current_height: float,
    ):
        new_row = []
        for v in last_row:
            for x in G.neighbors(v):
                if x not in two_rows_before:
                    new_row.append(x)

        new_row_length = len(new_row)

        if new_row_length == 0:
            return

        if new_row_length == 1:
            result[new_row[0]] = np.array([0, current_height, 0])
        else:
            for i in range(new_row_length):
                result[new_row[i]] = np.array(
                    [-1 + 2 * i / (new_row_length - 1), current_height, 0]
                )

        _recursive_position_for_row(
            G,
            result,
            two_rows_before=last_row,
            last_row=new_row,
            current_height=current_height + 1,
        )

    _recursive_position_for_row(
        G, result, two_rows_before=[], last_row=[root_vertex], current_height=1
    )

    height = max(map(lambda v: result[v][1], result))

    return dict(
        [
            (v, np.array([pos[0], 1 - 2 * pos[1] / height, pos[2]]) * scale / 2)
            for v, pos in result.items()
        ]
    )


class Graph(VMobject):
    """An undirected graph (that is, a collection of vertices connected with edges).

    Graphs can be instantiated by passing both a list of (distinct, hashable)
    vertex names, together with list of edges (as tuples of vertex names). See
    the examples below for details.

    .. note::

        This implementation uses updaters to make the edges move with
        the vertices.

    Parameters
    ----------

    vertices
        A list of vertices. Must be hashable elements.
    edges
        A list of edges, specified as tuples ``(u, v)`` where both ``u``
        and ``v`` are vertices.
    labels
        Controls whether or not vertices are labeled. If ``False`` (the default),
        the vertices are not labeled; if ``True`` they are labeled using their
        names (as specified in ``vertices``) via :class:`~.MathTex`. Alternatively,
        custom labels can be specified by passing a dictionary whose keys are
        the vertices, and whose values are the corresponding vertex labels
        (rendered via, e.g., :class:`~.Text` or :class:`~.Tex`).
    label_fill_color
        Sets the fill color of the default labels generated when ``labels``
        is set to ``True``. Has no effect for other values of ``labels``.
    layout
        Either one of ``"spring"`` (the default), ``"circular"``, ``"kamada_kawai"``,
        ``"planar"``, ``"random"``, ``"shell"``, ``"spectral"``, ``"spiral"``, ``"tree"``, and ``"partite"``
        for automatic vertex positioning using ``networkx``
        (see `their documentation <https://networkx.org/documentation/stable/reference/drawing.html#module-networkx.drawing.layout>`_
        for more details), or a dictionary specifying a coordinate (value)
        for each vertex (key) for manual positioning.
    layout_scale
        The scale of automatically generated layouts: the vertices will
        be arranged such that the coordinates are located within the
        interval ``[-scale, scale]``. Default: 2.
    layout_config
        Only for automatically generated layouts. A dictionary whose entries
        are passed as keyword arguments to the automatic layout algorithm
        specified via ``layout`` of``networkx``.
    vertex_type
        The mobject class used for displaying vertices in the scene.
    vertex_config
        Either a dictionary containing keyword arguments to be passed to
        the class specified via ``vertex_type``, or a dictionary whose keys
        are the vertices, and whose values are dictionaries containing keyword
        arguments for the mobject related to the corresponding vertex.
    edge_type
        The mobject class used for displaying edges in the scene.
    edge_config
        Either a dictionary containing keyword arguments to be passed
        to the class specified via ``edge_type``, or a dictionary whose
        keys are the edges, and whose values are dictionaries containing
        keyword arguments for the mobject related to the corresponding edge.

    Examples
    --------

    First, we create a small graph and demonstrate that the edges move
    together with the vertices.

    .. manim:: MovingVertices

        class MovingVertices(Scene):
            def construct(self):
                vertices = [1, 2, 3, 4]
                edges = [(1, 2), (2, 3), (3, 4), (1, 3), (1, 4)]
                g = Graph(vertices, edges)
                self.play(ShowCreation(g))
                self.wait()
                self.play(g[1].animate.move_to([1, 1, 0]),
                          g[2].animate.move_to([-1, 1, 0]),
                          g[3].animate.move_to([1, -1, 0]),
                          g[4].animate.move_to([-1, -1, 0]))
                self.wait()

    There are several automatic positioning algorithms to choose from:

    .. manim:: GraphAutoPosition
        :save_last_frame:

        class GraphAutoPosition(Scene):
            def construct(self):
                vertices = [1, 2, 3, 4, 5, 6, 7, 8]
                edges = [(1, 7), (1, 8), (2, 3), (2, 4), (2, 5),
                         (2, 8), (3, 4), (6, 1), (6, 2),
                         (6, 3), (7, 2), (7, 4)]
                autolayouts = ["spring", "circular", "kamada_kawai",
                               "planar", "random", "shell",
                               "spectral", "spiral"]
                graphs = [Graph(vertices, edges, layout=lt).scale(0.5)
                          for lt in autolayouts]
                r1 = VGroup(*graphs[:3]).arrange()
                r2 = VGroup(*graphs[3:6]).arrange()
                r3 = VGroup(*graphs[6:]).arrange()
                self.add(VGroup(r1, r2, r3).arrange(direction=DOWN))

    Vertices can also be positioned manually:

    .. manim:: GraphManualPosition
        :save_last_frame:

        class GraphManualPosition(Scene):
            def construct(self):
                vertices = [1, 2, 3, 4]
                edges = [(1, 2), (2, 3), (3, 4), (4, 1)]
                lt = {1: [0, 0, 0], 2: [1, 1, 0], 3: [1, -1, 0], 4: [-1, 0, 0]}
                G = Graph(vertices, edges, layout=lt)
                self.add(G)

    The vertices in graphs can be labeled, and configurations for vertices
    and edges can be modified both by default and for specific vertices and
    edges.

    .. note::

        In ``edge_config``, edges can be passed in both directions: if
        ``(u, v)`` is an edge in the graph, both ``(u, v)`` as well
        as ``(v, u)`` can be used as keys in the dictionary.

    .. manim:: LabeledModifiedGraph
        :save_last_frame:

        class LabeledModifiedGraph(Scene):
            def construct(self):
                vertices = [1, 2, 3, 4, 5, 6, 7, 8]
                edges = [(1, 7), (1, 8), (2, 3), (2, 4), (2, 5),
                         (2, 8), (3, 4), (6, 1), (6, 2),
                         (6, 3), (7, 2), (7, 4)]
                g = Graph(vertices, edges, layout="circular", layout_scale=3,
                          labels=True, vertex_config={7: {"fill_color": RED}},
                          edge_config={(1, 7): {"stroke_color": RED},
                                       (2, 7): {"stroke_color": RED},
                                       (4, 7): {"stroke_color": RED}})
                self.add(g)

    You can also lay out a partite graph on columns by specifying
    a list of the vertices on each side and choosing the partite layout.

    .. note::

        All vertices in your graph which are not listed in any of the partitions
        are collected in their own partition and rendered in the rightmost column.

    .. manim:: PartiteGraph
        :save_last_frame:

        import networkx as nx

        class PartiteGraph(Scene):
            def construct(self):
                G = nx.Graph()
                G.add_nodes_from([0, 1, 2, 3])
                G.add_edges_from([(0, 2), (0,3), (1, 2)])
                graph = Graph(list(G.nodes), list(G.edges), layout="partite", partitions=[[0, 1]])
                self.play(ShowCreation(graph))

    The custom tree layout can be used to show the graph
    by distance from the root vertex. You must pass the root vertex
    of the tree.

    .. manim:: Tree

        from manim import *
        import networkx as nx

        class Tree(Scene):
            def construct(self):
                G = nx.Graph()

                G.add_node("ROOT")

                for i in range(5):
                    G.add_node("Child_%i" % i)
                    G.add_node("Grandchild_%i" % i)
                    G.add_node("Greatgrandchild_%i" % i)

                    G.add_edge("ROOT", "Child_%i" % i)
                    G.add_edge("Child_%i" % i, "Grandchild_%i" % i)
                    G.add_edge("Grandchild_%i" % i, "Greatgrandchild_%i" % i)

                self.play(ShowCreation(
                    Graph(list(G.nodes), list(G.edges), layout="tree", root_vertex="ROOT")))
    """

    def __init__(
        self,
        vertices: List[Hashable],
        edges: List[Tuple[Hashable, Hashable]],
        labels: bool = False,
        label_fill_color: str = BLACK,
        layout: Union[str, dict] = "spring",
        layout_scale: float = 2,
        layout_config: Union[dict, None] = None,
        vertex_type: "Mobject" = Dot,
        vertex_config: Union[dict, None] = None,
        edge_type: "Mobject" = Line,
        partitions: Union[List[List[Hashable]], None] = None,
        root_vertex: Union[Hashable, None] = None,
        edge_config: Union[dict, None] = None,
    ) -> None:
        VMobject.__init__(self)

        nx_graph = nx.Graph()
        nx_graph.add_nodes_from(vertices)
        nx_graph.add_edges_from(edges)
        self._graph = nx_graph

        self._layout = _determine_graph_layout(
            nx_graph,
            layout=layout,
            layout_scale=layout_scale,
            layout_config=layout_config,
            partitions=partitions,
            root_vertex=root_vertex,
        )

        if isinstance(labels, dict):
            self._labels = labels
        elif isinstance(labels, bool):
            if labels:
                self._labels = dict(
                    [(v, MathTex(v, fill_color=label_fill_color)) for v in vertices]
                )
            else:
                self._labels = dict()

        if self._labels and vertex_type is Dot:
            vertex_type = LabeledDot

        # build vertex_config
        if vertex_config is None:
            vertex_config = {}
        default_vertex_config = {}
        if vertex_config:
            default_vertex_config = dict(
                [(k, v) for k, v in vertex_config.items() if k not in vertices]
            )
        self._vertex_config = dict(
            [(v, vertex_config.get(v, copy(default_vertex_config))) for v in vertices]
        )
        for v, label in self._labels.items():
            self._vertex_config[v]["label"] = label

        self.vertices = dict(
            [(v, vertex_type(**self._vertex_config[v])) for v in vertices]
        )
        for v in self.vertices:
            self[v].move_to(self._layout[v])

        # build edge_config
        if edge_config is None:
            edge_config = {}
        default_edge_config = {}
        if edge_config:
            default_edge_config = dict(
                (k, v)
                for k, v in edge_config.items()
                if k not in edges and k[::-1] not in edges
            )
        self._edge_config = {}
        for e in edges:
            if e in edge_config:
                self._edge_config[e] = edge_config[e]
            elif e[::-1] in edge_config:
                self._edge_config[e] = edge_config[e[::-1]]
            else:
                self._edge_config[e] = copy(default_edge_config)

        self.edges = dict(
            [
                (
                    (u, v),
                    edge_type(
                        self[u].get_center(),
                        self[v].get_center(),
                        z_index=-1,
                        **self._edge_config[(u, v)],
                    ),
                )
                for (u, v) in edges
            ]
        )

        self.add(*self.vertices.values())
        self.add(*self.edges.values())

        def update_edges(graph):
            for (u, v), edge in graph.edges.items():
                edge.put_start_and_end_on(graph[u].get_center(), graph[v].get_center())

        self.add_updater(update_edges)

    def __getitem__(self: "Graph", v: Hashable) -> "Mobject":
        return self.vertices[v]

    def __repr__(self: "Graph") -> str:
        return f"Graph on {len(self.vertices)} vertices and {len(self.edges)} edges"

    @staticmethod
    def from_networkx(nxgraph: nx.classes.graph.Graph, **kwargs) -> "Graph":
        """Build a :class:`~.Graph` from a given ``networkx`` graph.

        Parameters
        ----------

        nxgraph
            A ``networkx`` graph.
        **kwargs
            Keywords to be passed to the constructor of :class:`~.Graph`.

        Examples
        --------

        .. manim:: ImportNetworkxGraph

            import networkx as nx

            nxgraph = nx.erdos_renyi_graph(14, 0.5)

            class ImportNetworkxGraph(Scene):
                def construct(self):
                    G = Graph.from_networkx(nxgraph, layout="spring", layout_scale=3.5)
                    self.play(ShowCreation(G))
                    self.play(*[G[v].animate.move_to(5*RIGHT*np.cos(ind/7 * PI) +
                                                     3*UP*np.sin(ind/7 * PI))
                                for ind, v in enumerate(G.vertices)])
                    self.play(Uncreate(G))

        """
        return Graph(list(nxgraph.nodes), list(nxgraph.edges), **kwargs)

    def change_layout(
        self,
        layout: Union[str, dict] = "spring",
        layout_scale: float = 2,
        layout_config: Union[dict, None] = None,
        partitions: Union[List[List[Hashable]], None] = None,
        root_vertex: Union[Hashable, None] = None,
    ) -> "Graph":
        """Change the layout of this graph.

        See the documentation of :class:`~.Graph` for details about the
        keyword arguments.

        Examples
        --------

        .. manim:: ChangeGraphLayout

            class ChangeGraphLayout(Scene):
                def construct(self):
                    G = Graph([1, 2, 3, 4, 5], [(1, 2), (2, 3), (3, 4), (4, 5)],
                              layout={1: [-2, 0, 0], 2: [-1, 0, 0], 3: [0, 0, 0],
                                      4: [1, 0, 0], 5: [2, 0, 0]}
                              )
                    self.play(ShowCreation(G))
                    self.play(G.animate.change_layout("circular"))
                    self.wait()
        """
        self._layout = _determine_graph_layout(
            self._graph,
            layout=layout,
            layout_scale=layout_scale,
            layout_config=layout_config,
            partitions=partitions,
            root_vertex=root_vertex,
        )
        for v in self.vertices:
            self[v].move_to(self._layout[v])
        return self
