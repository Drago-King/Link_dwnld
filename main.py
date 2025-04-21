import os
import yt_dlp
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

import logging
logging.basicConfig(level=logging.INFO)

# Load token from env
TOKEN = os.getenv("BOT_TOKEN")

SUPPORTED_SERVICES = ["youtube", "facebook", "instagram", "tiktok"]

def extract_media_info(url):
    ydl_opts = {"quiet": True, "skip_download": True, "noplaylist": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title"),
            "duration": info.get("duration_string"),
            "thumbnail": info.get("thumbnail"),
            "platform": info.get("extractor_key", "Unknown")
        }

def build_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Extract Again", callback_data="extract_again"),
         InlineKeyboardButton("Get Audio", callback_data="get_audio")],
        [InlineKeyboardButton("Cancel", callback_data="cancel")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send a YouTube, Instagram, Facebook, or TikTok link!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "http" not in url:
        await update.message.reply_text("That's not a valid link.")
        return

    await update.message.reply_text("Processing...", reply_markup=build_menu())

    try:
        data = extract_media_info(url)
        caption = f"*Platform:* {data['platform']}\\n*Title:* {data['title']}\\n*Duration:* {data['duration']}"
        await update.message.reply_photo(photo=data["thumbnail"], caption=caption, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text("Failed to extract link.")
        logging.error(e)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "extract_again":
        await q.edit_message_text("Send another link.")
    elif q.data == "get_audio":
        await q.edit_message_text("Coming soon.")
    elif q.data == "cancel":
        await q.edit_message_text("Cancelled.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.run_polling()

if __name__ == "__main__":
    main()
