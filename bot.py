import telebot
import threading
import queue
from telebot import types

# 🔐 Directly paste your bot token here (only for local use/testing)
TOKEN = "7454690320:AAGhkSHdml4zXQfI5dBRgl4X9JULxLuH0Fs"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# 🔁 Quality options
QUALITY_OPTIONS = ["720p", "480p", "360p"]

# 📥 Download queue
download_queue = queue.Queue()

# ✅ Function to check YouTube link and send options
def linkCheck(bot, message):
    text = message.text.strip()
    if "youtube" in text.lower() or "youtu.be" in text.lower():
        videoURL = text
        markup = types.InlineKeyboardMarkup()
        for quality in QUALITY_OPTIONS:
            btn = types.InlineKeyboardButton(text=quality, callback_data=f"{quality}#{videoURL}")
            markup.add(btn)
        bot.reply_to(message, "Select the video quality to download:", reply_markup=markup)
    else:
        bot.reply_to(message, "❌ Please send a valid YouTube link.")

# 🚀 Download worker thread (simulated)
def download_worker(bot, download_queue):
    while True:
        try:
            msg, videoURL, quality = download_queue.get()
            bot.send_message(msg.chat.id, f"⬇️ Downloading video from:\n{videoURL}\nQuality: {quality}")
            import time
            time.sleep(5)  # Simulate download
            bot.send_message(msg.chat.id, "✅ Download completed!")
            download_queue.task_done()
        except Exception as e:
            print(f"❌ Error: {e}")

# 🟢 /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "Hello, I'm a <b>Simple YouTube Downloader! 👋</b>\n\nSend me a YouTube link or use /help."
    )

# 🟢 /help command
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(
        message,
        "<b>Send a YouTube link and choose quality.</b>\n\n<i>Developer: @X_NexusWraith_X</i>",
        disable_web_page_preview=True
    )

# 🔗 Handle all messages for link checking
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    linkCheck(bot, message)

# 🎯 Handle inline button callback
@bot.callback_query_handler(func=lambda call: any(call.data.startswith(q) for q in QUALITY_OPTIONS))
def handle_callback_query(call):
    try:
        data = call.data.split("#")
        if len(data) != 2:
            bot.answer_callback_query(call.id, "❌ Invalid data.")
            return
        quality, videoURL = data
        bot.answer_callback_query(call.id, f"🎞 Selected {quality}")
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception as e:
            print("Can't delete:", e)

        download_queue.put((call.message, videoURL, quality))
        queue_pos = download_queue.qsize()

        if queue_pos <= 1:
            bot.send_message(call.message.chat.id, "🟢 Added to queue.")
        else:
            bot.send_message(call.message.chat.id, f"🟡 Position in queue: #{queue_pos}")
    except Exception as ex:
        print("Callback error:", ex)

# 🚧 Start the download worker
download_thread = threading.Thread(target=download_worker, args=(bot, download_queue), daemon=True)
download_thread.start()

print("🚀 TelegramYTDLBot is running...")
bot.infinity_polling()
