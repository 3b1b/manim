from __future__ import print_function
from big_ol_pile_of_manim_imports import *
from dijkstra_scenes.graph import Graph
from dijkstra_scenes.dynamic_equation import DynamicEquation
import numpy.linalg as la
INFTY_COLOR = BLACK
DEFAULT_WIDTH = 2
SPT_WIDTH = 6
SPT_COLOR = VIOLET
QUEUE_COLOR = MAGENTA

def extend_arrow(G, u, v, color=None):
    u_v_vector = G.get_node(v).mobject.get_center() - \
                 G.get_node(u).mobject.get_center()
    u_v_vector /= la.norm(u_v_vector)
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
            u_edge_point + (v_edge_point - u_edge_point) * t,
        ),
    ), arrow

def relax_neighbors(G, parent, arrows=False):
    labels = []
    updates = OrderedDict()
    adj_edges = G.get_adjacent_edges(parent, use_direction=True)
    for edge in adj_edges:
        child = G.get_opposite_node(edge, parent)
        # the parent's path length is known
        parent_label = G.get_node_label(parent, "dist")
        if type(parent_label) == Integer:
            parent_dist = int(parent_label.number)
        elif type(parent_label) == TexMobject:
            # starts with '\le '
            parent_dist = int(parent_label.tex_string[4:])
        new_bound = parent_dist + G.get_edge_weight(edge)
        if G.node_has_label(child, "dist"):
            # node is already bounded
            old_bound = G.get_node_label(child, "dist")
            if type(old_bound) == Integer or len(old_bound.tex_string) == 1:
                # path length is already known
                continue
            relabel = False
            if old_bound.tex_string.endswith("\infty"):
                old_bound = float("inf")
            elif old_bound.tex_string.startswith("\le "):
                old_bound = int(old_bound.tex_string[4:])
            elif old_bound.tex_string.endswith("?"):
                old_bound = int(old_bound.tex_string[:-1])
                relabel = True
            else:
                print("Unexpected dist label {} on child".format(old_bound),
                        file=sys.stderr)
                import ipdb; ipdb.set_trace(context=7)
            if new_bound < old_bound:
                relabel = True
        else:
            relabel = True
        if relabel:
            updates[child] = OrderedDict([
                ("dist", TexMobject("\le {}".format(new_bound))),
                ("color", QUEUE_COLOR)
            ])
            if arrows:
                arrow_vec = G.get_node(parent).mobject.get_center() - \
                            G.get_node(child).mobject.get_center()
                arrow_vec /= la.norm(arrow_vec)
                arrow = Arrow(G.get_node(child).mobject.get_center(),
                              G.get_node(child).mobject.get_center() + arrow_vec)
                if G.get_node_parent_edge(child) is not None:
                    updates[G.get_node_parent_edge(child)] = OrderedDict([
                        ("stroke_width", 2),
                        ("color", BLACK),
                    ])
                updates[edge] = OrderedDict([
                    ("stroke_width", 4),
                    ("color", QUEUE_COLOR),
                ])
                updates[child]["parent_edge"] = edge
                updates[child]["parent_edge_color"] = QUEUE_COLOR
                updates[child]["parent_pointer"] = arrow
                G.set_node_parent_edge(child, edge)
    return G.update(updates)

def extract_node(G):
    bounded_nodes = filter(
        lambda v: G.node_has_label(v, "dist") and \
                type(G.get_node_label(v, "dist")) == TexMobject and \
                G.get_node_label(v, "dist").tex_string.startswith("\le"),
        G.get_nodes()
    )
    if not bounded_nodes:
        return None, None
    min_node  = bounded_nodes[0]
    if "\infty" in G.get_node_label(min_node, "dist").tex_string:
        min_bound = float("inf")
    else:
        min_bound = int(G.get_node_label(min_node, "dist").tex_string[4:])
    for v in bounded_nodes[1:]:
        if "\infty" in G.get_node_label(v, "dist").tex_string:
            cur_bound = float("inf")
        else:
            cur_bound = int(G.get_node_label(v, "dist").tex_string[4:])
        if cur_bound < min_bound:
            min_node = v
            min_bound = cur_bound
    return min_node, min_bound

class RunAlgorithm(MovingCameraScene):
    def first_try(self):
        # Draw borders
        top_border    = Line(TOP + LEFT_SIDE, TOP + RIGHT_SIDE)
        bottom_border = Line(BOTTOM + LEFT_SIDE, BOTTOM + RIGHT_SIDE)
        left_border   = Line(LEFT_SIDE + BOTTOM, LEFT_SIDE + TOP)
        right_border  = Line(RIGHT_SIDE + BOTTOM, RIGHT_SIDE + TOP)
        origin        = Dot(ORIGIN)
        self.add(top_border)
        self.add(bottom_border)
        self.add(left_border)
        self.add(right_border)
        #self.add(origin)

        # draw the graph
        X_DIST = 4.3
        Y_DIST = 2.8
        nodes = [
            (-X_DIST, Y_DIST , 0),
            ( 0     , Y_DIST , 0),
            ( X_DIST, Y_DIST , 0),
            (-X_DIST, 0      , 0),
            ( 0     , 0      , 0),
            ( X_DIST, 0      , 0),
            (-X_DIST, -Y_DIST, 0),
            ( 0     , -Y_DIST, 0),
            ( X_DIST, -Y_DIST, 0),
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
        weights = [2, 4, 3, 6, 3, 5, 5, 8, 1, 2, 4, 1, 2, 7]
        updates = OrderedDict()
        for i, edge in enumerate(edges):
            if weights[i]:
                edge_updates = OrderedDict([("weight", Integer(weights[i]))])
                updates[edge] = edge_updates
            else:
                rand = random.randint(1, 9)
                edge_updates = OrderedDict([("weight", Integer(rand))])
                updates[edge] = edge_updates
        self.play(*G.update(updates))

        # label s
        s = nodes[0]
        s_updates = OrderedDict([("variable", TexMobject("s"))])
        self.play(*G.single_update(s, s_updates))

        # set s to 0
        s_updates = OrderedDict([
            ("dist", Integer(0)),
            ("color", SPT_COLOR),
        ])
        self.play(*G.single_update(s, s_updates))

        # label neighbors with question marks
        updates = OrderedDict()
        for point in G.get_adjacent_nodes(s):
            updates[point] = OrderedDict([("dist", TexMobject("?"))])
        self.play(*G.update(updates))

        # set neighbors to edge weights with question mark
        updates = OrderedDict()
        s_adj_edges = G.get_adjacent_edges(s)
        s_adj_nodes = G.get_adjacent_nodes(s)
        for pair, point in zip(s_adj_edges, s_adj_nodes):
            edge_weight = G.get_edge_weight(pair)
            updates[point] = OrderedDict([
                ("dist", TexMobject(str(edge_weight) + "?"))])
        self.play(*G.update(updates))

        # scroll down to show example
        ShiftDown = lambda t: (0, -FRAME_HEIGHT * t, 0)
        self.play(MoveAlongPath(self.camera_frame,
                                ParametricFunction(ShiftDown)))

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
            (0,    0, 0),
            (4,  1.5, 0),
            (4, -1.5, 0),
        ]
        edges = [
            (nodes[0], nodes[1]),
            (nodes[0], nodes[2]),
            (nodes[1], nodes[2]),
        ]
        H = Graph(nodes, edges)
        H.shift(DOWN * FRAME_HEIGHT + LEFT * 0.5 * H.get_width())
        self.play(ShowCreation(H))

        # draw s and edge weights
        updates = OrderedDict()
        updates[nodes[0]] = OrderedDict([
            ("variable", TexMobject("s")),
            ("dist", Integer(0)),
            ("color", SPT_COLOR),
        ])
        updates[edges[0]] = OrderedDict([ ("weight", Integer(10)) ])
        updates[edges[1]] = OrderedDict([ ("weight", Integer(1))  ])
        updates[edges[2]] = OrderedDict([ ("weight", Integer(1))  ])
        self.play(*H.update(updates))

        # label nodes with tentative distances
        updates = OrderedDict()
        adj_edges = H.get_adjacent_edges(nodes[0])
        adj_nodes = H.get_adjacent_nodes(nodes[0])
        for pair, point in zip(adj_edges, adj_nodes):
            weight = H.get_edge_weight(pair)
            weight_mobject = TexMobject(str(weight) + "?")
            updates[point] = OrderedDict([("dist", weight_mobject)])
        self.play(*H.update(updates))

        # this is antipattern; possibly allow returning a copy edge?
        self.play(Indicate(H.edges[edges[0]].get_label("weight")))

        # switch to upper bound
        self.play(*relax_neighbors(H, nodes[0]))

        # scroll back up
        initial_height = self.camera_frame.get_center()[1]
        ShiftUp = lambda t: (0, initial_height + FRAME_HEIGHT * t, 0)
        self.play(MoveAlongPath(self.camera_frame,
                                ParametricFunction(ShiftUp)))

        save_state(self)

    def one_step(self):
        self.__dict__.update(load_previous_state())
        G = self.G
        s = self.s
        nodes = self.nodes
        edges = self.edges

        # set neighbors to upper bound
        adj_edges = G.get_adjacent_edges(s)
        self.play(*relax_neighbors(G, s))

        # tighten bound on min node
        min_node, min_bound = extract_node(G)
        min_node_updates = OrderedDict([
            ("dist", Integer(min_bound)),
            ("color", SPT_COLOR),
        ])
        self.play(*G.single_update(min_node, min_node_updates))

        # highlight other edge weights
        adj_edges = G.get_adjacent_edges(s)
        min_edge = min(adj_edges,
            key = lambda x: G.get_edge(x).get_label("weight").number)
        anims = []
        for edge in adj_edges:
            if edge != min_edge:
                anims.extend([Indicate(G.edges[edge].get_label("weight"))])
        self.play(*anims)

        # revert graph
        updates = OrderedDict()
        updates[s] = OrderedDict([("dist", None)])
        for node in G.get_adjacent_nodes(s):
            updates[node] = OrderedDict([("dist", None), ("color", BLACK)])
        self.play(*G.update(updates))

        # set s to 0
        self.play(*G.single_update(s, OrderedDict([
            ("dist", Integer(0)),
            ("color", SPT_COLOR),
        ])))

        # set bound on neighbors
        self.play(*relax_neighbors(G, s))

        # scroll camera
        ShiftRight = lambda t: (FRAME_WIDTH * t, 0, 0)
        self.play(MoveAlongPath(self.camera_frame,
                                ParametricFunction(ShiftRight)))

        self.G = G
        self.s = s
        save_state(self)

    def triangle_inequality(self):
        self.__dict__.update(load_previous_state())
        X_DIST = self.X_DIST
        Y_DIST = self.Y_DIST

        x_color = SPT_COLOR
        y_color = QUEUE_COLOR
        z_color = TEAL
        s = (-X_DIST * 0.60, 0 - 1, 0)
        v = ( X_DIST * 0.60, 0 - 1, 0)
        u = (             0, 3 - 1, 0)
        labels = {
            s: OrderedDict([("variable", TexMobject("s"))]),
            u: OrderedDict([("variable", TexMobject("u"))]),
            v: OrderedDict([("variable", TexMobject("v"))]),
            (u, v): OrderedDict([("color", y_color)])
        }
        S = Graph([s, u, v], [(u, v)], labels=labels)
        S.to_edge(DOWN, initial_offset=self.camera_frame.get_center())

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
        words.scale_to_fit_width(FRAME_WIDTH - 1)
        words.to_edge(UP, initial_offset=self.camera_frame.get_center())

        arrow_anim1, arrow1 = extend_arrow(S, s, v, color=z_color)
        self.play(arrow_anim1, Write(words[0]))

        arrow_anim2, arrow2 = extend_arrow(S, s, u, color=x_color)
        self.play(
            FadeIn(S.get_node(u)),
            FadeIn(S.get_edge((u, v))),
            arrow_anim2,
            Write(Group(words[1], words[2])),
        )

        self.play(Write(Group(words[3], words[4])))

        sx = Line(
            S.get_node(s).mobject.get_center(),
            S.get_node(u).mobject.get_center(),
            color=x_color,
        )
        sx_normal = rotate_vector(sx.get_vector(), np.pi/2)
        bx = BraceLabel(sx, "x", sx_normal, buff=SMALL_BUFF)
        bx.brace.set_color(x_color)
        x = bx.label.set_color(x_color)

        sy = Line(
            S.get_node(u).mobject.get_center(),
            S.get_node(v).mobject.get_center(),
            color=y_color,
        )
        sy_normal = rotate_vector(sy.get_vector(), np.pi/2)
        by = BraceLabel(sy, "y", sy_normal, buff=SMALL_BUFF)
        by.brace.set_color(y_color)
        y = by.label.set_color(y_color)

        sz = Line(
            S.get_node(s).mobject.get_center(),
            S.get_node(v).mobject.get_center(),
            color=z_color,
        )
        sz_normal = rotate_vector(sz.get_vector(), -np.pi/2)
        bz = BraceLabel(sz, "z", sz_normal, buff=SMALL_BUFF)
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
        eq1 = TexMobject("z \le x + y").move_to(sx.get_end() + RIGHT * 4)
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
        self.play(*S.update(updates) + [FadeOut(arrow1)])

        self.play(TransformEquation(eq1, eq2, "z \\\\le (.*) \\+ (.*)"))
        self.play(TransformEquation(eq2, eq3, "z \\\\le (.*)"))

        self.play(*relax_neighbors(S, u))

        self.wait(2)

        ShiftLeft = lambda t: (FRAME_WIDTH * (1 - t), 0, 0)
        self.play(MoveAlongPath(self.camera_frame,
                                ParametricFunction(ShiftLeft)))

        save_state(self)

    def generalize(self):
        self.__dict__.update(load_previous_state())
        s = self.s
        G = self.G

        # tighten bound for closest node
        min_node, min_bound = extract_node(G)
        self.play(*G.single_update(min_node, OrderedDict([
            ("dist", Integer(min_bound)),
            ("color", SPT_COLOR)
        ])))

        # relax neighbors of other neighbor
        neighbor = (0, 0, 0)
        to_revert = [
            node for node in G.get_adjacent_nodes(neighbor) \
            if G.get_node_label(node, "dist") is None
        ]
        self.play(*relax_neighbors(G, neighbor))

        updates = OrderedDict()
        for point in to_revert:
            updates[point] = OrderedDict([
                ("dist", None),
                ("color", BLACK),
            ])
        self.play(*G.update(updates))

        # TODO: tentatively label node across shortest edge

        # Indicate lengths of non-min edges
        anims = []
        adj_edges = G.get_adjacent_edges(s)
        min_edge = min(adj_edges, key=lambda e: G.get_edge_weight(e))
        for edge in adj_edges:
            if edge != min_edge:
                anims.extend([Indicate(G.edges[edge].get_label("weight"))])
        self.play(*anims)

        while True:
            # relax neighbors
            self.play(*relax_neighbors(G, min_node))

            # tighten bound on node with least bound
            min_node, min_bound = extract_node(G)
            if min_node:
                self.play(*G.single_update(min_node, OrderedDict([
                    ("dist", Integer(min_bound)),
                    ("color", SPT_COLOR),
                ])))
            else:
                break

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
                ("color", BLACK),
            ])
        self.play(*G.update(updates))

        min_node = s
        self.play(*G.single_update(s, OrderedDict([
            ("dist", Integer(0)),
            ("color", SPT_COLOR),
        ])))

        while min_node is not None:
            # relax neighbors
            self.play(*relax_neighbors(G, min_node, arrows=True))

            # tighten bound on node with least bound
            min_node, min_bound = extract_node(G)
            if min_node:
                parent_edge = G.get_node_parent_edge(min_node)
                updates = OrderedDict()
                updates[min_node] = OrderedDict([
                    ("dist", Integer(min_bound)),
                    ("color", SPT_COLOR),
                ])
                updates[parent_edge] = OrderedDict([
                    ("color", SPT_COLOR),
                ])
                self.play(*G.update(updates))
            else:
                break

        self.wait(1)
        self.play(FadeOut(G))

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
        """).scale_to_fit_width(0.5 * FRAME_WIDTH - 2 * MED_SMALL_BUFF) \
            .to_corner(UL, buff=MED_SMALL_BUFF)

        dijkstra_code = code.submobjects[0].copy()
        dijkstra_code.scale((FRAME_WIDTH - 2 * MED_SMALL_BUFF) / dijkstra_code.get_width()) \
            .shift(self.camera_frame.get_center() - dijkstra_code.get_center())
        self.play(ShowCreation(dijkstra_code))

        self.play(ReplacementTransform(dijkstra_code, code.submobjects[0]))

        s = (0, 0, 0)
        nodes = [
            s,
            ( 1.5,  1.5, 0),
            ( 1.5, -1.5, 0),
            (-1.5,  1.5, 0),
            (-1.5, -1.5, 0),
        ]
        edges = [
            (nodes[0], nodes[1]),
            (nodes[0], nodes[2]),
            (nodes[0], nodes[3]),
            (nodes[0], nodes[4]),
        ]
        labels = {
            s: OrderedDict([("variable", TexMobject("s"))]),
        }
        G = Graph(nodes, edges, labels=labels).shift(RIGHT * 0.25 * FRAME_WIDTH)

        updates = OrderedDict()
        for node in nodes:
            if node == s:
                updates[node] = OrderedDict([
                    ("dist", Integer(0)),
                    ("color", SPT_COLOR),
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
        bottom_initialize_line = SingleStringTexMobject(bottom_line.tex_string[4:-1])
        bottom_initialize_line.submobjects = bottom_line.submobjects[3:-1]
        bottom_initialize_line_ends = SingleStringTexMobject("")
        bottom_initialize_line_ends.submobjects = bottom_line.submobjects[0:3] + [bottom_line.submobjects[-1]]
        self.play(ReplacementTransform(top_initialize_line, bottom_initialize_line))
        self.play(
            FadeIn(bottom_initialize_line_ends),
            ShowCreation(Group(*code.submobjects[1].submobjects[1:])),
        )

        # show the graph
        self.play(FadeIn(G))
        self.play(*G.update(updates))
        self.play(FadeOut(G))

        u = (0, 0, 0)
        v = (3, 0, 0)
        nodes = [u, v]
        edges = [(u, v)]
        labels = {
            u: OrderedDict([
                ("variable", TexMobject("u")),
                ("dist", Integer(3)),
                ("color", SPT_COLOR),
            ]),
            v: OrderedDict([
                ("variable", TexMobject("v")),
                ("dist", TexMobject("\le\infty")),
            ]),
            (u, v): OrderedDict([
                ("weight", Integer(2)),
            ]),
        }
        G = Graph(nodes, edges, labels=labels).shift(RIGHT * 0.15 * FRAME_WIDTH)

        # shift relax header down and create next block
        top_line = code.submobjects[0] \
                       .submobjects[3] \
                       .submobjects[2] \
                       .submobjects[1]
        bottom_line = code.submobjects[2] \
                          .submobjects[0]
        top_relax_line = top_line.copy()
        bottom_relax_line = SingleStringTexMobject(bottom_line.tex_string[4:-1])
        bottom_relax_line.submobjects = bottom_line.submobjects[3:-1]
        bottom_relax_line_ends = SingleStringTexMobject("")
        bottom_relax_line_ends.submobjects = bottom_line.submobjects[0:3] + [bottom_line.submobjects[-1]]
        self.play(ReplacementTransform(top_relax_line, bottom_relax_line))
        self.play(
            FadeIn(bottom_relax_line_ends),
            ShowCreation(Group(*code.submobjects[2].submobjects[1:])),
        )

        # show the graph
        self.play(FadeIn(G))
        updates = OrderedDict()
        updates[v] = OrderedDict([
            ("dist", TexMobject("\le 5")),
            ("color", QUEUE_COLOR),
        ])
        updates[(u, v)] = OrderedDict([
            ("color", QUEUE_COLOR),
            ("stroke_width", 4),
        ])
        self.play(*G.update(updates))

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
        """).scale_to_fit_width(0.5 * FRAME_WIDTH - 2 * MED_SMALL_BUFF) \
            .to_corner(UL, buff=MED_SMALL_BUFF)

        self.remove(code.submobjects[0])
        self.add(code2.submobjects[0])

        top_line = code2.submobjects[0] \
                       .submobjects[2]
        bottom_line = code2.submobjects[1] \
                          .submobjects[0]
        top_relax_line = Group(*top_line.copy().submobjects[17:26])
        bottom_relax_line = SingleStringTexMobject(bottom_line.tex_string[6:-1])
        bottom_relax_line.submobjects = bottom_line.submobjects[5:-1]
        bottom_relax_line_ends = SingleStringTexMobject("")
        bottom_relax_line_ends.submobjects = bottom_line.submobjects[0:5] + [bottom_line.submobjects[-1]]
        self.play(ReplacementTransform(top_relax_line, bottom_relax_line))
        self.play(
            FadeIn(bottom_relax_line_ends),
            ShowCreation(Group(*code2.submobjects[1].submobjects[1:])),
        )

        self.play(
            Indicate(code2.submobjects[0].submobjects[2]),
            Indicate(code2.submobjects[1].submobjects[1].submobjects[0]),
        )
        self.play(
            Indicate(code2.submobjects[0].submobjects[3].submobjects[1]),
            Indicate(code2.submobjects[1].submobjects[2].submobjects[0]),
        )
        self.play(
            Indicate(code2.submobjects[0].submobjects[3].submobjects[2].submobjects[1]),
            Indicate(code2.submobjects[1].submobjects[3].submobjects[0]),
        )

        self.play(FadeOut(code2.submobjects[1]))
        self.remove(code2)
        self.add(code.submobjects[0])
        self.play(FadeIn(Group(*code.submobjects[1:])))

        self.code = code
        save_state(self)

    def run_code(self):
        self.__dict__.update(load_previous_state())

        s = ( 0,  2.6, 0)
        nodes = [
            ( 0,  2.6, 0),
            (-1.3,  1.3, 0), ( 1.3,  1.3, 0),
            (-2.6,  0, 0), ( 0,  0, 0), ( 2.6,  0, 0),
            (-1.3, -1.3, 0), ( 1.3, -1.3, 0),
            ( 0, -2.6, 0),
        ]
        edges = [
            (( 0,  2.6, 0), (-1.3,  1.3, 0)),
            (( 0,  2.6, 0), ( 1.3,  1.3, 0)),

            ((-1.3,  1.3, 0), (-2.6,  0, 0)),
            ((-1.3,  1.3, 0), ( 0,  0, 0)),
            (( 1.3,  1.3, 0), ( 0,  0, 0)),
            (( 1.3,  1.3, 0), ( 2.6,  0, 0)),

            ((-2.6,  0, 0), (-1.3, -1.3, 0)),
            (( 0,  0, 0), (-1.3, -1.3, 0)),
            (( 0,  0, 0), ( 1.3, -1.3, 0)),
            (( 2.6,  0, 0), ( 1.3, -1.3, 0)),

            ((-1.3, -1.3, 0), ( 0, -2.6, 0)),
            (( 1.3, -1.3, 0), ( 0, -2.6, 0)),
        ]
        labels = {
            ( 0,  2.6, 0): OrderedDict([("variable", TexMobject("s"))]),

            (( 0  , 2.6 , 0), (-1.3, 1.3 , 0)): OrderedDict([("weight", Integer(4))]),
            (( 0  , 2.6 , 0), ( 1.3, 1.3 , 0)): OrderedDict([("weight", Integer(1))]),

            ((-1.3, 1.3 , 0), (-2.6, 0   , 0)): OrderedDict([("weight", Integer(5))]),
            ((-1.3, 1.3 , 0), ( 0  , 0   , 0)): OrderedDict([("weight", Integer(4))]),
            (( 1.3, 1.3 , 0), ( 0  , 0   , 0)): OrderedDict([("weight", Integer(7))]),
            (( 1.3, 1.3 , 0), ( 2.6, 0   , 0)): OrderedDict([("weight", Integer(2))]),

            ((-2.6, 0   , 0), (-1.3, -1.3, 0)): OrderedDict([("weight", Integer(4))]),
            (( 0  , 0   , 0), (-1.3, -1.3, 0)): OrderedDict([("weight", Integer(5))]),
            (( 0  , 0   , 0), ( 1.3, -1.3, 0)): OrderedDict([("weight", Integer(1))]),
            (( 2.6, 0   , 0), ( 1.3, -1.3, 0)): OrderedDict([("weight", Integer(2))]),

            ((-1.3, -1.3, 0), ( 0  , -2.6, 0)): OrderedDict([("weight", Integer(2))]),
            (( 1.3, -1.3, 0), ( 0  , -2.6, 0)): OrderedDict([("weight", Integer(1))]),
        }
        G = Graph(nodes, edges, labels=labels, scale_factor=0.8).shift(self.camera_frame.get_right() * 0.5)
        self.play(ShowCreation(G))

        updates = OrderedDict()
        updates[s] = OrderedDict([
            ("dist", Integer(0)),
            ("color", SPT_COLOR),
        ])
        for node in nodes:
            if node != s:
                updates[node] = OrderedDict([
                    ("dist", TexMobject("\le\infty").set_color(INFTY_COLOR)),
                    ("color", INFTY_COLOR),
                ])
        self.play(*G.update(updates))

        min_node = (0, 2.6, 0)
        while True:
            # relax neighbors
            self.play(*relax_neighbors(G, min_node, arrows=True))

            # tighten bound on node with least bound
            min_node, min_bound = extract_node(G)
            if min_node:
                parent_edge = G.get_node_parent_edge(min_node)
                updates = OrderedDict()
                updates[min_node] = OrderedDict([
                    ("dist", Integer(min_bound)),
                    ("color", SPT_COLOR),
                ])
                updates[parent_edge] = OrderedDict([
                    ("color", SPT_COLOR),
                ])
                self.play(*G.update(updates))
            else:
                break

        self.G = G
        save_state(self)

    def analyze(self):
        self.__dict__.update(load_previous_state())
        G = self.G
        code = self.code

        self.play(FadeOut(G))

        runtime = AlignatTexMobject(
            "     &  \, &&       \,\, &&T_{\\text{build}(V)}      \\\\" + \
            "+ \, &V \, &&\\cdot \,\, &&T_{\\text{extract\_min}}  \\\\" + \
            "+ \, &E \, &&\\cdot \,\, &&T_{\\text{decrease\_key}} \\\\" + \
            "+ \, &V \, &&       \,\, &&                          \\\\" + \
            "+ \, &2 \, &&\\cdot \,\, &&E                         \\\\",
            columns=3,
        ).shift(RIGHT * 3)

        tbuild = SingleStringTexMobject("")
        tbuild.submobjects = runtime.submobjects[0].submobjects[0:9]
        v_textractmin = SingleStringTexMobject("")
        v_textractmin.submobjects = runtime.submobjects[0].submobjects[10:24]
        e_tdecreasekey = SingleStringTexMobject("")
        e_tdecreasekey.submobjects = runtime.submobjects[0].submobjects[25:40]
        v = SingleStringTexMobject("")
        v.submobjects = runtime.submobjects[0].submobjects[41]
        two_e = SingleStringTexMobject("")
        two_e.submobjects = runtime.submobjects[0].submobjects[43:]

        # time to build
        self.play(
            ReplacementTransform(
                code.submobjects[0].submobjects[2].copy(),
                tbuild
            ),
        )
        self.wait()

        # time to extract
        self.play(
            ReplacementTransform(
                code.submobjects[0].submobjects[3].submobjects[1].copy(),
                v_textractmin
            ),
            FadeIn(runtime.submobjects[0].submobjects[9]),
        )
        self.wait()

        # time to relax
        self.play(
            ReplacementTransform(
                code.submobjects[0].submobjects[3].submobjects[2].submobjects[1].copy(),
                e_tdecreasekey
            ),
            FadeIn(runtime.submobjects[0].submobjects[24]),
        )
        self.wait(2)

        # extraneous V
        self.play(
            ReplacementTransform(
                code.submobjects[0].submobjects[1].copy(),
                v
            ),
            FadeIn(runtime.submobjects[0].submobjects[40]),
        )
        self.wait()

        # extra 2 * E
        self.play(
            ReplacementTransform(
                code.submobjects[2].submobjects[1].submobjects[0].copy(),
                two_e
            ),
            FadeIn(runtime.submobjects[0].submobjects[42]),
        )
        self.wait(2)

        # remove extra
        self.play(
            FadeOut(Group(v, runtime.submobjects[0].submobjects[40])),
            FadeOut(Group(two_e, runtime.submobjects[0].submobjects[42])),
        )
        self.wait(2)

        # remove time to build
        self.play(
            FadeOut(tbuild),
            FadeOut(runtime.submobjects[0].submobjects[9]),
        )

        # show
        textbook_runtime = TexMobject(
            "O(E \cdot T_\\text{decrease\_key} + V \cdot T_\\text{extract\_min})"
        ).shift(RIGHT * 3 + UP * 0.5)

        textbook_term_1 = VGroup(*textbook_runtime.submobjects[0].submobjects[2:17])
        textbook_plus   = textbook_runtime.submobjects[0].submobjects[17]
        textbook_term_2 = VGroup(*textbook_runtime.submobjects[0].submobjects[18:32])


        self.play(
            ReplacementTransform(e_tdecreasekey, textbook_term_1),
            ReplacementTransform(runtime.submobjects[0].submobjects[24], textbook_plus),
            ReplacementTransform(v_textractmin, textbook_term_2),
            FadeIn(Group(*textbook_runtime.submobjects[0].submobjects[:2] +
                       [textbook_runtime.submobjects[0].submobjects[-1]]))
        )

        self.wait(2)

        self.code = code
        self.runtime = VGroup(
              textbook_runtime.submobjects[0].submobjects[:2]    + \
              textbook_runtime.submobjects[0].submobjects[2:17]  + \
              [textbook_runtime.submobjects[0].submobjects[17]]  + \
              textbook_runtime.submobjects[0].submobjects[18:32] + \
              [textbook_runtime.submobjects[0].submobjects[-1]]
        )
        save_state(self)

    def compare_data_structures(self):
        self.__dict__.update(load_previous_state())
        code = self.code
        runtime = self.runtime

        self.play(FadeOut(code))
        table = TextMobject(
            "\\begin{tabular}{ c | c }" + \
            "  Data Structure & $O(E \\cdot T_\\text{decrease\_key} + V \\cdot T_\\text{extract\_min})$ \\\\ \\hline" + \
            "  Array & $O(E + V \\cdot V)$ \\\\" + \
            "  Binary Heap & $O(E \\log V + V \\log V)$ \\\\" + \
            "  Fibonacci Heap & $O(E + V \\log V)$ \\\\" + \
            "\\end{tabular}"
        )
        table_lines = VGroup(
            table.submobjects[0].submobjects[13],
            table.submobjects[0].submobjects[47],
            table.submobjects[0].submobjects[53],
            table.submobjects[0].submobjects[72],
            table.submobjects[0].submobjects[100],
        )
        self.play(
            ReplacementTransform(runtime, VGroup(*table.submobjects[0].submobjects[14:47])),
            FadeIn(table_lines),
            FadeIn(Group(*table.submobjects[0].submobjects[:13])),
        )

        # Array
        array_word = VGroup(*table.submobjects[0].submobjects[48:53])
        table_array_time = VGroup(*table.submobjects[0].submobjects[54:62])
        array_time1 = TexMobject("O(E + V \cdot V)").move_to(table_array_time.get_center())
        array_time2 = TexMobject("O(E + V^2)").move_to(array_time1.get_center())
        array_time3 = TexMobject("O(V^2)").move_to(array_time2.get_center())
        self.play(FadeIn(array_word))
        self.play(Write(array_time1))
        self.play(TransformEquation(array_time1, array_time2, "O\\(E \\+ (.*)\\)"))
        self.play(TransformEquation(array_time2, array_time3, "O\\((.*)\\)"))

        # Binary Heap
        binheap_word = VGroup(*table.submobjects[0].submobjects[62:72])
        table_binheap_time = VGroup(*table.submobjects[0].submobjects[73:87])
        binheap_time1 = TexMobject("O(E \log V + V \log V)").move_to(table_binheap_time.get_center())
        binheap_time2 = TexMobject("O((E + V) \log V)").move_to(DOWN + binheap_time1.get_center())
        self.play(FadeIn(binheap_word))
        self.play(Write(binheap_time1))
        x = TransformEquation(
            binheap_time1,
            binheap_time2,
            "(O)(\\()(E) (\\\\log V) (\\+) (V) (\\\\log V)\\)",
            "(O)(\\()\\((E) (\\+) (V)\\) (\\\\log V)\\)",
            [(0,0), (1,1), (1,2), (2,3), (4,4), (5,5), (3,7), (6,7), (7,8), (7,6)],
        )
        self.play(x)

        # Fibonacci Heap
        fibo_word = VGroup(*table.submobjects[0].submobjects[87:100])
        table_fibo_time = VGroup(*table.submobjects[0].submobjects[101:])
        fibo_time = TexMobject("O(E + V \log V)").move_to(table_fibo_time.get_center())
        self.play(FadeIn(fibo_word))
        self.play(Write(fibo_time))
        self.play(Indicate(fibo_time))
        self.play(FadeOut(Group(
            table[:13],
            table[14:47],
            table_lines,
            array_word,
            array_time3,
            binheap_word,
            binheap_time2,
            fibo_word,
            fibo_time,
        )))

        self.wait(2)
        save_state(self)

    def directed_graph(self):
        self.__dict__.update(load_previous_state())
        DIST = 2.5 / 2**0.5
        nodes = [
            (-DIST * 1.2, DIST * 1.2 , 0),
            ( DIST * 1.2, DIST * 1.2 , 0),

            (-2 * DIST  , 0          , 0),
            (0          , 0          , 0),
            (2 * DIST   , 0          , 0),

            (-DIST * 1.2, -DIST * 1.2, 0),
            ( DIST * 1.2, -DIST * 1.2, 0),
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
        labels = {
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
        G = Graph(nodes, edges, labels=labels, directed=True)
        self.play(ShowCreation(G))

        min_node = (0, 0, 0)
        self.play(*G.single_update(min_node, OrderedDict([
            ("dist", Integer(0)),
            ("color", SPT_COLOR),
        ])))
        while True:
            # relax neighbors
            self.play(*relax_neighbors(G, min_node, arrows=True))

            # tighten bound on node with least bound
            min_node, min_bound = extract_node(G)
            if min_node:
                parent_edge = G.get_node_parent_edge(min_node)
                updates = OrderedDict()
                updates[min_node] = OrderedDict([
                    ("dist", Integer(min_bound)),
                    ("color", SPT_COLOR),
                ])
                updates[parent_edge] = OrderedDict([
                    ("color", SPT_COLOR),
                ])
                self.play(*G.update(updates))
            else:
                break
        self.wait()
        self.play(FadeOut(G))

    def construct(self):
        self.first_try()
        self.counterexample()
        self.one_step()
        self.triangle_inequality()
        self.generalize()
        self.last_run()
        # TODO: mention shortest path tree when arrows are used
        # TODO: directed graphs
        self.show_code()
        self.run_code()
        self.analyze()
        self.compare_data_structures()
        self.directed_graph()
