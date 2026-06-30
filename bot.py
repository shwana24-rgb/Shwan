import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram.ext import ApplicationBuilder, MessageHandler, filters
import google.generativeai as genai

# --- دروستکردنی سێرڤەرێکی بچووک بۆ ڕازیکردنی ڕێندەر ---
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

def run_dummy_server():
    # ڕێندەر خۆی پۆرتێک دیاری دەکات لە ڕێگەی ژینگەکەیەوە (PORT)
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyServer)
    server.serve_forever()
# --------------------------------------------------

# لێرە کلیلەکەی جیمینای دابنێ
genai.configure(api_key='لێرە_API_KEY_دابنێ')
model = genai.GenerativeModel('gemini-1.5-flash')

async def handle_message(update, context):
    user_text = update.message.text
    response = model.generate_content(user_text)
    await update.message.reply_text(response.text)

if __name__ == '__main__':
    # ١. دەستپێکردنی سێرڤەرە بچووکەکە لە Threadێکی جیاوازدا پێش بۆتەکە
    threading.Thread(target=run_dummy_server, daemon=True).start()

    # ٢. دەستپێکردنی بۆتی تێلیگرام بە شێوازی ئاسایی Polling (پێویست بە Webhook ناکات)
    app = ApplicationBuilder().token('لێرە_تۆکێن_دابنێ').build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Starting bot polling...")
    app.run_polling()