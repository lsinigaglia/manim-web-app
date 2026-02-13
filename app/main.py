"""
FastAPI server for Manim web app.
"""
import os
import json
import logging
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

logger = logging.getLogger(__name__)

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

# RAG retriever (initialized on startup if VOYAGE_API_KEY is set)
rag_retriever = None


@app.on_event("startup")
async def startup_event():
    """Initialize RAG retriever on startup if Voyage API key is available."""
    global rag_retriever

    voyage_key = os.getenv("VOYAGE_API_KEY")
    if not voyage_key:
        logger.warning(
            "VOYAGE_API_KEY not set — RAG disabled, falling back to keyword search. "
            "Set VOYAGE_API_KEY in .env to enable semantic search."
        )
        return

    try:
        from app.rag.retriever import RAGRetriever

        rag_retriever = RAGRetriever()
        counts = rag_retriever.initialize()
        logger.info(
            f"RAG initialized: {counts.get('api_chunks', 0)} API chunks, "
            f"{counts.get('examples', 0)} examples indexed"
        )
        print(
            f"[RAG] Indexed {counts.get('api_chunks', 0)} API chunks, "
            f"{counts.get('examples', 0)} examples"
        )
    except Exception as e:
        logger.error(f"RAG initialization failed: {e}")
        print(f"[RAG] Init failed: {e} — falling back to keyword search")
        rag_retriever = None


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

    1. Retrieve relevant examples + API refs (RAG or keyword fallback)
    2. Generate code using LLM
    3. Write to generated/scene.py
    4. Render using local Manim
    5. Return video URL
    """
    try:
        example_snippets = []
        api_refs = None

        # If user explicitly selected examples, use those
        if req.example_ids:
            for ex_id in req.example_ids:
                snippet = examples_manager.get_example(ex_id)
                if snippet:
                    example_snippets.append(snippet)

        # Otherwise, use RAG search or fall back to keyword search
        if not example_snippets:
            if rag_retriever and rag_retriever.is_ready:
                try:
                    rag_results = rag_retriever.search(req.prompt)
                    example_snippets = rag_results.get("examples", [])
                    api_refs = rag_results.get("api_refs", [])
                    logger.info(
                        f"RAG search: {len(example_snippets)} examples, "
                        f"{len(api_refs)} API refs"
                    )
                except Exception as e:
                    logger.warning(f"RAG search failed, falling back to keywords: {e}")
                    example_snippets = examples_manager.search_examples(
                        req.prompt, max_results=5
                    )
            else:
                example_snippets = examples_manager.search_examples(
                    req.prompt, max_results=5
                )

        # Generate code
        result = await generator.generate(req.prompt, example_snippets, api_refs=api_refs)

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


@app.post("/admin/rebuild-index")
async def rebuild_index():
    """Force rebuild the RAG index from scratch."""
    global rag_retriever

    if not os.getenv("VOYAGE_API_KEY"):
        raise HTTPException(
            status_code=400,
            detail="VOYAGE_API_KEY not set. Cannot rebuild index."
        )

    try:
        from app.rag.retriever import RAGRetriever

        rag_retriever = RAGRetriever()
        counts = rag_retriever.initialize(rebuild=True)
        return {
            "status": "success",
            "message": f"Index rebuilt: {counts.get('api_chunks', 0)} API chunks, "
                       f"{counts.get('examples', 0)} examples",
            "counts": counts,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rebuild failed: {str(e)}")


@app.get("/rag/browse", response_class=HTMLResponse)
async def rag_browse(request: Request, collection: str = "examples", page: int = 1, per_page: int = 50):
    """Browse the ChromaDB RAG database as HTML tables."""
    import chromadb
    import json as _json

    try:
        client = chromadb.PersistentClient(path=str(BASE_DIR / "chroma_db"))
    except Exception as e:
        return HTMLResponse(f"<h1>DB Error</h1><pre>{e}</pre>", status_code=500)

    collections_info = []
    for col in client.list_collections():
        collections_info.append({"name": col.name, "count": col.count()})

    col_name = {
        "examples": "manim_examples",
        "api": "manim_api",
    }.get(collection, "manim_examples")

    try:
        col_obj = client.get_collection(col_name)
    except Exception:
        return HTMLResponse(f"<h1>Collection '{col_name}' not found</h1>", status_code=404)

    total = col_obj.count()
    offset = (page - 1) * per_page
    results = col_obj.get(limit=per_page, offset=offset, include=["documents", "metadatas"])

    rows = []
    for doc_id, meta, doc in zip(results["ids"], results["metadatas"], results["documents"]):
        row = {"id": doc_id, **meta, "_document": doc[:300] + ("..." if len(doc) > 300 else "")}
        # Parse JSON tags if present
        if "tags" in row:
            try:
                row["tags"] = ", ".join(_json.loads(row["tags"]))
            except Exception:
                pass
        rows.append(row)

    # Build all column names from all rows
    all_keys = []
    seen = set()
    for r in rows:
        for k in r:
            if k not in seen:
                all_keys.append(k)
                seen.add(k)

    total_pages = (total + per_page - 1) // per_page

    # Render HTML
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>RAG Database Browser</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 20px; background: #f5f5f5; }}
  h1 {{ color: #333; }}
  .tabs {{ display: flex; gap: 8px; margin: 16px 0; }}
  .tabs a {{ padding: 8px 16px; background: #ddd; border-radius: 6px; text-decoration: none; color: #333; font-weight: 500; }}
  .tabs a.active {{ background: #4a90d9; color: white; }}
  .info {{ color: #666; margin-bottom: 12px; }}
  table {{ border-collapse: collapse; width: 100%; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  th {{ background: #4a90d9; color: white; padding: 10px 12px; text-align: left; font-size: 13px; white-space: nowrap; }}
  td {{ padding: 8px 12px; border-bottom: 1px solid #eee; font-size: 13px; max-width: 400px; overflow: hidden; text-overflow: ellipsis; }}
  tr:hover {{ background: #f0f7ff; }}
  .pagination {{ margin: 16px 0; display: flex; gap: 8px; }}
  .pagination a {{ padding: 6px 14px; background: #ddd; border-radius: 4px; text-decoration: none; color: #333; }}
  .pagination a.active {{ background: #4a90d9; color: white; }}
  .stats {{ display: flex; gap: 16px; margin: 12px 0; }}
  .stat {{ background: white; padding: 12px 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  .stat b {{ font-size: 20px; color: #4a90d9; }}
</style></head><body>
<h1>RAG Database Browser</h1>
<div class="stats">"""
    for ci in collections_info:
        html += f'<div class="stat"><b>{ci["count"]}</b><br>{ci["name"]}</div>'
    html += '</div><div class="tabs">'
    for tab_key, tab_label in [("examples", "Examples"), ("api", "API Chunks")]:
        active = "active" if tab_key == collection else ""
        html += f'<a href="/rag/browse?collection={tab_key}" class="{active}">{tab_label}</a>'
    html += f'</div><div class="info">Showing {offset+1}-{min(offset+per_page, total)} of {total} rows</div>'
    html += '<div style="overflow-x:auto"><table><tr>'
    for k in all_keys:
        html += f"<th>{k}</th>"
    html += "</tr>"
    for r in rows:
        html += "<tr>"
        for k in all_keys:
            val = str(r.get(k, ""))
            # Escape HTML
            val = val.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if len(val) > 120:
                val = val[:120] + "..."
            html += f"<td title='{val}'>{val}</td>"
        html += "</tr>"
    html += "</table></div>"

    if total_pages > 1:
        html += '<div class="pagination">'
        for p in range(1, total_pages + 1):
            active = "active" if p == page else ""
            html += f'<a href="/rag/browse?collection={collection}&page={p}" class="{active}">{p}</a>'
        html += "</div>"
    html += "</body></html>"
    return HTMLResponse(html)


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
    if os.getenv("VOYAGE_API_KEY"):
        print("RAG: Enabled (Voyage AI + ChromaDB)")
    else:
        print("RAG: Disabled (set VOYAGE_API_KEY to enable)")
    print("="*60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
