#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
    Telegram bot that search sounds in www.myinstants.com
    Author: Luiz Francisco Rodrigues da Silva <luizfrdasilva@gmail.com>
"""

import datetime
import logging
from uuid import uuid4
import json

from telegram import InlineQueryResultVoice, Message, Chat
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from telegram.ext.dispatcher import run_async
from telegram.contrib.botan import Botan

from myinstants import search_instants

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

LOGGER = logging.getLogger(__name__)

# Load config file
with open('config.json') as config_file:
    CONFIGURATION = json.load(config_file)

# Create a Botan tracker object
BOTAN = Botan(CONFIGURATION["botan_token"])


def start(bot, update):
    """Start command handler"""
    bot.sendMessage(update.message.chat_id, text='Hi!\nYou can use this bot in any chat, just type '
                                                 '@myinstantsbot query message\nEnjoy!')


def help_command(bot, update):
    """Help command"""
    bot.sendMessage(update.message.chat_id, text='This bot search sounds in myinstants.com\n'
                                                 'You can use it in any chat, just type '
                                                 '@myinstantsbot query message')


@run_async
def inlinequery(bot, update):
    """Inline query handler"""
    query = update.inline_query.query
    inline_results = list()

    results = search_instants(query)

    for instant in results:
        inline_results.append(InlineQueryResultVoice(id=uuid4(),
                                                     title=instant["text"],
                                                     voice_url=instant["url"]))

    bot.answerInlineQuery(update.inline_query.id, results=inline_results[:40])


def track(update):
    """Print to console and log activity with Botan.io"""
    message = Message(uuid4(),
                      update.inline_query.from_user,
                      datetime.datetime.now(),
                      Chat(uuid4(), "private"))

    BOTAN.track(message,
                update.inline_query.query)

    LOGGER.info("New message\nFrom: %s\nText: %s",
                update.inline_query.from_user,
                update.inline_query.query)


def error_handler(update, error):
    """Error Handler"""
    LOGGER.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Main function"""
    # Create the Updater and pass it your bot's token.
    updater = Updater(CONFIGURATION["telegram_token"])

    # on different commands - answer in Telegram
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("help", help_command))

    # on noncommand i.e message - echo the message on Telegram
    updater.dispatcher.add_handler(InlineQueryHandler(inlinequery))
    updater.dispatcher.add_handler(InlineQueryHandler(lambda bot, update: track(update)), group=1)

    # log all errors
    updater.dispatcher.add_error_handler(lambda bot, update, error: error_handler(update, error))

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
