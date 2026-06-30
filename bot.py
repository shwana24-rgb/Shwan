import os
import logging
from telegram.ext import ApplicationBuilder, MessageHandler, filters
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)

# خوێندنەوەی تۆکێنەکان لە سێتینگی ڕێندەر
TOKEN = os.environ.get('TELEGRAM_TOKEN')
API_KEY = os.environ.get('GEMINI_API_KEY')

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

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
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        app.run_polling()
