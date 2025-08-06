"""
Message processing handler
"""
from telethon.tl.types import Message
from typing import Dict, Any, List
from src.core.base_classes import BaseMessageHandler
from src.utils.logger import get_logger

logger = get_logger(__name__)

class MessageHandler(BaseMessageHandler):
    """Handle message processing and analysis"""
    
    def __init__(self):
        super().__init__()
    
    async def process_message(self, message: Message, channel_title: str) -> Dict[str, Any] | None:
        """Process a message and extract relevant information"""
        try:
            message_info = self.get_detailed_message_info(message)
            message_type = message_info['message_type']
            
            logger.info(f"Processing message from {channel_title}")
            logger.info(f"Message type: {message_type}")
            logger.info(f"Content: {message.message[:200]}...")
            
            # Extract Solana addresses
            solana_addresses = self.address_extractor.extract_solana_addresses(message.message)
            
            if solana_addresses:
                logger.info(f"Solana addresses found: {solana_addresses}")
                return {
                    'addresses': solana_addresses,
                    'message_info': message_info,
                    'channel_title': channel_title,
                    'message_text': message.message,
                    'message_date': message.date
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return None
    
    def get_detailed_message_info(self, message: Message) -> Dict[str, Any]:
        """Get detailed information about a message"""
        info = {
            'message_type': self.get_message_type(message),
            'has_text': bool(message.message and message.message.strip()),
            'text_length': len(message.message) if message.message else 0,
            'has_media': bool(message.media),
            'has_entities': bool(message.entities),
            'is_post': message.post,
            'is_out': message.out,
            'views': getattr(message, 'views', None),
            'forwards': getattr(message, 'forwards', None),
            'replies': getattr(message, 'replies', None),
        }
        
        if message.media:
            info['media_type'] = type(message.media).__name__
        
        if message.entities:
            entity_types = [type(entity).__name__ for entity in message.entities]
            info['entity_types'] = entity_types
        
        return info
    
    def get_message_type(self, message: Message) -> str:
        """Get the type of a message"""
        has_text = bool(message.message and message.message.strip())
        
        if message.media:
            media_type = type(message.media).__name__
            return media_type.lower().replace('messagemedia', '')
        
        if message.entities:
            entity_types = set()
            for entity in message.entities:
                entity_name = type(entity).__name__
                if "Url" in entity_name:
                    entity_types.add("link")
                elif "Mention" in entity_name:
                    entity_types.add("mention")
                elif "Hashtag" in entity_name:
                    entity_types.add("hashtag")
                elif "BotCommand" in entity_name:
                    entity_types.add("bot_command")
            
            if entity_types:
                return f"text_with_{'_'.join(sorted(entity_types))}"
        
        if has_text:
            return "text"
        
        return "empty" 