#!/usr/bin/env python3
# ============================================================
#  YouTube Downloader Bot — Railway deployment (Webhook mode)
# ============================================================
import os
import threading
import telebot
import yt_dlp
from flask import Flask, request

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise SystemExit("❌ BOT_TOKEN رو توی Railway Environment Variables تنظیم کن!")

# Railway automatically sets RAILWAY_PUBLIC_DOMAIN
_railway_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
if not WEBHOOK_URL and _railway_domain:
    WEBHOOK_URL = f"https://{_railway_domain}"

bot = telebot.TeleBot(BOT_TOKEN)

_YDL_BASE = {
    "quiet": True,
    "no_warnings": True,
}
COOKIES_PATH = os.path.join(os.path.dirname(__file__), "cookies.txt")
if os.path.exists(COOKIES_PATH):
    _YDL_BASE["cookiefile"] = COOKIES_PATH
    print("✅ cookies.txt پیدا شد")


def download(url, mode="video"):
    out = "/tmp/%(title).40s.%(ext)s"
    opts = dict(_YDL_BASE)
    opts["outtmpl"] = out
    if mode == "audio":
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}
        ]
    else:
        opts["format"] = "best[ext=mp4]/best"
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


@bot.message_handler(commands=["start", "help"])
def start(m):
    bot.reply_to(
        m,
        "سلام! 👋\n"
        "لینک یوتیوب بفرست تا دانلود کنم.\n\n"
        "/audio — حالت صدا (MP3)\n"
        "/video — حالت ویدیو (MP4)",
    )


user_modes = {}


@bot.message_handler(commands=["audio"])
def audio_mode(m):
    user_modes[m.chat.id] = "audio"
    bot.reply_to(m, "🎵 حالت صدا فعال شد. لینک یوتیوب بفرست.")


@bot.message_handler(commands=["video"])
def video_mode(m):
    user_modes[m.chat.id] = "video"
    bot.reply_to(m, "🎬 حالت ویدیو فعال شد. لینک یوتیوب بفرست.")


@bot.message_handler(func=lambda m: m.text and "youtu" in m.text)
def handle(m):
    url = m.text.strip()
    mode = user_modes.get(m.chat.id, "video")
    bot.reply_to(m, "در حال دانلود... ⏳")

    def do_download():
        try:
            path = download(url, mode)
            if mode == "audio":
                mp3_path = os.path.splitext(path)[0] + ".mp3"
                if os.path.exists(mp3_path):
                    path = mp3_path
            with open(path, "rb") as f:
                if mode == "audio":
                    bot.send_audio(m.chat.id, f)
                else:
                    bot.send_video(m.chat.id, f)
            os.remove(path)
        except Exception as e:
            bot.reply_to(m, f"❌ خطا: {e}")

    threading.Thread(target=do_download, daemon=True).start()


app = Flask(__name__)


@app.route("/")
def home():
    return "✅ YouTube Bot is running on Railway.", 200


@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_data = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_data)
        bot.process_new_updates([update])
        return "", 200
    return "Invalid content type", 403


def setup_webhook():
    if not WEBHOOK_URL:
        print("⚠️  WEBHOOK_URL مشخص نیست — بدون webhook اجرا می‌شه")
        return
    full_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
    print(f"🔗 تنظیم webhook: {full_url}")
    bot.remove_webhook()
    if bot.set_webhook(url=full_url):
        print("✅ Webhook تنظیم شد")
    else:
        print("❌ خطا در تنظیم webhook")


if __name__ == "__main__":
    setup_webhook()
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Server روی پورت {port}")
    app.run(host="0.0.0.0", port=port)
