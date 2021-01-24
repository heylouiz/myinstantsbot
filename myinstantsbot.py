#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
    Telegram bot that search sounds in www.myinstants.com
    Author: Luiz Francisco Rodrigues da Silva <luizfrdasilva@gmail.com>
"""
import os
import datetime
import logging
from uuid import uuid4
import json
import tempfile

from contextlib import suppress

from telegram import InlineQueryResultVoice, Message, Chat
from telegram.ext import Updater, Filters, InlineQueryHandler, CommandHandler, MessageHandler, ConversationHandler

from myinstants import search_instants, upload_instant, NameAlreadyExistsException, FileSizeException, HTTPErrorException, InvalidPageErrorException, LoginErrorException

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

LOGGER = logging.getLogger(__name__)

# States of upload machine state
SOUND, NAME, CONFIRMATION = range(3)

def start(update, context):
    """Start command handler"""
    update.message.reply_text('Hi!\nYou can use this bot in any chat, just type '
                              '@myinstantsbot query message\nEnjoy!')


def help_command(update, context):
    """Help command"""
    update.message.reply_text('This bot search sounds in myinstants.com\n'
                              'You can use it in any chat, just type '
                              '@myinstantsbot query message')

def info_command(update, context):
    """Info command"""
    update.message.reply_text('Source code: https://www.github.com/heylouiz/myinstantsbot\n'
                              'Developer: @heylouiz')

def inlinequery(update, context):
    """Inline query handler"""
    query = update.inline_query.query
    inline_results = list()

    results = search_instants(query)

    for instant in results:
        inline_results.append(InlineQueryResultVoice(id=uuid4(),
                                                     title=instant["text"],
                                                     voice_url=instant["url"]))

    update.inline_query.answer(inline_results[:40])

def error_handler(update, context):
    """Error Handler"""
    LOGGER.warning('Update "%s" caused error "%s"', update, context.error)


def remove_sound_file(filename):
    with suppress(FileNotFoundError):
        os.remove(filename)


"""  ------------------------------------- """
"""  Upload Instant State Machine Handlers """
"""  ------------------------------------- """
def upload_start(update, context):
    """First state of the upload instant state machine"""
    update.message.reply_text("Ok, you want to upload a sound to Myinstants.\n"
                              "First, send me the sound you want to upload, it can be a voice message or an audio file, "
                              "as long it is smaller than 300kb.\n\n"
                              "Use the command /cancel to abort the upload.")
    return SOUND

def get_voice(update, context):
    """Handler for a voice message"""
    if update.message.voice.file_size > 307200: # 300kb
        update.message.reply_text("Error: File must be smaller than 300kb, has {}\n\nAborting...".format(update.message.voice.file_size/1024))
        return ConversationHandler.END

    voice_file = update.message.voice.get_file()

    filename = tempfile.mkstemp(suffix=".mp3")[1]
    voice_file.download(filename)

    context.user_data['filename'] = filename

    update.message.reply_text("Nice, everything is fine with your audio!\n"
                              "Now send me a name for it, this name will appear on myinstants site "
                              "and you will search by this name when you want to send it.")
    return NAME

def get_audio(update, context):
    """Handler for a audio file message"""
    if update.message.audio.file_size > 307200: # 300kb
        update.message.reply_text("Error: File must be smaller than 300kb, has {}\n\nAborting...".format(update.message.audio.file_size/1024))
        return ConversationHandler.END

    audio_file = update.message.audio.get_file()
    filename = tempfile.mkstemp(suffix=".mp3")[1]
    audio_file.download(filename)

    context.user_data['filename'] = filename

    update.message.reply_text("Nice, everything is fine with your audio!\n"
                              "Now send me a name for it, this name will appear on myinstants site "
                              "and you will search by this name when you want to send it.")

    return NAME

def get_name(update, context):
    """Handler for instant name"""
    context.user_data['name'] = update.message.text

    update.message.reply_text("Your instant name will be \"{}\".\nAre you sure about it? Send Yes, No or /cancel".format(context.user_data['name']))

    return CONFIRMATION

def name_confirmation_and_upload(update, context):
    """Handler to confirm name"""
    if update.message.text not in ["Yes", "No"]:
        update.message.reply_text("Invalid confirmation word!\nTry again or send /cancel")
        return CONFIRMATION

    if update.message.text == "No":
        update.message.reply_text("Ok, let's pick another name.\nSend me a new name or send /cancel to abort.")
        return NAME

    if update.message.text == "Yes":
        update.message.reply_text("All right, your audio will be uploaded with the name \"{}\".".format(context.user_data['name']))

    try:
        url = upload_instant(context.user_data['name'], context.user_data['filename'])
    except NameAlreadyExistsException:
        update.message.reply_text("Error: There is already an Instant with this name!\nSend me another name or /cancel to abort.")
        return NAME
    except FileSizeException:
        update.message.reply_text("Error: File is bigger than 300kb!\nSend me another audio or /cancel to abort.")
        return SOUND
    except (HTTPErrorException, InvalidPageErrorException):
        update.message.reply_text("Error: Failed to send Instant, try again later.\nIf the problem persist talk to the developer @heylouiz")
        remove_sound_file(context.user_data['filename'])
        context.user_data.clear()
        return ConversationHandler.END
    except LoginErrorException:
        update.message.reply_text("Error: Login failed, try again later.\nIf the problem persist talk to the developer @heylouiz")
        remove_sound_file(context.user_data['filename'])
        context.user_data.clear()
        return ConversationHandler.END
    except Exception as e:
        LOGGER.exception("Unexpected error!")
        update.message.reply_text("Error: Unknown error!\nInform the developer @heylouiz")
        remove_sound_file(context.user_data['filename'])
        context.user_data.clear()
        return ConversationHandler.END

    update.message.reply_text("Instant was successfully sent, you should be able to search for it in a while.\n"
                              f"Your sound's url: {url}\n"
                              "See you later!")

    # Remove temporary file
    remove_sound_file(context.user_data['filename'])

    # Clear user data
    context.user_data.clear()

    return ConversationHandler.END

def cancel(update, context):
    """Handler to abort the machine state"""
    update.message.reply_text("Aborting...\n See you later!")

    if "filename" in context.user_data:
        remove_sound_file(context.user_data['filename'])

    # Clear user data
    context.user_data.clear()

    return ConversationHandler.END

def main():
    """Main function"""

    for var in ["MYINSTANTS_USERNAME", "MYINSTANTS_PASSWORD", "TELEGRAM_TOKEN"]:
        if var not in os.environ:
            LOGGER.error(f"Missing environment variable {var}! See README.md file for more information.")
            return 1

    # Create the Updater and pass it your bot's token.
    updater = Updater(os.environ["TELEGRAM_TOKEN"])

    # on different commands - answer in Telegram
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("help", help_command))
    updater.dispatcher.add_handler(CommandHandler("info", info_command))

    # on noncommand i.e message - echo the message on Telegram
    updater.dispatcher.add_handler(InlineQueryHandler(inlinequery))

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("upload", upload_start, run_async=True)],
        states={
            SOUND: [MessageHandler(Filters.voice, get_voice, run_async=True),
                    MessageHandler(Filters.audio, get_audio, run_async=True)],
            NAME: [MessageHandler(Filters.text, get_name, run_async=True)],
            CONFIRMATION: [MessageHandler(Filters.text, name_confirmation_and_upload, run_async=True)]
        },
        fallbacks=[CommandHandler("cancel", cancel, run_async=True)]
    )

    updater.dispatcher.add_handler(conv_handler)

    # log all errors
    updater.dispatcher.add_error_handler(error_handler)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
