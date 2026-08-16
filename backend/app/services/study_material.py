import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.study_material import StudyMaterial
from app.models.user import User
from app.repositories.study_material import StudyMaterialRepository


class StudyMaterialService:
    ALLOWED_CONTENT_TYPES = {
        "application/pdf",
    }

    def __init__(self, db: Session):
        self.repository = StudyMaterialRepository(db)

    async def upload(
        self,
        file: UploadFile,
        title: str,
        user: User,
    ) -> StudyMaterial:
        if file.content_type not in self.ALLOWED_CONTENT_TYPES:
            raise ValueError("Only PDF files are currently supported")

        content = await file.read()

        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

        if len(content) > max_size:
            raise ValueError(
                f"File size cannot exceed {settings.MAX_UPLOAD_SIZE_MB} MB"
            )

        if not content:
            raise ValueError("Uploaded file is empty")

        if not content.startswith(b"%PDF-"):
            raise ValueError("Invalid PDF file")

        upload_directory = Path(settings.UPLOAD_DIR)
        upload_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        stored_filename = f"{uuid.uuid4()}.pdf"
        file_path = upload_directory / stored_filename

        try:
            file_path.write_bytes(content)

            material = self.repository.create(
                user_id=user.id,
                title=title.strip(),
                original_filename=file.filename or "document.pdf",
                stored_filename=stored_filename,
                file_type="pdf",
            )

            return material

        except Exception:
            if file_path.exists():
                file_path.unlink()

            raise

        finally:
            await file.close()