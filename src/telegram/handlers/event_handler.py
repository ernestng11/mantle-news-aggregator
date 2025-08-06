"""
Event registration and handling
"""
from telethon import events
from telethon.tl.types import Message
from typing import Callable, List, Dict, Any
from src.utils.logger import get_logger

logger = get_logger(__name__)

class EventHandler:
    """Handle event registration and routing"""
    
    def __init__(self, client):
        self.client = client
        self.message_handlers = []
        self.edit_handlers = []
        self.delete_handlers = []
    
    def register_message_handler(self, handler: Callable) -> None:
        """Register a message handler"""
        self.message_handlers.append(handler)
    
    def register_edit_handler(self, handler: Callable) -> None:
        """Register an edit handler"""
        self.edit_handlers.append(handler)
    
    def register_delete_handler(self, handler: Callable) -> None:
        """Register a delete handler"""
        self.delete_handlers.append(handler)
    
    def install_handlers(self, channel_ids: List[int]) -> None:
        """Install all event handlers"""
        if not self.client:
            raise ValueError("Client not initialized")
        
        # Universal message handler
        @self.client.on(events.NewMessage(chats=channel_ids))
        async def universal_message_handler(event):
            """Handle all new messages"""
            print(event)
            message = event.message
            logger.info(f"🔥 INCOMING MESSAGE DETECTED: Channel {message.peer_id.channel_id} - Content: {message.message[:50] if message.message else 'No text'}")
            try:
                channel_id = message.peer_id.channel_id
                logger.info(f"📡 EVENT: New message received from channel ID: {channel_id}")
                logger.info(f"📨 Message content preview: {message.message[:100] if message.message else 'No text'}...")
                
                for handler in self.message_handlers:
                    await handler(message, channel_id)
                    
            except Exception as e:
                logger.error(f"❌ Error in message handler: {e}")
        
        # Edit message handler
        @self.client.on(events.MessageEdited(chats=channel_ids))
        async def edited_message_handler(event):
            """Handle edited messages"""
            message = event.message
            try:
                channel_id = message.peer_id.channel_id
                logger.info(f"✏️ EVENT: Message edited in channel ID: {channel_id}")
                logger.info(f"📝 Edited content: {message.message[:100] if message.message else 'No text'}...")
                
                for handler in self.edit_handlers:
                    await handler(message, channel_id, is_edit=True)
                    
            except Exception as e:
                logger.error(f"❌ Error in edit handler: {e}")
        
        # Delete message handler
        @self.client.on(events.MessageDeleted(chats=channel_ids))
        async def deleted_message_handler(event):
            """Handle deleted messages"""
            try:
                channel_id = event.chat_id
                logger.info(f"🗑️ EVENT: Messages deleted in channel ID: {channel_id}")
                logger.info(f"🗑️ Deleted message IDs: {event.deleted_ids}")
                
                for handler in self.delete_handlers:
                    await handler(event.deleted_ids, channel_id)
                    
            except Exception as e:
                logger.error(f"❌ Error in delete handler: {e}")
        
        logger.info("Event handlers installed successfully") 