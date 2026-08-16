from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.study_material import StudyMaterialRepository
from app.schemas.question import QuestionRequest, QuestionResponse
from app.schemas.study_material import StudyMaterialResponse
from app.services.answer_generator import AnswerGenerator
from app.services.semantic_search import SemanticSearchService
from app.services.study_material import StudyMaterialService


router = APIRouter(
    prefix="/materials",
)


# ==========================================
# Get All Study Materials
# ==========================================

@router.get(
    "",
    response_model=list[StudyMaterialResponse],
)
def get_materials(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repository = StudyMaterialRepository(db)

    return repository.get_all_by_user(
        user_id=current_user.id,
    )


# ==========================================
# Upload Study Material
# ==========================================

@router.post(
    "/upload",
    response_model=StudyMaterialResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_material(
    title: Annotated[
        str,
        Form(
            min_length=1,
            max_length=255,
        ),
    ],
    file: Annotated[
        UploadFile,
        File(),
    ],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StudyMaterialService(db)

    try:
        return await service.upload(
            file=file,
            title=title,
            user=current_user,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================
# Ask Question About Study Material
# ==========================================

@router.post(
    "/{material_id}/ask",
    response_model=QuestionResponse,
)
def ask_material(
    material_id: UUID,
    data: QuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repository = StudyMaterialRepository(db)

    # ======================================
    # Verify Material Ownership
    # ======================================

    material = repository.get_by_id_and_user(
        material_id=material_id,
        user_id=current_user.id,
    )

    if material is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study material not found",
        )

    # ======================================
    # Semantic Search
    # ======================================

    search_service = SemanticSearchService(db)

    results = search_service.search(
        material_id=material.id,
        query=data.question,
        top_k=5,
    )

    if not results:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Material has not been indexed yet",
        )

    # ======================================
    # Generate AI Answer
    # ======================================

    answer_generator = AnswerGenerator()

    answer = answer_generator.generate_answer(
        question=data.question,
        search_results=results,
    )

    # ======================================
    # Prepare Sources
    # ======================================

    sources = [
        {
            "chunk_index": result["chunk_index"],
            "score": result["score"],
        }
        for result in results
    ]

    # ======================================
    # Response
    # ======================================

    return QuestionResponse(
        question=data.question,
        answer=answer,
        sources=sources,
    )