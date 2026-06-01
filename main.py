import os
import telebot
from flask import Flask, request

# ========== تنظیمات از محیط ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set in environment variables")

ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "").rstrip('/')  # بدون اسلش آخر
WEBHOOK_PATH = "/webhook"   # مسیر ثابت و ساده

# ========== راه‌اندازی ==========
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ========== دستورات ربات ==========
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "✅ ربات با موفقیت کار می‌کند!\n\n"
        "برای خرید از دکمه‌های زیر استفاده کنید.",
        reply_markup=main_menu()
    )

def main_menu():
    from telebot.types import ReplyKeyboardMarkup, KeyboardButton
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("⭐ خرید پرمیوم"),
        KeyboardButton("🌟 خرید استارز"),
        KeyboardButton("📞 پشتیبانی"),
        KeyboardButton("ℹ️ راهنما")
    )
    return markup

@bot.message_handler(func=lambda m: m.text == "⭐ خرید پرمیوم")
def buy_premium(message):
    bot.send_message(message.chat.id, "لطفاً از منوی زیر انتخاب کنید (فعلاً نمونه):\nپرمیوم ۱ ماهه - ۳۵ هزار تومان")

@bot.message_handler(func=lambda m: m.text == "🌟 خرید استارز")
def buy_stars(message):
    bot.send_message(message.chat.id, "استارز: ۵۰ تا ۱۵ هزار تومان")

@bot.message_handler(func=lambda m: m.text == "📞 پشتیبانی")
def support(message):
    bot.send_message(message.chat.id, "پشتیبانی: @ig3ell")

@bot.message_handler(func=lambda m: m.text == "ℹ️ راهنما")
def guide(message):
    bot.send_message(message.chat.id, "راهنما:\n1. محصول را انتخاب کنید\n2. یوزرنوم بفرستید\n3. رسید بفرستید")

@bot.message_handler(func=lambda m: True)
def unknown(message):
    bot.send_message(message.chat.id, "از دکمه‌های زیر استفاده کنید.", reply_markup=main_menu())

# ========== Webhook Flask ==========
@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_str = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_str)
        if update is not None:
            bot.process_new_updates([update])
        return "OK", 200
    else:
        return "Unsupported Media Type", 415

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    if not WEBHOOK_URL:
        return "WEBHOOK_URL is not set", 500
    url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
    try:
        bot.delete_webhook()  # حذف قبلی
        bot.set_webhook(url=url)
        return f"✅ Webhook successfully set to {url}", 200
    except Exception as e:
        return f"❌ Error: {str(e)}", 500

@app.route('/', methods=['GET'])
def index():
    return "🤖 Telegram bot is running!"

# ========== اجرای محلی (برای تست) ==========
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
