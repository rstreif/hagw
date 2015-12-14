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
    if '*' in devices or 'thermostat' in devices:
        data = getThingcontrolStatus('thermostat')
    else:
        logger.warning('Thingcontrol Callback Server: getDeviceStatus: unknown device')
        return {u'status': 1}
    if data == None:
        logger.warning('Thingcontrol Callback Server: getDeviceStatus: no status information received')
        return {u'status': 1}
    sendRVIMessage(sendto, data)
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
    sendThingcontrolCommand('huelighting', data)
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
    sendThingcontrolCommand('wallsmartoutlet', data)
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
    sendThingcontrolCommand('smartswitch', data)
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
    sendThingcontrolCommand('doorlock', data)
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
    sendThingcontrolCommand('dimmer', data)
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
    sendThingcontrolCommand('thermostat', data)
    return {u'status': 0}

def secureHome(deviceid, control):
    """
    Control thermostat device.
    :param: deviceid: id of the thermostat device
    :param: control: state
    """
    logger.info('Thingcontrol Callback Server: secureHome: deviceid: %s, control: %s.', deviceid, control)
    for c in control:
        if 'value' in c:
            if c['value'] == 'arm':
                switchLights('off')
                lockDoors('lock')
            elif c['value'] == 'disarm':
                switchLights('on')
                lockDoors('unlock')
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
    
def switchLights(state):
    """
    Turn on/off all lights in the smarthome.
    :param: state: 'on' or 'off'
    """
    data = initData()
    data['device_id'] = 'wip_gw2.zb_hue01'
    data['device_type'] = 'zb_hue_bulb'
    data['msgTyp'] = 'zb_hue_msg'
    if state == "off":
        data['control'] = [{"value":0, "controlR":0, "controlG":0, "controlB":0}]
    else:
        data['control'] = [{"value":255, "controlR":255, "controlG":255, "controlB":255}]
    sendThingcontrolCommand('huelighting', data)
    
def lockDoors(state):
    """
    Lock/unlock all doors in the smarthome
    :param: state: 'lock' or 'unlock'
    """
    data = initData()
    data['device_id'] = 'wip_gw2.zb_lock01'
    data['device_type'] = 'zb_door_lock'
    data['msgTyp'] = 'zb_door_msg'
    data['control'] = [{"state":state}]
    sendThingcontrolCommand('doorlock', data)
    
    
    
def sendThingcontrolCommand(command, data):
    """
    Connect to the Thingcontrol server and send a command.
    :param: command: command to send
    :param: data: JSON data blob for command
    """
    logger.info('Thingcontrol Callback Server: sendThingcontrolCommand: command: %s, data: %s, dest: %s.', command, data, settings.TC_SERVER_GATEWAY_URL)
    try:
        url = urlparse(settings.TC_SERVER_GATEWAY_URL)
        con = httplib.HTTPConnection(url.hostname, url.port)
        path = settings.TC_SERVER_GATEWAY_DOMAIN_CONTROL + '/' + command
        headers = { 'Content-Type':'application/json', 'Accept':'application/json'}
        con.request('POST', path, json.dumps(data), headers)
        res = con.getresponse()
        logger.info('Thingcontrol Callback Server: sendThingcontrolCommand: Response: %s %s', res.status, res.reason)
    except Exception as e:
        logger.error('Thingcontrol Callback Server: sendThingcontrolCommand: Exception: %s', e)
    return data
    
    
def getThingcontrolStatus(command):
    """
    Connect to the Thingcontrol Server and get the termostat status information.
    :param: command: the status command
    """
    logger.info('Thingcontrol Callback Server: getThingcontrolStatus: command: %s, dest: %s.', command, settings.TC_SERVER_GATEWAY_URL)
    try:
        url = urlparse(settings.TC_SERVER_GATEWAY_URL)
        con = httplib.HTTPConnection(url.hostname, url.port)
        path = settings.TC_SERVER_GATEWAY_DOMAIN_STATUS + '/' + command
        con.request('GET', path)
        res = con.getresponse()
        data = json.loads(res.read())
    except Exception as e:
        logger.error('Thingcontrol Callback Server: getThingcontrolStatus: Exception: %s', e)
        data = None
    return data
    

old_temp = 0
def setIVIHVAC():
    data = getThingcontrolStatus('thermostat')
    if data == None: return False
    for c in data['control']:
        if 'target_temp' in c: temp = c['target_temp']
    if temp != old_temp:
        control = {}
        control['temp_front_left'] = temp
        control['temp_front_right'] = temp
        control['fan_speed'] = 5
        sendIVI(settings.IVI_SERVICE_EDGE_URL, control)
    return True
    
    
def sendRVIMessage(sendto, message):
    """
    Send message to recipient via RVI.
    :param: sendto: recipient RVI service
    :param: meessage: message as RVI parameter block
    """
    
    logger.info('Thingcontrol Callback Server: sending message: %s to %s', message, sendto)
    
    # send message
    try:
        service_edge.message(service_name = sendto,
                           timeout = int(time.time()) + settings.RVI_SEND_TIMEOUT,
                           parameters = [message])
    except Exception as e:
        logger.error('Thingcontrol Callback Server: cannot send message: %s', e)
        return False
    
    logger.info('Thingcontrol Callback Server: successfully sent message: to %s', sendto)

    return True



