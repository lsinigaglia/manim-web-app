"""
Example management and retrieval.
"""
import json
from pathlib import Path
from typing import List, Dict, Any


class ExampleManager:
    """Manages curated Manim examples."""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.examples_dir = self.base_dir / "examples"
        self.examples_dir.mkdir(exist_ok=True)
        self._cache = None

    def list_examples(self) -> List[Dict[str, Any]]:
        """Return list of all examples with metadata."""
        if self._cache is None:
            self._cache = self._load_all_examples()
        return self._cache

    def get_example(self, example_id: str) -> Dict[str, Any]:
        """Get a specific example by ID."""
        examples = self.list_examples()
        for ex in examples:
            if ex["id"] == example_id:
                return ex
        return None

    def search_examples(self, query: str, max_results: int = 2) -> List[Dict[str, Any]]:
        """
        Simple keyword-based example search.

        Matches against:
        - Example name
        - Tags
        - Notes
        """
        query_lower = query.lower()
        examples = self.list_examples()

        # Score each example
        scored = []
        for ex in examples:
            score = 0

            # Check name
            if query_lower in ex["name"].lower():
                score += 10

            # Check tags
            for tag in ex.get("tags", []):
                if query_lower in tag.lower():
                    score += 5

            # Check notes
            notes = ex.get("notes", "")
            if query_lower in notes.lower():
                score += 2

            # Keyword matching
            keywords = ["plot", "graph", "axes", "function", "transform", "animate",
                       "circle", "square", "vector", "arrow", "text", "label",
                       "riemann", "integral", "derivative", "tangent"]

            for keyword in keywords:
                if keyword in query_lower and keyword in ex["name"].lower():
                    score += 3

            if score > 0:
                scored.append((score, ex))

        # Sort by score and return top results
        scored.sort(reverse=True, key=lambda x: x[0])
        return [ex for score, ex in scored[:max_results]]

    def _load_all_examples(self) -> List[Dict[str, Any]]:
        """Load all examples from disk."""
        examples = []

        for example_dir in sorted(self.examples_dir.iterdir()):
            if not example_dir.is_dir():
                continue

            meta_file = example_dir / "meta.json"
            code_file = example_dir / "example.py"
            notes_file = example_dir / "notes.md"

            if not code_file.exists():
                continue

            # Load metadata
            meta = {}
            if meta_file.exists():
                try:
                    meta = json.loads(meta_file.read_text())
                except json.JSONDecodeError:
                    pass

            # Load code
            code = code_file.read_text()

            # Load notes
            notes = ""
            if notes_file.exists():
                notes = notes_file.read_text()

            examples.append({
                "id": example_dir.name,
                "name": meta.get("name", example_dir.name),
                "tags": meta.get("tags", []),
                "difficulty": meta.get("difficulty", "medium"),
                "description": meta.get("description", ""),
                "code": code,
                "notes": notes
            })

        return examples
