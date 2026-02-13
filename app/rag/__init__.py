"""
RAG (Retrieval-Augmented Generation) module for Manim code generation.

Uses ChromaDB for vector storage and Voyage AI for embeddings.
"""
import os
from pathlib import Path

# Paths
CHROMA_DB_PATH = str(Path(__file__).parent.parent.parent / "chroma_db")

# Voyage AI config
VOYAGE_MODEL = "voyage-code-3"
VOYAGE_API_KEY_ENV = "VOYAGE_API_KEY"

# ChromaDB collection names
COLLECTION_MANIM_API = "manim_api"
COLLECTION_MANIM_EXAMPLES = "manim_examples"

# Retrieval defaults
DEFAULT_TOP_K_API = 10
DEFAULT_TOP_K_EXAMPLES = 5
