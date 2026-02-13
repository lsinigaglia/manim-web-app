# Multiple ValueTrackers Notes

Key patterns:
- Create multiple `ValueTracker` instances to control different parameters
- `always_redraw` rebuilds mobjects using tracker values each frame
- `tracker.animate.set_value(x)` smoothly transitions the value
- Animate multiple trackers simultaneously by passing them in one `self.play()`
- `rate_func=linear` makes rotation constant speed
- `int(tracker.get_value())` converts float to int for discrete parameters
