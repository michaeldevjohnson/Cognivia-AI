import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "husnain")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "512"))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # RAG Optimization Settings
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
    MAX_DOCUMENTS_PER_QUERY = int(os.getenv("MAX_DOCUMENTS_PER_QUERY", "5"))
    TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))
    
    # Chatbot Settings
    MAX_CHAT_HISTORY = int(os.getenv("MAX_CHAT_HISTORY", "20"))
    ENABLE_SOURCE_DISPLAY = os.getenv("ENABLE_SOURCE_DISPLAY", "true").lower() == "true"

    @classmethod
    def validate(cls):
        required_vars = [
            ("OPENAI_API_KEY", cls.OPENAI_API_KEY),
            ("PINECONE_API_KEY", cls.PINECONE_API_KEY),
            ("PINECONE_INDEX_NAME", cls.PINECONE_INDEX_NAME),
        ]
        
        missing = [name for name, value in required_vars if not value]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}") 