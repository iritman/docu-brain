import json
import os
from datetime import datetime
from typing import List, Dict, Any
import streamlit as st

class ChatHistory:
    """کلاس مدیریت تاریخچه چت"""
    
    def __init__(self, history_file: str = "data/chat_history.json"):
        self.history_file = history_file
        self.messages = self.load_history()
    
    def add_message(self, question: str, answer: str, sources: List[Dict] = None):
        """افزودن پیام جدید به تاریخچه"""
        message = {
            "id": len(self.messages) + 1,
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "sources": sources or []
        }
        self.messages.append(message)
        self.save_history()
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """دریافت تمام پیام‌ها"""
        return self.messages
    
    def clear_history(self):
        """پاک کردن تاریخچه"""
        self.messages = []
        self.save_history()
    
    def save_history(self):
        """ذخیره تاریخچه در فایل"""
        try:
            # اطمینان از وجود پوشه data
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"خطا در ذخیره تاریخچه: {str(e)}")
    
    def load_history(self) -> List[Dict[str, Any]]:
        """بارگذاری تاریخچه از فایل"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            st.error(f"خطا در بارگذاری تاریخچه: {str(e)}")
            return []
    
    def get_last_messages(self, count: int = 10) -> List[Dict[str, Any]]:
        """دریافت آخرین پیام‌ها"""
        return self.messages[-count:] if len(self.messages) > count else self.messages
    
    def format_timestamp(self, timestamp: str) -> str:
        """فرمت کردن زمان برای نمایش"""
        try:
            dt = datetime.fromisoformat(timestamp)
            return dt.strftime("%Y/%m/%d - %H:%M")
        except:
            return timestamp