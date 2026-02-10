from manim import *

class MovingDotExample(Scene):
    def construct(self):
        # Create axes and graph
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-2, 2, 1],
            x_length=6,
            y_length=4
        )

        graph = axes.plot(lambda x: np.sin(x), color=BLUE)

        # Create moving dot with tracker
        t = ValueTracker(-3)
        dot = always_redraw(
            lambda: Dot(color=RED).move_to(
                axes.c2p(t.get_value(), np.sin(t.get_value()))
            )
        )

        # Animate
        self.play(Create(axes), Create(graph))
        self.add(dot)
        self.play(t.animate.set_value(3), run_time=4, rate_func=linear)
        self.wait()
