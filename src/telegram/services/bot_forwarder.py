"""
Bot forwarding service
"""
import aiohttp
import json
from typing import Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)

class BotForwarder:
    """Forward messages to Telegram bot"""
    
    def __init__(self, bot_token: str, chat_id: str, channel_id: Optional[str] = None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.channel_id = channel_id
        self.bot_url = f"https://api.telegram.org/bot{bot_token}"
        self.enabled = bool(bot_token and (chat_id or channel_id))
        
        if self.enabled:
            targets = []
            if chat_id:
                targets.append(f"personal chat ({chat_id})")
            if channel_id:
                targets.append(f"channel ({channel_id})")
            logger.info(f"Bot forwarder initialized for: {', '.join(targets)}")
        else:
            logger.warning("Bot forwarder disabled - missing BOT_TOKEN and both BOT_CHAT_ID and BOT_CHANNEL_ID")
    
    def _sanitize_text(self, text: str) -> str:
        """Sanitize text to prevent Markdown parsing errors"""
        if not text:
            return text
        
        # Only escape characters that actually cause Markdown parsing issues
        # These are the main culprits for "can't parse entities" errors
        # Note: We don't escape hyphens (-) or dots (.) as they're common in URLs
        # problematic_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '=', '|', '{', '}', '!']
        # sanitized = text
        
        # for char in problematic_chars:
        #     sanitized = sanitized.replace(char, f'\\{char}')
        
        # # Handle common problematic patterns more carefully
        # sanitized = sanitized.replace('**', '\\*\\*')  # Escape double asterisks
        # sanitized = sanitized.replace('__', '\\_\\_')  # Escape double underscores
        
        return text
    
    async def _send_to_chat(self, target_id: str, channel_handle: str, message_text: str) -> bool:
        """Send message to a specific chat/channel"""
        try:
            # Sanitize the message text
            sanitized_message = self._sanitize_text(message_text)
            
            # Format the message with channel handle
            # formatted_message = f"📢 **@{channel_handle}**\n\n{sanitized_message}"
            
            # Prepare the payload
            payload = {
                "chat_id": target_id,
                "text": sanitized_message,
                "parse_mode": "HTML"
            }
            
            # Send via Telegram Bot API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.bot_url}/sendMessage",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        logger.info(f"✅ Message forwarded to {target_id} from {channel_handle}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Failed to forward message to {target_id}: {response.status} - {error_text}")
                        
                        # Fallback: try without parse_mode if Markdown fails
                        if response.status == 400 and "parse entities" in error_text:
                            logger.info(f"🔄 Retrying without Markdown formatting for {target_id}")
                            # Remove parse_mode key for fallback
                            payload.pop("parse_mode", None)
                            payload["text"] = f"📢 @{channel_handle}\n\n{sanitized_message}"
                            
                            async with session.post(
                                f"{self.bot_url}/sendMessage",
                                json=payload,
                                timeout=aiohttp.ClientTimeout(total=10)
                            ) as retry_response:
                                if retry_response.status == 200:
                                    logger.info(f"✅ Message forwarded (fallback) to {target_id} from {channel_handle}")
                                    return True
                                else:
                                    retry_error = await retry_response.text()
                                    logger.error(f"❌ Fallback also failed for {target_id}: {retry_error}")
                        
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Error forwarding message to {target_id}: {e}")
            return False
    
    def _extract_urls_from_entities(self, message) -> list:
        """Extract URLs from Telegram message entities"""
        urls = []
        
        if not hasattr(message, 'entities') or not message.entities:
            return urls
        
        for entity in message.entities:
            if hasattr(entity, 'url') and entity.url:
                urls.append(entity.url)
            elif hasattr(entity, 'text') and entity.text:
                urls.append(entity.text)
        
        return list(set(urls))  # Remove duplicates
    
    def _extract_urls_from_text(self, text: str) -> list:
        """Extract URLs from text using regex (fallback)"""
        import re
        url_pattern = r'https?://[^\s]+'
        return list(set(re.findall(url_pattern, text)))
    
    async def forward_message(self, channel_handle: str, message_text: str, message=None) -> bool:
        """Forward a message to bot (personal chat and/or channel)"""
        if not self.enabled:
            return False
        
        # Extract URLs from message entities if available, otherwise from text
        urls = []
        if message:
            urls = self._extract_urls_from_entities(message)
        
        if not urls:
            urls = self._extract_urls_from_text(message_text)
        
        # Add URLs to message if found
        # if urls:
        #     message_text += f"\n\n🔗 **Links:**\n" + "\n".join([f"• {url}" for url in urls])
        
        success = True
        
        # Send to personal chat if configured
        if self.chat_id:
            success &= await self._send_to_chat(self.chat_id, channel_handle, message_text)
        
        # Send to channel if configured
        if self.channel_id:
            success &= await self._send_to_chat(self.channel_id, channel_handle, message_text)
        
        return success
    
    async def send_test_message(self) -> bool:
        """Send a test message to verify bot configuration"""
        if not self.enabled:
            logger.warning("Bot forwarder is disabled")
            return False
        
        test_message = "🤖 Bot forwarder is working! Messages from monitored channels will be forwarded here."
        return await self.forward_message("TEST", test_message) 