import streamlit as st
from pathlib import Path
from io import BytesIO
import time
import uuid

from pdf_search_engine import PDFSearchEngine
from config import Config

st.set_page_config(
    page_title="Cognivia AI",
    page_icon="🤖",
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

def render_chat_message(role: str, message: str, avatar: str = None):
    """Render a chat message with premium styling"""
    if role == "user":
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end; margin: 1.5rem 0; animation: slideInRight 0.3s ease-out;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 1rem 1.5rem; border-radius: 25px 25px 8px 25px; 
                        max-width: 75%; box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
                        backdrop-filter: blur(10px); position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; 
                           background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
                           pointer-events: none;"></div>
                <div style="position: relative; z-index: 1;">
                    <div style="font-weight: 600; margin-bottom: 0.5rem; font-size: 0.85rem; 
                               opacity: 0.9; display: flex; align-items: center;">
                        <span style="margin-right: 0.5rem;">👤</span>You
                    </div>
                    <div style="line-height: 1.5; font-size: 1rem;">{message}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-start; margin: 1.5rem 0; animation: slideInLeft 0.3s ease-out;">
            <div style="background: rgba(255, 255, 255, 0.95); border: 1px solid rgba(0,0,0,0.05);
                        color: #2c3e50; padding: 1rem 1.5rem; border-radius: 25px 25px 25px 8px; 
                        max-width: 75%; box-shadow: 0 8px 32px rgba(0,0,0,0.08);
                        backdrop-filter: blur(20px); position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; 
                           background: linear-gradient(45deg, rgba(102, 126, 234, 0.02) 0%, rgba(118, 75, 162, 0.02) 100%);
                           pointer-events: none;"></div>
                <div style="position: relative; z-index: 1;">
                    <div style="font-weight: 600; margin-bottom: 0.5rem; font-size: 0.85rem; 
                               color: #667eea; display: flex; align-items: center;">
                        <span style="margin-right: 0.5rem;">🤖</span>AI Assistant
                    </div>
                    <div style="line-height: 1.6; font-size: 1rem; color: #2c3e50;">{message}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_loading_message():
    """Render a ChatGPT-style loading message"""
    st.markdown("""
    <div style="display: flex; justify-content: flex-start; margin: 1.5rem 0; animation: slideInLeft 0.3s ease-out;">
        <div style="background: rgba(255, 255, 255, 0.95); border: 1px solid rgba(0,0,0,0.05);
                    color: #2c3e50; padding: 1rem 1.5rem; border-radius: 25px 25px 25px 8px; 
                    max-width: 75%; box-shadow: 0 8px 32px rgba(0,0,0,0.08);
                    backdrop-filter: blur(20px); position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; 
                       background: linear-gradient(45deg, rgba(102, 126, 234, 0.02) 0%, rgba(118, 75, 162, 0.02) 100%);
                       pointer-events: none;"></div>
            <div style="position: relative; z-index: 1;">
                <div style="font-weight: 600; margin-bottom: 0.5rem; font-size: 0.85rem; 
                           color: #667eea; display: flex; align-items: center;">
                    <span style="margin-right: 0.5rem;">🤖</span>AI Assistant
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div class="typing-indicator">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                    <span style="color: #6b7280; font-size: 0.9rem;">Analyzing your documents...</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    # ChatGPT-style CSS
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles - ChatGPT-like */
    .stApp {
        background: #f7f7f8;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header {visibility: hidden;}
    
         /* Remove default Streamlit containers */
     .main .block-container {
         padding-top: 1rem;
         padding-bottom: 1rem;
         max-width: 100%;
         padding-left: 1rem;
         padding-right: 1rem;
     }
     
     /* Main content area */
     .main-content {
         max-width: 800px;
         margin: 0 auto;
         padding: 0 1rem;
     }
    
    /* Premium Header */
    .premium-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(20px);
    }
    
    .premium-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        pointer-events: none;
    }
    
    .premium-header h1 {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 4px 20px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }
    
    .premium-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        margin: 1rem 0 0 0;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    
         /* Animations */
     @keyframes slideInRight {
         from { opacity: 0; transform: translateX(30px); }
         to { opacity: 1; transform: translateX(0); }
     }
     
     @keyframes slideInLeft {
         from { opacity: 0; transform: translateX(-30px); }
         to { opacity: 1; transform: translateX(0); }
     }
     
     @keyframes fadeInUp {
         from { opacity: 0; transform: translateY(20px); }
         to { opacity: 1; transform: translateY(0); }
     }
     
     @keyframes typing {
         0%, 60%, 100% { 
             transform: translateY(0); 
             opacity: 0.4; 
         }
         30% { 
             transform: translateY(-10px); 
             opacity: 1; 
         }
     }
     
     /* Typing Indicator */
     .typing-indicator {
         display: flex;
         gap: 4px;
         align-items: center;
     }
     
     .typing-dot {
         width: 8px;
         height: 8px;
         border-radius: 50%;
         background: #10b981;
         animation: typing 1.4s infinite ease-in-out;
     }
     
     .typing-dot:nth-child(1) { animation-delay: 0s; }
     .typing-dot:nth-child(2) { animation-delay: 0.2s; }
     .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    
         /* ChatGPT-style Input */
     .stTextInput > div > div > input {
         border-radius: 12px !important;
         border: 1px solid #d1d5db !important;
         padding: 1rem 1rem 1rem 1rem !important;
         font-size: 1rem !important;
         background: white !important;
         transition: all 0.2s ease !important;
         box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
         width: 100% !important;
     }
     
     .stTextInput > div > div > input:focus {
         border-color: #10b981 !important;
         box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1) !important;
         outline: none !important;
     }
    
         /* ChatGPT-style Send Button */
     .stButton > button {
         border-radius: 8px !important;
         height: 3rem !important;
         font-weight: 500 !important;
         background: #10b981 !important;
         border: none !important;
         color: white !important;
         transition: all 0.2s ease !important;
         font-size: 0.9rem !important;
         min-width: 80px !important;
     }
     
     .stButton > button:hover {
         background: #059669 !important;
         transform: none !important;
     }
     
     .stButton > button:disabled {
         background: #d1d5db !important;
         color: #9ca3af !important;
     }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(0,0,0,0.1) !important;
    }
    
    /* Upload Section */
    .upload-section {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        padding: 2rem;
        border-radius: 20px;
        border: 2px dashed rgba(102, 126, 234, 0.3);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .upload-section:hover {
        border-color: #667eea;
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.15);
    }
    
    /* Stats Card */
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }
    
    .stats-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        pointer-events: none;
    }
    
    .stats-card h3, .stats-card p {
        position: relative;
        z-index: 1;
    }
    
    /* Warning Card */
    .warning-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        color: #8b4513;
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(252, 182, 159, 0.3);
        backdrop-filter: blur(10px);
    }
    
         /* Welcome Message - ChatGPT style */
     .welcome-message {
         text-align: center;
         color: #374151;
         padding: 4rem 2rem;
         animation: fadeInUp 0.6s ease-out;
         background: transparent;
         max-width: 800px;
         margin: 0 auto;
     }
     
     .welcome-message h3 {
         font-size: 2rem;
         font-weight: 600;
         margin-bottom: 1rem;
         color: #374151;
     }
    
         /* Chat Input Container - ChatGPT style */
     .chat-input-container {
         position: fixed;
         bottom: 0;
         left: 0;
         right: 0;
         background: #f7f7f8;
         padding: 1rem 2rem 2rem 2rem;
         border-top: 1px solid #e5e7eb;
         z-index: 1000;
     }
     
     .chat-input-wrapper {
         max-width: 800px;
         margin: 0 auto;
         position: relative;
     }
    
    /* File Uploader */
    .stFileUploader > div > div {
        border-radius: 15px !important;
        border: 2px dashed rgba(102, 126, 234, 0.3) !important;
        background: rgba(255, 255, 255, 0.5) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.8) !important;
        border-radius: 15px !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 10px !important;
    }
    
    /* Source Documents */
    .source-doc {
        background: rgba(255, 255, 255, 0.9);
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        backdrop-filter: blur(10px);
    }
    
    /* Scrollbar */
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.05);
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Premium Header
    st.markdown("""
    <div class="premium-header">
        <h1>🤖 Cognivia AI</h1>
        <p>Experience next-generation document intelligence with premium AI technology</p>
    </div>
    """, unsafe_allow_html=True)
    
    search_engine, error = initialize_search_engine()
    
    if error:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%); 
                    color: white; padding: 2rem; border-radius: 20px; text-align: center;
                    box-shadow: 0 10px 30px rgba(238, 90, 82, 0.3);">
            <h3>⚠️ Configuration Error</h3>
            <p>{error}</p>
        </div>
        """, unsafe_allow_html=True)
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
    
    # Initialize session state
    if 'search_engine' not in st.session_state:
        st.session_state.search_engine = search_engine
    
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = st.session_state.search_engine.start_conversation()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Check for existing documents in vector store
    if 'existing_docs_checked' not in st.session_state:
        existing_docs = st.session_state.search_engine.check_existing_documents()
        st.session_state.existing_docs = existing_docs
        st.session_state.documents_uploaded = existing_docs.get('document_count', 0)
        st.session_state.existing_docs_checked = True
    
    # Premium Sidebar
    with st.sidebar:
        st.markdown("### 📁 Document Management")
        
        # Premium upload section
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.markdown("**✨ Upload Premium PDFs**")
        
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            accept_multiple_files=True,
            type="pdf",
            help="Upload one or more PDF files to chat with",
            label_visibility="collapsed"
        )
        
        if uploaded_files:
            if st.button("🚀 Process PDFs", type="primary", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                success_count = 0
                for i, uploaded_file in enumerate(uploaded_files):
                    try:
                        status_text.markdown(f"**Processing:** {uploaded_file.name}")
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
                    st.session_state.documents_uploaded += success_count
                    st.success(f"✅ Successfully processed {success_count} PDF(s)")
                    time.sleep(1)
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Premium document stats
        existing_docs = st.session_state.get('existing_docs', {})
        has_existing = existing_docs.get('has_documents', False)
        total_docs = st.session_state.documents_uploaded
        
        if has_existing or total_docs > 0:
            st.markdown(f"""
            <div class="stats-card">
                <h3 style="margin: 0;">📊 Knowledge Base</h3>
                <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; font-weight: 600;">
                    {total_docs} Document(s) Ready
                </p>
                <p style="margin: 0.25rem 0 0 0; font-size: 0.9rem; opacity: 0.9;">
                    {existing_docs.get('total_vectors', 0):,} AI-processed chunks
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show existing document sources
            if existing_docs.get('document_sources'):
                with st.expander("📄 Available Documents", expanded=False):
                    for i, source in enumerate(existing_docs['document_sources'][:10], 1):
                        st.markdown(f"**{i}.** 📄 {source}")
                    if len(existing_docs['document_sources']) > 10:
                        st.markdown(f"*... and {len(existing_docs['document_sources']) - 10} more documents*")
        
        # Show helpful message if no documents
        elif not has_existing and total_docs == 0:
            st.markdown("""
            <div class="warning-card">
                <h4 style="margin: 0;">📁 No Documents Found</h4>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.95rem;">
                    Upload PDFs above to unlock AI-powered document intelligence
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Premium conversation controls
        st.markdown("### 💭 Conversation Controls")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.search_engine.clear_conversation(st.session_state.current_session_id)
                st.session_state.chat_history = []
                st.success("✨ Chat cleared!")
                time.sleep(0.5)
                st.rerun()
        
        with col2:
            if st.button("🆕 New Chat", use_container_width=True):
                st.session_state.current_session_id = st.session_state.search_engine.start_conversation()
                st.session_state.chat_history = []
                st.success("🎉 New chat started!")
                time.sleep(0.5)
                st.rerun()
        
        # Refresh documents button
        if st.button("🔄 Refresh Docs", use_container_width=True, help="Scan for new documents in database"):
            existing_docs = st.session_state.search_engine.check_existing_documents()
            st.session_state.existing_docs = existing_docs
            old_count = st.session_state.documents_uploaded
            new_count = existing_docs.get('document_count', 0)
            st.session_state.documents_uploaded = new_count
            
            if new_count > old_count:
                st.success(f"🎉 Found {new_count - old_count} new document(s)!")
            elif new_count == old_count:
                st.info("✅ All documents up to date")
            else:
                st.info(f"📊 {new_count} documents available")
            
            time.sleep(1)
            st.rerun()
    
    # Main content wrapper
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # Check if documents are available
    existing_docs = st.session_state.get('existing_docs', {})
    has_any_docs = existing_docs.get('has_documents', False) or st.session_state.documents_uploaded > 0
    
    if not has_any_docs:
        st.markdown("""
        <div class="warning-card">
            <h3>👆 Ready to Get Started?</h3>
            <p>Upload some PDF documents in the sidebar to begin your AI-powered document conversation!</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # ChatGPT-style chat area
    if not st.session_state.chat_history and not st.session_state.get('is_loading', False):
        existing_docs = st.session_state.get('existing_docs', {})
        doc_count = existing_docs.get('document_count', 0)
        
        if doc_count > 0:
            welcome_msg = f"""
            <div class="welcome-message">
                <h3>👋 How can I help you today?</h3>
                <p>I have access to <strong>{doc_count} document(s)</strong> in your knowledge base.</p>
                <p>Ask me anything about your documents.</p>
            </div>
            """
        else:
            welcome_msg = """
            <div class="welcome-message">
                <h3>👋 How can I help you today?</h3>
                <p>Ask me anything about your uploaded documents.</p>
            </div>
            """
        
        st.markdown(welcome_msg, unsafe_allow_html=True)
    elif st.session_state.chat_history and not st.session_state.get('is_loading', False):
        # Display chat history with ChatGPT styling (only when not loading)
        recent_history = st.session_state.chat_history[-Config.MAX_CHAT_HISTORY:]
        for role, message in recent_history:
            render_chat_message(role, message)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add bottom padding for fixed input
    st.markdown('<div style="height: 120px;"></div>', unsafe_allow_html=True)
    
    # ChatGPT-style chat input
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    st.markdown('<div class="chat-input-wrapper">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([6, 1])
    
    with col1:
        question = st.text_input(
            "Message AI PDF Assistant...",
            placeholder="Ask me anything about your documents...",
            key=f"question_input_{len(st.session_state.chat_history)}",
            label_visibility="collapsed",
            value=""
        )
    
    with col2:
        is_loading = st.session_state.get('is_loading', False)
        send_button = st.button(
            "..." if is_loading else "Send", 
            type="primary", 
            use_container_width=True,
            disabled=is_loading
        )
    
    # Handle question submission
    if send_button and question and question.strip() and not st.session_state.get('is_loading', False):
        # Add user message to chat
        st.session_state.chat_history.append(("user", question))
        
        # Add loading state
        st.session_state.is_loading = True
        st.rerun()
    
    # Handle loading state and API call
    if st.session_state.get('is_loading', False):
        # Display chat history with loading indicator
        recent_history = st.session_state.chat_history[-Config.MAX_CHAT_HISTORY:]
        for role, message in recent_history:
            render_chat_message(role, message)
        
        # Show loading message
        render_loading_message()
        
        # Process the question
        try:
            # Add a small delay to show loading animation
            import time
            time.sleep(0.5)
            
            last_user_message = st.session_state.chat_history[-1][1]  # Get last user message
            result = st.session_state.search_engine.ask_question(
                last_user_message,
                use_memory=True,
                session_id=st.session_state.current_session_id
            )
            
            # Add AI response to chat
            st.session_state.chat_history.append(("assistant", result['answer']))
            
            # Store source documents for the last response
            st.session_state.last_sources = result.get('source_documents', [])
            
            # Clear loading state
            st.session_state.is_loading = False
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.session_state.is_loading = False
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Premium source documents display
    if st.session_state.get('last_sources') and st.session_state.chat_history:
        st.markdown("---")
        st.markdown("**📚 Source Documents:**")
        for i, doc in enumerate(st.session_state.last_sources[:3], 1):
            content = doc.get('content', '')
            preview = content[:300] + "..." if len(content) > 300 else content
            st.markdown(f"""
            <div class="source-doc">
                <strong>📄 Source {i}:</strong> {doc.get('source_file', 'Unknown')} - Page {doc.get('page', 'N/A')}
                <div style="margin-top: 0.5rem; font-family: monospace; background: rgba(0,0,0,0.05); 
                           padding: 1rem; border-radius: 10px; font-size: 0.9rem;">
                    {preview}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Premium Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 2rem; 
                    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
                    border-radius: 15px; backdrop-filter: blur(10px);'>
            <strong>🚀 Powered by Premium AI Technology</strong><br>
            OpenAI GPT • LangChain • Pinecone Vector DB • Supabase<br>
            <em>Built with ❤️ for next-generation document intelligence</em>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
