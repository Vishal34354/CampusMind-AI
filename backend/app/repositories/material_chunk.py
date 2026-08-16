import uuid

from sqlalchemy.orm import Session

from app.models.material_chunk import MaterialChunk


class MaterialChunkRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_many(
        self,
        material_id: uuid.UUID,
        chunks: list[str],
    ) -> list[MaterialChunk]:

        chunk_objects = [
            MaterialChunk(
                material_id=material_id,
                chunk_index=index,
                content=content,
            )
            for index, content in enumerate(chunks)
        ]

        self.db.add_all(chunk_objects)
        self.db.commit()

        return chunk_objects