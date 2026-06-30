import os
import logging
import requests
from flask import Flask, request

logging.basicConfig(level=logging.INFO)

# خوێندنەوەی زانیارییەکان لە Environment Variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", "10000"))

if not TELEGRAM_TOKEN or not GEMINI_API_KEY or not WEBHOOK_URL:
    raise RuntimeError("تکایە دڵنیابە لەوەی TELEGRAM_TOKEN, GEMINI_API_KEY, و WEBHOOK_URL لە سێتینگی ڕێندەر دانراون")

app = Flask(__name__)

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
# ناوی مۆدێلی دروست بۆ جیمینای
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    f"models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
)

def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=20)

def ask_gemini(user_text):
    payload = {"contents": [{"parts": [{"text": user_text}]}]}
    try:
        r = requests.post(GEMINI_URL, json=payload, timeout=40)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "هەڵەیەک لە جیمینای ڕوویدا، تکایە API KEYـەکەت بپشکنە."
    except Exception:
        return "سێرڤەری جیمینای وەڵام ناداتەوە."

@app.route("/")
def home():
    return "Bot is alive!"

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = request.get_json(force=True)
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        user_text = update["message"].get("text", "")
        
        if user_text == "/start":
            send_message(chat_id, "سڵاو! من ئامادەم، پرسیارێکت هەیە؟")
        else:
            answer = ask_gemini(user_text)
            send_message(chat_id, answer)
    return "ok"

def set_webhook():
    webhook = f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
    requests.post(f"{TELEGRAM_API}/setWebhook", json={"url": webhook}, timeout=20)

if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=PORT)