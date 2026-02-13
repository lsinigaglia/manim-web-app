from manim import *

class LissajousExample(Scene):
    def construct(self):
        # Parameters
        a_tracker = ValueTracker(3)
        b_tracker = ValueTracker(2)
        delta_tracker = ValueTracker(PI / 2)

        curve = always_redraw(
            lambda: ParametricFunction(
                lambda t: np.array([
                    3 * np.sin(a_tracker.get_value() * t + delta_tracker.get_value()),
                    3 * np.sin(b_tracker.get_value() * t),
                    0,
                ]),
                t_range=[0, 2 * PI, 0.01],
                color=GREEN,
                stroke_width=3,
            )
        )

        # Dot tracing the curve
        dot = always_redraw(
            lambda: Dot(color=RED, radius=0.08).move_to(
                curve.get_end()
            )
        )

        self.add(curve, dot)
        self.wait(1)

        # Change frequency ratio from 3:2 to 3:4
        self.play(b_tracker.animate.set_value(4), run_time=3)
        self.wait(1)

        # Change phase
        self.play(delta_tracker.animate.set_value(0), run_time=2)
        self.wait(1)

        # Change to 1:1 (ellipse)
        self.play(
            a_tracker.animate.set_value(1),
            b_tracker.animate.set_value(1),
            delta_tracker.animate.set_value(PI / 2),
            run_time=3,
        )
        self.wait(1)

        # Back to complex pattern
        self.play(
            a_tracker.animate.set_value(5),
            b_tracker.animate.set_value(4),
            delta_tracker.animate.set_value(PI / 6),
            run_time=3,
        )
        self.wait(1)
