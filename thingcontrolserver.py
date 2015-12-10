"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

"""
Thingcontrol (HomeLake) Server.
"""

import os, threading, base64
import time, httplib, json, math
from urlparse import urlparse
from rvijsonrpc import RVIJSONRPCServer

import settings

logger = None
service_edge = None
transaction_id = 0

# Thingcontrol Callback Server
class ThingcontrolCallbackServer(threading.Thread):
    """
    RPC server thread responding to Thingcontrol callbacks from the RVI framework
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
        url = urlparse(settings.TC_SERVER_CALLBACK_URL)
        self.localServer =  RVIJSONRPCServer(addr=((url.hostname, url.port)), logRequests=False)
        self.localServer.register_function(getDeviceStatus, settings.TC_SERVER_SERVICE_ID + "/getdevicestatus")
        self.localServer.register_function(setHueLighting, settings.TC_SERVER_SERVICE_ID + "/sethuelighting")
        self.localServer.register_function(setOutlet, settings.TC_SERVER_SERVICE_ID + "/setoutlet")
        self.localServer.register_function(setSwitch, settings.TC_SERVER_SERVICE_ID + "/setswitch")
        self.localServer.register_function(setLock, settings.TC_SERVER_SERVICE_ID + "/setlock")
        self.localServer.register_function(setDimmer, settings.TC_SERVER_SERVICE_ID + "/setdimmer")
        self.localServer.register_function(setThermostat, settings.TC_SERVER_SERVICE_ID + "/setthermostat")
        self.localServer.register_function(secureHome, settings.TC_SERVER_SERVICE_ID + "/securehome")
        
    def register_services(self):
        # register services with RVI framework
        result = service_edge.register_service(service = settings.TC_SERVER_SERVICE_ID + '/getdevicestatus',
                                               network_address = settings.TC_SERVER_CALLBACK_URL)
        logger.info('Thingcontrol Service Registration: getdevicestatus service name: %s', result['service'])
        result = service_edge.register_service(service = settings.TC_SERVER_SERVICE_ID + '/sethuelighting',
                                               network_address = settings.TC_SERVER_CALLBACK_URL)
        logger.info('Thingcontrol Service Registration: sethuelighting service name: %s', result['service'])
        result = service_edge.register_service(service = settings.TC_SERVER_SERVICE_ID + '/setoutlet',
                                               network_address = settings.TC_SERVER_CALLBACK_URL)
        logger.info('Thingcontrol Service Registration: setoutlet service name: %s', result['service'])
        result = service_edge.register_service(service = settings.TC_SERVER_SERVICE_ID + '/setswitch',
                                               network_address = settings.TC_SERVER_CALLBACK_URL)
        logger.info('Thingcontrol Service Registration: setswitch service name: %s', result['service'])
        result = service_edge.register_service(service = settings.TC_SERVER_SERVICE_ID + '/setlock',
                                               network_address = settings.TC_SERVER_CALLBACK_URL)
        logger.info('Thingcontrol Service Registration: setlock service name: %s', result['service'])
        result = service_edge.register_service(service = settings.TC_SERVER_SERVICE_ID + '/setdimmer',
                                               network_address = settings.TC_SERVER_CALLBACK_URL)
        logger.info('Thingcontrol Service Registration: setdimmer service name: %s', result['service'])
        result = service_edge.register_service(service = settings.TC_SERVER_SERVICE_ID + '/setthermostat',
                                               network_address = settings.TC_SERVER_CALLBACK_URL)
        logger.info('Thingcontrol Service Registration: setthermostat service name: %s', result['service'])
        result = service_edge.register_service(service = settings.TC_SERVER_SERVICE_ID + '/securehome',
                                               network_address = settings.TC_SERVER_CALLBACK_URL)
        logger.info('Thingcontrol Service Registration: setthermostat service name: %s', result['service'])

    def run(self):
        self.localServer.serve_forever()
        
    def shutdown(self):
        self.localServer.shutdown()
        self.localServer.server_close()


# Callback functions
def getDeviceStatus(devices, sendto):
    """
    Return the status of the home automation devices.
    :param: devices: list of devices (wildcards ok)
    :param: sendto: RVI service to send the response to
    """
    logger.info('Thingcontrol Callback Server: getDeviceStatus: devices: %s, sento: %s.', devices, sendto)
    return {u'status': 0}

def setHueLighting(deviceid, control):
    """
    Control hue lighting device.
    :param: deviceid: id of the hue lighting device
    :param: control: hue settings
    """
    logger.info('Thingcontrol Callback Server: setHueLighting: deviceid: %s, control: %s.', deviceid, control)
    data = initData()
    data['device_id'] = deviceid
    data['device_type'] = 'zb_hue_bulb'
    data['msgTyp'] = 'zb_hue_msg'
    data['control'] = control
    sendCommand('huelighting', data)
    return {u'status': 0}

def setOutlet(deviceid, control):
    """
    Control wall outlet device.
    :param: deviceid: id of the outlet device
    :param: control: state
    """
    logger.info('Thingcontrol Callback Server: setOutlet: deviceid: %s, control: %s.', deviceid, control)
    data = initData()
    data['device_id'] = deviceid
    data['device_type'] = 'zb-smartplug'
    data['msgTyp'] = 'zb_smartplug_msg'
    data['control'] = control
    sendCommand('wallsmartoutlet', data)
    return {u'status': 0}

def setSwitch(deviceid, control):
    """
    Control switch device.
    :param: deviceid: id of the switch device
    :param: control: state
    """
    logger.info('Thingcontrol Callback Server: setSwitch: deviceid: %s, control: %s.', deviceid, control)
    data = initData()
    data['device_id'] = deviceid
    data['device_type'] = 'zb-smartswitch'
    data['msgTyp'] = 'zb_smartswitch_msg'
    data['control'] = control
    sendCommand('smartswitch', data)
    return {u'status': 0}

def setLock(deviceid, control):
    """
    Control door lock device.
    :param: deviceid: id of the lock device
    :param: control: state
    """
    logger.info('Thingcontrol Callback Server: setLock: deviceid: %s, control: %s.', deviceid, control)
    data = initData()
    data['device_id'] = deviceid
    data['device_type'] = 'zb_door_lock'
    data['msgTyp'] = 'zb_door_msg'
    data['control'] = control
    sendCommand('doorlock', data)
    return {u'status': 0}

def setDimmer(deviceid, control):
    """
    Control dimmer device.
    :param: deviceid: id of the dimmer device
    :param: control: state
    """
    logger.info('Thingcontrol Callback Server: setDimmer: deviceid: %s, control: %s.', deviceid, control)
    data = initData()
    data['device_id'] = deviceid
    data['device_type'] = 'zb-dimmer'
    data['msgTyp'] = 'zb_dimmer_msg'
    data['control'] = control
    sendCommand('dimmer', data)
    return {u'status': 0}

def setThermostat(deviceid, control):
    """
    Control thermostat device.
    :param: deviceid: id of the thermostat device
    :param: control: state
    """
    logger.info('Thingcontrol Callback Server: setThermostat: deviceid: %s, control: %s.', deviceid, control)
    data = initData()
    data['device_id'] = deviceid
    data['device_type'] = 'zw_thermostat'
    data['msgTyp'] = 'zw_thermostat_msg'
    data['control'] = control
    sendCommand('thermostat', data)
    return {u'status': 0}

def secureHome(deviceid, control):
    """
    Control thermostat device.
    :param: deviceid: id of the thermostat device
    :param: control: state
    """
    logger.info('Thingcontrol Callback Server: secureHome: deviceid: %s, control: %s.', deviceid, control)
    data = initData()
    data['device_id'] = deviceid
    data['device_type'] = 'zw_thermostat'
    data['msgTyp'] = 'zw_thermostat_msg'
    data['control'] = control
    sendCommand('homeComing', data)
    return {u'status': 0}

   
def initData():
    """
    Initialize data structure for Thingcontrol message
    return: data structure in JSON format
    """
    data = {
        "strId": "",
        "device_id": "",
        "device_type": "",
        "display_name": "none",
        "msgId": "",
        "msgTyp": "",
        "time": "",
        "loc": [{}],
        "pyld": [{}],
        "control": [{}]
    }
    return data
    
def sendCommand(command, data):
    """
    Connect to the Thingcontrol server and send a command.
    :param: command: command to send
    :param: data: JSON data blob for command
    """
    logger.info('Thingcontrol Callback Server: sendCommand: command: %s, data: %s, dest: %s.', command, data, settings.TC_SERVER_GATEWAY_URL)
    try:
        url = urlparse(settings.TC_SERVER_GATEWAY_URL)
        con = httplib.HTTPConnection(url.hostname, url.port)
        path = settings.TC_SERVER_GATEWAY_DOMAIN + '/' + command
        headers = { 'Content-Type':'application/json', 'Accept':'application/json'}
        con.request('POST', path, json.dumps(data), headers)
        res = con.getresponse()
        logger.info('Thingcontrol Callback Server: sendCommand: Response: %s %s', res.status, res.reason)
    except Exception as e:
        logger.error('Thingcontrol Callback Server: sendCommand: Exception: %s', e)
    return data

