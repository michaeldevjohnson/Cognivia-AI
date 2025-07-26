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
            temperature=0,
            openai_api_key=Config.OPENAI_API_KEY
        )
        
        self.current_memory = None
        self.current_session_id = None
        self.conversational_chain = None

    def ask_question(self, question: str, k: int = 5) -> Dict[str, Any]:
        try:
            retriever = self.vector_store.vector_store.as_retriever(search_kwargs={"k": k})
            
            custom_prompt = PromptTemplate(
                input_variables=["context", "question"],
                template="""Use the following pieces of context to answer the question at the end. 
If you don't know the answer based on the context, just say that you don't know.

{context}

Question: {question}
Answer:"""
            )

            from langchain.chains import RetrievalQA
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": custom_prompt}
            )

            result = qa_chain.invoke({"query": question})
            
            response = {
                "question": question,
                "answer": result["result"],
                "source_documents": []
            }

            for i, doc in enumerate(result.get("source_documents", [])):
                source_info = {
                    "chunk_index": i,
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "source_file": doc.metadata.get("source", "Unknown")
                }
                response["source_documents"].append(source_info)

            logger.info(f"Answered question: '{question[:50]}...'")
            return response

        except Exception as e:
            logger.error(f"Error answering question: {e}")
            raise

    def search_documents(self, query: str, k: int = 5, with_scores: bool = False) -> List[Dict[str, Any]]:
        try:
            documents = self.vector_store.search_documents(query, k=k, with_scores=with_scores)
            
            for doc in documents:
                doc_info = {
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "source_file": doc["source_file"]
                }
                if with_scores and "similarity_score" in doc:
                    doc_info["similarity_score"] = doc["similarity_score"]
                    documents.append(doc_info)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise

    def start_conversation(self, session_id: Optional[str] = None) -> str:
        self.current_memory, actual_session_id = create_supabase_memory(session_id)
        self.current_session_id = actual_session_id
        
        retriever = self.vector_store.vector_store.as_retriever()
        retriever.search_kwargs = {"k": 5}
        
        self.conversational_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            return_source_documents=True,
            verbose=True
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
            
            from langchain_core.messages import HumanMessage, AIMessage
            self.current_memory.chat_memory.add_message(HumanMessage(content=question))
            self.current_memory.chat_memory.add_message(AIMessage(content=result["answer"]))
            
            response = {
                "question": question,
                "answer": result["answer"],
                "session_id": self.current_session_id,
                "source_documents": []
            }
            
            for i, doc in enumerate(result.get("source_documents", [])):
                source_info = {
                    "chunk_index": i,
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "source_file": doc.metadata.get("source", "Unknown")
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