#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
    # Loads Units
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
    print ""
    # Load on the lines
    print "multigraph loads_lines"
    print "graph_title Rivne NPP Load on the lines (in MWh)"
    print "graph_category performance"
    print "graph_scale no"
    print "graph_args --base 1000"
    print "graph_vlabel megawatt-hours"
    print ""
    print "l_kyiv.min 0"
    print "l_kyiv.label AL-750kV Kyiv"
    print "l_zu.min 0"
    print "l_zu.label AL-750kV Western-Ukrainian"
    print "l_grabiv.min 0"
    print "l_grabiv.label AL-330kV Hrabiv"
    print "l_rivne.min 0"
    print "l_rivne.label AL-330kV Rivne"
    print "l_lutsk.min 0"
    print "l_lutsk.label AL-330kV Lutsk"
    print "l_kovel.min 0"
    print "l_kovel.label AL-330kV Kovel"
    print "l_vladimirets.min 0"
    print "l_vladimirets.label AL-110kV Volodymyrets"
    print "l_hinochi.min 0"
    print "l_hinochi.label AL-110kV Hinochi"
    print "l_kuznetsovsk.min 0"
    print "l_kuznetsovsk.label AL-110kV Kuznetsovsk"
    print "l_manevichi.min 0"
    print "l_manevichi.label AL-110kV Manevychi"
    print "l_komarovo.min 0"
    print "l_komarovo.label AL-110kV Komarovo"
    print ""
    # Meteo
    print "multigraph air_temperature"
    print "graph_title Rivne NPP Air temperature (in Degrees Celsius)"
    print "graph_category meteo"
    print "graph_scale no"
    print "graph_args --base 1000 --upper-limit 20 --lower-limit -20"
    print "graph_vlabel degrees Celsius"
    print ""
    print "air_temp.label Air temperature"
    print ""


def rnpp_node(config):
    url = "http://%s/informer/sprut.php" % (config['host'])

    response = requests.get(url=url, params=config['params1'],
                            headers=config["headers"])
    response.encoding = 'utf-8'
    data = json.loads(response.text)

    print "multigraph loads_units"
    print "unit1.value %s" % (data["R_N_B1"])
    print "unit2.value %s" % (data["R_N_B2"])
    print "unit3.value %s" % (data["R_N_B3"])
    print "unit4.value %s" % (data["R_N_B4"])

    print "multigraph air_temperature"
    print "air_temp.value %s" % (data["M_TA_1M_AVG"])

    response = requests.get(url=url, params=config['params2'],
                            headers=config["headers"])
    response.encoding = 'utf-8'
    data = json.loads(response.text)["N"]
    print "multigraph loads_lines"
    print "l_kyiv.value %s" % (data["L_KYIV"])
    print "l_zu.value %s" % (data["L_ZU"])
    print "l_grabiv.value %s" % (data["L_GRABIV"])
    print "l_rivne.value %s" % (data["L_RIVNE"])
    print "l_lutsk.value %s" % (data["L_LUTSK"])
    print "l_kovel.value %s" % (data["L_KOVEL"])
    print "l_vladimirets.value %s" % (data["L_VLADIMIRETS"])
    print "l_hinochi.value %s" % (data["L_HINOCHI"])
    print "l_kuznetsovsk.value %s" % (data["L_KUZNETSOVSK"])
    print "l_manevichi.value %s" % (data["L_MANEVICHI"])
    print "l_komarovo.value %s" % (data["L_KOMAROVO"])
    sys.exit(0)


def main():
    # Init User-Agent
    user_agent = UserAgent()
    user_agent.update()

    # Init config
    config = {
        'host': os.environ.get('host', 'www.rnpp.rv.ua'),
        'logging': os.environ.get('logging', 'no'),
        'params1': {'value': 'sprutbase'},
        'params2': {'value': 'rnpp_n'},
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
