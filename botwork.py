import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ВСТАВЬТЕ СВОИ ДАННЫЕ
TOKEN = "Ваш токен"
OWNER_ID = 123456789  # ID владельца

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

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_owner))
    app.add_handler(MessageHandler(filters.PHOTO, forward_media))
    app.add_handler(MessageHandler(filters.VIDEO, forward_media))
    app.add_handler(MessageHandler(filters.Document.ALL, forward_media))  # ИСПРАВЛЕНО!
    app.add_handler(MessageHandler(filters.AUDIO, forward_media))
    app.add_handler(MessageHandler(filters.VOICE, forward_media))
    
    print("Бот запущен...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()