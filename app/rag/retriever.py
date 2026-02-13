"""
RAG retriever — searches ChromaDB collections for relevant Manim API refs and examples.
"""
import json
import logging
from typing import List, Dict, Any, Optional

import chromadb

from app.rag import (
    CHROMA_DB_PATH,
    COLLECTION_MANIM_API,
    COLLECTION_MANIM_EXAMPLES,
    DEFAULT_TOP_K_API,
    DEFAULT_TOP_K_EXAMPLES,
)
from app.rag.embeddings import VoyageEmbeddingFunction
from app.rag.indexer import ManimIndexer

logger = logging.getLogger(__name__)


class RAGRetriever:
    """Main search interface for Manim RAG."""

    def __init__(self):
        self._initialized = False
        self._client = None
        self._embedding_fn = None
        self._api_collection = None
        self._examples_collection = None

    def initialize(self, rebuild: bool = False) -> Dict[str, int]:
        """
        Initialize the retriever: build or load the index.

        Returns counts of indexed items.
        """
        self._embedding_fn = VoyageEmbeddingFunction()
        self._client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

        # Build index if needed
        indexer = ManimIndexer(embedding_fn=self._embedding_fn)
        counts = indexer.build_index(rebuild=rebuild)

        # Get collection references
        self._api_collection = self._client.get_collection(
            name=COLLECTION_MANIM_API,
            embedding_function=self._embedding_fn,
        )
        self._examples_collection = self._client.get_collection(
            name=COLLECTION_MANIM_EXAMPLES,
            embedding_function=self._embedding_fn,
        )

        self._initialized = True
        logger.info("RAG retriever initialized")
        return counts

    @property
    def is_ready(self) -> bool:
        return self._initialized

    def search(
        self,
        query: str,
        top_k_api: int = DEFAULT_TOP_K_API,
        top_k_examples: int = DEFAULT_TOP_K_EXAMPLES,
    ) -> Dict[str, Any]:
        """
        Search both collections for relevant results.

        Returns:
            {
                "api_refs": [{"name", "module", "content", "score"}, ...],
                "examples": [{"id", "name", "code", "notes", "tags", "score"}, ...],
            }
        """
        if not self._initialized:
            raise RuntimeError("RAG retriever not initialized. Call initialize() first.")

        api_refs = self._search_api(query, top_k_api)
        examples = self._search_examples(query, top_k_examples)

        return {
            "api_refs": api_refs,
            "examples": examples,
        }

    def _search_api(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Search the Manim API collection."""
        try:
            results = self._api_collection.query(
                query_texts=[query],
                n_results=top_k,
            )
        except Exception as e:
            logger.error(f"API search failed: {e}")
            return []

        refs = []
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i] if results.get("distances") else 0
                metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                document = results["documents"][0][i] if results.get("documents") else ""

                refs.append({
                    "id": doc_id,
                    "name": metadata.get("name", ""),
                    "module": metadata.get("module", ""),
                    "type": metadata.get("type", ""),
                    "content": document,
                    "score": 1.0 - distance,  # Convert distance to similarity
                })

        return refs

    def _search_examples(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Search the curated examples collection."""
        try:
            results = self._examples_collection.query(
                query_texts=[query],
                n_results=top_k,
            )
        except Exception as e:
            logger.error(f"Examples search failed: {e}")
            return []

        examples = []
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i] if results.get("distances") else 0
                metadata = results["metadatas"][0][i] if results.get("metadatas") else {}

                tags = []
                if metadata.get("tags"):
                    try:
                        tags = json.loads(metadata["tags"])
                    except (json.JSONDecodeError, TypeError):
                        pass

                examples.append({
                    "id": doc_id,
                    "name": metadata.get("name", doc_id),
                    "code": metadata.get("code", ""),
                    "notes": metadata.get("notes", ""),
                    "tags": tags,
                    "description": metadata.get("description", ""),
                    "score": 1.0 - distance,
                })

        return examples
