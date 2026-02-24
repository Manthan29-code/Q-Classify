"""
Q-Classify - Concept Map Page
Interactive visualization of concepts and their relationships
"""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config import init_session_state, is_api_configured, render_api_key_sidebar
from services.ai_analyzer import ai_analyzer
from components.header import render_page_header, render_api_warning
from components.footer import render_compact_footer

# Page config
st.set_page_config(
    page_title="Concept Map | Q-Classify",
    page_icon="🗺️",
    layout="wide"
)

# Initialize session state
init_session_state()

# Custom CSS
st.markdown("""
<style>
    .map-container {
        background: linear-gradient(145deg, #1E1E2E, #2D2D44);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        min-height: 500px;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 5px 0;
    }
    .legend-dot {
        width: 15px;
        height: 15px;
        border-radius: 50%;
    }
    .concept-list {
        background: #2D2D44;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Page Header
render_page_header(
    "Concept Map",
    "🗺️",
    "Visual representation of concepts and their relationships"
)

# Check prerequisites
if not st.session_state.questions_data:
    st.warning("⚠️ Please complete the question analysis first")
    if st.button("🔍 Go to Analysis Page"):
        st.switch_page("pages/2_🔍_Analysis.py")
    st.stop()

if not st.session_state.syllabus_text:
    st.warning("⚠️ Please upload a syllabus first")
    if st.button("📤 Go to Upload Page"):
        st.switch_page("pages/1_📤_Upload_Files.py")
    st.stop()

questions_data = st.session_state.questions_data
syllabus_text = st.session_state.syllabus_text

# ==================== GENERATE CONCEPT GRAPH ====================
st.markdown("### 🕸️ Concept Relationship Graph")

# Check if graph data exists
if not st.session_state.concept_graph:
    if st.button("✨ Generate Concept Map", type="primary", width="stretch"):
        with st.spinner("🤖 AI is mapping concept relationships..."):
            try:
                # Check API
                if not render_api_warning():
                    st.stop()
                
                graph_data = ai_analyzer.extract_concepts_relationships(
                    syllabus_text,
                    questions_data
                )
                st.session_state.concept_graph = graph_data
                st.session_state.last_error = None
                st.rerun()
            except Exception as e:
                error_str = str(e)
                # Parse specific error types
                if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                    error_msg = "🚫 **API Quota Exceeded**: Your API usage limit has been reached. Please wait a few minutes or check your Google Cloud quota."
                elif "401" in error_str or "403" in error_str or "authentication" in error_str.lower():
                    error_msg = "🔑 **Authentication Error**: Invalid API key. Please check your GOOGLE_API_KEY in the .env file."
                elif "timeout" in error_str.lower() or "timed out" in error_str.lower():
                    error_msg = "⏱️ **Timeout Error**: The request took too long. Please try again."
                elif "connection" in error_str.lower() or "network" in error_str.lower():
                    error_msg = "🌐 **Connection Error**: Unable to reach the API. Please check your internet connection."
                else:
                    error_msg = f"❌ **Error**: {error_str}"
                
                st.warning(error_msg)
                st.info("📊 Generating basic concept map from analyzed questions instead...")
                
                # Fallback: generate basic graph from questions data
                graph_data = generate_basic_graph(questions_data)
                st.session_state.concept_graph = graph_data
                st.rerun()
    else:
        # Show previous error with retry option
        if st.session_state.get('last_error'):
            st.error(st.session_state.last_error)
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🔄 Retry", type="primary", width="stretch"):
                    st.session_state.last_error = None
                    st.rerun()
        
        # Show basic visualization while waiting
        st.info("👆 Click the button above to generate an AI-powered concept map")
        
        # Show simple concept list as preview
        st.markdown("#### 📋 Concepts Found in Questions")
        
        all_concepts = []
        for q in questions_data:
            all_concepts.extend(q.get('concepts', []))
        
        concept_counts = {}
        for c in all_concepts:
            concept_counts[c] = concept_counts.get(c, 0) + 1
        
        sorted_concepts = sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)
        
        col1, col2, col3 = st.columns(3)
        for i, (concept, count) in enumerate(sorted_concepts[:15]):
            col = [col1, col2, col3][i % 3]
            with col:
                st.markdown(f"""
                <div class="concept-list">
                    <span style="color: #9B59B6;">●</span>
                    <span style="color: #E0E0E0;">{concept}</span>
                    <span style="color: #888; float: right;">({count})</span>
                </div>
                """, unsafe_allow_html=True)
        
        st.stop()


def generate_basic_graph(questions_data):
    """Generate basic graph from questions data without AI"""
    nodes = []
    edges = []
    
    # Extract chapters and concepts
    chapters = set()
    concept_chapter_map = {}
    concept_counts = {}
    
    for q in questions_data:
        chapter = q.get('chapter', 'Unknown')
        chapters.add(chapter)
        
        for concept in q.get('concepts', []):
            concept_counts[concept] = concept_counts.get(concept, 0) + 1
            if concept not in concept_chapter_map:
                concept_chapter_map[concept] = set()
            concept_chapter_map[concept].add(chapter)
    
    # Create chapter nodes
    for chapter in chapters:
        nodes.append({
            'id': chapter,
            'type': 'chapter',
            'importance': 10
        })
    
    # Create concept nodes
    for concept, count in concept_counts.items():
        importance = min(count * 2, 10)
        nodes.append({
            'id': concept,
            'type': 'concept',
            'importance': importance
        })
        
        # Create edges to chapters
        for chapter in concept_chapter_map.get(concept, []):
            edges.append({
                'source': chapter,
                'target': concept,
                'relationship': 'contains'
            })
    
    return {'nodes': nodes, 'edges': edges}


# ==================== DISPLAY CONCEPT MAP ====================
if st.session_state.concept_graph:
    graph_data = st.session_state.concept_graph
    
    # Option to regenerate
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Regenerate"):
            st.session_state.concept_graph = None
            st.rerun()
    
    # Check for streamlit-agraph
    try:
        from streamlit_agraph import agraph, Node, Edge, Config
        
        # Prepare nodes
        nodes = []
        edges = []
        
        node_data = graph_data.get('nodes', [])
        edge_data = graph_data.get('edges', [])
        
        # Color scheme
        type_colors = {
            'chapter': '#4A90D9',
            'concept': '#9B59B6',
            'topic': '#2ECC71'
        }
        
        for node in node_data:
            node_id = node.get('id', '')
            node_type = node.get('type', 'concept')
            importance = node.get('importance', 5)
            
            size = 20 + (importance * 3)
            color = type_colors.get(node_type, '#888888')
            
            nodes.append(Node(
                id=node_id,
                label=node_id[:25] + ('...' if len(node_id) > 25 else ''),
                size=size,
                color=color,
                font={'color': '#FFFFFF', 'size': 12}
            ))
        
        for edge in edge_data:
            source = edge.get('source', '')
            target = edge.get('target', '')
            relationship = edge.get('relationship', 'related')
            
            # Edge color based on relationship
            edge_colors = {
                'requires': '#E74C3C',
                'related': '#4A90D9',
                'part_of': '#2ECC71',
                'contains': '#9B59B6'
            }
            
            edges.append(Edge(
                source=source,
                target=target,
                color=edge_colors.get(relationship, '#888888'),
                width=2
            ))
        
        # Graph configuration
        config = Config(
            width=1200,
            height=600,
            directed=True,
            physics=True,
            hierarchical=False,
            nodeHighlightBehavior=True,
            highlightColor='#F7A7A6',
            collapsible=True,
            node={'labelProperty': 'label'},
            link={'labelProperty': 'relationship', 'renderLabel': False}
        )
        
        # Display graph
        agraph(nodes=nodes, edges=edges, config=config)
        
        # Legend
        st.markdown("#### 📍 Legend")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="legend-item">
                <div class="legend-dot" style="background: #4A90D9;"></div>
                <span style="color: #E0E0E0;">Chapter</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="legend-item">
                <div class="legend-dot" style="background: #9B59B6;"></div>
                <span style="color: #E0E0E0;">Concept</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="legend-item">
                <div class="legend-dot" style="background: #2ECC71;"></div>
                <span style="color: #E0E0E0;">Topic</span>
            </div>
            """, unsafe_allow_html=True)
        
    except ImportError:
        st.warning("📦 streamlit-agraph is not installed. Showing alternative visualization.")
        
        # Alternative: Use Plotly network graph
        try:
            import plotly.graph_objects as go
            import networkx as nx
            
            # Create networkx graph
            G = nx.Graph()
            
            node_data = graph_data.get('nodes', [])
            edge_data = graph_data.get('edges', [])
            
            for node in node_data:
                G.add_node(node.get('id'), **node)
            
            for edge in edge_data:
                G.add_edge(edge.get('source'), edge.get('target'))
            
            # Get positions
            pos = nx.spring_layout(G, k=2, iterations=50)
            
            # Create edge traces
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=1, color='#4A90D9'),
                hoverinfo='none',
                mode='lines'
            )
            
            # Create node traces
            node_x = []
            node_y = []
            node_text = []
            node_colors = []
            
            type_colors = {'chapter': '#4A90D9', 'concept': '#9B59B6', 'topic': '#2ECC71'}
            
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(node)
                
                node_type = G.nodes[node].get('type', 'concept')
                node_colors.append(type_colors.get(node_type, '#888888'))
            
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=node_text,
                textposition='top center',
                textfont=dict(size=10, color='#E0E0E0'),
                marker=dict(
                    size=20,
                    color=node_colors,
                    line=dict(width=2, color='#FFFFFF')
                )
            )
            
            # Create figure
            fig = go.Figure(
                data=[edge_trace, node_trace],
                layout=go.Layout(
                    showlegend=False,
                    hovermode='closest',
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    plot_bgcolor='rgba(30,30,46,1)',
                    paper_bgcolor='rgba(30,30,46,1)',
                    height=600
                )
            )
            
            st.plotly_chart(fig, width="stretch")
            
        except Exception as e:
            st.error(f"Could not create visualization: {str(e)}")
            
            # Fallback: simple list view
            st.markdown("#### 📋 Concept Hierarchy")
            
            node_data = graph_data.get('nodes', [])
            chapters = [n for n in node_data if n.get('type') == 'chapter']
            concepts = [n for n in node_data if n.get('type') == 'concept']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📚 Chapters:**")
                for ch in chapters:
                    st.markdown(f"- {ch.get('id')}")
            
            with col2:
                st.markdown("**🎯 Concepts:**")
                for c in concepts[:15]:
                    st.markdown(f"- {c.get('id')}")

# ==================== CONCEPT STATISTICS ====================
st.markdown("---")
st.markdown("### 📊 Concept Statistics")

# Calculate statistics
all_concepts = []
chapter_concepts = {}

for q in questions_data:
    chapter = q.get('chapter', 'Unknown')
    concepts = q.get('concepts', [])
    
    all_concepts.extend(concepts)
    
    if chapter not in chapter_concepts:
        chapter_concepts[chapter] = []
    chapter_concepts[chapter].extend(concepts)

concept_counts = {}
for c in all_concepts:
    concept_counts[c] = concept_counts.get(c, 0) + 1

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🏆 Most Connected Concepts")
    sorted_concepts = sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)
    
    for concept, count in sorted_concepts[:10]:
        pct = count / len(questions_data) * 100
        st.markdown(f"""
        <div style="margin: 8px 0;">
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #E0E0E0;">{concept[:30]}{'...' if len(concept) > 30 else ''}</span>
                <span style="color: #888;">{count} ({pct:.1f}%)</span>
            </div>
            <div style="background: #1E1E2E; border-radius: 5px; height: 6px; margin-top: 4px;">
                <div style="background: #9B59B6; width: {pct}%; height: 100%; border-radius: 5px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("#### 📚 Concepts per Chapter")
    
    for chapter, concepts in sorted(chapter_concepts.items(), key=lambda x: len(set(x[1])), reverse=True)[:8]:
        unique_concepts = len(set(concepts))
        st.markdown(f"""
        <div style="background: #2D2D44; border-radius: 8px; padding: 10px; margin: 5px 0;">
            <span style="color: #4A90D9; font-weight: bold;">{chapter[:25]}{'...' if len(chapter) > 25 else ''}</span>
            <span style="color: #2ECC71; float: right;">{unique_concepts} concepts</span>
        </div>
        """, unsafe_allow_html=True)

# Sidebar - API Key Settings
render_api_key_sidebar()

# Sidebar - Stats
with st.sidebar:
    st.markdown("### 📊 Graph Stats")
    
    if st.session_state.concept_graph:
        nodes = st.session_state.concept_graph.get('nodes', [])
        edges = st.session_state.concept_graph.get('edges', [])
        
        st.metric("Nodes", len(nodes))
        st.metric("Connections", len(edges))
        
        chapters = len([n for n in nodes if n.get('type') == 'chapter'])
        concepts = len([n for n in nodes if n.get('type') == 'concept'])
        
        st.markdown("---")
        st.markdown(f"**Chapters:** {chapters}")
        st.markdown(f"**Concepts:** {concepts}")
    
    st.markdown("---")
    if st.button("📥 Download Report", width="stretch"):
        st.switch_page("pages/2_🔍_Analysis.py")

# Footer
render_compact_footer()
