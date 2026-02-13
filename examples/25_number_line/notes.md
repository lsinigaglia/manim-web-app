# NumberLine with Animated Pointer Notes

Key patterns:
- `NumberLine(x_range, length, include_tip=True)` creates a number line
- `include_numbers=False` avoids LaTeX rendering issues
- `number_line.n2p(value)` converts a number to a scene point
- `always_redraw` keeps pointer/dot synced with ValueTracker
- `next_to(point, direction, buff)` positions relative to a point
- Different `rate_func` values create different motion styles
