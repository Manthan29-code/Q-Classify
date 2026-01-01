"""
Q-Classify Configuration Module
Handles session state and app configuration
"""

import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # API Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    
    # Model Configuration - Read from .env
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.3"))
    
    # Available Gemini Models (for selection box)
    AVAILABLE_MODELS = [
        {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "description": "Best accuracy, 1M token context"},
        {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash", "description": "Fast & cost-effective"},
        {"id": "gemini-1.5-flash-8b", "name": "Gemini 1.5 Flash-8B", "description": "Fastest, most economical"},
        {"id": "gemini-1.0-pro", "name": "Gemini 1.0 Pro", "description": "Legacy model"},
    ]
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    UPLOADS_DIR = DATA_DIR / "uploads"
    OUTPUTS_DIR = DATA_DIR / "outputs"
    ASSETS_DIR = BASE_DIR / "assets"
    
    # Ensure directories exist
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Theme colors
    PRIMARY_COLOR = "#4A90D9"      # Blue
    SECONDARY_COLOR = "#2ECC71"    # Green
    ACCENT_COLOR = "#9B59B6"       # Purple
    
    # Difficulty levels
    DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]
    
    # File size limits (in MB)
    MAX_FILE_SIZE_MB = 50


def init_session_state():
    """Initialize all session state variables"""
    
    # File storage
    if 'syllabus_file' not in st.session_state:
        st.session_state.syllabus_file = None
    
    if 'syllabus_text' not in st.session_state:
        st.session_state.syllabus_text = None
    
    if 'syllabus_chapters' not in st.session_state:
        st.session_state.syllabus_chapters = []
    
    if 'question_papers' not in st.session_state:
        st.session_state.question_papers = []  # List of dicts with 'name', 'text', 'year'
    
    # Analysis results
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    if 'questions_data' not in st.session_state:
        st.session_state.questions_data = []  # List of analyzed questions
    
    if 'trend_data' not in st.session_state:
        st.session_state.trend_data = None
    
    if 'concept_graph' not in st.session_state:
        st.session_state.concept_graph = None
    
    if 'syllabus_summary' not in st.session_state:
        st.session_state.syllabus_summary = None
    
    # Processing state
    if 'is_processing' not in st.session_state:
        st.session_state.is_processing = False
    
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    
    # Error tracking
    if 'last_error' not in st.session_state:
        st.session_state.last_error = None
    
    if 'syllabus_path' not in st.session_state:
        st.session_state.syllabus_path = None


def clear_session_state():
    """Clear all analysis data from session state and delete uploaded files"""
    # Delete uploaded files from disk
    try:
        for file in Config.UPLOADS_DIR.iterdir():
            if file.is_file():
                file.unlink()
    except Exception as e:
        print(f"Error deleting files: {e}")
    
    # Clear session state
    st.session_state.syllabus_file = None
    st.session_state.syllabus_text = None
    st.session_state.syllabus_chapters = []
    st.session_state.syllabus_path = None
    st.session_state.question_papers = []
    st.session_state.analysis_results = None
    st.session_state.questions_data = []
    st.session_state.trend_data = None
    st.session_state.concept_graph = None
    st.session_state.syllabus_summary = None
    st.session_state.is_processing = False
    st.session_state.analysis_complete = False
    st.session_state.last_error = None


def restore_files_from_disk():
    "Restore uploaded files from disk on page load "
    from services.pdf_extractor import pdf_extractor
    from utils.helpers import extract_year_from_filename
    
    # Check if files exist but session state is empty
    if st.session_state.syllabus_text is None or not st.session_state.question_papers:
        try:
            for file in Config.UPLOADS_DIR.iterdir():
                if file.is_file() and file.suffix.lower() == '.pdf':
                    file_content = file.read_bytes()
                    
                    if file.name.startswith('syllabus_') and st.session_state.syllabus_text is None:
                        extraction = pdf_extractor.extract_text(file_content, file.name)
                        if extraction['success']:
                            st.session_state.syllabus_file = file.name.replace('syllabus_', '')
                            st.session_state.syllabus_text = extraction['text']
                            st.session_state.syllabus_path = str(file)
                    
                    elif file.name.startswith('paper_') and not any(
                        p['name'] == file.name.replace('paper_', '') 
                        for p in st.session_state.question_papers
                    ):
                        extraction = pdf_extractor.extract_text(file_content, file.name)
                        if extraction['success']:
                            original_name = file.name.replace('paper_', '')
                            year = extract_year_from_filename(original_name)
                            st.session_state.question_papers.append({
                                'name': original_name,
                                'text': extraction['text'],
                                'year': year,
                                'pages': extraction['page_count'],
                                'method': extraction['method'],
                                'path': str(file)
                            })
        except Exception as e:
            print(f"Error restoring files: {e}")


def get_api_key():
    """Get Google API key with validation"""
    api_key = Config.GOOGLE_API_KEY
    if not api_key or api_key == "your_gemini_api_key_here":
        return None
    return api_key


def is_api_configured():
    """Check if API is properly configured"""
    return get_api_key() is not None
