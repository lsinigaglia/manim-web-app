# 3D Parametric Curve Notes

Key patterns:
- `ParametricFunction` works in 3D when returning 3D points
- Use `axes.c2p()` to map parametric coordinates to scene coordinates
- `t_range` controls the parameter domain
- A helix is `(cos(t), sin(t), c*t)` for constant c
- `stroke_width` controls line thickness
