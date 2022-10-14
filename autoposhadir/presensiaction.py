#!/usr/bin/env pipenv-shebang
import sys
import logging

from presensi import login_app


def main():
    logger.debug(sys.argv)
    chat_id = sys.argv[1]
    action = sys.argv[2]

    if len(sys.argv) == 3:
        logger.debug(action)
        login_app(chat_id, action)
    elif len(sys.argv) == 5:
        userid = sys.argv[3]
        password = sys.argv[4]
        login_args = {
            "chat_id": chat_id,
            "action": action,
            "userid": userid,
            "password": password,
        }
        logger.debug(login_args)
        login_app(chat_id, action, userid, password)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    main()
