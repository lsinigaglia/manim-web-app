from manim import *

class MovingCameraFollowExample(MovingCameraScene):
    def construct(self):
        # Create a long path
        path = VMobject(color=GREY, stroke_width=2)
        path.set_points_smoothly([
            np.array([-6, 0, 0]),
            np.array([-3, 2, 0]),
            np.array([0, -1, 0]),
            np.array([3, 2, 0]),
            np.array([6, 0, 0]),
        ])

        # Dot that moves along the path
        dot = Dot(color=RED, radius=0.15)
        dot.move_to(path.get_start())

        # Trailing circle around dot
        ring = always_redraw(
            lambda: Circle(radius=0.4, color=YELLOW, stroke_width=2)
            .move_to(dot.get_center())
        )

        # Background markers along the way
        markers = VGroup()
        for t in np.linspace(0, 1, 8):
            point = path.point_from_proportion(t)
            marker = Star(n=4, outer_radius=0.15, inner_radius=0.07, color=BLUE, fill_opacity=0.8)
            marker.move_to(point)
            markers.add(marker)

        self.add(path, markers, ring, dot)

        # Zoom camera in and attach to dot
        self.play(self.camera.frame.animate.scale(0.4), run_time=1)

        # Add updater for camera to follow dot
        self.camera.frame.add_updater(
            lambda m: m.move_to(dot.get_center())
        )

        # Move dot along path
        self.play(MoveAlongPath(dot, path), run_time=6, rate_func=linear)

        # Remove updater and zoom out
        self.camera.frame.clear_updaters()
        self.play(self.camera.frame.animate.scale(2.5).move_to(ORIGIN), run_time=2)
        self.wait(2)
