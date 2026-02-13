from manim import *

class ParametricCurve3DExample(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)

        axes = ThreeDAxes(
            x_range=[-4, 4, 1],
            y_range=[-4, 4, 1],
            z_range=[-3, 3, 1],
            x_length=6,
            y_length=6,
            z_length=4,
        )

        # Helix parametric curve
        helix = ParametricFunction(
            lambda t: axes.c2p(
                2 * np.cos(t),
                2 * np.sin(t),
                0.3 * t
            ),
            t_range=[-4 * PI, 4 * PI],
            color=YELLOW,
            stroke_width=3,
        )

        self.play(Create(axes), run_time=1)
        self.play(Create(helix), run_time=4)
        self.begin_ambient_camera_rotation(rate=0.3)
        self.wait(5)
        self.stop_ambient_camera_rotation()
        self.wait(1)
