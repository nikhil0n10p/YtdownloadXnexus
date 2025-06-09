import telebot
import threading
from checker import linkCheck  # ✅ using existing checker.py
from myqueues import download_queue, download_worker  # ✅ using existing myqueues.py

# 🔐 Paste your bot token directly (safe only for testing)
TOKEN = "7454690320:AAGhkSHdml4zXQfI5dBRgl4X9JULxLuH0Fs"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
                 "Hello, I'm a <b>Simple YouTube Downloader Bot! 👋</b>\n\nJust send a YouTube link to get started.")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message,
                 "<b>Send a YouTube link and choose the quality.</b>\n\n<i>Developer: @dev00111</i>",
                 disable_web_page_preview=True)

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    linkCheck(bot, message)  # ✅ This calls your checker.py logic

@bot.callback_query_handler(func=lambda call: "#" in call.data)
def handle_callback(call):
    try:
        quality, video_url = call.data.split("#")
        bot.answer_callback_query(call.id, f"🎥 Selected: {quality}")
        bot.delete_message(call.message.chat.id, call.message.message_id)

        download_queue.put((call.message, video_url, quality))  # ✅ Send to queue
        pos = download_queue.qsize()

        if pos <= 1:
            bot.send_message(call.message.chat.id, "✅ Download started.")
        else:
            bot.send_message(call.message.chat.id, f"⏳ Added to queue at position #{pos}.")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Error: {e}")

# 🔁 Start download thread
threading.Thread(target=download_worker, args=(bot, download_queue), daemon=True).start()

print("🚀 Bot is running...")
bot.infinity_polling()
