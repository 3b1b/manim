import numpy.linalg as la
from big_ol_pile_of_manim_imports import *
from dijkstra_scenes.graph import Graph
from dijkstra_scenes.dynamic_equation import DynamicEquation

def extend_arrow(G, u, v, camera_location=ORIGIN):
    u_v_vector = G.get_node(v).mobject.get_center() - \
                 G.get_node(u).mobject.get_center() 
    u_v_vector /= la.norm(u_v_vector)
    u_edge_point = G.get_node(u).mobject.get_center() + \
                   u_v_vector * G.get_node(u).mobject.radius
    v_edge_point = G.get_node(v).mobject.get_center() - \
                   u_v_vector * G.get_node(v).mobject.radius
    # the default arrow tip length is 0.25
    arrow_tip_start = u_edge_point + u_v_vector * 0.25
    arrow = Arrow(
        u_edge_point,
        arrow_tip_start,
        rectangular_stem_width=0.005,
        # prevent arrow tip from shrinking
        max_tip_length_to_length_ratio=float("inf"),
    )
    return UpdateFromAlphaFunc(
        arrow,
        lambda a, t: a.put_start_and_end_on(
            u_edge_point,
            arrow_tip_start + (v_edge_point - arrow_tip_start) * t,
        ),
    ), arrow

def relax_node(G, parent, arrows=False):
    labels = []
    adj_edges = G.get_adjacent_edges(parent)
    for edge in adj_edges:
        child = G.get_opposite_node(edge, parent)
        # the parent's path length is known
        parent_dist = int(G.get_node_label(parent, "dist").number)
        new_bound = parent_dist + G.get_edge_weight(edge)
        if G.node_has_label(child, "dist"):
            old_bound = G.get_node_label(child, "dist") 
            if type(old_bound) == Integer or len(old_bound.tex_string) == 1:
                # path length is already known
                continue
            if "\infty" in old_bound.tex_string:
                old_bound = float("inf")
            else:
                old_bound = int(old_bound.tex_string[4:])
            if new_bound < old_bound:
                labels.append((child, "dist", TexMobject("\le {}".format(new_bound))))
                if arrows:
                    arrow_vec = G.get_node(parent).mobject.get_center() - \
                                G.get_node(child).mobject.get_center()
                    arrow_vec /= la.norm(arrow_vec)
                    arrow = Arrow(G.get_node(child).get_center(),
                                  G.get_node(child).get_center() + arrow_vec)
                    labels.append((child, "parent", arrow))
        else:
            # use new bound
            labels.append((child, "dist", TexMobject("\le {}".format(new_bound))))
            if arrows:
                arrow_vec = G.get_node(parent).mobject.get_center() - \
                            G.get_node(child).mobject.get_center()
                arrow_vec /= la.norm(arrow_vec)
                arrow = Arrow(G.get_node(child).get_center(),
                              G.get_node(child).get_center() + arrow_vec)
                labels.append((child, "parent", arrow))
    return G.set_node_labels(*labels)

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
            (-X_DIST , Y_DIST  , 0),
            ( 0      , Y_DIST  , 0),
            ( X_DIST , Y_DIST  , 0),
            (-X_DIST , 0       , 0),
            ( 0      , 0       , 0),
            ( X_DIST , 0       , 0),
            (-X_DIST , -Y_DIST , 0),
            ( 0      , -Y_DIST , 0),
            ( X_DIST , -Y_DIST , 0),
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
        G_gradient = color_gradient([BLUE_E, RED_E], 20)
        G = Graph(nodes, edges)
        self.play(ShowCreation(G))

        # weight edges
        random.seed()
        weights = [2, 4, 3, 6, 3, 5, 5, 8, 1, 2, 4, 1, 2, 7]
        anims = []
        for i, edge in enumerate(edges):
            if weights[i]:
                anims.extend(G.set_edge_weight(edge, weights[i]))
            else:
                anims.extend(G.set_edge_weight(edge, random.randint(1, 9)))

        self.play(*anims)

        # label s
        s = nodes[0]
        self.play(*G.set_node_labels((s, "variable", TexMobject("s"))))

        # set s to 0
        self.play(*G.set_node_labels(
            (s, "dist", Integer(0), {"color" : G_gradient[0]})
        ))

        # label neighbors with question marks
        neighbors = G.get_adjacent_nodes(s)
        labels = []
        for node in neighbors:
            labels.append((node, "dist", TexMobject("?")))
        self.play(*G.set_node_labels(*labels))

        # set neighbors to edge weights with question mark
        adj_edges = G.get_adjacent_edges(s)
        anims = []
        for edge in adj_edges:
            (u, v) = edge
            adj_node = (u if s == v else v)
            edge_weight = G.get_edge_weight(edge)
            uncertain_weight = TexMobject(str(edge_weight) + "?")
            anims.extend(G.set_node_labels((
                adj_node,
                "dist",
                uncertain_weight,
                {"color":G_gradient[edge_weight]},
            )))
        self.play(*anims)

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
        self.G_gradient = G_gradient
        save_state(self)

    def counterexample(self):
        self.__dict__.update(load_previous_state())
        G_gradient = self.G_gradient

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
        anims = []
        anims.extend(H.set_node_labels(
            (nodes[0], "variable", TexMobject("s")),
            (nodes[0], "dist", Integer(0), {"color" : G_gradient[0]}),
        ))
        anims.extend(H.set_edge_weight(edges[0], 10))
        anims.extend(H.set_edge_weight(edges[1], 1))
        anims.extend(H.set_edge_weight(edges[2], 1))
        self.play(*anims)

        # tentative distances to nodes
        adj_edges = H.get_adjacent_edges(nodes[0])
        anims = []
        labels = []
        for edge in adj_edges:
            (u, v) = edge
            adj_node = (u if nodes[0] == v else v)
            weight = H.get_edge_weight(edge)
            weight_mobject = TexMobject(str(weight) + "?")
            labels.append((adj_node, "dist", weight_mobject, {"color":G_gradient[weight]}))
        anims.extend(H.set_node_labels(*labels))
        self.play(*anims)

        # this is antipattern; possibly allow returning a copy edge?
        self.play(Indicate(H.edges[edges[0]].get_weight()))

        # switch to upper bound
        anims = []
        for edge in adj_edges:
            (u, v) = edge
            adj_node = (u if nodes[0] == v else v)
            upper_bound = TexMobject("\le " + str(H.get_edge_weight(edge)))
            anims.extend(H.set_node_labels((adj_node, "dist", upper_bound)))
        self.play(*anims)

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
        anims = []
        for edge in adj_edges:
            (u, v) = edge
            adj_node = (u if s == v else v)
            uncertain_weight = TexMobject("\le " + str(G.get_edge_weight(edge)))
            anims.extend(G.set_node_labels((adj_node, "dist", uncertain_weight)))
        self.play(*anims)

        # tighten bound on min node
        min_node, min_bound = extract_node(G)
        if min_node:
            self.play(*G.set_node_labels((min_node, "dist", Integer(min_bound))))

        # highlight other edge weights
        ## antipattern
        adj_edges = G.get_adjacent_edges(s)    
        min_edge = min(adj_edges, key = lambda x: G.get_edge(x).get_weight().number) 

        anims = []
        for edge in adj_edges:
            if edge != min_edge:
                anims.extend([Indicate(G.edges[edge].get_weight())])
        self.play(*anims)

        # revert graph
        node_labels = [(s, "dist")]
        for node in G.get_adjacent_nodes(s):
            node_labels.append((node, "dist"))
        self.play(*G.remove_node_labels(*node_labels))

        # set s to 0
        self.play(*G.set_node_labels((s, "dist", Integer(0))))

        # set bound on neighbors
        adj_edges = G.get_adjacent_edges(s)
        labels = []
        for edge in adj_edges:
            uncertain_weight = TexMobject("\le " + str(G.get_edge_weight(edge)))
            # this will cause problems, and you'll have to settle the allclose thing
            labels.append((G.edges[edge].opposite(s), "dist", uncertain_weight))
        self.play(*G.set_node_labels(*labels))

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

        s = (-X_DIST * 0.60, 0 - 1, 0)
        v = ( X_DIST * 0.60, 0 - 1, 0)
        u = (             0, 3 - 1, 0)
        labels = {
            s: [("variable", TexMobject("s"))],
            u: [("variable", TexMobject("u"))],
            v: [("variable", TexMobject("v"))],
        }
        S = Graph([s, u, v], [(u, v)], labels=labels)
        S.to_edge(DOWN, initial_offset=self.camera_frame.get_center())

        self.play(
            FadeIn(S.get_node(s)),
            FadeIn(S.get_node(v)),
        )

        # TODO: add color
        words = TextMobject(
            "\\large The shortest path from $s$ to $v$ ",
            "is at most as long as the shortest path from $s$ "
            "to any node $u$ adjacent to $v$ ",
            "plus the length of the edge connecting $u$ to $v$.",
        )
        words.scale_to_fit_width(FRAME_WIDTH - 1)
        words.to_edge(UP, initial_offset=self.camera_frame.get_center())

        arrow_anim1, arrow1 = extend_arrow(S, s, v, camera_location=self.camera_frame.get_center())
        self.play(
            arrow_anim1,
            Write(words[0]),
        )

        arrow_anim2, arrow2 = extend_arrow(S, s, u,
                camera_location=self.camera_frame.get_center())
        self.play(
            FadeIn(S.get_node(u)),
            FadeIn(S.get_edge((u, v))),
            arrow_anim2,
            Write(words[1]),
        )

        self.play(Write(words[2]))

        sx = Line(
            S.get_node(s).get_center(),
            S.get_node(u).get_center(),
        )
        sx_normal = rotate_vector(sx.get_vector(), np.pi/2)
        sy = Line(
            S.get_node(u).get_center(),
            S.get_node(v).get_center(),
        )
        sy_normal = rotate_vector(sy.get_vector(), np.pi/2)
        sz = Line(
            S.get_node(s).get_center(),
            S.get_node(v).get_center(),
        )
        sz_normal = rotate_vector(sz.get_vector(), -np.pi/2)
        x = TexMobject("x").next_to(sx.get_midpoint(), sx_normal, buff=0.04)
        y = TexMobject("y").next_to(sy.get_midpoint(), sy_normal, buff=0.04)
        z = TexMobject("z").next_to(sz.get_midpoint(), sz_normal, buff=0.04)
        triangle = Group(sx, sy, sz, x, y, z)
        
        self.play(
            FadeIn(triangle),
            FadeOut(S),
            FadeOut(arrow1),
            FadeOut(arrow2),
        )

        # TODO: convert this to use DynamicEquation
        x_len = 5
        y_len = 2
        dyneq = DynamicEquation(
            "z &\le x + y",
            "z &\le {} + {}".format(x_len, y_len),
            "z &\le {}".format(x_len + y_len),
        ).move_to(sx.get_end() + RIGHT * 4)

        self.play(
            ReplacementTransform(x.copy(), dyneq.symbol_at_index(2)),
            ReplacementTransform(y.copy(), dyneq.symbol_at_index(4)),
            ReplacementTransform(z.copy(), dyneq.symbol_at_index(0)),
            FadeIn(dyneq.symbols_at_indices(1, 3)),
        )
        
        self.play(
            FadeOut(triangle),
            FadeIn(S),
            FadeIn(arrow1),
            FadeIn(arrow2),
        )

        anims = \
            S.set_node_labels((s, "dist", Integer(0))) + \
            S.set_node_labels((u, "dist", Integer(x_len))) + \
            S.set_edge_weight((u, v), y_len)        + \
            [FadeOut(arrow1)]
        self.play(*anims)

        initial_groups = "z \\\\le (.*) \+ (.*)"
        target_groups  = "z \\\\le (.*) \+ (.*)"
        anims, cb = dyneq.transform_equation(1, "\le",
                initial_groups, target_groups, self)
        self.play(*anims, callback=cb)

        initial_groups = "z \\\\le (.*)"
        target_groups  = "z \\\\le (.*)"
        anims, cb = dyneq.transform_equation(2, "\le",
                initial_groups, target_groups, self)
        self.play(*anims, callback=cb)

        self.play(*S.set_node_labels(
            (v, "dist", TexMobject("\le {}".format(x_len + y_len))),
        ))

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
        # get shortest edge
        adj_edges = G.get_adjacent_edges(s)
        min_edge, min_weight = None, float("inf")
        for edge in adj_edges:
            edge_weight = G.get_edge_weight(edge)
            if edge_weight < min_weight:
                min_weight = edge_weight
                min_edge = edge
        (u, v) = min_edge

        # tighten bound on corresponding node
        min_node = (u if s == v else v)
        cur_label = int(G.get_node_label(min_node, "dist").tex_string[3:])
        new_label = Integer(cur_label)
        self.play(*G.set_node_labels((min_node, "dist", new_label)))

        # relax neighbors of other neighbor
        # get neighbor
        for edge in adj_edges:
            if np.allclose(edge[0], (0, 0, 0)) or \
               np.allclose(edge[1], (0, 0, 0)):
                neighbor = G.get_edge(edge).opposite(s)
            
        #self.play(Indicate(G.get_node(neighbor)))
        # relax neighbors (doesn't work with function)
        labels = []
        adj_edges = G.get_adjacent_edges(neighbor)
        to_revert = []
        for edge in adj_edges:
            adj_node = G.get_opposite_node(edge, neighbor)
            # the parent's path length is not known
            adj_node_bound = int(G.get_node_label(neighbor, "dist").tex_string[4:])

            new_bound = adj_node_bound + G.get_edge_weight(edge)
            if G.node_has_label(adj_node, "dist"):
                old_bound = G.get_node_label(adj_node, "dist") 
                if type(old_bound) == Integer or len(old_bound.tex_string) == 1:
                    # path length is already known
                    continue
                # compare both bounds
                old_bound = int(old_bound.tex_string[4:])
                if new_bound < old_bound:
                    labels.append((adj_node, "dist", TexMobject("\le {}".format(new_bound))))
            else:
                # use new bound
                labels.append((adj_node, "dist", TexMobject("\le {}".format(new_bound))))
                to_revert.append(adj_node)
        self.play(*G.set_node_labels(*labels))

        # TODO:
        # tentatively label node across shortest edge
        # highlight shorter path

        labels = []
        for node in to_revert:
            labels.append((node, "dist")) 
        self.play(*G.remove_node_labels(*labels))

        ## antipattern
        anims = []
        adj_edges = G.get_adjacent_edges(s)
        for edge in adj_edges:
            if edge != min_edge:
                anims.extend([Indicate(G.edges[edge].get_weight())])
        self.play(*anims)

        self.play(*relax_node(G, min_node))
        min_node, min_bound = extract_node(G)
        self.play(*G.set_node_labels((min_node, "dist", Integer(min_bound))))

        while True:
            # relax neighbors
            self.play(*relax_node(G, min_node))

            # tighten bound on node with least bound
            min_node, min_bound = extract_node(G)
            if min_node:
                self.play(*G.set_node_labels((min_node, "dist", Integer(min_bound))))
            else:
                break

        self.wait(2)
        save_state(self)

    def last_run(self):
        self.__dict__.update(load_previous_state())
        G = self.G
        s = self.s

        labels = []
        for node in G.get_nodes():
            labels.append((node, "dist"))
        self.play(*G.remove_node_labels(*labels))

        min_node = s
        self.play(*G.set_node_labels((s, "dist", Integer(0))))

        while True:
            # relax neighbors
            self.play(*relax_node(G, min_node, arrows=True))

            # tighten bound on node with least bound
            min_node, min_bound = extract_node(G)
            if min_node:
                self.play(*G.set_node_labels((min_node, "dist", Integer(min_bound))))
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
            s: [("variable", TexMobject("s"))],
        }
        G = Graph(nodes, edges, labels=labels).shift(RIGHT * 0.25 * FRAME_WIDTH)

        labels = []
        for node in nodes:
            if node == s:
                labels.append((node, "dist", Integer(0)))
            else:
                labels.append((node, "dist", TexMobject("\le\infty")))

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
        self.play(*G.set_node_labels(*labels))
        self.play(FadeOut(G))

        u = (0, 0, 0)
        v = (3, 0, 0)
        nodes = [u, v]
        edges = [(u, v)]
        labels = {
            u: [("variable", TexMobject("u")), ("dist", Integer(3))],
            v: [("variable", TexMobject("v")), ("dist", TexMobject("\le 7"))],
            (u, v): [("weight", Integer(2))],
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
        self.play(*G.set_node_labels((v, "dist", TexMobject("\le 5"))))

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
            ( 0,  2.6, 0): [("variable", TexMobject("s"))],

            (( 0  , 2.6 , 0) , (-1.3, 1.3 , 0)): [("weight", Integer(6))],
            (( 0  , 2.6 , 0) , ( 1.3, 1.3 , 0)): [("weight", Integer(1))],

            ((-1.3, 1.3 , 0) , (-2.6, 0   , 0)): [("weight", Integer(5))],
            ((-1.3, 1.3 , 0) , ( 0  , 0   , 0)): [("weight", Integer(4))],
            (( 1.3, 1.3 , 0) , ( 0  , 0   , 0)): [("weight", Integer(9))],
            (( 1.3, 1.3 , 0) , ( 2.6, 0   , 0)): [("weight", Integer(2))],

            ((-2.6, 0   , 0) , (-1.3, -1.3, 0)): [("weight", Integer(4))],
            (( 0  , 0   , 0) , (-1.3, -1.3, 0)): [("weight", Integer(5))],
            (( 0  , 0   , 0) , ( 1.3, -1.3, 0)): [("weight", Integer(1))],
            (( 2.6, 0   , 0) , ( 1.3, -1.3, 0)): [("weight", Integer(2))],

            ((-1.3, -1.3, 0) , ( 0  , -2.6, 0)): [("weight", Integer(2))],
            (( 1.3, -1.3, 0) , ( 0  , -2.6, 0)): [("weight", Integer(1))],
        }
        G = Graph(nodes, edges, labels=labels, scale_factor=0.8).shift(self.camera_frame.get_right() * 0.5)
        self.play(ShowCreation(G))

        labels = [
            (s, "dist", Integer(0))
        ]
        for node in nodes:
            if node != s:
                labels.append((node, "dist", TexMobject("\le\infty")))
        self.play(*G.set_node_labels(*labels))

        min_node = (0, 2.6, 0)
        while True:
            # relax neighbors
            self.play(*relax_node(G, min_node, arrows=True))

            # tighten bound on node with least bound
            min_node, min_bound = extract_node(G)
            if min_node:
                self.play(*G.set_node_labels((min_node, "dist", Integer(min_bound))))
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
        #self.play(FadeOut(runtime))
        #self.play(ShowCreation(table))
        #number_anims = []
        #for i, mob in enumerate(table.submobjects[0].submobjects):
        #    num = Integer(i, color=RED).next_to(mob, UR, buff=0.1).scale(0.5)
        #    number_anims.append(ShowCreation(num))
        #self.play(*number_anims)
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
        self.wait(2)
        save_state(self)

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
