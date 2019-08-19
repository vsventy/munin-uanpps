#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import ast
import logging
import os
import pdb
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

logger = logging.getLogger('znpp-node')

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
ABSOLUTE_PATH = ROOT_PATH + '/data/znpp/'

AIR_TEMPERATURE = load_json(ABSOLUTE_PATH + 'air_temperature.json')
ATM = load_json(ABSOLUTE_PATH + 'atm.json')
HUMIDITY = load_json(ABSOLUTE_PATH + 'humidity.json')
LOADS_UNITS = load_json(ABSOLUTE_PATH + 'loads_units.json')
RADIOLOGY_30KM = load_json(ABSOLUTE_PATH + 'radiology_30km.json')
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

    # Loads Units
    init_multigraph(LOADS_UNITS)
    print('graph_args --base 1000 --lower-limit 0')
    init_base_parameters(LOADS_UNITS, COLORS)
    for field in LOADS_UNITS['fields']:
        print('{}.min 0'.format(field['id']))
    print('')

    # Radiological situation (30-km)
    init_multigraph(RADIOLOGY_30KM)
    print('graph_args --base 1000 --lower-limit 0 --alt-y-grid')
    init_base_parameters(RADIOLOGY_30KM, COLORS)
    print('')

    # Radiological situation (industrial site)
    init_multigraph(RADIOLOGY)
    print('graph_args --base 1000 --lower-limit 0 --alt-y-grid')
    init_base_parameters(RADIOLOGY, COLORS)
    print('')


def znpp_node(config):
    logger.info('Start znpp-node (main)')

    # retrieve meteo parameters
    request = urllib2.Request(config['perform_url'], headers=config['headers'])
    response = urllib2.urlopen(request).read()
    meteo_soup = BeautifulSoup(response, 'html.parser')

    meteo_container = meteo_soup.find('div', {'id': 'block-znppmawssidebar'})
    meteo_table_rows = meteo_container.find('table').find_all('tr')
    meteo_data = get_lists_of_values(meteo_table_rows)

    air_temperature = meteo_data[0][1]
    humidity = meteo_data[3][1].split(' ', 1)[0]
    atmospheric_pressure = meteo_data[4][1]

    wind_speed_avg = meteo_data[2][1]

    # retrieve performance parameters
    request = urllib2.Request(config['meteo_url'], headers=config['headers'])
    response = urllib2.urlopen(request).read()
    perform_soup = BeautifulSoup(response, 'html.parser')

    perform_container = perform_soup.find('div', {'id': 'block-znppunitssidebar'})
    perform_table_rows = perform_container.find('table').find_all('tr')
    perform_data = get_lists_of_values(perform_table_rows)

    units_list = []
    iter_perform = iter(perform_data)
    for item in iter_perform:
        value = item[1] if len(item) > 2 else 0
        units_list.append(value)

    # retrieve radiological situation
    request = urllib2.Request(config['radio_url'], headers=config['headers'])
    response = urllib2.urlopen(request).read()
    radiology_soup = BeautifulSoup(response, 'html.parser')

    radiology_container = radiology_soup.find('div', {'id': 'block-porto-content'})
    radiology_table_rows = radiology_container.find('table').find_all('tr')
    radiology_data = get_lists_of_values(radiology_table_rows)

    radiology_values_30km = []
    iter_radiology = iter(radiology_data)
    iter_radiology.next()  # skip header row
    for item in iter_radiology:
        item_value = item[1].strip()
        radiology_values_30km.append(item_value)

    # Air temperature
    get_values_multigraph(air_temperature, AIR_TEMPERATURE)

    # Atmospheric pressure (convert hectopascals to millimeter of mercury)
    get_values_multigraph(atmospheric_pressure, ATM)

    # Relative humidity
    get_values_multigraph(humidity, HUMIDITY)

    # Wind speed
    get_values_multigraph(wind_speed_avg, WIND_SPEED)

    # Loads Units
    get_values_multigraph(units_list, LOADS_UNITS)

    # Radiological situation (30-km)
    get_values_multigraph(radiology_values_30km, RADIOLOGY_30KM)

    logger.info('Finish znpp-node (main)')
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
        'perform_url': os.environ.get('perform_url', 'https://www.npp.zp.ua/uk/activities/performance-indicators'),
        'meteo_url': os.environ.get('meteo_url', 'https://www.npp.zp.ua/uk/safety/meteo'),
        'radio_url': os.environ.get('radio_url', 'https://www.npp.zp.ua/uk/safety/arms'),
        'headers': {'User-Agent': user_agent}
    }

    # turn on requests logging
    if ast.literal_eval(config['logging']):
        enable_requests_logging()

    znpp_node(config)

if __name__ == '__main__':
    main()
