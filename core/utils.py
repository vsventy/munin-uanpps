# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import httplib
import json
import logging
import os
import requests

from fake_useragent import FakeUserAgentError
from fake_useragent import UserAgent
from logging.config import fileConfig

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

fileConfig(os.path.join(ROOT_PATH, 'logging_config.ini'))
logger = logging.getLogger('uanpps-core')


def load_json(full_path):
    with open(full_path) as json_file:
        return json.load(json_file)


def init_multigraph(config):
    print('multigraph {}'.format(config['id']))
    print('graph_title {}'.format(config['title']))
    print('graph_category {}'.format(config['category']))
    print('graph_vlabel {}'.format(config['vlabel']))
    if config['total']:
        print('graph_total {}'.format(config['total']))
    print('graph_scale {}'.format(config['scale']))


def get_lists_of_values(html_table_rows):
    values_list = []
    for row in html_table_rows:
        cols = row.find_all('td')
        cols = [elem.text.strip() for elem in cols]
        values_list.append([elem for elem in cols if elem])
    return values_list


def get_color_value(colors, name):
    if '.' in name:
        parameter = name.split('.')
        value = colors[parameter[0]][parameter[1]].replace('#', '')
    else:
        value = name
    return value


def init_base_parameters(config, colors):
    for field in config['fields']:
        print('{}.label {}'.format(field['id'], field['label']))
        if 'colour' in field:
            print('{}.colour {}'.format(
                field['id'],
                get_color_value(colors, field['colour']))
            )
        if 'info' in field:
            print('{}.info {}'.format(field['id'], field['info']))


def get_values_multigraph(data, config, ratio=None):
    print('multigraph {}'.format(config['id']))
    for i, field in enumerate(config['fields']):
        if 'parameter' in field.keys():
            if '.' in field['parameter']:
                parameter = field['parameter'].split('.')
                value = data[parameter[0]][parameter[1]]
            else:
                parameter = field['parameter']
                value = data[parameter]
        else:
            value = data[i] if isinstance(data, list) else data
        try:
            if isinstance(value, (str, unicode)):
                value = value.replace(',', '.')
            value = float(value)
        except (TypeError, ValueError):
            logger.error('Invalid value for field \'%s\': %s=%s',
                         field['id'], parameter, value)
            continue
        if ratio:
            value = float(value) * ratio
        print('{}.value {:.2f}'.format(field['id'], value))


def enable_requests_logging():
    httplib.HTTPConnection.debuglevel = 1
    requests_log = logging.getLogger('requests.packages.urllib3')
    requests_log.setLevel(logging.DEBUG)
    requests.propagate = True


def get_random_user_agent():
    try:
        user_agent = UserAgent()
        user_agent = user_agent.random
    except FakeUserAgentError:
        user_agent = ('Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) '
                      'Gecko/20100101 Firefox/41.0')
    logger.debug('UserAgent = "%s"', user_agent)
    return user_agent
