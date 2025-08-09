# Dev 2.0 - Telegram Media Management Bot

A lightweight Telegram bot designed to track, manage, and analyze media files across chats and channels. Dev 2.0 has been managing media collections since 2018, providing real-time statistics and file management capabilities.

## 🚀 Features

- **📊 Media Tracking**: Automatically tracks documents, videos, audio files, and images
- **📈 Statistics Dashboard**: Real-time file count and storage usage analytics
- **🗑️ File Management**: Delete files by ID or filename with automatic stats updates
- **🔄 Refresh System**: Validates file availability and cleans up deleted files
- **💾 In-Memory Storage**: Fast, lightweight data storage without external dependencies
- **📱 Multi-Chat Support**: Works in private chats, groups, and channels

## 📋 Prerequisites

- Python 3.7 or higher
- A Telegram Bot Token from [@BotFather](https://t.me/botfather)
- `python-telegram-bot` library

## 🛠 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/fafawds67685da/Telegram_bot.git
   cd Telegram_bot
   ```

2. **Install required dependencies**
   ```bash
   pip install python-telegram-bot
   ```

3. **Configure your bot token**
   
   Open `bot.py` and replace the token on line 18:
   ```python
   BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
   ```

4. **Run the bot**
   ```bash
   python bot.py
   ```

## 🤖 Available Commands

### Core Commands
- `/start` - Initialize the bot and display welcome message
- `/stats` - Display comprehensive media statistics across all chats
- `/refresh` - Validate file availability and remove deleted files from tracking

### File Management Commands
- `/report_deletion <file_id>` - Report a file as deleted and update statistics
- `/delete_by_name <filename>` - Delete file records by exact filename match

### Usage Examples
```bash
/stats                           # Get global media statistics
/report_deletion BAADBAADqwAD    # Report file deletion by ID
/delete_by_name example.pdf      # Delete by exact filename
/refresh                         # Clean up deleted files
```

## 📊 Statistics Display

The bot provides detailed analytics including:
- **Total file count** across all monitored chats
- **Storage usage** in GB, MB, and KB
- **Per-chat tracking** with chat names and individual statistics
- **Real-time updates** as files are added or removed

Example stats output:
```
📊 Global File Stats Summary:

  • Total Files: 1,247
  • Total Size: 15 GB
  • Total Size: 432 MB
  • Total Size: 891 KB
```

## 🔧 Technical Details

### Supported File Types
- **Documents**: PDF, DOCX, TXT, ZIP, and other document formats
- **Videos**: MP4, AVI, MKV, and other video formats
- **Audio**: MP3, WAV, OGG, and other audio formats
- **Images**: JPG, PNG, GIF, and other image formats

### Data Storage Structure
The bot uses efficient in-memory storage with two main data structures:

```python
# Chat-level statistics
file_stats = {
    chat_id: {
        "name": "Chat Name",
        "count": 150,        # Number of files
        "size": 1048576      # Total size in bytes
    }
}

# Individual file tracking
file_index = {
    file_id: {
        "chat_id": -1001234567890,
        "size": 2048576,
        "filename": "document.pdf"
    }
}
```

### Error Handling
- Comprehensive logging for all operations
- Graceful handling of deleted files
- Protection against invalid file IDs
- Safe arithmetic operations to prevent negative stats

## 🚀 Deployment

### Local Development
```bash
python bot.py
```

### Production Deployment

#### Using systemd (Linux)
Create `/etc/systemd/system/telegram-media-bot.service`:
```ini
[Unit]
Description=Telegram Media Management Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/Telegram_bot
ExecStart=/usr/bin/python3 /path/to/Telegram_bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable telegram-media-bot
sudo systemctl start telegram-media-bot
sudo systemctl status telegram-media-bot
```

#### Using Docker
Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY bot.py .
RUN pip install python-telegram-bot

CMD ["python", "bot.py"]
```

Build and run:
```bash
docker build -t telegram-media-bot .
docker run -d --restart unless-stopped telegram-media-bot
```

#### Using screen (Simple)
```bash
screen -S telegram-bot
python bot.py
# Press Ctrl+A then D to detach
```

## ⚠️ Important Security Notes

1. **Bot Token Security**: 
   - Never commit your bot token to version control
   - Use environment variables in production:
   ```python
   import os
   BOT_TOKEN = os.getenv("BOT_TOKEN", "your-default-token")
   ```

2. **Data Persistence**: 
   - Current implementation uses in-memory storage
   - Data is lost when bot restarts
   - Consider adding database integration for production use

## 🔧 Customization Options

### Modify File Types
To track additional file types, update the media filter:
```python
media_filters = (
    filters.Document.ALL |
    filters.PHOTO |
    filters.VIDEO |
    filters.AUDIO |
    filters.Sticker |        # Add stickers
    filters.ANIMATION        # Add GIFs
)
```

### Add Database Persistence
Replace in-memory storage with SQLite:
```python
import sqlite3

def init_db():
    conn = sqlite3.connect('media_bot.db')
    # Create tables and return connection
    return conn
```

### Custom Logging
Enhance logging configuration:
```python
logging.basicConfig(
    filename='media_bot.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filemode='a'
)
```

## 🐛 Troubleshooting

### Common Issues

**Bot not responding:**
- Verify the bot token is correct
- Check internet connectivity
- Ensure bot is added to the chat/channel

**Files not being tracked:**
- Check if file types are in the media_filters
- Verify bot has permission to read messages
- Check logs for error messages

**Stats showing incorrect data:**
- Run `/refresh` to clean up deleted files
- Restart bot to reset in-memory storage
- Check for permission issues

### Log Analysis
The bot logs all operations. Look for these patterns:
- `✅ Processed` - Successful file tracking
- `❌ Error` - Failed operations
- `🔄 Refresh` - Cleanup operations

## 🛡️ Bot Permissions Required

For optimal functionality, ensure your bot has these permissions:
- Read messages
- Send messages  
- Access to file information
- Download files (for refresh validation)

## 📈 Performance Considerations

- **Memory Usage**: Grows with the number of tracked files
- **API Limits**: Telegram has rate limits for file downloads
- **Refresh Operation**: Can be slow with many files
- **Concurrent Access**: Bot handles one operation at a time

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. Feel free to modify and distribute according to your needs.

## 🙏 Acknowledgments

- Built with the excellent [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) library
- Inspired by the need for efficient media management in Telegram chats
- Managing Dev's media collection since 2018

---

**💡 Tip**: For production use, consider implementing database persistence and proper environment variable management for enhanced security and reliability.

**🔗 Support**: If you encounter issues, check the troubleshooting section or create an issue in the repository.
