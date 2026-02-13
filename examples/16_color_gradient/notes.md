# Color Gradients on Shapes Notes

Key patterns:
- `mobject.set_color(color=[C1, C2, C3])` applies a gradient
- Works with any VMobject (Circle, Square, Star, etc.)
- `DrawBorderThenFill` draws outline first, then fills
- Gradients can be animated with `.animate.set_color()`
- `fill_opacity=1` is needed to see fill gradients
