import streamlit as st
import time
from utils.rag import answer_question

# --- Page Configuration ---
st.set_page_config(
    page_title="Pakistan Law Helper",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS for Legal Assistant Styling ---
st.markdown("""
    <style>
        /* Base styles and typography */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        .main-title {
            font-size: 2.8rem;
            font-weight: 800;
            color: #1e293b;
            margin-bottom: 0.5rem;
            letter-spacing: -0.02em;
        }
        .sub-title {
            font-size: 1.15rem;
            color: #64748b;
            font-weight: 400;
            margin-bottom: 2.5rem;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 1rem;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #f8fafc;
            border-right: 1px solid #e2e8f0;
        }
        .sidebar-header {
            font-size: 1.2rem;
            font-weight: 600;
            color: #0f172a;
            margin-bottom: 1rem;
        }
        
        /* Answer Section */
        .answer-box {
            background-color: #ffffff;
            border-left: 4px solid #0ea5e9;
            padding: 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            margin-bottom: 2.5rem;
            font-size: 1.05rem;
            line-height: 1.6;
            color: #334155;
            white-space: pre-wrap;
        }
        
        /* Source Citation Cards */
        .citation-header {
            font-size: 1.25rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 0.5rem;
        }
        .source-card {
            background-color: #f1f5f9;
            border: 1px solid #cbd5e1;
            border-radius: 0.5rem;
            padding: 1.25rem;
            margin-bottom: 1rem;
            transition: transform 0.2s ease-in-out;
        }
        .source-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        .source-title {
            font-weight: 700;
            color: #0f172a;
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .badge-container {
            display: flex;
            gap: 0.5rem;
        }
        .badge {
            background-color: #e2e8f0;
            color: #475569;
            padding: 0.2rem 0.6rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
        }
        .badge-province {
            background-color: #dbeafe;
            color: #1e40af;
        }
        .source-text {
            background-color: #ffffff;
            padding: 1rem;
            border: 1px solid #e2e8f0;
            border-radius: 0.375rem;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 0.9rem;
            color: #334155;
            white-space: pre-wrap;
            margin-top: 0.75rem;
        }
        
        /* Empty State */
        .empty-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 4rem 2rem;
            text-align: center;
            background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
            border: 1px solid #e2e8f0;
            border-radius: 1rem;
            margin-top: 2rem;
        }
        .empty-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            opacity: 0.9;
        }
        .empty-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #334155;
            margin-bottom: 0.5rem;
        }
        .empty-text {
            color: #64748b;
            max-width: 500px;
            margin: 0 auto;
        }
        
        /* Footer */
        .footer {
            margin-top: 4rem;
            padding-top: 1.5rem;
            border-top: 1px solid #e2e8f0;
            text-align: center;
            font-size: 0.85rem;
            color: #94a3b8;
        }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown('<div class="sidebar-header">⚙️ Configuration</div>', unsafe_allow_html=True)
    
    province = st.selectbox(
        "Jurisdiction",
        options=["Federal", "Punjab", "Khyber Pakhtunkhwa", "Sindh", "Balochistan"],
        index=0,
        help="Select the jurisdiction to filter laws. Federal laws will always be considered."
    )
    
    st.markdown("---")
    st.markdown("""
        ### About
        **Pakistan Law Helper** uses a localized AI engine to retrieve sections of the law and answer your legal questions.
        
        **Features:**
        - Offline Document Retrieval
        - Hybrid Search (TF-IDF + Keyword)
        - Strict Source Validation
        
        *Version 1.1.0*
    """)

# --- Main Layout ---
st.markdown('<div class="main-title">Pakistan Law Helper <span style="color:#0ea5e9;">⚖️</span></div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Intelligent Legal Research & Document Retrieval</div>', unsafe_allow_html=True)

# Input Section
st.markdown("### Describe your legal query")
question = st.text_area(
    "Query",
    placeholder="e.g., What is the punishment for cyber terrorism under PECA?",
    height=100,
    label_visibility="collapsed"
)

# Center the button nicely
col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
with col3:
    ask_button = st.button("Retrieve & Analyze", type="primary", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Output Section
if ask_button:
    if not question.strip():
        st.warning("Please enter a legal query.", icon="⚠️")
    else:
        with st.spinner("Searching local index and generating legal analysis..."):
            time.sleep(1) # UX slight delay
            answer, retrieved_sources = answer_question(question, province)
        
        # Display Answer
        st.markdown("### 🧠 AI Analysis")
        st.markdown(f'<div class="answer-box">{answer}</div>', unsafe_allow_html=True)
        
        # Display Sources
        if retrieved_sources:
            st.markdown('<div class="citation-header">📚 Retrieved Legal Citations</div>', unsafe_allow_html=True)
            
            for src in retrieved_sources:
                law_name = src.get('law_name', 'Unknown Act')
                year = src.get('year', 'N/A')
                sec_num = src.get('section_number', 'N/A')
                prov = src.get('province', 'Federal')
                text = src.get('section_text', '')
                
                st.markdown(f"""
                    <div class="source-card">
                        <div class="source-title">
                            <span>{law_name} ({year})</span>
                            <div class="badge-container">
                                <span class="badge">Section {sec_num}</span>
                                <span class="badge badge-province">{prov}</span>
                            </div>
                        </div>
                        <div class="source-text">{text}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No corresponding legal sections were found in the local database.", icon="ℹ️")
            
else:
    # Empty State
    st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🏛️</div>
            <div class="empty-title">Ready to assist</div>
            <div class="empty-text">
                Enter your legal question above. The system will securely search through the locally indexed Pakistani laws and provide an analysis supported by direct citations.
            </div>
        </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown(
    '<div class="footer">'
    '<b>Disclaimer:</b> This application provides AI-generated assistance based on retrieved documents and does not constitute professional legal advice. Consult a qualified attorney for legal matters.'
    '</div>',
    unsafe_allow_html=True
)

