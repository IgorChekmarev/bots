import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, request
import os
import threading

# Токен и ID владельца берутся из переменных окружения
TOKEN = os.environ.get('BOT_TOKEN')
OWNER_ID = int(os.environ.get('OWNER_ID', 0))

if not TOKEN or not OWNER_ID:
    raise ValueError("BOT_TOKEN и OWNER_ID должны быть установлены в переменных окружения!")

# Flask приложение для Koyeb
app = Flask(__name__)
bot_app = None

@app.route('/')
def home():
    return "Бот работает на Koyeb! 🚀"

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint для Telegram webhook"""
    if bot_app:
        update = Update.de_json(request.get_json(), bot_app.bot)
        bot_app.process_update(update)
    return "OK", 200

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Здравствуйте, {user.first_name}!\n"
        "Я пересылаю ваши сообщения владельцу."
    )

async def forward_to_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message
    
    user_info = (
        f"📨 Новое сообщение для бота\n"
        f"👤 От: {user.first_name} {user.last_name or ''}\n"
        f"🆔 ID: {user.id}\n"
        f"📱 Username: @{user.username or 'нет'}\n"
        f"💬 Сообщение:\n{message.text}"
    )
    
    await context.bot.send_message(
        chat_id=OWNER_ID,
        text=user_info
    )
    
    await message.reply_text("✅ Сообщение отправлено владельцу!")

async def forward_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if update.message.photo:
        file_type = "📸 Фото"
        file_id = update.message.photo[-1].file_id
        caption = f"{file_type} от @{user.username or user.id}"
        await context.bot.send_photo(chat_id=OWNER_ID, photo=file_id, caption=caption)
    
    elif update.message.video:
        file_type = "🎥 Видео"
        file_id = update.message.video.file_id
        caption = f"{file_type} от @{user.username or user.id}"
        await context.bot.send_video(chat_id=OWNER_ID, video=file_id, caption=caption)
    
    elif update.message.document:
        file_type = "📎 Документ"
        file_id = update.message.document.file_id
        caption = f"{file_type} от @{user.username or user.id}"
        await context.bot.send_document(chat_id=OWNER_ID, document=file_id, caption=caption)
    
    elif update.message.audio:
        file_type = "🎵 Аудио"
        file_id = update.message.audio.file_id
        caption = f"{file_type} от @{user.username or user.id}"
        await context.bot.send_audio(chat_id=OWNER_ID, audio=file_id, caption=caption)
    
    elif update.message.voice:
        file_type = "🎤 Голосовое"
        file_id = update.message.voice.file_id
        caption = f"{file_type} от @{user.username or user.id}"
        await context.bot.send_voice(chat_id=OWNER_ID, voice=file_id, caption=caption)
    
    await update.message.reply_text("✅ Сообщение отправлено владельцу!")

async def setup_webhook():
    """Установка webhook при запуске"""
    global bot_app
    bot_app = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_owner))
    bot_app.add_handler(MessageHandler(filters.PHOTO, forward_media))
    bot_app.add_handler(MessageHandler(filters.VIDEO, forward_media))
    bot_app.add_handler(MessageHandler(filters.Document.ALL, forward_media))
    bot_app.add_handler(MessageHandler(filters.AUDIO, forward_media))
    bot_app.add_handler(MessageHandler(filters.VOICE, forward_media))
    
    # Инициализируем приложение
    await bot_app.initialize()
    
    # Получаем имя приложения из переменных окружения Koyeb
    app_name = os.environ.get('KOYEB_APP_NAME', 'your-app-name')
    webhook_url = f"https://{app_name}.koyeb.app/webhook"
    
    await bot_app.bot.set_webhook(url=webhook_url)
    print(f"Webhook установлен на: {webhook_url}")

def run_flask():
    """Запуск Flask сервера"""
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)

def main():
    """Главная функция"""
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Устанавливаем webhook и запускаем
    asyncio.run(setup_webhook())
    
    # Держим скрипт запущенным
    flask_thread.join()

if __name__ == "__main__":
    main()