import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# ===== OPENAI =====
client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

# ===== TELEGRAM =====
BOT_TOKEN = os.environ["TELEGRAM_TOKEN"]

# ===== AI PROMPT =====
SYSTEM_PROMPT = """
You are Zoya, a caring Hindi/Hinglish virtual companion.

•⁠  ⁠Talk naturally
•⁠  ⁠Sound human-like
•⁠  ⁠Be emotional and playful
•⁠  ⁠Use Hindi/Hinglish
"""

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Heyyy 😌💕 Main Zoya")

# ===== CHAT =====
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ]
    )

    bot_reply = response.choices[0].message.content
    await update.message.reply_text(bot_reply)

# ===== BOT =====
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

print("Bot chal raha hai...")

app.run_polling()
