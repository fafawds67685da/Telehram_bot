import logging
import tempfile
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.error import TelegramError

# === Logger ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = "7808185967:AAHOpUEoxP3kM_Rg7BtrMWdD0icpdkt8U9M"
bot = Bot(token=BOT_TOKEN)

# === In-Memory Storage ===
file_stats = {}  # {chat_id: {"name": str, "count": int, "size": int}}
file_index = {}  # {file_id: {"chat_id": int, "size": int, "filename": str}}

# === Start Command ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi there, I am Dev 2.0, managing Dev's media collection since 2018!")

# === Handle File Messages ===
async def handle_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.message or update.channel_post
        if not message:
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
            return

        file_size = file_obj.file_size or 0
        file_id = file_obj.file_id
        filename = getattr(file_obj, 'file_name', f"{file_type}_{file_id}")
        chat_id = message.chat.id
        chat_title = message.chat.title or message.chat.username or "Private Chat"

        if chat_id not in file_stats:
            file_stats[chat_id] = {"name": chat_title, "count": 0, "size": 0}

        file_stats[chat_id]["count"] += 1
        file_stats[chat_id]["size"] += file_size

        file_index[file_id] = {"chat_id": chat_id, "size": file_size, "filename": filename}

        logging.info(f"✅ Processed {file_type} in {chat_title}: {file_size} bytes")

    except Exception as e:
        logging.error(f"❌ Error processing file: {e}")

# === Delete by file ID ===
async def report_deletion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("Please provide a file ID to report deletion.")
            return

        file_id = context.args[0]

        if file_id not in file_index:
            await update.message.reply_text(f"⚠️ File ID {file_id} not found.", parse_mode="Markdown")
            return

        record = file_index.pop(file_id)
        chat_id = record["chat_id"]
        size = record["size"]

        if chat_id in file_stats:
            file_stats[chat_id]["count"] = max(0, file_stats[chat_id]["count"] - 1)
            file_stats[chat_id]["size"] = max(0, file_stats[chat_id]["size"] - size)

        await update.message.reply_text(f"🗑️ File ID {file_id} deleted and stats updated.", parse_mode="Markdown")

    except Exception as e:
        logging.error(f"❌ Error reporting deletion: {e}")
        await update.message.reply_text(f"Error: {e}")

# === Delete by file name ===
async def delete_by_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("Please provide the filename to delete.")
            return

        filename = " ".join(context.args)
        deleted = False

        for file_id, info in list(file_index.items()):
            if info.get("filename") == filename:
                chat_id = info["chat_id"]
                size = info["size"]

                file_stats[chat_id]["count"] = max(0, file_stats[chat_id]["count"] - 1)
                file_stats[chat_id]["size"] = max(0, file_stats[chat_id]["size"] - size)

                del file_index[file_id]
                deleted = True

                await update.message.reply_text(f"🗑️ File '{filename}' deleted and stats updated.")
                break

        if not deleted:
            await update.message.reply_text(f"⚠️ File named '{filename}' not found.")

    except Exception as e:
        logging.error(f"❌ Error deleting by name: {e}")
        await update.message.reply_text(f"Error: {e}")

# === Refresh Command (checks if file can be downloaded) ===
async def refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        deleted_files = 0

        for file_id in list(file_index.keys()):
            try:
                file = await bot.get_file(file_id)
                # Try downloading to memory to detect real deletion
                await file.download_to_memory()

            except TelegramError:
                record = file_index.pop(file_id)
                chat_id = record["chat_id"]
                size = record["size"]

                if chat_id in file_stats:
                    file_stats[chat_id]["count"] = max(0, file_stats[chat_id]["count"] - 1)
                    file_stats[chat_id]["size"] = max(0, file_stats[chat_id]["size"] - size)

                deleted_files += 1

        await update.message.reply_text(f"🔄 Refresh complete. Removed {deleted_files} deleted file(s).")

    except Exception as e:
        logging.error(f"❌ Error during refresh: {e}")
        await update.message.reply_text(f"Error during refresh: {e}")

# === Stats Command ===
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not file_stats:
        await update.message.reply_text("No file data recorded yet.")
        return

    total_files = sum(stat["count"] for stat in file_stats.values())
    total_size = sum(stat["size"] for stat in file_stats.values())

    size_mb = total_size / (1024 * 1024)
    gb = int(size_mb // 1000)
    mb = int(size_mb % 1000)
    kb = int((size_mb - int(size_mb)) * 1000)

    msg = (
        "📊 *Global File Stats Summary:*\n\n"
        f"  • Total Files: {total_files}\n"
        f"  • Total Size: {gb} GB\n"
        f"  • Total Size: {mb} MB\n"
        f"  • Total Size: {kb} KB\n"
    )

    await update.message.reply_text(msg, parse_mode="Markdown")

# === Main ===
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("report_deletion", report_deletion))
    app.add_handler(CommandHandler("delete_by_name", delete_by_name))
    app.add_handler(CommandHandler("refresh", refresh))  # ✅ Updated

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