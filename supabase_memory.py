from typing import List, Dict, Any, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain.memory import ConversationBufferMemory
from supabase import create_client, Client
from config import Config
import logging
import json
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class SupabaseChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id: Optional[str] = None):
        if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
            logger.error("Supabase credentials required for conversation memory")
            raise ValueError("Supabase URL and KEY must be configured for conversation memory")
        
        self.session_id = session_id or str(uuid.uuid4())
        self.supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

    @property
    def messages(self) -> List[BaseMessage]:
        try:
            result = self.supabase.table('chat_messages')\
                .select("*")\
                .eq('session_id', self.session_id)\
                .order('created_at')\
                .execute()
            
            messages = []
            for record in result.data:
                if record['message_type'] == 'human':
                    messages.append(HumanMessage(content=record['content']))
                elif record['message_type'] == 'ai':
                    messages.append(AIMessage(content=record['content']))
            
            return messages
            
        except Exception as e:
            logger.error(f"Error loading messages: {e}")
            return []

    def add_message(self, message: BaseMessage) -> None:
        try:
            self._ensure_session_exists()
            
            message_type = 'human' if isinstance(message, HumanMessage) else 'ai'
            
            self.supabase.table('chat_messages').insert({
                'id': str(uuid.uuid4()),
                'session_id': self.session_id,
                'message_type': message_type,
                'content': message.content,
                'created_at': datetime.now().isoformat(),
                'metadata': json.dumps(getattr(message, 'additional_kwargs', {}))
            }).execute()
            
        except Exception as e:
            logger.error(f"Error saving message: {e}")

    def _ensure_session_exists(self):
        try:
            self.supabase.table('chat_sessions').upsert({
                'id': self.session_id,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'metadata': '{}'
            }, on_conflict='id').execute()
        except Exception as e:
            logger.error(f"Error ensuring session exists: {e}")

    def clear(self) -> None:
        try:
            self.supabase.table('chat_messages')\
                .delete()\
                .eq('session_id', self.session_id)\
                .execute()
        except Exception as e:
            logger.error(f"Error clearing messages: {e}")

def create_supabase_memory(session_id: Optional[str] = None) -> ConversationBufferMemory:
    chat_history = SupabaseChatMessageHistory(session_id=session_id)
    chat_history._ensure_session_exists()
    
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        chat_memory=chat_history
    )
    
    return memory, chat_history.session_id

def get_all_sessions() -> List[Dict[str, Any]]:
    try:
        if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
            return []
        
        supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        result = supabase.table('chat_sessions')\
            .select("id, created_at, updated_at")\
            .order('updated_at', desc=True)\
            .limit(20)\
            .execute()
        
        return [
            {
                "session_id": record['id'],
                "created_at": record['created_at'],
                "updated_at": record['updated_at']
            }
            for record in result.data
        ]
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        return []

def clear_session(session_id: str):
    try:
        chat_history = SupabaseChatMessageHistory(session_id=session_id)
        chat_history.clear()
    except Exception as e:
        logger.error(f"Error clearing session: {e}") 