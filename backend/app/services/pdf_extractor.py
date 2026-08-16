from pathlib import Path

import fitz


class PDFExtractor:
    @staticmethod
    def extract_text(file_path: str | Path) -> str:
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"PDF not found: {file_path}")

        text_parts = []

        with fitz.open(file_path) as document:
            for page in document:
                text = page.get_text("text")

                if text:
                    text_parts.append(text)

        return "\n".join(text_parts).strip()