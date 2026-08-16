import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.material_chunk import MaterialChunk
from app.services.embedding_service import EmbeddingService


class SemanticSearchService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()

    def search(
        self,
        material_id,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:

        statement = (
            select(MaterialChunk)
            .where(
                MaterialChunk.material_id == material_id,
                MaterialChunk.embedding.is_not(None),
            )
            .order_by(MaterialChunk.chunk_index)
        )

        chunks = list(
            self.db.scalars(statement).all()
        )

        if not chunks:
            return []

        # Only the QUESTION gets embedded now
        query_embedding = np.array(
            self.embedding_service.embed_text(query),
            dtype=np.float32,
        )

        # Existing embeddings come directly from PostgreSQL
        chunk_embeddings = np.array(
            [chunk.embedding for chunk in chunks],
            dtype=np.float32,
        )

        # Embeddings were normalized during generation,
        # so dot product = cosine similarity
        scores = chunk_embeddings @ query_embedding

        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []

        for index in top_indices:
            chunk = chunks[index]

            results.append(
                {
                    "chunk_index": chunk.chunk_index,
                    "score": float(scores[index]),
                    "content": chunk.content,
                }
            )

        return results