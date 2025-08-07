# Heroku Deployment Guide

## Prerequisites

1. **Heroku CLI installed**
2. **Git repository set up**
3. **All environment variables ready**

## Step 1: Install Heroku CLI

```bash
# macOS
brew install heroku/brew/heroku

# Or download from https://devcenter.heroku.com/articles/heroku-cli
```

## Step 2: Login to Heroku

```bash
heroku login
```

## Step 3: Create Heroku App

```bash
# Create a new app
heroku create your-app-name

# Or use existing app
heroku git:remote -a your-app-name
```

## Step 4: Set Environment Variables

```bash
# Set all required environment variables
heroku config:set TELEGRAM_API_ID="your_api_id"
heroku config:set TELEGRAM_API_HASH="your_api_hash"
heroku config:set TELEGRAM_SESSION_NAME="anon"
heroku config:set BOT_TOKEN="your_bot_token"
heroku config:set BOT_CHAT_ID="your_chat_id"
heroku config:set BOT_CHANNEL_ID="your_channel_id"
heroku config:set OPENAI_API_KEY="your_openai_key"

# Optional: Set batch interval
heroku config:set BATCH_INTERVAL="120"
```

## Step 5: Deploy to Heroku

```bash
# Add all files
git add .

# Commit changes
git commit -m "Deploy to Heroku"

# Push to Heroku
git push heroku main
```

## Step 6: Start the Worker Dyno

```bash
# Scale up the worker dyno
heroku ps:scale worker=1

# Check dyno status
heroku ps
```

## Step 7: Monitor Logs

```bash
# View real-time logs
heroku logs --tail

# View recent logs
heroku logs
```

## Important Notes

1. **Worker Dyno**: This app runs as a worker dyno, not a web dyno
2. **Session Files**: Telegram session files will be stored in Heroku's ephemeral filesystem
3. **Restarts**: The app will need to re-authenticate with Telegram after each restart
4. **Costs**: Worker dynos cost money (~$7/month for hobby dyno)

## Troubleshooting

### Check if app is running:
```bash
heroku ps
```

### Restart the app:
```bash
heroku restart
```

### View detailed logs:
```bash
heroku logs --tail
```

### Access Heroku console:
```bash
heroku run bash
```

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_API_ID` | Yes | Your Telegram API ID |
| `TELEGRAM_API_HASH` | Yes | Your Telegram API Hash |
| `TELEGRAM_SESSION_NAME` | No | Session name (default: anon) |
| `BOT_TOKEN` | Yes | Your Telegram Bot Token |
| `BOT_CHAT_ID` | Yes | Your personal chat ID |
| `BOT_CHANNEL_ID` | No | Channel ID for forwarding |
| `OPENAI_API_KEY` | Yes | OpenAI API Key |
| `BATCH_INTERVAL` | No | Batch interval in seconds (default: 120) | 