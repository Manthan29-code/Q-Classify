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
    
    # Model Configuration - Read from .env (fallback defaults)
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.3"))
    
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
    """Get Google API key - checks sidebar input first, then .env"""
    # Priority 1: Sidebar input (stored in session state)
    if st.session_state.get('gemini_api_key'):
        st.session_state.api_key_source = 'sidebar'
        return st.session_state.gemini_api_key
    
    # Priority 2: Environment variable from .env
    if Config.GOOGLE_API_KEY:
        st.session_state.api_key_source = 'env'
        return Config.GOOGLE_API_KEY
    
    st.session_state.api_key_source = None
    return None


def is_api_configured():
    """Check if API is properly configured"""
    return get_api_key() is not None


def get_api_key_source():
    """Get the source of the current API key"""
    get_api_key()  # This updates the source
    return st.session_state.get('api_key_source')


def validate_api_key(api_key: str, model_id: str = None) -> tuple:
    """
    Validate a Gemini API key and optionally check if selected model is accessible.
    
    Args:
        api_key: The API key to validate
        model_id: Optional model ID to test (if None, just validates key)
    
    Returns:
        tuple: (is_valid, message)
    """
    if not api_key or not api_key.strip():
        return False, "API key cannot be empty"
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Step 1: List models to validate API key (doesn't consume tokens)
        available_models = list(genai.list_models())
        
        if not available_models:
            return False, "API key validation failed - no models available"
        
        # Step 2: If model_id provided, check if it's accessible
        if model_id:
            # Get list of model names user has access to
            accessible_model_names = [m.name for m in available_models]
            
            # Check if selected model (or its variations) is in the list
            model_accessible = any(
                model_id in name or name.endswith(model_id) 
                for name in accessible_model_names
            )
            
            if not model_accessible:
                # Try a minimal test call to confirm
                try:
                    model = genai.GenerativeModel(model_id)
                    response = model.generate_content(
                        "Hi",
                        generation_config={"max_output_tokens": 5}
                    )
                    if response:
                        return True, f"API key valid, model '{model_id}' accessible"
                except Exception as model_error:
                    error_msg = str(model_error).lower()
                    if "not found" in error_msg or "404" in error_msg:
                        return False, f"Model '{model_id}' not available. Try a different model."
                    elif "permission" in error_msg or "403" in error_msg:
                        return False, f"No access to '{model_id}'. May require billing."
                    elif "quota" in error_msg or "429" in error_msg:
                        # Quota error means model IS accessible, just rate limited
                        return True, f"API key valid (quota limited)"
                    else:
                        return False, f"Model error: {str(model_error)[:80]}"
            
            return True, f"API key valid, model '{model_id}' accessible"
        
        return True, "API key is valid"
        
    except Exception as e:
        error_str = str(e).lower()
        if "api_key" in error_str or "invalid" in error_str or "401" in error_str:
            return False, "Invalid API key. Please check and try again."
        elif "quota" in error_str or "429" in error_str:
            return False, "API quota exceeded. Key is valid but rate limited."
        elif "permission" in error_str or "403" in error_str:
            return False, "API key lacks required permissions."
        else:
            return False, f"Validation error: {str(e)[:100]}"


def get_selected_model():
    """Get the currently selected model - checks session state first, then .env"""
    from utils.models import DEFAULT_MODEL
    
    if st.session_state.get('selected_model'):
        return st.session_state.selected_model
    if Config.GEMINI_MODEL:
        return Config.GEMINI_MODEL
    return DEFAULT_MODEL


def get_selected_temperature():
    """Get the currently selected temperature - checks session state first, then .env"""
    from utils.models import DEFAULT_TEMPERATURE
    
    if st.session_state.get('selected_temperature') is not None:
        return st.session_state.selected_temperature
    if Config.TEMPERATURE is not None:
        return Config.TEMPERATURE
    return DEFAULT_TEMPERATURE


def render_api_key_sidebar():
    """
    Render API key and model configuration section in sidebar.
    Call this function in every page's sidebar.
    """
    from utils.models import (
        AVAILABLE_MODELS, DEFAULT_MODEL, DEFAULT_TEMPERATURE,
        TEMPERATURE_PRESETS, get_model_ids, get_recommended_model
    )
    
    # Initialize API-related session state
    if 'gemini_api_key' not in st.session_state:
        st.session_state.gemini_api_key = None
    if 'api_key_source' not in st.session_state:
        st.session_state.api_key_source = None
    if 'api_key_valid' not in st.session_state:
        st.session_state.api_key_valid = None
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = Config.GEMINI_MODEL or DEFAULT_MODEL
    if 'selected_temperature' not in st.session_state:
        st.session_state.selected_temperature = Config.TEMPERATURE if Config.TEMPERATURE is not None else DEFAULT_TEMPERATURE
    
    with st.sidebar:
        # API Key Settings
        with st.expander("🔑 API Key", expanded=not is_api_configured()):
            # Show current status
            current_key = get_api_key()
            source = get_api_key_source()
            
            if current_key:
                if source == 'sidebar':
                    st.success("✅ Configured (sidebar)")
                else:
                    st.success("✅ Configured (.env)")
                
                # Show masked key preview
                masked = current_key[:8] + "..." + current_key[-4:] if len(current_key) > 12 else "****"
                st.caption(f"`{masked}`")
            else:
                st.warning("⚠️ Not configured")
                st.caption("Enter your Gemini API key to use AI features.")
            
            st.markdown("---")
            
            # API Key input
            new_key = st.text_input(
                "Gemini API Key",
                type="password",
                placeholder="AIzaSy...",
                help="Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)",
                key="api_key_input"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("💾 Save", use_container_width=True, type="primary"):
                    if new_key and new_key.strip():
                        # Get currently selected model to validate
                        model_to_test = st.session_state.get('selected_model') or get_selected_model()
                        
                        with st.spinner(f"Validating key & model..."):
                            is_valid, message = validate_api_key(new_key.strip(), model_to_test)
                        
                        if is_valid:
                            st.session_state.gemini_api_key = new_key.strip()
                            st.session_state.api_key_valid = True
                            st.toast("✅ API key saved!", icon="✅")
                            
                            try:
                                from services.ai_analyzer import ai_analyzer
                                ai_analyzer.update_api_key(new_key.strip())
                            except:
                                pass
                            
                            st.rerun()
                        else:
                            st.session_state.api_key_valid = False
                            st.toast(f"❌ {message}", icon="🚫")
                            st.error(message)
                    else:
                        st.toast("⚠️ Enter an API key", icon="⚠️")
            
            with col2:
                if st.button("🗑️ Clear", use_container_width=True):
                    st.session_state.gemini_api_key = None
                    st.session_state.api_key_valid = None
                    st.session_state.api_key_source = None
                    st.toast("API key cleared", icon="🗑️")
                    st.rerun()
            
            st.markdown("[Get API Key →](https://aistudio.google.com/app/apikey)")
        
        # Model Settings
        with st.expander("🤖 Model Settings", expanded=False):
            # Model selection
            model_ids = get_model_ids()
            model_options = {m["id"]: f"{m['name']} {'⭐' if m.get('recommended') else ''}" for m in AVAILABLE_MODELS}
            
            current_model = st.session_state.selected_model
            if current_model not in model_ids:
                current_model = get_recommended_model()
            current_index = model_ids.index(current_model) if current_model in model_ids else 0
            
            selected_model = st.selectbox(
                "Model",
                options=model_ids,
                index=current_index,
                format_func=lambda x: model_options.get(x, x),
                help="Choose the Gemini model",
                key="model_selector"
            )
            
            # Show model description
            for m in AVAILABLE_MODELS:
                if m["id"] == selected_model:
                    st.caption(f"ℹ️ {m.get('description', '')}")
                    break
            
            st.markdown("---")
            
            # Temperature selection
            st.markdown("**Temperature**")
            preset_names = list(TEMPERATURE_PRESETS.keys())
            current_temp = st.session_state.selected_temperature
            
            # Find matching preset
            current_preset_idx = 1  # Default to "Balanced"
            for i, (name, value) in enumerate(TEMPERATURE_PRESETS.items()):
                if abs(value - current_temp) < 0.05:
                    current_preset_idx = i
                    break
            
            selected_preset = st.selectbox(
                "Preset",
                options=preset_names,
                index=current_preset_idx,
                key="temp_preset",
                help="Quick temperature presets"
            )
            
            preset_temp = TEMPERATURE_PRESETS[selected_preset]
            
            selected_temp = st.slider(
                "Fine-tune",
                min_value=0.0,
                max_value=1.0,
                value=preset_temp,
                step=0.1,
                key="temp_slider",
                help="Lower = consistent, Higher = creative"
            )
            
            # Save button
            if st.button("💾 Save Settings", use_container_width=True, type="secondary"):
                st.session_state.selected_model = selected_model
                st.session_state.selected_temperature = selected_temp
                
                try:
                    from services.ai_analyzer import ai_analyzer
                    ai_analyzer.set_model(selected_model)
                    ai_analyzer.set_temperature(selected_temp)
                except:
                    pass
                
                st.toast(f"✅ Model: {selected_model}, Temp: {selected_temp}", icon="🤖")
                st.rerun()
            
            # Current settings display
            st.markdown("---")
            st.caption(f"📌 **Model:** {st.session_state.selected_model}")
            st.caption(f"🌡️ **Temp:** {st.session_state.selected_temperature}")
