import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# === Logger ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# === Bot Token ===
BOT_TOKEN = "7808185967:AAHOpUEoxP3kM_Rg7BtrMWdD0icpdkt8U9M"

# === Storage for file statistics ===
file_stats = {}  # {chat_id: {"name": str, "count": int, "size": int}}

# === Start Command ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your File Tracker Bot 📊")

# === Handle File Messages ===
async def handle_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.message or update.channel_post
        if not message:
            logging.info("No message received")
            return

        file_obj = None
        file_type = None

        if message.document:
            file_obj = message.document
            file_type = "Document"
        elif message.video:
            file_obj = message.video
            file_type = "Video"
        elif message.audio:
            file_obj = message.audio
            file_type = "Audio"
        elif message.photo:
            file_obj = message.photo[-1]
            file_type = "Image"

        if not file_obj:
            logging.info(f"🟡 Not a file: {message.text or 'non-text content'}")
            return

        file_size = file_obj.file_size or 0
        chat_id = message.chat.id
        chat_title = message.chat.title or message.chat.username or "Private Chat"

        if chat_id not in file_stats:
            file_stats[chat_id] = {"name": chat_title, "count": 0, "size": 0}

        file_stats[chat_id]["count"] += 1
        file_stats[chat_id]["size"] += file_size

        logging.info(f"✅ Processed {file_type} in {chat_title}: {file_size} bytes")

    except Exception as e:
        logging.error(f"❌ Error processing file: {e}")

# === Stats Command ===
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not file_stats:
        await update.message.reply_text("No file data recorded yet.")
        return

    msg = "📊 *File Stats Summary:*\n\n"
    for chat_id, stat in file_stats.items():
        size_mb = stat["size"] / (1024 * 1024)
        msg += f"📁 *{stat['name']}*\n"
        msg += f"  • Files: {stat['count']}\n"
        size_mb = float(size_mb)  # ensure it's a float
        gb = int(size_mb // 1000)
        mb = int(size_mb % 1000)
        kb = int((size_mb - int(size_mb)) * 1000)

        msg += f"  • Total Size: {gb} GB\n"
        msg += f"  • Total Size: {mb} MB\n"
        msg += f"  • Total Size: {kb} KB\n\n"


    await update.message.reply_text(msg, parse_mode="Markdown")

# === Main ===
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))

    # ✅ Correct filters for PTB v20+
    media_filters = (
    filters.Document.ALL |
    filters.PHOTO |
    filters.VIDEO |
    filters.AUDIO
)


    app.add_handler(MessageHandler(media_filters, handle_files))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
