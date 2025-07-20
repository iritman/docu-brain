import requests
import os
from typing import Dict, Any

class LLMClient:
    """کلاس ارتباط با مدل زبانی"""
    
    def __init__(self):        
        # تنظیمات OpenRouter
        print('>>', os.getenv("OPENROUTER_BASE_URL"))
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = os.getenv("OPENROUTER_MODEL", "google/gemma-3n-e2b-it:free")
    
    def generate_response(self, context: str, question: str) -> str:
        """تولید پاسخ با استفاده از مدل زبانی"""
        prompt = f"""اطلاعات بازیابی‌شده:
{context}

سؤال:
{question}

لطفاً فقط بر اساس اطلاعات بازیابی‌شده پاسخ دهید. اگر اطلاعات کافی نیست، این موضوع را اعلام کنید."""
        
        try:
            return self._generate_openrouter_response(prompt)
        
        except requests.exceptions.RequestException as e:
            return f"خطا در ارتباط با مدل زبانی: {str(e)}"
        except Exception as e:
            return f"خطا در پردازش پاسخ: {str(e)}"
    
    def _generate_openrouter_response(self, prompt: str) -> str:
        """تولید پاسخ با استفاده از OpenRouter"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']