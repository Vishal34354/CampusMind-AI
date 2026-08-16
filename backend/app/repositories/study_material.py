from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.study_material import StudyMaterial


class StudyMaterialRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: UUID,
        title: str,
        original_filename: str,
        stored_filename: str,
        file_type: str,
    ) -> StudyMaterial:
        material = StudyMaterial(
            user_id=user_id,
            title=title,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_type=file_type,
        )

        self.db.add(material)
        self.db.commit()
        self.db.refresh(material)

        return material

    def get_by_id_and_user(
        self,
        material_id: UUID,
        user_id: UUID,
    ) -> StudyMaterial | None:
        statement = select(StudyMaterial).where(
            StudyMaterial.id == material_id,
            StudyMaterial.user_id == user_id,
        )

        return self.db.scalar(statement)

    def get_all_by_user(
        self,
        user_id: UUID,
    ) -> list[StudyMaterial]:
        statement = (
            select(StudyMaterial)
            .where(StudyMaterial.user_id == user_id)
            .order_by(StudyMaterial.created_at.desc())
        )

        return list(self.db.scalars(statement).all())