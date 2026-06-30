import os
import logging
from flask import Flask, request
import google.generativeai as genai
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://shwan.onrender.com
PORT = int(os.getenv("PORT", "10000"))

if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN missing")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY missing")
if not WEBHOOK_URL:
    raise RuntimeError("WEBHOOK_URL missing")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

flask_app = Flask(__name__)
telegram_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سڵاو! من ئامادەم.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text or "ببورە، وەڵامم نەبوو.")
    except Exception:
        logging.exception("Gemini error")
        await update.message.reply_text("هەڵە ڕوویدا. دوبارە هەوڵ بدە.")


telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


@flask_app.route("/")
def home():
    return "Bot is alive!"


@flask_app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    await telegram_app.initialize()
    await telegram_app.process_update(update)
    return "ok"


@flask_app.before_request
async def setup_webhook_once():
    if not getattr(flask_app, "webhook_set", False):
        await telegram_app.bot.set_webhook(f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}")
        flask_app.webhook_set = True


if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=PORT)