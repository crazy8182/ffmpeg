#!/usr/bin/env python3
"""Main entry point for the FFmpeg Processor Bot"""

import asyncio
import os
from aiohttp import web

from pyrogram import idle
from bot import bot, LOGGER, MONGO_URI, DATABASE_NAME, OWNER_ID, db
from bot.utils.db_handler import Database


# ---------------- WEB SERVER ---------------- #

async def health(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", 8080))

    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    LOGGER.info(f"Web server started on port {port}")


# ---------------- MAIN BOT ---------------- #

async def main():
    """Main function to start the bot"""

    global db

    # Start web server for Koyeb health check
    await start_web_server()

    # Initialize database
    if MONGO_URI:
        try:
            from bot.utils.db_handler import init_database
            await init_database(MONGO_URI, DATABASE_NAME)
            LOGGER.info("Connected to MongoDB successfully")
        except Exception as e:
            LOGGER.error(f"Failed to connect to MongoDB: {e}")

    # Import handlers
    from bot.handlers import commands, callbacks, file_handler, message_handler

    # Start the bot
    await bot.start()

    bot_info = await bot.get_me()
    LOGGER.info(f"Bot started: @{bot_info.username}")

    # Notify owner
    try:
        await bot.send_message(
            OWNER_ID,
            "🚀 <b>FFmpeg Processor Bot Started!</b>\n\n"
            f"<b>Bot:</b> @{bot_info.username}\n"
            "<b>Status:</b> Online ✅"
        )
    except Exception as e:
        LOGGER.warning(f"Could not notify owner: {e}")

    await idle()

    # Cleanup
    await bot.stop()
    LOGGER.info("Bot stopped")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
