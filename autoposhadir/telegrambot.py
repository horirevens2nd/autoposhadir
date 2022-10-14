#!/usr/bin/env pipenv-shebang
import logging.config
import os
import sys
from threading import Thread

import pretty_errors
import yaml
from dotenv import load_dotenv
from telegram.ext import CommandHandler, Filters, Updater

# this is my telegram id
YOGI = 159508674


# init logger
with open("logger/loggerconfig.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
logging.config.dictConfig(config)

load_dotenv()
updater = Updater(token=os.environ.get("POSHADIR64400_BOT"), use_context=True)


def send_message(chat_id=None, text=None, parse_mode=None):
    """send message to client"""
    updater.bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)


def send_document(chat_id=None, filepath=None, caption=None):
    """send document to user"""
    if os.path.isfile(filepath):
        updater.bot.send_document(
            chat_id=chat_id,
            document=open(filepath, "rb"),
            caption=caption,
        )


def start(update, context):
    """run start command"""
    chat_id = update.message.chat.id
    if chat_id == YOGI:
        message = (
            "*PosHadir Command*\n"
            "/checkin \- use for checkin\n"
            "/checkout \- use for checkout\n\n"
            "*Bot Command*\n"
            "/getid \- get telegram ID\n"
            "/help \- show this message\n"
            "/restart \- restart the bot\n"
            "/stop \- stop the bot"
        )
    else:
        message = (
            "*PosHadir Command*\n"
            "/checkin nippos password \- use for checkin\n"
            "/checkout nippos password \- use for checkout\n\n"
            "*Bot Command*\n"
            "/getid \- get telegram ID\n"
            "/help \- show this message\n"
        )
    update.message.reply_text(message, parse_mode="MarkdownV2")


def get_id(update, context):
    """get telegram ID"""
    chat_id = update.message.chat.id
    # first_name = update.message.chat.first_name
    # last_name = update.message.chat.last_name
    # last_name = f" {last_name}" if last_name is not None else ""
    message = f"Your ID is {chat_id}"
    update.message.reply_text(message)


def stop_and_restart():
    updater.stop()
    os.execl(sys.executable, sys.executable, *sys.argv)


def restart(update, context):
    """restart telegram bot"""
    update.message.reply_text("Bot is restarting...")
    Thread(target=stop_and_restart).start()


def stop_and_shutdown():
    updater.stop()
    updater.is_idle = False


def stop(update, context):
    """stop telegram bot"""
    update.message.reply_text("Bot is shutting down...")
    Thread(target=stop_and_shutdown).start()


def validate_command(update, context, action):
    chat_id = update.message.chat.id

    if len(context.args) == 0 and chat_id == YOGI:
        command = f"pipenv-shebang presensiaction.py {chat_id} {action}"
        logger.debug(command)
        os.system(command)
    elif len(context.args) == 2:
        userid = context.args[0]
        password = context.args[1]
        login_args = {"userid": userid, "password": password}
        logger.debug(login_args)

        command = (
            f"pipenv-shebang presensiaction.py {chat_id} {action} {userid} {password}"
        )
        logger.debug(command)
        os.system(command)
    else:
        logger.debug("argument length != 0 or 2")
        message = (
            "Format tidak sesuai, silakan gunakan format seperti dibawah ini.\n"
            "/checkin nippos password\n"
            "/checkout nippos password\n"
        )
        update.message.reply_text(message)


def check_in(update, context):
    validate_command(update, context, "check_in")


def check_out(update, context):
    validate_command(update, context, "check_out")


def main():
    # filter by username
    yogitrismayana = Filters.user(username="@yogitrismayana")

    # init handler
    checkin_handler = CommandHandler("checkin", check_in)
    checkout_handler = CommandHandler("checkout", check_out)
    getid_handler = CommandHandler("getid", get_id)
    start_handler = CommandHandler("start", start)
    help_handler = CommandHandler("help", start)
    restart_handler = CommandHandler("restart", restart, filters=yogitrismayana)
    stop_handler = CommandHandler("stop", stop, filters=yogitrismayana)

    # add handler to dispatcher
    dispatcher = updater.dispatcher
    dispatcher.add_handler(checkin_handler)
    dispatcher.add_handler(checkout_handler)
    dispatcher.add_handler(getid_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(stop_handler)

    # start the bot
    updater.bot.send_message(chat_id=YOGI, text="Bot is starting...")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    main()
