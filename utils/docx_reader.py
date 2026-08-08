from docx import Document

def read_docx(file):
    document = Document(file)

    text = ""

    for para in document.paragraphs:
        text += para.text + "\n"

    return text