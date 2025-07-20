import os
import pickle
import numpy as np
from typing import List, Dict
from datetime import datetime
import streamlit as st
from sentence_transformers import SentenceTransformer
import faiss

class VectorDatabase:
    """کلاس مدیریت پایگاه داده برداری"""
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.documents = []
        self.metadata = []
        self.db_path = "data/vector_db.pkl"
        self.load_database()
    
    def add_documents(self, texts: List[str], file_name: str):
        """افزودن اسناد به پایگاه داده برداری"""
        embeddings = self.model.encode(texts)
        
        if self.index is None:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner Product for similarity
        
        # نرمال‌سازی بردارها برای استفاده از cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))
        
        # ذخیره متادیتا
        for i, text in enumerate(texts):
            self.documents.append(text)
            self.metadata.append({
                'file_name': file_name,
                'chunk_id': len(self.documents),
                'timestamp': datetime.now().isoformat()
            })
        
        self.save_database()
    
    def search(self, query: str, k: int = 5, selected_files: List[str] = None) -> List[Dict]:
        """جستجو در پایگاه داده برداری"""
        if self.index is None or len(self.documents) == 0:
            return []
        
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        scores, indices = self.index.search(query_embedding.astype('float32'), min(k, len(self.documents)))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.documents):
                metadata = self.metadata[idx]
                # فیلتر کردن بر اساس فایل‌های انتخاب‌شده
                if selected_files is None or (selected_files is not None and metadata['file_name'] in selected_files):
                    results.append({
                        'text': self.documents[idx],
                        'score': float(score),
                        'metadata': metadata
                    })
        
        return results
    
    def remove_documents_by_file(self, file_name: str):
        """حذف اسناد مربوط به یک فایل خاص"""
        # پیدا کردن ایندکس‌های مربوط به فایل
        indices_to_remove = []
        for i, meta in enumerate(self.metadata):
            if meta['file_name'] == file_name:
                indices_to_remove.append(i)
        
        # حذف از لیست‌ها (از آخر به اول)
        for idx in sorted(indices_to_remove, reverse=True):
            del self.documents[idx]
            del self.metadata[idx]
        
        # بازسازی ایندکس
        if self.documents:
            embeddings = self.model.encode(self.documents)
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings.astype('float32'))
        else:
            self.index = None
        
        self.save_database()
    
    def save_database(self):
        """ذخیره پایگاه داده"""
        try:
            db_data = {
                'documents': self.documents,
                'metadata': self.metadata,
                'index': faiss.serialize_index(self.index) if self.index else None
            }
            with open(self.db_path, 'wb') as f:
                pickle.dump(db_data, f)
        except Exception as e:
            st.error(f"خطا در ذخیره پایگاه داده: {str(e)}")
    
    def load_database(self):
        """بارگذاری پایگاه داده"""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'rb') as f:
                    db_data = pickle.load(f)
                
                self.documents = db_data.get('documents', [])
                self.metadata = db_data.get('metadata', [])
                
                index_data = db_data.get('index')
                if index_data is not None:
                    self.index = faiss.deserialize_index(index_data)
                else:
                    self.index = None
        except Exception as e:
            st.error(f"خطا در بارگذاری پایگاه داده: {str(e)}")
            self.documents = []
            self.metadata = []
            self.index = None