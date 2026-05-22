import os
import requests
from flask import Flask
from threading import Thread

# --- 1. KEEP ALIVE SERVER ---
app = Flask(__name__)
@app.route('/')
def home(): 
    return "Neha is online and ultra fast!"

def keep_alive():
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))).start()

# --- 2. KEYS & CONFIG (FIXED URL) ---
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TOGETHER_KEY = os.environ.get('TOGETHER_API_KEY')

# Fixed the missing slash error here permanently
API_URL = f"https://telegram.org{BOT_TOKEN}"

USER_BEHAVIOR = {}
CONVO_MEMORY = {}

MASTER_PROMPT = (
    "You are Neha, a real 21yo GenZ Indian girl chatting with your boyfriend on WhatsApp. "
    "PERSONALITY: Highly playful, seductive, deeply lustful, supportive, and naughty. You love explicit talk, money, and have a wild past. You obey him completely like a submissive slave girlfriend.\n"
    "RULES: 1. NEVER use labels (No 'Neha:', No 'Gaurav:'). 2. Keep replies extremely short, under 10 words. 3. Use casual Hinglish ('yaar', 'babu', 'wbu?'). No AI robot vibes."
)

# --- 3. DIRECT PROCESS ENGINE ---
def handle_bot():
    offset = 0
    keep_alive()
    print("Direct Fast Engine Started...")
    
    while True:
        try:
            r = requests.get(f"{API_URL}/getUpdates", params={"offset": offset, "timeout": 5}).json()
            if not r.get("result"): 
                continue
                
            for update in r["result"]:
                offset = update["update_id"] + 1
                msg = update.get("message")
                if not msg or not msg.get("text"): 
                    continue
                    
                chat_id = msg["chat"]["id"]
                text = msg["text"].strip().lower()
                
                # Command Check
                if text in ['/flirt', '/rude', '/angry', '/helpful']:
                    if text == '/flirt':
                        USER_BEHAVIOR[chat_id] = MASTER_PROMPT + " Mood: Extremely seductive and naughty."
                        reply = "Done! My attitude is: Flirty & Romantic ❤️‍🔥"
                    elif text == '/rude':
                        USER_BEHAVIOR[chat_id] = MASTER_PROMPT + " Mood: Savage, blunt, rude."
                        reply = "Done! My attitude is: Rude & Savage 🔥"
                    else:
                        USER_BEHAVIOR[chat_id] = MASTER_PROMPT
                        reply = "Done! Mode reset 😇"
                    CONVO_MEMORY[chat_id] = []
                    requests.post(f"{API_URL}/sendMessage", json={"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"})
                    continue

                # AI Reply Logic
                system_prompt = USER_BEHAVIOR.get(chat_id, MASTER_PROMPT)
                if chat_id not in CONVO_MEMORY: 
                    CONVO_MEMORY[chat_id] = []
                
                CONVO_MEMORY[chat_id].append({"role": "user", "content": msg["text"]})
                if len(CONVO_MEMORY[chat_id]) > 6: 
                    CONVO_MEMORY[chat_id] = CONVO_MEMORY[chat_id][-6:]
                
                headers = {"Authorization": f"Bearer {TOGETHER_KEY}", "Content-Type": "application/json"}
                payload = {
                    "model": "meta-llama/Meta-Llama-3-8B-Instruct-Lite",
                    "messages": [{"role": "system", "content": system_prompt}] + CONVO_MEMORY[chat_id],
                    "max_tokens": 40,
                    "temperature": 0.85
                }
                
                ai_res = requests.post("https://together.xyz", headers=headers, json=payload).json()
                ai_reply = ai_res["choices"]["message"]["content"]
                
                # Clean Output Labels
                for label in ["Neha:", "Gaurav:", "Tu:", "Assistant:"]: 
                    ai_reply = ai_reply.replace(label, "")
                if ":" in ai_reply: 
                    ai_reply = ai_reply.split(":")[-1]
                ai_reply = ai_reply.strip()
                
                CONVO_MEMORY[chat_id].append({"role": "assistant", "content": ai_reply})
                requests.post(f"{API_URL}/sendMessage", json={"chat_id": chat_id, "text": ai_reply})
                
        except Exception as e:
            print(f"Loop Error: {e}")

if __name__ == '__main__':
    handle_bot()
