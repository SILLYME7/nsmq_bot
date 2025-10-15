import feedparser
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio
import requests
import time

# ==============================
# 🔧 BOT CONFIGURATION (CHANGE THESE)
# ==============================

BOT_TOKEN = "8262088439:AAFzNhiQUXTljuv0SDpsAq-1GZx1pxspMBk"
CHANNEL_USERNAME = "@VoiceOfKNUST"  # Example: @NSMQUpdates
RSS_FEED_URL = "https://rss.app/feeds/TUtRboBGqpdbDR7P.xml"  # From RSS.app (linked to NSMQ Facebook)
ADMIN_ID = 1181012452  # Your Telegram user ID
CHECK_INTERVAL = 300  # seconds (every 5 minutes)

# ==============================
# 🔒 FORCE JOIN CHECK
# ==============================

async def is_user_member(user_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id={CHANNEL_USERNAME}&user_id={user_id}"
    response = requests.get(url).json()
    try:
        status = response["result"]["status"]
        return status in ["member", "administrator", "creator"]
    except:
        return False

# ==============================
# 🧠 NSMQ UPDATES
# ==============================

latest_post_link = None  # To track the most recent post

async def nsmq_updates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not await is_user_member(user_id):
        await update.message.reply_text(
            f"🚫 You must join our NSMQ Updates Channel first!\n\n👉 Join here: {CHANNEL_USERNAME}\n\nThen try again."
        )
        return

    try:
        feed = feedparser.parse(RSS_FEED_URL)
        if not feed.entries:
            await update.message.reply_text("😕 No new updates found.")
            return

        message = "🧠 *Latest NSMQ Updates:*\n\n"
        for entry in feed.entries[:5]:
            message += f"• [{entry.title}]({entry.link})\n"

        await update.message.reply_text(
            message,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

    except Exception as e:
        await update.message.reply_text("❌ Error fetching updates.")
        print(e)

# ==============================
# 👋 START COMMAND
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if not await is_user_member(user_id):
        await update.message.reply_text(
            f"👋 Welcome! Before using this bot, please join our official NSMQ channel:\n\n👉 {CHANNEL_USERNAME}\n\nThen tap /start again."
        )
        return

    welcome_text = (
        "🎉 *Welcome to the NSMQ Live Updates Bot!*\n\n"
        "Stay informed with the latest updates from the National Science & Maths Quiz.\n"
        "Use /updates anytime to view the most recent posts."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

# ==============================
# 🤖 AUTO POSTER FUNCTION
# ==============================

async def auto_post_updates(application: Application):
    global latest_post_link
    while True:
        try:
            feed = feedparser.parse(RSS_FEED_URL)
            if feed.entries:
                latest_entry = feed.entries[0]
                if latest_entry.link != latest_post_link:
                    latest_post_link = latest_entry.link

                    message = f"🧠 *New NSMQ Update!*\n\n[{latest_entry.title}]({latest_entry.link})"
                    await application.bot.send_message(
                        chat_id=CHANNEL_USERNAME,
                        text=message,
                        parse_mode="Markdown",
                        disable_web_page_preview=True
                    )
                    print(f"✅ Posted new update: {latest_entry.title}")

        except Exception as e:
            print(f"⚠️ Auto-posting error: {e}")

        await asyncio.sleep(CHECK_INTERVAL)

# ==============================
# 🚀 RUN THE BOT
# ==============================

async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("updates", nsmq_updates))

    print("✅ NSMQ Bot is running — enforcing channel join and auto-posting new updates...")

    # Start background auto-posting task
    asyncio.create_task(auto_post_updates(app))

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
