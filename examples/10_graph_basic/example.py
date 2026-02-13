from manim import *

class BasicGraphExample(Scene):
    def construct(self):
        # Define vertices and edges
        vertices = [1, 2, 3, 4, 5, 6]
        edges = [(1, 2), (1, 3), (2, 4), (3, 4), (3, 5), (4, 6), (5, 6)]

        graph = Graph(
            vertices,
            edges,
            layout="spring",
            vertex_config={"fill_color": BLUE, "radius": 0.25},
            edge_config={"stroke_color": WHITE, "stroke_width": 2},
        )

        self.play(Create(graph), run_time=3)
        self.wait(1)

        # Highlight a path
        path_edges = [(1, 2), (2, 4), (4, 6)]
        highlight_anims = []
        for edge in path_edges:
            highlight_anims.append(
                graph.edges[edge].animate.set_color(YELLOW).set_stroke(width=4)
            )
        self.play(*highlight_anims, run_time=2)
        self.wait(1)

        # Change vertex colors along path
        for v in [1, 2, 4, 6]:
            self.play(graph.vertices[v].animate.set_color(YELLOW), run_time=0.5)
        self.wait(2)
