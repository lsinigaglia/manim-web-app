from manim import *

class TransformShapesExample(Scene):
    def construct(self):
        # Create shapes
        circle = Circle(radius=1.5, color=BLUE, fill_opacity=0.5)
        square = Square(side_length=3, color=RED, fill_opacity=0.5)
        triangle = Triangle(color=GREEN, fill_opacity=0.5).scale(2)

        # Position initial shape
        circle.move_to(ORIGIN)

        # Animate transformations
        self.play(FadeIn(circle))
        self.wait(0.5)
        self.play(Transform(circle, square), run_time=1.5)
        self.wait(0.5)
        self.play(Transform(circle, triangle), run_time=1.5)
        self.wait(0.5)
        self.play(FadeOut(circle))
        self.wait()
