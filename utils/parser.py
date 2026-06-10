import os
import pdfplumber
import docx2txt

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        with pdfplumber.open(file_path) as pdf:
            return ' '.join(page.extract_text() or '' for page in pdf.pages)
    elif ext == '.docx':
        return docx2txt.process(file_path)
    elif ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return ""
