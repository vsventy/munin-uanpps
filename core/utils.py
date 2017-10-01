# -*- coding: utf-8 -*-
from __future__ import print_function

import json
import logging

logger = logging.getLogger('uanpps.nodes')


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
