# -*- coding: utf-8 -*-
import os
import os.path

from logging.config import fileConfig

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))

logs_dir = os.path.join(ROOT_PATH, 'logs/')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

fileConfig(os.path.join(ROOT_PATH, 'logging_config.ini'))
