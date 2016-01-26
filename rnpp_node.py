#!/usr/bin/env python
import os
import sys


def display_config(config):
    print("")


def rnpp_node(config):
    print("")

if __name__ == "__main__":
    # Init config
    CONFIG = {
        'url': os.environ.get('url', '')
    }

    # Display config
    if len(sys.argv) > 1 and sys.argv[1] == 'config':
        display_config(CONFIG)
        sys.exit(0)
    rnpp_node(CONFIG)
