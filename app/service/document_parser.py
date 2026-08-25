from PyPDF2 import PdfReader


def _stats(text: str, page_count: int) -> dict:
    stripped = text.strip()
    return {
        "text": stripped,
        "text_count": len(stripped),
        "word_count": len(stripped.split()),
        "page_count": page_count,
    }


def extract_text_from_pdf(file_path: str) -> dict:
    with open(file_path, "rb") as f:
        pdf_reader = PdfReader(f)
        pages = [(page.extract_text() or "") for page in pdf_reader.pages]
        return _stats("\n".join(pages), page_count=len(pdf_reader.pages) or 1)


def extract_text_from_txt(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    return _stats(text, page_count=1)


def extract_text(file_path: str) -> dict:
    ext = file_path.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        return extract_text_from_pdf(file_path)
    if ext == "txt":
        return extract_text_from_txt(file_path)
    raise ValueError(f"Unsupported file type: {ext}")
