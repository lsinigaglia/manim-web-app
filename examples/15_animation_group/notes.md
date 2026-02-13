# AnimationGroup with Lag Ratio Notes

Key patterns:
- `AnimationGroup(*anims, lag_ratio=0.3)` staggers animations
- `lag_ratio=0` plays all simultaneously, `lag_ratio=1` plays sequentially
- Intermediate values create an overlapping cascade effect
- Works with any animation type: Create, Rotate, FadeOut, etc.
- `FadeOut(mob, shift=DOWN)` adds directional fade
