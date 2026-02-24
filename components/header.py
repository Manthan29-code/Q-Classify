"""
Q-Classify Header Component
Reusable header component for all pages
"""

import streamlit as st


def render_header(title: str = "Q-Classify", subtitle: str = None, show_api_status: bool = True):
    """
    Render the page header with optional API status indicator
    
    Args:
        title: Main title text
        subtitle: Optional subtitle
        show_api_status: Whether to show API configuration status
    """
    from utils.config import is_api_configured, get_api_key_source
    
    # Header container
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 2rem;">🎓</span>
            <div>
                <h1 style="margin: 0; color: #4A90D9; font-size: 1.8rem;">{title}</h1>
                {f'<p style="margin: 0; color: #888; font-size: 0.9rem;">{subtitle}</p>' if subtitle else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if show_api_status:
            if is_api_configured():
                source = get_api_key_source()
                source_label = "sidebar" if source == "sidebar" else ".env"
                st.markdown(f"""
                <div style="text-align: right; padding: 10px;">
                    <span style="background: #2ECC71; color: white; padding: 5px 12px; 
                           border-radius: 15px; font-size: 0.8rem;">
                        ✓ API Connected ({source_label})
                    </span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align: right; padding: 10px;">
                    <span style="background: #E74C3C; color: white; padding: 5px 12px; 
                           border-radius: 15px; font-size: 0.8rem;">
                        ⚠ API Not Configured
                    </span>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 10px 0 20px 0; border-color: #4A90D9;'>", unsafe_allow_html=True)


def render_page_header(page_title: str, page_icon: str, description: str = None):
    """
    Render a styled page header for individual pages
    """
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #4A90D9 0%, #9B59B6 100%);
                padding: 1.5rem 2rem;
                border-radius: 15px;
                margin-bottom: 1.5rem;">
        <h2 style="color: white; margin: 0; display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.8rem;">{page_icon}</span>
            {page_title}
        </h2>
        {f'<p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">{description}</p>' if description else ''}
    </div>
    """, unsafe_allow_html=True)


def render_api_warning():
    """Render a warning if API is not configured"""
    from utils.config import is_api_configured
    
    if not is_api_configured():
        st.warning("""
        ⚠️ **API Key Not Configured**
        
        Please add your Google Gemini API key using one of these methods:
        
        **Option 1: Sidebar (Recommended for deployed apps)**
        - Look for the "🔑 API Settings" section in the sidebar
        - Enter your API key and click "Save Key"
        
        **Option 2: Environment file (For local development)**
        - Add to your `.env` file: `GOOGLE_API_KEY=your_api_key`
        
        [Get your API key from Google AI Studio](https://aistudio.google.com/app/apikey)
        """)
        return False
    return True
