from telebot import TeleBot, types
import json
import os
import time
import threading
from database.db import save_file

BOT_TOKEN = "7920918778:AAFF4MDkYX4qBpuyXyBgcuCssLa6vjmTN1c"
uploader_bot = TeleBot(BOT_TOKEN, threaded=True)

ADMINS = [123456789]
DB_PATH = "data/db.json"

if not os.path.exists(DB_PATH):
    with open(DB_PATH, "w") as f:
        json.dump({}, f)

def save_data(file_id, caption):
    with open(DB_PATH, "r") as f:
        db = json.load(f)
    db[file_id] = caption
    with open(DB_PATH, "w") as f:
        json.dump(db, f)

@uploader_bot.message_handler(commands=["start"])
def start_handler(message):
    uploader_bot.send_message(message.chat.id, "سلام! لطفاً فایل ویدیویی خود را ارسال کنید.")

@uploader_bot.message_handler(content_types=["video"])
def video_handler(message):
    if message.from_user.id not in ADMINS:
        return uploader_bot.send_message(message.chat.id, "دسترسی ندارید.")
    file_id = message.video.file_id
    uploader_bot.send_message(message.chat.id, "لطفاً کاور (در صورت وجود) یا 'ندارم' را بفرستید.")
    uploader_bot.register_next_step_handler(message, process_cover, file_id)

def process_cover(message, file_id):
    if message.content_type == "photo":
        cover_id = message.photo[-1].file_id
    elif message.text and message.text.strip().lower() == "ندارم":
        cover_id = None
    else:
        return uploader_bot.send_message(message.chat.id, "لطفاً عکس یا 'ندارم' را بفرستید.")
    uploader_bot.send_message(message.chat.id, "لطفاً کپشن مورد نظر را ارسال کنید.")
    uploader_bot.register_next_step_handler(message, process_caption, file_id, cover_id)

def process_caption(message, file_id, cover_id):
    caption = message.text or ""
    save_data(file_id, caption)

    checker_link = f"https://t.me/TofLinkBot?start={file_id}"

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("مشاهده", url=checker_link))
    
    if cover_id:
        uploader_bot.send_photo(message.chat.id, cover_id, caption=caption + "\n\n@hottof | تُفِ داغ", reply_markup=markup)
    else:
        uploader_bot.send_message(message.chat.id, caption + "\n\n@hottof | تُفِ داغ", reply_markup=markup)
