#!/usr/bin/env python
import os
import sys
import requests
import json
import logging
import httplib
from fake_useragent import UserAgent


def init_logging():
    httplib.client.HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests.propagate = True


def display_config():
    print "multigraph loads_units"
    print "graph_title Rivne NPP Loads Units (in MW)"
    print "graph_category performance"
    print "graph_scale no"
    print "graph_args --base 1000"
    print "graph_vlabel megawatts"
    print "graph_total Total plant load"
    print ""
    print "unit1.min 0"
    print "unit1.label Unit 1"
    print "unit2.min 0"
    print "unit2.label Unit 2"
    print "unit3.min 0"
    print "unit3.label Unit 3"
    print "unit4.min 0"
    print "unit4.label Unit 4"


def rnpp_node(config):
    url = "http://%s/informer/sprut.php" % (config['host'])

    response = requests.get(url=url, params=config['params'],
                            headers=config["headers"])
    response.encoding = 'utf-8'
    data = json.loads(response.text)

    print "multigraph loads_units"
    print "unit1.value %s" % (data["R_N_B1"])
    print "unit2.value %s" % (data["R_N_B2"])
    print "unit3.value %s" % (data["R_N_B3"])
    print "unit4.value %s" % (data["R_N_B4"])
    print ""


def main():
    # Init User-Agent
    user_agent = UserAgent()
    user_agent.update()

    # Init config
    config = {
        'host': os.environ.get('host', 'www.rnpp.rv.ua'),
        'logging': os.environ.get('logging', 'no'),
        'params': {'value': 'sprutbase'},
        'headers': {'User-Agent': user_agent.random}
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
