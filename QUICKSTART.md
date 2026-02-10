# Quick Start - TL;DR

Get running in 2 minutes.

## Prerequisites
- Python 3.10+
- Anthropic API key

## Setup (One Time)

```bash
# 1. Create .env file with your API key
echo "ANTHROPIC_API_KEY=your-key-here" > .env

# 2. Install dependencies (includes Manim)
pip install -r requirements.txt
```

## Run

```bash
# Start server
python -m app.main

# Open browser
# http://localhost:8000
```

Or use quick start scripts:
- Windows: `start.bat`
- Mac/Linux: `./start.sh`

## Try It

Enter a prompt like:
```
Plot y = sin(x) on axes and animate a dot moving along it
```

Click **Generate Animation** and wait 1-2 minutes.

## If It Breaks

```bash
# Server issues?
python test_smoke.py

# Clean slate
rm -rf generated/
```

## Common Commands

```bash
# Start server
python -m app.main

# Test full system (server must be running)
python test_smoke.py

# Clean generated files
rm -rf generated/
```

## Keyboard Shortcuts

In the web UI:
- `Ctrl+Enter` in prompt box = Generate

## Prompt Tips

Good prompts:
- "Plot y = sin(x) on axes"
- "Show Riemann rectangles under y = x^2 from 0 to 2"
- "Animate a circle transforming into a square"
- "Create a moving dot along a sine curve"

Bad prompts (too vague):
- "Make something cool"
- "Animation"
- "Math"

## Debugging

If generation fails:
1. Click **Fix Error** button
2. Check Debug Info panel for errors
3. Look at `generated/scene.py` for the code
4. Check `generated/media/` for render logs

## File Locations

- **Generated code:** `generated/scene.py`
- **Latest video:** `generated/latest.mp4`
- **Examples:** `examples/`
- **Logs:** Terminal output

## That's It

You're ready to generate animations. See README.md for more details.
