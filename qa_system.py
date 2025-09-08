from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from vector_store import VectorStore
from supabase_memory import create_supabase_memory, get_all_sessions, clear_session, SupabaseChatMessageHistory
from config import Config
import logging

logger = logging.getLogger(__name__)

class QASystem:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS,
            openai_api_key=Config.OPENAI_API_KEY
        )
        
        self.current_memory = None
        self.current_session_id = None
        self.conversational_chain = None
        
        # RAG optimization settings from config
        self.similarity_threshold = Config.SIMILARITY_THRESHOLD
        self.max_documents = Config.MAX_DOCUMENTS_PER_QUERY

    def _create_strict_prompt(self) -> PromptTemplate:
        """Create a strict prompt that ensures document-based responses only"""
        return PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a helpful AI assistant that answers questions STRICTLY based on the provided document context. 

IMPORTANT RULES:
1. ONLY use information from the provided context below
2. If the context doesn't contain enough information to answer the question, respond with: "I don't have enough information in the provided documents to answer this question."
3. Do NOT use any external knowledge or general information
4. Always cite which document(s) your answer comes from
5. Be specific and accurate based on the document content
6. If asked about topics not covered in the documents, clearly state that the information is not available in the provided documents

CONTEXT FROM DOCUMENTS:
{context}

QUESTION: {question}

ANSWER (based only on the provided context):"""
        )

    def _create_conversational_prompt(self) -> PromptTemplate:
        """Create a conversational prompt for chat-based interactions"""
        return PromptTemplate(
            input_variables=["context", "question", "chat_history"],
            template="""You are a helpful AI assistant that maintains conversations about documents. Answer questions STRICTLY based on the provided document context.

IMPORTANT RULES:
1. ONLY use information from the provided document context
2. Consider the conversation history for context, but still answer based on documents only
3. If the documents don't contain the information, say: "I don't have that information in the provided documents."
4. Maintain a friendly, conversational tone while staying factual
5. Reference previous parts of the conversation when relevant
6. Always ground your answers in the document content

CONVERSATION HISTORY:
{chat_history}

DOCUMENT CONTEXT:
{context}

CURRENT QUESTION: {question}

ANSWER (based only on document context):"""
        )

    def _filter_relevant_documents(self, documents: List[Document], query: str) -> List[Document]:
        """Filter documents based on relevance and similarity scores"""
        if not documents:
            return []
        
        # Get similarity scores for filtering
        try:
            scored_docs = self.vector_store.vector_store.similarity_search_with_score(query, k=len(documents))
            relevant_docs = []
            
            for doc, score in scored_docs:
                # Lower scores indicate higher similarity in most vector stores
                if score <= (1.0 - self.similarity_threshold):
                    relevant_docs.append(doc)
                    
            return relevant_docs if relevant_docs else documents[:3]  # Fallback to top 3
            
        except Exception as e:
            logger.warning(f"Could not filter by similarity score: {e}")
            return documents[:5]  # Return top 5 as fallback

    def ask_question(self, question: str, k: int = None) -> Dict[str, Any]:
        try:
            if k is None:
                k = self.max_documents
            retriever = self.vector_store.vector_store.as_retriever(search_kwargs={"k": k})
            
            # Get documents and filter for relevance
            retrieved_docs = retriever.get_relevant_documents(question)
            relevant_docs = self._filter_relevant_documents(retrieved_docs, question)
            
            if not relevant_docs:
                return {
                    "question": question,
                    "answer": "I don't have enough relevant information in the provided documents to answer this question.",
                    "source_documents": []
                }
            
            custom_prompt = self._create_strict_prompt()

            from langchain.chains import RetrievalQA
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": custom_prompt}
            )

            result = qa_chain.invoke({"query": question})
            
            # Validate that the response is document-based
            answer = result["result"]
            if self._is_generic_response(answer):
                answer = "I don't have specific information about this in the provided documents. Please ask about content that's covered in your uploaded PDFs."
            
            response = {
                "question": question,
                "answer": answer,
                "source_documents": []
            }

            for i, doc in enumerate(result.get("source_documents", [])):
                source_info = {
                    "chunk_index": i,
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "source_file": doc.metadata.get("source", "Unknown"),
                    "page": doc.metadata.get("page", "Unknown")
                }
                response["source_documents"].append(source_info)

            logger.info(f"Answered question: '{question[:50]}...'")
            return response

        except Exception as e:
            logger.error(f"Error answering question: {e}")
            raise

    def _is_generic_response(self, answer: str) -> bool:
        """Check if response seems too generic or not document-based"""
        generic_indicators = [
            "in general", "typically", "usually", "commonly", 
            "it's important to", "you should", "it's recommended",
            "generally speaking", "as a rule"
        ]
        answer_lower = answer.lower()
        return any(indicator in answer_lower for indicator in generic_indicators)

    def search_documents(self, query: str, k: int = 5, with_scores: bool = False) -> List[Dict[str, Any]]:
        try:
            documents = self.vector_store.search_documents(query, k=k, with_scores=with_scores)
            
            result_docs = []
            for doc in documents:
                doc_info = {
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "source_file": doc["source_file"]
                }
                if with_scores and "similarity_score" in doc:
                    doc_info["similarity_score"] = doc["similarity_score"]
                result_docs.append(doc_info)
            
            return result_docs
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise

    def start_conversation(self, session_id: Optional[str] = None) -> str:
        self.current_memory, actual_session_id = create_supabase_memory(session_id)
        self.current_session_id = actual_session_id
        
        retriever = self.vector_store.vector_store.as_retriever()
        retriever.search_kwargs = {"k": self.max_documents}
        
        # Create conversational chain with custom prompt
        custom_prompt = self._create_conversational_prompt()
        
        self.conversational_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            return_source_documents=True,
            verbose=True,
            combine_docs_chain_kwargs={"prompt": custom_prompt}
        )
        
        return self.current_session_id

    def ask_conversational_question(self, question: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        if not self.conversational_chain or (session_id and self.current_session_id != session_id):
            self.start_conversation(session_id)
        
        try:
            chat_history = self.current_memory.chat_memory.messages
            formatted_history = []
            
            for msg in chat_history:
                if hasattr(msg, 'content'):
                    msg_type = 'Human' if msg.__class__.__name__ == 'HumanMessage' else 'Assistant'
                    formatted_history.append((msg_type, msg.content))
            
            inputs = {
                "question": question,
                "chat_history": formatted_history
            }
            
            result = self.conversational_chain.invoke(inputs)
            
            # Validate response is document-based
            answer = result["answer"]
            if self._is_generic_response(answer):
                answer = "I don't have specific information about this in the provided documents. Please ask about content that's covered in your uploaded PDFs."
            
            from langchain_core.messages import HumanMessage, AIMessage
            self.current_memory.chat_memory.add_message(HumanMessage(content=question))
            self.current_memory.chat_memory.add_message(AIMessage(content=answer))
            
            response = {
                "question": question,
                "answer": answer,
                "session_id": self.current_session_id,
                "source_documents": []
            }
            
            for i, doc in enumerate(result.get("source_documents", [])):
                source_info = {
                    "chunk_index": i,
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "source_file": doc.metadata.get("source", "Unknown"),
                    "page": doc.metadata.get("page", "Unknown")
                }
                response["source_documents"].append(source_info)
            
            logger.info(f"Answered conversational question: '{question[:50]}...'")
            return response
            
        except Exception as e:
            logger.error(f"Error in conversational question: {e}")
            raise

    def get_conversation_history(self, session_id: Optional[str] = None) -> List[Dict[str, str]]:
        try:
            if session_id:
                chat_history = SupabaseChatMessageHistory(session_id=session_id)
                messages = chat_history.messages
            elif self.current_memory:
                messages = self.current_memory.chat_memory.messages
            else:
                return []
            
            history = []
            for msg in messages:
                if hasattr(msg, 'content'):
                    msg_type = 'human' if msg.__class__.__name__ == 'HumanMessage' else 'ai'
                    history.append({
                        "type": msg_type,
                        "content": msg.content
                    })
            
            return history
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []

    def clear_conversation(self, session_id: Optional[str] = None):
        if session_id:
            clear_session(session_id)
        elif self.current_session_id:
            clear_session(self.current_session_id)

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        return get_all_sessions() 