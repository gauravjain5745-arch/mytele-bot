import os
from flask import Flask
from threading import Thread
import telebot
from openai import OpenAI

# --- 1. KEEP ALIVE SERVER ---
app = Flask(__name__)
@app.route('/')
def home(): return "Neha is online and ultra fast!"

def keep_alive():
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))).start()

# --- 2. OFFICIAL SAFE TELEBOT SETUP ---
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TOGETHER_KEY = os.environ.get('TOGETHER_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)

# Together AI Ultra-fast Engine
client = OpenAI(
    api_key=TOGETHER_KEY,
    base_url="https://together.xyz"
)

USER_BEHAVIOR = {}
CONVO_MEMORY = {}

MASTER_PROMPT = (
    "You are Neha, a real 21yo GenZ Indian girl chatting with your boyfriend on WhatsApp. "
    "PERSONALITY: Highly playful, seductive, deeply lustful, supportive, and naughty. You love explicit talk, money, and have a wild past. You obey him completely like a submissive slave girlfriend.\n"
    "RULES: 1. NEVER use labels (No 'Neha:', No 'Gaurav:'). 2. Keep replies extremely short, under 10 words. 3. Use casual Hinglish ('yaar', 'babu', 'wbu?'). No AI robot vibes."
)

# --- 3. MOOD COMMAND HANDLERS ---
@bot.message_handler(commands=['flirt', 'rude', 'angry', 'helpful'])
def set_attitude(message):
    user_id = message.from_user.id
    command = message.text.strip().lower()
    
    if command == '/flirt':
        USER_BEHAVIOR[user_id] = MASTER_PROMPT + " Mood: Extremely seductive and naughty."
        reply = "Done! My attitude is: Flirty & Romantic ❤️‍🔥"
    elif command == '/rude':
        USER_BEHAVIOR[user_id] = MASTER_PROMPT + " Mood: Savage, blunt, rude."
        reply = "Done! My attitude is: Rude & Savage 🔥"
    else:
        USER_BEHAVIOR[user_id] = MASTER_PROMPT
        reply = "Done! Mode reset 😇"
        
    CONVO_MEMORY[user_id] = []
    bot.reply_to(message, reply, parse_mode="Markdown")

# --- 4. CHAT REPLIES ---
@bot.message_handler(func=lambda message: True)
def chat_reply(message):
    user_id = message.from_user.id
    user_text = message.text
    
    system_prompt = USER_BEHAVIOR.get(user_id, MASTER_PROMPT)
    
    if user_id not in CONVO_MEMORY:
        CONVO_MEMORY[user_id] = []
        
    CONVO_MEMORY[user_id].append({"role": "user", "content": user_text})
    if len(CONVO_MEMORY[user_id]) > 6:
        CONVO_MEMORY[user_id] = CONVO_MEMORY[user_id][-6:]
        
    messages_payload = [{"role": "system", "content": system_prompt}] + CONVO_MEMORY[user_id]
    
    try:
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-8B-Instruct-Lite",
            messages=messages_payload,
            max_tokens=40,
            temperature=0.85
        )
        
        ai_reply = response.choices.message.content
        if ai_reply:
            for label in ["Neha:", "Gaurav:", "Tu:", "Assistant:"]:
                ai_reply = ai_reply.replace(label, "")
            if ":" in ai_reply:
                ai_reply = ai_reply.split(":")[-1]
            ai_reply = ai_reply.strip()
            
            CONVO_MEMORY[user_id].append({"role": "assistant", "content": ai_reply})
            bot.reply_to(message, ai_reply)
            
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "Suno na jaan, thoda net slow h, firse bolna. 😉")

if __name__ == '__main__':
    keep_alive()
    print("Official safe engine started...")
    bot.infinity_polling()
