import pdfplumber
from docx import Document

def read_pdf(file_path: str) -> str:
    with pdfplumber.open(file_path) as pdf:
        return "".join([page.extract_text() for page in pdf.pages])

def read_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])
