"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

"""
Pixie Adjacent Server (PAS) services.
"""

import os, threading, base64, socket
import time, httplib, json, math
from urlparse import urlparse
from rvijsonrpc import RVIJSONRPCServer

import settings

logger = None
service_edge = None

# Pixie Callback Server
class PixieCallbackServer(threading.Thread):
    """
    RPC server thread responding to Pixie callbacks from the RVI framework
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
        url = urlparse(settings.PIXIE_SERVER_CALLBACK_URL)
        self.localServer =  RVIJSONRPCServer(addr=((url.hostname, url.port)), logRequests=False)
        self.localServer.register_function(getRawItemLocations, settings.PIXIE_SERVER_SERVICE_ID + "/getrawitemlocations")
        self.localServer.register_function(getItemLocations, settings.PIXIE_SERVER_SERVICE_ID + "/getitemlocations")
        
    def register_services(self):
        # register services with RVI framework
        result = service_edge.register_service(service = settings.PIXIE_SERVER_SERVICE_ID + '/getrawitemlocations',
                                               network_address = settings.PIXIE_SERVER_CALLBACK_URL)
        logger.info('PIXIE Service Registration: Get Raw Item Locations service name: %s', result['service'])
        result = service_edge.register_service(service = settings.PIXIE_SERVER_SERVICE_ID + '/getitemlocations',
                                               network_address = settings.PIXIE_SERVER_CALLBACK_URL)
        logger.info('PIXIE Service Registration: Get Item Locations service name: %s', result['service'])

    def run(self):
        self.localServer.serve_forever()
        
    def shutdown(self):
        self.localServer.shutdown()
        self.localServer.server_close()


# Callback functions
def getRawItemLocations(tags, sendto):
    """
    Return the locations of the items as reported by the PIXI API.
    :param: tags: list of tags (regular expressions ok)
    :param: sendto: RVI service to send response to
    """
    logger.info('PIXIE Callback Server: getRawItemLocations: tags: %s, sento: %s.', tags, sendto)
    pstatus = getPixieStatus()
    sendMessage(sendto, pstatus)
    return {u'status': 0}

def getItemLocations(tags, sendto):
    """
    Return the locations of the items relative to the reference points.
    :param: tags: list of tags (regular expressions ok)
    :param: sendto: RVI service to send response to
    """
    logger.info('PIXIE Callback Server: getItemLocations: tags: %s, sento: %s.', tags, sendto)
    ploc = getPixieLocations()
    sendMessage(sendto, ploc)
    return {u'status': 0}

    
# private functions
def getPixieStatus():
    """
    Connect to the Pixie Adjacant Server and get the tag status information.
    """
    try:
        url = urlparse(settings.PIXIE_SERVER_ADJACENT_URL)
        con = httplib.HTTPConnection(url.hostname, url.port)
        con.request('GET', '/getPixieStatus')
        res = con.getresponse()
        data = json.loads(res.read())
    except Exception as e:
        logger.error('PIXIE Callback Server: getPixieStatus: Exception: %s', e)
        data = None
    return data

    
def getPixieLocations():
    """
    Calibrate Pixie tag locations based on two reference points and return
    the coordinates.
    """
    # get Pixie status
    pstatus = getPixieStatus()
    if pstatus == None:
		return None
    # get refernece points from data
    loc = {}
    prefs = {}
    points = {}
    try:
        for i, p in enumerate(settings.PIXIE_SERVER_REFERENCE_POINTS):
            pref = {}
            pp = pstatus['pixiePoints'][p]
            pref['ref'] = pp
            pref['distn'] = 0
            pref['distp'] = 0
            if i < len(settings.PIXIE_SERVER_REFERENCE_POINTS) - 1:
                pref['distn'] = pp['range'][settings.PIXIE_SERVER_REFERENCE_POINTS[i+1]]
            if i > 0:
                pref['distp'] = pp['range'][settings.PIXIE_SERVER_REFERENCE_POINTS[i-1]]
            prefs[p] = pref
        for key, value in pstatus['pixiePoints'].iteritems():
            if key not in settings.PIXIE_SERVER_REFERENCE_POINTS:
                point = {}
                point['status'] = value['status']
                point['tagName'] = value['tagName']
                point['tagColor'] = value['tagColor']
                c = {}
                if value['status'] == 'Connected':
                    dr1 = value['range'][settings.PIXIE_SERVER_REFERENCE_POINTS[0]]
                    dr2 = value['range'][settings.PIXIE_SERVER_REFERENCE_POINTS[1]]
                    d = prefs[settings.PIXIE_SERVER_REFERENCE_POINTS[0]]['distn']
                    c['x'], c['y'] = calculateCoordinates(dr1, dr2, d)
                point['coordinates'] = c
                points[key] = point
    except Exception as e:
        logger.error('PIXIE Callback Server: calibratePixieLocations: Exception: %s', e)
    loc['username'] = pstatus['username']
    loc['pixiePoints'] = points
    loc['dimensions'] = settings.PIXIE_SERVER_HOME_DIMENSIONS
    return loc
    
    
def calculateCoordinates(dr1, dr2, d):
    """
    Calculate the x and y coordinates of a point based on its distance
    to two reference points.
    :param dr1: distance of the point to reference point 1
    :param dr2: distance of the point to reference point 2
    :param d: distance between the two reference points
    """
    logger.debug('PIXIE Callback Server: calculateCoordinates: dr1: %d, dr2: %d, d: %d', dr1, dr2, d)
    try:
        x = ((dr1 * dr1) - (dr2 * dr2) + (d * d)) / (2 * d)
        y =  math.sqrt((dr1 * dr1) - (x * x))
        logger.debug('PIXIE Callback Server: calculateCoordinates: x: %f, y: %f', x, y)
        return (int(round(x)), int(round(y)))
    except Exception as e: raise


def sendMessage(sendto, message):
    """
    Send message to recipient via RVI.
    :param: sendto: recipient RVI service
    :param: meessage: message as RVI parameter block
    """
    
    logger.info('PIXIE Callback Server: sending message: %s to %s', message, sendto)
    
    # send message
    try:
        service_edge.message(service_name = sendto,
                           timeout = int(time.time()) + settings.RVI_SEND_TIMEOUT,
                           parameters = [message])
    except Exception as e:
        logger.error('PIXIE Callback Server: cannot send message: %s', e)
        return False
    
    logger.info('PIXIE Callback Server: successfully sent message: to %s', sendto)

    return True


