#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import logging
import os
import sys
import urllib2

from bs4 import BeautifulSoup
from fake_useragent import FakeUserAgentError
from fake_useragent import UserAgent
from logging.config import fileConfig

from core.utils import get_values_multigraph
from core.utils import init_base_parameters
from core.utils import init_multigraph
from core.utils import load_json

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))

fileConfig(os.path.join(ROOT_PATH, 'logging_config.ini'))
logger = logging.getLogger('khnpp-node')

ABSOLUTE_PATH = ROOT_PATH + '/data/khnpp/'
AIR_TEMPERATURE = load_json(ABSOLUTE_PATH + 'air_temperature.json')
ATM = load_json(ABSOLUTE_PATH + 'atm.json')
HUMIDITY = load_json(ABSOLUTE_PATH + 'humidity.json')
WIND_SPEED = load_json(ABSOLUTE_PATH + 'wind_speed.json')
COLORS = load_json(ROOT_PATH + '/data/colors.json')


def get_lists_of_values(html_table_rows):
    values_list = []
    for row in html_table_rows:
        cols = row.find_all('td')
        cols = [elem.text.strip() for elem in cols]
        values_list.append([elem for elem in cols if elem])
    return values_list


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


def khnpp_node(config):
    logger.info('Start khnpp-node (main)')

    request = urllib2.Request(config['host'], headers=config['headers'])
    response = urllib2.urlopen(request).read()
    soup = BeautifulSoup(response, 'html.parser')

    # retrieve meteo parameters
    meteo_container = soup.find(id='lightmeteo')
    meteo_table_rows = meteo_container.find('table').find_all('tr')
    meteo_data = get_lists_of_values(meteo_table_rows)

    air_temperature = meteo_data[1][1].split(' ', 1)[0]
    wind_speed = meteo_data[2][1].split(' ', 1)[0]
    humidity = meteo_data[3][1].split(' ', 1)[0]
    atmospheric_pressure = meteo_data[4][1].split(' ', 1)[0]

    # Air temperature
    get_values_multigraph(air_temperature, AIR_TEMPERATURE)

    # Atmospheric pressure (convert hectopascals to millimeter of mercury)
    get_values_multigraph(atmospheric_pressure, ATM, 0.7500637554192)

    # Relative humidity
    get_values_multigraph(humidity, HUMIDITY)

    # Wind speed
    get_values_multigraph(wind_speed, WIND_SPEED)

    logger.info('Finish khnpp-node (main)')
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
        'host': os.environ.get('host', 'http://www.xaec.org.ua'),
        'headers': {'User-Agent': user_agent}
    }

    khnpp_node(config)

if __name__ == '__main__':
    main()
