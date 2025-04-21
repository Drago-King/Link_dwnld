import logging
import yt_dlp
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Supported platforms
SUPPORTED_SERVICES = ["youtube", "facebook", "instagram", "tiktok"]

# Multilingual messages
LANG = {
    "en": {
        "welcome": "Welcome to the *Cinematic Link Whisperer*.\nSend a media link from YouTube, Facebook, Instagram, TikTok...",
        "invalid": "That doesn't look like a supported media link.",
        "processing": "Analyzing your link in cinematic silence...",
        "again": "Send another media link.",
        "audio": "Fetching cinematic audio (coming soon).",
        "cancel": "Operation cancelled.",
        "failed": "Failed to extract details. Try a different link."
    }
}

def t(lang_code, key):
    return LANG.get(lang_code, LANG["en"]).get(key, "")

def detect_lang(update: Update):
    return update.effective_user.language_code or "en"

# Inline buttons
def build_main_menu(lang):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Extract Again", callback_data="extract_again"),
            InlineKeyboardButton("Get Audio", callback_data="get_audio"),
        ],
        [InlineKeyboardButton("Cancel", callback_data="cancel")]
    ])

# Media info extractor using yt_dlp
def extract_media_info(url):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "noplaylist": True,
        "forcejson": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title"),
            "duration": info.get("duration_string"),
            "thumbnail": info.get("thumbnail"),
            "url": info.get("webpage_url"),
            "platform": info.get("extractor_key", "Unknown")
        }

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = detect_lang(update)
    await update.message.reply_text(t(lang, "welcome"), parse_mode="Markdown")

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = detect_lang(update)
    text = update.message.text.strip()

    if "http" not in text:
        await update.message.reply_text(t(lang, "invalid"))
        return

    await update.message.reply_text(t(lang, "processing"), reply_markup=build_main_menu(lang))

    try:
        data = extract_media_info(text)
        platform = data["platform"].lower()

        if platform not in SUPPORTED_SERVICES:
            await update.message.reply_text(f"{platform} is not yet supported.")
            return

        response = (
            f"*Platform:* {platform.title()}\n"
            f"*Title:* {data['title']}\n"
            f"*Duration:* {data['duration']}\n"
            f"[Thumbnail]({data['thumbnail']})"
        )
        await update.message.reply_photo(photo=data["thumbnail"], caption=response, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Extraction error: {e}")
        await update.message.reply_text(t(lang, "failed"))

# Callback buttons
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = detect_lang(update)
    query = update.callback_query
    await query.answer()

    if query.data == "extract_again":
        await query.edit_message_text(t(lang, "again"))
    elif query.data == "get_audio":
        await query.edit_message_text(t(lang, "audio"))
    elif query.data == "cancel":
        await query.edit_message_text(t(lang, "cancel"))
    else:
        await query.edit_message_text("Unknown action.")

# Run the bot
def main():
    app = ApplicationBuilder().token("7518970885:AAFH6uxaE8gZUaK_zlkY3Z9nqDICD8Og8P0").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_buttons))

    logger.info("Bot is live. Accepting links...")
    app.run_polling()

if __name__ == "__main__":
    main()
