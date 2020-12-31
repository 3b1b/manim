from manim import Graph


def test_graph_creation():
    vertices = [1, 2, 3, 4]
    edges = [(1, 2), (2, 3), (3, 4), (4, 1)]
    layout = {1: [0, 0, 0], 2: [1, 1, 0], 3: [1, -1, 0], 4: [-1, 0, 0]}
    G_manual = Graph(vertices=vertices, edges=edges, layout=layout)
    assert str(G_manual) == "Graph on 4 vertices and 4 edges"
    G_spring = Graph(vertices=vertices, edges=edges)
    assert str(G_spring) == "Graph on 4 vertices and 4 edges"
