#!/usr/bin/env pipenv-shebang
import sys

from presensi import login_app


def main():
    if len(sys.argv) == 1:
        login_app(action="checkin")
    elif len(sys.argv) == 3:
        userid = sys.argv[1]
        password = sys.argv[2]
        login_app(action="checkin", userid=userid, password=password)


if __name__ == "__main__":
    main()
