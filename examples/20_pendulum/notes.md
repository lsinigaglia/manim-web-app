# Simple Pendulum Simulation Notes

Key patterns:
- Use `add_updater(func)` with `dt` parameter for physics simulation
- Store mutable state in a dictionary so lambdas can access it
- `always_redraw` rebuilds rod and bob each frame based on state
- `TracedPath` records the path of a point over time
- Small damping factor (0.999) prevents perpetual motion
- Real physics: angular_acceleration = -(g/L) * sin(theta)
