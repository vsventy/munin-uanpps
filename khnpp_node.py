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
LOADS_UNITS = load_json(ABSOLUTE_PATH + 'loads_units.json')
RADIOLOGY = load_json(ABSOLUTE_PATH + 'radiology.json')
RAINFALL_INTENSITY = load_json(ABSOLUTE_PATH + 'rainfall_intensity.json')
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

    # Loads Units
    init_multigraph(LOADS_UNITS)
    print('graph_args --base 1000 --lower-limit 0')
    init_base_parameters(LOADS_UNITS, COLORS)
    for field in LOADS_UNITS['fields']:
        print('{}.min 0'.format(field['id']))
    print('')

    # Radiological situation
    init_multigraph(RADIOLOGY)
    print('graph_args --base 1000 --lower-limit 0 --alt-y-grid')
    init_base_parameters(RADIOLOGY, COLORS)
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

    # retrieve performance parameters
    perform_container = soup.find_all('div', class_='latest-projects-list')[0]\
        .find_all('ul')[0].find_all('li')[0].find('div')
    perform_table_rows = perform_container.find('table').find_all('tr')
    perform_data = get_lists_of_values(perform_table_rows)

    units_list = []
    unit_1 = perform_data[1][1].split(' ', 1)[0]
    unit_2 = perform_data[2][1].split(' ', 1)[0]
    units_list.extend((unit_1, unit_2))

    # retrieve radiological situation
    request = urllib2.Request(config['radiology_url'], headers=config['headers'])
    response = urllib2.urlopen(request).read()
    radiology_soup = BeautifulSoup(response, 'html.parser')

    radiology_container = radiology_soup.find('div', class_='nucASKRO dataASKRO')
    radiology_items = radiology_container.find_all('div', class_='mesPoint')

    radiology_values = []
    for item in radiology_items:
        item_text = item.find('div', class_='nucItemData').text.strip()
        radiology_values.append(item_text.split(' ', 1)[0])

    # retrieve detail meteo parameters
    request = urllib2.Request(config['meteo_url'], headers=config['headers'])
    response = urllib2.urlopen(request).read()
    meteo_soup = BeautifulSoup(response, 'html.parser')

    meteo_detail_items = meteo_soup.find('div', class_='meteoData')\
        .find_all('div', class_='smallItem')

    meteo_detail_values = []
    for item in meteo_detail_items:
        item_text = item.find('div', class_='valueM').text.strip()
        meteo_detail_values.append(item_text)

    rainfall_intensity = meteo_detail_values[3]

    # Air temperature
    get_values_multigraph(air_temperature, AIR_TEMPERATURE)

    # Atmospheric pressure (convert hectopascals to millimeter of mercury)
    get_values_multigraph(atmospheric_pressure, ATM, 0.7500637554192)

    # Relative humidity
    get_values_multigraph(humidity, HUMIDITY)

    # Intensity of rainfall
    get_values_multigraph(rainfall_intensity, RAINFALL_INTENSITY)

    # Wind speed
    get_values_multigraph(wind_speed, WIND_SPEED)

    # Loads Units
    get_values_multigraph(units_list, LOADS_UNITS)

    # Radiological situation
    get_values_multigraph(radiology_values, RADIOLOGY)

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
        'radiology_url': os.environ.get(
            'radiology_url', 'http://www.xaec.org.ua/store/pages/ukr/nuccon'
        ),
        'meteo_url': os.environ.get(
            'meteo_url', 'http://www.xaec.org.ua/store/pages/ukr/meteo'
        ),
        'headers': {'User-Agent': user_agent}
    }

    khnpp_node(config)

if __name__ == '__main__':
    main()
