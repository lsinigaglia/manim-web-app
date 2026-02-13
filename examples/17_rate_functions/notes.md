# Rate Functions Demo Notes

Key patterns:
- `rate_func=smooth` is the default (ease in/out)
- `linear` gives constant speed
- `rush_into` accelerates toward the end
- `rush_from` decelerates from a fast start
- `there_and_back` goes to target and returns
- `wiggle` oscillates around the target
- Set via `self.play(anim, rate_func=...)` or `.animate(rate_func=...)`
