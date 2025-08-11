#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تست سیستم تولید سوال چهار گزینه‌ای
این فایل برای آزمایش عملکرد سیستم در تولید سوالات چهار گزینه‌ای استفاده می‌شود
"""

import os
from dotenv import load_dotenv
from modules.llm_client import LLMClient

# بارگذاری متغیرهای محیطی
load_dotenv()

def test_mcq_generation():
    """تست تولید سوال چهار گزینه‌ای"""
    
    # ایجاد کلاینت LLM
    llm_client = LLMClient()
    
    # متن نمونه برای تست
    sample_context = """
    هوش مصنوعی (Artificial Intelligence) شاخه‌ای از علوم کامپیوتر است که به ایجاد سیستم‌هایی می‌پردازد که قادر به انجام کارهایی هستند که معمولاً نیاز به هوش انسانی دارند. این کارها شامل یادگیری، استدلال، درک زبان طبیعی، بینایی کامپیوتری و تصمیم‌گیری می‌شود.
    
    انواع اصلی هوش مصنوعی عبارتند از:
    1. هوش مصنوعی ضعیف (Narrow AI): که برای انجام یک کار خاص طراحی شده است
    2. هوش مصنوعی قوی (General AI): که قادر به انجام هر کاری است که انسان می‌تواند انجام دهد
    3. هوش مصنوعی فوق‌العاده (Super AI): که از توانایی‌های انسان فراتر می‌رود
    
    یادگیری ماشین (Machine Learning) زیرمجموعه‌ای از هوش مصنوعی است که به سیستم‌ها اجازه می‌دهد بدون برنامه‌نویسی صریح، از داده‌ها یاد بگیرند و عملکرد خود را بهبود دهند.
    """
    
    # تست‌های مختلف
    test_questions = [
        "از انواع هوش مصنوعی، سوال چهار گزینه‌ای بساز",
        "سوال تستی در مورد تعریف هوش مصنوعی طراحی کن",
        "چهار گزینه‌ای از مفهوم یادگیری ماشین",
        "سوال کنکوری از این متن بساز",
        "تست چهارگزینه‌ای از انواع AI"
    ]
    
    print("=" * 80)
    print("تست سیستم تولید سوال چهار گزینه‌ای")
    print("=" * 80)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🔍 تست {i}: {question}")
        print("-" * 60)
        
        try:
            # تولید پاسخ
            response = llm_client.generate_response(sample_context, question)
            print(f"✅ پاسخ تولید شد:")
            print(response)
            
        except Exception as e:
            print(f"❌ خطا در تولید پاسخ: {str(e)}")
        
        print("\n" + "=" * 80)

def test_normal_question():
    """تست سوال معمولی برای مقایسه"""
    
    llm_client = LLMClient()
    
    sample_context = """
    هوش مصنوعی شاخه‌ای از علوم کامپیوتر است که به ایجاد سیستم‌هایی می‌پردازد که قادر به انجام کارهایی هستند که معمولاً نیاز به هوش انسانی دارند.
    """
    
    normal_question = "هوش مصنوعی چیست؟"
    
    print("\n🔍 تست سوال معمولی:")
    print("-" * 40)
    print(f"سوال: {normal_question}")
    
    try:
        response = llm_client.generate_response(sample_context, normal_question)
        print(f"✅ پاسخ: {response}")
    except Exception as e:
        print(f"❌ خطا: {str(e)}")

if __name__ == "__main__":
    print("شروع تست سیستم...")
    
    # بررسی وجود کلید API
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ خطا: کلید API در فایل .env تنظیم نشده است")
        exit(1)
    
    # تست سوالات چهار گزینه‌ای
    test_mcq_generation()
    
    # تست سوال معمولی
    test_normal_question()
    
    print("\n✅ تست‌ها تکمیل شد!")