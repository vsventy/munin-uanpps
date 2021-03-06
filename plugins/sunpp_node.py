#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import ast
import logging
import os
import sys
import urllib2

from bs4 import BeautifulSoup

from core.utils import enable_requests_logging
from core.utils import get_lists_of_values
from core.utils import get_random_user_agent
from core.utils import get_values_multigraph
from core.utils import init_base_parameters
from core.utils import init_multigraph
from core.utils import load_json

logger = logging.getLogger('sunpp-node')

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
ABSOLUTE_PATH = ROOT_PATH + '/data/sunpp/'

AIR_TEMPERATURE = load_json(ABSOLUTE_PATH + 'air_temperature.json')
ATM = load_json(ABSOLUTE_PATH + 'atm.json')
HUMIDITY = load_json(ABSOLUTE_PATH + 'humidity.json')
RADIOLOGY = load_json(ABSOLUTE_PATH + 'radiology.json')
WIND_SPEED = load_json(ABSOLUTE_PATH + 'wind_speed.json')
COLORS = load_json(ROOT_PATH + '/data/colors.json')


def display_config():
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


def sunpp_node(config):
    logger.info('Start sunpp-node (main)')

    # retrieve meteo parameters
    request = urllib2.Request(config['home_url'], headers=config['headers'])
    response = urllib2.urlopen(request).read()
    soup = BeautifulSoup(response, 'html.parser')

    table_rows = soup.find('table', class_='"table-param-block"').find_all('tr')
    data = get_lists_of_values(table_rows)

    air_temperature = data[1][1]
    wind_speed = data[3][1]
    atmospheric_pressure = data[4][1]
    humidity = data[5][1]

    # retrieve radiological situation
    request = urllib2.Request(config['radio_url'], headers=config['headers'])
    response = urllib2.urlopen(request).read()
    radio_soup = BeautifulSoup(response, 'html.parser')

    radio_table_rows = radio_soup.find('table', class_='"table-param-askro"')\
        .find_all('tr')
    radio_data = get_lists_of_values(radio_table_rows)

    iter_radio = iter(radio_data)
    iter_radio.next()  # skip header row
    radio_values = []
    for item in iter_radio:
        value = item[2].strip()
        radio_values.append(value)

    # Air temperature
    get_values_multigraph(air_temperature, AIR_TEMPERATURE)

    # Atmospheric pressure (convert hectopascals to millimeter of mercury)
    get_values_multigraph(atmospheric_pressure, ATM, 0.7500637554192)

    # Relative humidity
    get_values_multigraph(humidity, HUMIDITY)

    # Wind speed
    get_values_multigraph(wind_speed, WIND_SPEED)

    # Radiological situation
    get_values_multigraph(radio_values, RADIOLOGY)

    logger.info('Finish sunpp-node (main)')
    sys.exit(0)


def main():
    # display config
    if len(sys.argv) > 1 and sys.argv[1] == 'config':
        display_config()
        sys.exit(0)

    # init User-Agent
    user_agent = get_random_user_agent()

    # init config
    config = {
        'logging': os.environ.get('uanpps_logging', 'False'),
        'home_url': os.environ.get('home_url', 'https://www.sunpp.mk.ua/'),
        'radio_url': os.environ.get('radio_url', 'https://www.sunpp.mk.ua/uk/activities/radiation'),
        'headers': {'User-Agent': user_agent}
    }

    # turn on requests logging
    if ast.literal_eval(config['logging']):
        enable_requests_logging()

    sunpp_node(config)

if __name__ == '__main__':
    main()
