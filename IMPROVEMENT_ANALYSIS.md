# Improvement Analysis: Path to Long, Customized Videos

## Current State Assessment

**What works well:**
- ✅ Example retrieval (keyword search is fine for 5-10 examples)
- ✅ Single-scene generation (~70% success rate)
- ✅ Error recovery (one-click fix)
- ✅ Fast iteration (15-25 sec per render)

**What breaks:**
- ❌ Long videos (>20 seconds) → LLM generates overly complex code
- ❌ Multi-part animations ("First show X, then Y, then Z")
- ❌ Customization ("Like the last video, but change the color")
- ❌ No context between requests (every prompt starts from scratch)

---

## The Real Problem

**It's NOT retrieval quality.**

With 5-10 examples, keyword search works fine. Even with 100 examples, semantic search would only improve accuracy by maybe 10-15%.

**The REAL problems are:**

### 1. **Complexity Ceiling**
LLM tries to fit everything into one `construct()` method. For long videos, this generates:
- 100+ line methods (hard to debug)
- Memory issues (too many objects)
- Slow renders (30+ seconds)
- Brittle code (one error breaks everything)

### 2. **No Composability**
User wants: "Show a parabola, then zoom in on the vertex, then show the derivative"

Current system: Generates one giant scene. High failure rate.

Better approach: Generate 3 separate scenes → compose them.

### 3. **No State/Memory**
User: "Create a circle"
System: [generates video]
User: "Now make it blue and add a square"
System: Starts from scratch, ignores previous video.

### 4. **No Planning**
For complex requests, LLM jumps straight to code. No decomposition.

---

## Critical Analysis: Do We Need RAG?

### What RAG Would Give Us

**Semantic search** instead of keyword matching:
- Query: "show how limits work" → finds calculus examples (even without keyword "limit")
- Query: "animate blockchain" → finds transform/sequence examples

**When this helps:**
- Large example library (50+ examples)
- Domain-specific terminology (user says "convergence", examples say "approaching")
- Cross-domain analogies (user asks for "sorting visualization", finds "transform" examples)

### What RAG Would NOT Solve

❌ Long video generation (still generates one big scene)
❌ Multi-part composition (retrieval doesn't help with decomposition)
❌ Customization (can't reference previous renders)
❌ Complexity management (more examples ≠ simpler code)

### Cost-Benefit Analysis

**RAG Implementation Cost:**
- 2-3 days to integrate (sentence-transformers + FAISS/ChromaDB)
- Need 20+ examples to see benefits (current: 5)
- Ongoing: maintain embeddings when examples change

**Actual Benefit:**
- Maybe 10% better retrieval accuracy
- Only noticeable with 50+ examples
- Doesn't solve the core problems

**Verdict: RAG is premature optimization.**

---

## Better Approaches (Step-by-Step)

### Phase 1: Multi-Scene Composition (HIGHEST IMPACT)

**Problem:** Long videos = complex single scene.

**Solution:** Break into multiple scenes, render separately, concatenate.

**Implementation:**

```python
# New prompt format:
"""
Create a 60-second video:
1. [0-20s] Show a parabola on axes
2. [20-40s] Zoom in on the vertex
3. [40-60s] Show the derivative tangent line
"""

# Planning agent:
plan = [
    {"duration": 20, "description": "Show parabola", "scene_name": "Scene1"},
    {"duration": 20, "description": "Zoom on vertex", "scene_name": "Scene2"},
    {"duration": 20, "description": "Show derivative", "scene_name": "Scene3"}
]

# Generate each scene separately:
for step in plan:
    code = llm.generate(step["description"], examples, max_duration=step["duration"])
    video = render(code)
    clips.append(video)

# Concatenate:
final_video = ffmpeg.concat(clips)
```

**Why this works:**
- Each scene is simple (high success rate)
- Easy to fix one part without regenerating everything
- Natural parallelization (render scenes concurrently)
- Better than RAG for handling complexity

**Effort:** 1-2 days
**Impact:** 10x (enables 60+ second videos)

---

### Phase 2: Stateful Conversation (HIGH IMPACT)

**Problem:** Can't customize previous renders.

**Solution:** Track conversation history, reference previous code.

**Implementation:**

```python
# Store conversation context:
conversation = {
    "history": [
        {"role": "user", "content": "Create a red circle"},
        {"role": "assistant", "scene_code": "...", "video_path": "..."}
    ],
    "current_scene": "class MyScene(Scene): ..."
}

# User: "Make it blue"
# System: Understands "it" refers to previous circle
# Generates: scene_code.replace("RED", "BLUE")
```

**Types of modifications:**
1. **Color/size/position changes** → regex/AST manipulation
2. **Add new elements** → append to construct()
3. **Remove elements** → filter out code blocks
4. **Replace elements** → targeted code rewrite

**Prompt to LLM:**
```python
system_prompt = f"""
Previous scene code:
{previous_scene_code}

User wants to modify it: "{user_request}"

Generate a minimal diff or full updated code.
"""
```

**Why this works:**
- Enables iteration ("now make it faster", "add a label")
- Reduces regeneration cost (only change what's needed)
- Better UX (feels like a conversation)

**Effort:** 2-3 days
**Impact:** 5x (enables customization workflow)

---

### Phase 3: Planning Agent (MEDIUM IMPACT)

**Problem:** Complex prompts → LLM jumps to code → fails.

**Solution:** Separate planning from coding.

**Two-stage generation:**

```python
# Stage 1: Planning
plan = planning_llm.generate(user_prompt)
# Output:
{
    "steps": [
        "1. Create coordinate axes",
        "2. Plot y = x^2 as a yellow curve",
        "3. Show rectangles under the curve",
        "4. Animate the rectangles filling"
    ],
    "manim_objects": ["Axes", "plot", "Rectangle", "Create", "FadeIn"],
    "complexity": "medium",
    "estimated_duration": "20s"
}

# Stage 2: Coding
code = coding_llm.generate(plan, examples)
```

**Why this works:**
- Forces LLM to think before coding
- Easier to catch logical errors early
- Can show plan to user for approval
- Better for complex requests

**Effort:** 2-3 days
**Impact:** 3x (improves success rate for complex prompts)

---

### Phase 4: Template-Based Generation (LOW EFFORT, MEDIUM IMPACT)

**Problem:** LLM reinvents the wheel every time.

**Solution:** Pre-built templates for common patterns.

**Example templates:**

```python
templates = {
    "axes_and_plot": {
        "pattern": "plot {function} on axes",
        "code_template": """
axes = Axes(x_range=[{x_min}, {x_max}], y_range=[{y_min}, {y_max}])
graph = axes.plot(lambda x: {function}, color={color})
self.play(Create(axes), Create(graph))
"""
    },
    "transform_shapes": {
        "pattern": "transform {shape1} into {shape2}",
        "code_template": """
shape1 = {shape1}()
shape2 = {shape2}()
self.play(Create(shape1))
self.play(Transform(shape1, shape2))
"""
    }
}

# If prompt matches template → use template (faster, more reliable)
# Else → fall back to LLM
```

**Why this works:**
- 100% success rate for common patterns
- Instant generation (no LLM call)
- Reduces LLM load (save API costs)

**Effort:** 1 day (5-10 templates)
**Impact:** 2x (for common use cases)

---

### Phase 5: Agentic Workflow (RESEARCH-LEVEL)

**Problem:** Single LLM call does planning + coding + error handling.

**Solution:** Multiple specialized agents.

**Agent roles:**

```
User Prompt
    ↓
[Planner Agent] → Breaks down into steps
    ↓
[Example Retriever] → Finds relevant examples
    ↓
[Coder Agent] → Writes Manim code
    ↓
[Reviewer Agent] → Checks for common errors
    ↓
[Renderer] → Executes code
    ↓
[Debugger Agent] → If error, analyzes and fixes
```

**Why this could work:**
- Each agent is simpler (single responsibility)
- Can fine-tune agents separately
- Better error handling (specialized debugger)

**Why this might NOT work:**
- Complexity explosion (5+ agents to maintain)
- Latency (multiple LLM calls)
- Error propagation (planner mistakes → coder fails)

**Effort:** 2-3 weeks
**Impact:** Uncertain (needs experimentation)

---

## When Would We ACTUALLY Need RAG?

RAG becomes valuable when:

1. **Large example library** (50+ examples)
   - Current: 5 examples → keyword search is fine
   - Future: 100 examples → semantic search helps

2. **Domain-specific terminology**
   - User: "show eigenvectors" → Examples: "matrix transformation"
   - Requires understanding that these are related concepts

3. **Cross-domain analogies**
   - User: "visualize quicksort" → Examples: "array transformations"
   - Keyword search wouldn't catch this

**Timeline:** Phase 6 or 7, AFTER we have 50+ examples.

---

## Recommended Roadmap

### Week 1-2: Multi-Scene Composition
**Why:** Biggest blocker to long videos.
**How:** Planning agent → generate N scenes → concat with ffmpeg.
**Risk:** Low (ffmpeg concat is well-understood).
**Expected Outcome:** Can generate 60+ second videos reliably.

### Week 3: Stateful Conversation
**Why:** Enables customization workflow.
**How:** Store previous scene code → allow diffs/modifications.
**Risk:** Medium (AST manipulation is tricky).
**Expected Outcome:** "Make it blue", "Add a square" works.

### Week 4: Template System
**Why:** Quick wins for common patterns.
**How:** 10 templates for frequent requests.
**Risk:** Low (just string formatting).
**Expected Outcome:** 2x faster for 30% of requests.

### Month 2: Planning Agent
**Why:** Better handling of complex prompts.
**How:** Two-stage generation (plan → code).
**Risk:** Medium (might not improve enough to justify complexity).
**Expected Outcome:** Complex prompts work 50% more often.

### Month 3+: Consider RAG
**Why:** By now we have 20-30 examples, semantic search starts helping.
**How:** Embed examples with sentence-transformers, FAISS for search.
**Risk:** Low (well-trodden path).
**Expected Outcome:** 10-15% better retrieval.

---

## Critical Questions to Answer First

Before building anything, test these hypotheses:

### Hypothesis 1: "Multi-scene composition solves long videos"
**Test:** Manually split a 60s prompt into 3 scenes, render separately, concat.
**Success criteria:** Works better than single-scene generation.
**Time:** 2 hours
**If fails:** Rethink entire approach.

### Hypothesis 2: "Stateful conversation enables customization"
**Test:** Save previous scene code, prompt LLM with "modify this code: make circle blue"
**Success criteria:** LLM generates valid diff.
**Time:** 1 hour
**If fails:** Need better prompting or AST tools.

### Hypothesis 3: "Planning stage reduces complexity"
**Test:** Prompt LLM with "first plan, then code" for 5 complex examples.
**Success criteria:** Better success rate than direct generation.
**Time:** 2 hours
**If fails:** Planning stage is overhead, skip it.

### Hypothesis 4: "Templates cover common cases"
**Test:** Analyze last 100 user prompts, check how many match 10 templates.
**Success criteria:** >30% match rate.
**Time:** 3 hours (need prompt logs)
**If fails:** Templates not worth it, focus on LLM.

---

## The Uncomfortable Truth

**We might not need to improve retrieval at all.**

With 5-10 carefully chosen examples, the system already works for simple cases. The bottleneck is:
1. Complexity management (multi-scene)
2. Customization (stateful conversation)
3. Planning (decomposition)

RAG would be a distraction. It's the "cool tech" answer, not the right answer.

**Better strategy:**
- Phase 1-2: Enable long/complex videos (multi-scene + planning)
- Phase 3: Enable customization (stateful)
- Phase 4: Optimize common cases (templates)
- Phase 5+: Consider RAG IF we have 50+ examples

---

## Alternative Radical Idea: No LLM for Composition

**What if:** We skip LLM for high-level composition, use it only for low-level code generation.

**Flow:**
1. User: "60 second video: parabola, zoom, derivative"
2. **Rule-based planner** (no LLM): Split into 3×20s scenes
3. **LLM**: Generate code for each scene independently
4. **ffmpeg**: Concat videos

**Why this might work:**
- Simpler (rule-based planning is deterministic)
- Faster (no planning LLM call)
- More reliable (no hallucination risk)

**Why this might NOT work:**
- Less flexible (can't handle "smooth transition between scenes")
- Requires manual rules for decomposition

**Worth testing:** Definitely. Try rule-based planning for 10 prompts, compare to LLM planning.

---

## Final Recommendation

**DON'T start with RAG.**

**DO start with:**
1. ✅ Multi-scene composition (enables long videos)
2. ✅ Stateful conversation (enables customization)
3. ✅ Planning agent OR rule-based decomposition (test both)

**Test these first:** Spend 1 day validating hypotheses before writing code.

**RAG timeline:** Month 3+, IF we have 50+ examples AND keyword search is proven insufficient.

**Focus on the right problems:**
- Composition > Retrieval
- Iteration > Generation
- Simplicity > Sophistication

---

**The best improvement is often the boring one.**

Multi-scene composition isn't sexy. But it directly solves the core problem: complex videos are hard to generate as one monolithic scene.

RAG is sexy. But it solves a problem we don't have yet: retrieval quality with large example sets.

Build what's needed, not what's cool.
