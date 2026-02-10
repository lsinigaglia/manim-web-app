from manim import *

class RiemannSumExample(Scene):
    def construct(self):
        # Create axes
        axes = Axes(
            x_range=[0, 3, 1],
            y_range=[0, 5, 1],
            x_length=6,
            y_length=4
        )

        # Define function
        graph = axes.plot(lambda x: x**2, color=BLUE)

        # Create Riemann rectangles
        rectangles = axes.get_riemann_rectangles(
            graph,
            x_range=[0, 2],
            dx=0.5,
            color=YELLOW,
            fill_opacity=0.5
        )

        # Animate
        self.play(Create(axes))
        self.play(Create(graph))
        self.wait(0.5)
        self.play(Create(rectangles))
        self.wait(2)
