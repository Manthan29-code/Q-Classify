"""
Q-Classify Footer Component
Reusable footer component for all pages
"""

import streamlit as st


def render_footer():
    """Render the standard footer"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1E1E2E 0%, #2D2D44 100%);
                padding: 1.5rem;
                border-radius: 15px;
                text-align: center;
                margin-top: 3rem;
                border-top: 3px solid #4A90D9;">
        <p style="color: #B0B0C0; margin: 0;">
            🎓 Empowering students with AI-driven learning insights.
        </p>
        <p style="color: #6c757d; font-size: 0.8rem; margin-top: 0.5rem;">
            Built with Streamlit • Powered by Google Gemini AI
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_compact_footer():
    """Render a compact footer for inner pages"""
    st.markdown("""
    <div style="text-align: center; padding: 1rem; margin-top: 2rem; 
                border-top: 1px solid #4A90D9;">
        <p style="color: #888; font-size: 0.8rem; margin: 0;">
            Q-Classify • AI-Powered Question Analysis
        </p>
    </div>
    """, unsafe_allow_html=True)
