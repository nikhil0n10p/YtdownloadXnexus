import re
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

def linkCheck(bot, message):
    # Extract YouTube link using regex
    linkFilter = re.compile(r'(https?://[^\s]+)')
    userLinks = re.findall(linkFilter, message.text)

    yt_link = []
    for link in userLinks:
        if 'youtube.com' in link or 'youtu.be' in link:
            yt_link.append(link)

    if yt_link:
        videoURL = yt_link[0]
        qualityChecker(bot=bot, message=message, videoURL=videoURL)
    else:
        bot.reply_to(message, "❌ No valid YouTube link found!")

def qualityChecker(bot, message, videoURL):
    loadingMsg = bot.reply_to(message, "🔍 Looking for available qualities...")

    ydl_opts = {'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(videoURL, download=False)
        except Exception as e:
            bot.reply_to(message, f"❌ Error:\n<code>{str(e)}</code>", parse_mode="HTML")
            return

    title = info.get('title', 'Untitled Video')
    formats = info.get('formats', [])

    urlList = []
    for f in formats:
        if f.get('ext') == 'mp4' and f.get('height') and f.get('url'):
            height = f['height']
            size_bytes = f.get('filesize') or f.get('filesize_approx')
            size_str = f"{round(size_bytes / (1024 * 1024), 1)} MB" if size_bytes else "Unknown"
            urlList.append([f"{height}p", size_str, f['url']])

    if not urlList:
        bot.reply_to(message, "❌ No downloadable MP4 streams found.")
        return

    global showList
    showList = []
    markup = InlineKeyboardMarkup()
    for count, item in enumerate(urlList[:6], 1):  # show only top 6 qualities
        q, size, _ = item
        showList.append(f"{q}#{videoURL}")
        markup.add(InlineKeyboardButton(text=f"{q} ({size})", callback_data=f"{q}#{videoURL}"))

    bot.delete_message(loadingMsg.chat.id, loadingMsg.message_id)
    bot.reply_to(message, f"<b>{title}</b>\nSelect quality to download:", reply_markup=markup, parse_mode="HTML")
