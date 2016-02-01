#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import requests
import json
import logging
import httplib
from fake_useragent import UserAgent

with open("data/rnpp/loads_units.json") as json_file:
    LOADS_UNITS = json.load(json_file)

with open("data/rnpp/loads_lines.json") as json_file:
    LOADS_LINES = json.load(json_file)

with open("data/rnpp/air_temperature.json") as json_file:
    AIR_TEMPERATURE = json.load(json_file)


def init_logging():
    httplib.HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests.propagate = True


def display_config():
    # Loads Units
    init_multigraph(LOADS_UNITS)
    print "graph_args --base 1000"
    print ""
    for field in LOADS_UNITS["fields"]:
        print "%s.min 0" % (field["id"])
        print "%s.label %s" % (field["id"], field["label"])
    print ""

    # Load on the lines
    init_multigraph(LOADS_LINES)
    print "graph_args --base 1000"
    print ""
    for field in LOADS_LINES["fields"]:
        print "%s.min 0" % (field["id"])
        print "%s.label %s" % (field["id"], field["label"])
    print ""

    # Air temperature
    init_multigraph(AIR_TEMPERATURE)
    print "graph_args --base 1000 --upper-limit 20 --lower-limit -20"
    print ""
    for field in AIR_TEMPERATURE["fields"]:
        print "%s.label %s" % (field["id"], field["label"])
    print ""


def init_multigraph(config):
    print "multigraph %s" % (config["id"])
    print "graph_title %s" % (config["title"])
    print "graph_category %s" % (config["category"])
    print "graph_vlabel %s" % (config["vlabel"])
    if not config["total"]:
        print "graph_total %s" % (config["total"])
    print "graph_scale %s" % (config["scale"])


def get_values_multigraph(data, config):
    print "multigraph %s" % (config["id"])
    for field in config["fields"]:
        print "%s.value %s" % (field["id"], data[field["parameter"]])


def rnpp_node(config):
    url = "http://%s/informer/sprut.php" % (config['host'])

    response = requests.get(url=url, params=config['params1'],
                            headers=config["headers"])
    response.encoding = 'utf-8'
    data = json.loads(response.text)

    # Loads Units
    get_values_multigraph(data, LOADS_UNITS)

    # Air temperature
    get_values_multigraph(data, AIR_TEMPERATURE)

    # Load on the lines
    response = requests.get(url=url, params=config['params2'],
                            headers=config["headers"])
    response.encoding = 'utf-8'
    data = json.loads(response.text)["N"]
    get_values_multigraph(data, LOADS_LINES)

    sys.exit(0)


def main():
    # Init User-Agent
    try:
        user_agent = UserAgent()
        user_agent.update()
        user_agent = user_agent.random
    except:
        user_agent = 'Default Browser'

    # Init config
    config = {
        'host': os.environ.get('host', 'www.rnpp.rv.ua'),
        'logging': os.environ.get('logging', 'no'),
        'params1': {'value': 'sprutbase'},
        'params2': {'value': 'rnpp_n'},
        'headers': {'User-Agent': user_agent}
    }

    # Init logging
    if config["logging"] == "yes":
        init_logging()

    # Display config
    if len(sys.argv) > 1 and sys.argv[1] == "config":
        display_config()
        sys.exit(0)
    rnpp_node(config)

if __name__ == "__main__":
    main()
