import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# ڕێکخستنی ژینگە
TOKEN = os.getenv('TELEGRAM_TOKEN')
API_KEY = os.getenv('GEMINI_API_KEY')
PORT = int(os.environ.get('PORT', '8080'))

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سڵاو! من ئامادەم بۆ یارمەتیدانت.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    response = model.generate_content(user_text)
    await update.message.reply_text(response.text)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    # بەکارهێنانی Webhook بۆ ئەوەی Render بۆتەکەت نەکوژێنێتەوە
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://shwan.onrender.com/{TOKEN}"
    )