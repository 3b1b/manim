"""Mobjects used to represent mathematical graphs (think graph theory, not plotting)."""

__all__ = [
    "Graph",
]

from ..constants import UP
from ..utils.color import BLACK
from .types.vectorized_mobject import VMobject
from .geometry import Dot, Line, LabeledDot
from .svg.tex_mobject import MathTex

from typing import Hashable, Union, List, Tuple

from copy import copy
import networkx as nx
import numpy as np


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
        ``"planar"``, ``"random"``, ``"shell"``, ``"spectral"``, and ``"spiral"``
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
        edge_config: Union[dict, None] = None,
    ) -> None:
        VMobject.__init__(self)

        nx_graph = nx.Graph()
        nx_graph.add_nodes_from(vertices)
        nx_graph.add_edges_from(edges)
        self._graph = nx_graph

        automatic_layouts = {
            "circular": nx.layout.circular_layout,
            "kamada_kawai": nx.layout.kamada_kawai_layout,
            "planar": nx.layout.planar_layout,
            "random": nx.layout.random_layout,
            "shell": nx.layout.shell_layout,
            "spectral": nx.layout.spectral_layout,
            "spiral": nx.layout.spiral_layout,
            "spring": nx.layout.spring_layout,
        }

        if layout_config is None:
            layout_config = {}

        if isinstance(layout, dict):
            self._layout = layout
        elif layout in automatic_layouts and layout != "random":
            self._layout = automatic_layouts[layout](
                nx_graph, scale=layout_scale, **layout_config
            )
            self._layout = dict(
                [(k, np.append(v, [0])) for k, v in self._layout.items()]
            )
        elif layout == "random":
            # the random layout places coordinates in [0, 1)
            # we need to rescale manually afterwards...
            self._layout = automatic_layouts["random"](nx_graph, **layout_config)
            for k, v in self._layout.items():
                self._layout[k] = 2 * layout_scale * (v - np.array([0.5, 0.5]))
            self._layout = dict(
                [(k, np.append(v, [0])) for k, v in self._layout.items()]
            )
        else:
            raise ValueError(
                f"The layout '{layout}' is neither a recognized automatic layout, "
                "nor a vertex placement dictionary."
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

        for (u, v), edge in self.edges.items():

            def update_edge(e, u=u, v=v):
                e.set_start_and_end_attrs(self[u].get_center(), self[v].get_center())
                e.generate_points()

            update_edge(edge)
            edge.add_updater(update_edge)

    def __getitem__(self: "Graph", v: Hashable) -> "Mobject":
        return self.vertices[v]

    def __repr__(self: "Graph") -> str:
        return f"Graph on {len(self.vertices)} vertices and {len(self.edges)} edges"
