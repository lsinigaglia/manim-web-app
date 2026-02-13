from manim import *

class PendulumExample(Scene):
    def construct(self):
        # Pendulum parameters
        pivot = UP * 2.5
        length = 3.0
        g = 9.8
        theta0 = PI / 4  # initial angle

        # State: [angle, angular_velocity]
        state = {"theta": theta0, "omega": 0.0}

        pivot_dot = Dot(pivot, color=WHITE, radius=0.08)

        # Bob and rod as always_redraw
        rod = always_redraw(lambda: Line(
            pivot,
            pivot + length * np.array([np.sin(state["theta"]), -np.cos(state["theta"]), 0]),
            color=GREY, stroke_width=3,
        ))

        bob = always_redraw(lambda: Dot(
            pivot + length * np.array([np.sin(state["theta"]), -np.cos(state["theta"]), 0]),
            radius=0.2, color=RED, fill_opacity=1,
        ))

        # Trail
        trail = TracedPath(
            lambda: pivot + length * np.array([np.sin(state["theta"]), -np.cos(state["theta"]), 0]),
            stroke_color=YELLOW, stroke_width=1, stroke_opacity=0.5,
        )

        self.add(pivot_dot, rod, bob, trail)

        # Physics updater
        dt_val = 1 / 60

        def update_pendulum(mob, dt):
            alpha = -g / length * np.sin(state["theta"])
            state["omega"] += alpha * dt
            state["omega"] *= 0.999  # small damping
            state["theta"] += state["omega"] * dt

        bob.add_updater(update_pendulum)

        self.wait(12)
