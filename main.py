import os
from flask import Flask, request
import telebot

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "سلام! ربات کار می‌کنه ✅")

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.get_json():
        update = telebot.types.Update.de_json(request.get_json())
        bot.process_new_updates([update])
    return "OK", 200

@app.route('/')
def index():
    return "Bot is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
