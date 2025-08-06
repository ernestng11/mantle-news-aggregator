#!/usr/bin/env python3
"""
Script to get your chat ID for bot forwarding
"""
import asyncio
import aiohttp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def get_chat_id():
    """Get chat ID from bot updates"""
    bot_token = os.getenv("BOT_TOKEN")
    
    if not bot_token:
        print("❌ Please set BOT_TOKEN in your .env file")
        print("💡 Create a bot via @BotFather and get the token")
        return
    
    print("🔍 Getting chat ID from bot updates...")
    print(f"🤖 Bot token: {bot_token[:10]}...")
    print()
    print("📝 Instructions:")
    print("1. Start your bot by sending /start to it")
    print("2. Send any message to your bot")
    print("3. This script will show your chat ID")
    print()
    
    bot_url = f"https://api.telegram.org/bot{bot_token}"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Get updates
            async with session.get(f"{bot_url}/getUpdates") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("ok") and data.get("result"):
                        updates = data["result"]
                        print(f"📊 Found {len(updates)} updates:")
                        print()
                        
                        for update in updates:
                            print(update)
                            if "message" in update:
                                message = update["message"]
                                chat = message.get("chat", {})
                                chat_id = chat.get("id")
                                chat_type = chat.get("type")
                                chat_title = chat.get("title", "")
                                chat_username = chat.get("username", "")
                                chat_first_name = chat.get("first_name", "")
                                
                                print(f"💬 Chat ID: {chat_id}")
                                print(f"📋 Type: {chat_type}")
                                if chat_title:
                                    print(f"📝 Title: {chat_title}")
                                if chat_username:
                                    print(f"👤 Username: @{chat_username}")
                                if chat_first_name:
                                    print(f"👤 Name: {chat_first_name}")
                                print(f"📄 Message: {message.get('text', '')[:50]}...")
                                print("-" * 40)
                        
                        if updates:
                            print()
                            print("💡 Add this to your .env file:")
                            print(f"BOT_CHAT_ID={updates[-1]['message']['chat']['id']}")
                        else:
                            print("❌ No messages found. Please send a message to your bot first.")
                    else:
                        print(f"❌ Error getting updates: {data}")
                else:
                    print(f"❌ HTTP error: {response.status}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(get_chat_id()) 