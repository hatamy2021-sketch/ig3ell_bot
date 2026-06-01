import os
import telebot
from telebot import types
from flask import Flask, request
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8851801825:AAEz8FdkDCfEw8Nshto9HJumzWLEKmnc2vQ")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "6204956765"))
ADMIN_USERNAME = "@ig3ell"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://ig3ell-bot.onrender.com")
CARD_NUMBER = "6037-XXXX-XXXX-XXXX"
CARD_OWNER = "نام صاحب کارت"

PRODUCTS = {
    "premium": {"items": [
        {"id": "p1m",  "name": "۱ ماه پرمیوم",  "price": "35,000 تومان"},
        {"id": "p3m",  "name": "۳ ماه پرمیوم",  "price": "90,000 تومان"},
        {"id": "p6m",  "name": "۶ ماه پرمیوم",  "price": "160,000 تومان"},
        {"id": "p12m", "name": "۱۲ ماه پرمیوم", "price": "280,000 تومان"},
    ]},
    "stars": {"items": [
        {"id": "s50",   "name": "۵۰ استارز",   "price": "15,000 تومان"},
        {"id": "s100",  "name": "۱۰۰ استارز",  "price": "28,000 تومان"},
        {"id": "s250",  "name": "۲۵۰ استارز",  "price": "65,000 تومان"},
        {"id": "s500",  "name": "۵۰۰ استارز",  "price": "120,000 تومان"},
        {"id": "s1000", "name": "۱۰۰۰ استارز", "price": "220,000 تومان"},
    ]}
}

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
pending_orders = {}

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("⭐ خرید پرمیوم"), types.KeyboardButton("🌟 خرید استارز"), types.KeyboardButton("📞 پشتیبانی"), types.KeyboardButton("ℹ️ راهنما"))
    return markup

def back_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🔙 بازگشت به منو"))
    return markup

@bot.message_handler(commands=["start"])
def start(message):
    name = message.from_user.first_name or "کاربر"
    bot.send_message(message.chat.id, f"سلام {name} عزیز! 👋\n\nبه ربات فروش پرمیوم و استارز ig3ell خوش اومدی 🎉\n\n🔹 پرمیوم تلگرام\n🔹 استارز تلگرام\n\nاز منو زیر انتخاب کن 👇", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "⭐ خرید پرمیوم")
def buy_premium(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for item in PRODUCTS["premium"]["items"]:
        markup.add(types.InlineKeyboardButton(f"{item['name']} — {item['price']}", callback_data=f"buy_{item['id']}"))
    bot.send_message(message.chat.id, "⭐ *پرمیوم تلگرام*\n\nپلن مورد نظر رو انتخاب کن:", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🌟 خرید استارز")
def buy_stars(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for item in PRODUCTS["stars"]["items"]:
        markup.add(types.InlineKeyboardButton(f"{item['name']} — {item['price']}", callback_data=f"buy_{item['id']}"))
    bot.send_message(message.chat.id, "🌟 *استارز تلگرام*\n\nتعداد مورد نظر رو انتخاب کن:", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def product_selected(call):
    product_id = call.data[4:]
    product = None
    for cat in PRODUCTS.values():
        for item in cat["items"]:
            if item["id"] == product_id:
                product = item
                break
    if not product:
        return
    pending_orders[call.from_user.id] = {"product": product, "step": "waiting_username", "time": datetime.now().strftime("%Y-%m-%d %H:%M")}
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, f"✅ انتخاب شد: *{product['name']}* — {product['price']}\n\n📱 یوزرنیم حسابی که باید بهش داده بشه رو بفرست:\n\nمثال: `@username`", parse_mode="Markdown", reply_markup=back_menu())

@bot.message_handler(func=lambda m: m.from_user.id in pending_orders and pending_orders[m.from_user.id].get("step") == "waiting_username")
def get_username(message):
    if message.text == "🔙 بازگشت به منو":
        pending_orders.pop(message.from_user.id, None)
        return start(message)
    order = pending_orders[message.from_user.id]
    order["target_username"] = message.text
    order["step"] = "waiting_payment"
    product = order["product"]
    bot.send_message(message.chat.id, f"📋 *جزئیات سفارش:*\n\n🛒 {product['name']}\n💰 {product['price']}\n👤 حساب: `{message.text}`\n\n━━━━━━━━━━━━━━\n💳 *اطلاعات پرداخت:*\n\nشماره کارت: `{CARD_NUMBER}`\nبه نام: {CARD_OWNER}\n\n⚠️ بعد از پرداخت *تصویر رسید* رو بفرست.", parse_mode="Markdown")

@bot.message_handler(content_types=["photo"], func=lambda m: m.from_user.id in pending_orders and pending_orders[m.from_user.id].get("step") == "waiting_payment")
def get_receipt(message):
    order = pending_orders[message.from_user.id]
    product = order["product"]
    user = message.from_user
    markup_admin = types.InlineKeyboardMarkup(row_width=2)
    markup_admin.add(types.InlineKeyboardButton("✅ تأیید", callback_data=f"confirm_{user.id}"), types.InlineKeyboardButton("❌ رد", callback_data=f"reject_{user.id}"))
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"🔔 *سفارش جدید!*\n\n👤 [{user.first_name}](tg://user?id={user.id})\n🆔 `{user.id}`\n🛒 {product['name']}\n💰 {product['price']}\n👤 حساب هدف: `{order['target_username']}`\n🕐 {order['time']}", parse_mode="Markdown", reply_markup=markup_admin)
    bot.send_message(message.chat.id, "✅ رسید دریافت شد!\n⏳ در کمتر از ۳۰ دقیقه پردازش میشه.", reply_markup=main_menu())
    order["step"] = "submitted"

@bot.callback_query_handler(func=lambda c: c.data.startswith("confirm_"))
def confirm_order(call):
    if call.from_user.id != ADMIN_ID:
        return
    user_id = int(call.data[8:])
    bot.send_message(user_id, "🎉 *سفارش شما تأیید شد!*\nممنون از خریدت 🙏", parse_mode="Markdown", reply_markup=main_menu())
    bot.answer_callback_query(call.id, "✅ تأیید شد")
    bot.edit_message_caption("✅ تأیید شد", call.message.chat.id, call.message.message_id)
    pending_orders.pop(user_id, None)

@bot.callback_query_handler(func=lambda c: c.data.startswith("reject_"))
def reject_order(call):
    if call.from_user.id != ADMIN_ID:
        return
    user_id = int(call.data[7:])
    bot.send_message(user_id, f"❌ سفارش تأیید نشد.\nبا پشتیبانی تماس بگیر: {ADMIN_USERNAME}", reply_markup=main_menu())
    bot.answer_callback_query(call.id, "❌ رد شد")
    bot.edit_message_caption("❌ رد شد", call.message.chat.id, call.message.message_id)
    pending_orders.pop(user_id, None)

@bot.message_handler(func=lambda m: m.text == "📞 پشتیبانی")
def support(message):
    bot.send_message(message.chat.id, f"📞 *پشتیبانی ig3ell*\n\n👤 {ADMIN_USERNAME}\n⏰ ۹ صبح تا ۱۲ شب", parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "ℹ️ راهنما")
def guide(message):
    bot.send_message(message.chat.id, "ℹ️ *راهنمای خرید*\n\n1️⃣ محصول رو انتخاب کن\n2️⃣ یوزرنیم حساب هدف رو بفرست\n3️⃣ مبلغ رو واریز کن\n4️⃣ رسید رو بفرست\n5️⃣ صبر کن تا تأیید بشه ✅\n\n❓ سوال؟ " + ADMIN_USERNAME, parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🔙 بازگشت به منو")
def back(message):
    pending_orders.pop(message.from_user.id, None)
    start(message)

@bot.message_handler(func=lambda m: True)
def unknown(message):
    bot.send_message(message.chat.id, "از منو زیر انتخاب کن 👇", reply_markup=main_menu())

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def index():
    return "ig3ell bot is running! ✅"

@app.route("/set_webhook")
def set_webhook():
    bot.remove_webhook()
    result = bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    if result:
        return f"✅ Webhook set successfully!"
    else:
        return "❌ Failed to set webhook"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
