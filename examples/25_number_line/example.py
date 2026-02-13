from manim import *

class NumberLineExample(Scene):
    def construct(self):
        # Create number line
        number_line = NumberLine(
            x_range=[-5, 5, 1],
            length=10,
            include_numbers=False,  # no LaTeX numbers
            include_tip=True,
            color=WHITE,
        )

        # Add tick marks (already included by default)
        self.play(Create(number_line), run_time=1.5)
        self.wait(0.5)

        # Value tracker for pointer position
        tracker = ValueTracker(-4)

        # Pointer triangle
        pointer = always_redraw(
            lambda: Triangle(color=RED, fill_opacity=1)
            .scale(0.15)
            .rotate(PI)
            .next_to(number_line.n2p(tracker.get_value()), UP, buff=0.1)
        )

        # Dot on the number line
        dot = always_redraw(
            lambda: Dot(
                number_line.n2p(tracker.get_value()),
                color=RED, radius=0.1,
            )
        )

        # Vertical indicator line
        indicator_line = always_redraw(
            lambda: Line(
                number_line.n2p(tracker.get_value()) + DOWN * 0.3,
                number_line.n2p(tracker.get_value()) + UP * 0.5,
                color=YELLOW, stroke_width=2,
            )
        )

        self.play(FadeIn(pointer), FadeIn(dot), FadeIn(indicator_line), run_time=0.5)

        # Animate pointer moving right
        self.play(tracker.animate.set_value(4), run_time=3, rate_func=smooth)
        self.wait(0.5)

        # Move to specific positions
        self.play(tracker.animate.set_value(0), run_time=1.5)
        self.wait(0.5)

        self.play(tracker.animate.set_value(-2.5), run_time=1.5)
        self.wait(0.5)

        self.play(tracker.animate.set_value(3.5), run_time=2, rate_func=there_and_back)
        self.wait(0.5)

        # Bounce to final position
        self.play(tracker.animate.set_value(0), run_time=1.5, rate_func=rush_from)
        self.wait(2)
