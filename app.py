import streamlit as st
from pathlib import Path
from io import BytesIO
import time

from pdf_search_engine import PDFSearchEngine
from config import Config

st.set_page_config(
    page_title="AI PDF Search Engine",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def initialize_search_engine():
    try:
        Config.validate()
        engine = PDFSearchEngine()
        return engine, None
    except Exception as e:
        return None, str(e)

def main():
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 20px;
        height: 3rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI PDF Search Engine</h1>
        <p style="font-size: 1.2rem; color: #666;">Upload PDFs and ask questions with AI-powered conversation memory</p>
    </div>
    """, unsafe_allow_html=True)
    
    search_engine, error = initialize_search_engine()
    
    if error:
        st.error(f"Configuration Error: {error}")
        with st.expander("🔧 Setup Instructions"):
            st.code("""
# Create .env file with:
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here  
PINECONE_INDEX_NAME=husnain
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=512
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
            """)
        return
    
    if 'search_engine' not in st.session_state:
        st.session_state.search_engine = search_engine
    
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = st.session_state.search_engine.start_conversation()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    with st.sidebar:
        st.markdown("## 📁 Document Upload")
        
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            accept_multiple_files=True,
            type="pdf",
            help="Upload one or more PDF files to search through"
        )
        
        if uploaded_files:
            if st.button("🚀 Process PDFs", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                success_count = 0
                for i, uploaded_file in enumerate(uploaded_files):
                    try:
                        status_text.text(f"Processing {uploaded_file.name}...")
                        progress_bar.progress((i + 1) / len(uploaded_files))
                        
                        pdf_bytes = uploaded_file.read()
                        result = st.session_state.search_engine.upload_pdf(
                            pdf_bytes, 
                            uploaded_file.name
                        )
                        
                        if result['status'] == 'success':
                            success_count += 1
                        
                        time.sleep(0.5)
                        
                    except Exception as e:
                        st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                
                progress_bar.empty()
                status_text.empty()
                
                if success_count > 0:
                    st.success(f"✅ Successfully processed {success_count} PDF(s)")
                    st.rerun()
        
        st.markdown("---")
        st.markdown("### 💭 Conversation")
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.search_engine.clear_conversation(st.session_state.current_session_id)
            st.session_state.chat_history = []
            st.success("Chat history cleared!")
            time.sleep(1)
            st.rerun()
        
        if st.button("🆕 New Conversation"):
            st.session_state.current_session_id = st.session_state.search_engine.start_conversation()
            st.session_state.chat_history = []
            st.success("Started new conversation!")
            time.sleep(1)
            st.rerun()
    
    st.markdown("## 💬 Ask Questions")
    
    if st.session_state.chat_history:
        st.markdown("### Previous Conversation:")
        for i, (role, message) in enumerate(st.session_state.chat_history[-10:]):
            if role == "user":
                st.markdown(f"**🧑 You:** {message}")
            else:
                st.markdown(f"**🤖 AI:** {message}")
        st.markdown("---")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        question = st.text_input(
            "What would you like to know about your PDFs?",
            placeholder="e.g., What are the main topics discussed?",
            key="question_input"
        )
    
    with col2:
        ask_button = st.button("🔍 Ask", type="primary", key="ask_button")
    
    if ask_button and question:
        if question.strip():
            with st.spinner("🤔 AI is thinking..."):
                try:
                    result = st.session_state.search_engine.ask_question(
                        question,
                        use_memory=True,
                        session_id=st.session_state.current_session_id
                    )
                    
                    st.session_state.chat_history.append(("user", question))
                    st.session_state.chat_history.append(("assistant", result['answer']))
                    
                    st.markdown("### 🤖 Answer:")
                    st.markdown(result['answer'])
                    
                    if result.get('source_documents'):
                        with st.expander(f"📚 Sources ({len(result['source_documents'])} documents)"):
                            for i, doc in enumerate(result['source_documents'][:3]):
                                st.markdown(f"**Source {i+1}:** {doc.get('source_file', 'Unknown')}")
                                st.text(doc.get('content', '')[:200] + "..." if len(doc.get('content', '')) > 200 else doc.get('content', ''))
                                st.markdown("---")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter a question.")
    
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; padding: 1rem;'>"
        "🚀 Powered by OpenAI, LangChain, Pinecone & Supabase"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
