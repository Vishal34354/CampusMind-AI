from google import genai

from app.core.config import settings


class AnswerGenerator:
    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
        )

        self.model = settings.GEMINI_MODEL

    def generate_answer(
        self,
        question: str,
        search_results: list[dict],
    ) -> str:
        if not search_results:
            return "I could not find relevant information in the study material."

        context_parts = []

        for result in search_results:
            context_parts.append(
                f"""
[Chunk {result['chunk_index']}]
{result['content']}
"""
            )

        context = "\n".join(context_parts)

        prompt = f"""
You are CampusMind AI, an AI-powered study assistant.

Answer the student's question using ONLY the study material
provided in the context below.

Rules:
1. Do not use outside knowledge.
2. If the context does not contain enough information, clearly say so.
3. Give a clear and educational answer.
4. Explain concepts in student-friendly language.
5. Do not mention that you are an AI model.
6. Do not invent facts that are not present in the context.

STUDY MATERIAL:

{context}

STUDENT QUESTION:

{question}

ANSWER:
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        if not response.text:
            return "I could not generate an answer from the study material."

        return response.text.strip()