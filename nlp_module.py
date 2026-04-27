import torch
from transformers import pipeline
from langdetect import detect
from googletrans import Translator
import logging

# Initialize translator
translator = Translator()

# Lazy loading for models
models = {}

def get_summarizer():
    if 'fast' not in models:
        # Use an extremely fast and lightweight summarizer (approx 240MB)
        # This is massively faster than distilbart or mt5 on a CPU!
        models['fast'] = pipeline("summarization", model="Falconsai/text_summarization")
    return models['fast']

def detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return 'en'

def translate_text(text: str, target_language: str) -> str:
    if not text or target_language == 'auto':
        return text
    try:
        result = translator.translate(text, dest=target_language, src='auto')
        return result.text
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def chunk_text(text: str, chunk_size: int = 400) -> list:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks

def _core_summarize(text: str, length: str) -> str:
    """Core summarization handling chunking."""
    length_mapping = {
        'short': {"max_length": 60, "min_length": 25},
        'medium': {"max_length": 120, "min_length": 50},
        'long': {"max_length": 250, "min_length": 100}
    }
    params = length_mapping.get(length, length_mapping['medium'])
    summarizer = get_summarizer()
    
    chunks = chunk_text(text, chunk_size=400) 
    summaries = []
    for chunk in chunks:
        # The fast T5 model requires the 'summarize: ' prefix
        prompt = f"summarize: {chunk}"
        try:
            res = summarizer(prompt, **params, truncation=True)
            summaries.append(res[0]['summary_text'])
        except Exception as e:
            print(f"Error summarizing chunk: {e}")
            
    final_summary = " ".join(summaries)
    # Recursively summarize if the summary is still too long
    if len(final_summary.split()) > 1000 and len(chunks) > 2:
        return _core_summarize(final_summary, length)
    return final_summary

def summarize_text(text: str, target_lang: str, length: str) -> str:
    """
    Decides the summarization approach based on the input text language.
    1. Detect language
    2. If not English -> Translate to English (Very fast via API)
    3. Summarize using lightweight English model (Extremely fast)
    4. If target_lang not English -> Translate to target_lang
    """
    # 1. Detect Language
    source_lang = detect_language(text)
    
    # 2. Translate to English if needed
    working_text = text
    if source_lang != 'en':
        working_text = translate_text(text, target_language='en')
        
    # 3. Summarize Text
    english_summary = _core_summarize(working_text, length=length)
    
    # 4. Translate out to target
    if target_lang != 'en':
        final_summary = translate_text(english_summary, target_language=target_lang)
        return final_summary
        
    return english_summary
