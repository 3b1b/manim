import dill
import pickle
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
        self.play(*G.set_node_label(s, "variable", TexMobject("s")))

        # set s to 0
        self.play(*G.set_node_label(s, "dist", Integer(0)))

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
            uncertain_weight = TexMobject(str(G.get_edge_weight(edge)) + "?")
            anims.extend(G.set_node_label(adj_node, "dist", uncertain_weight))
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
        state = self.__dict__.copy()
        # must be removed before save to prevent segfault
        if "writing_process" in self.__dict__:
            del state["writing_process"]
        if "canvas" in state["camera"].__dict__:
            del state["camera"].__dict__["canvas"]
        pickle.dump(state, open("first_try.mnm", "wb"))

    def counterexample(self):
        loaded_state = pickle.load(open("first_try.mnm", "rb"))
        self.__dict__.update(loaded_state)

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
        # TODO: that leftward shift in the coordinates above
        H.shift(DOWN * FRAME_HEIGHT + LEFT * 0.5 * H.get_width())
        self.play(ShowCreation(H))

        # draw s and edge weights
        anims = []
        anims.extend(H.set_node_label(nodes[0], "variable", TexMobject("s")))
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
            uncertain_weight = TexMobject(str(H.get_edge_weight(edge)) + "?")
            labels.append((adj_node, "dist", uncertain_weight))
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
            anims.extend(H.set_node_label(adj_node, "dist", upper_bound))
        self.play(*anims)

        # scroll back up
        initial_height = self.camera_frame.get_center()[1]
        ShiftUp = lambda t: (0, initial_height + FRAME_HEIGHT * t, 0)
        self.play(MoveAlongPath(self.camera_frame,
                                ParametricFunction(ShiftUp)))

        state = self.__dict__.copy()
        # must be removed before save to prevent segfault
        if "writing_process" in self.__dict__:
            del state["writing_process"]
        if "canvas" in state["camera"].__dict__:
            del state["camera"].__dict__["canvas"]
        pickle.dump(state, open("counterexample.mnm", "wb"))

    def one_step(self):
        loaded_state = pickle.load(open("counterexample.mnm", "rb"))
        self.__dict__.update(loaded_state)
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
            anims.extend(G.set_node_label(adj_node, "dist", uncertain_weight))
        self.play(*anims)

        # tighten bound on min node
        min_node, min_bound = extract_node(G)
        if min_node:
            self.play(*G.set_node_label(min_node, "dist", Integer(min_bound)))

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
        self.play(*G.set_node_label(s, "dist", Integer(0)))

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
        state = self.__dict__.copy()
        # must be removed before save to prevent segfault
        if "writing_process" in self.__dict__:
            del state["writing_process"]
        if "canvas" in state["camera"].__dict__:
            del state["camera"].__dict__["canvas"]
        pickle.dump(state, open("one_step.mnm", "wb"))

    def triangle_inequality(self):
        loaded_state = pickle.load(open("one_step.mnm", "rb"))
        self.__dict__.update(loaded_state)

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
            S.set_node_label(s, "dist", Integer(0)) + \
            S.set_node_label(u, "dist", Integer(x_len)) + \
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

        self.play(*S.set_node_label(
            v, "dist", TexMobject("\le {}".format(x_len + y_len))))

        self.wait(2)

        ShiftLeft = lambda t: (FRAME_WIDTH * (1 - t), 0, 0)
        self.play(MoveAlongPath(self.camera_frame,
                                ParametricFunction(ShiftLeft)))

        state = self.__dict__.copy()
        # must be removed before save to prevent segfault
        if "writing_process" in self.__dict__:
            del state["writing_process"]
        if "canvas" in state["camera"].__dict__:
            del state["camera"].__dict__["canvas"]
        pickle.dump(state, open("triangle_inequality.mnm", "wb"))

    def generalize(self):
        loaded_state = pickle.load(open("triangle_inequality.mnm", "rb"))
        self.__dict__.update(loaded_state)
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
        self.play(*G.set_node_label(min_node, "dist", new_label))

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
        self.play(*G.set_node_label(min_node, "dist", Integer(min_bound)))

        while True:
            # relax neighbors
            self.play(*relax_node(G, min_node))

            # tighten bound on node with least bound
            min_node, min_bound = extract_node(G)
            if min_node:
                self.play(*G.set_node_label(min_node, "dist", Integer(min_bound)))
            else:
                break

        self.wait(2)

        state = self.__dict__.copy()
        # must be removed before save to prevent segfault
        if "writing_process" in self.__dict__:
            del state["writing_process"]
        if "canvas" in state["camera"].__dict__:
            del state["camera"].__dict__["canvas"]
        pickle.dump(state, open("generalize.mnm", "wb"))

    def last_run(self):
        loaded_state = pickle.load(open("generalize.mnm", "rb"))
        self.__dict__.update(loaded_state)
        G = self.G
        s = self.s

        labels = []
        for node in G.get_nodes():
            labels.append((node, "dist"))
        self.play(*G.remove_node_labels(*labels))

        min_node = s
        self.play(*G.set_node_label(s, "dist", Integer(0)))

        while True:
            # relax neighbors
            self.play(*relax_node(G, min_node, arrows=True))

            # tighten bound on node with least bound
            min_node, min_bound = extract_node(G)
            if min_node:
                self.play(*G.set_node_label(min_node, "dist", Integer(min_bound)))
            else:
                break

        self.wait(1)
        self.play(FadeOut(G))

        state = self.__dict__.copy()
        # must be removed before save to prevent segfault
        if "writing_process" in self.__dict__:
            del state["writing_process"]
        if "canvas" in state["camera"].__dict__:
            del state["camera"].__dict__["canvas"]
        pickle.dump(state, open("last_run.mnm", "wb"))

    def show_code(self):
        loaded_state = pickle.load(open("last_run.mnm", "rb"))
        self.__dict__.update(loaded_state)

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
                v.dist = infinity
            s.dist = 0

        def relax_edge(G, u, v):
            if v.dist > u.dist + G.weights(u, v):
                v.dist = u.dist + G.weights(u, v)
                v.parent = u

        class min_queue:
            def __init__(self, items, key):
                pass

            def extract_min(self):
                pass

            def decrease_key(self, item, new_value):
                pass
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
        G = Graph(nodes, edges, labels).shift(RIGHT * 0.25 * FRAME_WIDTH)

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
        G = Graph(nodes, edges, labels).shift(RIGHT * 0.15 * FRAME_WIDTH)

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
        self.play(FadeOut(G))

        self.wait(2)

        state = self.__dict__.copy()
        # must be removed before save to prevent segfault
        if "writing_process" in self.__dict__:
            del state["writing_process"]
        if "canvas" in state["camera"].__dict__:
            del state["camera"].__dict__["canvas"]
        pickle.dump(state, open("show_code.mnm", "wb"))

    def run_code(self):
        loaded_state = pickle.load(open("show_code.mnm", "rb"))
        self.__dict__.update(loaded_state)

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
        G = Graph(nodes, edges, labels, scale=0.8).shift(self.camera_frame.get_right() * 0.5)
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
                self.play(*G.set_node_label(min_node, "dist", Integer(min_bound)))
            else:
                break

        self.wait(2)

    def construct(self):
        self.first_try()
        self.counterexample()
        self.one_step()
        self.triangle_inequality()
        self.generalize()
        self.last_run()
        # TODO: mention shortest path tree when arrows are used
        # TODO: directed graphs
        self.show_code() # TODO: min_queue
        self.run_code()

