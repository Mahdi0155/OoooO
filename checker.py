from flask import Flask, request
from telebot import TeleBot, types
import json
import os
import threading
import time

checker_app = Flask(__name__)
checker_app = app
BOT_TOKEN = "7679592392:AAHi7YBXB3wmCdsrzTnyURwyljDRvMckoVY"
bot = TeleBot(BOT_TOKEN, threaded=True)

CHANNELS = [
    {"id": "@channel1", "name": "کانال اول"},
    {"id": "@channel2", "name": "کانال دوم"}
]
DB_PATH = "data/db.json"
CHECK_TIMEOUT = 30

if not os.path.exists(DB_PATH):
    with open(DB_PATH, "w") as f:
        json.dump({}, f)

def get_caption(file_id):
    with open(DB_PATH, "r") as f:
        db = json.load(f)
    return db.get(file_id)

def check_membership(user_id):
    not_joined = []
    for ch in CHANNELS:
        try:
            member = bot.get_chat_member(ch["id"], user_id)
            if member.status in ["left", "kicked"]:
                not_joined.append(ch)
        except:
            not_joined.append(ch)
    return not_joined

def delete_after(chat_id, message_id, delay):
    time.sleep(delay)
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass

@bot.message_handler(commands=['start'])
def handle_start(message):
    args = message.text.split(" ")
    if len(args) < 2:
        return bot.send_message(message.chat.id, "درخواست نامعتبر است.")
    file_id = args[1]
    not_joined = check_membership(message.from_user.id)
    if not_joined:
        markup = types.InlineKeyboardMarkup()
        for ch in not_joined:
            markup.add(types.InlineKeyboardButton(ch["name"], url=f"https://t.me/{ch['id'].replace('@', '')}"))
        markup.add(types.InlineKeyboardButton("بررسی عضویت", callback_data=f"check_{file_id}"))
        bot.send_message(message.chat.id, "لطفاً ابتدا در کانال‌های زیر عضو شوید:", reply_markup=markup)
    else:
        send_file(message.chat.id, file_id)

def send_file(chat_id, file_id):
    caption = get_caption(file_id)
    if not caption:
        return bot.send_message(chat_id, "فایل یافت نشد.")
    bot.send_message(chat_id, "این ویدیو پس از ۳۰ ثانیه حذف می‌گردد.")
    sent = bot.send_video(chat_id, file_id, caption=caption)
    threading.Thread(target=delete_after, args=(chat_id, sent.message_id, CHECK_TIMEOUT)).start()

@bot.callback_query_handler(func=lambda call: call.data.startswith("check_"))
def handle_check(call):
    file_id = call.data.split("_")[1]
    not_joined = check_membership(call.from_user.id)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    if not_joined:
        markup = types.InlineKeyboardMarkup()
        for ch in not_joined:
            markup.add(types.InlineKeyboardButton(ch["name"], url=f"https://t.me/{ch['id'].replace('@', '')}"))
        markup.add(types.InlineKeyboardButton("بررسی عضویت", callback_data=f"check_{file_id}"))
        bot.send_message(call.message.chat.id, "لطفاً ابتدا در کانال‌های زیر عضو شوید:", reply_markup=markup)
    else:
        send_file(call.message.chat.id, file_id)

@checker_app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_data = request.get_data().decode("utf-8")
    update = types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return "ok"

@checker_app.route('/')
def index():
    return "Checker Bot Running"

bot.remove_webhook()
bot.set_webhook(url="https://ooooo-lrww.onrender.com/" + BOT_TOKEN)
