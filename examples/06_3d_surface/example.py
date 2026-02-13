from manim import *

class SurfacePlotExample(ThreeDScene):
    def construct(self):
        # Set up camera
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES)

        # Create axes
        axes = ThreeDAxes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            z_range=[-1, 1, 0.5],
            x_length=6,
            y_length=6,
            z_length=3,
        )

        # Create surface
        surface = Surface(
            lambda u, v: axes.c2p(u, v, np.sin(u) * np.cos(v)),
            u_range=[-3, 3],
            v_range=[-3, 3],
            resolution=(30, 30),
            fill_opacity=0.7,
        )
        surface.set_color_by_gradient(BLUE, GREEN, YELLOW)

        self.play(Create(axes), run_time=1)
        self.play(Create(surface), run_time=3)
        self.begin_ambient_camera_rotation(rate=0.3)
        self.wait(6)
        self.stop_ambient_camera_rotation()
        self.wait(1)
