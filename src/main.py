"""
Main application entry point
"""
import asyncio
from src.core.config import Config
from src.telegram.services.channel_monitor import ChannelMonitor
from src.utils.logger import setup_logger

def main():
    """Main application function"""
    # Setup logging
    logger = setup_logger()
    
    print("PG Onchain - Telegram Channel Monitor & Trading Bot")
    print("=" * 60)
    
    try:
        # Validate configuration
        logger.info("Starting configuration validation...")
        Config.validate_config()
        logger.info("Configuration validated successfully")
        
        logger.info("Starting application...")
        # Run the application
        asyncio.run(run_application())
        
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
    except Exception as e:
        logger.error(f"Application failed: {e}")
        raise

async def run_application():
    """Run the main application"""
    logger = setup_logger()
    logger.info("Creating channel monitor...")
    monitor = ChannelMonitor()
    
    try:
        # Initialize monitor
        logger.info("Initializing channel monitor...")
        await monitor.initialize()
        logger.info("Channel monitor initialized successfully")
        
        # Add target channels
        logger.info(f"Adding {len(Config.TARGET_CHANNELS)} target channels...")
        await monitor.add_channels(Config.TARGET_CHANNELS)
        logger.info("All channels added successfully")
        
        # Start monitoring
        logger.info("Starting monitoring...")
        await monitor.start_monitoring()
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise

if __name__ == "__main__":
    main() 