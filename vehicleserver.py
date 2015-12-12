"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

"""
Vehicle Server.
"""

import os, threading, base64, socket
import time, httplib, json, math
from urlparse import urlparse
from rvijsonrpc import RVIJSONRPCServer

import settings

logger = None
service_edge = None
transaction_id = 0

# Vehicle Callback Server
class VehicleCallbackServer(threading.Thread):
    """
    RPC server thread responding to vehicle callbacks from the RVI framework
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
        url = urlparse(settings.VH_SERVER_CALLBACK_URL)
        self.localServer =  RVIJSONRPCServer(addr=((url.hostname, url.port)), logRequests=False)
        self.localServer.register_function(statusReport, settings.VH_SERVER_SERVICE_ID + "/statusreport")
        
    def register_services(self):
        # register services with RVI framework
        result = service_edge.register_service(service = settings.VH_SERVER_SERVICE_ID + '/statusreport',
                                               network_address = settings.VH_SERVER_CALLBACK_URL)
        logger.info('Vehicle Server Service Registration: %s', result['service'])

    def run(self):
        self.localServer.serve_forever()
        
    def shutdown(self):
        self.localServer.shutdown()
        self.localServer.server_close()


# Callback functions
def statusReport(vin, timestamp, data):
    """
    Receive a status report from a vehicle
    :param: vin: vehicle identification number
    :param: timestamp: date and time in ISO 8601 format
    :param: data: status report data
    """
    logger.info('Vehicle Callback Server: statusReport: vin: %s, timestamp: %s, data: %s.', vin, timestamp, data)
    
    for channel in data:
        key = channel['channel']
        value = channel['value']
        if key == 'seats':
            frontleft = value['frontleft']
            frontright = value['frontright']
        elif key == 'trunk':
            if value == 'open':
                msg = '{ "command": "vehicleIncursion", "type": "hatch" }'
                sendTV(msg)
        elif key == 'speed':
            speed = float(value)
        elif key == 'odometer':
            odometer = float(value)
    
    return {u'status': 0}

def sendTV(message):
    """
    Send a message to the smarthome TV.
    :param: message: message
    """
    logger.info('Sending to TV: %s, message: %s', settings.TV_SERVICE_EDGE_URL, message)
    try:
        url = urlparse(settings.TV_SERVICE_EDGE_URL)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((url.hostname, url.port))
        sock.send(message)
        sock.close()
    except Exception as e:
        logger.error('Sending to TV failed: %s', e)

