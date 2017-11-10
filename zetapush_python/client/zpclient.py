#/usr/bin/python3.5
# coding: utf-8

import json
import websocket
import time
import re
import logging
import random
import urllib.request
from threading import Thread
from zetapush_python.utils.constants import *

logging.getLogger().setLevel(logging.DEBUG)

__all__ = ['Client']

def singleton(cls):
    instance = None
    def ctor(*args, **kwargs):
        nonlocal instance
        if not instance:
            instance = cls(*args, **kwargs)
        return instance
    return ctor

@singleton
class Client:
    """ 
    ZetaPush client 
    """

    def __init__(self, businessId, apiUrl="http://api.zpush.io/"):
        """ Constructor """
        logging.info("Create ZetaPush client on {}".format(businessId))
        self.url = apiUrl
        self.wsOpen = False                                                                 #   Say when the WS connection is open
        self.businessId = businessId                                                        #   Business ID
        self.connected = False                                                              #   When the client is connected to the ZetaPush platform
        self.login = None                                                                   #   Login to the ZP platform
        self.password = None                                                                #   Password to the ZP platform
        self.authenticationId = "simple_0"                                                  #   Deployment ID for the authentication service                         
        self.identifiant = 1                                                                #   Identifiant of the current trame
        self.supportedConnectionTypes = ["websocket", "long-polling"]
        self.ws = websocket.WebSocketApp(self.getUrlServer(), on_message = self.listenMsg, on_error = self.listenError, on_close = self.wsClosed)
        self.ws.on_open = self.wsOpened
        self.pattern = re.compile("/service/*")
        self.thread = Thread(target=self.ws.run_forever).start()
        self.services = {}
        self.onConnectionSuccess = None                                                     #   Callback connection success

    def getUrlServer(self): 
        """ Method to get the url server for the websocket connection """

        # In case of localhost test
        if self.url.split("//") == 'ws:':
            return self.url

        res = (urllib.request.urlopen(self.url + self.businessId).read()).decode('utf-8')
        data = json.loads(res)
        urlTab = (random.choice(data['servers'])).split('//')[-1]

        return 'ws://' + urlTab + '/strd'


    def stopZPConnection(self):
        """ Method to stop WebSocket communication """
        self.ws.close()

    def wsOpened(self, ws):
        """ React when the WS connection is open"""
        self.wsOpen = True

    def listenMsg(self, ws, msg):
        """ React when we received a message from the WS connection"""
        self._processMessageReceived(msg)

    def listenError(self, ws, error):
        """ React when we received an error from the WS connection"""
        logging.error("Error listen WS : {}".format(error))

    def wsClosed(self, ws):
        """ React when the WS connection is closed """
        logging.info("WS closed")
        self.wsOpen = False

    def connect(self, login, password):
        """ Launch the connection to the ZetaPush platform """

        self.login = login
        self.password = password

        jsonMessage = self._formatJSONHandshake()

        if self.wsOpen is not True:
            time.sleep(0.5)

        self.ws.send(jsonMessage)

    def disconnect(self):
        """ Launch the disconnection to the ZetaPush platform """
        self.identifiant = int(self.identifiant) + 1 
        res = [{'id': str(self.identifiant), 'channel': META_DISCONNECT}]
        res = json.dumps(res)
        self.ws.send(res)

    def _formatJSONHandshake(self):
        """ Method to format the JSON string """

        data = [{ 'ext': { 'authentication': { 'data': { 'login': self.login, 'password': self.password}, \
                'type': self.businessId + '.' + self.authenticationId + '.simple', 'version': 'none'}}, \
                'id': str(self.identifiant), 'version': '1.0', 'minimumVersion': '1.0', 'channel': META_HANDSHAKE, \
                'supportedConnectionTypes': self.supportedConnectionTypes, 'advice': { 'timeout': 60000, 'interval': 0}}]

        return json.dumps(data)

    def _processMessageReceived(self, msg):
        """ Handle message received """

        # Extract data
        data = json.loads(msg)
        data = data[0]

        # ===================================
        #           HANDSHAKE
        # ===================================
        if data['channel'] == META_HANDSHAKE:                   # The first exchange

            if data['successful'] == True:                      # The handshake is successful, we launch the connection
                self.clientId = data['clientId']
                self.identifiant = int(data['id']) + 1
                res = [{'id': str(self.identifiant), 'channel': META_CONNECT, 'connectionType': 'websocket', 'advice': {'timeout': 0}, 'clientId': self.clientId}]
                res = json.dumps(res)
                self.ws.send(res)

            elif data['successful'] == False:                   # The handshake failed, we launch disconnection
                self.disconnect()

        # ===================================
        #           CONNECT
        # ===================================
        elif data['channel'] == META_CONNECT:                   
            if data['successful'] == True:                      # The connection is successful
                if self.connected == False:
                    logging.info("Client connected")
                    self.connected = True
                    try:
                        self.onConnectionSuccess()
                    except:
                        print("ZpClient::NoConnectionSuccessFunctionDefined")
                self.identifiant = int(data['id']) + 1  

                res = [{'id': str(self.identifiant), 'channel': META_CONNECT, 'connectionType': 'websocket', 'clientId': self.clientId}]
                res = json.dumps(res)
                self.ws.send(res)

        # ===================================
        #           DISCONNECT
        # ===================================
        elif data['channel'] == META_DISCONNECT:                # When we disconnected the connection
            if data['successful'] == False:
                logging.info("Client disconnected")

        # ===================================
        #           SUBSCRIBE
        # ===================================
        elif data['channel'] == META_SUBSCRIBE:
            if data['successful'] == True:
                logging.info("Client subscribe on {}".format(data['subscription']))


        # ===================================
        #           UNSUBSCRIBE
        # ===================================
        elif data['channel'] == META_UNSUBSCRIBE:
            if data['successful'] == True:
                logging.info("Client unsubscribe on {}".format(data['subscription']))

        # ===================================
        #           DATA CHANNEL
        # ===================================
        elif self.pattern.match(data['channel']):
            try:
                if data['data'] is not None and (data['data']['requestId']).split(':')[0] == self.clientId:
                    service = self.services['macro_0']
                    service.activeCallback((data['channel']).split('/')[-1], data['data']['result'])    
            except:
                pass 
        else:
            logging.warning("Unable to read WS message : {}".format(msg))

        
    

    



