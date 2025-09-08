from typing import List, Dict, Any, Optional
import logging

from pdf_processor import PDFProcessor
from vector_store import VectorStore
from qa_system import QASystem
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class PDFSearchEngine:
    def __init__(self):
        logger.info("Initializing PDF Search Engine...")
        
        self.pdf_processor = PDFProcessor()
        self.vector_store = VectorStore()
        self.qa_system = QASystem(self.vector_store)
        
        logger.info("PDF Search Engine initialized successfully!")

    def upload_pdf(self, pdf_content: bytes, filename: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            documents = self.pdf_processor.process_pdf(pdf_content, filename)
            
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)

            result = self.vector_store.add_documents(documents)
            
            logger.info(f"Successfully processed {filename}: {len(documents)} chunks created")
            return result

        except Exception as e:
            error_msg = f"Error processing {filename}: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}

    def upload_multiple_pdfs(self, pdf_files: List[tuple]) -> Dict[str, Any]:
        results = []
        total_success = 0
        total_failed = 0

        for pdf_content, filename in pdf_files:
            try:
                result = self.upload_pdf(pdf_content, filename)
                if result["status"] == "success":
                    total_success += 1
                else:
                    total_failed += 1
                results.append({"filename": filename, "result": result})
                
            except Exception as e:
                total_failed += 1
                results.append({
                    "filename": filename,
                    "result": {"status": "error", "message": str(e)}
                })

        return {
            "status": "completed",
            "total_processed": len(pdf_files),
            "successful": total_success,
            "failed": total_failed,
            "detailed_results": results
        }

    def ask_question(self, question: str, k: int = 5, use_memory: bool = False, session_id: Optional[str] = None) -> Dict[str, Any]:
        try:
            if use_memory:
                return self.qa_system.ask_conversational_question(question, session_id)
            else:
                return self.qa_system.ask_question(question, k)
                
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            raise

    def search_documents(self, query: str, k: int = 5, with_scores: bool = False) -> List[Dict[str, Any]]:
        return self.qa_system.search_documents(query, k, with_scores)

    def get_stats(self) -> Dict[str, Any]:
        return self.vector_store.get_stats()

    def check_existing_documents(self) -> Dict[str, Any]:
        """Check for existing documents in the vector store"""
        try:
            stats = self.get_stats()
            sources = self.vector_store.get_document_sources()
            
            return {
                "has_documents": stats.get("has_documents", False),
                "total_vectors": stats.get("total_vectors", 0),
                "document_sources": sources,
                "document_count": len(sources)
            }
        except Exception as e:
            logger.error(f"Error checking existing documents: {e}")
            return {
                "has_documents": False,
                "total_vectors": 0,
                "document_sources": [],
                "document_count": 0
            }

    def clear_all_documents(self):
        self.vector_store.delete_documents()
        logger.info("All documents cleared from vector store")

    def start_conversation(self, session_id: Optional[str] = None) -> str:
        return self.qa_system.start_conversation(session_id)

    def get_conversation_history(self, session_id: Optional[str] = None) -> List[Dict[str, str]]:
        return self.qa_system.get_conversation_history(session_id)

    def clear_conversation(self, session_id: Optional[str] = None):
        self.qa_system.clear_conversation(session_id)

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        return self.qa_system.get_all_sessions() 