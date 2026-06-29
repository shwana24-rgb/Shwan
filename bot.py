from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import google.generativeai as genai

# لێرەدا تۆکێنەکەی تێلیگرامەکەت دابنێ
TOKEN = ''

# لێرەدا API Keyـەکەی جیمینای دابنێ
genai.configure(api_key='')

model = genai.GenerativeModel('gemini-1.5-flash')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="سڵاو! من ئامادەم، هەر پرسیارێکت هەیە لێم بکە.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    response = model.generate_content(user_text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response.text)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    application.run_polling()