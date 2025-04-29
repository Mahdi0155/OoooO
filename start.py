from flask import Flask, request
from uploader import uploader_bot
from checker import checker_bot
from telebot import types

WEBHOOK_BASE = "https://ooooo-lrww.onrender.com"
UPLOADER_TOKEN = "7920918778:AAFF4MDkYX4qBpuyXyBgcuCssLa6vjmTN1c"
CHECKER_TOKEN = "7679592392:AAHi7YBXB3wmCdsrzTnyURwyljDRvMckoVY"

app = Flask(__name__)

@app.route(f"/{UPLOADER_TOKEN}", methods=["POST"])
def webhook_uploader():
    json_data = request.get_data().decode("utf-8")
    update = types.Update.de_json(json_data)
    uploader_bot.process_new_updates([update])
    return "OK"

@app.route(f"/{CHECKER_TOKEN}", methods=["POST"])
def webhook_checker():
    json_data = request.get_data().decode("utf-8")
    update = types.Update.de_json(json_data)
    checker_bot.process_new_updates([update])
    return "OK"

@app.route("/")
def index():
    return "Both Bots Running"

if __name__ == "__main__":
    uploader_bot.remove_webhook()
    checker_bot.remove_webhook()
    uploader_bot.set_webhook(url=f"{WEBHOOK_BASE}/{UPLOADER_TOKEN}")
    checker_bot.set_webhook(url=f"{WEBHOOK_BASE}/{CHECKER_TOKEN}")
    app.run(host="0.0.0.0", port=10000)
