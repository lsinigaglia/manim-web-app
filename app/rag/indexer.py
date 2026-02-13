"""
Manim RAG indexer — builds ChromaDB collections from Manim source and curated examples.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

import chromadb

from app.rag import (
    CHROMA_DB_PATH,
    COLLECTION_MANIM_API,
    COLLECTION_MANIM_EXAMPLES,
)
from app.rag.embeddings import VoyageEmbeddingFunction
from app.rag.chunker import ManimChunker

logger = logging.getLogger(__name__)

BATCH_SIZE = 100


class ManimIndexer:
    """Builds and manages ChromaDB collections for Manim RAG."""

    def __init__(self, embedding_fn: VoyageEmbeddingFunction = None):
        self.embedding_fn = embedding_fn or VoyageEmbeddingFunction()
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    def index_exists(self) -> bool:
        """Check if both collections already exist and have data."""
        try:
            api_col = self.client.get_collection(COLLECTION_MANIM_API)
            ex_col = self.client.get_collection(COLLECTION_MANIM_EXAMPLES)
            return api_col.count() > 0 and ex_col.count() > 0
        except Exception:
            return False

    def build_index(self, rebuild: bool = False) -> Dict[str, int]:
        """
        Build the full index. Returns counts of indexed items.

        Args:
            rebuild: If True, delete existing collections and rebuild from scratch.
        """
        if rebuild:
            self._delete_collections()
        elif self.index_exists():
            api_count = self.client.get_collection(COLLECTION_MANIM_API).count()
            ex_count = self.client.get_collection(COLLECTION_MANIM_EXAMPLES).count()
            logger.info(f"Using existing index ({api_count} API chunks, {ex_count} examples)")
            return {"api_chunks": api_count, "examples": ex_count}

        # Build API collection
        api_count = self._index_manim_api()

        # Build examples collection
        ex_count = self._index_examples()

        logger.info(f"Indexed {api_count} API chunks, {ex_count} examples")
        return {"api_chunks": api_count, "examples": ex_count}

    def _delete_collections(self):
        """Delete existing collections."""
        for name in [COLLECTION_MANIM_API, COLLECTION_MANIM_EXAMPLES]:
            try:
                self.client.delete_collection(name)
            except Exception:
                pass

    def _index_manim_api(self) -> int:
        """Index Manim library source into the API collection."""
        collection = self.client.get_or_create_collection(
            name=COLLECTION_MANIM_API,
            embedding_function=self.embedding_fn,
        )

        chunker = ManimChunker()
        chunks = chunker.extract_chunks()

        if not chunks:
            logger.warning("No Manim API chunks extracted")
            return 0

        # Batch insert
        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i : i + BATCH_SIZE]
            collection.add(
                ids=[c["id"] for c in batch],
                documents=[c["content"] for c in batch],
                metadatas=[
                    {
                        "type": c["type"],
                        "name": c["name"],
                        "module": c["module"],
                        "bases": json.dumps(c["bases"]),
                        "methods": json.dumps(c["methods"][:20]),  # Cap method list
                    }
                    for c in batch
                ],
            )

        return len(chunks)

    def _index_examples(self) -> int:
        """Index curated examples into the examples collection."""
        collection = self.client.get_or_create_collection(
            name=COLLECTION_MANIM_EXAMPLES,
            embedding_function=self.embedding_fn,
        )

        examples_dir = Path(__file__).parent.parent.parent / "examples"
        if not examples_dir.exists():
            logger.warning(f"Examples directory not found: {examples_dir}")
            return 0

        count = 0
        ids = []
        documents = []
        metadatas = []

        for example_dir in sorted(examples_dir.iterdir()):
            if not example_dir.is_dir():
                continue

            code_file = example_dir / "example.py"
            meta_file = example_dir / "meta.json"
            notes_file = example_dir / "notes.md"

            if not code_file.exists():
                continue

            # Load data
            code = code_file.read_text(encoding="utf-8", errors="ignore")
            meta = {}
            if meta_file.exists():
                try:
                    meta = json.loads(meta_file.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    pass

            notes = ""
            if notes_file.exists():
                notes = notes_file.read_text(encoding="utf-8", errors="ignore")

            name = meta.get("name", example_dir.name)
            tags = meta.get("tags", [])
            description = meta.get("description", "")

            # Build document text for embedding
            doc_text = f"Example: {name}\n"
            if description:
                doc_text += f"Description: {description}\n"
            if tags:
                doc_text += f"Tags: {', '.join(tags)}\n"
            doc_text += f"\nCode:\n{code}"
            if notes:
                doc_text += f"\n\nNotes:\n{notes}"

            ids.append(example_dir.name)
            documents.append(doc_text)
            metadatas.append({
                "name": name,
                "tags": json.dumps(tags),
                "difficulty": meta.get("difficulty", "medium"),
                "description": description,
                "code": code,
                "notes": notes,
            })
            count += 1

        # Batch insert
        if ids:
            for i in range(0, len(ids), BATCH_SIZE):
                end = i + BATCH_SIZE
                collection.add(
                    ids=ids[i:end],
                    documents=documents[i:end],
                    metadatas=metadatas[i:end],
                )

        return count
