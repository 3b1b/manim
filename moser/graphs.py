import itertools as it
import numpy as np

CUBE_GRAPH = {
    "name" : "CubeGraph",
                        # 6  4
                        #  20 
                        #  31 
                        # 7  5
    "vertices" : [
        (x, y, 0)
        for r in (1, 2)
        for x, y in it.product([-r,r], [-r, r])
    ],
    "edges" : [
        (0, 1),
        (0, 2),
        (3, 1),
        (3, 2),
        (4, 5),
        (4, 6),
        (7, 5),
        (7, 6),
        (0, 4),
        (1, 5),
        (2, 6),
        (3, 7),
    ], 
    "region_cycles" : [
        [0, 2, 3, 1],
        [4, 0, 1, 5],
        [4, 6, 2, 0],
        [6, 7, 3, 2],
        [7, 5, 1, 3],
        [4, 6, 7, 5],#By convention, last region will be "outside"
    ]
}

SAMPLE_GRAPH = {
    "name" : "SampleGraph",
                     #  4 2  3
                     #   0 1
                     #       
                     # 5 
    "vertices" :[
        ( 0, 0, 0),
        ( 2, 0, 0),
        ( 1, 1, 0),
        ( 3, 1, 0),
        (-1, 1, 0),
        (-2,-2, 0),
    ],
    "edges" : [
        (0, 1),
        (1, 2),
        (1, 3),
        (3, 2),
        (2, 4),
        (4, 0),
        (2, 0),
        (4, 5),
        (0, 5),
        (1, 5),
    ],
    "region_cycles" : [
        (0, 1, 2),
        (1, 3, 2),
        (2, 4, 0),
        (4, 5, 0),
        (0, 5, 1),
        (4, 5, 1, 3),
    ]

}

OCTOHEDRON_GRAPH = {
    "name" : "OctohedronGraph",
                    #       3
                    #
                    #     1   0
                    #       2
                    #4             5
    "vertices" : [
        (r*np.cos(angle), r*np.sin(angle)-1, 0)
        for r, s in [(1, 0), (3, 3)]
        for angle in (np.pi/6) * np.array([s, 4 + s, 8 + s])
    ],
    "edges" : [
        (0, 1),
        (1, 2),
        (2, 0),
        (5, 0),
        (0, 3),
        (3, 5),
        (3, 1),
        (3, 4),
        (1, 4),
        (4, 2),
        (4, 5),
        (5, 2),
    ],
    "region_cycles" : [
        (0, 1, 2),
        (0, 5, 3),
        (3, 1, 0),
        (3, 4, 1),
        (1, 4, 2),
        (2, 4, 5),
        (5, 0, 2),
        (3, 4, 5),
    ]
}
