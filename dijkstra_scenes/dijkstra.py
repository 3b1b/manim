from animation.composition import LaggedStart
from animation.composition import Succession
from animation.creation import FadeIn, FadeOut
from animation.creation import ShowCreation
from animation.creation import Uncreate
from animation.creation import Write
from animation.indication import Indicate
from animation.movement import MoveAlongPath
from animation.specialized import TransformEquation
from animation.transform import ApplyMethod
from animation.transform import MoveToTarget
from animation.transform import ReplacementTransform
from animation.update import UpdateFromAlphaFunc
from collections import OrderedDict
from dijkstra_scenes.edge import Side
from dijkstra_scenes.graph import Graph
from mobject.functions import ParametricFunction
from mobject.geometry import Arrow
from mobject.geometry import Line, Dot
from mobject.mobject import Group
from mobject.mobject import interpolate_color
from mobject.numbers import Integer
from mobject.svg.tex_mobject import TexMobject
from mobject.svg.tex_mobject import TextMobject
from mobject.svg.brace import BraceLabel
from mobject.svg.tex_mobject import AlignatTexMobject
from mobject.svg.tex_mobject import CodeMobject
from mobject.svg.tex_mobject import SingleStringTexMobject
from mobject.types.vectorized_mobject import VGroup
from mobject.types.vectorized_mobject import VMobject
from scene.moving_camera_scene import MovingCameraScene
from utils.bezier import interpolate
from utils.rate_functions import there_and_back_with_pause
from utils.rate_functions import wiggle
from utils.save import save_state, load_previous_state
from utils.space_ops import rotate_vector
import constants as const
import numpy as np
import random
import sys
INFTY_COLOR = const.BLACK
DEFAULT_WIDTH = 2
SPT_WIDTH = 6
SPT_COLOR = const.VIOLET
QUEUE_COLOR = const.MAGENTA
RELAXATION_COLOR = const.ORANGE
LINE_HEIGHT = 0.3
CURSOR_COLOR = const.BLUE


def place_arrows(block, group=None):
    if group is None:
        group = Group()
    for sub_block in block.submobjects:
        if "\n" in sub_block.tex_string:
            place_arrows(sub_block, group)
        elif not sub_block.tex_string.startswith("def"):
            new_cursor = TexMobject("\\blacktriangleright") \
                .set_color(CURSOR_COLOR) \
                .set_height(LINE_HEIGHT) \
                .next_to(sub_block, const.LEFT)
            group.add(new_cursor)
    return group


def extend_arrow(G, u, v, color=None):
    u_v_vector = G.get_node(v).mobject.get_center() - \
        G.get_node(u).mobject.get_center()
    u_v_vector /= np.linalg.norm(u_v_vector)
    u_edge_point = G.get_node(u).mobject.get_center() + \
        u_v_vector * G.get_node(u).mobject.radius
    v_edge_point = G.get_node(v).mobject.get_center() - \
        u_v_vector * G.get_node(v).mobject.radius
    arrow = Arrow(
        u_edge_point,
        u_edge_point,
        rectangular_stem_width=0.03,
        color=color,
    )
    return UpdateFromAlphaFunc(
        arrow,
        lambda a, t: a.put_start_and_end_on(
            u_edge_point,
            interpolate(u_edge_point, v_edge_point, t),
        ),
    ), arrow


def relax_neighbors(scene,
                    G,
                    parent,
                    show_relaxation=True,
                    arrows=False,
                    code=None,
                    cursor=None):
    if show_relaxation:
        saved_edge_attrs = {}
        for edge in G.get_adjacent_edges(parent):
            saved_edge_attrs[edge] = {
                "color": G.get_edge(edge).mobject.get_color(),
                "stroke_width": G.get_edge(edge).mobject.get_stroke_width(),
            }
        indicate_neighbors_updates = OrderedDict()
        for edge in G.get_adjacent_edges(parent):
            if edge != G.get_node_parent_edge(parent):
                indicate_neighbors_updates[edge] = OrderedDict([
                    ("color", RELAXATION_COLOR),
                    ("stroke_width", 4),
                ])
        if cursor is not None:
            cursor_anims = [
                ApplyMethod(cursor.shift, const.DOWN * LINE_HEIGHT)
            ]
        else:
            cursor_anims = []
        scene.play(
            *G.update_components(indicate_neighbors_updates) + cursor_anims)

    updates = OrderedDict()
    adj_edges = G.get_adjacent_edges(parent)
    any_relabel = False
    for edge in adj_edges:
        child = G.get_opposite_node(edge, parent)
        # find parent bound
        parent_label = G.get_node_label(parent, "dist")
        if type(parent_label) == Integer:
            parent_dist = int(parent_label.number)
        elif type(parent_label) == TexMobject:
            # starts with '\le '
            parent_dist = int(parent_label.tex_string[4:])
        new_bound = parent_dist + G.get_edge_weight(edge)

        relabel = False
        if not G.node_has_label(child, "dist"):
            relabel = True
            any_relabel = True
        else:
            # child node is already bounded
            old_bound = G.get_node_label(child, "dist")
            if type(old_bound) == Integer or len(old_bound.tex_string) == 1:
                # path length is already known
                if new_bound < old_bound.number:
                    updates[child] = OrderedDict([("color", const.RED)])
                continue

            # find child bound
            if old_bound.tex_string.endswith("\infty"):
                old_bound = float("inf")
            elif old_bound.tex_string.startswith("\le "):
                old_bound = int(old_bound.tex_string[4:])
            elif old_bound.tex_string.endswith("?"):
                old_bound = int(old_bound.tex_string[:-1])
                relabel = True
            else:
                print(
                    "Unexpected dist label {} on child".format(old_bound),
                    file=sys.stderr)
                breakpoint()

            if new_bound < old_bound:
                relabel = True
                any_relabel = True
        if relabel:
            updates[child] = OrderedDict([("dist",
                                           TexMobject(
                                               "\le {}".format(new_bound))),
                                          ("color", QUEUE_COLOR)])
            if arrows:
                arrow_vec = G.get_node(parent).mobject.get_center() - \
                    G.get_node(child).mobject.get_center()
                arrow_vec /= np.linalg.norm(arrow_vec)
                arrow = Arrow(
                    G.get_node(child).mobject.get_center(),
                    G.get_node(child).mobject.get_center() + arrow_vec)
                if G.get_node_parent_edge(child) is not None:
                    updates[G.get_node_parent_edge(child)] = OrderedDict([
                        ("stroke_width", 2),
                        ("color", const.BLACK),
                    ])
                updates[edge] = OrderedDict([
                    ("stroke_width", 4),
                    ("color", QUEUE_COLOR),
                ])
                updates[child]["parent_pointer"] = arrow
                G.set_node_parent_edge(child, edge)

    # highlight edges and place cursors
    if cursor is not None:
        relax_line_cursor = cursor.copy().next_to(
            code.submobjects[0].submobjects[3].submobjects[2].submobjects[1],
            const.LEFT)
        relax_block_cursors = place_arrows(code.submobjects[2])
        relax_block_cursors.remove(relax_block_cursors[2])
        if not any_relabel:
            relax_block_cursors.remove(relax_block_cursors[1])
            cursor_anims = [
                ShowCreation(relax_line_cursor),
                ShowCreation(relax_block_cursors, run_time=1),
            ]
        else:
            cursor_anims = [
                ShowCreation(relax_line_cursor),
                Succession(
                    ShowCreation,
                    relax_block_cursors,
                    {"run_time": 0.5},
                    ApplyMethod,
                    relax_block_cursors[1].shift,
                    const.DOWN * LINE_HEIGHT,
                    {"run_time": 0.5},
                ),
            ]
    else:
        cursor_anims = []
    scene.play(*G.update_components(updates) + cursor_anims)

    # restore edges and remove cursors
    if show_relaxation:
        restore_neighbors_updates = OrderedDict()
        for edge in G.get_adjacent_edges(parent):
            if str(G.get_edge(edge).mobject.color) == RELAXATION_COLOR:
                restore_neighbors_updates[edge] = OrderedDict([
                    ("color", saved_edge_attrs[edge]["color"]),
                    ("stroke_width", saved_edge_attrs[edge]["stroke_width"]),
                ])
        edge_restore_anims = G.update_components(restore_neighbors_updates)
    else:
        edge_restore_anims = []
    if cursor is not None:
        cursor_anims = [
            Uncreate(relax_line_cursor),
            Uncreate(relax_block_cursors, run_time=1),
        ]
    else:
        cursor_anims = []

    if edge_restore_anims or cursor_anims:
        scene.play(*edge_restore_anims + cursor_anims)
    else:
        scene.wait()

    if cursor is not None and not bounded_nodes(G):
        scene.play(Uncreate(cursor))


def bounded_nodes(G):
    def in_queue(v):
        if not G.node_has_label(v, "dist"):
            return False
        if G.get_node_label(v, "dist") is None:
            return True
        if type(G.get_node_label(v, "dist")) == TexMobject and \
                G.get_node_label(v, "dist").tex_string.startswith("\le"):
            return True

    ret = list(filter(in_queue, G.get_nodes()))
    return ret


def extract_node(scene, G, arrows=False, code=None, cursor=None):
    queue = bounded_nodes(G)
    if not queue:
        return None
    min_node = queue[0]
    if "\infty" in G.get_node_label(min_node, "dist").tex_string:
        min_bound = float("inf")
    elif "\le 0" == G.get_node_label(min_node, "dist").tex_string:
        min_bound = 0
    else:
        min_bound = int(G.get_node_label(min_node, "dist").tex_string[4:])
    for v in queue[1:]:
        if "\infty" in G.get_node_label(v, "dist").tex_string:
            cur_bound = float("inf")
        elif "\le 0" == G.get_node_label(min_node, "dist").tex_string:
            cur_bound = 0
        else:
            cur_bound = int(G.get_node_label(v, "dist").tex_string[4:])
        if cur_bound < min_bound:
            min_node = v
            min_bound = cur_bound
    updates = OrderedDict()
    updates[min_node] = OrderedDict([("dist", Integer(min_bound)),
                                     ("color", SPT_COLOR)])
    if arrows:
        parent_edge = G.get_node_parent_edge(min_node)
        if parent_edge is not None:
            updates[parent_edge] = OrderedDict([
                ("color", SPT_COLOR),
            ])
    if cursor is not None:
        if cursor not in scene.mobjects:
            cursor.next_to(code.submobjects[0].submobjects[3].submobjects[1],
                           const.LEFT)
            cursor_anims = [ShowCreation(cursor)]
        else:
            cursor.generate_target() \
                .next_to(code.submobjects[0].submobjects[3].submobjects[1],
                         const.LEFT)
            cursor_anims = [MoveToTarget(cursor)]
    else:
        cursor_anims = []
    scene.play(*G.update_components(updates) + cursor_anims)
    return min_node


class RunAlgorithm(MovingCameraScene):
    def first_try(self):
        # Draw borders
        self.add(
            Line(const.TOP + const.LEFT_SIDE, const.TOP + const.RIGHT_SIDE))
        self.add(
            Line(const.BOTTOM + const.LEFT_SIDE,
                 const.BOTTOM + const.RIGHT_SIDE))
        self.add(
            Line(const.LEFT_SIDE + const.BOTTOM, const.LEFT_SIDE + const.TOP))
        self.add(
            Line(const.RIGHT_SIDE + const.BOTTOM,
                 const.RIGHT_SIDE + const.TOP))
        self.add(Dot(const.ORIGIN))

        # draw the graph
        X_DIST = 4.3
        Y_DIST = 2.8
        nodes = [
            (-X_DIST, Y_DIST, 0),
            (0, Y_DIST, 0),
            (X_DIST, Y_DIST, 0),
            (-X_DIST, 0, 0),
            (0, 0, 0),
            (X_DIST, 0, 0),
            (-X_DIST, -Y_DIST, 0),
            (0, -Y_DIST, 0),
            (X_DIST, -Y_DIST, 0),
        ]
        edges = [
            (nodes[0], nodes[1]),
            (nodes[1], nodes[2]),
            (nodes[0], nodes[3]),
            (nodes[0], nodes[4]),
            (nodes[1], nodes[4]),
            (nodes[2], nodes[5]),
            (nodes[3], nodes[4]),
            (nodes[4], nodes[5]),
            (nodes[3], nodes[6]),
            (nodes[4], nodes[7]),
            (nodes[4], nodes[8]),
            (nodes[5], nodes[8]),
            (nodes[6], nodes[7]),
            (nodes[7], nodes[8]),
        ]
        G = Graph(nodes, edges)
        self.play(ShowCreation(G))

        # weight edges
        random.seed()
        weights = [4, 6, 5, 8, 3, 5, 1, 8, 2, 3, 4, 1, 2, 7]
        updates = OrderedDict()
        for i, edge in enumerate(edges):
            if weights[i]:
                edge_updates = OrderedDict([("weight", Integer(weights[i]))])
                updates[edge] = edge_updates
            else:
                rand = random.randint(1, 9)
                edge_updates = OrderedDict([("weight", Integer(rand))])
                updates[edge] = edge_updates
        self.play(*G.update_components(updates))

        # label s
        s = nodes[0]
        s_updates = OrderedDict([("variable", TexMobject("s"))])
        self.play(*G.update_component(s, s_updates))

        # set s to 0
        s_updates = OrderedDict([
            ("dist", Integer(0)),
            ("color", SPT_COLOR),
        ])
        self.play(*G.update_component(s, s_updates))

        # set neighbors to edge weights with question mark
        updates = OrderedDict()
        s_adj_edges = G.get_adjacent_edges(s)
        s_adj_nodes = G.get_adjacent_nodes(s)
        for pair, point in zip(s_adj_edges, s_adj_nodes):
            edge_weight = G.get_edge_weight(pair)
            updates[point] = OrderedDict(
                [("dist", TexMobject(str(edge_weight) + "?"))])
        self.play(*G.update_components(updates))

        # scroll down to show example
        self.play(
            MoveAlongPath(
                self.camera_frame,
                ParametricFunction(lambda t: (0, -const.FRAME_HEIGHT * t, 0)),
            ))

        self.G = G
        self.s = s
        self.nodes = nodes
        self.edges = edges
        self.X_DIST = X_DIST
        self.Y_DIST = Y_DIST
        save_state(self)

    def counterexample(self):
        self.__dict__.update(load_previous_state())

        # draw counterexample graph
        nodes = [
            (0, 0, 0),
            (4, 1.5, 0),
            (4, -1.5, 0),
        ]
        edges = [
            (nodes[0], nodes[1]),
            (nodes[0], nodes[2]),
            (nodes[1], nodes[2]),
        ]
        H = Graph(nodes, edges)
        H.shift(const.DOWN * const.FRAME_HEIGHT +
                const.LEFT * 0.5 * H.get_width())
        self.play(ShowCreation(H))

        # draw s and edge weights
        updates = OrderedDict()
        updates[nodes[0]] = OrderedDict([
            ("variable", TexMobject("s")),
            ("dist", Integer(0)),
            ("color", SPT_COLOR),
        ])
        updates[edges[0]] = OrderedDict([("weight", Integer(10))])
        updates[edges[1]] = OrderedDict([("weight", Integer(1))])
        updates[edges[2]] = OrderedDict([("weight", Integer(1))])
        self.play(*H.update_components(updates))

        # label nodes with tentative distances
        updates = OrderedDict()
        adj_edges = H.get_adjacent_edges(nodes[0])
        adj_nodes = H.get_adjacent_nodes(nodes[0])
        for pair, point in zip(adj_edges, adj_nodes):
            weight = H.get_edge_weight(pair)
            weight_mobject = TexMobject(str(weight) + "?")
            updates[point] = OrderedDict([("dist", weight_mobject)])
        self.play(*H.update_components(updates))

        # this is antipattern; possibly allow returning a copy edge?
        self.play(
            Indicate(
                H.edges[edges[0]].get_label("weight"),
                rate_func=there_and_back_with_pause,
                run_time=2))

        # switch to upper bound
        relax_neighbors(self, H, nodes[0], show_relaxation=False)

        # scroll back up
        initial_height = self.camera_frame.get_center()[1]
        self.play(
            MoveAlongPath(
                self.camera_frame,
                ParametricFunction(
                    lambda t: (0, initial_height + const.FRAME_HEIGHT * t, 0)))
        )

        save_state(self)

    def one_step(self):
        self.__dict__.update(load_previous_state())
        G = self.G
        s = self.s

        # set neighbors to upper bound
        adj_edges = G.get_adjacent_edges(s)
        relax_neighbors(self, G, s, show_relaxation=False)

        # highlight other edge weights
        adj_edges = G.get_adjacent_edges(s)
        min_edge = min(
            adj_edges, key=lambda x: G.get_edge(x).get_label("weight").number)
        anims = []
        for edge in adj_edges:
            if edge != min_edge:
                anims.extend([
                    Indicate(
                        G.edges[edge].get_label("weight"),
                        rate_func=there_and_back_with_pause,
                        run_time=2,
                    )
                ])
        self.play(*anims)

        # revert graph
        updates = OrderedDict()
        updates[s] = OrderedDict([("dist", None)])
        for node in G.get_adjacent_nodes(s):
            updates[node] = OrderedDict([("dist", None), ("color",
                                                          const.BLACK)])
        self.play(*G.update_components(updates))

        # set s to 0
        self.play(*G.update_component(
            s, OrderedDict([
                ("dist", Integer(0)),
                ("color", SPT_COLOR),
            ])))

        # set bound on neighbors
        relax_neighbors(self, G, s, show_relaxation=False)

        # scroll camera
        self.play(
            MoveAlongPath(
                self.camera_frame,
                ParametricFunction(lambda t: (const.FRAME_WIDTH * t, 0, 0))))

        self.G = G
        self.s = s
        save_state(self)

    def triangle_inequality(self):
        self.__dict__.update(load_previous_state())
        X_DIST = self.X_DIST

        x_color = SPT_COLOR
        y_color = QUEUE_COLOR
        z_color = RELAXATION_COLOR
        s = (-X_DIST * 0.60, 0 - 1, 0)
        v = (X_DIST * 0.60, 0 - 1, 0)
        u = (0, 3 - 1, 0)
        attrs = {
            s: OrderedDict([("variable", TexMobject("s"))]),
            u: OrderedDict([("variable", TexMobject("u"))]),
            v: OrderedDict([("variable", TexMobject("v"))]),
            (u, v): OrderedDict([("color", y_color)])
        }
        S = Graph([s, u, v], [(u, v)], attrs=attrs)
        S.to_edge(const.DOWN, initial_offset=self.camera_frame.get_center())

        self.play(
            FadeIn(S.get_node(s)),
            FadeIn(S.get_node(v)),
        )

        words = TextMobject(
            "\\large The shortest path from $s$ to $v$ ",
            "is at most as long as ",
            "the shortest path from $s$ to any node $u$ adjacent to $v$ ",
            "plus ",
            "the length of the edge connecting $u$ to $v$.",
        )
        words[0].set_color(z_color)
        words[2].set_color(x_color)
        words[4].set_color(y_color)
        words.set_width(const.FRAME_WIDTH - 1)
        words.to_edge(const.UP, initial_offset=self.camera_frame.get_center())

        arrow_anim1, arrow1 = extend_arrow(S, s, v, color=z_color)
        self.play(arrow_anim1, Write(words[0]))

        arrow_anim2, arrow2 = extend_arrow(S, s, u, color=x_color)
        self.play(
            FadeIn(S.get_node(u)),
            FadeIn(S.get_edge((u, v))),
            arrow_anim2,
            Write(VMobject(words[1], words[2])),
        )

        self.play(Write(VMobject(words[3], words[4])))
        self.wait()

        sx = Line(
            S.get_node(s).mobject.get_center(),
            S.get_node(u).mobject.get_center(),
            color=x_color,
        )
        sx_normal = rotate_vector(sx.get_vector(), np.pi / 2)
        bx = BraceLabel(sx, "x", sx_normal, buff=const.SMALL_BUFF)
        bx.brace.set_color(x_color, family=True)
        x = bx.label.set_color(x_color, family=True)

        sy = Line(
            S.get_node(u).mobject.get_center(),
            S.get_node(v).mobject.get_center(),
            color=y_color,
        )
        sy_normal = rotate_vector(sy.get_vector(), np.pi / 2)
        by = BraceLabel(sy, "y", sy_normal, buff=const.SMALL_BUFF)
        by.brace.set_color(y_color)
        y = by.label.set_color(y_color)

        sz = Line(
            S.get_node(s).mobject.get_center(),
            S.get_node(v).mobject.get_center(),
            color=z_color,
        )
        sz_normal = rotate_vector(sz.get_vector(), -np.pi / 2)
        bz = BraceLabel(sz, "z", sz_normal, buff=const.SMALL_BUFF)
        bz.brace.set_color(z_color)
        z = bz.label.set_color(z_color)

        triangle = Group(sx, sy, sz)
        brace_labels = Group(bx, by, bz)
        self.play(
            FadeIn(triangle),
            FadeOut(S),
            FadeOut(arrow1),
            FadeOut(arrow2),
        )

        self.play(
            bx.creation_anim(),
            by.creation_anim(),
            bz.creation_anim(),
        )
        self.wait()

        # TODO: convert this to use DynamicEquation
        x_len = 5
        y_len = 2
        eq1 = TexMobject("z \le x + y").move_to(sx.get_end() + const.RIGHT * 4)
        eq1[2].set_color(x_color)
        eq1[4].set_color(y_color)
        eq1[0].set_color(z_color)
        eq2 = TexMobject("z \le {} + {}".format(x_len, y_len))
        eq2[2].set_color(x_color)
        eq2[4].set_color(y_color)
        eq2[0].set_color(z_color)
        eq3 = TexMobject("z \le {}".format(x_len + y_len))
        eq3[2].set_color(QUEUE_COLOR)
        eq3[0].set_color(z_color)

        self.play(
            ReplacementTransform(x.copy(), eq1[2]),
            ReplacementTransform(y.copy(), eq1[4]),
            ReplacementTransform(z.copy(), eq1[0]),
            FadeIn(Group(eq1[1], eq1[3])),
        )
        self.wait()

        self.play(
            FadeOut(triangle),
            FadeOut(brace_labels),
            FadeIn(S),
            FadeIn(arrow1),
            FadeIn(arrow2),
        )

        updates = OrderedDict()
        updates[s] = OrderedDict([
            ("dist", Integer(0)),
            ("color", SPT_COLOR),
        ])
        updates[u] = OrderedDict([
            ("dist", Integer(x_len)),
            ("color", SPT_COLOR),
        ])
        updates[(u, v)] = OrderedDict([
            ("weight", Integer(y_len)),
        ])
        self.play(*S.update_components(updates) + [FadeOut(arrow1)])

        self.play(TransformEquation(eq1, eq2, "z \\\\le (.*) \\+ (.*)"))
        self.play(TransformEquation(eq2, eq3, "z \\\\le (.*)"))

        relax_neighbors(self, S, u)

        self.wait(2)

        self.play(
            MoveAlongPath(
                self.camera_frame,
                ParametricFunction(
                    lambda t: (const.FRAME_WIDTH * (1 - t), 0, 0))))

        save_state(self)

    def generalize(self):
        self.__dict__.update(load_previous_state())
        s = self.s
        G = self.G
        edges = self.edges

        # tighten bound for closest node
        min_node = extract_node(self, G)

        # relax neighbors of min node
        saved_state = []
        for node in G.get_adjacent_nodes(min_node):
            weight_label = G.get_node_label(node, "dist")
            if weight_label is not None:
                saved_state.append((node, weight_label.copy()))
            else:
                saved_state.append((node, weight_label))

        relax_neighbors(self, G, min_node)

        # Indicate shorter path
        anims = []
        anims.append(
            Indicate(G.edges[edges[2]].get_label("weight"), run_time=2))
        anims.append(
            Indicate(G.edges[edges[6]].get_label("weight"), run_time=2))
        self.play(*anims)

        # Revert the relaxation
        updates = OrderedDict()
        for node, saved_weight in saved_state:
            updates[node] = OrderedDict([("dist", saved_weight)])
        min_node_bound = G.get_node_label(min_node, "dist").number
        updates[min_node] = OrderedDict([
            ("dist", TexMobject(f"\\le {min_node_bound}")),
            ("color", QUEUE_COLOR),
        ])
        self.play(*G.update_components(updates))

        # highlight other edge weights
        adj_edges = G.get_adjacent_edges(s)
        min_edge = min(
            adj_edges, key=lambda x: G.get_edge(x).get_label("weight").number)
        anims = []
        for edge in adj_edges:
            if edge != min_edge:
                anims.extend([
                    Indicate(
                        G.edges[edge].get_label("weight"),
                        rate_func=there_and_back_with_pause,
                        run_time=2,
                    )
                ])
        self.play(*anims)

        min_node = extract_node(self, G)
        relax_neighbors(self, G, min_node)

        # scroll camera
        self.play(
            MoveAlongPath(
                self.camera_frame,
                ParametricFunction(
                    lambda t: (
                        const.FRAME_WIDTH * t,
                        -const.FRAME_HEIGHT * t,
                        0,
                    )
                )))
        save_state(self)

    def tightening(self):
        self.__dict__.update(load_previous_state())
        H_DIST = 3
        V_DIST = 1.5

        nodes = [
            (-H_DIST, V_DIST * 1.5, 0),
            (-H_DIST, V_DIST * 0.5, 0),
            (-H_DIST, -V_DIST * 0.5, 0),
            (-H_DIST, -V_DIST * 1.5, 0),
            (H_DIST, V_DIST * 1.5, 0),
            (H_DIST, V_DIST * 0.5, 0),
            (H_DIST, -V_DIST * 0.5, 0),
            (H_DIST, -V_DIST * 1.5, 0),
        ]
        edges = [
            (nodes[0], nodes[6]),
            (nodes[1], nodes[7]),
            (nodes[2], nodes[4]),
            (nodes[3], nodes[5]),
        ]
        attrs = {
            nodes[0]:
            OrderedDict([
                ("dist", Integer(5)),
                ("color", SPT_COLOR),
            ]),
            nodes[1]:
            OrderedDict([
                ("dist", Integer(3)),
                ("color", SPT_COLOR),
            ]),
            nodes[2]:
            OrderedDict([
                ("dist", Integer(4)),
                ("color", SPT_COLOR),
            ]),
            nodes[3]:
            OrderedDict([
                ("dist", Integer(6)),
                ("color", SPT_COLOR),
            ]),
            nodes[4]:
            OrderedDict([
                ("dist", TexMobject("\\le 6")),
                ("color", QUEUE_COLOR),
            ]),
            nodes[5]:
            OrderedDict([
                ("dist", TexMobject("\\le 11")),
                ("color", QUEUE_COLOR),
            ]),
            nodes[6]:
            OrderedDict([
                ("dist", TexMobject("\\le 8")),
                ("color", QUEUE_COLOR),
            ]),
            nodes[7]:
            OrderedDict([
                ("dist", TexMobject("\\le 7")),
                ("color", QUEUE_COLOR),
            ]),
            edges[0]:
            OrderedDict([
                ("weight", Integer(3)),
                ("label_location", 0.09),
                ("label_side", Side.COUNTERCLOCKWISE),
            ]),
            edges[1]:
            OrderedDict([
                ("weight", Integer(4)),
                ("label_location", 0.09),
                ("label_side", Side.COUNTERCLOCKWISE),
            ]),
            edges[2]:
            OrderedDict([
                ("weight", Integer(2)),
                ("label_location", 0.09),
            ]),
            edges[3]:
            OrderedDict([
                ("weight", Integer(5)),
                ("label_location", 0.09),
            ]),
        }
        G = Graph(nodes, edges, attrs=attrs) \
            .move_to(self.camera_frame.get_center())
        self.play(ShowCreation(G))
        self.wait(1)

        known_nodes = Group(*[G.get_node(point) for point in nodes[:4]])
        known_text = TextMobject("Known").next_to(known_nodes, const.UP)
        unknown_nodes = Group(*[G.get_node(point) for point in nodes[4:]])
        unknown_text = TextMobject("Unknown").next_to(unknown_nodes, const.UP)

        unknown_nodes.save_state()
        unknown_nodes.generate_target()
        unknown_nodes.target.set_color(
            interpolate_color(const.BLACK, const.WHITE, 0.9))
        self.play(MoveToTarget(unknown_nodes), Write(known_text))
        self.wait(1)

        known_nodes.save_state()
        known_nodes.generate_target()
        known_nodes.target.set_color(
            interpolate_color(const.BLACK, const.WHITE, 0.9))
        known_text.save_state()
        known_text.generate_target()
        known_text.target.set_color(
            interpolate_color(const.BLACK, const.WHITE, 0.9))
        unknown_nodes.target = unknown_nodes.saved_state
        self.play(
            MoveToTarget(known_nodes),
            MoveToTarget(known_text),
            MoveToTarget(unknown_nodes),
            Write(unknown_text),
        )
        self.wait(1)

        known_nodes.target = known_nodes.saved_state
        known_text.target = known_text.saved_state
        self.play(MoveToTarget(known_nodes), MoveToTarget(known_text))

        edges = Group(*[G.get_edge(edge).mobject for edge in edges])
        self.play(
            LaggedStart(
                ApplyMethod,
                edges,
                lambda m: (m.rotate_in_place, np.pi / 24),
                rate_func=wiggle,
                run_time=2,
            ))

        anims = []
        for node in nodes[4:]:
            bound = G.get_node_label(node, "dist")
            anims.append(Indicate(bound))
        self.play(*anims, rate_func=there_and_back_with_pause, run_time=2)

        self.play(*G.update_component(
            nodes[4],
            OrderedDict([
                ("dist", Integer(6)),
                ("color", SPT_COLOR),
            ])))

        self.wait(2)

        # scroll camera
        self.play(
            MoveAlongPath(
                self.camera_frame,
                ParametricFunction(
                    lambda t: (
                        const.FRAME_WIDTH * (1 - t),
                        const.FRAME_HEIGHT * (t - 1),
                        0,
                    )
                )))

        save_state(self)

    def first_run(self):
        self.__dict__.update(load_previous_state())
        G = self.G
        while bounded_nodes(G):
            min_node = extract_node(self, G)
            relax_neighbors(self, G, min_node)

        self.wait(2)
        save_state(self)

    def last_run(self):
        self.__dict__.update(load_previous_state())
        G = self.G
        s = self.s

        updates = OrderedDict()
        for node in G.get_nodes():
            updates[node] = OrderedDict([
                ("dist", None),
                ("color", const.BLACK),
            ])
        self.play(*G.update_components(updates))

        min_node = s
        self.play(*G.update_component(
            s, OrderedDict([
                ("dist", Integer(0)),
                ("color", SPT_COLOR),
            ])))

        relax_neighbors(self, G, s, arrows=True)
        while bounded_nodes(G):
            min_node = extract_node(self, G, arrows=True)
            relax_neighbors(self, G, min_node, arrows=True)
        self.wait(1)

        not_in_tree = VGroup()
        for node in G.get_nodes():
            if str(G.get_node(node).mobject.color) != SPT_COLOR:
                not_in_tree.add(G.get_node(node).mobject)
        for edge in G.get_edges():
            if str(G.get_edge(edge).mobject.color) != SPT_COLOR:
                not_in_tree.add(*G.get_edge(edge).submobjects)
        not_in_tree.generate_target() \
            .set_color(interpolate_color(const.BLACK, const.WHITE, 0.9))
        self.play(MoveToTarget(not_in_tree))
        self.wait(1)

        self.play(FadeOut(G))

        save_state(self)

    def directed_graph(self):
        self.__dict__.update(load_previous_state())
        DIST = 1.8
        nodes = [
            (-DIST * 1.2, DIST * 1.2, 0),
            (DIST * 1.2, DIST * 1.2, 0),
            (-2 * DIST, 0, 0),
            (0, 0, 0),
            (2 * DIST, 0, 0),
            (-DIST * 1.2, -DIST * 1.2, 0),
            (DIST * 1.2, -DIST * 1.2, 0),
        ]
        edges = [
            (nodes[1], nodes[0]),
            (nodes[0], nodes[2]),
            (nodes[3], nodes[0]),
            (nodes[3], nodes[1]),
            (nodes[4], nodes[1]),
            (nodes[0], nodes[5]),
            (nodes[5], nodes[0]),
            (nodes[1], nodes[6]),
            (nodes[6], nodes[1]),
            (nodes[5], nodes[2]),
            (nodes[3], nodes[5]),
            (nodes[3], nodes[6]),
            (nodes[6], nodes[4]),
            (nodes[5], nodes[6]),
        ]
        attrs = {
            edges[0]: OrderedDict([("weight", Integer(9))]),
            edges[1]: OrderedDict([("weight", Integer(4))]),
            edges[2]: OrderedDict([("weight", Integer(8))]),
            edges[3]: OrderedDict([("weight", Integer(2))]),
            edges[4]: OrderedDict([("weight", Integer(2))]),
            edges[5]: OrderedDict([("weight", Integer(2))]),
            edges[6]: OrderedDict([("weight", Integer(2))]),
            edges[7]: OrderedDict([("weight", Integer(5))]),
            edges[8]: OrderedDict([("weight", Integer(1))]),
            edges[9]: OrderedDict([("weight", Integer(4))]),
            edges[10]: OrderedDict([("weight", Integer(3))]),
            edges[11]: OrderedDict([("weight", Integer(9))]),
            edges[12]: OrderedDict([("weight", Integer(9))]),
            edges[13]: OrderedDict([("weight", Integer(8))]),
            (0, 0, 0): OrderedDict([("variable", TexMobject("s"))]),
        }
        G = Graph(nodes, edges, attrs=attrs, directed=True)
        self.play(ShowCreation(G))

        min_node = (0, 0, 0)
        self.play(*G.update_component(
            min_node,
            OrderedDict([
                ("dist", Integer(0)),
                ("color", SPT_COLOR),
            ])))
        while min_node is not None:
            relax_neighbors(self, G, min_node, arrows=True)
            min_node = extract_node(self, G, arrows=True)
        self.wait()

        # show spt
        not_in_tree = VGroup()
        for node in G.get_nodes():
            if str(G.get_node(node).mobject.color) != SPT_COLOR:
                not_in_tree.add(G.get_node(node).mobject)
        for edge in G.get_edges():
            if str(G.get_edge(edge).mobject.color) != SPT_COLOR:
                not_in_tree.add(*G.get_edge(edge).submobjects)
        not_in_tree.generate_target() \
            .set_color(interpolate_color(const.BLACK, const.WHITE, 0.9))
        self.play(MoveToTarget(not_in_tree))
        self.wait(1)

        self.play(FadeOut(G))
        save_state(self)

    def spt_vs_mst(self):
        self.__dict__.update(load_previous_state())
        DIST = 2.5

        nodes = [
            (0, 0, 0),
            (DIST, DIST, 0),
            (-DIST, DIST, 0),
        ]
        edges = [
            (nodes[0], nodes[1]),
            (nodes[0], nodes[2]),
            (nodes[1], nodes[2]),
        ]
        attrs = {
            nodes[0]: OrderedDict([("variable", TexMobject("s"))]),
            edges[0]: OrderedDict([("weight", Integer(2))]),
            edges[1]: OrderedDict([("weight", Integer(2))]),
            edges[2]: OrderedDict([("weight", Integer(1))]),
        }
        H_spt = Graph(nodes, edges, attrs=attrs).shift(const.DOWN)
        H_spt.generate_target().shift(3 * const.LEFT)
        H_mst = H_spt.deepcopy()
        H_mst.generate_target().shift(3 * const.RIGHT)

        # split graphs
        self.play(ShowCreation(H_spt))
        self.play(MoveToTarget(H_spt), MoveToTarget(H_mst))

        # show spt
        spt_updates = OrderedDict()
        spt_updates[nodes[0]] = OrderedDict([("color", SPT_COLOR)])
        spt_updates[nodes[1]] = OrderedDict([("color", SPT_COLOR)])
        spt_updates[nodes[2]] = OrderedDict([("color", SPT_COLOR)])
        spt_updates[edges[0]] = OrderedDict([
            ("color", SPT_COLOR),
            ("stroke_width", 4),
        ])
        spt_updates[edges[1]] = OrderedDict([
            ("color", SPT_COLOR),
            ("stroke_width", 4),
        ])
        spt_text = TextMobject(
            "Shortest Path Tree", hsize="85pt").next_to(H_spt, const.DOWN)
        self.play(*H_spt.update_components(spt_updates) + [Write(spt_text)])

        # show mst
        mst_updates = OrderedDict()
        mst_updates[nodes[0]] = OrderedDict([("color", SPT_COLOR)])
        mst_updates[nodes[1]] = OrderedDict([("color", SPT_COLOR)])
        mst_updates[nodes[2]] = OrderedDict([("color", SPT_COLOR)])
        mst_updates[edges[1]] = OrderedDict([
            ("color", SPT_COLOR),
            ("stroke_width", 4),
        ])
        mst_updates[edges[2]] = OrderedDict([
            ("color", SPT_COLOR),
            ("stroke_width", 4),
        ])
        mst_text = TextMobject(
            "Minimum Spanning Tree", hsize="85pt").next_to(H_mst, const.DOWN)
        self.play(*H_mst.update_components(mst_updates) + [Write(mst_text)])
        self.wait()

        # restore spt + mst
        spt_updates = OrderedDict()
        spt_updates[nodes[0]] = OrderedDict([("color", const.BLACK)])
        spt_updates[nodes[1]] = OrderedDict([("color", const.BLACK)])
        spt_updates[nodes[2]] = OrderedDict([("color", const.BLACK)])
        spt_updates[edges[0]] = OrderedDict([
            ("color", const.BLACK),
            ("stroke_width", 2),
        ])
        spt_updates[edges[1]] = OrderedDict([
            ("color", const.BLACK),
            ("stroke_width", 2),
        ])

        mst_updates = OrderedDict()
        mst_updates[nodes[0]] = OrderedDict([("color", const.BLACK)])
        mst_updates[nodes[1]] = OrderedDict([("color", const.BLACK)])
        mst_updates[nodes[2]] = OrderedDict([("color", const.BLACK)])
        mst_updates[edges[1]] = OrderedDict([
            ("color", const.BLACK),
            ("stroke_width", 2),
        ])
        mst_updates[edges[2]] = OrderedDict([
            ("color", const.BLACK),
            ("stroke_width", 2),
        ])

        self.play(
            FadeOut(mst_text), FadeOut(spt_text),
            *H_spt.update_components(spt_updates) +
            H_mst.update_components(mst_updates))

        H_spt.generate_target().shift(3 * const.RIGHT)
        H_mst.generate_target().shift(3 * const.LEFT)
        self.play(
            MoveToTarget(H_spt),
            MoveToTarget(H_mst),
        )
        self.remove(H_mst)

        updates = OrderedDict()
        updates[edges[0]] = OrderedDict([
            ("weight", Integer(2)),
            ("directed", True),
        ])
        updates[edges[1]] = OrderedDict([
            ("weight", Integer(1)),
            ("directed", True),
        ])
        updates[edges[2]] = OrderedDict([
            ("weight", Integer(-2)),
            ("directed", True),
        ])
        updates[nodes[0]] = OrderedDict([
            ("dist", Integer(0)),
            ("color", SPT_COLOR),
        ])
        self.play(*H_spt.update_components(updates))

        min_node = nodes[0]
        while min_node is not None:
            relax_neighbors(self, H_spt, min_node, arrows=True)
            min_node = extract_node(self, H_spt, arrows=True)

        self.play(FadeOut(H_spt))
        self.wait()
        save_state(self)

    def show_code(self):
        self.__dict__.update(load_previous_state())

        code = CodeMobject("""
        def dijkstra(G):
            initialize_source(s)
            bounded_vertices = min_queue(G.vertices)
            while bounded_vertices:
                u = bounded_vertices.extract_min()
                for v in G.neighbors(u):
                    relax_edge(G, u, v)

        def initialize_source(s):
            for v in G.vertices:
                if v == s:
                    v.dist = 0
                else:
                    v.dist = float("inf")

        def relax_edge(G, u, v):
            if v.dist > u.dist + G.weights(u, v):
                v.dist = u.dist + G.weights(u, v)
                v.parent = u
        """).set_width(0.5 * const.FRAME_WIDTH - 2 * const.MED_SMALL_BUFF) \
            .to_corner(const.UL, buff=const.MED_SMALL_BUFF)

        dijkstra_code = code.submobjects[0].copy()
        dijkstra_code.scale(
            (const.FRAME_WIDTH - 2 * const.MED_SMALL_BUFF) /
            dijkstra_code.get_width()) \
            .shift(self.camera_frame.get_center() - dijkstra_code.get_center())
        self.play(ShowCreation(dijkstra_code))

        self.play(ReplacementTransform(dijkstra_code, code.submobjects[0]))

        s = (0, 0, 0)
        nodes = [
            s,
            (1.5, 1.5, 0),
            (1.5, -1.5, 0),
            (-1.5, 1.5, 0),
            (-1.5, -1.5, 0),
        ]
        edges = [
            (nodes[0], nodes[1]),
            (nodes[0], nodes[2]),
            (nodes[0], nodes[3]),
            (nodes[0], nodes[4]),
        ]
        attrs = {
            s: OrderedDict([("variable", TexMobject("s"))]),
        }
        G = Graph(
            nodes, edges,
            attrs=attrs).shift(const.RIGHT * 0.25 * const.FRAME_WIDTH)

        updates = OrderedDict()
        for node in nodes:
            if node == s:
                updates[node] = OrderedDict([
                    ("dist", TexMobject("\le 0")),
                ])
            else:
                updates[node] = OrderedDict([
                    ("dist", TexMobject("\le\infty").set_color(INFTY_COLOR)),
                    ("color", INFTY_COLOR),
                ])

        # shift initialize header down and create next block
        top_line = code.submobjects[0].submobjects[1]
        bottom_line = code.submobjects[1].submobjects[0]
        top_initialize_line = top_line.copy()
        bottom_initialize_line = SingleStringTexMobject(
            bottom_line.tex_string[4:-1])
        bottom_initialize_line.submobjects = bottom_line.submobjects[3:-1]
        bottom_initialize_line_ends = VMobject()
        bottom_initialize_line_ends.submobjects = \
            bottom_line.submobjects[0:3] + [bottom_line.submobjects[-1]]
        self.play(
            ReplacementTransform(top_initialize_line, bottom_initialize_line))
        self.play(
            FadeIn(bottom_initialize_line_ends),
            ShowCreation(Group(*code.submobjects[1].submobjects[1:])),
        )

        # show the graph
        self.play(FadeIn(G))
        self.play(*G.update_components(updates))
        self.play(FadeOut(G))

        # shift relax header down and create next block
        top_line = code.submobjects[0] \
                       .submobjects[3] \
                       .submobjects[2] \
                       .submobjects[1]
        bottom_line = code.submobjects[2] \
                          .submobjects[0]
        top_relax_line = top_line.copy()
        bottom_relax_line = SingleStringTexMobject(
            bottom_line.tex_string[4:-1])
        bottom_relax_line.submobjects = bottom_line.submobjects[3:-1]
        bottom_relax_line_ends = VMobject()
        bottom_relax_line_ends.submobjects = bottom_line.submobjects[0:3] + [
            bottom_line.submobjects[-1]
        ]
        self.play(ReplacementTransform(top_relax_line, bottom_relax_line))
        self.play(
            FadeIn(bottom_relax_line_ends),
            ShowCreation(Group(*code.submobjects[2].submobjects[1:])),
        )

        u = (0, 0, 0)
        v = (3, 0, 0)
        nodes = [u, v]
        edges = [(u, v)]
        attrs = {
            u:
            OrderedDict([
                ("variable", TexMobject("u")),
                ("dist", Integer(3)),
                ("color", SPT_COLOR),
            ]),
            v:
            OrderedDict([
                ("variable", TexMobject("v")),
                ("dist", TexMobject("\le\infty")),
            ]),
            (u, v):
            OrderedDict([
                ("weight", Integer(2)),
            ]),
        }
        G = Graph(
            nodes, edges,
            attrs=attrs).shift(const.RIGHT * 0.15 * const.FRAME_WIDTH)

        self.play(FadeIn(G))
        updates = OrderedDict()
        relax_neighbors(self, G, u)

        # remove lower blocks
        self.play(
            FadeOut(G),
            FadeOut(code.submobjects[1]),
            FadeOut(code.submobjects[2]),
        )

        code2 = CodeMobject("""
        def dijkstra(G):
            initialize_source(s)
            bounded_vertices = min_queue(G.vertices)
            while bounded_vertices:
                u = bounded_vertices.extract_min()
                for v in G.neighbors(u):
                    relax_edge(G, u, v)

        class min_queue:
            def __init__(self, items):
                pass

            def extract_min(self):
                pass

            def decrease_key(self, item, new_value):
                pass
        """).set_width(0.5 * const.FRAME_WIDTH - 2 * const.MED_SMALL_BUFF) \
            .to_corner(const.UL, buff=const.MED_SMALL_BUFF)

        self.remove(code.submobjects[0])
        self.add(code2.submobjects[0])

        top_line = code2.submobjects[0] \
                        .submobjects[2]
        bottom_line = code2.submobjects[1] \
                           .submobjects[0]
        top_relax_line = Group(*top_line.copy().submobjects[17:26])
        bottom_relax_line = SingleStringTexMobject(
            bottom_line.tex_string[6:-1])
        bottom_relax_line.submobjects = bottom_line.submobjects[5:-1]
        bottom_relax_line_ends = VMobject()
        bottom_relax_line_ends.submobjects = bottom_line.submobjects[0:5] + [
            bottom_line.submobjects[-1]
        ]
        self.play(ReplacementTransform(top_relax_line, bottom_relax_line))
        self.play(
            FadeIn(bottom_relax_line_ends),
            ShowCreation(Group(*code2.submobjects[1].submobjects[1:])),
        )

        self.play(
            Indicate(code2.submobjects[0].submobjects[2]),
            Indicate(code2.submobjects[1].submobjects[1].submobjects[0]),
            rate_func=there_and_back_with_pause,
            run_time=2,
        )
        self.play(
            Indicate(code2.submobjects[0].submobjects[3].submobjects[1]),
            Indicate(code2.submobjects[1].submobjects[2].submobjects[0]),
            rate_func=there_and_back_with_pause,
            run_time=2,
        )
        self.play(
            Indicate(code2.submobjects[0].submobjects[3]
                     .submobjects[2].submobjects[1]),
            Indicate(code2.submobjects[1].submobjects[3].submobjects[0]),
            rate_func=there_and_back_with_pause,
            run_time=2,
        )

        self.play(FadeOut(code2.submobjects[1]))
        self.remove(code2)
        self.add(code.submobjects[0])
        self.play(FadeIn(Group(*code.submobjects[1:])))

        self.code = code
        save_state(self)

    def run_code(self):
        self.__dict__.update(load_previous_state())
        code = self.code

        s = (0, 2.6, 0)
        nodes = [
            (0, 2.6, 0),
            (-1.3, 1.3, 0),
            (1.3, 1.3, 0),
            (-2.6, 0, 0),
            (0, 0, 0),
            (2.6, 0, 0),
            (-1.3, -1.3, 0),
            (1.3, -1.3, 0),
            (0, -2.6, 0),
        ]
        edges = [
            ((0, 2.6, 0), (-1.3, 1.3, 0)),
            ((0, 2.6, 0), (1.3, 1.3, 0)),
            ((-1.3, 1.3, 0), (-2.6, 0, 0)),
            ((-1.3, 1.3, 0), (0, 0, 0)),
            ((1.3, 1.3, 0), (0, 0, 0)),
            ((1.3, 1.3, 0), (2.6, 0, 0)),
            ((-2.6, 0, 0), (-1.3, -1.3, 0)),
            ((0, 0, 0), (-1.3, -1.3, 0)),
            ((0, 0, 0), (1.3, -1.3, 0)),
            ((2.6, 0, 0), (1.3, -1.3, 0)),
            ((-1.3, -1.3, 0), (0, -2.6, 0)),
            ((1.3, -1.3, 0), (0, -2.6, 0)),
        ]
        attrs = {
            (0, 2.6, 0):
            OrderedDict([("variable", TexMobject("s"))]),
            ((0, 2.6, 0), (-1.3, 1.3, 0)):
            OrderedDict([("weight", Integer(4))]),
            ((0, 2.6, 0), (1.3, 1.3, 0)):
            OrderedDict([("weight", Integer(1))]),
            ((-1.3, 1.3, 0), (-2.6, 0, 0)):
            OrderedDict([("weight", Integer(5))]),
            ((-1.3, 1.3, 0), (0, 0, 0)):
            OrderedDict([("weight", Integer(4))]),
            ((1.3, 1.3, 0), (0, 0, 0)):
            OrderedDict([("weight", Integer(7))]),
            ((1.3, 1.3, 0), (2.6, 0, 0)):
            OrderedDict([("weight", Integer(2))]),
            ((-2.6, 0, 0), (-1.3, -1.3, 0)):
            OrderedDict([("weight", Integer(4))]),
            ((0, 0, 0), (-1.3, -1.3, 0)):
            OrderedDict([("weight", Integer(5))]),
            ((0, 0, 0), (1.3, -1.3, 0)):
            OrderedDict([("weight", Integer(1))]),
            ((2.6, 0, 0), (1.3, -1.3, 0)):
            OrderedDict([("weight", Integer(2))]),
            ((-1.3, -1.3, 0), (0, -2.6, 0)):
            OrderedDict([("weight", Integer(2))]),
            ((1.3, -1.3, 0), (0, -2.6, 0)):
            OrderedDict([("weight", Integer(1))]),
        }
        G = Graph(
            nodes, edges, attrs=attrs,
            scale_factor=0.8).shift(self.camera_frame.get_right() * 0.5)
        self.play(ShowCreation(G))

        dijkstra_cursor = TexMobject("\\blacktriangleright") \
            .set_color(CURSOR_COLOR) \
            .set_height(LINE_HEIGHT) \
            .next_to(code.submobjects[0].submobjects[1], const.LEFT)

        initialize_cursors = place_arrows(code.submobjects[1])

        self.wait()

        updates = OrderedDict()
        updates[s] = OrderedDict([
            ("dist", TexMobject("\le 0")),
        ])
        for node in nodes:
            if node != s:
                updates[node] = OrderedDict([
                    ("dist", TexMobject("\le\infty").set_color(INFTY_COLOR)),
                    ("color", INFTY_COLOR),
                ])

        self.play(*G.update_components(updates) + [
            Succession(
                ShowCreation,
                initialize_cursors,
                {"run_time": 1},
                Uncreate,
                initialize_cursors,
                {"run_time": 1},
            ),
            ShowCreation(dijkstra_cursor),
        ])
        self.play(
            ApplyMethod(dijkstra_cursor.shift, const.DOWN * 2 * LINE_HEIGHT))

        bounded_cursor = dijkstra_cursor.copy()
        while bounded_nodes(G):
            min_node = extract_node(
                self, G, arrows=True, code=code, cursor=bounded_cursor)
            relax_neighbors(
                self,
                G,
                min_node,
                arrows=True,
                code=code,
                cursor=bounded_cursor)
        self.play(Uncreate(dijkstra_cursor))

        self.G = G
        save_state(self)

    def analyze(self):
        self.__dict__.update(load_previous_state())
        G = self.G
        code = self.code

        self.play(FadeOut(G))

        runtime = AlignatTexMobject(
            "     &  \, &&       \,\, &&T_{\\text{build}(V)}      \\\\" +
            "+ \, &V \, &&\\cdot \,\, &&T_{\\text{extract\_min}}  \\\\" +
            "+ \, &E \, &&\\cdot \,\, &&T_{\\text{decrease\_key}} \\\\" +
            "+ \, &V \, &&       \,\, &&                          \\\\" +
            "+ \, &2 \, &&\\cdot \,\, &&E                         \\\\",
            columns=3,
        ).shift(const.RIGHT * 3)

        tbuild = VMobject()
        tbuild.submobjects = runtime.submobjects[0].submobjects[0:9]
        v_textractmin = VMobject()
        v_textractmin.submobjects = runtime.submobjects[0].submobjects[10:24]
        e_tdecreasekey = VMobject()
        e_tdecreasekey.submobjects = runtime.submobjects[0].submobjects[25:40]
        v = VMobject()
        v.submobjects = runtime.submobjects[0].submobjects[41]
        two_e = VMobject()
        two_e.submobjects = runtime.submobjects[0].submobjects[43:]

        # time to build
        indicated = code.submobjects[0] \
                        .submobjects[2] \
                        .copy().scale_in_place(1.2).set_color(const.YELLOW)
        regular = code.submobjects[0].submobjects[2].copy()
        self.play(
            ReplacementTransform(
                code.submobjects[0].submobjects[2],
                indicated,
                run_time=0.7,
            ))
        self.play(ReplacementTransform(indicated.copy(), tbuild))
        self.play(ReplacementTransform(indicated, regular, run_time=0.7))
        code.submobjects[0].submobjects[2] = regular  # restore code

        # time to extract
        indicated = code.submobjects[0] \
                        .submobjects[3] \
                        .submobjects[1] \
                        .copy().scale_in_place(1.2).set_color(const.YELLOW)
        regular = code.submobjects[0].submobjects[3].submobjects[1].copy()
        self.play(
            ReplacementTransform(
                code.submobjects[0].submobjects[3].submobjects[1],
                indicated,
                run_time=0.7,
            ))
        self.play(
            ReplacementTransform(indicated.copy(), v_textractmin),
            FadeIn(runtime.submobjects[0].submobjects[9]),
        )
        self.play(ReplacementTransform(indicated, regular, run_time=0.7))
        code.submobjects[0].submobjects[3].submobjects[1] = regular

        # time to relax
        indicated = code.submobjects[0] \
                        .submobjects[3] \
                        .submobjects[2] \
                        .submobjects[1] \
                        .copy().scale_in_place(1.2).set_color(const.YELLOW)
        regular = code.submobjects[0] \
                      .submobjects[3] \
                      .submobjects[2] \
                      .submobjects[1] \
                      .copy()
        self.play(
            ReplacementTransform(
                code.submobjects[0].submobjects[3]
                .submobjects[2].submobjects[1],
                indicated,
                run_time=0.7,
            ))
        self.play(
            ReplacementTransform(
                code.submobjects[0].submobjects[3]
                .submobjects[2].submobjects[1].copy(),
                e_tdecreasekey,
            ),
            FadeIn(runtime.submobjects[0].submobjects[24]),
        )
        self.play(ReplacementTransform(indicated, regular, run_time=0.7))
        code.submobjects[0] \
            .submobjects[3] \
            .submobjects[2] \
            .submobjects[1] = regular
        self.wait()

        # show
        textbook_runtime = TexMobject("O(T_\\text{build(V)} "
                                      "+ E \cdot T_\\text{decrease\_key} "
                                      "+ V \cdot T_\\text{extract\_min})")

        textbook_term_0 = VGroup(*textbook_runtime.submobjects[0]
                                 .submobjects[2:2 + 9])
        textbook_term_1 = VGroup(*textbook_runtime.submobjects[0]
                                 .submobjects[11:11 + 16])
        textbook_term_2 = VGroup(*textbook_runtime.submobjects[0]
                                 .submobjects[27:26 + 16])

        v_textractmin.add_to_back(runtime.submobjects[0].submobjects[9])
        e_tdecreasekey.add_to_back(runtime.submobjects[0].submobjects[24])
        self.play(
            ReplacementTransform(tbuild, textbook_term_0),
            ReplacementTransform(v_textractmin, textbook_term_2),
            ReplacementTransform(e_tdecreasekey, textbook_term_1),
            FadeIn(
                Group(*textbook_runtime.submobjects[0].submobjects[:2] +
                      [textbook_runtime.submobjects[0].submobjects[-1]])),
            FadeOut(code),
        )
        self.wait(2)

        self.runtime = VGroup(
            *textbook_runtime.submobjects[0]
            .submobjects[:2] + textbook_term_0.submobjects +
            textbook_term_1.submobjects + textbook_term_2.submobjects +
            [textbook_runtime.submobjects[0].submobjects[-1]])
        save_state(self)

    def compare_data_structures(self):
        self.__dict__.update(load_previous_state())
        runtime = self.runtime

        table = TextMobject(
            "\\begin{tabular}{ c | c }" +
            "  Data Structure & $O(T_\\text{build(V)} + "
            "E \cdot T_\\text{decrease\_key} + "
            "V \cdot T_\\text{extract\_min})$ \\\\ \\hline" +
            "  Array & $O(E + V \\cdot V)$ \\\\" +
            "  Binary Heap & $O(E \\log V + V \\log V)$ \\\\" +
            "  Fibonacci Heap & $O(E + V \\log V)$ \\\\" +
            "\\end{tabular}", ).set_width(const.FRAME_WIDTH - 0.1)
        n = Integer(0).shift(3 * const.DOWN)
        for mob in table.submobjects[0].submobjects:
            next_number = Integer(n.number + 1).shift(3 * const.DOWN)
            self.play(
                Indicate(mob),
                ReplacementTransform(n, next_number),
                run_time=0.7,
            )
            n = next_number
        table_lines = VGroup(
            table.submobjects[0].submobjects[13],
            table.submobjects[0].submobjects[57],
            table.submobjects[0].submobjects[63],
            table.submobjects[0].submobjects[82],
            table.submobjects[0].submobjects[110],
        )
        self.play(
            ReplacementTransform(
                runtime, VGroup(*table.submobjects[0]
                                .submobjects[14:14 + 43])),
            FadeIn(table_lines),
            FadeIn(Group(*table.submobjects[0].submobjects[:13])),
        )

        # Array
        array_word = VGroup(*table.submobjects[0].submobjects[58:58 + 5])
        table_array_time = VGroup(*table.submobjects[0].submobjects[64:64 + 8])
        array_time1 = TexMobject("O(V + E + V \cdot V)").move_to(
            table_array_time.get_center())
        array_time2 = TexMobject("O(E + V^2)").move_to(
            array_time1.get_center())
        array_time3 = TexMobject("O(V^2)").move_to(array_time2.get_center())
        self.play(FadeIn(array_word))
        self.play(Write(array_time1))
        self.play(
            TransformEquation(array_time1, array_time2,
                              "O\\((.*) \\+ (.*)\\)"))
        self.play(TransformEquation(array_time2, array_time3, "O\\((.*)\\)"))

        # Binary Heap
        binheap_word = VGroup(*table.submobjects[0].submobjects[72:72 + 10])
        table_binheap_time = VGroup(
            *table.submobjects[0].submobjects[83:83 + 14])
        binheap_time1 = TexMobject("O(V + E \log V + V \log V)").move_to(
            table_binheap_time.get_center())
        binheap_time2 = TexMobject("O((E + V) \log V)").move_to(
            const.DOWN + binheap_time1.get_center())
        self.play(FadeIn(binheap_word))
        self.play(Write(binheap_time1))
        x = TransformEquation(
            binheap_time1,
            binheap_time2,
            "(O)(\\()(V \\+ )(E) (\\\\log V) (\\+) (V) (\\\\log V)\\)",
            "(O)(\\()\\((E) (\\+) (V)\\) (\\\\log V)\\)",
            [(0, 0), (1, 1), (1, 2), (3, 3), (5, 4), (6, 5), (4, 7), (7, 7),
             (8, 8), (8, 6)],
        )
        self.play(x)

        # Fibonacci Heap
        fibo_word = VGroup(*table.submobjects[0].submobjects[97:110])
        table_fibo_time = VGroup(*table.submobjects[0].submobjects[111:])
        fibo_time1 = TexMobject("O(V + E + V \log V)") \
            .move_to(table_fibo_time.get_center())
        fibo_time2 = TexMobject("O(E + V \log V)") \
            .move_to(table_fibo_time.get_center())
        self.play(FadeIn(fibo_word))
        self.play(Write(fibo_time1))
        x = TransformEquation(fibo_time1, fibo_time2,
                              "O\\((.*) \\+ V \\\\log V\\)")
        self.play(x)
        self.play(
            Indicate(fibo_time2),
            rate_func=there_and_back_with_pause,
            run_time=2,
        )
        self.play(
            FadeOut(
                Group(
                    *table.submobjects[0].submobjects[14:14 + 43] +
                    table.submobjects[0].submobjects[:13],
                    table_lines,
                    array_word,
                    array_time3,
                    binheap_word,
                    binheap_time2,
                    fibo_word,
                    fibo_time2,
                )))

        self.wait(2)
        save_state(self)

    def construct(self):
        self.first_try()
        self.counterexample()
        self.one_step()
        self.triangle_inequality()
        self.generalize()
        self.tightening()
        self.first_run()
        self.last_run()
        self.directed_graph()
        self.spt_vs_mst()
        self.show_code()
        self.run_code()
        self.analyze()
        self.compare_data_structures()
