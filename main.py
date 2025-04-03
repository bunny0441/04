import telebot
import os
import time
import random
import threading
from flask import Flask

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Get dynamic port from Render environment
PORT = int(os.environ.get("PORT", 5000))

# Run Flask in a separate thread
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=PORT), daemon=True).start()

# Get bot token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Replace with your private channel IDs
CHANNELS = ["-1002408073109", "-1002568559251"]  # Use real channel IDs

# Storage for all forwarded posts
collection_list = []
new_posts = []

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# Function to send messages in batches of 10 every 3 hours
def send_scheduled_messages():
    while True:
        selected_posts = []

        if new_posts:
            selected_posts = new_posts[:10]
            del new_posts[:10]
        else:
            if len(collection_list) >= 10:
                selected_posts = random.sample(collection_list, 10)
            elif collection_list:
                selected_posts = collection_list[:10]

        for message in selected_posts:
            send_message_to_channels(message)

        print("✅ Sent 10 messages. Next batch in 3 hours...")
        time.sleep(3 * 60 * 60)  # Wait 3 hours before sending the next batch

# Start the scheduled message thread
threading.Thread(target=send_scheduled_messages, daemon=True).start()

# Function to send messages to all channels
def send_message_to_channels(message):
    for channel in CHANNELS:
        if isinstance(message, str):
            bot.send_message(channel, message)
        elif isinstance(message, telebot.types.Message):
            if message.photo:
                bot.send_photo(channel, message.photo[-1].file_id, caption=message.caption)
            elif message.video:
                bot.send_video(channel, message.video.file_id, caption=message.caption)
            elif message.document:
                bot.send_document(channel, message.document.file_id, caption=message.caption)
            elif message.audio:
                bot.send_audio(channel, message.audio.file_id, caption=message.caption)
            elif message.voice:
                bot.send_voice(channel, message.voice.file_id, caption=message.caption)

# Handle text messages
@bot.message_handler(content_types=['text'])
def handle_text(message):
    collection_list.append(message.text)
    new_posts.append(message.text)
    bot.reply_to(message, "📩 Added to collection & priority list!")

# Handle media files
@bot.message_handler(content_types=['photo', 'video', 'document', 'audio', 'voice'])
def handle_media(message):
    collection_list.append(message)
    new_posts.append(message)
    bot.reply_to(message, "📩 Added to collection & priority list!")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello! Forward messages here. The bot will send 10 posts every 3 hours, prioritizing new ones. If no new posts, it will send 10 random posts.")

print("Bot is running...")
bot.polling()
