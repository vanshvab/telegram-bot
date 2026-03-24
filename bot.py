import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
import anthropic

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
conversation_history = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! 👋 Я AI-асистент на базі Claude. Напиши мені що-небудь!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    if user_id not in conversation_history:
        conversation_history[user_id] = []

    conversation_history[user_id].append({"role": "user", "content": user_text})

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system="You are a helpful AI assistant in Telegram. Always respond in the same language the user writes in.",
        messages=conversation_history[user_id]
    )

    reply = response.content[0].text
    conversation_history[user_id].append({"role": "assistant", "content": reply})

    if len(conversation_history[user_id]) > 20:
        conversation_history[user_id] = conversation_history[user_id][-20:]

    await update.message.reply_text(reply)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot started! ✅")
    app.run_polling()

if __name__ == "__main__":
    main()
