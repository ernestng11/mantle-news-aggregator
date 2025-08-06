# Telegram News Funnel

A Python application that monitors Telegram channels and forwards messages to a bot with batching capabilities.

## How main.py Runs

### Application Flow

The application follows this execution flow when `main.py` is run:

#### 1. **Initialization Phase**
```python
# Setup logging and validate configuration
logger = setup_logger()
Config.validate_config()
```

#### 2. **Channel Monitor Creation**
```python
# Create the main monitoring service
monitor = ChannelMonitor()
await monitor.initialize()
```

#### 3. **Channel Addition**
```python
# Load channels from allowed_channels.txt and add them to monitoring
await monitor.add_channels(Config.TARGET_CHANNELS)
```

#### 4. **Monitoring Start**
```python
# Begin continuous monitoring with background tasks
await monitor.start_monitoring()
```

### Background Tasks

The application runs several background tasks simultaneously:

- **Message Processing**: Handles incoming messages from Telegram channels
- **Gap Filling**: Ensures no messages are missed during connection issues
- **Heartbeat**: Maintains connection health with periodic signals
- **Batch Processing**: Collects messages for 2 minutes before forwarding

### Message Flow

1. **Message Reception**: Telegram messages are received via event handlers
2. **URL Extraction**: URLs are extracted from message entities
3. **Batch Collection**: Messages are added to a 2-minute batch
4. **Batch Forwarding**: Collected messages are sent to configured bot targets

### Configuration

The application uses environment variables and configuration files:

- **`.env`**: Contains API credentials and bot settings
- **`allowed_channels.txt`**: List of Telegram channels to monitor
- **`config.py`**: Centralized configuration management

### Running the Application

```bash
# Install dependencies
poetry install

# Run the application
poetry run python -m src.main
```

### Expected Output

```
PG Onchain - Telegram Channel Monitor & Trading Bot
============================================================
2025-07-14 18:39:00,177 - pg_onchain - INFO - Starting configuration validation...
2025-07-14 18:39:00,178 - pg_onchain - INFO - Configuration validated successfully
2025-07-14 18:39:00,178 - pg_onchain - INFO - Creating channel monitor...
2025-07-14 18:39:00,178 - pg_onchain - INFO - Initializing channel monitor...
2025-07-14 18:39:00,178 - pg_onchain - INFO - Channel monitor initialized successfully
2025-07-14 18:39:00,178 - pg_onchain - INFO - Adding 29 target channels...
2025-07-14 18:39:00,178 - pg_onchain - INFO - All channels added successfully
2025-07-14 18:39:00,178 - pg_onchain - INFO - Starting monitoring...
```

### Key Features

- **Message Batching**: Collects messages for 2 minutes before forwarding
- **URL Extraction**: Automatically extracts and displays URLs from messages
- **Dual Forwarding**: Sends to both personal chat and channel
- **Error Handling**: Robust error handling with fallback mechanisms
- **Connection Management**: Automatic reconnection and gap filling

### Architecture

```
main.py
├── Config (Configuration Management)
├── ChannelMonitor (Main Service)
│   ├── TelegramClientWrapper (Telegram Connection)
│   ├── MessageHandler (Message Processing)
│   ├── BotForwarder (Bot Communication)
│   └── Background Tasks (Batch, Heartbeat, Gap Filling)
└── Event Handlers (Message Reception)
```

### Environment Variables

Required environment variables in `.env`:

```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
BOT_CHAT_ID=your_chat_id
BOT_CHANNEL_ID=your_channel_id
```

### Monitoring Channels

The application monitors channels listed in `allowed_channels.txt`:

```
https://t.me/cointelegraph
https://t.me/CoinDeskGlobal
https://t.me/the_block_crypto
...
```

### Output Format

Forwarded messages include:

- **Channel handle**: `@cointelegraph`
- **Message content**: Original message text
- **Extracted URLs**: Links found in the message
- **Batch information**: Number of messages in batch

Example:
```
📢 @cointelegraph

COINTELEGRAPH: Arcadia Finance exploited, $2.5M stolen and converted to WETH

🔗 Links (1):
• https://cointelegraph.com/news/arcadia-finance-exploit-2-5m-crypto-theft
```
