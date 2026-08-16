from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class StudyMaterialResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    original_filename: str
    file_type: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )