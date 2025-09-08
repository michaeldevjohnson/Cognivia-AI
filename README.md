# 🔍 Cognivia AI

[![Python](https://img.shields.io/badge/language-Python-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-Framework-orange)](https://python.langchain.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-green.svg)](https://openai.com/)
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector%20DB-blue)](https://www.pinecone.io/)
[![Supabase](https://img.shields.io/badge/Supabase-Database-dark)](https://supabase.com/)

Cognivia AI leverages cutting-edge technologies to provide intelligent document analysis and natural language interactions.

**Author:** Muhammad Husnain Ali

## 🛠️ Technologies Used

### Core Technologies
- **[Python](https://www.python.org/)** - Primary programming language
- **[LangChain](https://python.langchain.com/)** - Framework for building LLM applications
- **[OpenAI GPT-3.5](https://openai.com/)** - Large Language Model for text processing
- **[Streamlit](https://streamlit.io/)** - Web application framework

### Data Processing & Storage
- **[Pinecone](https://www.pinecone.io/)** - Vector database for similarity search
- **[Supabase](https://supabase.com/)** - PostgreSQL database for conversation history
- **[PyPDF2](https://pypdf2.readthedocs.io/)** - PDF processing library

### AI/ML Components
- **OpenAI Embeddings** - text-embedding-3-small model (512 dimensions)
- **Vector Search** - Semantic similarity matching
- **Conversation Memory** - Context-aware chat history

### Development Tools
- **Python Virtual Environment** - Dependency isolation
- **Environment Variables** - Secure configuration management
- **SQL** - Database schema management

## 🚀 Features

- **Advanced PDF Processing**
  - Automatic text extraction and semantic chunking
  - Support for multiple PDF uploads
  - Intelligent document metadata preservation
  - OCR support for scanned documents

- **Optimized RAG (Retrieval-Augmented Generation)**
  - **Document-Only Responses**: Strictly answers based on uploaded documents
  - **Existing Document Support**: Automatically detects and works with pre-existing PDFs
  - **Similarity Threshold Filtering**: Configurable relevance scoring
  - **Generic Response Detection**: Prevents hallucination and general knowledge responses
  - **Source Attribution**: Always cites document sources with page numbers
  - **Context Validation**: Ensures answers are grounded in document content

- **AI-Powered Question Answering**
  - Natural language understanding with document constraints
  - Context-aware responses from your PDFs only
  - Multi-document correlation and analysis
  - Intelligent "I don't know" responses when information isn't available

- **Enterprise-Grade Vector Search**
  - High-performance similarity matching with thresholds
  - Scalable document indexing
  - Real-time search capabilities
  - Configurable search parameters and document limits

- **Smart Conversation Management**
  - Persistent chat history with Supabase
  - Context retention across sessions
  - Document-aware conversation flow
  - Multi-user support with session isolation

- **Modern Chatbot Interface**
  - **Chat Bubble Design**: WhatsApp-style message interface
  - **Real-time Conversations**: Instant responses with typing indicators
  - **Source Document Display**: Expandable source citations
  - **Responsive Design**: Mobile-friendly chat experience
  - **Document Status Tracking**: Upload progress and document counts

## 🏗️ Architecture

- **Frontend**: Streamlit web interface
- **LLM**: OpenAI GPT-3.5-turbo for intelligent responses
- **Embeddings**: OpenAI text-embedding-3-small (512 dimensions)
- **Vector Store**: Pinecone for document similarity search
- **Memory**: Supabase PostgreSQL for conversation persistence
- **PDF Processing**: PyPDF2 with intelligent text chunking

## ⚙️ Requirements

- Python 3.8+
- OpenAI API key
- Pinecone account and API key
- Supabase project (for conversation memory)

## 🚀 Quick Setup

### 1. Clone and Setup Virtual Environment

```bash
# Clone the repository
git clone <repository-url>
cd ai-pdf-search-engine

# Create and activate virtual environment
# For Windows
python -m venv venv
.\venv\Scripts\activate

# For macOS/Linux
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file in the project root:

```env
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=your_index_name
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=512
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# RAG Optimization Settings (Optional)
SIMILARITY_THRESHOLD=0.7          # Document relevance threshold (0.0-1.0)
MAX_DOCUMENTS_PER_QUERY=5         # Maximum documents to retrieve
LLM_TEMPERATURE=0                 # Response creativity (0.0-1.0)
MAX_TOKENS=1000                   # Maximum response length

# Chatbot Settings (Optional)
MAX_CHAT_HISTORY=20               # Messages to keep in memory
ENABLE_SOURCE_DISPLAY=true        # Show source documents
```

### 3. Setup Supabase Tables

1. Navigate to your Supabase project dashboard
2. Go to the SQL Editor
3. Open the provided `setup_supabase.sql` file in the project root
4. Execute the SQL commands to:
   - Create chat sessions and messages tables
   - Set up appropriate indexes
   - Enable Row Level Security (RLS)
   - Configure access policies

The SQL file includes all necessary table definitions, indexes, and security policies for the chat system.

### 4. Run Application

```bash
# Option 1: Use the runner script (recommended)
python run_app.py

# Option 2: Run directly with Streamlit
# Make sure your virtual environment is activated
# For Windows
.\venv\Scripts\activate

# For macOS/Linux
source venv/bin/activate

# Run the application
streamlit run app.py
```

### 5. Test the System

Run the test scripts to verify functionality:

```bash
# Test that the system only responds based on documents
python test_optimized_rag.py

# Demo working with existing documents (if any)
python demo_existing_docs.py
```

### 6. Deactivating Virtual Environment

When you're done working on the project, you can deactivate the virtual environment:

```bash
deactivate
```

## 🏗️ Project Structure

```
ai-pdf-search-engine/
├── app.py                 # Streamlit web interface
├── config.py             # Configuration and environment variables
├── pdf_processor.py      # PDF text extraction and chunking
├── vector_store.py       # Pinecone vector database integration
├── qa_system.py          # Question-answering logic
├── pdf_search_engine.py  # Main orchestration class
├── supabase_memory.py    # Conversation memory with Supabase
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── setup_supabase.sql   # Database schema for memory
├── .gitignore          # Git ignore configuration
└── README.md           # This file
```

## 💡 Advanced Configuration

### RAG Optimization

```python
# Fine-tune document retrieval and response quality
SIMILARITY_THRESHOLD = 0.7     # Higher = more strict document relevance
MAX_DOCUMENTS_PER_QUERY = 5    # More documents = better context, slower response
LLM_TEMPERATURE = 0            # 0 = deterministic, 1 = creative responses
MAX_TOKENS = 1000              # Longer responses vs. faster generation
```

### Performance Tuning

```python
# config.py
CHUNK_SIZE = 1000          # Adjust based on document complexity
CHUNK_OVERLAP = 200        # Increase for better context preservation
MAX_CHAT_HISTORY = 20      # Balance memory vs. performance
CACHE_TTL = 3600          # Cache lifetime in seconds
```

### Scaling Considerations

- Recommended Pinecone tier: Standard or Enterprise
- Minimum RAM: 4GB
- Recommended CPU: 4 cores
- Storage: 10GB+ for document cache

## 🔧 Troubleshooting

### Common Issues

1. **PDF Processing Fails**
   - Ensure PDF is not password protected
   - Check file permissions
   - Verify PDF is not corrupted

2. **Vector Store Errors**
   - Confirm Pinecone API key is valid
   - Check index dimensions match configuration
   - Verify network connectivity

3. **Memory Issues**
   - Clear browser cache
   - Restart application
   - Check Supabase connection

4. **Existing Documents Not Found**
   - Verify correct Pinecone index name in .env
   - Check if using different API keys
   - Run `python demo_existing_docs.py` to diagnose
   - Use "Refresh Documents" button in the app

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- OpenAI team for their powerful language models
- Pinecone for vector search capabilities
- Supabase team for the excellent database platform
- LangChain community for the framework
- All contributors and users of this project

## 📞 Support

- 📧 Email: m.husnainali.work@gmail.com
- 📝 Issues: [GitHub Issues](https://github.com/M-Husnain-Ali/AI-PDF-Search-Engine/issues)

---
Made with ❤️ by Muhammad Husnain Ali
