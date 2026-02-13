from manim import *

class RotatingCubeExample(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)

        # Create a cube (Prism with square base)
        cube = Cube(side_length=2, fill_opacity=0.6, fill_color=BLUE)
        cube.set_stroke(WHITE, width=2)

        self.play(Create(cube), run_time=2)
        self.play(Rotate(cube, angle=PI, axis=UP), run_time=3)
        self.play(Rotate(cube, angle=PI / 2, axis=RIGHT), run_time=2)
        self.begin_ambient_camera_rotation(rate=0.4)
        self.wait(4)
        self.stop_ambient_camera_rotation()
        self.wait(1)
