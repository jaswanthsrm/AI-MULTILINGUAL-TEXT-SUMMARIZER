import fitz  # PyMuPDF
import re

def extract_text_from_pdf(file) -> str:
    """
    Extracts text from a multi-page PDF document using PyMuPDF.
    Reads all pages, combines text, and cleans up unwanted characters.
    """
    text = ""
    try:
        # Check if it's a file-like object (e.g., from Streamlit uploader)
        if hasattr(file, "read"):
            pdf_bytes = file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        else:
            # Handle if passing raw bytes or file path
            if isinstance(file, bytes):
                doc = fitz.open(stream=file, filetype="pdf")
            else:
                doc = fitz.open(file)
            
        # Read multi-page PDFs and combine all text
        for page in doc:
            text += page.get_text("text") + "\n"
            
        doc.close()
        
        # Clean unwanted characters
        if text:
            # Remove obscure control characters (keeping \n and \t)
            text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
            
            # Remove zero-width formatting characters that often pollute PDFs
            text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)
            
            # Normalize whitespace: replace multiple spaces/tabs with a single space
            text = re.sub(r'[ \t]+', ' ', text)
            
            # Normalize newlines: replace 3+ consecutive newlines with just 2 (standard paragraph break)
            text = re.sub(r'\n{3,}', '\n\n', text)
            
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        
    return text.strip()
