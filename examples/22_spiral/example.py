from manim import *

class SpiralExample(Scene):
    def construct(self):
        # Archimedean spiral: r = a + b*theta
        spiral = ParametricFunction(
            lambda t: np.array([
                (0.1 + 0.12 * t) * np.cos(t),
                (0.1 + 0.12 * t) * np.sin(t),
                0
            ]),
            t_range=[0, 6 * PI],
            color=BLUE,
            stroke_width=3,
        )

        # Dot at the tip
        dot = Dot(spiral.get_end(), radius=0.1, color=RED)

        self.play(Create(spiral), run_time=4)
        self.play(FadeIn(dot), run_time=0.3)
        self.wait(0.5)

        # Create second spiral (logarithmic) in different color
        log_spiral = ParametricFunction(
            lambda t: np.array([
                0.15 * np.exp(0.1 * t) * np.cos(t),
                0.15 * np.exp(0.1 * t) * np.sin(t),
                0
            ]),
            t_range=[0, 5 * PI],
            color=YELLOW,
            stroke_width=3,
        )

        self.play(Create(log_spiral), run_time=4)
        self.wait(1)

        # Fade everything with a spin
        all_objects = VGroup(spiral, dot, log_spiral)
        self.play(Rotate(all_objects, angle=PI), FadeOut(all_objects), run_time=2)
        self.wait(1)
