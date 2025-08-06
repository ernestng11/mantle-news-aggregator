"""
Session management for Telegram client
"""
from telethon.sessions import StringSession
from src.core.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)

class SessionManager:
    """Manage Telegram session"""
    
    @staticmethod
    def create_session() -> StringSession:
        """Create a new session using the configured session string"""
        return StringSession(Config.TELEGRAM_SESSION_STR)
    
    @staticmethod
    def get_session_string() -> str:
        """Get the current session string"""
        return Config.TELEGRAM_SESSION_STR
    
    @staticmethod
    def validate_session() -> bool:
        """Validate session string format"""
        session_str = Config.TELEGRAM_SESSION_STR
        if not session_str or len(session_str) < 100:
            return False
        return True 