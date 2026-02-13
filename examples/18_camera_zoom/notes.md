# Camera Zoom and Pan Notes

Key patterns:
- Use `MovingCameraScene` as base class (not regular Scene)
- `self.camera.frame.animate.scale(0.5)` zooms in (smaller scale = closer)
- `self.camera.frame.animate.move_to(point)` pans the camera
- Chain `.scale()` and `.move_to()` for simultaneous zoom + pan
- Remember to zoom back out by scaling with the inverse factor
