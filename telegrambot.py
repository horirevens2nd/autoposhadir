#!/usr/bin/env pipenv-shebang
import os
import sys
import logging
from threading import Thread

import pretty_errors
import yaml
from telegram.ext import Updater, CommandHandler, Filters

import filehandler

# get object from secret.yaml
with open("secret.yaml", "r") as file:
    secret = yaml.load(file, Loader=yaml.FullLoader)
ID = secret["telegram"]["id"]
TOKEN = secret["telegram"]["token"]
USERID = secret["presensi"]["userid"]
PASSWORD = secret["presensi"]["password"]
URL = secret["presensi"]["url"]

updater = Updater(token=TOKEN, use_context=True)


def send_message(chat_id=ID, text="...", parse_mode=None):
    """send message to client"""
    updater.bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)


def send_document_(chat_id=ID, filepath=None, caption=None):
    """send document to user"""
    if os.path.isfile(filepath):
        updater.bot.send_document(
            chat_id=chat_id,
            document=open(filepath, "rb"),
            caption=caption,
        )


def start(update, context):
    """run start command"""
    message = (
        "*Presensi Command*\n"
        "/checkin \- use for checkin\n"
        "/checkout \- use for checkout\n\n"
        "*Bot Command*\n"
        "/getid \- get telegram ID\n"
        "/start \- show this message\n"
        "/restart \- restart the bot\n"
        "/shutdown \- stop the bot"
    )
    update.message.reply_text(message, parse_mode="MarkdownV2")


def getid(update, context):
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


def checkin(update, context):
    """run checkin.py script"""
    if len(context.args) == 0:
        logger.debug("argument length is equal 0")
        os.system("pipenv-shebang checkin.py")
    elif len(context.args) == 2:
        logger.debug("argument length is equal 2")
        userid = context.args[0]
        password = context.args[1]
        login_data = {"userid": userid, "password": password}
        if len(userid) == 9 and len(password) > 0:
            logger.debug(login_data)
            os.system(f"pipenv-shebang checkin.py {userid} {password}")
        else:
            logger.debug(login_data)
            update.message.reply_text("User ID and Password is not valid")
    else:
        logger.debug("argument lenght is not equal 0 or 2")
        update.message.reply_text("Format is not valid")


def checkout(update, context):
    """run checkout.py script"""
    if len(context.args) == 0:
        logger.debug("argument length is equal 0")
        os.system("pipenv-shebang checkout.py")
    elif len(context.args) == 2:
        logger.debug("argument length is equal 2")
        userid = context.args[0]
        password = context.args[1]
        login_data = {"userid": userid, "password": password}
        if len(userid) == 9 and len(password) == 10:
            logger.debug(login_data)
            os.system(f"pipenv-shebang checkout.py {userid} {password}")
        else:
            logger.debug(login_data)
            update.message.reply_text("User ID and Password is not valid")
    else:
        logger.debug("argument length is not equal 0 or 2")
        update.message.reply_text("Format is not valid")


def main():
    # filter by username
    yogitrismayana = Filters.user(username="@yogitrismayana")

    # init handler
    checkin_handler = CommandHandler("checkin", checkin, filters=yogitrismayana)
    checkout_handler = CommandHandler("checkout", checkout, filters=yogitrismayana)
    getid_handler = CommandHandler("getid", getid)
    start_handler = CommandHandler("start", start)
    restart_handler = CommandHandler("restart", restart, filters=yogitrismayana)
    stop_handler = CommandHandler("stop", stop, filters=yogitrismayana)

    # add handler to dispatcher
    dispatcher = updater.dispatcher
    dispatcher.add_handler(checkin_handler)
    dispatcher.add_handler(checkout_handler)
    dispatcher.add_handler(getid_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(stop_handler)

    # start the bot
    updater.bot.send_message(chat_id=ID, text="Bot is starting...")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    main()
