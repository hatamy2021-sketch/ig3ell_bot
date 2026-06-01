import os
import requests
from flask import Flask, request

TOKEN = os.environ.get("BOT_TOKEN")
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')
        if text == '/start':
            url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
            requests.post(url, json={'chat_id': chat_id, 'text': '✅ ربات فعال است!'})
    return 'OK', 200

@app.route('/')
def index():
    return 'Bot is running'
