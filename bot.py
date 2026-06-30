import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import ApplicationBuilder, MessageHandler, filters
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)

# خوێندنەوەی تۆکێنەکان لە سێتینگی ڕێندەر
TOKEN = os.environ.get('TELEGRAM_TOKEN')
API_KEY = os.environ.get('GEMINI_API_KEY')
PORT = int(os.environ.get('PORT', 10000))  # ڕێندەر خۆی ئەم PORT ـە دابین دەکات

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')


# --- سێرڤەرێکی سادەی HTTP، تەنها بۆ ئەوەی ڕێندەر port ـێکی کراوە ببینێت ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def log_message(self, format, *args):
        pass  # بێدەنگ کردنی لۆگی هەر ڕیکوێستێکی HTTP


def run_health_server():
    server = HTTPServer(('0.0.0.0', PORT), HealthCheckHandler)
    server.serve_forever()


async def handle_message(update, context):
    try:
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


if __name__ == '__main__':
    if not TOKEN or not API_KEY:
        print("تۆکێن یان API Key دیاری نەکراوە!")
    else:
        # سێرڤەری HTTP لە thread ـێکی جیادا دەستپێدەکات
        threading.Thread(target=run_health_server, daemon=True).start()

        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        app.run_polling()
