import streamlit as st
import traceback
from nlp_module import detect_language, summarize_text
from cv_module import extract_text_from_image
from pdf_module import extract_text_from_pdf
from utils import calculate_compression_ratio, generate_pdf, clean_text

# Configure page settings
st.set_page_config(page_title="AI Multilingual Text Summarizer", page_icon="🌍", layout="wide")

# Custom UI Styling for a modern, beautiful interface
st.markdown("""
<style>
    .main-title { color: #1E3A8A; font-family: 'Helvetica Neue', sans-serif; text-align: center; padding-bottom: 20px; font-weight: 800;}
    .metric-card { background-color: #F8FAFC; border-left: 5px solid #3B82F6; padding: 15px; border-radius: 8px; margin-bottom: 15px; font-size: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);}
    .stButton>button { background-color: #2563EB; color: white; border-radius: 8px; transition: 0.3s; height: 50px; font-weight: bold; border: none; box-shadow: 0 4px 6px rgba(37,99,235,0.2);}
    .stButton>button:hover { background-color: #1D4ED8; color: white; border: none; transform: translateY(-2px);}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">🌍 AI Multilingual Text Summarizer</h1>', unsafe_allow_html=True)
st.markdown("---")

# --- SIDEBAR CONFIGURATION ---
st.sidebar.title("⚙️ Configuration")

# Sidebar Project Description
st.sidebar.markdown("### 📖 About")
st.sidebar.info(
    "This **Advanced AI Text Summarizer** leverages Hugging Face Transformers (mT5 & BART) "
    "and Computer Vision (Tesseract OCR) to extract, analyze, and conditionally summarize content "
    "from dense texts, PDFs, and images into multiple languages."
)

st.sidebar.markdown("---")
# Beautiful language mapping for requested languages
LANGUAGE_MAPPING = {
    "en": "English",
    "te": "Telugu",
    "hi": "Hindi",
    "fr": "French",
    "es": "Spanish",
    "de": "German",
    "zh-cn": "Chinese",
    "ja": "Japanese"
}

output_lang = st.sidebar.selectbox(
    "🗣️ Output Language", 
    options=list(LANGUAGE_MAPPING.keys()), 
    format_func=lambda x: LANGUAGE_MAPPING[x],
    index=0
)
summary_length = st.sidebar.select_slider("📏 Summary Length", options=["short", "medium", "long"], value="medium")

# --- MAIN INPUT AREA ---
st.subheader("📥 Input Your Content")
input_method = st.radio("Choose input method:", ("✍️ Text Box", "📄 File Upload (PDF/Image)"), horizontal=True)

input_text = ""

if "Text" in input_method:
    input_text = st.text_area("Paste your text here to summarize:", height=200)
else:
    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        file_type = uploaded_file.name.split('.')[-1].lower()
        
        try:
            # Loading spinner during extraction processing
            with st.spinner(f"Extracting text from {file_type.upper()}..."):
                if file_type == 'pdf':
                    raw_text = extract_text_from_pdf(uploaded_file)
                else:
                    raw_text = extract_text_from_image(uploaded_file)
                    
                input_text = clean_text(raw_text)
                
                # Handling empty/invalid file extraction
                if input_text:
                    st.success("Text extracted successfully!")
                    
                    # Option to preview extracted text
                    with st.expander("👁️ Preview Extracted Text"):
                        st.write(input_text)
                else:
                    st.error("❌ The uploaded file appears to be empty or unreadable. Please check the file and try again.")
        except Exception as e:
            # Exception handling for corrupted/invalid files
            st.error(f"❌ Failed to extract text from file. The file may be corrupted or invalid. Error: {str(e)}")

st.markdown("---")

# --- ACTION & RESULTS ---
col1, col2, col3 = st.columns([1, 2, 1])
if col2.button("🚀 Summarize Now", use_container_width=True):
    
    # Graceful handling of empty input
    if not input_text or not input_text.strip():
        st.warning("⚠️ Please provide some input text or upload a valid file first.")
    else:
        detected_lang = detect_language(input_text)
        st.info(f"🔍 **Detected Input Language:** `{LANGUAGE_MAPPING.get(detected_lang, detected_lang.upper())}`")
        
        # Loading spinner during summarization processing
        with st.spinner("🤖 Analyzing and summarizing your text... (This may take a moment)"):
            try:
                summary = summarize_text(input_text, target_lang=output_lang, length=summary_length)
                metrics = calculate_compression_ratio(input_text, summary)
                
                st.markdown("---")
                st.subheader("✨ Final Summary")
                
                res_col1, res_col2 = st.columns([2.5, 1])
                
                with res_col1:
                    st.success(summary)
                    
                with res_col2:
                    st.markdown("### 📊 Metrics")
                    st.markdown(f"""
                    <div class="metric-card"><b>Original Words:</b><br>{metrics["original_words"]}</div>
                    <div class="metric-card"><b>Summary Words:</b><br>{metrics["summary_words"]}</div>
                    <div class="metric-card"><b>Compression Ratio:</b><br>{metrics["compression_ratio"]}</div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                pdf_bytes = generate_pdf(summary)
                st.download_button(
                    label="⬇️ Download Summary as PDF",
                    data=pdf_bytes,
                    file_name="AI_Summary.pdf",
                    mime="application/pdf"
                )
                    
            except Exception as e:
                st.error("❌ A model error occurred during summarization. If the text is extremely long, verify model size or network connection.")
                st.error(traceback.format_exc())
