"""
Main channel monitoring service
"""
import asyncio
from typing import Dict, Any, Optional
from telethon.tl.functions.updates import GetStateRequest
from src.telegram.client.telegram_client import TelegramClientWrapper
from src.telegram.handlers.message_handler import MessageHandler
from src.telegram.handlers.event_handler import EventHandler
from src.telegram.handlers.gap_handler import GapHandler
from src.telegram.services.bot_forwarder import BotForwarder
from src.telegram.services.llm_processor import process_batch_with_llm
from src.core.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ChannelMonitor:
    """Main channel monitoring service"""
    
    def __init__(self):
        self.telegram_client = TelegramClientWrapper()
        self.message_handler = MessageHandler()
        self.event_handler = None
        self.gap_handler = None
        self.bot_forwarder = BotForwarder(Config.BOT_TOKEN, Config.BOT_CHAT_ID, Config.BOT_CHANNEL_ID)
        self.background_tasks = []
        
        # Message batching
        self.message_batch = []
        self.batch_lock = asyncio.Lock()
        self.last_batch_time = asyncio.get_event_loop().time()
        self.batch_interval = Config.BATCH_INTERVAL
    
    async def initialize(self) -> None:
        """Initialize the channel monitor"""
        try:
            await self.telegram_client.connect()
            self.event_handler = EventHandler(self.telegram_client.get_client())
            self.gap_handler = GapHandler(
                self.telegram_client.get_client(),
                self.telegram_client.get_target_channels()
            )
            # Set up message processor for gap handler
            self.gap_handler.set_message_processor(self.process_message)
            logger.info("Channel monitor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize channel monitor: {e}")
            raise

    async def add_channels(self, channels: list) -> None:
        """Add channels to monitor"""
        for channel in channels:
            try:
                await self.telegram_client.add_target_channel(channel)
                logger.info(f"Added channel: {channel}")
            except Exception as e:
                logger.error(f"Failed to add channel {channel}: {e}")

    def _extract_urls_from_message(self, message) -> list:
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

    async def process_message(self, message, channel_title: str, is_edit: bool = False) -> None:
        """Process incoming message: add to batch for later forwarding"""
        try:
            message_text = getattr(message, 'message', str(message))
            print(f"[Channel: {channel_title}] {message_text}")
            
            # Get channel handle from target channels
            channel_id = message.peer_id.channel_id
            target_channels = self.telegram_client.get_target_channels()
            channel_data = target_channels.get(channel_id, {})
            channel_handle = channel_data.get('handle', channel_title)
            
            # Extract URLs from message
            urls = self._extract_urls_from_message(message)
            
            # Add message to batch with URLs
            async with self.batch_lock:
                self.message_batch.append({
                    'channel_handle': channel_handle,
                    'message_text': message_text,
                    'urls': urls,
                    'timestamp': asyncio.get_event_loop().time()
                })
            
            logger.info(f"📦 Added message to batch from {channel_handle} (batch size: {len(self.message_batch)}, URLs: {len(urls)})")
            
        except Exception as e:
            logger.error(f"❌ Error processing message in channel monitor: {e}")
    
    async def send_batch(self) -> None:
        """Send all collected messages as a batch"""
        async with self.batch_lock:
            if not self.message_batch:
                return
            
            batch_messages = self.message_batch.copy()
            self.message_batch.clear()
            self.last_batch_time = asyncio.get_event_loop().time()
        
        if not batch_messages:
            return
        
        logger.info(f"📤 Sending batch of {len(batch_messages)} messages")
        
        # Combine all messages into one batch
        combined_text = f"**Batched {len(batch_messages)} messages:**\n\n"
        
        # Collect all URLs
        all_urls = []
        
        for i, msg in enumerate(batch_messages, 1):
            channel_handle = msg['channel_handle']
            message_text = msg['message_text']
            urls = msg.get('urls', [])
            
            combined_text += f"{i}. @{channel_handle}: {message_text}\n\n"
            all_urls.extend(urls)
        
        # Add URLs section if any URLs were found
        if all_urls:
            unique_urls = list(set(all_urls))  # Remove duplicates
            combined_text += f"🔗 **Links ({len(unique_urls)}):**\n"
            for url in unique_urls:
                combined_text += f"• {url}\n"
        
        # Send the original batch
        await self.bot_forwarder.forward_message("BATCH", combined_text)
        
        # Process with LLM and send result
        try:
            llm_result = await process_batch_with_llm(batch_messages)
            
            # Handle different result types
            if hasattr(llm_result, 'result'):
                # ProcessingResult object
                result_text = llm_result.result
            elif isinstance(llm_result, str):
                # String result
                result_text = llm_result
            else:
                # Other object types
                result_text = str(llm_result)
            
            if result_text and not result_text.startswith("LLM processing failed"):
                # llm_text = f"🤖 **LLM Analysis:**\n\n{result_text}"
                await self.bot_forwarder.forward_message("LLM", result_text)
                logger.info(f"✅ LLM analysis sent for {len(batch_messages)} messages")
            else:
                logger.warning(f"⚠️ LLM processing failed or returned empty result")
        except Exception as e:
            logger.error(f"❌ Error in LLM processing: {e}")
        
        logger.info(f"✅ Batch sent successfully ({len(batch_messages)} messages, {len(all_urls)} URLs)")
    
    async def batch_processor_task(self) -> None:
        """Background task to process message batches every 2 minutes"""
        while True:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                current_time = asyncio.get_event_loop().time()
                if current_time - self.last_batch_time >= self.batch_interval:
                    await self.send_batch()
                    
            except Exception as e:
                logger.error(f"❌ Error in batch processor: {e}")
                await asyncio.sleep(10)

    async def start_background_tasks(self) -> None:
        """Start background polling and heartbeat tasks"""
        polling_task = asyncio.create_task(self.polling_task())
        self.background_tasks.append(polling_task)
        heartbeat_task = asyncio.create_task(self.heartbeat_task())
        self.background_tasks.append(heartbeat_task)
        batch_task = asyncio.create_task(self.batch_processor_task())
        self.background_tasks.append(batch_task)
        logger.info("Background tasks started")

    async def polling_task(self) -> None:
        """Background polling task"""
        while True:
            try:
                await self.gap_handler.fill_gap()
                await asyncio.sleep(Config.POLLING_INTERVAL)
            except Exception as e:
                logger.error(f"Polling error: {e}")
                await asyncio.sleep(10)

    async def heartbeat_task(self) -> None:
        """Background heartbeat task"""
        while True:
            try:
                if self.telegram_client.get_client().is_connected():
                    await self.telegram_client.get_client()(GetStateRequest())
                    logger.info("Heartbeat signal sent")
                await asyncio.sleep(Config.HEARTBEAT_INTERVAL)
            except Exception as e:
                logger.warning(f"Heartbeat error: {e}")
                await asyncio.sleep(10)

    async def start_monitoring(self) -> None:
        """Start monitoring all channels"""
        try:
            # Send test message to bot
            await self.bot_forwarder.send_test_message()
            
            # Setup event handlers
            channel_ids = self.telegram_client.get_channel_ids()
            self.event_handler.register_message_handler(self.process_message)
            self.event_handler.install_handlers(channel_ids)
            # Start background tasks
            await self.start_background_tasks()
            # Start monitoring
            channel_names = [channel['title'] for channel in self.telegram_client.get_target_channels().values()]
            logger.info(f"Monitoring started for channels: {', '.join(channel_names)}")
            await self.telegram_client.get_client().run_until_disconnected()
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        finally:
            await self.cleanup()

    async def cleanup(self) -> None:
        """Cleanup resources"""
        for task in self.background_tasks:
            task.cancel()
        await self.telegram_client.disconnect()
        logger.info("Channel monitor cleaned up") 