"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

"""
Initialize HAGW.
"""

import sys, os, logging
import logging.config
import settings


# setup logging
logging.config.dictConfig(settings.LOGGING_CONFIG)
# use HAGW default logger for general logging
__HAGW_LOGGER__ = logging.getLogger('hagw.default')


