"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

"""
User Message Server.
"""

import os, threading, base64
import time, httplib, json, math
from urlparse import urlparse
from rvijsonrpc import RVIJSONRPCServer

import settings

logger = None
service_edge = None
transaction_id = 0

# Usermessage Callback Server
class UsermessageCallbackServer(threading.Thread):
    """
    RPC server thread responding to user message callbacks from the RVI framework
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
        url = urlparse(settings.UM_SERVER_CALLBACK_URL)
        self.localServer =  RVIJSONRPCServer(addr=((url.hostname, url.port)), logRequests=False)
        self.localServer.register_function(showUserMessage, settings.UM_SERVER_SERVICE_ID + "/showusermessage")
        self.localServer.register_function(cancelUserMessage, settings.UM_SERVER_SERVICE_ID + "/canelusermessage")
        
    def register_services(self):
        # register services with RVI framework
        result = service_edge.register_service(service = settings.UM_SERVER_SERVICE_ID + '/showusermessage',
                                               network_address = settings.UM_SERVER_CALLBACK_URL)
        logger.info('Usermessage Service Registration: showusermessage service name: %s', result['service'])
        result = service_edge.register_service(service = settings.UM_SERVER_SERVICE_ID + '/cancelusermessage',
                                               network_address = settings.UM_SERVER_CALLBACK_URL)
        logger.info('Usermessage Service Registration: cancelusermessage service name: %s', result['service'])

    def run(self):
        self.localServer.serve_forever()
        
    def shutdown(self):
        self.localServer.shutdown()
        self.localServer.server_close()


# Callback functions
def showUserMessage(messageid, displays, messagetext):
    """
    Show a message to users on displays in the house.
    :param: messageid: unique id of the message
    :param: displays: list of displays to show the message on
    :param: messagetext: text of the message
    """
    logger.info('Usermessage Callback Server: showUserMessage: messageid: %s, displays: %s, message: %s.', messageid, displays, messagetext)
    return {u'status': 0}

def cancelUserMessage(messageid, displays):
    """
    Cancel a previously shown message on one or more displays
    :param: messageid: unique id of the message
    :param: displays: list of displays to remove the message from
    """
    logger.info('Usermessage Callback Server: cancelUserMessage: messageid: %s, displays: %s, message: %s.', messageid, displays, messagetext)
    return {u'status': 0}
