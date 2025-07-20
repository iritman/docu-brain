import requests
import json
import os
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

def test_llm_api():
    """تست API مدل زبانی (Ollama یا OpenRouter) با استفاده از متغیرهای محیطی"""
    
    # فقط استفاده از OpenRouter
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")
    model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.2-3b-instruct:free")
    print("🌐 استفاده از OpenRouter (مدل ابری)")
    if not api_key:
        print("❌ خطا: OPENROUTER_API_KEY در فایل .env تنظیم نشده است")
        return
    
    site_url = os.getenv("SITE_URL", "http://localhost:8501")  # اختیاری
    site_name = os.getenv("SITE_NAME", "RAG System")  # اختیاری
    
    print(f"🔗 URL: {base_url}")
    print(f"🤖 Model: {model}")
    if api_key:
        print(f"🔑 API Key: {api_key[:10]}...")
    print("\n📤 ارسال درخواست...")
    
    try:
        # فقط درخواست OpenRouter
        response = requests.post(
            url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": site_url,  # اختیاری - URL سایت برای رتبه‌بندی در openrouter.ai
                "X-Title": site_name,  # اختیاری - نام سایت برای رتبه‌بندی در openrouter.ai
            },
            data=json.dumps({
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": "What is the meaning of life?"
                    }
                ],
                "max_tokens": 150,
                "temperature": 0.7
            })
        )
        
        # بررسی وضعیت پاسخ
        if response.status_code == 200:
            result = response.json()
            print("✅ درخواست موفق بود!")
            # پردازش پاسخ OpenRouter
            print(f"📝 پاسخ: {result['choices'][0]['message']['content']}")
            # نمایش آمار استفاده (در صورت وجود)
            if 'usage' in result:
                usage = result['usage']
                print(f"\n📊 آمار استفاده:")
                print(f"   - توکن‌های ورودی: {usage.get('prompt_tokens', 'نامشخص')}")
                print(f"   - توکن‌های خروجی: {usage.get('completion_tokens', 'نامشخص')}")
                print(f"   - کل توکن‌ها: {usage.get('total_tokens', 'نامشخص')}")
        else:
            print(f"❌ خطا در درخواست: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"پیام خطا: {json.dumps(error_detail, ensure_ascii=False, indent=2)}")
            except:
                print(f"پیام خطا: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ خطا در ارتباط: {str(e)}")
    except json.JSONDecodeError as e:
        print(f"❌ خطا در تجزیه JSON: {str(e)}")
    except Exception as e:
        print(f"❌ خطای غیرمنتظره: {str(e)}")

if __name__ == "__main__":
    print("🧪 تست API مدل زبانی")
    print("=" * 30)
    test_llm_api()