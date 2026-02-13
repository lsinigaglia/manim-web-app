# Lissajous Curves Notes

Key patterns:
- Lissajous: `x = A*sin(a*t + delta)`, `y = B*sin(b*t)`
- Ratio a:b determines the shape pattern
- 1:1 with PI/2 phase gives a circle/ellipse
- `always_redraw` with `ParametricFunction` redraws curve when trackers change
- Small `t_range` step (0.01) gives smooth curves
- Animate `ValueTracker` to morph between different Lissajous patterns
