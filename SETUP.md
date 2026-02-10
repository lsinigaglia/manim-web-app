# Setup Guide

Complete setup instructions for the Tiny Manim Web App.

## Prerequisites

Before starting, ensure you have:

1. **Python 3.10 or newer**
   - Check: `python --version`
   - Download: https://www.python.org/downloads/

2. **Anthropic API Key**
   - Get one at: https://console.anthropic.com/
   - You'll need API access to Claude

## Installation Steps

### Step 1: Create .env File

Create a `.env` file in the project root with your API key:

```
ANTHROPIC_API_KEY=your_api_key_here
```

You can copy from the example:
```bash
cp .env.example .env
```
Then edit `.env` and add your API key.

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Anthropic SDK (for Claude API)
- Jinja2 (templating)
- Manim Community v0.18.0 (animation engine)

## Running the Application

### Quick Start

**Windows:**
```cmd
start.bat
```

**macOS/Linux:**
```bash
bash start.sh
```

### Manual Start

```bash
python -m app.main
```

Then open your browser to: **http://localhost:8000**

## Verifying Installation

Run the smoke tests (requires server to be running in another terminal):

```bash
python test_smoke.py
```

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
- Make sure you have a `.env` file in the project root
- Check that the API key is correctly set in the `.env` file
- Verify the `.env` file contains: `ANTHROPIC_API_KEY=your_api_key_here`

### "Module not found" errors
- Reinstall dependencies: `pip install -r requirements.txt`
- Make sure you're in the project directory
- Check Python version: `python --version` (needs 3.10+)

### Manim installation issues
- On Windows, you may need to install Cairo, Pango, and FFmpeg
- See Manim installation guide: https://docs.manim.community/en/stable/installation.html
- Consider using Windows Subsystem for Linux (WSL) for easier Manim installation

### Video doesn't render
1. Look at `generated/` folder for error logs
2. Check terminal output for Manim errors
3. Verify that generated/scene.py has valid Python syntax
4. Test Manim directly: `manim -qm generated/scene.py SceneName`

### Port 8000 already in use
- Change port in `app/main.py` (last line, `port=8000`)
- Or kill the process using port 8000

## Project Structure

```
manim-web-app/
├── app/                      # FastAPI application
│   ├── __init__.py
│   ├── main.py              # Server + routes
│   ├── generator.py         # LLM code generation
│   ├── renderer.py          # Local Manim rendering
│   ├── examples.py          # Example management
│   └── templates/
│       └── index.html       # Web UI
├── examples/                # Curated Manim examples
│   ├── 01_axes_plot/
│   ├── 02_riemann_sums/
│   ├── 03_vector_addition/
│   ├── 04_transform_shapes/
│   └── 05_moving_dot/
├── generated/               # Output (gitignored)
│   ├── scene.py            # Generated code
│   ├── latest.mp4          # Latest video
│   └── media/              # Manim output
├── requirements.txt
├── .env                     # API key (not in git)
├── .env.example             # Template for .env
├── test_smoke.py           # Full system test
├── start.sh / start.bat    # Quick start scripts
└── README.md

```

## Next Steps

Once running:

1. Try the smoke test prompts from README.md
2. Experiment with the example selector
3. Use the "Fix Error" button if compilation fails
4. Check `generated/scene.py` to see the LLM-generated code

## Development

To modify examples:
- Add new folders in `examples/`
- Include `example.py`, `meta.json`, and `notes.md`
- Restart server to load new examples

To modify UI:
- Edit `app/templates/index.html`
- Refresh browser (no restart needed for templates)

To change LLM behavior:
- Edit system prompts in `app/generator.py`
- Modify `_build_system_prompt()` method

## Security Notes

Generated code runs locally with:
- 2-minute timeout limit
- Execution in a separate subprocess

Be cautious when running code from untrusted sources.
