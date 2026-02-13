# Complex Updater Chain Notes

Key patterns:
- `always_redraw(lambda: ...)` recreates a mobject every frame
- Updaters can reference other mobjects' positions via `get_center()`
- Multiply position by `np.array([1, -1, 0])` to mirror vertically
- `DashedLine` creates a dashed connecting line
- Chain multiple updaters to create linked dynamic systems
