"""
Gap filling logic for missed updates
"""
import asyncio
from telethon.tl.functions.updates import GetChannelDifferenceRequest
from telethon.tl.types import ChannelMessagesFilterEmpty
from telethon import errors, types
from typing import Dict, Any
from src.utils.logger import get_logger

logger = get_logger(__name__)

class GapHandler:
    """Handle gap filling for missed updates"""
    
    def __init__(self, client, target_channels: Dict[int, Dict[str, Any]]):
        self.client = client
        self.target_channels = target_channels
    
    async def fill_gap(self) -> None:
        """Fill gaps in updates using getChannelDifference for all channels"""
        if not self.client or not self.target_channels:
            return
        
        for channel_id, channel_data in self.target_channels.items():
            try:
                diff = await self.client(GetChannelDifferenceRequest(
                    channel=channel_data['input_channel'],
                    filter=ChannelMessagesFilterEmpty(),
                    pts=channel_data['pts'],
                    limit=100
                ))
                
                if isinstance(diff, types.updates.ChannelDifference):
                    logger.info(f"Filling gap for {channel_data['title']}: {len(diff.new_messages)} new messages")
                    for message in diff.new_messages:
                        # Process message through registered handlers
                        await self.process_gap_message(message, channel_data['title'])
                    
                    self.target_channels[channel_id]['pts'] = diff.pts
                
                elif isinstance(diff, types.updates.ChannelDifferenceTooLong):
                    logger.warning(f"Gap too long for {channel_data['title']}, refreshing dialog state")
                    dialog = diff.dialog
                    # Use getattr to safely access pts attribute
                    pts = getattr(dialog, 'pts', None)
                    if pts is not None:
                        self.target_channels[channel_id]['pts'] = pts
                
            except errors.FloodWaitError as e:
                logger.warning(f"Flood wait for {channel_data['title']}: {e.seconds} seconds")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                logger.error(f"Gap filling failed for {channel_data['title']}: {e}")
    
    async def process_gap_message(self, message, channel_title: str) -> None:
        """Process a message from gap filling"""
        # This will be overridden by the channel monitor
        logger.info(f"Processing gap message from {channel_title}: {message.id}")
    
    def set_message_processor(self, processor) -> None:
        """Set the message processor for gap messages"""
        self.process_gap_message = processor 