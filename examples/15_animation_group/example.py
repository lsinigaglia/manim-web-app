from manim import *

class AnimationGroupExample(Scene):
    def construct(self):
        # Create a row of circles
        circles = VGroup(*[
            Circle(radius=0.3, color=color, fill_opacity=0.8)
            for color in [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
        ]).arrange(RIGHT, buff=0.5)

        # Staggered creation with lag_ratio
        self.play(
            AnimationGroup(
                *[GrowFromCenter(c) for c in circles],
                lag_ratio=0.3,
            ),
            run_time=3,
        )
        self.wait(0.5)

        # Staggered rotation
        self.play(
            AnimationGroup(
                *[Rotate(c, angle=PI) for c in circles],
                lag_ratio=0.15,
            ),
            run_time=2,
        )
        self.wait(0.5)

        # Staggered color flash
        self.play(
            AnimationGroup(
                *[c.animate.set_color(WHITE) for c in circles],
                lag_ratio=0.2,
            ),
            run_time=2,
        )
        self.play(
            AnimationGroup(
                *[FadeOut(c, shift=DOWN) for c in circles],
                lag_ratio=0.2,
            ),
            run_time=2,
        )
        self.wait(1)
