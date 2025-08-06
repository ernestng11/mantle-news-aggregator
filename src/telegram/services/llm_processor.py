from workers.llm_process import LLMProcess, PromptType, LLMConfig
from typing import List, Dict, Any
import re
from src.utils.logger import get_logger

logger = get_logger(__name__)

def fix_telegram_hashtags(text: str) -> str:
    """Fix hashtags for Telegram Markdown formatting"""
    # Remove backslashes before hashtags
    text = re.sub(r'\\#', '#', text)
    # Ensure hashtags are properly formatted
    text = re.sub(r'#(\w+)', r'#\1', text)
    return text

def convert_markdown_to_html(text: str) -> str:
    """Convert Markdown formatting to HTML for Telegram"""
    # Convert bold markdown to HTML
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    return text

async def process_batch_with_llm(batch_messages: List[Dict[str, Any]], prompt: str = None) -> str:
    """
    Process batched messages with LLM
    
    Args:
        batch_messages: List of message dictionaries with 'channel_handle', 'message_text', 'urls'
        prompt: Custom prompt to use (optional)
    
    Returns:
        Processed text from LLM
    """
    try:
        # Combine all messages into one text
        combined_text = "Batched Messages:\n\n"
        for i, msg in enumerate(batch_messages, 1):
            channel = msg.get('channel_handle', 'unknown')
            text = msg.get('message_text', '')
            urls = msg.get('urls', [])
            
            combined_text += f"{i}. @{channel}: {text}\n"
            if urls:
                combined_text += f"   Links: {', '.join(urls)}\n"
            combined_text += "\n"
        
        # Use enhanced expert prompt if none provided
        if not prompt:
            prompt = f"""You are a cryptocurrency and macro markets analyst. Analyze the provided news messages and organize them into the following categories:

**Categories to identify:**
- 🏦 **Macro Economics** (Fed policy, inflation, interest rates, GDP)
- 💰 **Bitcoin/Digital Gold** (BTC price, adoption, institutional flows)
- 🏗️ **DeFi/Protocols** (DeFi hacks, new protocols, yield farming)
- 🏢 **Institutional** (ETF flows, corporate adoption, regulatory news)
- ⚡ **Layer 2/Scaling** (Ethereum L2s, scaling solutions)
- 🎯 **Altcoins** (specific altcoin news, memecoins)
- 🔒 **Security/Hacks** (exploits, security incidents, audits)
- 📊 **Market Analysis** (price action, technical analysis, sentiment)
- 🌍 **Global Adoption** (country adoption, CBDCs, regulations)
- 🚀 **Innovation/Technology** (new tech, partnerships, developments)

**Format your response as:**

**📂 Categorized News Summary:**

🏦 **Macro Economics**
• [News point with context] #Macro #Economics #Fed

💰 **Bitcoin/Digital Gold** 
• [News point with context] #Bitcoin #BTC #DigitalGold

[Continue for each relevant category...]

Use relevant hashtags for each category and point. Focus on actionable insights and market implications.

{combined_text}"""
        
        # Create LLM configuration
        config = LLMConfig(
            model_name="gpt-4o",
            temperature=0.2,
            max_tokens=16000
        )
        
        # Process with LLM
        result = await LLMProcess.process_text_with_prompt(
            text_data=combined_text,
            prompt_type=PromptType.CUSTOM,
            custom_prompt=prompt,
            provider_name="openai",
            config=config
        )
        
        # Fix formatting for Telegram
        if hasattr(result, 'result'):
            result.result = fix_telegram_hashtags(result.result)
            result.result = convert_markdown_to_html(result.result)
        elif isinstance(result, str):
            result = fix_telegram_hashtags(result)
            result = convert_markdown_to_html(result)
        
        logger.info(f"✅ LLM processed {len(batch_messages)} messages")
        return result
        
    except Exception as e:
        logger.error(f"❌ LLM processing failed: {e}")
        return f"LLM processing failed: {str(e)}"
