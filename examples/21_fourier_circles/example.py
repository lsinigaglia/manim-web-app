from manim import *

class FourierCirclesExample(Scene):
    def construct(self):
        # Define epicycle parameters: (radius, frequency, phase)
        epicycles = [
            (1.5, 1, 0),
            (0.7, -2, PI / 4),
            (0.4, 3, PI / 3),
            (0.25, -5, PI / 6),
        ]

        tracker = ValueTracker(0)

        def get_tip_position(t):
            x, y = 0.0, 0.0
            for radius, freq, phase in epicycles:
                x += radius * np.cos(freq * t + phase)
                y += radius * np.sin(freq * t + phase)
            return np.array([x, y, 0])

        # Draw the circles and radii
        def get_circles_group():
            group = VGroup()
            cx, cy = 0.0, 0.0
            t = tracker.get_value()
            for radius, freq, phase in epicycles:
                center = np.array([cx, cy, 0])
                circle = Circle(radius=radius, color=BLUE, stroke_width=1, stroke_opacity=0.4)
                circle.move_to(center)
                # Radius line
                nx = cx + radius * np.cos(freq * t + phase)
                ny = cy + radius * np.sin(freq * t + phase)
                line = Line(center, np.array([nx, ny, 0]), color=WHITE, stroke_width=1.5)
                group.add(circle, line)
                cx, cy = nx, ny
            # Tip dot
            tip = Dot(np.array([cx, cy, 0]), radius=0.06, color=RED)
            group.add(tip)
            return group

        circles_group = always_redraw(get_circles_group)

        # Traced path of the tip
        trail = TracedPath(
            lambda: get_tip_position(tracker.get_value()),
            stroke_color=YELLOW,
            stroke_width=2,
        )

        self.add(circles_group, trail)

        self.play(
            tracker.animate.set_value(2 * PI),
            run_time=8,
            rate_func=linear,
        )
        self.wait(1)

        # Second revolution faster
        self.play(
            tracker.animate.set_value(4 * PI),
            run_time=4,
            rate_func=linear,
        )
        self.wait(1)
