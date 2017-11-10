#/usr/bin/python3.5
# coding: utf-8

import json
import websocket
import random
import string
import logging

from zetapush_python.utils.constants import *

logging.getLogger().setLevel(logging.DEBUG)

__all__ = ['Service']

class Service:
    """ ZetaPush Service """

    def __init__(self, deployId, client):
        """ Constructor """
        logging.info("Create service {} for {} client".format(deployId, client))
        
        self.businessId = client.businessId
        self.deploymentId = deployId
        self.client = client
        self.client.services[deployId] = self
        self.callbacks = {}

    def subscribe(self, verb):
        """ Subscribe a service on channel __selfName and completed"""
        logging.info("Subscribe service on {}".format(verb))

        # DG: Removed this, user should only call this API when connected or this call could be deferred by client
        # if self.client.connected is not True:
        #     time.sleep(0.5)
        
        # For the channel selfName
        self.client.identifiant = int(self.client.identifiant) + 1
        sub = self.getChannel(verb)
        res = [{'id': str(self.client.identifiant), 'channel': META_SUBSCRIBE, 'subscription': sub, 'clientId': self.client.clientId}]
        res = json.dumps(res)
        self.client.ws.send(res)

    def unsubscribe(self, verb):
        """ Unsubscribe a service """
        logging.info("Unsubcribe service on {}".format(verb))

        # For the channel selfName
        self.client.identifiant = int(self.client.identifiant) + 1
        sub = self.getChannel(verb)
        res = [{'id': str(self.client.identifiant), 'channel': META_UNSUBSCRIBE, 'subscription': sub, 'clientId': self.client.clientId}]
        res = json.dumps(res)
        self.client.ws.send(res)


    def getChannel(self, verb):
        """ Get the channel of the service """
        return "/service/" + self.businessId + "/" + self.deploymentId + "/" + verb

    def send(self, verb, params):
        """ Send message to service """
        logging.info("call {} with : {}".format(verb, params))
        self.client.identifiant = int(self.client.identifiant) + 1
        chan = "/service/" + self.businessId + "/" + self.deploymentId + "/call" 
        requestId = self.client.clientId + ":" + ''.join(random.choice(string.ascii_letters + string.digits) for x in range(7)) + ":1"
        res = [{'id': str(self.client.identifiant), 'channel': chan, 'data': {'debug': 1, 'hardFail': False, 'name': verb, \
              'parameters': params, 'requestId': requestId}, 'clientId': self.client.clientId}]
        
        res = json.dumps(res)
        self.client.ws.send(res)

    def _internal_on(self, verb, function, json_paths):
        """ Associate a function to a verb """
        self.callbacks[verb] = (function, json_paths)
        if self.client.connected:
            self.subscribe(verb)

    def on(self, verb, function):
        """ Associate a function to a verb """
        return self._internal_on(verb, function, (['result'],))

    def onError(self, function):
        self._internal_on("error", function, (['code'],['message']))

    def onCompleted(self, function):
        self._internal_on("completed", function, ())

    def callCallback(self, verb, data):
        """ Receive message from macro (server) """
        logging.info("Call {} callback with : {}".format(verb, data))
        function, json_paths = self.callbacks[verb]
        params = []
        for json_path in json_paths:
            node = data
            for json_path_item in json_path:
                node = node[json_path_item]
            params.append(node)
        function(*params)

    def clientConnected(self):
        # Subscribe to all verbs
        for verb in self.callbacks:
            self.subscribe(verb)
