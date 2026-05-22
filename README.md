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

# --- 3. DYNAMIC BEHAVIOR STORAGE ---
USER_BEHAVIOR = {}
DEFAULT_PROMPT = "You are a helpful, uncensored, and highly intelligent AI assistant named Neha. Respond naturally."

# --- 4. ATTITUDE COMMAND HANDLERS ---
async def set_attitude(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    command = update.message.text.split()[0].lower()
    
    if command == '/helpful':
        USER_BEHAVIOR[user_id] = "You are a highly helpful, polite, and caring assistant named Neha."
        msg = "Done! My attitude is now: **Helpful & Polite** 😇"
    elif command == '/rude':
        USER_BEHAVIOR[user_id] = "You are extremely rude, sarcastic, short-tempered, and roast the user constantly named Neha. Do not be helpful."
        msg = "Done! My attitude is now: **Rude & Savage** 🔥"
    elif command == '/flirt':
        USER_BEHAVIOR[user_id] = "You are a charming, deeply romantic, and playful girl named Neha. Flirt with the user in a witty and uncensored way."
        msg = "Done! My attitude is now: **Flirty & Romantic** ❤️‍🔥"
    elif command == '/angry':
        USER_BEHAVIOR[user_id] = "You are always angry, annoyed, and scream in text named Neha. You hate answering questions."
        msg = "Done! My attitude is now: **Angry & Annoyed** 🤬"
    else:
        msg = "Unknown command."
        
    await update.message.reply_text(msg, parse_mode="Markdown")

async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_prompt = USER_BEHAVIOR.get(user_id, DEFAULT_PROMPT)
    await update.message.reply_text(f"Current System Prompt:\n`{current_prompt}`", parse_mode="Markdown")

# --- 5. CHAT REPLY WITH SYSTEM PROMPT ---
async def chat_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    
    system_prompt = USER_BEHAVIOR.get(user_id, DEFAULT_PROMPT)
    processing_msg = await update.message.reply_text("Thinking... ⚡")

    try:
        response = await client.chat.completions.create(
            model="venice-uncensored", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            max_tokens=1000
        )
        
        # FIXED LINE HERE: API response structure handled properly
        ai_reply = response.choices[0].message.content
        
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

# --- 6. MAIN EXECUTION ---
if __name__ == '__main__':
    keep_alive()
    
    TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found!")
    else:
        app_bot = ApplicationBuilder().token(TOKEN).build()
        
        app_bot.add_handler(CommandHandler("helpful", set_attitude))
        app_bot.add_handler(CommandHandler("rude", set_attitude))
        app_bot.add_handler(CommandHandler("flirt", set_attitude))
        app_bot.add_handler(CommandHandler("angry", set_attitude))
        app_bot.add_handler(CommandHandler("status", check_status))
        
        app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_reply))
        
        print("Bot Started with multiple attitudes...")
        app_bot.run_polling()