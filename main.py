import os
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import AsyncOpenAI

# --- 1. KEEP ALIVE SERVER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# --- 2. VENICE AI SETUP ---
client = AsyncOpenAI(
    api_key=os.environ.get('VENICE_API_KEY'),
    base_url="https://venice.ai"
)

# --- 3. BOT LOGIC ---
async def chat_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    processing_msg = await update.message.reply_text("Thinking... ⚡")

    try:
        response = await client.chat.completions.create(
            model="venice-uncensored", 
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_text}
            ],
            max_tokens=1000
        )
        
        ai_reply = response.choices.message.content
        
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=processing_msg.message_id,
            text=ai_reply
        )

    except Exception as e:
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=processing_msg.message_id,
            text=f"Error: {str(e)}"
        )

# --- 4. MAIN EXECUTION ---
if __name__ == '__main__':
    keep_alive()
    
    TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found!")
    else:
        app_bot = ApplicationBuilder().token(TOKEN).build()
        app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_reply))
        
        print("Bot Started...")
        app_bot.run_polling()
