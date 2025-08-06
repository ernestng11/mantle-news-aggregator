"""
Configuration management for the application
"""
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from src.utils.logger import get_logger

load_dotenv()

class Config:
    """Centralized configuration management"""
    
    # Telegram Configuration
    TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "29695747"))
    TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "adc8079294b4d2e224197beda96af3d3")
    TELEGRAM_SESSION_STR = os.getenv("TELEGRAM_SESSION_STR", "1AZWarzUBu3Xj3HzPnYWHADM1xR0yMrMvpi5WTtfxpf0vQxVFc6T1VTbURSJagA0aRbr4CLjAkTYXbslw8PEeKX8eYmH9UAN6oOcsWr7MHHlEC-nvV71xdQPDzASxB-FNQOv4tYmZM0OaNz6-Y97js0CbXxzfbj1N_abrsZQJ9I8Hx79gHOtsy2V5AUMrJFa_E0RBXuGk5c5inXEikbabcej7U38B3shxJ8_CaLOWtticAieWH5i0xqqfE7dNDbmPEnOhPkNYCKFgs_z2BwrVRvsSkerfWKsiAJazbt18FP0lsm1xVhkrv8vgoq-mMACkHJDknJiRfLwgd7pVBKAR3HmrOHGzpHQ=")
    TELEGRAM_SESSION_NAME = os.getenv("TELEGRAM_SESSION_NAME", "anon")
    
    # Bot Configuration
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    BOT_CHAT_ID = os.getenv("BOT_CHAT_ID", "")
    BOT_CHANNEL_ID = os.getenv("BOT_CHANNEL_ID", "")
    
    # Target Channels
    def _load_target_channels():
        """Load target channels from allowed_channels.txt file"""
        channels = []
        try:
            file_path = os.path.join(os.path.dirname(__file__), 'allowed_channels.txt')
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and line.startswith('https://t.me/'):
                        # Extract channel handle from URL
                        handle = line.replace('https://t.me/', '@')
                        channels.append(handle)
            logger = get_logger(__name__)
            logger.info(f"Loaded {len(channels)} channels from allowed_channels.txt")
        except Exception as e:
            logger = get_logger(__name__)
            logger.warning(f"Could not load allowed_channels.txt: {e}")
            # Fallback to default channels
            channels = [
                "@CoinDeskGlobal",
                "@pgonchaintesting", 
                "@the_block_crypto",
                "@WatcherGuru",
                "@cointelegraph",
                "@unfolded",
            ]
        return channels
    
    TARGET_CHANNELS = _load_target_channels()
  
    
    # Background task intervals
    POLLING_INTERVAL = 5
    HEARTBEAT_INTERVAL = 840  # 14 minutes
    BATCH_INTERVAL = 5*60  # 5 minutes in seconds
    
    # File paths
    TRADE_LOG_FILE = "output.jsonl"
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration values"""
        if not cls.TARGET_CHANNELS:
            raise ValueError("No target channels configured")
        return True 