import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

def clean_text(text: str) -> str:
    """
    Cleans up unwanted characters, normalizes whitespace, and handles edge cases.
    Reusable for PDF, Image (OCR), or plain text inputs.
    """
    if not text:
        return ""
    
    # 1. Remove obscure control characters (keeping \n and \t)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # 2. Remove zero-width formatting characters (common in PDFs/web scrapes)
    text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)
    
    # 3. Normalize whitespace: replace multiple spaces/tabs with a single space
    text = re.sub(r'[ \t]+', ' ', text)
    
    # 4. Normalize newlines: replace 3+ consecutive newlines with just 2 (standard paragraph break)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def count_words(text: str) -> int:
    """
    Returns the word count of the provided text.
    """
    if not text:
        return 0
    return len(text.split())

def calculate_compression_ratio(original: str, summary: str) -> dict:
    """
    Calculates word counts and compression ratio for the summarizer.
    """
    orig_count = count_words(original)
    summ_count = count_words(summary)
    
    ratio = 0.0
    if orig_count > 0:
        ratio = round((summ_count / orig_count) * 100, 2)
        
    return {
        "original_words": orig_count,
        "summary_words": summ_count,
        "compression_ratio": f"{ratio}%"
    }

def generate_pdf(summary_text: str) -> bytes:
    """
    Takes plain text and generates a cleanly formatted PDF document.
    Returns the raw bytes of the PDF.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=72, leftMargin=72,
        topMargin=72, bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Custom, clean document styles
    style = styles["Normal"]
    style.fontSize = 11
    style.leading = 16  # Clean line height for readability
    style.spaceAfter = 14 # Space between paragraphs
    
    title_style = styles["Title"]
    title_style.fontSize = 18
    title_style.spaceAfter = 20
    
    story = []
    
    # Add Header Title
    story.append(Paragraph("AI Generated Summary", title_style))
    story.append(Spacer(1, 10))
    
    # Splitting to handle paragraphs smoothly
    paragraphs = summary_text.split('\n')
    
    for p in paragraphs:
        if p.strip():
            story.append(Paragraph(p.strip(), style))
            
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
