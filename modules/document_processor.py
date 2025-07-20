import fitz  # PyMuPDF
from typing import List
import streamlit as st

class DocumentProcessor:
    """کلاس پردازش اسناد PDF"""
    
    def __init__(self):
        self.chunk_size = 500
        self.chunk_overlap = 50
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """استخراج متن از فایل PDF"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            st.error(f"خطا در خواندن فایل PDF: {str(e)}")
            return ""
    
    def chunk_text(self, text: str) -> List[str]:
        """تقسیم متن به چانک‌های کوچک"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk = " ".join(words[i:i + self.chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks