# 3D Camera Rotation Notes

Key patterns:
- `move_camera(phi, theta, run_time)` animates camera to new orientation
- `phi` is the polar angle (from top), `theta` is the azimuthal angle
- `Sphere`, `Torus`, `Cone` are built-in 3D primitives
- Combine `move_camera` with `begin_ambient_camera_rotation` for dynamic views
- `resolution` on Sphere controls mesh density
