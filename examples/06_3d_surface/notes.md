# 3D Surface Plot Notes

Key patterns:
- Use `ThreeDScene` as the base class for 3D scenes
- `Surface` takes a function mapping (u, v) to 3D point
- `axes.c2p()` converts coordinates to scene points
- `set_color_by_gradient()` applies gradient coloring
- `begin_ambient_camera_rotation()` rotates camera continuously
- `set_camera_orientation(phi, theta)` sets initial viewing angle
