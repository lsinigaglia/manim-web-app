from manim import *

class VectorAdditionExample(Scene):
    def construct(self):
        # Create number plane
        plane = NumberPlane(
            x_range=[-5, 5, 1],
            y_range=[-5, 5, 1],
            background_line_style={
                "stroke_color": BLUE_E,
                "stroke_width": 2,
                "stroke_opacity": 0.3
            }
        )

        # Create vectors
        v1 = Arrow(ORIGIN, [2, 1, 0], buff=0, color=RED)
        v2 = Arrow(ORIGIN, [1, 2, 0], buff=0, color=GREEN)
        v3 = Arrow(ORIGIN, [3, 3, 0], buff=0, color=YELLOW)

        # Labels
        label1 = MathTex("\\vec{v_1}").next_to(v1, DOWN)
        label2 = MathTex("\\vec{v_2}").next_to(v2, LEFT)
        label3 = MathTex("\\vec{v_1} + \\vec{v_2}").next_to(v3, UP)

        # Animate
        self.play(Create(plane))
        self.play(GrowArrow(v1), Write(label1))
        self.play(GrowArrow(v2), Write(label2))
        self.wait(0.5)
        self.play(GrowArrow(v3), Write(label3))
        self.wait(2)
