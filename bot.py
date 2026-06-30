import os
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PORT = int(os.getenv("PORT", "8080"))

if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN is missing in Render Environment")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing in Render Environment")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

    def log_message(self, format, *args):
        return


def run_dummy_server():
    server = HTTPServer(("0.0.0.0", PORT), DummyServer)
    server.serve_forever()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سڵاو! من ئامادەم بۆ یارمەتیدانت.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        response = model.generate_content(user_text)
        text = response.text if response.text else "ببورە، وەڵامم بۆ دروست نەبوو."
        await update.message.reply_text(text)
    except Exception as e:
        logging.exception(e)
        await update.message.reply_text("هەڵەیەک ڕوویدا، تکایە دووبارە هەوڵ بدەوە.")


if __name__ == "__main__":
    threading.Thread(target=run_dummy_server, daemon=True).start()

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Starting bot polling...")
    app.run_polling()
