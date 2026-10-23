import telebot
from telebot import types
import os, json
from flask import Flask, request
import threading

# 👇👇👇 শুধু এই একটা লাইনে তোমার টোকেন বসাও 👇👇👇
BOT_TOKEN = "8994880058:AAGEmXc194MPKwMvWPdt-8ONqyL3L9TZOHQ"

WALL_ID = "f31e3c4789a1"
MY_UID = "8088665721"
TIMEWALL_ID = "adcd643fca590c56"
DB_FILE = "users.json"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

def load_db():
    if not os.path.exists(DB_FILE): return {}
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return {}
def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

@app.route('/')
def home(): return "Rocket Bot 24/7 Running! OK"

@app.route('/postback/timewall')
def timewall_postback():
    user_id = request.args.get('uid') or request.args.get('subID1')
    amount = request.args.get('amount') or request.args.get('currencyAmount') or "0"
    print(f"Timewall hit: {request.args}")
    try:
        points = int(float(amount))
        if points <= 0: points = 10
        db = load_db()
        if user_id in db:
            db[user_id]["balance"] += points
            save_db(db)
            try: bot.send_message(int(user_id), f"✅ Task Complete! 🔥 {points} Points যোগ হয়েছে!")
            except: pass
        return "OK", 200
    except Exception as e:
        print(e)
        return "OK", 200

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    db = load_db()
    if user_id not in db:
        db[user_id] = {"balance": 0, "name": message.from_user.first_name}
        save_db(db)
    bitcowall_link = f"https://bitcowall.com/w/{WALL_ID}?uid={MY_UID}&subid={user_id}"
    timewall_link = f"https://timewall.io/offerwall/{TIMEWALL_ID}?uid={user_id}&subID1={user_id}"
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("🎯 Task Wall 1", url=bitcowall_link))
    markup.add(types.InlineKeyboardButton("🔥 Task Wall 2", url=timewall_link))
    markup.add(types.InlineKeyboardButton("⭐ My Points", callback_data="balance"))
    bot.send_message(message.chat.id, f"🚀 Rocket Micro Jobs\n\nহ্যালো {message.from_user.first_name}!\nTask করে Points জমাও 👇", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = str(call.from_user.id); db = load_db()
    if call.data == "balance":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"⭐ তোমার Points: {db.get(user_id, {}).get('balance',0)}")

def run_flask():
    app.run(host='0.0.0.0', port=8000)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("Bot Starting...")
    bot.infinity_polling(skip_pending=True)
