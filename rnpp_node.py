#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import ast
import os
import sys
import httplib
import json
import logging
import requests

from logging.handlers import TimedRotatingFileHandler

from fake_useragent import FakeUserAgentError
from fake_useragent import UserAgent

from core.utils import get_values_multigraph
from core.utils import init_base_parameters
from core.utils import init_multigraph
from core.utils import load_json

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
ABSOLUTE_PATH = ROOT_PATH + '/data/rnpp/'

LOADS_UNITS = load_json(ABSOLUTE_PATH + 'loads_units.json')
LOADS_UNITS_BY_TGEN = load_json(ABSOLUTE_PATH + 'loads_units_by_tgen.json')
LOADS_LINES = load_json(ABSOLUTE_PATH + 'loads_lines.json')
AIR_TEMPERATURE = load_json(ABSOLUTE_PATH + 'air_temperature.json')
HUMIDITY = load_json(ABSOLUTE_PATH + 'humidity.json')
ATM = load_json(ABSOLUTE_PATH + 'atm.json')
RAINFALL_INTENSITY = load_json(ABSOLUTE_PATH + 'rainfall_intensity.json')
WIND_SPEED = load_json(ABSOLUTE_PATH + 'wind_speed.json')
RADIOLOGY = load_json(ABSOLUTE_PATH + 'radiology.json')
PRODUCTION_ELECTRICITY = load_json(ABSOLUTE_PATH + 'production_electricity.json')
COLORS = load_json(ROOT_PATH + '/data/colors.json')

logger = logging.getLogger('uanpps.nodes')
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
    init_base_parameters(LOADS_UNITS, COLORS)
    for field in LOADS_UNITS['fields']:
        print('{}.min 0'.format(field['id']))
    print('')

    # Loads Units by turbogenerators
    init_multigraph(LOADS_UNITS_BY_TGEN)
    print('graph_args --base 1000 --lower-limit 0')
    init_base_parameters(LOADS_UNITS_BY_TGEN, COLORS)
    for field in LOADS_UNITS_BY_TGEN['fields']:
        print('{}.min 0'.format(field['id']))
        print('{}.draw AREASTACK'.format(field['id']))
    print('')

    # Load on the lines
    init_multigraph(LOADS_LINES)
    print('graph_args --base 1000 --lower-limit 0')
    init_base_parameters(LOADS_LINES, COLORS)
    for field in LOADS_LINES['fields']:
        print('{}.min 0'.format(field['id']))
        print('{}.draw AREASTACK'.format(field['id']))
    print('')

    # Air temperature
    init_multigraph(AIR_TEMPERATURE)
    print(('graph_args --base 1000 --upper-limit 20 --lower-limit -20 '
           'HRULE:0#a1a1a1'))
    init_base_parameters(AIR_TEMPERATURE, COLORS)
    print('')

    # Relative humidity
    init_multigraph(HUMIDITY)
    print('graph_args --base 1000 --upper-limit 100 --lower-limit 0')
    init_base_parameters(HUMIDITY, COLORS)
    print('')

    # Atmospheric pressure
    init_multigraph(ATM)
    print('graph_args --base 1000')
    init_base_parameters(ATM, COLORS)
    for field in ATM['fields']:
        print('{}.draw AREA'.format(field['id']))
    print('')

    # Intensity of rainfall
    init_multigraph(RAINFALL_INTENSITY)
    print('graph_args --base 1000 --upper-limit 5 --lower-limit 0')
    init_base_parameters(RAINFALL_INTENSITY, COLORS)
    for field in RAINFALL_INTENSITY['fields']:
        print('{}.draw AREA'.format(field['id']))
    print('')

    # Wind speed
    init_multigraph(WIND_SPEED)
    print('graph_args --base 1000 --upper-limit 20 --lower-limit 0')
    init_base_parameters(WIND_SPEED, COLORS)
    for field in WIND_SPEED['fields']:
        print('{}.draw LINE{}'.format(field['id'], field['thickness']))
    print('')

    # Radiological situation
    init_multigraph(RADIOLOGY)
    print('graph_args --base 1000 --lower-limit 0 --alt-y-grid')
    init_base_parameters(RADIOLOGY, COLORS)
    print('')

    # Production of electricity for current day/month
    init_multigraph(PRODUCTION_ELECTRICITY)
    print('graph_args --base 1000 --lower-limit 0')
    init_base_parameters(PRODUCTION_ELECTRICITY, COLORS)
    for field in PRODUCTION_ELECTRICITY['fields']:
        print('{}.draw AREA'.format(field['id']))
    print('')


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


def main():
    # display config
    if len(sys.argv) > 1 and sys.argv[1] == 'config':
        display_config()
        sys.exit(0)

    # init User-Agent
    try:
        user_agent = UserAgent()
        user_agent = user_agent.random
    except FakeUserAgentError:
        user_agent = ('Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) '
                      'Gecko/20100101 Firefox/41.0')

    logger.debug('UserAgent = "%s"', user_agent)

    # init config
    config = {
        'host': os.environ.get('host', 'www.rnpp.rv.ua'),
        'logging': os.environ.get('uanpps_logging', 'False'),
        'params1': {'value': 'sprutbase'},
        'params2': {'value': 'rnpp_n'},
        'params3': {'value': 'rnpp_current_state'},
        'headers': {'User-Agent': user_agent}
    }

    # turn on requests logging
    if ast.literal_eval(config['logging']):
        enable_requests_logging()

    rnpp_node(config)

if __name__ == '__main__':
    main()
