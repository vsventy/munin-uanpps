#!/usr/bin/env python3
import ast
import json
import logging
import os
import requests
import sys

from core.utils import enable_requests_logging
from core.utils import get_random_user_agent
from core.utils import get_values_multigraph
from core.utils import init_base_parameters
from core.utils import init_multigraph
from core.utils import load_json
from core.utils import COLORS

logger = logging.getLogger('rnpp-node')

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
ABSOLUTE_PATH = ROOT_PATH + '/data/rnpp/'

AIR_TEMPERATURE = load_json(ABSOLUTE_PATH + 'air_temperature.json')
HUMIDITY = load_json(ABSOLUTE_PATH + 'humidity.json')
ATM = load_json(ABSOLUTE_PATH + 'atm.json')
RAINFALL_INTENSITY = load_json(ABSOLUTE_PATH + 'rainfall_intensity.json')
WIND_SPEED = load_json(ABSOLUTE_PATH + 'wind_speed.json')
RADIOLOGY = load_json(ABSOLUTE_PATH + 'radiology.json')
PRODUCTION_ELECTRICITY = load_json(ABSOLUTE_PATH + 'production_electricity.json')


def display_config():
    # Air temperature
    init_multigraph(AIR_TEMPERATURE)
    print('graph_args --base 1000 --upper-limit 20 --lower-limit -20 '
          'HRULE:0#a1a1a1')
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
        print(f"{field['id']}.draw AREA")
    print('')

    # Intensity of rainfall
    init_multigraph(RAINFALL_INTENSITY)
    print('graph_args --base 1000 --upper-limit 5 --lower-limit 0')
    init_base_parameters(RAINFALL_INTENSITY, COLORS)
    for field in RAINFALL_INTENSITY['fields']:
        print(f"{field['id']}.draw AREA")
    print('')

    # Wind speed
    init_multigraph(WIND_SPEED)
    print('graph_args --base 1000 --upper-limit 20 --lower-limit 0')
    init_base_parameters(WIND_SPEED, COLORS)
    for field in WIND_SPEED['fields']:
        print(f"{field['id']}.draw LINE{field['thickness']}")
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
        print(f"{field['id']}.draw AREA")
    print('')


def rnpp_node(config):
    logger.info('Start rnpp-node (main)')

    url = 'https://{}/informer/sprut.php'.format(config['host'])

    proxies = {}
    if config['proxies']:
        proxies['http'] = config['proxies']
        proxies['https'] = config['proxies']

    response = requests.get(
        url=url,
        params=config['params1'],
        headers=config['headers'],
        timeout=config['timeout'],
        proxies=proxies
    )
    response.encoding = 'utf-8'
    data = json.loads(response.text)

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

    response = requests.get(
        url=url,
        params=config['params3'],
        headers=config['headers'],
        timeout=config['timeout'],
        proxies=proxies
    )
    response.encoding = 'utf-8'
    try:
        data = json.loads(response.text)
    except ValueError:
        logger.error('When decode data: url=%s, params=%s',
                     url, config['params3'])

    # Production of electricity for current month
    get_values_multigraph(data, PRODUCTION_ELECTRICITY, 0.001)

    logger.info('Finish rnpp-node (main)')
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
        'host': os.environ.get('host', 'www.rnpp.rv.ua'),
        'logging': os.environ.get('uanpps_logging', 'False'),
        'proxies': os.environ.get('proxies', ''),
        'timeout': os.environ.get('timeout', 10),
        'params1': {'value': 'sprutbase'},
        'params2': {'value': 'rnpp_n'},
        'params3': {'value': 'rnpp_current_state_sm'},
        'headers': {'User-Agent': user_agent}
    }

    # turn on requests logging
    if ast.literal_eval(config['logging']):
        enable_requests_logging()

    rnpp_node(config)


if __name__ == '__main__':
    main()
