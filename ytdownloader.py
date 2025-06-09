import os
import yt_dlp

def download(bot, message, quality, videoURL):
    msg = bot.send_message(message.chat.id, "⏬ Downloading started...")

    ydl_opts = {
        'format': f'bestvideo[height={quality[:-1]}]+bestaudio/best/best',
        'outtmpl': f'{videoURL[-10:]}.mp4',
        'merge_output_format': 'mp4',
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([videoURL])

        filename = f"{videoURL[-10:]}.mp4"

        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video, caption="✅ Video downloaded successfully.")
        os.remove(filename)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error:\n<code>{str(e)}</code>", parse_mode="HTML")
