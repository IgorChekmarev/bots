import telebot
import json
import os
import signal
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# === НАСТРОЙКИ ===
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

if not TOKEN:
    print("❌ Токен не найден в .env!")
    exit(1)

bot = telebot.TeleBot(TOKEN, parse_mode='Markdown')
print(f"✅ Бот инициализирован")

# === ХРАНЕНИЕ ДАННЫХ ===
MAPPING_FILE = 'mapping.json'
chats_mapping = {}
temp_shop_data = {}

def load_mapping():
    global chats_mapping
    try:
        with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
            chats_mapping = json.load(f)
        print(f"✅ Загружено {len(chats_mapping)} привязок")
    except:
        chats_mapping = {}
        print("ℹ️ Создаем новую базу привязок")

def save_mapping():
    with open(MAPPING_FILE, 'w', encoding='utf-8') as f:
        json.dump(chats_mapping, f, ensure_ascii=False, indent=2)

# === КОМАНДЫ (ТОЛЬКО ОДИН РАЗ КАЖДАЯ!) ===
@bot.message_handler(commands=['start', 'help'])
def start_command(message):
    """Команда /start и /help"""
    print(f"\n📨 [{datetime.now().strftime('%H:%M:%S')}] /start от {message.from_user.id}")
    
    help_text = (
        "🤖 *Бот-мост для отчетов магазинов*\n\n"
        "⚙️ *Основные команды:*\n"
        "▫️ /setup - пошаговая настройка магазина\n"
        "▫️ /id - узнать ID чата/топика\n"
        "▫️ /myid - узнать свой личный ID\n"
        "▫️ /list - список всех привязок\n"
        "▫️ /delete [ID_маг] - удалить привязку\n\n"
        "🔧 *Команды для настройки:*\n"
        "▫️ /get_shop_id - в чате магазина: получить ID\n"
        "▫️ /get_topic_id - в топике руководства: привязать\n"
        "▫️ /manual_add - ручная привязка\n\n"
        "📝 *Как настроить:*\n"
        "1. В чате магазина напишите /get_shop_id\n"
        "2. В топике руководства напишите /get_topic_id\n"
        "3. Готово! Сообщения будут пересылаться автоматически."
    )
    
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['id', 'chatid'])
def id_command(message):
    """Узнать ID чата и топика"""
    print(f"\n📨 [{datetime.now().strftime('%H:%M:%S')}] /id от {message.from_user.id}")
    
    info = f"💬 *ID чата:* `{message.chat.id}`\n"
    
    if hasattr(message, 'message_thread_id') and message.message_thread_id:
        info += f"🗂️ *ID топика:* `{message.message_thread_id}`\n"
    
    info += f"📋 Тип чата: {message.chat.type}\n"
    
    if hasattr(message.chat, 'title'):
        info += f"🏷️ Название: {message.chat.title}\n"
    
    info += f"\n👤 Ваш личный ID: `{message.from_user.id}`"
    
    bot.send_message(message.chat.id, info)
    print(f"   📤 Отправлен ID чата: {message.chat.id}")

@bot.message_handler(commands=['myid'])
def myid_command(message):
    """Узнать свой личный Telegram ID"""
    print(f"\n📨 [{datetime.now().strftime('%H:%M:%S')}] /myid от {message.from_user.id}")
    
    response = (
        f"👤 *Ваши данные:*\n\n"
        f"🆔 Личный ID: `{message.from_user.id}`\n"
        f"📛 Имя: {message.from_user.first_name}\n"
    )
    
    if message.from_user.last_name:
        response += f"📛 Фамилия: {message.from_user.last_name}\n"
    
    if message.from_user.username:
        response += f"📱 Username: @{message.from_user.username}\n"
    
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['setup'])
def setup_command(message):
    """Пошаговая настройка магазина"""
    print(f"\n📨 [{datetime.now().strftime('%H:%M:%S')}] /setup от {message.from_user.id}")
    
    instructions = (
        "🔧 *Пошаговая настройка магазина:*\n\n"
        "1️⃣ *Добавьте бота в чат магазина*\n"
        "   - Зайдите в чат вашего магазина\n"
        "   - Добавьте бота как участника\n"
        "   - Дайте права администратора\n\n"
        "2️⃣ *Получите ID чата магазина*\n"
        "   - В чате магазина напишите: `/get_shop_id`\n"
        "   - Бот сохранит ID чата\n\n"
        "3️⃣ *Привяжите к топику руководства*\n"
        "   - Зайдите в супергруппу '🎯 ОПЕРАЦИОННЫЙ ШТАБ'\n"
        "   - Откройте топик вашего магазина\n"
        "   - Напишите: `/get_topic_id`\n\n"
        "✅ *Готово!* Сообщения будут пересылаться автоматически."
    )
    
    bot.send_message(message.chat.id, instructions)

@bot.message_handler(commands=['get_shop_id'])
def get_shop_id_command(message):
    """Получить ID чата магазина"""
    if message.chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "❌ Работает только в чатах магазинов!")
        return
    
    print(f"\n📨 [{datetime.now().strftime('%H:%M:%S')}] /get_shop_id в чате {message.chat.id}")
    
    chat_title = getattr(message.chat, 'title', 'Без названия')
    user_id = str(message.from_user.id)
    
    temp_shop_data[user_id] = {
        'shop_chat_id': message.chat.id,
        'shop_name': chat_title
    }
    
    response = (
        f"🏪 *ID чата магазина получен!*\n\n"
        f"📛 Название: {chat_title}\n"
        f"🔢 ID чата: `{message.chat.id}`\n\n"
        f"📝 *Следующий шаг:*\n"
        f"Зайдите в топик этого магазина в супергруппе руководства "
        f"и напишите `/get_topic_id`"
    )
    
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['get_topic_id'])
def get_topic_id_command(message):
    """Получить ID топика и завершить привязку"""
    user_id = str(message.from_user.id)
    
    if user_id not in temp_shop_data:
        bot.reply_to(message, "❌ Сначала /get_shop_id в чате магазина!")
        return
    
    # Определяем topic_id
    if hasattr(message, 'message_thread_id') and message.message_thread_id:
        topic_id = message.message_thread_id
    else:
        topic_id = 1  # Для General/основного чата
    
    shop_data = temp_shop_data[user_id]
    
    # Проверяем, нет ли уже привязки
    if str(shop_data['shop_chat_id']) in chats_mapping:
        bot.reply_to(message, f"❌ Этот магазин уже привязан!")
        del temp_shop_data[user_id]
        return
    
    # Создаем привязку
    chats_mapping[str(shop_data['shop_chat_id'])] = {
        'name': shop_data['shop_name'],
        'management_chat': message.chat.id,
        'topic_id': topic_id,
        'created': datetime.now().strftime('%d.%m.%Y %H:%M')
    }
    
    save_mapping()
    del temp_shop_data[user_id]
    
    response = (
        f"✅ *Привязка создана!*\n\n"
        f"🏪 Магазин: {shop_data['shop_name']}\n"
        f"🔢 ID чата магазина: `{shop_data['shop_chat_id']}`\n"
        f"👥 ID супергруппы: `{message.chat.id}`\n"
        f"🗂️ ID топика: `{topic_id}`\n\n"
        f"🔔 *Теперь:*\n"
        f"• Сообщения из чата магазина будут пересылаться в этот топик\n"
        f"• Ответы из топика будут пересылаться обратно в чат"
    )
    
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['list'])
def list_command(message):
    """Список всех привязок"""
    print(f"\n📨 [{datetime.now().strftime('%H:%M:%S')}] /list от {message.from_user.id}")
    
    if not chats_mapping:
        bot.reply_to(message, "📭 Нет привязок")
        return
    
    text = "📋 *Привязанные магазины:*\n\n"
    for shop_id, data in chats_mapping.items():
        text += f"🏪 *{data['name']}*\n"
        text += f"• ID магазина: `{shop_id}`\n"
        text += f"• ID руководства: `{data['management_chat']}`\n"
        text += f"• ID топика: `{data['topic_id']}`\n"
        text += f"• Добавлен: {data['created']}\n"
        text += "━━━━━━━━━━━━━━━━\n"
    
    bot.send_message(message.chat.id, text)
    print(f"   📤 Отправлен список из {len(chats_mapping)} привязок")

@bot.message_handler(commands=['delete'])
def delete_command(message):
    """Удалить привязку"""
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Формат: /delete ID_магазина")
            return
        
        shop_id = parts[1]
        if shop_id in chats_mapping:
            name = chats_mapping[shop_id]['name']
            del chats_mapping[shop_id]
            save_mapping()
            bot.reply_to(message, f"✅ Удалено: {name}")
        else:
            bot.reply_to(message, "❌ Магазин не найден")
    
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

# === ПЕРЕСЫЛКА СООБЩЕНИЙ ===
@bot.message_handler(func=lambda m: str(m.chat.id) in chats_mapping and m.text)
def forward_from_shop(message):
    """Пересылка из чата магазина в топик руководства"""
    try:
        shop_id = str(message.chat.id)
        data = chats_mapping.get(shop_id)
        
        if not data or not data.get('management_chat'):
            return
        
        sender_name = message.from_user.first_name
        if message.from_user.last_name:
            sender_name += f" {message.from_user.last_name}"
        
        text = (
            f"🏪 *{data['name']}*\n"
            f"👤 {sender_name}\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"{message.text}"
        )
        
        bot.send_message(
            chat_id=data['management_chat'],
            message_thread_id=data['topic_id'],
            text=text
        )
        
        print(f"📤 [{datetime.now().strftime('%H:%M:%S')}] Отчет из {data['name']}")
        
    except Exception as e:
        print(f"❌ Ошибка пересылки из магазина: {e}")

@bot.message_handler(func=lambda m: any(
    str(m.chat.id) == str(data.get('management_chat')) 
    and m.message_thread_id == data.get('topic_id')
    for data in chats_mapping.values() if data.get('management_chat')
))
def forward_from_management(message):
    """Пересылка ответа из топика руководства обратно в магазин"""
    try:
        for shop_id, data in chats_mapping.items():
            if (str(message.chat.id) == str(data.get('management_chat')) and 
                message.message_thread_id == data.get('topic_id')):
                
                sender_name = message.from_user.first_name
                if message.from_user.last_name:
                    sender_name += f" {message.from_user.last_name}"
                
                text = f"{sender_name}:\n{message.text}"
                
                bot.send_message(
                    chat_id=int(shop_id),
                    text=text
                )
                
                print(f"📤 [{datetime.now().strftime('%H:%M:%S')}] Ответ от {sender_name} в {data['name']}")
                break
                
    except Exception as e:
        print(f"❌ Ошибка обратной пересылки: {e}")

# === ЗАПУСК ===
if __name__ == '__main__':
    load_mapping()
    
    print("=" * 60)
    print("🤖 СИСТЕМА ОТЧЕТНОСТИ МАГАЗИНОВ")
    print("=" * 60)
    print(f"🔗 Привязок: {len(chats_mapping)}")
    print("👂 Ожидание сообщений...")
    print("⚡ Ctrl+C для остановки")
    print("=" * 60)
    
    try:
        bot.polling(none_stop=True, timeout=30)
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
        save_mapping()