import os
import uuid
import streamlit as st
from typing import List, Tuple, Optional

class FileManager:
    """کلاس مدیریت فایل‌ها"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """اطمینان از وجود پوشه data"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def get_uploaded_files(self) -> List[str]:
        """دریافت لیست فایل‌های آپلودشده"""
        if not os.path.exists(self.data_dir):
            return []
        
        files = []
        for file in os.listdir(self.data_dir):
            if file.endswith('.pdf'):
                files.append(file)
        return files
    
    def save_uploaded_file(self, uploaded_file) -> Tuple[Optional[str], Optional[str]]:
        """ذخیره فایل آپلودشده"""
        try:
            # ایجاد نام یونیک برای فایل
            file_id = str(uuid.uuid4())[:8]
            file_extension = uploaded_file.name.split('.')[-1]
            unique_filename = f"{file_id}_{uploaded_file.name}"
            file_path = os.path.join(self.data_dir, unique_filename)
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            return unique_filename, file_path
        except Exception as e:
            st.error(f"خطا در ذخیره فایل: {str(e)}")
            return None, None
    
    def delete_file(self, filename: str) -> bool:
        """حذف فایل"""
        try:
            file_path = os.path.join(self.data_dir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            st.error(f"خطا در حذف فایل: {str(e)}")
            return False
    
    def get_total_size(self) -> float:
        """محاسبه حجم کل فایل‌ها به مگابایت"""
        uploaded_files = self.get_uploaded_files()
        total_size = sum(
            os.path.getsize(os.path.join(self.data_dir, f)) 
            for f in uploaded_files 
            if os.path.exists(os.path.join(self.data_dir, f))
        )
        return total_size / 1024 / 1024  # تبدیل به مگابایت