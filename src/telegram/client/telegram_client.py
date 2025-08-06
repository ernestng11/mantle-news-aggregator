"""
Telegram client wrapper
"""
from telethon import TelegramClient
from telethon.tl.types import InputChannel, Channel
from telethon.tl.functions.updates import GetStateRequest
from typing import Dict, Any, Optional
from src.core.config import Config
from src.core.exceptions import TelegramError
from src.utils.logger import get_logger

logger = get_logger(__name__)

class TelegramClientWrapper:
    """Wrapper for Telegram client operations"""
    
    def __init__(self):
        logger.info("Initializing Telegram client wrapper...")
        # Use file-based session instead of StringSession
        session_name = getattr(Config, 'TELEGRAM_SESSION_NAME', 'anon')
        self.client = TelegramClient(
            session_name,
            Config.TELEGRAM_API_ID,
            Config.TELEGRAM_API_HASH
        )
        self.target_channels = {}
        logger.info(f"Telegram client wrapper initialized with session: {session_name}")
    
    async def connect(self) -> None:
        """Connect to Telegram"""
        try:
            logger.info("Attempting to connect to Telegram...")
            await self.client.connect()
            logger.info("Telegram client connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Telegram: {e}")
            raise TelegramError(f"Failed to connect to Telegram: {e}")
    
    async def disconnect(self) -> None:
        """Disconnect from Telegram"""
        if self.client:
            await self.client.disconnect()
            logger.info("Telegram client disconnected")
    
    async def get_entity(self, channel_identifier: str) -> Channel:
        """Get channel entity"""
        try:
            logger.info(f"Getting entity for: {channel_identifier}")
            entity = await self.client.get_entity(channel_identifier)
            if not isinstance(entity, Channel):
                raise TelegramError("Entity is not a channel")
            logger.info(f"Successfully got entity: {entity.title}")
            return entity
        except Exception as e:
            logger.error(f"Failed to get entity for {channel_identifier}: {e}")
            raise TelegramError(f"Failed to get entity: {e}")
    
    async def add_target_channel(self, channel_identifier: str) -> Dict[str, Any]:
        """Add target channel to monitor"""
        try:
            logger.info(f"Adding target channel: {channel_identifier}")
            entity = await self.get_entity(channel_identifier)
            
            if entity.access_hash is None:
                raise TelegramError("Channel access_hash is None")
            
            input_channel = InputChannel(entity.id, entity.access_hash)
            
            # Extract channel handle
            handle = channel_identifier.replace('@', '').lower()
            
            channel_data = {
                'input_channel': input_channel,
                'title': entity.title,
                'handle': handle,
                'pts': 0
            }
            
            self.target_channels[entity.id] = channel_data
            
            # Initialize pts
            try:
                logger.info(f"Initializing pts for {entity.title}...")
                state = await self.client(GetStateRequest())
                self.target_channels[entity.id]['pts'] = state.pts
                logger.info(f"Initialized pts for {entity.title}: {state.pts}")
            except Exception as e:
                logger.warning(f"Could not initialize pts for {entity.title}, using 0: {e}")
                self.target_channels[entity.id]['pts'] = 0
            
            logger.info(f"Added target channel: {entity.title} (ID: {entity.id})")
            return channel_data
            
        except Exception as e:
            logger.error(f"Failed to add target channel {channel_identifier}: {e}")
            raise TelegramError(f"Failed to add target channel: {e}")
    
    def get_client(self) -> TelegramClient:
        """Get the underlying Telegram client"""
        return self.client
    
    def get_target_channels(self) -> Dict[int, Dict[str, Any]]:
        """Get target channels dictionary"""
        return self.target_channels
    
    def get_channel_ids(self) -> list:
        """Get list of channel IDs"""
        return list(self.target_channels.keys()) 