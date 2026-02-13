from manim import *

class GraphLayoutExample(Scene):
    def construct(self):
        vertices = list(range(1, 9))
        edges = [
            (1, 2), (2, 3), (3, 4), (4, 5),
            (5, 6), (6, 7), (7, 8), (8, 1),
            (1, 5), (2, 6), (3, 7), (4, 8),
        ]

        # Start with circular layout
        graph = Graph(
            vertices,
            edges,
            layout="circular",
            vertex_config={"fill_color": BLUE, "radius": 0.2},
            edge_config={"stroke_color": GREY, "stroke_width": 2},
        )

        self.play(Create(graph), run_time=2)
        self.wait(1)

        # Transition to spring layout
        self.play(
            graph.animate.change_layout("spring", seed=42),
            run_time=2
        )
        self.wait(1)

        # Transition to kamada_kawai layout
        self.play(
            graph.animate.change_layout("kamada_kawai"),
            run_time=2
        )
        self.wait(1)

        # Back to circular
        self.play(
            graph.animate.change_layout("circular"),
            run_time=2
        )
        self.wait(2)
