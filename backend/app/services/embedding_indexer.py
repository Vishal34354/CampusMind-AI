from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.material_chunk import MaterialChunk
from app.services.embedding_service import EmbeddingService


class EmbeddingIndexer:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()

    def index_material(
        self,
        material_id: UUID,
        batch_size: int = 64,
    ) -> int:
        statement = (
            select(MaterialChunk)
            .where(
                MaterialChunk.material_id == material_id,
                MaterialChunk.embedding.is_(None),
            )
            .order_by(MaterialChunk.chunk_index)
        )

        chunks = list(self.db.scalars(statement).all())

        if not chunks:
            return 0

        total_indexed = 0

        for start in range(0, len(chunks), batch_size):
            batch = chunks[start:start + batch_size]

            texts = [chunk.content for chunk in batch]

            embeddings = self.embedding_service.embed_texts(texts)

            for chunk, embedding in zip(batch, embeddings):
                chunk.embedding = embedding

            self.db.commit()

            total_indexed += len(batch)

            print(
                f"Indexed {total_indexed}/{len(chunks)} chunks"
            )

        return total_indexed