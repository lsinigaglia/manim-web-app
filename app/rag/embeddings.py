"""
Voyage AI embedding function for ChromaDB.
"""
import os
from typing import List

from chromadb.api.types import EmbeddingFunction, Documents, Embeddings

from app.rag import VOYAGE_MODEL, VOYAGE_API_KEY_ENV


class VoyageEmbeddingFunction(EmbeddingFunction):
    """ChromaDB-compatible embedding function using Voyage AI."""

    def __init__(self, model: str = VOYAGE_MODEL, api_key: str = None):
        import voyageai

        self.api_key = api_key or os.getenv(VOYAGE_API_KEY_ENV)
        if not self.api_key:
            raise ValueError(
                f"{VOYAGE_API_KEY_ENV} environment variable not set. "
                "Get your key at https://dash.voyageai.com/"
            )
        self.client = voyageai.Client(api_key=self.api_key)
        self.model = model

    def __call__(self, input: Documents) -> Embeddings:
        """Embed a list of documents."""
        if not input:
            return []

        # Voyage AI has a batch limit; process in chunks of 128
        all_embeddings = []
        for i in range(0, len(input), 128):
            batch = input[i : i + 128]
            result = self.client.embed(batch, model=self.model, input_type="document")
            all_embeddings.extend(result.embeddings)

        return all_embeddings
