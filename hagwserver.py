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

import pixieserver
import thingcontrolserver
import umsgserver

logger = logging.getLogger('hagw.default')

class HAGWServer(Daemon):
    """
    Main server daemon
    """
    rvi_service_edge = None
    pixie_cb_serer = None
    tc_cb_server = None
    umsg_cb_server = None

    def cleanup(self, *args):
        """
        Clean up and exit.
        """
        logger.info('HAGW Server: Caught signal: %d. Shutting down...', args[0])
        if self.pixie_cb_server:
            self.pixie_cb_server.shutdown()
        if self.tc_cb_server:
            self.tc_cb_server.shutdown()
        if self.umsg_cb_server:
            self.umsg_cb_server.shutdown()
        sys.exit(0)

    def run(self):
        """
        Main execution loop
        """
        logger.info('HAGW Server: Starting...')

        logger.debug('HAGW Server: General Configuration: ' + 
            'RVI_SERVICE_EDGE_URL: '  + settings.RVI_SERVICE_EDGE_URL
            )

        # setup RVI Service Edge
        logger.info('HAGW Server: Setting up outbound connection to RVI Service Edge at %s', settings.RVI_SERVICE_EDGE_URL)
        self.rvi_service_edge = jsonrpclib.Server(settings.RVI_SERVICE_EDGE_URL)

        # Pixie Server Startup
        if settings.PIXIE_SERVER_ENABLE == True:
            # start the Pixie Server
            try:
                logger.info('HAGW Server: Starting Pixie Adjacent Callback Server on %s with service id %s.', settings.PIXIE_SERVER_CALLBACK_URL, settings.PIXIE_SERVER_SERVICE_ID)
                self.pixie_cb_server = pixieserver.PixieCallbackServer(logger, self.rvi_service_edge)
                self.pixie_cb_server.start()
                logger.info('HAGW Server: Pixie Adjacent Callback Server started.')
            except Exception as e:
                logger.error('HAGW Server: Cannot start Pixie Adjacent Callback Server: %s', e)
                sys.exit(1)
            # wait for Pixie Adjacent Callback server to come up    
            time.sleep(0.5)
        else:
            logger.info('HAGW Server: Pixie Adjacent Server not enabled')
        
        # Thingcontrol Server Startup
        if settings.TC_SERVER_ENABLE == True:
            # start the Thingcontrol Server
            try:
                logger.info('HAGW Server: Starting Thingcontrol Callback Server on %s with service id %s.', settings.TC_SERVER_CALLBACK_URL, settings.TC_SERVER_SERVICE_ID)
                self.tc_cb_server = thingcontrolserver.ThingcontrolCallbackServer(logger, self.rvi_service_edge)
                self.tc_cb_server.start()
                logger.info('HAGW Server: Thingcontrol Callback Server started.')
            except Exception as e:
                logger.error('HAGW Server: Cannot start Thingcontrol Callback Server: %s', e)
                sys.exit(1)
            # wait for Thingcontrol Callback server to come up    
            time.sleep(0.5)
        else:
            logger.info('HAGW Server: Thingcontrol Server not enabled')

        # Usermessage Server Startup
        if settings.UM_SERVER_ENABLE == True:
            # start the Usermessage Server
            try:
                logger.info('HAGW Server: Starting Usermessage Callback Server on %s with service id %s.', settings.UM_SERVER_CALLBACK_URL, settings.UM_SERVER_SERVICE_ID)
                self.umsg_cb_server = umsgserver.UsermessageCallbackServer(logger, self.rvi_service_edge)
                self.umsg_cb_server.start()
                logger.info('HAGW Server: Usermessage Callback Server started.')
            except Exception as e:
                logger.error('HAGW Server: Cannot start Usermessage Callback Server: %s', e)
                sys.exit(1)
            # wait for Usermessge Callback server to come up    
            time.sleep(0.5)
        else:
            logger.info('HAGW Server: Usermessage Server not enabled')

        # catch signals for proper shutdown
        for sig in (SIGABRT, SIGTERM, SIGINT):
            signal(sig, self.cleanup)

        # main execution loop
        while True:
            try:
                time.sleep(settings.MAIN_LOOP_INTERVAL)
                logger.info('HAGW Server: Main Loop')
                print pixieserver.getPixieLocations()
            except KeyboardInterrupt:
                print ('\n')
                break



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
