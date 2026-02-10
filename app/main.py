"""
FastAPI server for Manim web app.
"""
import os
import json
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.generator import ManimGenerator
from app.renderer import ManimRenderer
from app.examples import ExampleManager

# Setup paths
BASE_DIR = Path(__file__).parent.parent
GENERATED_DIR = BASE_DIR / "generated"
GENERATED_DIR.mkdir(exist_ok=True)

# Initialize FastAPI
app = FastAPI(title="Tiny Manim Web App")

# Templates
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

# Initialize components
generator = ManimGenerator()
renderer = ManimRenderer()
examples_manager = ExampleManager()


# Request/Response models
class GenerateRequest(BaseModel):
    prompt: str
    example_ids: Optional[List[str]] = None


class FixRequest(BaseModel):
    prompt: str
    traceback: str


class GenerateResponse(BaseModel):
    status: str
    video_url: Optional[str] = None
    plan: Optional[str] = None
    errors: Optional[str] = None
    code: Optional[str] = None


# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main UI page."""
    examples = examples_manager.list_examples()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "examples": examples}
    )


@app.get("/examples")
async def list_examples():
    """Return list of available examples with metadata."""
    return examples_manager.list_examples()


@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    """
    Generate Manim animation from prompt.

    1. Retrieve relevant examples
    2. Generate code using LLM
    3. Write to generated/scene.py
    4. Render using local Manim
    5. Return video URL
    """
    try:
        # Load selected examples
        example_snippets = []
        if req.example_ids:
            for ex_id in req.example_ids:
                snippet = examples_manager.get_example(ex_id)
                if snippet:
                    example_snippets.append(snippet)

        # If no examples selected, do basic keyword matching
        if not example_snippets:
            example_snippets = examples_manager.search_examples(req.prompt, max_results=2)

        # Generate code
        result = await generator.generate(req.prompt, example_snippets)

        if result["status"] == "error":
            return GenerateResponse(
                status="error",
                errors=result["error"]
            )

        # Write scene code
        scene_path = GENERATED_DIR / "scene.py"
        scene_path.write_text(result["scene_code"], encoding="utf-8")

        # Render
        render_result = await renderer.render(scene_path)

        if render_result["status"] == "error":
            return GenerateResponse(
                status="error",
                errors=render_result["error"],
                code=result["scene_code"],
                plan=result["plan"]
            )

        return GenerateResponse(
            status="success",
            video_url=f"/video/latest.mp4?t={os.path.getmtime(render_result['video_path'])}",
            plan=result["plan"],
            code=result["scene_code"]
        )

    except Exception as e:
        return GenerateResponse(
            status="error",
            errors=str(e)
        )


@app.post("/fix", response_model=GenerateResponse)
async def fix_error(req: FixRequest):
    """
    Fix compilation error by applying minimal patch.

    1. Send traceback to LLM
    2. Get unified diff patch
    3. Apply patch to generated/scene.py
    4. Re-render
    5. Return result
    """
    try:
        scene_path = GENERATED_DIR / "scene.py"

        if not scene_path.exists():
            raise HTTPException(status_code=400, detail="No scene file to fix")

        original_code = scene_path.read_text()

        # Generate fix
        fix_result = await generator.fix_error(
            original_code=original_code,
            prompt=req.prompt,
            traceback=req.traceback
        )

        if fix_result["status"] == "error":
            return GenerateResponse(
                status="error",
                errors=fix_result["error"]
            )

        # Write fixed code
        scene_path.write_text(fix_result["fixed_code"], encoding="utf-8")

        # Re-render
        render_result = await renderer.render(scene_path)

        if render_result["status"] == "error":
            return GenerateResponse(
                status="error",
                errors=render_result["error"],
                code=fix_result["fixed_code"]
            )

        return GenerateResponse(
            status="success",
            video_url=f"/video/latest.mp4?t={os.path.getmtime(render_result['video_path'])}",
            code=fix_result["fixed_code"]
        )

    except Exception as e:
        return GenerateResponse(
            status="error",
            errors=str(e)
        )


@app.get("/video/latest.mp4")
async def serve_video():
    """Serve the most recently rendered video."""
    video_path = GENERATED_DIR / "latest.mp4"

    if not video_path.exists():
        raise HTTPException(status_code=404, detail="No video available")

    return FileResponse(
        video_path,
        media_type="video/mp4",
        headers={"Cache-Control": "no-cache"}
    )


if __name__ == "__main__":
    import uvicorn

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("Please set it with: export ANTHROPIC_API_KEY='your-key-here'")
        exit(1)

    print("\n" + "="*60)
    print("Starting Tiny Manim Web App")
    print("="*60)
    print(f"Server: http://localhost:8000")
    print(f"Generated files: {GENERATED_DIR}")
    print("="*60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
