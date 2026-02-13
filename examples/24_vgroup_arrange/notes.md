# VGroup Arrange Layout Notes

Key patterns:
- `VGroup(*mobjects).arrange(direction, buff=spacing)` for linear layout
- `arrange_in_grid(rows, cols, buff)` for grid layout
- `interpolate_color(C1, C2, alpha)` blends between two colors
- `.animate.arrange(...)` can rearrange layouts as an animation
- `buff` controls spacing between elements
- Nested VGroups can be arranged independently
