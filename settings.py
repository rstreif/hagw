"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

"""
Settings for Home Automation Gatewey
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(__file__)

# Logging settings
LOGGING_DIR = os.path.join(BASE_DIR, 'hagw.log')
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
             'level': 'DEBUG',
             'class': 'logging.StreamHandler',
             'formatter': 'simple',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOGGING_DIR,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'hagw.default': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'hagw.console': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# General Configuration
MAIN_LOOP_INTERVAL = 5

# RVI Configuration
RVI_SERVICE_EDGE_URL = 'http://192.168.100.101:8801'
RVI_SEND_TIMEOUT = 10

# TV Configuration
TV_SERVICE_EDGE_URL = 'tcp://192.168.100.101:11264'
TV_SEND_TIMEOUT = 10


# HAGW Core Services
#CORE_SERVER_CALLBACK_URL = 'http://127.0.0.1:20000'
CORE_SERVER_CALLBACK_URL = 'http://192.168.100.100:20000'
CORE_SERVER_SERVICE_ID = '/core'
CORE_SERVER_RVI_DOMAIN = 'jlr.com/smarthome/myhome'

# Pixie Adjacent Server Configuration
PIXIE_SERVER_ENABLE = True
#PIXIE_SERVER_CALLBACK_URL = 'http://127.0.0.1:20001'
PIXIE_SERVER_CALLBACK_URL = 'http://192.168.100.100:20001'
PIXIE_SERVER_SERVICE_ID = '/pixie'
PIXIE_SERVER_ADJACENT_URL = 'http://192.168.100.101:3000'
PIXIE_SERVER_REFERENCE_POINTS = ['D78D11E03AC8', 'DC955EBFD1C1']
PIXIE_SERVER_HOME_DIMENSIONS = {'x': 350, 'y': 300}

# Thingcontrol Server Configuration
TC_SERVER_ENABLE = True
#TC_SERVER_CALLBACK_URL = 'http://127.0.0.1:20002'
TC_SERVER_CALLBACK_URL = 'http://192.168.100.100:20002'
TC_SERVER_SERVICE_ID = '/thingcontrol'
TC_SERVER_GATEWAY_URL = 'http://192.168.100.151:9091'
TC_SERVER_GATEWAY_DOMAIN = '/hlg/thingcontrol'

# Usermessage Server Configuration
UM_SERVER_ENABLE = True
#UM_SERVER_CALLBACK_URL = 'http://127.0.0.1:20003'
UM_SERVER_CALLBACK_URL = 'http://192.168.100.100:20003'
UM_SERVER_SERVICE_ID = '/message'

# Vehicle Server Configuration
VH_SERVER_ENABLE = True
#VH_SERVER_CALLBACK_URL = 'http://127.0.0.1:20004'
VH_SERVER_CALLBACK_URL = 'http://192.168.100.100:20004'
VH_SERVER_SERVICE_ID = '/vehicle'
