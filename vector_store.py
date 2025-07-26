from typing import List, Dict, Any, Optional
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from pinecone import Pinecone, ServerlessSpec
from config import Config
import logging
import time

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        self.pc = Pinecone(api_key=Config.PINECONE_API_KEY)
        self.index_name = Config.PINECONE_INDEX_NAME
        self.embeddings = OpenAIEmbeddings(
            model=Config.EMBEDDING_MODEL,
            dimensions=Config.EMBEDDING_DIMENSION
        )
        self.vector_store = self._initialize_vector_store()

    def _initialize_vector_store(self):
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=Config.EMBEDDING_DIMENSION,
                metric='cosine',
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )
            time.sleep(1)

        logger.info(f"Connected to Pinecone index: {self.index_name}")
        return PineconeVectorStore.from_existing_index(
            index_name=self.index_name,
            embedding=self.embeddings
        )

    def add_documents(self, documents: List[Document]) -> Dict[str, Any]:
        try:
            if not documents:
                return {"status": "error", "message": "No documents provided"}

            self.vector_store.add_documents(documents)
            
            logger.info(f"Added {len(documents)} documents to vector store")
            return {
                "status": "success",
                "documents_added": len(documents),
                "message": f"Successfully added {len(documents)} document chunks"
            }
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            return {"status": "error", "message": str(e)}

    def search_documents(self, query: str, k: int = 5, with_scores: bool = False) -> List[Dict[str, Any]]:
        try:
            if with_scores:
                results = self.vector_store.similarity_search_with_score(query, k=k)
                documents = []
                for doc, score in results:
                    documents.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "source_file": doc.metadata.get("source", "Unknown"),
                        "similarity_score": float(score)
                    })
                return documents
            else:
                docs = self.vector_store.similarity_search(query, k=k)
                return [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "source_file": doc.metadata.get("source", "Unknown")
                    }
                    for doc in docs
                ]
                
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise

    def delete_documents(self, source_filename: Optional[str] = None):
        try:
            index = self.pc.Index(self.index_name)
            if source_filename:
                index.delete(filter={"source": source_filename})
                logger.info(f"Deleted documents for source: {source_filename}")
            else:
                index.delete(delete_all=True)
                logger.info("Deleted all documents from vector store")
                
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        try:
            index = self.pc.Index(self.index_name)
            stats = index.describe_index_stats()
            return {
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"total_vectors": 0, "dimension": 0, "index_fullness": 0.0} 