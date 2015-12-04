"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com)
"""

"""
Home Automation Gateway with RVI integration.
"""

import sys, os, logging, jsonrpclib
import time
from signal import *
from urlparse import urlparse


import __init__, settings
from daemon import Daemon

import coreserver
import pixieserver
import thingcontrolserver
import umsgserver
import vehicleserver

logger = logging.getLogger('hagw.default')

class HAGWServer(Daemon):
    """
    Main server daemon
    """
    rvi_service_edge = None
    servers = {}
    
    core_cb_server = None
    pixie_cb_server = None
    tc_cb_server = None
    umsg_cb_server = None
    umsg_cb_server = None
    
    def shutdown(self, *args):
        """
        Clean up and exit.
        """
        logger.info('HAGW Server: Caught signal: %d. Shutting down...', args[0])
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """
        Clean up.
        """
        for key, value in self.servers.iteritems():
            if value is not None:
                value.shutdown()

    def startup(self):
        """
        Initialization and startup
        """
        logger.info('HAGW Server: Starting...')

        logger.debug('HAGW Server: General Configuration: ' + 
            'RVI_SERVICE_EDGE_URL: '  + settings.RVI_SERVICE_EDGE_URL
            )

        # setup RVI Service Edge
        logger.info('HAGW Server: Setting up outbound connection to RVI Service Edge at %s', settings.RVI_SERVICE_EDGE_URL)
        self.rvi_service_edge = jsonrpclib.Server(settings.RVI_SERVICE_EDGE_URL)
        
        # Core Server Startup
        logger.info('HAGW Server: Starting Core Server on %s with service id %s.', settings.CORE_SERVER_CALLBACK_URL, settings.CORE_SERVER_SERVICE_ID)
        while True:
            try:
                server = coreserver.CoreCallbackServer(logger, self.rvi_service_edge)
                server.start()
                self.servers['core'] = server
                logger.info('HAGW Server: Core Server started.')
                break
            except Exception as e:
                logger.error('HAGW Server: Core Server startup failure: %s', e)
                self.cleanup()
                time.sleep(settings.MAIN_LOOP_INTERVAL)
                
        # Pixie Server Startup
        if settings.PIXIE_SERVER_ENABLE == True:
            # start the Pixie Server
            try:
                logger.info('HAGW Server: Starting Pixie Adjacent Callback Server on %s with service id %s.', settings.PIXIE_SERVER_CALLBACK_URL, settings.PIXIE_SERVER_SERVICE_ID)
                server = pixieserver.PixieCallbackServer(logger, self.rvi_service_edge)
                server.start()
                self.servers['pixie'] = server
                logger.info('HAGW Server: Pixie Adjacent Callback Server started.')
            except Exception as e:
                logger.error('HAGW Server: Cannot start Pixie Adjacent Callback Server: %s', e)
                self.cleanup()
                return False
            # wait for Pixie Adjacent Callback server to come up    
            time.sleep(0.5)
        else:
            logger.info('HAGW Server: Pixie Adjacent Server not enabled')
        
        # Thingcontrol Server Startup
        if settings.TC_SERVER_ENABLE == True:
            # start the Thingcontrol Server
            try:
                logger.info('HAGW Server: Starting Thingcontrol Callback Server on %s with service id %s.', settings.TC_SERVER_CALLBACK_URL, settings.TC_SERVER_SERVICE_ID)
                server = thingcontrolserver.ThingcontrolCallbackServer(logger, self.rvi_service_edge)
                server.start()
                self.servers['thingcontrol'] = server
                logger.info('HAGW Server: Thingcontrol Callback Server started.')
            except Exception as e:
                logger.error('HAGW Server: Cannot start Thingcontrol Callback Server: %s', e)
                self.cleanup()
                return False
            # wait for Thingcontrol Callback server to come up    
            time.sleep(0.5)
        else:
            logger.info('HAGW Server: Thingcontrol Server not enabled')

        # Usermessage Server Startup
        if settings.UM_SERVER_ENABLE == True:
            # start the Usermessage Server
            try:
                logger.info('HAGW Server: Starting Usermessage Callback Server on %s with service id %s.', settings.UM_SERVER_CALLBACK_URL, settings.UM_SERVER_SERVICE_ID)
                server = umsgserver.UsermessageCallbackServer(logger, self.rvi_service_edge)
                server.start()
                self.servers['usermessage'] = server
                logger.info('HAGW Server: Usermessage Callback Server started.')
            except Exception as e:
                logger.error('HAGW Server: Cannot start Usermessage Callback Server: %s', e)
                self.cleanup()
                return False
            # wait for Usermessge Callback server to come up    
            time.sleep(0.5)
        else:
            logger.info('HAGW Server: Usermessage Server not enabled')

        # Vehicle Server Startup
        if settings.VH_SERVER_ENABLE == True:
            # start the Vehicle Server
            try:
                logger.info('HAGW Server: Starting Vehicle Callback Server on %s with service id %s.', settings.VH_SERVER_CALLBACK_URL, settings.VH_SERVER_SERVICE_ID)
                server = vehicleserver.VehicleCallbackServer(logger, self.rvi_service_edge)
                server.start()
                self.servers['vehicle'] = server
                logger.info('HAGW Server: Vehicle Callback Server started.')
            except Exception as e:
                logger.error('HAGW Server: Cannot start Vehicle Callback Server: %s', e)
                self.cleanup()
                return False
            # wait for Vehicle Callback server to come up    
            time.sleep(0.5)
        else:
            logger.info('HAGW Server: Vehicle Server not enabled')

        return True

    def run(self):
        """
        Main execution loop
        """
        # catch signals for proper shutdown
        for sig in (SIGABRT, SIGTERM, SIGINT):
            signal(sig, self.shutdown)
        # start servers
        self.startup()
        while True:
            try:
                time.sleep(settings.MAIN_LOOP_INTERVAL)
                logger.debug('HAGW Server: Main Loop')
                if self.ping() == False:
                    # cannot ping myself via RVI -> restart
                    logger.warning('HAGW Server: ping failed -> restarting')
                    self.cleanup()
                    self.startup()
                #logger.debug('HAGW Server: Item Locations: %s', pixieserver.getPixieLocations())
            except KeyboardInterrupt:
                print ('\n')
                break
                
    def ping(self):
        """
        Ping myself via RVI
        """
        try:
            server = jsonrpclib.Server(settings.RVI_SERVICE_EDGE_URL)
            server.message(service_name = settings.CORE_SERVER_RVI_DOMAIN + settings.CORE_SERVER_SERVICE_ID + "/ping",
                           timeout = int(time.time()) + settings.RVI_SEND_TIMEOUT,
                           parameters = [{"message":"alive"}]
                          )
            return True
        except Exception as e:
            return False



def usage():
    """
    Print usage message
    """
    print "HAGW Server: Usage: %s foreground|start|stop|restart" % sys.argv[0]        
    
"""
Main Function
"""    
if __name__ == "__main__":
    pid_file = '/var/run/' + os.path.splitext(__file__)[0] + '.pid'
    hagw_server = None
    if len(sys.argv) == 3:
        pid_file = sys.argv[2]
    hagw_server = HAGWServer(pid_file, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null')
    if len(sys.argv) >= 2:
        if sys.argv[1] in ('foreground', 'fg'):
            # in foreground we also log to the console
            logger = logging.getLogger('hagw.console')
            hagw_server.run()
        elif sys.argv[1] in ('start', 'st'):
            hagw_server.start()
        elif sys.argv[1] in ('stop', 'sp'):
            hagw_server.stop()
        elif sys.argv[1] in ('restart', 're'):
            hagw_server.restart()
        else:
            print "HAGW Server: Unknown command."
            usage()
            sys.exit(2)
    else:
        usage()
        sys.exit(2)
