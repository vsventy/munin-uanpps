#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import requests
import json
import logging
import httplib
from fake_useragent import UserAgent


ABSOLUTE_PATH = os.path.dirname(os.path.realpath(__file__)) + "/data/rnpp/"

with open(ABSOLUTE_PATH + "loads_units.json") as json_file:
    LOADS_UNITS = json.load(json_file)

with open(ABSOLUTE_PATH + "loads_lines.json") as json_file:
    LOADS_LINES = json.load(json_file)

with open(ABSOLUTE_PATH + "air_temperature.json") as json_file:
    AIR_TEMPERATURE = json.load(json_file)

with open(ABSOLUTE_PATH + "humidity.json") as json_file:
    HUMIDITY = json.load(json_file)

with open(ABSOLUTE_PATH + "atm.json") as json_file:
    ATM = json.load(json_file)

with open(ABSOLUTE_PATH + "rainfall_intensity.json") as json_file:
    RAINFALL_INTENSITY = json.load(json_file)

with open(ABSOLUTE_PATH + "wind_speed.json") as json_file:
    WIND_SPEED = json.load(json_file)

with open(ABSOLUTE_PATH + "radiology.json") as json_file:
    RADIOLOGY = json.load(json_file)


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
    print "graph_args --base 1000 --lower-limit 0"
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
    print "graph_args --base 1000 --upper-limit 20 --lower-limit -20 HRULE:0#a1a1a1"
    print ""
    for field in AIR_TEMPERATURE["fields"]:
        print "%s.label %s" % (field["id"], field["label"])
    print ""

    # Relative humidity
    init_multigraph(HUMIDITY)
    print "graph_args --base 1000 --upper-limit 100 --lower-limit 0"
    print ""
    for field in HUMIDITY["fields"]:
        print "%s.label %s" % (field["id"], field["label"])
        print "%s.colour %s" % (field["id"], field["colour"])
    print ""

    # Atmospheric pressure
    init_multigraph(ATM)
    print "graph_args --base 1000"
    print ""
    for field in ATM["fields"]:
        print "%s.label %s" % (field["id"], field["label"])
        print "%s.colour %s" % (field["id"], field["colour"])
        print "%s.type GAUGE" % (field["id"])
        print "%s.draw AREA" % (field["id"])
    print ""

    # Intensity of rainfall
    init_multigraph(RAINFALL_INTENSITY)
    print "graph_args --base 1000 --upper-limit 100 --lower-limit 0"
    print ""
    for field in RAINFALL_INTENSITY["fields"]:
        print "%s.label %s" % (field["id"], field["label"])
        print "%s.colour %s" % (field["id"], field["colour"])
        print "%s.type GAUGE" % (field["id"])
        print "%s.draw AREA" % (field["id"])
    print ""

    # Wind speed
    init_multigraph(WIND_SPEED)
    print "graph_args --base 1000 --upper-limit 50 --lower-limit 0"
    print ""
    for field in WIND_SPEED["fields"]:
        print "%s.label %s" % (field["id"], field["label"])
        print "%s.draw LINE%s" % (field["id"], field["thickness"])
        print "%s.colour %s" % (field["id"], field["colour"])
    print ""

    # Radiological situation
    init_multigraph(RADIOLOGY)
    print "graph_args --base 1000 --lower-limit 0 --alt-y-grid"
    print ""
    for field in RADIOLOGY["fields"]:
        print "%s.label %s" % (field["id"], field["label"])
        print "%s.info %s" % (field["id"], field["info"])
    print ""

def init_multigraph(config):
    print "multigraph %s" % (config["id"])
    print "graph_title %s" % (config["title"])
    print "graph_category %s" % (config["category"])
    print "graph_vlabel %s" % (config["vlabel"])
    if config["total"]:
        print "graph_total %s" % (config["total"])
    print "graph_scale %s" % (config["scale"])


def get_values_multigraph(data, config, ratio=None):
    print "multigraph %s" % (config["id"])
    for field in config["fields"]:
        if ratio is None:
            value = data[field["parameter"]]
        else:
            value = float(data[field["parameter"]]) * ratio
        print "%s.value %.2f" % (field["id"], value)


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

    # Relative humidity
    get_values_multigraph(data, HUMIDITY)

    # Atmospheric pressure (convert hectopascals to millimeter of mercury)
    get_values_multigraph(data, ATM, 0.7500637554192)

    # Intensity of rainfall
    get_values_multigraph(data, RAINFALL_INTENSITY)

    # Wind speed
    get_values_multigraph(data, WIND_SPEED)

    # Wind speed
    get_values_multigraph(data, RADIOLOGY)

    # Radiological situation
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
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'

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
