# Animated Graph Growth Notes

Key patterns:
- Build graphs manually with `Dot` and `Line` for full animation control
- `GrowFromCenter` is a good entrance animation for dots
- `Create(line)` draws a line progressively
- Use dictionaries to map vertex IDs to mobjects
- Animate properties with `.animate.set_color()` etc.
