# Animated Spiral Notes

Key patterns:
- Archimedean spiral: `r = a + b*theta` -> `(r*cos(t), r*sin(t))`
- Logarithmic spiral: `r = a * exp(b*t)` -> grows exponentially
- `ParametricFunction` with `t_range` controls how many turns
- `Create()` draws the curve progressively from start to end
- `get_end()` returns the final point of a parametric curve
