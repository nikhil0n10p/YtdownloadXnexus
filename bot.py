import os
import threading
import queue
import telebot
from telebot import types
from dotenv import load_dotenv

# Load environment variables (ensure you have a .env file with TOKEN variable)
load_dotenv()

# Get your bot token from the environment variable
TOKEN = os.getenv("7454690320:AAGhkSHdml4zXQfI5dBRgl4X9JULxLuH0Fs")  # Update your .env file variable name to TOKEN
if not TOKEN:
    raise ValueError("No TOKEN found. Please set your Telegram bot token in the .env file.")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# --- Global settings and inline options ---
# Example video quality options (adjust as needed)
QUALITY_OPTIONS = ["720p", "480p", "360p"]

# Create a download queue
download_queue = queue.Queue()


# --- Functions that were previously in external modules ---

def linkCheck(bot, message):
    """
    Checks the message for a valid YouTube URL.
    If valid, sends a set of inline buttons for quality selection.
    """
    text = message.text.strip()
    if "youtube" in text.lower() or "youtu.be" in text.lower():
        videoURL = text  # In a real scenario, more validation could occur here.
        # Build inline keyboard with quality options
        markup = types.InlineKeyboardMarkup()
        for quality in QUALITY_OPTIONS:
            # Callback data contains the quality and the video URL separated by a hash.
            btn = types.InlineKeyboardButton(text=quality, callback_data=f"{quality}#{videoURL}")
            markup.add(btn)
        bot.reply_to(message, "Select the video quality to download:", reply_markup=markup)
    else:
        bot.reply_to(message, "Please send a valid YouTube URL.")


def download_worker(bot, download_queue):
    """
    Background worker thread that processes download tasks from the queue.
    For each task, it simulates the download process.
    """
    while True:
        try:
            msg, videoURL, quality = download_queue.get()
            bot.send_message(msg.chat.id, f"Downloading video from:\n{videoURL}\nQuality: {quality}")
            
            # Simulate a download process.
            # Replace this block with the actual download code as needed.
            import time
            time.sleep(5)  # Simulate time-consuming download
            
            bot.send_message(msg.chat.id, "Download completed!")
            download_queue.task_done()
        except Exception as e:
            print(f"Error in download_worker: {e}")


# --- Bot Command Handlers ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "Hello, I'm a <b>Simple Youtube Downloader! 👋</b>\n\nTo get started, just type the /help command."
    )


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(
        message,
        (
            "<b>Just send your YouTube link and select the video quality.</b> 😉\n\n"
            "<i>Developer: @dev00111</i>\n"
            "<i>Source: <a href='https://github.com/hansanaD/TelegramYTDLBot'>TelegramYTDLBot</a></i>"
        ),
        disable_web_page_preview=True
    )


@bot.message_handler(func=lambda m: True)
def handle_message(message):
    """
    Handler for every message sent to the bot.
    Delegates link checking to the linkCheck() function.
    """
    linkCheck(bot, message)


@bot.callback_query_handler(func=lambda call: any(call.data.startswith(q) for q in QUALITY_OPTIONS))
def handle_callback_query(call):
    """
    Callback query handler for the inline buttons.
    Splits the callback data to get the selected quality and video URL,
    then adds a task to the download queue.
    """
    try:
        data = call.data.split("#")
        if len(data) != 2:
            bot.answer_callback_query(call.id, "Invalid callback data.")
            return
        
        quality, videoURL = data
        
        bot.answer_callback_query(call.id, f"Selected {quality} quality for download.")
        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except Exception as e:
            print("Error deleting message:", e)

        # Add task to the download queue
        download_queue.put((call.message, videoURL, quality))
        queue_position = download_queue.qsize()

        if queue_position <= 1:
            bot.send_message(call.message.chat.id, "Download has been added to the queue.")
        else:
            bot.send_message(call.message.chat.id, f"Download has been added to the queue at position #{queue_position}.")

    except Exception as ex:
        print("Error in handling callback query:", ex)


# --- Start background download thread ---
download_thread = threading.Thread(target=download_worker, args=(bot, download_queue), daemon=True)
download_thread.start()

print("TelegramYTDLBot is running...\n")
bot.infinity_polling()
