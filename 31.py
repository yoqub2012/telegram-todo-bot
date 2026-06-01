"""
📋 Telegram To-Do List Bot
Yoqub's Portfolio Project

O'rnatish:
    pip install pyTelegramBotAPI

Ishlatish:
    1. @BotFather dan token oling
    2. TOKEN o'zgaruvchisiga joylashtiring
    3. python todo_bot.py
"""

import telebot
from telebot import types

TOKEN = "8859549037:AAFPLK--RMEg_dSlpWsiS-7PnHxwWJ3vSRE"  # @BotFather dan olingan token

bot = telebot.TeleBot(TOKEN)

# Foydalanuvchilarning vazifalari (xotira ichida)
# Production uchun SQLite yoki PostgreSQL ishlatish tavsiya etiladi
user_tasks = {}


def get_tasks(user_id):
    """Foydalanuvchi vazifalarini olish"""
    if user_id not in user_tasks:
        user_tasks[user_id] = []
    return user_tasks[user_id]


def main_keyboard():
    """Asosiy tugmalar"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Vazifa qo'shish", "📋 Ro'yxat")
    markup.add("✅ Bajarildi", "❌ O'chirish")
    markup.add("🗑 Hammasini tozalash")
    return markup


@bot.message_handler(commands=['start', 'help'])
def start(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    get_tasks(user_id)  # Foydalanuvchini ro'yxatga olish

    text = (
        f"👋 Salom, {name}!\n\n"
        f"📋 Men — vazifalar botiman.\n\n"
        f"Nima qila olaman:\n"
        f"➕ Vazifa qo'shish\n"
        f"📋 Vazifalar ro'yxatini ko'rish\n"
        f"✅ Vazifani bajarildi deb belgilash\n"
        f"❌ Vazifani o'chirish\n\n"
        f"Boshlaylik! 🚀"
    )
    bot.send_message(message.chat.id, text, reply_markup=main_keyboard())


@bot.message_handler(func=lambda m: m.text == "📋 Ro'yxat")
def show_tasks(message):
    user_id = message.from_user.id
    tasks = get_tasks(user_id)

    if not tasks:
        bot.send_message(
            message.chat.id,
            "📭 Hozircha vazifalar yo'q.\n➕ Yangi vazifa qo'shing!",
            reply_markup=main_keyboard()
        )
        return

    text = "📋 *Sizning vazifalaringiz:*\n\n"
    for i, task in enumerate(tasks, 1):
        status = "✅" if task['done'] else "⬜"
        text += f"{status} *{i}.* {task['text']}\n"

    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_keyboard())


@bot.message_handler(func=lambda m: m.text == "➕ Vazifa qo'shish")
def add_task_prompt(message):
    msg = bot.send_message(
        message.chat.id,
        "✏️ Yangi vazifani yozing:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(msg, save_task)


def save_task(message):
    user_id = message.from_user.id
    task_text = message.text.strip()

    if not task_text or task_text.startswith('/'):
        bot.send_message(message.chat.id, "❗ Noto'g'ri kiritish.", reply_markup=main_keyboard())
        return

    tasks = get_tasks(user_id)
    tasks.append({'text': task_text, 'done': False})

    bot.send_message(
        message.chat.id,
        f"✅ Vazifa qo'shildi:\n📌 *{task_text}*",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )


@bot.message_handler(func=lambda m: m.text == "✅ Bajarildi")
def mark_done_prompt(message):
    user_id = message.from_user.id
    tasks = get_tasks(user_id)
    undone = [(i, t) for i, t in enumerate(tasks) if not t['done']]

    if not undone:
        bot.send_message(
            message.chat.id,
            "🎉 Barcha vazifalar bajarilgan!",
            reply_markup=main_keyboard()
        )
        return

    markup = types.InlineKeyboardMarkup()
    for i, task in undone:
        btn = types.InlineKeyboardButton(
            text=f"⬜ {i+1}. {task['text'][:30]}",
            callback_data=f"done_{i}"
        )
        markup.add(btn)

    bot.send_message(
        message.chat.id,
        "✅ Qaysi vazifa bajarildi?",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith("done_"))
def mark_done(call):
    user_id = call.from_user.id
    task_index = int(call.data.split("_")[1])
    tasks = get_tasks(user_id)

    if task_index < len(tasks):
        tasks[task_index]['done'] = True
        task_text = tasks[task_index]['text']
        bot.answer_callback_query(call.id, "✅ Bajarildi!")
        bot.edit_message_text(
            f"✅ *{task_text}* — bajarildi!",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )


@bot.message_handler(func=lambda m: m.text == "❌ O'chirish")
def delete_task_prompt(message):
    user_id = message.from_user.id
    tasks = get_tasks(user_id)

    if not tasks:
        bot.send_message(message.chat.id, "📭 O'chiriladigan vazifa yo'q.", reply_markup=main_keyboard())
        return

    markup = types.InlineKeyboardMarkup()
    for i, task in enumerate(tasks):
        status = "✅" if task['done'] else "⬜"
        btn = types.InlineKeyboardButton(
            text=f"{status} {i+1}. {task['text'][:30]}",
            callback_data=f"del_{i}"
        )
        markup.add(btn)

    bot.send_message(message.chat.id, "❌ Qaysi vazifani o'chirasiz?", reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data.startswith("del_"))
def delete_task(call):
    user_id = call.from_user.id
    task_index = int(call.data.split("_")[1])
    tasks = get_tasks(user_id)

    if task_index < len(tasks):
        removed = tasks.pop(task_index)
        bot.answer_callback_query(call.id, "🗑 O'chirildi!")
        bot.edit_message_text(
            f"🗑 *{removed['text']}* — o'chirildi.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )


@bot.message_handler(func=lambda m: m.text == "🗑 Hammasini tozalash")
def clear_all_prompt(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Ha, tozala", callback_data="clear_yes"),
        types.InlineKeyboardButton("❌ Yo'q", callback_data="clear_no")
    )
    bot.send_message(message.chat.id, "⚠️ Barcha vazifalar o'chirilsinmi?", reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data in ["clear_yes", "clear_no"])
def clear_all(call):
    if call.data == "clear_yes":
        user_tasks[call.from_user.id] = []
        bot.answer_callback_query(call.id, "🗑 Tozalandi!")
        bot.edit_message_text("✅ Barcha vazifalar o'chirildi.", call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "Bekor qilindi.")
        bot.edit_message_text("❌ Bekor qilindi.", call.message.chat.id, call.message.message_id)


if __name__ == "__main__":
    print("🤖 Bot ishga tushdi...")
    print("Toxtatish uchun: Ctrl+C")
    bot.infinity_polling()