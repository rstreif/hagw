"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

"""
Core Server. Used to control functionality of the Home Automation Gateway
itself rather than devices it connects to.
"""

import os, threading, base64
import time, httplib, json, math
from urlparse import urlparse
from rvijsonrpc import RVIJSONRPCServer

import settings

logger = None
service_edge = None
transaction_id = 0

# Core Callback Server
class CoreCallbackServer(threading.Thread):
    """
    RPC server thread responding to core callbacks from the RVI framework
    """
    
    def __init__(self, _logger, _service_edge):
        global logger
        global service_edge
        logger = _logger
        service_edge = _service_edge
        threading.Thread.__init__(self)
        self.init_callback_server()
        self.register_services()

    def init_callback_server(self):
        # initialize RPC server and register callback functions
        url = urlparse(settings.CORE_SERVER_CALLBACK_URL)
        self.localServer =  RVIJSONRPCServer(addr=((url.hostname, url.port)), logRequests=False)
        self.localServer.register_function(ping, settings.CORE_SERVER_SERVICE_ID + "/ping")
        
    def register_services(self):
        # register services with RVI framework
        result = service_edge.register_service(service = settings.CORE_SERVER_SERVICE_ID + '/ping',
                                               network_address = settings.CORE_SERVER_CALLBACK_URL)
        logger.info('Core Server: Service Registration: ping service name: %s', result)
        return result

    def run(self):
        self.localServer.serve_forever()
        
    def shutdown(self):
        self.localServer.shutdown()
        self.localServer.server_close()


# Callback functions
    def ping(message):
        logger.info('Core Server: Ping: "%s"', message)

def ping(message):
    """
    Ping the HAGW with a message.
    :param: message: ping message, will just be logged
    """
    logger.info('Core Callback Server: ping: message: %s', message)
    return {u'status': 0}
