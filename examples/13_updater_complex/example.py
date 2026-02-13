from manim import *

class ComplexUpdaterExample(Scene):
    def construct(self):
        # Main dot that moves along a path
        main_dot = Dot(color=RED, radius=0.12)
        main_dot.move_to(LEFT * 3)

        # Trailing circle that follows the main dot
        circle = always_redraw(
            lambda: Circle(radius=0.6, color=BLUE, stroke_width=2)
            .move_to(main_dot.get_center())
        )

        # Line from origin to the dot
        line = always_redraw(
            lambda: Line(ORIGIN, main_dot.get_center(), color=YELLOW, stroke_width=2)
        )

        # Shadow dot that mirrors vertically
        shadow = always_redraw(
            lambda: Dot(color=GREEN, radius=0.1).move_to(
                main_dot.get_center() * np.array([1, -1, 0])
            )
        )

        # Connecting dashed line between dot and shadow
        connector = always_redraw(
            lambda: DashedLine(
                main_dot.get_center(), shadow.get_center(),
                color=GREY, stroke_width=1
            )
        )

        self.add(line, circle, connector, shadow, main_dot)

        # Move main dot in an arc
        self.play(main_dot.animate.move_to(UP * 2 + RIGHT * 2), run_time=3)
        self.play(main_dot.animate.move_to(DOWN * 1 + RIGHT * 3), run_time=3)
        self.play(main_dot.animate.move_to(LEFT * 3), run_time=3)
        self.wait(2)
