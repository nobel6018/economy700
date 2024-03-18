import os


def mupdf():
    import fitz
    path = "economy_dictionary_700.pdf"
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def plumber():
    import pdfplumber
    pdf = pdfplumber.open("economy_dictionary_700.pdf")
    pages = pdf.pages
    text = ""
    for page in pages:
        sub = page.extract_text()
        text += sub
    return text


def miner():
    from pdfminer.high_level import extract_text
    text = extract_text("economy_dictionary_700.pdf")
    return text


def reader():
    from PyPDF2 import PdfReader
    reader = PdfReader("economy_dictionary_700.pdf")
    pages = reader.pages
    text = ""
    for page in pages:
        sub = page.extract_text()
        text += sub
    return text


def save_to_text(text, file_ext_name):
    file_path = os.path.join("result", file_ext_name)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(text)
    print(f"'{file_path}'에 텍스트 저장 완료.")


if __name__ == '__main__':
    # plumber()
    # miner()
    # reader()
    result_text = mupdf()

    save_to_text(result_text, "mupdf.txt")
