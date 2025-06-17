import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = telebot.TeleBot(TOKEN)

post_text = ""
sponsors = []
join_button = {"text": "🚀 Вступити в команду", "url": "https://t.me/your_join_link"}

def create_keyboard():
    keyboard = InlineKeyboardMarkup()
    for s in sponsors:
        keyboard.add(InlineKeyboardButton(s['text'], url=s['url']))
    keyboard.add(InlineKeyboardButton(join_button["text"], callback_data="join_team"))
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привіт! 🤖 Я бот для створення постів. Обери дію:")
    show_menu(message.chat.id)

def show_menu(chat_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('➕ Додати спонсора', '✏️ Змінити текст')
    markup.row('👁 Попередній перегляд', '📢 Опублікувати пост')
    bot.send_message(chat_id, "Меню:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    global post_text
    if message.text == '➕ Додати спонсора':
        bot.send_message(message.chat.id, "Введи текст кнопки і посилання через кому:")
        bot.register_next_step_handler(message, add_sponsor)
    elif message.text == '✏️ Змінити текст':
        bot.send_message(message.chat.id, "Введи новий текст посту:")
        bot.register_next_step_handler(message, change_post_text)
    elif message.text == '👁 Попередній перегляд':
        bot.send_message(message.chat.id, post_text or "⛔️ Текст порожній", reply_markup=create_keyboard())
    elif message.text == '📢 Опублікувати пост':
        bot.send_message(CHANNEL_ID, post_text or "⛔️ Текст порожній", reply_markup=create_keyboard())
        bot.send_message(message.chat.id, "✅ Пост опубліковано!")
    else:
        bot.send_message(message.chat.id, "Команду не розпізнано.")
        show_menu(message.chat.id)

def add_sponsor(message):
    try:
        text, url = map(str.strip, message.text.split(',', 1))
        sponsors.append({"text": text, "url": url})
        bot.send_message(message.chat.id, f"✅ Додано спонсора: {text}")
    except:
        bot.send_message(message.chat.id, "❌ Помилка. Формат: Текст, https://...")
    show_menu(message.chat.id)

def change_post_text(message):
    global post_text
    post_text = message.text
    bot.send_message(message.chat.id, "✅ Текст оновлено.")
    show_menu(message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "join_team")
def check_subscription(call):
    user_id = call.from_user.id
    all_subscribed = True
    for s in sponsors:
        try:
            channel = s['url'].split("/")[-1]
            member = bot.get_chat_member(f"@{channel}", user_id)
            if member.status in ['left', 'kicked']:
                all_subscribed = False
                break
        except:
            all_subscribed = False
            break
    if all_subscribed:
        bot.send_message(user_id, f"🎉 Дякую! Тепер ти в команді.")
        bot.answer_callback_query(call.id, "✅ Доступ відкрито.")
    else:
        bot.answer_callback_query(call.id, "🔒 Підпишись на всі канали!")

bot.infinity_polling()
