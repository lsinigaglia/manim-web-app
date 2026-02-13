# Camera Following Object Notes

Key patterns:
- `self.camera.frame.add_updater(lambda m: m.move_to(target))` makes camera follow
- `MoveAlongPath(mobject, path)` moves a mobject along a VMobject path
- `path.set_points_smoothly([...])` creates smooth curve through points
- `clear_updaters()` removes all updaters when done tracking
- `point_from_proportion(t)` gets a point at fraction t along a path
