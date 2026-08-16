import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.repositories.material_chunk import MaterialChunkRepository
from app.services.pdf_extractor import PDFExtractor
from app.services.text_chunker import TextChunker


class MaterialProcessor:

    def __init__(self, db: Session):
        self.db = db
        self.chunk_repository = MaterialChunkRepository(db)

    def process_pdf(
        self,
        material_id: uuid.UUID,
        file_path: str | Path,
    ) -> int:

        text = PDFExtractor.extract_text(file_path)

        if not text:
            raise ValueError("No text could be extracted from PDF")

        chunks = TextChunker.chunk_text(text)

        if not chunks:
            raise ValueError("No chunks were generated from PDF")

        self.chunk_repository.create_many(
            material_id=material_id,
            chunks=chunks,
        )

        return len(chunks)