# Manim Web App - Technical Overview

## How It Works (High Level)

```
User Prompt → LLM (Claude) → Python Code → Manim Renderer → MP4 Video
```

### The Pipeline

1. **User writes a prompt**: "Plot y = sin(x)"
2. **System retrieves relevant examples** from `examples/` folder using keyword matching
3. **LLM generates Manim code**: Claude Sonnet 4.5 receives:
   - System prompt with strict rules (no LaTeX, use v0.18.0 APIs only)
   - 1-2 curated code examples
   - User's request
4. **Code is saved** to `generated/scene.py`
5. **Manim renders** the scene programmatically (no subprocess, no Docker)
6. **Video is served** to the browser

If rendering fails → user clicks "Fix" → LLM sees the traceback → generates minimal patch → retry.

---

## Why This Works

### The Secret Sauce

**Example-driven generation**: Instead of expecting the LLM to know all Manim APIs, we show it working examples first.

```python
# What we send to Claude:
system_prompt = """
You are a Manim expert. Rules:
- Use ONLY Manim Community v0.18.0
- NO Text/MathTex/Tex (LaTeX not configured)
- Keep animations 8-15 seconds
- Return JSON: {plan, imports, scene_code, notes}

Example 1: [axes plotting code]
Example 2: [vector animation code]
"""

user_prompt = "Plot y = sin(x) and animate a dot"
```

**Result**: Claude sees the pattern, adapts it to the new request. Success rate: ~70-80%.

### Example Retrieval

Simple keyword scoring:
- Name match: +10 points
- Tag match: +5 points
- Notes match: +2 points

Query: "plot sine" → finds `01_axes_plot` (tags: ["axes", "plot", "function"])

**No RAG, no embeddings, no vector DB**. Just string matching. Works surprisingly well for 5-10 examples.

---

## Repository Structure

```
examples/
├── 01_axes_plot/          # x/y axes + function plotting
├── 02_riemann_sums/       # calculus visualization
├── 03_vector_addition/    # arrows and vector math
├── 04_transform_shapes/   # morphing animations
└── 05_moving_dot/         # ValueTracker + updaters

Each example has:
- meta.json     (name, tags, difficulty, description)
- example.py    (working Manim code)
- notes.md      (technical notes)
```

**Why these examples?**
- Cover common mathematical concepts (calculus, geometry, algebra)
- Demonstrate different Manim patterns (axes, shapes, transforms, updaters)
- Keep it minimal (5 examples = ~500 lines total)

---

## Current Limitations

### Hard Limits (By Design)
1. **No LaTeX support**: Text/MathTex disabled → LLM must use shapes only
2. **Single render at a time**: No queue, no concurrency
3. **No persistent storage**: Each render overwrites `latest.mp4`
4. **Fixed Manim version**: Hardcoded to v0.18.0
5. **Local only**: Not designed for multi-user deployment

### Soft Limits (Could Fix)
1. **Example search is naive**: Keyword matching misses semantic similarity
2. **One-shot error fixing**: If fix fails, user must rewrite prompt
3. **No render progress**: User stares at loading spinner for 20+ seconds
4. **LLM isn't deterministic**: Same prompt can produce different code
5. **No code validation**: We render first, catch errors later

---

## Ways to Improve

### Low-Hanging Fruit (Easy Wins)

1. **Add more examples** (30 min each)
   - Derivatives/tangents, matrices, 3D rotations, parametric curves
   - Each new example = better coverage for that topic

2. **Better error messages** (2 hours)
   - Parse common Manim errors → give specific hints
   - "AttributeError: 'Axes' has no 'get_axis_labels'" → "Try: labels = axes.get_axis_labels()"

3. **Render progress bar** (4 hours)
   - Stream Manim's stdout → show "Rendering frame 42/120..."
   - Requires async subprocess instead of programmatic rendering

### Medium Effort (Better Architecture)

4. **RAG with embeddings** (1-2 days)
   - Embed all examples with sentence-transformers
   - Semantic search: "show derivative" finds calculus examples even without keyword "derivative"
   - Use FAISS or ChromaDB

5. **Multi-attempt error fixing** (1 day)
   - Allow 2-3 fix iterations before giving up
   - Track what was tried → avoid repeating failed approaches

6. **Code validation before render** (2 days)
   - Parse AST → check for banned imports (os, subprocess)
   - Static analysis → catch syntax errors without running Manim
   - Estimate render time from scene complexity

### High Effort (New Features)

7. **Manim version selector** (1 week)
   - Support v0.17.x, v0.18.x, latest
   - LLM chooses API calls based on version
   - Docker containers for each version

8. **Prompt-to-prompt diffing** (1 week)
   - "Take the last animation but make the circle blue"
   - Read previous `scene.py` → apply minimal diff
   - Requires state tracking

9. **Multi-scene animations** (2 weeks)
   - "First show a parabola, then its derivative, then zoom out"
   - Generate multiple scenes → concat videos
   - Needs timeline planning

### Research-Level (Hard Problems)

10. **Fine-tune LLM on Manim code** (months)
    - Scrape GitHub for Manim projects → build dataset
    - Fine-tune Codex/StarCoder on Manim patterns
    - Could reduce hallucinations, improve API usage

11. **Visual feedback loop** (months)
    - Show LLM a screenshot of the rendered video
    - "Does this match the prompt?" → iterate if not
    - Requires vision model + video → frame extraction

12. **Interactive editing** (months)
    - Live code editor with instant preview
    - Manim's `--save_last_frame` for fast iteration
    - Monaco editor + LSP server for autocomplete

---

## Why Not Use Docker?

**Original plan**: Sandbox renders in Docker containers.

**Reality**: Programmatic rendering is faster and simpler:
- No subprocess overhead (shaves 2-3 seconds)
- Direct access to Manim objects (can introspect Scene)
- Easier debugging (errors are Python exceptions, not container crashes)
- Windows file lock issues with Docker volumes

**Trade-off**: Less isolation. But for local use with trusted prompts, acceptable.

---

## Key Insight

> **You don't need perfect retrieval or a huge example library.**
> 5-10 well-chosen examples + strict LLM rules = 70% success rate.
> The trick is making errors recoverable (one-click fix) so users iterate quickly.

The system is **deliberately minimal**. Every feature is questioned: "Can we ship without this?"

- No database → filesystem
- No embeddings → keyword search
- No Docker → programmatic render
- No auth → local only

This keeps complexity low and makes the system easy to understand, debug, and extend.

---

## Tech Stack Summary

| Component | Choice | Why |
|-----------|--------|-----|
| LLM | Claude Sonnet 4.5 | Best at following strict rules (JSON output, API constraints) |
| Backend | FastAPI | Async, fast, Python-native |
| Rendering | Manim Community v0.18.0 | Programmatic API, active community |
| Examples | Filesystem (JSON + .py files) | No DB needed, easy to edit |
| Search | Keyword scoring | Good enough for 5-10 examples |
| Frontend | Vanilla JS | Zero build step, instant load |

**Total LOC**: ~1500 lines (excluding examples)

---

## Success Metrics (Observed)

- **Generation success rate**: ~70% (first try)
- **Fix success rate**: ~50% (if first attempt fails)
- **Average render time**: 15-25 seconds
- **Time to add new example**: 30 minutes
- **Learning curve**: <10 minutes (if you know Manim basics)

---

## When This Breaks

**LLM hallucinates APIs**:
- Manim Community ≠ 3b1b/manim (legacy)
- Sometimes Claude mixes them up
- Fix: Add more v0.18.0 examples, stronger system prompt

**LaTeX errors**:
- User asks for "show equation x^2 + y^2 = r^2"
- LLM tries to use Text/MathTex → crash
- Fix: System prompt explicitly bans LaTeX, but LLM sometimes ignores it

**Complex animations**:
- "Show Fourier series with 20 terms"
- Generates slow, memory-hungry code
- No timeout → hangs for minutes
- Fix: Add render timeout, prompt LLM to keep it simple

---

## Bottom Line

This is a **proof of concept** that LLMs can write Manim code if you:
1. Give them working examples
2. Constrain the API surface (no LaTeX)
3. Make errors visible and fixable

It's not production-ready, but it's a solid foundation for experimentation.

**Use it to**: Quickly prototype Manim animations without writing code.
**Don't use it for**: Mission-critical renders, batch processing, multi-user deployments.

---

**Last updated**: 2026-02-10
