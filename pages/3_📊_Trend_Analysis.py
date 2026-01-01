"""
Q-Classify - Trend Analysis Page
Identify recurring concepts and patterns across years
"""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config import init_session_state
from utils.helpers import calculate_concept_frequency, calculate_chapter_frequency
from services.ai_analyzer import ai_analyzer
from components.header import render_page_header
from components.footer import render_compact_footer

# Page config
st.set_page_config(
    page_title="Trend Analysis | Q-Classify",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
init_session_state()

# Custom CSS
st.markdown("""
<style>
    .trend-card {
        background: linear-gradient(145deg, #2D2D44, #1E1E2E);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #4A90D9;
    }
    .trend-title {
        color: #4A90D9;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .concept-bar {
        background: #2D2D44;
        border-radius: 8px;
        padding: 8px 15px;
        margin: 5px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .concept-name {
        color: #E0E0E0;
    }
    .concept-count {
        background: #9B59B6;
        color: white;
        padding: 2px 10px;
        border-radius: 10px;
        font-size: 0.85rem;
    }
    .insight-box {
        background: rgba(46, 204, 113, 0.1);
        border-left: 4px solid #2ECC71;
        padding: 1rem;
        border-radius: 0 10px 10px 0;
        margin: 1rem 0;
    }
    .insight-title {
        color: #2ECC71;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Page Header
render_page_header(
    "Trend Analysis",
    "📊",
    "Discover recurring concepts and question patterns across different years"
)

# Check prerequisites
if not st.session_state.questions_data:
    st.warning("⚠️ Please complete the question analysis first")
    if st.button("🔍 Go to Analysis Page"):
        st.switch_page("pages/2_🔍_Analysis.py")
    st.stop()

questions_data = st.session_state.questions_data

# ==================== GENERATE TRENDS ====================
if not st.session_state.trend_data:
    with st.spinner("Analyzing trends..."):
        trend_data = ai_analyzer.identify_trends(questions_data)
        st.session_state.trend_data = trend_data
else:
    trend_data = st.session_state.trend_data

# ==================== OVERVIEW ====================
st.markdown("### 📈 Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Questions", trend_data.get('total_questions', len(questions_data)))

with col2:
    st.metric("Unique Chapters", len(trend_data.get('top_chapters', [])))

with col3:
    st.metric("Unique Concepts", len(trend_data.get('top_concepts', [])))

with col4:
    years = set(q.get('year') for q in questions_data if q.get('year'))
    st.metric("Years Covered", len(years) if years else "N/A")

st.markdown("---")

# ==================== CONCEPT FREQUENCY ====================
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎯 Most Tested Concepts")
    
    top_concepts = trend_data.get('top_concepts', [])[:15]
    
    if top_concepts:
        # Create chart data
        import plotly.express as px
        import pandas as pd
        
        df = pd.DataFrame(top_concepts, columns=['Concept', 'Count'])
        
        fig = px.bar(
            df,
            x='Count',
            y='Concept',
            orientation='h',
            color='Count',
            color_continuous_scale=['#4A90D9', '#9B59B6', '#2ECC71']
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#E0E0E0',
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'},
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No concept data available")

with col2:
    st.markdown("### 📚 Chapter Distribution")
    
    top_chapters = trend_data.get('top_chapters', [])[:10]
    
    if top_chapters:
        import plotly.express as px
        import pandas as pd
        
        df = pd.DataFrame(top_chapters, columns=['Chapter', 'Questions'])
        
        fig = px.pie(
            df,
            values='Questions',
            names='Chapter',
            hole=0.4,
            color_discrete_sequence=['#4A90D9', '#9B59B6', '#2ECC71', '#F39C12', '#E74C3C']
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#E0E0E0',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No chapter data available")

# ==================== DIFFICULTY DISTRIBUTION ====================
st.markdown("---")
st.markdown("### 📊 Difficulty Distribution")

difficulty_data = trend_data.get('difficulty_distribution', {})

if difficulty_data:
    import plotly.express as px
    import pandas as pd
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        df = pd.DataFrame([
            {'Difficulty': k, 'Count': v}
            for k, v in difficulty_data.items()
        ])
        
        colors = {'Easy': '#2ECC71', 'Medium': '#F39C12', 'Hard': '#E74C3C'}
        df['Color'] = df['Difficulty'].map(colors)
        
        fig = px.bar(
            df,
            x='Difficulty',
            y='Count',
            color='Difficulty',
            color_discrete_map=colors
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#E0E0E0',
            showlegend=False,
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        total = sum(difficulty_data.values())
        for diff, count in difficulty_data.items():
            pct = round(count / total * 100) if total > 0 else 0
            color = colors.get(diff, '#888')
            st.markdown(f"""
            <div style="margin: 10px 0;">
                <span style="color: {color}; font-weight: bold;">{diff}</span>
                <span style="color: #888;"> - {count} questions ({pct}%)</span>
            </div>
            """, unsafe_allow_html=True)

# ==================== YEARLY TRENDS ====================
yearly_data = trend_data.get('yearly_trends', {})

if yearly_data:
    st.markdown("---")
    st.markdown("### 📅 Yearly Trends")
    
    years = sorted(yearly_data.keys())
    
    if len(years) > 1:
        import plotly.graph_objects as go
        import pandas as pd
        
        # Get all chapters across years
        all_chapters = set()
        for year_data in yearly_data.values():
            all_chapters.update(year_data.get('chapters', {}).keys())
        
        # Create data for stacked bar chart
        fig = go.Figure()
        
        colors = ['#4A90D9', '#9B59B6', '#2ECC71', '#F39C12', '#E74C3C', '#1ABC9C', '#E91E63']
        
        for i, chapter in enumerate(list(all_chapters)[:7]):
            y_values = []
            for year in years:
                count = yearly_data.get(year, {}).get('chapters', {}).get(chapter, 0)
                y_values.append(count)
            
            fig.add_trace(go.Bar(
                name=chapter[:20],
                x=[str(y) for y in years],
                y=y_values,
                marker_color=colors[i % len(colors)]
            ))
        
        fig.update_layout(
            barmode='stack',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#E0E0E0',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Need multiple years of data for yearly trend analysis")

# ==================== INSIGHTS ====================
st.markdown("---")
st.markdown("### 💡 Key Insights")

col1, col2 = st.columns(2)

with col1:
    # Most important concepts
    if top_concepts:
        st.markdown("""
        <div class="insight-box">
            <div class="insight-title">🎯 Focus Areas</div>
            <p style="color: #E0E0E0;">Based on frequency analysis, prioritize these concepts:</p>
        </div>
        """, unsafe_allow_html=True)
        
        for concept, count in top_concepts[:5]:
            st.markdown(f"- **{concept}** ({count} questions)")

with col2:
    # Difficulty insight
    if difficulty_data:
        total = sum(difficulty_data.values())
        hard_pct = round(difficulty_data.get('Hard', 0) / total * 100) if total > 0 else 0
        easy_pct = round(difficulty_data.get('Easy', 0) / total * 100) if total > 0 else 0
        
        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-title">📈 Difficulty Analysis</div>
            <p style="color: #E0E0E0;">
                <b>{hard_pct}%</b> of questions are Hard level.<br>
                <b>{easy_pct}%</b> of questions are Easy level.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if hard_pct > 40:
            st.warning("⚠️ High proportion of difficult questions. Focus on deep understanding.")
        elif easy_pct > 50:
            st.success("✅ Many straightforward questions. Good coverage of basics.")

# Sidebar
with st.sidebar:
    st.markdown("### 📊 Quick Stats")
    st.metric("Questions Analyzed", len(questions_data))
    
    if top_concepts:
        st.markdown("**Top 3 Concepts:**")
        for concept, count in top_concepts[:3]:
            st.markdown(f"- {concept} ({count})")
    
    st.markdown("---")
    if st.button("🔍 Search Questions", use_container_width=True):
        st.switch_page("pages/4_🔎_Custom_Search.py")
    if st.button("📝 View Summary", use_container_width=True):
        st.switch_page("pages/5_📝_Summary.py")

# Footer
render_compact_footer()
