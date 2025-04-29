from flask import Flask, request
from telebot import TeleBot, types
import json
import os
import threading
import time

uploader_app = Flask(__name__)
BOT_TOKEN = "7920918778:AAFM8JNgk4cUhn0_P81hkB1Y0cYifjdSt-M"
bot = TeleBot(BOT_TOKEN, threaded=True)

ADMIN_IDS = [7189616405, 6387942633, 5459406429]
FILE_DB = "data/db.json"
FORCE_CHANNELS = []  # بررسی عضویت اینجا انجام نمی‌شود، فقط در چکر ربات است
CHECKER_BOT_USERNAME = "TofLinkBot"
CHANNEL_TAG = "@hottof | تُفِ داغ"

user_state = {}

if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists(FILE_DB):
    with open(FILE_DB, "w") as f:
        json.dump({}, f)

def save_file(file_id, caption):
    with open(FILE_DB, "r") as f:
        db = json.load(f)
    db[file_id] = caption
    with open(FILE_DB, "w") as f:
        json.dump(db, f)

@bot.message_handler(commands=['start'])
def handle_start(message):
    if message.from_user.id in ADMIN_IDS:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("پست", "سوپر")
        bot.send_message(message.chat.id, "به پنل خوش آمدید:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "پست")
def handle_post(message):
    bot.send_message(message.chat.id, "لطفاً ویدیو را فوروارد کنید.")
    user_state[message.chat.id] = {"mode": "post"}

@bot.message_handler(func=lambda m: m.text == "سوپر")
def handle_super(message):
    bot.send_message(message.chat.id, "لطفاً ویدیو را ارسال کنید.")
    user_state[message.chat.id] = {"mode": "super", "step": "video"}

@bot.message_handler(content_types=['video'])
def handle_video(message):
    if message.chat.id not in user_state:
        return
    state = user_state[message.chat.id]
    if state.get("mode") == "post":
        user_state[message.chat.id]["file_id"] = message.video.file_id
        ask_caption(message)
    elif state.get("mode") == "super" and state.get("step") == "video":
        user_state[message.chat.id]["file_id"] = message.video.file_id
        user_state[message.chat.id]["step"] = "cover"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("ندارم", callback_data="no_cover"))
        bot.send_message(message.chat.id, "لطفاً کاور ارسال کنید یا روی 'ندارم' بزنید.", reply_markup=markup)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    state = user_state.get(message.chat.id)
    if state and state.get("mode") == "super" and state.get("step") == "cover":
        user_state[message.chat.id]["thumb_id"] = message.photo[-1].file_id
        user_state[message.chat.id]["step"] = "caption"
        bot.send_message(message.chat.id, "لطفاً کپشن را وارد کنید:")

@bot.message_handler(func=lambda m: True)
def handle_caption(m):
    state = user_state.get(m.chat.id)
    if not state:
        return
    if state.get("mode") == "post" and "file_id" in state:
        user_state[m.chat.id]["caption"] = m.text
        file_id = state["file_id"]
        save_file(file_id, m.text)
        bot.send_video(m.chat.id, file_id, caption=m.text)
        user_state.pop(m.chat.id)
    elif state.get("mode") == "super" and state.get("step") == "caption":
        file_id = state["file_id"]
        thumb_id = state.get("thumb_id")
        caption = m.text + f"\n\n{CHANNEL_TAG}"
        save_file(file_id, caption)
        markup = types.InlineKeyboardMarkup()
        link = f"https://t.me/{CHECKER_BOT_USERNAME}?start={file_id}"
        markup.add(types.InlineKeyboardButton("مشاهده", url=link))
        bot.send_photo(m.chat.id, thumb_id, caption=caption, reply_markup=markup) if thumb_id else bot.send_message(m.chat.id, caption, reply_markup=markup)
        user_state.pop(m.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "no_cover")
def no_cover_handler(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    user_state[call.message.chat.id]["thumb_id"] = None
    user_state[call.message.chat.id]["step"] = "caption"
    bot.send_message(call.message.chat.id, "لطفاً کپشن را وارد کنید:")

@uploader_app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_data = request.get_data().decode("utf-8")
    update = types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return "ok"

@uploader_app.route('/')
def index():
    return "Uploader Bot Running"

bot.remove_webhook()
bot.set_webhook(url="https://ooooo-lrww.onrender.com/" + BOT_TOKEN)
