from manim import *

class RateFunctionsExample(Scene):
    def construct(self):
        # Create dots with different rate functions
        rate_funcs = [
            smooth,
            linear,
            rush_into,
            rush_from,
            there_and_back,
            wiggle,
        ]
        colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]

        dots = VGroup()
        start_x = -5
        end_x = 5
        spacing = 1.0

        for i, (rf, color) in enumerate(zip(rate_funcs, colors)):
            y_pos = 2.5 - i * spacing
            dot = Dot(
                point=np.array([start_x, y_pos, 0]),
                radius=0.15,
                color=color,
            )
            # Add small indicator line at start
            start_line = Line(
                np.array([start_x, y_pos - 0.2, 0]),
                np.array([start_x, y_pos + 0.2, 0]),
                color=GREY, stroke_width=1,
            )
            end_line = Line(
                np.array([end_x, y_pos - 0.2, 0]),
                np.array([end_x, y_pos + 0.2, 0]),
                color=GREY, stroke_width=1,
            )
            self.add(start_line, end_line)
            dots.add(dot)

        self.add(dots)
        self.wait(0.5)

        # Animate all dots simultaneously with different rate functions
        anims = []
        for dot, rf in zip(dots, rate_funcs):
            target = dot.copy().set_x(end_x)
            anims.append(dot.animate(rate_func=rf).set_x(end_x))

        self.play(*anims, run_time=4)
        self.wait(1)

        # Reset and do it again
        anims_back = []
        for dot, rf in zip(dots, rate_funcs):
            anims_back.append(dot.animate(rate_func=rf).set_x(start_x))
        self.play(*anims_back, run_time=4)
        self.wait(2)
