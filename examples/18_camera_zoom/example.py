from manim import *

class CameraZoomExample(MovingCameraScene):
    def construct(self):
        # Create a grid of shapes
        shapes = VGroup()
        for i in range(5):
            for j in range(5):
                if (i + j) % 2 == 0:
                    shape = Circle(radius=0.3, fill_opacity=0.8, color=BLUE)
                else:
                    shape = Square(side_length=0.5, fill_opacity=0.8, color=RED)
                shape.move_to(np.array([i - 2, j - 2, 0]))
                shapes.add(shape)

        self.play(FadeIn(shapes), run_time=1.5)
        self.wait(0.5)

        # Zoom into top-right corner
        self.play(
            self.camera.frame.animate.scale(0.4).move_to(np.array([2, 2, 0])),
            run_time=2,
        )
        self.wait(1)

        # Pan to bottom-left
        self.play(
            self.camera.frame.animate.move_to(np.array([-2, -2, 0])),
            run_time=2,
        )
        self.wait(1)

        # Zoom out to see everything
        self.play(
            self.camera.frame.animate.scale(2.5 / 0.4).move_to(ORIGIN),
            run_time=2,
        )
        self.wait(1)

        # Zoom back to normal
        self.play(
            self.camera.frame.animate.scale(1 / 2.5).move_to(ORIGIN),
            run_time=2,
        )
        self.wait(1)
