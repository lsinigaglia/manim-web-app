from manim import *

class MultiValueTrackerExample(Scene):
    def construct(self):
        # Trackers for radius, angle, and color hue
        radius_tracker = ValueTracker(1)
        angle_tracker = ValueTracker(0)
        sides_tracker = ValueTracker(3)

        # Dot that orbits based on angle and radius
        dot = always_redraw(
            lambda: Dot(
                radius=0.1,
                color=RED,
            ).move_to(
                radius_tracker.get_value() * np.array([
                    np.cos(angle_tracker.get_value()),
                    np.sin(angle_tracker.get_value()),
                    0
                ])
            )
        )

        # Polygon with dynamic number of sides
        polygon = always_redraw(
            lambda: RegularPolygon(
                n=int(sides_tracker.get_value()),
                color=BLUE,
                stroke_width=3,
            ).scale(radius_tracker.get_value())
        )

        # Trail line from origin to dot
        trail_line = always_redraw(
            lambda: Line(ORIGIN, dot.get_center(), color=YELLOW, stroke_width=2)
        )

        self.add(polygon, trail_line, dot)

        # Animate angle rotation while changing radius
        self.play(
            angle_tracker.animate.set_value(2 * PI),
            run_time=3,
            rate_func=linear,
        )
        self.play(
            radius_tracker.animate.set_value(2.5),
            sides_tracker.animate.set_value(8),
            run_time=2,
        )
        self.play(
            angle_tracker.animate.set_value(4 * PI),
            run_time=3,
            rate_func=linear,
        )
        self.play(
            radius_tracker.animate.set_value(0.5),
            sides_tracker.animate.set_value(3),
            run_time=2,
        )
        self.wait(2)
