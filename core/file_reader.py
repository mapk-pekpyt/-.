import os
from PyPDF2 import PdfReader
from docx import Document
import pandas as pd
from PIL import Image
import json

def read_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif ext == '.pdf':
        reader = PdfReader(file_path)
        return "\n".join([page.extract_text() for page in reader.pages])
    elif ext == '.docx':
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])
    elif ext in ['.json', '.md']:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif ext == '.csv':
        df = pd.read_csv(file_path)
        return df.to_string()
    elif ext == '.xlsx':
        df = pd.read_excel(file_path)
        return df.to_string()
    elif ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
        img = Image.open(file_path)
        return f"[Image: {img.size[0]}x{img.size[1]}, mode={img.mode}]"
    else:
        return f"[Unsupported file: {ext}]"