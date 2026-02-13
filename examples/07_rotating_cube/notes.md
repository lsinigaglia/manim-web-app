# Rotating 3D Cube Notes

Key patterns:
- `Cube(side_length=...)` creates a 3D cube
- `Rotate(mobject, angle, axis)` rotates around a given axis
- `UP`, `RIGHT`, `OUT` are standard 3D axis vectors
- Combine explicit `Rotate` animations with `begin_ambient_camera_rotation`
- `set_stroke()` controls edge appearance
