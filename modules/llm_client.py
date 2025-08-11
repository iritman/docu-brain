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
        # تشخیص نوع درخواست
        is_mcq_request = self._is_multiple_choice_request(question)
        
        if is_mcq_request:
            prompt = self._create_mcq_prompt(context, question)
        else:
            prompt = self._create_standard_prompt(context, question)
        
        try:
            return self._generate_openrouter_response(prompt)
        
        except requests.exceptions.RequestException as e:
            return f"خطا در ارتباط با مدل زبانی: {str(e)}"
        except Exception as e:
            return f"خطا در پردازش پاسخ: {str(e)}"
    
    def _is_multiple_choice_request(self, question: str) -> bool:
        """تشخیص اینکه آیا درخواست برای تولید سوال چهار گزینه‌ای است یا خیر"""
        mcq_keywords = [
            'سوال چهار گزینه', 'سوال چهارگزینه', 'چهار گزینه', 'چهارگزینه',
            'سوال تستی', 'تست', 'گزینه', 'multiple choice', 'mcq',
            'سوال انتخابی', 'سوال کنکوری', 'آزمون', 'امتحان'
        ]
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in mcq_keywords)
    
    def _create_mcq_prompt(self, context: str, question: str) -> str:
        """ایجاد پرامپت برای تولید سوال چهار گزینه‌ای"""
        return f"""شما یک متخصص طراحی سوال هستید. بر اساس اطلاعات ارائه شده، سوال‌های چهار گزینه‌ای با کیفیت بالا تولید کنید.

اطلاعات مرجع:
{context}

درخواست کاربر:
{question}

دستورالعمل‌ها:
1. بر اساس محتوای ارائه شده، سوال‌های چهار گزینه‌ای طراحی کنید
2. هر سوال باید دارای یک گزینه صحیح و سه گزینه غلط منطقی باشد
3. گزینه‌های غلط باید قابل اعتماد و فریبنده باشند
4. سوال‌ها باید از نظر علمی دقیق و بر اساس متن مرجع باشند
5. از زبان فارسی روان و صحیح استفاده کنید
6. پاسخ صحیح را در انتها مشخص کنید

فرمت خروجی:
سوال ۱: [متن سوال]
الف) [گزینه اول]
ب) [گزینه دوم]
ج) [گزینه سوم]
د) [گزینه چهارم]

پاسخ صحیح: [حرف گزینه صحیح]

توضیح: [توضیح کوتاه در مورد پاسخ صحیح]

---

اگر اطلاعات کافی برای تولید سوال نیست، این موضوع را اعلام کنید."""
    
    def _create_standard_prompt(self, context: str, question: str) -> str:
        """ایجاد پرامپت استاندارد برای پاسخ‌های معمولی"""
        return f"""شما یک دستیار هوشمند و دقیق هستید که بر اساس اطلاعات ارائه شده پاسخ می‌دهید.
 
 اطلاعات مرجع:
 {context}
 
 سؤال کاربر:
 {question}
 
 دستورالعمل‌ها:
 1. فقط بر اساس اطلاعات ارائه شده پاسخ دهید
 2. اگر اطلاعات کافی نیست، این موضوع را صراحت اعلام کنید
 3. پاسخ‌های دقیق، جامع و مفید ارائه دهید
 4. از زبان فارسی روان و صحیح استفاده کنید
 5. در صورت امکان، منابع مربوطه را ذکر کنید
 
 پاسخ:"""
    
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