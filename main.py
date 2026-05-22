import os
from flask import Flask
from threading import Thread
import telebot
from openai import OpenAI

# --- 1. KEEP ALIVE SERVER (Render Free Tier Ke Liye) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Neha Bot is running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# --- 2. KEYS & OPENROUTER SETUP ---
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OPENROUTER_KEY = os.environ.get('OPENROUTER_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)

client = OpenAI(
    api_key=OPENROUTER_KEY,
    base_url="https://openrouter.ai",
    default_headers={
        "HTTP-Referer": "https://render.com",
        "X-Title": "Telegram Uncensored GenZ Bot"
    }
)

# --- 3. GENZ PERSONALITY STORAGE ---
USER_BEHAVIOR = {}
CONVO_MEMORY = {}

# Strict GenZ Rules: No robot script, mix of English/Hinglish, short replies
DEFAULT_PROMPT = (
    "You are a real human GenZ Indian girl named Neha, talking to your close friend. "
    "STRICT RULES:\n"
    "1. Never use dialogue labels like 'Gaurav:', 'Tu:', 'Neha:', or 'Assistant:'. Reply ONLY with your direct thoughts.\n"
    "2. Keep your replies extremely short, punchy, and casual (strictly 1 or 2 short sentences, under 15 words).\n"
    "3. Speak like a modern Indian girl using Hinglish (mix of Hindi and English, use words like 'yaar', 'chill', 'hmmm', 'wbu?'). No formal robotic language."
)

# --- 4. ATTITUDE COMMAND HANDLERS ---
@bot.message_handler(commands=['flirt', 'rude', 'angry', 'helpful'])
def set_attitude(message):
    user_id = message.from_user.id
    command = message.text.strip().lower()
    
    if command == '/flirt':
        USER_BEHAVIOR[user_id] = "You are a charming, deeply romantic, and playful GenZ girl named Neha. Flirt witty and uncensored, keep it to 1-2 short sentences without any script formatting."
        msg = "Done! My attitude is now: **Flirty & Romantic** ❤️‍🔥"
    elif command == '/rude':
        USER_BEHAVIOR[user_id] = "You are an extremely rude, sarcastic GenZ girl named Neha. Roast the user bluntly in 1 short sentence. No robot style."
        msg = "Done! My attitude is now: **Rude & Savage** 🔥"
    elif command == '/angry':
        USER_BEHAVIOR[user_id] = "You are always angry, annoyed, and scream in text (use CAPS). Short irritated GenZ responses only."
        msg = "Done! My attitude is now: **Angry & Annoyed** 🤬"
    else:
        USER_BEHAVIOR[user_id] = DEFAULT_PROMPT
        msg = "Done! My attitude is now: **Helpful & Polite** 😇"
        
    CONVO_MEMORY[user_id] = [] # Memory reset on mood change
    bot.reply_to(message, msg, parse_mode="Markdown")

# --- 5. CHAT REPLIES WITH FALLBACK & CLEANING ---
MODELS_POOL = [
    "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
    "meta-llama/llama-3-8b-instruct:free",
    "gryphe/mythomax-l2-13b:free"
]

@bot.message_handler(func=lambda message: True)
def chat_reply(message):
    user_id = message.from_user.id
    user_text = message.text
    
    system_prompt = USER_BEHAVIOR.get(user_id, DEFAULT_PROMPT)
    
    if user_id not in CONVO_MEMORY:
        CONVO_MEMORY[user_id] = []
        
    CONVO_MEMORY[user_id].append({"role": "user", "content": user_text})
    if len(CONVO_MEMORY[user_id]) > 8:
        CONVO_MEMORY[user_id] = CONVO_MEMORY[user_id][-8:]
        
    messages_payload = [{"role": "system", "content": system_prompt}] + CONVO_MEMORY[user_id]
    processing_msg = bot.reply_to(message, "Thinking... ⚡")
    ai_reply = None
    
    for model_name in MODELS_POOL:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages_payload,
                max_tokens=150
            )
            if response and response.choices:
                ai_reply = response.choices.message.content
                if ai_reply:
                    break
        except Exception:
            continue

    if ai_reply:
        # STRICT FORCE CLEANING: Script formats (Labels) ko delete karna
        cleaned_reply = ai_reply
        for label in ["Neha:", "Gaurav:", "Tu:", "Assistant:", "Shakshi:"]:
            cleaned_reply = cleaned_reply.replace(label, "")
        if ":" in cleaned_reply and len(cleaned_reply.split(":")[0]) < 12:
            cleaned_reply = cleaned_reply.split(":")[-1] # Strip any accidental script tags
            
        cleaned_reply = cleaned_reply.strip()
        CONVO_MEMORY[user_id].append({"role": "assistant", "content": cleaned_reply})
        
        try:
            bot.edit_message_text(cleaned_reply, chat_id=message.chat.id, message_id=processing_msg.message_id)
        except Exception:
            bot.send_message(message.chat.id, cleaned_reply)
    else:
        bot.edit_message_text("All servers are busy, try in 5 seconds! ⏳", chat_id=message.chat.id, message_id=processing_msg.message_id)

if __name__ == '__main__':
    keep_alive()
    print("Neha is starting on Render...")
    bot.infinity_polling()

