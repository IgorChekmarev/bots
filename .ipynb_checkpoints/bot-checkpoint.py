import os
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен и ID из переменных окружения
TOKEN = os.environ.get('BOT_TOKEN')
OWNER_ID = int(os.environ.get('OWNER_ID', 0))
WEBHOOK_URL = os.environ.get('RENDER_EXTERNAL_HOSTNAME')

# Создаем Flask приложение для вебхуков
flask_app = Flask(__name__)

# Создаем Telegram бота
bot = Bot(token=TOKEN)
application = Application.builder().bot(bot).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик /start"""
    await update.message.reply_text(
        f"✅ Бот работает!\n"
        f"Твой ID: {update.effective_user.id}"
    )
    logger.info(f"Start от {update.effective_user.id}")

async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пересылка сообщений владельцу"""
    user = update.effective_user
    await context.bot.send_message(
        chat_id=OWNER_ID,
        text=f"👤 @{user.username or user.id}: {update.message.text}"
    )
    await update.message.reply_text("✅ Отправлено!")
    logger.info(f"Переслано сообщение от {user.id}")

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    """Обработчик вебхуков"""
    update = Update.de_json(request.get_json(), bot)
    application.process_update(update)
    return 'OK', 200

@flask_app.route('/')
def index():
    return 'Telegram bot is running!', 200

def main():
    """Запуск"""
    logger.info("🚀 Запуск бота...")
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))
    
    # Инициализируем бота
    application.initialize()
    
    # Запускаем Flask
    port = int(os.environ.get('PORT', 10000))
    flask_app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    main()