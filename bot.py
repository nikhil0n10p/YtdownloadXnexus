import telebot
import threading
from checker import linkCheck
from myqueues import download_queue, download_worker

# ✅ Your bot token here
TOKEN = "7454690320:AAGhkSHdml4zXQfI5dBRgl4X9JULxLuH0Fs"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello, I'm a <b>YouTube Downloader Bot! 👋</b>\nSend a YouTube link to start.")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "<b>Send a YouTube link and choose the quality.</b>\nDeveloper: @dev00111", disable_web_page_preview=True)

@bot.message_handler(func=lambda m: True)
def handle_link(message):
    linkCheck(bot, message)

@bot.callback_query_handler(func=lambda call: "#" in call.data)
def handle_callback(call):
    try:
        quality, url = call.data.split("#")
        bot.answer_callback_query(call.id, f"Selected {quality}")
        bot.delete_message(call.message.chat.id, call.message.message_id)

        download_queue.put((call.message, url, quality))
        pos = download_queue.qsize()
        msg = f"🟢 Download started." if pos == 1 else f"⏳ Queued at position #{pos}"
        bot.send_message(call.message.chat.id, msg)

    except Exception as e:
        bot.send_message(call.message.chat.id, f"Error: {e}")

threading.Thread(target=download_worker, args=(bot, download_queue), daemon=True).start()

print("✅ Bot is running...")
bot.infinity_polling()
