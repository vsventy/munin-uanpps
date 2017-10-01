#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import sys
import httplib
import json
import logging
import requests

from logging.handlers import TimedRotatingFileHandler

from fake_useragent import FakeUserAgentError
from fake_useragent import UserAgent

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
ABSOLUTE_PATH = ROOT_PATH + '/data/rnpp/'

with open(ABSOLUTE_PATH + 'loads_units.json') as json_file:
    LOADS_UNITS = json.load(json_file)

with open(ABSOLUTE_PATH + 'loads_units_by_tgen.json') as json_file:
    LOADS_UNITS_BY_TGEN = json.load(json_file)

with open(ABSOLUTE_PATH + 'loads_lines.json') as json_file:
    LOADS_LINES = json.load(json_file)

with open(ABSOLUTE_PATH + 'air_temperature.json') as json_file:
    AIR_TEMPERATURE = json.load(json_file)

with open(ABSOLUTE_PATH + 'humidity.json') as json_file:
    HUMIDITY = json.load(json_file)

with open(ABSOLUTE_PATH + 'atm.json') as json_file:
    ATM = json.load(json_file)

with open(ABSOLUTE_PATH + 'rainfall_intensity.json') as json_file:
    RAINFALL_INTENSITY = json.load(json_file)

with open(ABSOLUTE_PATH + 'wind_speed.json') as json_file:
    WIND_SPEED = json.load(json_file)

with open(ABSOLUTE_PATH + 'radiology.json') as json_file:
    RADIOLOGY = json.load(json_file)

with open(ABSOLUTE_PATH + 'production_electricity.json') as json_file:
    PRODUCTION_ELECTRICITY = json.load(json_file)

with open(ROOT_PATH + '/data/' + 'colors.json') as json_file:
    COLORS = json.load(json_file)

logger = logging.getLogger(__name__)
logHandler = TimedRotatingFileHandler(
    ROOT_PATH + '/logs/rnpp-node.log',
    when='D',
    interval=1,
    backupCount=5)
logFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logHandler.setFormatter(logFormatter)
logger.addHandler(logHandler)
logger.setLevel(logging.DEBUG)


def enable_requests_logging():
    httplib.HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger('requests.packages.urllib3')
    requests_log.setLevel(logging.DEBUG)
    requests.propagate = True


def display_config():
    # Loads Units
    init_multigraph(LOADS_UNITS)
    print('graph_args --base 1000 --lower-limit 0')
    init_base_parameters(LOADS_UNITS)
    for field in LOADS_UNITS['fields']:
        print('{}.min 0'.format(field['id']))
    print('')

    # Loads Units by turbogenerators
    init_multigraph(LOADS_UNITS_BY_TGEN)
    print('graph_args --base 1000 --lower-limit 0')
    init_base_parameters(LOADS_UNITS_BY_TGEN)
    for field in LOADS_UNITS_BY_TGEN['fields']:
        print('{}.min 0'.format(field['id']))
        print('{}.draw AREASTACK'.format(field['id']))
    print('')

    # Load on the lines
    init_multigraph(LOADS_LINES)
    print('graph_args --base 1000 --lower-limit 0')
    init_base_parameters(LOADS_LINES)
    for field in LOADS_LINES['fields']:
        print('{}.min 0'.format(field['id']))
        print('{}.draw AREASTACK'.format(field['id']))
    print('')

    # Air temperature
    init_multigraph(AIR_TEMPERATURE)
    print('graph_args --base 1000 --upper-limit 20 --lower-limit -20 HRULE:0#a1a1a1')
    init_base_parameters(AIR_TEMPERATURE)
    print('')

    # Relative humidity
    init_multigraph(HUMIDITY)
    print('graph_args --base 1000 --upper-limit 100 --lower-limit 0')
    init_base_parameters(HUMIDITY)
    print('')

    # Atmospheric pressure
    init_multigraph(ATM)
    print('graph_args --base 1000')
    init_base_parameters(ATM)
    for field in ATM['fields']:
        print('{}.draw AREA'.format(field['id']))
    print('')

    # Intensity of rainfall
    init_multigraph(RAINFALL_INTENSITY)
    print('graph_args --base 1000 --upper-limit 5 --lower-limit 0')
    init_base_parameters(RAINFALL_INTENSITY)
    for field in RAINFALL_INTENSITY['fields']:
        print('{}.draw AREA'.format(field['id']))
    print('')

    # Wind speed
    init_multigraph(WIND_SPEED)
    print('graph_args --base 1000 --upper-limit 20 --lower-limit 0')
    init_base_parameters(WIND_SPEED)
    for field in WIND_SPEED['fields']:
        print('{}.draw LINE{}'.format(field['id'], field['thickness']))
    print('')

    # Radiological situation
    init_multigraph(RADIOLOGY)
    print('graph_args --base 1000 --lower-limit 0 --alt-y-grid')
    init_base_parameters(RADIOLOGY)
    print('')

    # Production of electricity for current day/month
    init_multigraph(PRODUCTION_ELECTRICITY)
    print('graph_args --base 1000 --lower-limit 0')
    init_base_parameters(PRODUCTION_ELECTRICITY)
    for field in PRODUCTION_ELECTRICITY['fields']:
        print('{}.draw AREA'.format(field['id']))
    print('')


def init_multigraph(config):
    print('multigraph {}'.format(config['id']))
    print('graph_title {}'.format(config['title']))
    print('graph_category {}'.format(config['category']))
    print('graph_vlabel {}'.format(config['vlabel']))
    if config['total']:
        print('graph_total {}'.format(config['total']))
    print('graph_scale {}'.format(config['scale']))


def init_base_parameters(config):
    for field in config['fields']:
        print('{}.label {}'.format(field['id'], field['label']))
        if 'colour' in field:
            print('{}.colour {}'.format(field['id'],
                                        get_color_value(field['colour'])))
        if 'info' in field:
            print('{}.info {}'.format(field['id'], field['info']))


def get_values_multigraph(data, config, ratio=None):
    print('multigraph {}'.format(config['id']))
    for field in config['fields']:
        if '.' in field['parameter']:
            parameter = field['parameter'].split('.')
            value = data[parameter[0]][parameter[1]]
        else:
            parameter = field['parameter']
            value = data[parameter]
        try:
            value = float(value)
        except (TypeError, ValueError):
            logger.error('Invalid value for field \'%s\': %s=%s',
                         field['id'], parameter, value)
            continue
        if ratio:
            value = float(value) * ratio
        print('{}.value {:.2f}'.format(field['id'], value))


def rnpp_node(config):
    logger.info('Start rnpp-node (main)')

    url = 'http://{}/informer/sprut.php'.format(config['host'])

    response = requests.get(url=url, params=config['params1'],
                            headers=config['headers'])
    response.encoding = 'utf-8'
    data = json.loads(response.text)

    # Loads Units
    get_values_multigraph(data, LOADS_UNITS)

    # Air temperature
    get_values_multigraph(data, AIR_TEMPERATURE)

    # Relative humidity
    get_values_multigraph(data, HUMIDITY)

    # Atmospheric pressure (convert hectopascals to millimeter of mercury)
    get_values_multigraph(data, ATM, 0.7500637554192)

    # Intensity of rainfall
    get_values_multigraph(data, RAINFALL_INTENSITY)

    # Wind speed
    get_values_multigraph(data, WIND_SPEED)

    # Radiological situation
    get_values_multigraph(data, RADIOLOGY)

    response = requests.get(url=url, params=config['params2'],
                            headers=config['headers'])
    response.encoding = 'utf-8'
    try:
        data = json.loads(response.text)['N']
    except ValueError:
        logger.error('When decode data: url=%s, params=%s',
                     url, config['params2'])

    # Load on the lines
    get_values_multigraph(data, LOADS_LINES)

    # Loads Units by turbogenerators
    get_values_multigraph(data, LOADS_UNITS_BY_TGEN)

    response = requests.get(url=url, params=config['params3'],
                            headers=config['headers'])
    response.encoding = 'utf-8'
    try:
        data = json.loads(response.text)
    except ValueError:
        logger.error('When decode data: url=%s, params=%s',
                     url, config['params3'])

    # Production of electricity for current day/month
    get_values_multigraph(data, PRODUCTION_ELECTRICITY, 0.001)

    logger.info('Finish rnpp-node (main)')
    sys.exit(0)


def get_color_value(name):
    if '.' in name:
        parameter = name.split('.')
        value = COLORS[parameter[0]][parameter[1]].replace('#', '')
    else:
        value = name
    return value


def main():
    # display config
    if len(sys.argv) > 1 and sys.argv[1] == 'config':
        display_config()
        sys.exit(0)

    # init User-Agent
    try:
        user_agent = UserAgent()
        user_agent.update()
        user_agent = user_agent.random
    except FakeUserAgentError:
        user_agent = ('Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) '
                      'Gecko/20100101 Firefox/41.0')

    logger.debug('UserAgent = "%s"', user_agent)

    # init config
    config = {
        'host': os.environ.get('host', 'www.rnpp.rv.ua'),
        'logging': os.environ.get('logging', 'no'),
        'params1': {'value': 'sprutbase'},
        'params2': {'value': 'rnpp_n'},
        'params3': {'value': 'rnpp_current_state'},
        'headers': {'User-Agent': user_agent}
    }

    # turn on requests logging
    if config['logging'] == 'yes':
        enable_requests_logging()

    rnpp_node(config)

if __name__ == '__main__':
    main()
