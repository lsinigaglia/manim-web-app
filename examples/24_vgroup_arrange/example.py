from manim import *

class VGroupArrangeExample(Scene):
    def construct(self):
        # Create a row of shapes
        row = VGroup(
            Circle(radius=0.3, color=RED, fill_opacity=0.8),
            Square(side_length=0.5, color=BLUE, fill_opacity=0.8),
            Triangle(color=GREEN, fill_opacity=0.8).scale(0.4),
            RegularPolygon(n=5, color=YELLOW, fill_opacity=0.8).scale(0.35),
            RegularPolygon(n=6, color=PURPLE, fill_opacity=0.8).scale(0.35),
        )
        row.arrange(RIGHT, buff=0.5)
        row.shift(UP * 2)

        self.play(
            AnimationGroup(*[GrowFromCenter(s) for s in row], lag_ratio=0.2),
            run_time=2,
        )
        self.wait(0.5)

        # Create a grid of circles
        grid = VGroup(*[
            Circle(
                radius=0.25,
                fill_opacity=0.8,
                color=interpolate_color(BLUE, RED, i / 15),
            )
            for i in range(16)
        ])
        grid.arrange_in_grid(rows=4, cols=4, buff=0.3)
        grid.shift(DOWN * 0.8)

        self.play(
            AnimationGroup(*[FadeIn(c, scale=0.5) for c in grid], lag_ratio=0.05),
            run_time=2,
        )
        self.wait(1)

        # Rearrange grid into a single row
        self.play(grid.animate.arrange(RIGHT, buff=0.15).shift(DOWN * 0.8), run_time=2)
        self.wait(1)

        # Stack everything vertically
        all_shapes = VGroup(row, grid)
        self.play(all_shapes.animate.arrange(DOWN, buff=0.5).move_to(ORIGIN), run_time=2)
        self.wait(2)
