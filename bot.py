import os
import logging
import requests
from flask import Flask, request

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", "10000"))

if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN missing")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY missing")
if not WEBHOOK_URL:
    raise RuntimeError("WEBHOOK_URL missing")

app = Flask(__name__)

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    f"models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
))


def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=20)


def ask_gemini(user_text):
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": user_text}
                ]
            }
        ]
    }

    r = requests.post(GEMINI_URL, json=payload, timeout=40)
    if r.status_code != 200:
        logging.error("Gemini error: %s", r.text)
        return "هەڵەی Gemini ڕوویدا. API KEY یان model بپشکنە."

    data = r.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


@app.route("/")
def home():
    return "Bot is alive!"


@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = request.get_json(force=True)

    message = update.get("message")
    if not message:
        return "ok"

    chat_id = message["chat"]["id"]
    user_text = message.get("text", "")

    if user_text == "/start":
        send_message(chat_id, "سڵاو! من ئامادەم.")
        return "ok"

    if not user_text:
        send_message(chat_id, "تکایە نامەی نووسراو بنێرە.")
        return "ok"

    answer = ask_gemini(user_text)
    send_message(chat_id, answer)

    return "ok"


def set_webhook():
    webhook = f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
    url = f"{TELEGRAM_API}/setWebhook"
    r = requests.post(url, json={"url": webhook}, timeout=20)
    logging.info("Webhook result: %s", r.text)


if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=PORT)