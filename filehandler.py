#!/usr/bin/env pipenv-shebang
import os
import datetime
import logging
import logging.config

import pretty_errors
import yaml


def create_dirs(dirnames):
    new_dirnames = []
    for dirname in dirnames:
        dirpath = os.path.join(os.path.dirname(__file__), dirname)
        if not os.path.isdir(dirpath):
            os.mkdir(dirpath)
        new_dirnames.append(dirpath)
    return new_dirnames


def create_subdirs(base_dirpath, dirnames):
    new_dirnames = []
    for dirname in dirnames:
        dirpath = os.path.join(base_dirpath, dirname)
        if not os.path.isdir(dirpath):
            os.mkdir(dirpath)
        new_dirnames.append(dirpath)
    return new_dirnames


if __name__ != "__main__":
    # init logger
    create_dirs(["log"])
    with open("logging.yaml", "r") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)
    logger = logging.getLogger(__name__)
