#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
    Telegram bot that search sounds in www.myinstants.com
    Author: Luiz Francisco Rodrigues da Silva <luizfrdasilva@gmail.com>
"""
import os
import logging
from uuid import uuid4


from telegram import InlineQueryResultVoice, Update
from telegram.ext import Application, CommandHandler, ContextTypes, InlineQueryHandler

from myinstants import search_instants

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, _: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    await update.message.reply_text(
        "Hi!\nYou can use this bot in any chat, just type "
        "@myinstantsbot query message\nEnjoy!"
    )


async def help_command(update: Update, _: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    await update.message.reply_text(
        "This bot search sounds in myinstants.com\n"
        "You can use it in any chat, just type "
        "@myinstantsbot query message"
    )


async def info_command(update: Update, _: ContextTypes.DEFAULT_TYPE):
    """Info command"""
    await update.message.reply_text(
        "Source code: https://www.github.com/heylouiz/myinstantsbot\n"
        "Developer: @heylouiz"
    )


async def inline_query(update: Update, _: ContextTypes.DEFAULT_TYPE):
    """Inline query handler"""
    query = update.inline_query.query

    if not query:
        return

    inline_results = list()
    results = search_instants(query)

    for instant in results:
        inline_results.append(
            InlineQueryResultVoice(
                id=str(uuid4()), title=instant["text"], voice_url=instant["url"]
            )
        )

    await update.inline_query.answer(inline_results[:40])


def error_handler(update, context):
    """Error Handler"""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Main function"""
    if "TELEGRAM_TOKEN" not in os.environ:
        logger.error(
            f"Missing environment variable TELEGRAM_TOKEN! See README.md file for more information."
        )
        return 1

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.environ.get("TELEGRAM_TOKEN")).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info_command))

    # on inline queries - show corresponding inline results
    application.add_handler(InlineQueryHandler(inline_query))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
