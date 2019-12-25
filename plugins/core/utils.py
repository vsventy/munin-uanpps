import http.client
import json
import logging
import os
import requests

from fake_useragent import FakeUserAgentError
from fake_useragent import UserAgent

logger = logging.getLogger('uanpps-core')

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))


def load_json(full_path):
    with open(full_path, mode='r', encoding='utf-8') as json_file:
        return json.load(json_file)


def init_multigraph(config):
    print(f"multigraph {config['id']}")
    print(f"graph_title {config['title']}")
    print(f"graph_category {config['category']}")
    print(f"graph_vlabel {config['vlabel']}")
    if config['total']:
        print(f"graph_total {config['total']}")
    print(f"graph_scale {config['scale']}")


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
        try:
            id = field['id']
            print(f"{id}.label {field['label']}")
        except UnicodeEncodeError:
            logger.exception('Encoding error for field %s', id)
            continue
        if 'colour' in field:
            color_value = get_color_value(colors, field['colour'])
            print(f"{id}.colour {color_value}")
        if 'info' in field:
            print(f"{id}.info {field['info']}")


def get_values_multigraph(data, config, ratio=None):
    print(f"multigraph {config['id']}")
    for i, field in enumerate(config['fields']):
        id = field['id']
        if 'parameter' in list(field.keys()):
            if '.' in field['parameter']:
                parameter = field['parameter'].split('.')
                value = data[parameter[0]][parameter[1]]
            else:
                parameter = field['parameter']
                try:
                    value = data[parameter]
                except KeyError:
                    logger.exception('Parameter \'%s\' is missing', parameter)
                    break
        else:
            try:
                value = data[i] if isinstance(data, list) else data
            except IndexError:
                logger.exception('Mismatch data for field \'%s\': %s',
                                 id, data)
                break
        try:
            if isinstance(value, str):
                value = value.replace(',', '.')
            value = float(value)
        except (TypeError, ValueError):
            logger.exception('Invalid value for field \'%s\': %s', id, value)
            continue
        if ratio:
            value = float(value) * ratio
        print(f"{id}.value {value:.2f}")


def enable_requests_logging():
    http.client.HTTPConnection.debuglevel = 1
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


COLORS = load_json(ROOT_PATH + '/..' + '/data/colors.json')
