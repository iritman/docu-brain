import streamlit as st
import os
from dotenv import load_dotenv
from modules import DocumentProcessor, VectorDatabase, LLMClient, FileManager, ChatHistory

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

# تنظیمات صفحه
st.set_page_config(
    page_title="DocuBrain - هوش اسناد و بازیابی",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS برای راست‌چین کردن متن فارسی و استایل‌های اضافی
st.markdown("""
<style>
body, .rtl, .main-header, .upload-section, .query-section, .keyboard-hint, .stTextInput, .stButton, .stTextArea, .stMarkdown, .stMetric, .stAlert, .stInfo, .stWarning, .stSuccess, .stError {
    font-family: 'Tahoma', Tahoma, Arial, sans-serif !important;
}
.rtl {
    direction: rtl;
    text-align: right;
}
.stTextInput > div > div > input {
    direction: rtl;
    text-align: right;
}
.stTextArea > div > div > textarea {
    direction: rtl;
    text-align: right;
}
.stSelectbox > div > div > div {
    direction: rtl;
    text-align: right;
}
.main-header {
    text-align: center;
    color: #1f77b4;
    margin-bottom: 30px;
}
.upload-section {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}
.query-section {
    background-color: #e8f4fd;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}
.response-section {
    background-color: #f9f9f9;
    padding: 20px;
    border-radius: 10px;
    border-left: 5px solid #1f77b4;
}
.chat-message {
    padding: 15px;
    margin: 10px 0;
    border-radius: 10px;
    border-left: 4px solid #1f77b4;
}
.user-message {
    background-color: #e3f2fd;
    border-left-color: #2196f3;
}
.assistant-message {
    background-color: #f3e5f5;
    border-left-color: #9c27b0;
}
.message-timestamp {
    font-size: 0.8em;
    color: #666;
    margin-bottom: 5px;
}
.message-content {
    margin: 5px 0;
}
.sources-section {
    background-color: #fff3e0;
    padding: 10px;
    border-radius: 5px;
    margin-top: 10px;
    font-size: 0.9em;
}
.keyboard-hint {
    font-size: 0.8em;
    color: #666;
    margin-top: 5px;
    text-align: left;
}
</style>
""", unsafe_allow_html=True)

# JavaScript برای کلیدهای میانبر
st.markdown("""
<script>
document.addEventListener('keydown', function(e) {
    // اگر Shift + Enter زده شد، خط جدید اضافه کن
    if (e.shiftKey && e.key === 'Enter') {
        e.preventDefault();
        // این کار توسط textarea خودش انجام می‌شود
        return;
    }
    // اگر فقط Enter زده شد، فرم را ارسال کن
    if (e.key === 'Enter' && !e.shiftKey) {
        const textarea = document.querySelector('textarea[aria-label="سؤال خود را وارد کنید:"]');
        if (textarea && document.activeElement === textarea) {
            e.preventDefault();
            // شبیه‌سازی کلیک روی دکمه ارسال
            const submitButton = document.querySelector('button[kind="primary"]');
            if (submitButton) {
                submitButton.click();
            }
        }
    }
});
</script>
""", unsafe_allow_html=True)

def initialize_session_state():
    """مقداردهی اولیه session state"""
    if 'doc_processor' not in st.session_state:
        st.session_state.doc_processor = DocumentProcessor()
    
    if 'vector_db' not in st.session_state:
        st.session_state.vector_db = VectorDatabase()
    
    if 'llm_client' not in st.session_state:
        st.session_state.llm_client = LLMClient()
    
    if 'file_manager' not in st.session_state:
        st.session_state.file_manager = FileManager()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = ChatHistory()
    
    if 'current_question' not in st.session_state:
        st.session_state.current_question = ""

def render_chat_history():
    """نمایش تاریخچه چت"""
    st.markdown('<h3 class="rtl">💬 تاریخچه گفتگو</h3>', unsafe_allow_html=True)
    
    messages = st.session_state.chat_history.get_messages()
    
    if not messages:
        st.info("هنوز هیچ گفتگویی انجام نشده است.")
        return
    
    # دکمه پاک کردن تاریخچه
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🗑️ پاک کردن تاریخچه", type="secondary"):
            st.session_state.chat_history.clear_history()
            st.rerun()
    
    # نمایش پیام‌ها
    for message in reversed(messages[-10:]):  # نمایش 10 پیام آخر
        timestamp = st.session_state.chat_history.format_timestamp(message['timestamp'])
        
        # پیام کاربر
        st.markdown(f"""
        <div class="chat-message user-message rtl">
            <div class="message-timestamp">👤 کاربر - {timestamp}</div>
            <div class="message-content"><strong>سؤال:</strong> {message['question']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # پاسخ دستیار
        sources_info = ""
        if message.get('sources'):
            source_files = list(set([s['metadata']['file_name'] for s in message['sources']]))
            sources_info = f"<div class='sources-section'>📚 منابع: {', '.join(source_files)}</div>"
        
        st.markdown(f"""
        <div class="chat-message assistant-message rtl">
            <div class="message-timestamp">🤖 دستیار - {timestamp}</div>
            <div class="message-content"><strong>پاسخ:</strong> {message['answer']}</div>
            {sources_info}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")

def render_file_management():
    """نمایش بخش مدیریت فایل‌ها"""
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.markdown('<h3 class="rtl">📁 آپلود فایل‌های PDF</h3>', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "فایل‌های PDF خود را انتخاب کنید",
        type=['pdf'],
        accept_multiple_files=True,
        help="می‌توانید چندین فایل PDF همزمان آپلود کنید"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if st.button(f"پردازش {uploaded_file.name}", key=f"process_{uploaded_file.name}"):
                with st.spinner(f"در حال پردازش {uploaded_file.name}..."):
                    # ذخیره فایل
                    unique_filename, file_path = st.session_state.file_manager.save_uploaded_file(uploaded_file)
                    
                    if file_path:
                        # استخراج متن
                        text = st.session_state.doc_processor.extract_text_from_pdf(file_path)
                        
                        if text:
                            # تقسیم به چانک
                            chunks = st.session_state.doc_processor.chunk_text(text)
                            
                            # افزودن به پایگاه داده برداری
                            st.session_state.vector_db.add_documents(chunks, unique_filename)
                            
                            st.success(f"✅ فایل {uploaded_file.name} با موفقیت پردازش شد! ({len(chunks)} چانک ایجاد شد)")
                        else:
                            st.error(f"❌ خطا در استخراج متن از {uploaded_file.name}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # بخش مدیریت فایل‌ها
    st.markdown('<h3 class="rtl">📋 مدیریت فایل‌های آپلودشده</h3>', unsafe_allow_html=True)
    
    uploaded_files_list = st.session_state.file_manager.get_uploaded_files()
    
    if uploaded_files_list:
        st.markdown('<p class="rtl">فایل‌های موجود:</p>', unsafe_allow_html=True)
        selected_files = st.multiselect(
            "فایل‌هایی که می‌خواهید در آن‌ها جستجو کنید را انتخاب کنید:",
            uploaded_files_list,
            default=uploaded_files_list,
            help="می‌توانید فایل‌های خاصی را برای جستجو انتخاب کنید"
        )
        st.markdown('<p class="rtl">حذف فایل:</p>', unsafe_allow_html=True)
        file_to_delete = st.selectbox("فایل برای حذف:", ["انتخاب کنید..."] + uploaded_files_list)
        if file_to_delete != "انتخاب کنید...":
            if st.button("🗑️ حذف فایل", type="secondary"):
                if st.session_state.file_manager.delete_file(file_to_delete):
                    st.session_state.vector_db.remove_documents_by_file(file_to_delete)
                    st.success(f"✅ فایل {file_to_delete} حذف شد")
                    st.rerun()
                else:
                    st.error("❌ خطا در حذف فایل")
        return selected_files
    else:
        st.info("هیچ فایلی آپلود نشده است.")
        return []

def render_query_section(selected_files):
    """نمایش بخش پرسش و پاسخ"""
    if not selected_files:
        st.warning("لطفاً ابتدا فایل‌هایی را آپلود و انتخاب کنید.")
        return
    
    st.markdown('<div class="query-section">', unsafe_allow_html=True)
    st.markdown('<h3 class="rtl">❓ پرسش از اسناد</h3>', unsafe_allow_html=True)
    
    # راهنمای کلیدهای میانبر
    st.markdown('<p class="keyboard-hint">💡 راهنما: Enter برای ارسال، Shift+Enter برای خط جدید</p>', unsafe_allow_html=True)
    
    user_question = st.text_area(
        "سؤال خود را وارد کنید:",
        height=100,
        placeholder="سؤال خود را در اینجا بنویسید...\nShift+Enter: خط جدید\nEnter: ارسال سؤال",
        help="سؤال خود را بر اساس محتوای فایل‌های آپلودشده بپرسید",
        value=st.session_state.current_question,
        key="question_input"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        submit_button = st.button("🔍 جستجو و پاسخ", type="primary")
    
    # پردازش سؤال
    if submit_button and user_question.strip():
        with st.spinner("در حال جستجو و تولید پاسخ..."):
            # جستجو در پایگاه داده برداری
            search_results = st.session_state.vector_db.search(
                user_question, 
                k=5, 
                selected_files=selected_files
            )
            
            if search_results:
                # ترکیب نتایج جستجو
                context = "\n\n".join([result['text'] for result in search_results])
                
                # تولید پاسخ
                response = st.session_state.llm_client.generate_response(context, user_question)
                
                # افزودن به تاریخچه
                st.session_state.chat_history.add_message(
                    question=user_question,
                    answer=response,
                    sources=search_results
                )
                
                # پاک کردن سؤال فعلی
                st.session_state.current_question = ""
                
                # نمایش پاسخ
                st.markdown('<div class="response-section">', unsafe_allow_html=True)
                st.markdown('<h4 class="rtl">📝 پاسخ جدید:</h4>', unsafe_allow_html=True)
                st.markdown(f'<div class="rtl">{response}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # نمایش منابع
                with st.expander("📚 منابع استفاده‌شده"):
                    for i, result in enumerate(search_results, 1):
                        st.markdown(f"**منبع {i}** (امتیاز: {result['score']:.3f})")
                        st.markdown(f"فایل: {result['metadata']['file_name']}")
                        st.markdown(f"متن: {result['text'][:200]}...")
                        st.markdown("---")
                
                # بروزرسانی صفحه برای نمایش تاریخچه جدید
                st.rerun()
            else:
                st.warning("هیچ نتیجه‌ای برای سؤال شما یافت نشد.")
    
    elif submit_button:
        st.warning("لطفاً سؤال خود را وارد کنید.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_statistics():
    """نمایش آمار سیستم"""
    uploaded_files_list = st.session_state.file_manager.get_uploaded_files()
    
    if uploaded_files_list:
        st.markdown('<h3 class="rtl">📊 آمار سیستم</h3>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("تعداد فایل‌ها", len(uploaded_files_list))
        
        with col2:
            st.metric("تعداد چانک‌ها", len(st.session_state.vector_db.documents))
        
        with col3:
            total_size = st.session_state.file_manager.get_total_size()
            st.metric("حجم کل", f"{total_size:.1f} MB")
        
        with col4:
            chat_count = len(st.session_state.chat_history.get_messages())
            st.metric("تعداد گفتگوها", chat_count)

def main():
    """تابع اصلی اپلیکیشن"""
    # عنوان اصلی
    st.markdown('<h1 class="main-header rtl">🧠 DocuBrain - هوش اسناد و بازیابی</h1>', unsafe_allow_html=True)
    
    # مقداردهی اولیه
    initialize_session_state()
    
    # بخش مدیریت فایل‌ها
    selected_files = render_file_management()
    if not selected_files:
        selected_files = []
    
    # بخش پرسش و پاسخ
    uploaded_files_list = st.session_state.file_manager.get_uploaded_files()
    if uploaded_files_list:
        render_query_section(selected_files)
    
    # بخش تاریخچه چت
    render_chat_history()
    
    # بخش آمار
    render_statistics()
    
    # --- Copyright/Footer ---
    st.markdown('<hr style="margin-top:32px; margin-bottom:8px;">', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center; color:#888; font-size:14px;">This project was designed by <b>Naiem Yousefifard</b> | iritman@gmail.com<br>All rights reserved.</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()