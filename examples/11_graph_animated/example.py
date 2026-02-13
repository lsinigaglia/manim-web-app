from manim import *

class AnimatedGraphExample(Scene):
    def construct(self):
        # Start with vertices only
        vertices = [1, 2, 3, 4, 5]
        positions = {
            1: LEFT * 2 + UP,
            2: RIGHT * 2 + UP,
            3: RIGHT * 2 + DOWN,
            4: LEFT * 2 + DOWN,
            5: ORIGIN,
        }

        # Create dots for vertices
        dots = {}
        for v, pos in positions.items():
            dot = Dot(pos, radius=0.2, color=BLUE)
            dots[v] = dot

        # Animate vertices appearing
        self.play(*[GrowFromCenter(d) for d in dots.values()], run_time=1.5)
        self.wait(0.5)

        # Animate edges growing one by one
        edges_order = [(1, 5), (2, 5), (3, 5), (4, 5), (1, 2), (2, 3), (3, 4), (4, 1)]
        lines = []
        for u, v in edges_order:
            line = Line(
                dots[u].get_center(), dots[v].get_center(),
                color=WHITE, stroke_width=2
            )
            lines.append(line)
            self.play(Create(line), run_time=0.6)

        self.wait(1)

        # Pulse the center vertex
        self.play(
            dots[5].animate.scale(1.5).set_color(YELLOW),
            *[line.animate.set_color(YELLOW) for line in lines[:4]],
            run_time=1.5
        )
        self.wait(2)
