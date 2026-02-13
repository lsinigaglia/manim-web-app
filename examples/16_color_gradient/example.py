from manim import *

class ColorGradientExample(Scene):
    def construct(self):
        # Circle with gradient
        circle = Circle(radius=1.2, fill_opacity=1, stroke_width=3)
        circle.set_color(color=[RED, YELLOW, GREEN, BLUE])
        circle.shift(LEFT * 3)

        # Square with gradient
        square = Square(side_length=2, fill_opacity=1, stroke_width=3)
        square.set_color(color=[PURPLE, PINK, ORANGE])

        # Star with gradient
        star = Star(n=5, outer_radius=1.2, inner_radius=0.5, fill_opacity=1, stroke_width=3)
        star.set_color(color=[BLUE, TEAL, GREEN, YELLOW])
        star.shift(RIGHT * 3)

        self.play(
            DrawBorderThenFill(circle),
            DrawBorderThenFill(square),
            DrawBorderThenFill(star),
            run_time=3,
        )
        self.wait(1)

        # Animate color change
        self.play(
            circle.animate.set_color(color=[BLUE, PURPLE, RED]),
            square.animate.set_color(color=[GREEN, YELLOW, ORANGE, RED]),
            star.animate.set_color(color=[WHITE, BLUE, PURPLE]),
            run_time=2,
        )
        self.wait(1)

        # Scale and rotate
        self.play(
            circle.animate.scale(0.5),
            square.animate.rotate(PI / 4),
            star.animate.scale(1.5),
            run_time=2,
        )
        self.wait(2)
