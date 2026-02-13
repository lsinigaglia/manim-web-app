# Fourier Epicycles Notes

Key patterns:
- Epicycles are nested circles: each orbits around the previous one's edge
- Each circle has (radius, frequency, phase) parameters
- `always_redraw` rebuilds the circle chain each frame
- `TracedPath` records the tip position over time to draw the shape
- `ValueTracker` drives the animation parameter `t`
- Use `rate_func=linear` for constant angular speed
