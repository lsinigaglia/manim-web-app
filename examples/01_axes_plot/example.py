from manim import *

class AxesPlotExample(Scene):
    def construct(self):
        # Create axes
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-2, 2, 1],
            x_length=6,
            y_length=4,
            axis_config={"color": BLUE}
        )

        # Add labels
        labels = axes.get_axis_labels(x_label="x", y_label="y")

        # Create a function graph
        graph = axes.plot(lambda x: np.sin(x), color=YELLOW)

        # Animate
        self.play(Create(axes), Write(labels))
        self.play(Create(graph), run_time=2)
        self.wait()
