from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=2,
        max_length=1000,
    )


class SourceChunk(BaseModel):
    chunk_index: int
    score: float


class QuestionResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceChunk]