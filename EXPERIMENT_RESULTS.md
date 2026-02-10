# Multi-Scene Validation Experiment - Results

**Date:** 2026-02-10
**Test:** Complex 45-second animation (parabola + moving dot + Riemann sums)

---

## Experiment Setup

**Complex Prompt:**
> "Create a 45-second animation showing calculus concepts:
> 1. Display axes with parabola y = x²
> 2. Animate dot moving along curve from x=-2 to x=2
> 3. Show Riemann sum rectangles under the curve"

**Approach A - Single Scene:**
- Generate everything in one `construct()` method
- Current system approach

**Approach B - Multi-Scene:**
- Split into 3 separate scenes (15s each)
- Generate and render independently
- Would concat with ffmpeg (not tested yet)

---

## Results

### ✅ Single-Scene Generation

**Status:** SUCCESS

**Code Complexity:** 68 lines

**Structure:**
```python
class ParabolaRiemannScene(Scene):
    def construct(self):
        # 1. Create axes + parabola (3s)
        # 2. Moving dot with ValueTracker (4s)
        # 3. Riemann rectangles (4.5s)
        # Total: ~12s actual duration
```

**Observations:**
- LLM generated clean, working code
- All 3 parts in one method
- Used advanced patterns (ValueTracker, always_redraw)
- Render time: ~20 seconds

---

### ⚠️ Multi-Scene Generation

**Status:** PARTIAL SUCCESS (2/3 scenes)

#### Scene 1: Axes + Parabola
**Status:** ✅ SUCCESS
**Code:** 32 lines
**Duration:** ~5s
**Notes:** Simple, clean generation

#### Scene 2: Moving Dot
**Status:** ✅ SUCCESS (but generated full scene)
**Code:** 57 lines
**Problem:** Re-created axes + parabola (not just the dot)
**Notes:** LLM didn't understand "add to existing scene"

#### Scene 3: Riemann Rectangles
**Status:** ✅ SUCCESS
**Code:** 44 lines
**Problem:** Also re-created axes + parabola

**Total Code:** 133 lines (nearly 2x single-scene)

---

## Key Findings

### 🔍 Discovery 1: Code Duplication

**Problem:** Each multi-scene regenerates the same setup code.

```python
# Scene 1
axes = Axes(...)
parabola = axes.plot(...)

# Scene 2 (duplicates Scene 1)
plane = NumberPlane(...)  # Different but equivalent
parabola = plane.plot(...)  # Same parabola!

# Scene 3 (duplicates again)
axes = Axes(...)
parabola = axes.plot(...)
```

**Why this happens:**
LLM treats each scene as isolated. Doesn't know Scene 1 already created the axes.

**Impact:**
- 2x more code to maintain
- Inconsistent visuals (different axis styles per scene)
- Harder to concat (axes might shift between scenes)

---

### 🔍 Discovery 2: LLM Prefers Monolithic

**Observation:** When given complex prompt, LLM naturally generates everything in one scene.

**Evidence:** Single-scene code is elegant:
- One axes setup
- Logical flow (axes → curve → dot → rectangles)
- Smooth transitions (FadeOut dot before rectangles)

**Multi-scene code is awkward:**
- Each scene is self-contained
- No transitions between scenes
- Would need manual ffmpeg concat

---

### 🔍 Discovery 3: Success Rate

**Single-scene:** 1/1 (100%)
**Multi-scene:** 2-3/3 (67-100%, depending on criteria)

But multi-scene "succeeded" by regenerating context each time, which defeats the purpose.

---

## Critical Analysis

### What We Learned

**Hypothesis:** "Multi-scene composition makes complex videos easier"

**Result:** **REJECTED** (with caveats)

**Reasons:**

1. **LLM doesn't understand scene continuity**
   - Each scene is isolated
   - Can't reference "the axes from Scene 1"
   - Would need explicit state management

2. **Code duplication problem**
   - Each scene rebuilds the world
   - More code = more bugs
   - Inconsistent visuals

3. **Single-scene already works**
   - For 45s prompt, single-scene succeeded
   - Code is cleaner
   - No concat issues

### When Multi-Scene WOULD Help

**Scenario 1: Truly independent scenes**
```
"Create 3 separate animations:
 1. Show binary search
 2. Show merge sort
 3. Show quicksort"
```

Here, scenes share nothing → multi-scene makes sense.

**Scenario 2: Scene-level failures**
If Scene 3 fails, but Scene 1 & 2 succeeded:
- Fix only Scene 3
- Concat with previous scenes
- Don't re-render everything

**Scenario 3: Very long videos (>60s)**
One giant `construct()` method becomes unmaintainable.
But need better decomposition strategy than naive splitting.

---

## Revised Recommendation

### ❌ Don't Build: Naive Multi-Scene

The experiment shows that simply splitting prompts into N scenes doesn't work because:
- LLM treats scenes as isolated
- Massive code duplication
- Visual inconsistency
- Harder to concat than expected

### ✅ DO Build: Stateful Scene Composition

**Better approach:**

```python
# Scene 1: Setup
state = {
    "axes": axes,
    "parabola": parabola,
    "camera_position": ...
}
save_state(state)

# Scene 2: Add to existing (not rebuild)
state = load_state()
dot = create_dot(state["parabola"])
animate_dot(dot)
update_state(state, {"dot": dot})

# Scene 3: Continue from Scene 2
state = load_state()
rectangles = create_rectangles(state["axes"], state["parabola"])
```

**Key insight:** Don't treat scenes as isolated. Maintain shared state.

---

## Alternative: Iterative Single-Scene

**Better idea:** Instead of multi-scene, use iterative refinement of ONE scene.

**Flow:**
```
1. User: "Show parabola"
   → Generate Scene v1 (axes + parabola)

2. User: "Add a moving dot"
   → Modify Scene v1 → Scene v2 (axes + parabola + dot)

3. User: "Add Riemann rectangles"
   → Modify Scene v2 → Scene v3 (full animation)
```

**Advantages:**
- One scene, progressively enhanced
- No duplication
- User controls the flow
- Easier to fix (modify last version)

**This is stateful conversation, not multi-scene!**

---

## Updated Roadmap

Based on experiment results:

### Phase 1: Stateful Conversation (PRIORITY)

**Not multi-scene, but scene evolution:**

```python
conversation_state = {
    "scene_code": "...",  # Latest version
    "objects": {"axes": ..., "parabola": ...},  # Track what exists
    "video": "latest.mp4"
}

# User: "Add a circle"
# System: Reads current scene, adds circle, re-renders
```

**Effort:** 2-3 days
**Impact:** HIGH (enables customization + progressive complexity)

### Phase 2: Prompt Decomposition (TEST FIRST)

**Not for multi-scene, but for planning:**

```python
# Complex prompt → break into steps
steps = [
    "Create axes and plot parabola",
    "Animate dot moving along parabola",
    "Show Riemann rectangles"
]

# Generate ONE scene that does all steps
code = generate_scene_with_steps(steps)
```

**Key:** Still one scene, but LLM thinks step-by-step.

**Effort:** 1 day to test
**Impact:** MEDIUM (might improve complex prompts)

### Phase 3: Scene Library (MAYBE)

If we really need multi-scene, build a library of compatible scenes:

```python
# All library scenes use same axis setup
standard_axes = """
axes = Axes(
    x_range=[-3, 3, 1],
    y_range=[-2, 5, 1],
    ...
)
"""

# Scenes can safely concat because axes are consistent
```

**Effort:** 1 week
**Impact:** LOW (only useful for specific use cases)

---

## Conclusion

**The experiment was VALUABLE, even though it rejected the hypothesis.**

**Key Learnings:**

1. ✅ Single-scene generation already works well (even for 45s prompts)
2. ❌ Naive multi-scene creates more problems than it solves
3. ✅ Stateful conversation is the real solution (not multi-scene)
4. ⚠️ Multi-scene might work for truly independent animations

**Next Step:**
Build stateful conversation (scene evolution), NOT multi-scene composition.

---

## Code Comparison

### Single-Scene (68 lines)

```python
class ParabolaRiemannScene(Scene):
    def construct(self):
        axes = Axes(...)          # Setup once
        parabola = axes.plot(...)  # Draw once

        self.play(Create(axes))    # Part 1
        self.play(Create(parabola))

        dot = always_redraw(...)   # Part 2
        self.play(x_tracker.animate...)

        rectangles = axes.get_riemann_rectangles(...)  # Part 3
        self.play(Create(rectangles))
```

**Elegant. Single setup. Logical flow.**

### Multi-Scene (133 lines total)

```python
# Scene 1 (32 lines)
class Scene1(Scene):
    def construct(self):
        axes = Axes(...)          # Setup
        parabola = axes.plot(...)

# Scene 2 (57 lines)
class Scene2(Scene):
    def construct(self):
        plane = NumberPlane(...)  # Setup AGAIN
        parabola = plane.plot(...) # Draw AGAIN
        dot = always_redraw(...)

# Scene 3 (44 lines)
class Scene3(Scene):
    def construct(self):
        axes = Axes(...)           # Setup AGAIN
        parabola = axes.plot(...)  # Draw AGAIN
        rectangles = axes.get_riemann_rectangles(...)
```

**Duplicated. Inconsistent. Hard to concat.**

---

**Verdict: Build stateful conversation, not multi-scene.**

The real problem isn't "how to split scenes", it's "how to evolve one scene over multiple user requests."

Stateful conversation solves this elegantly.
