import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен и ID из переменных окружения
TOKEN = os.environ.get('BOT_TOKEN')
OWNER_ID = int(os.environ.get('OWNER_ID', 0))

if not TOKEN:
    raise ValueError("Нет BOT_TOKEN в переменных окружения!")
if not OWNER_ID:
    raise ValueError("Нет OWNER_ID в переменных окружения!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}!\n"
        f"Я бот-пересылатель. Твой ID: {user.id}\n"
        f"Бот работает через webhook на Render!"
    )
    logger.info(f"Пользователь {user.id} запустил бота")

async def forward_to_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пересылает сообщения владельцу"""
    user = update.effective_user
    message = update.message
    
    try:
        # Отправляем владельцу
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"📨 От @{user.username or user.id}:\n{message.text}"
        )
        await message.reply_text("✅ Сообщение отправлено владельцу!")
        logger.info(f"Переслано сообщение от {user.id} владельцу {OWNER_ID}")
    except Exception as e:
        logger.error(f"Ошибка при пересылке: {e}")
        await message.reply_text("❌ Не удалось отправить сообщение")

async def forward_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пересылает медиафайлы владельцу"""
    user = update.effective_user
    
    try:
        if update.message.photo:
            file_id = update.message.photo[-1].file_id
            await context.bot.send_photo(
                chat_id=OWNER_ID,
                photo=file_id,
                caption=f"📸 Фото от @{user.username or user.id}"
            )
        elif update.message.document:
            file_id = update.message.document.file_id
            await context.bot.send_document(
                chat_id=OWNER_ID,
                document=file_id,
                caption=f"📎 Документ от @{user.username or user.id}"
            )
        await update.message.reply_text("✅ Файл отправлен владельцу!")
        logger.info(f"Переслан файл от {user.id}")
    except Exception as e:
        logger.error(f"Ошибка при пересылке файла: {e}")
        await update.message.reply_text("❌ Не удалось отправить файл")

async def webhook_handler(request):
    """Обработчик webhook запросов"""
    return "OK"

def main():
    """Главная функция запуска бота"""
    logger.info("🚀 Запуск бота на Render...")
    logger.info(f"📱 Бот: {TOKEN[:10]}...")
    logger.info(f"👤 Владелец ID: {OWNER_ID}")
    
    # Создаем приложение (НЕ Updater!)
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_owner))
    application.add_handler(MessageHandler(filters.PHOTO, forward_media))
    application.add_handler(MessageHandler(filters.Document.ALL, forward_media))
    
    # Для Render используем webhook
    port = int(os.environ.get('PORT', 10000))
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    
    logger.info(f"🌍 Webhook URL: {webhook_url}")
    logger.info(f"🔌 Порт: {port}")
    
    # Запускаем webhook
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_url=webhook_url,
        secret_token=None,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()