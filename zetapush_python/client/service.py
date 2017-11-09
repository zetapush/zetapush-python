#/usr/bin/python3.5
# coding: utf-8

import json
import websocket
import random
import string
import time
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
        if self.client.connected is not True:
            time.sleep(0.5)
        
        # For the channel selfName
        self.client.identifiant = int(self.client.identifiant) + 1
        sub = self.getChannel(verb)
        res = [{'id': str(self.client.identifiant), 'channel': META_SUBSCRIBE, 'subscription': sub, 'clientId': self.client.clientId}]
        res = json.dumps(res)
        self.client.ws.send(res)

        # Fort the channel completed
        self.client.identifiant = int(self.client.identifiant) + 1
        sub = "/service/" + self.businessId + "/" + self.deploymentId + "/completed"
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

        # For the channel completed
        self.client.identifiant = int(self.client.identifiant) + 1
        sub = "/service/" + self.businessId + "/" + self.deploymentId + "/completed"
        res = [{'id': str(self.client.identifiant), 'channel': META_UNSUBSCRIBE, 'subscription': sub, 'clientId': self.client.clientId}]
        res = json.dumps(res)
        self.client.ws.send(res)


    def getChannel(self, verb):
        """ Get the channel of the service """
        return "/service/" + self.businessId + "/" + self.deploymentId + "/" + verb

    def send(self, verb, params):
        """ Send message to service """
        self.subscribe(verb)

        logging.info("call {} with : {}".format(verb, params))
        self.client.identifiant = int(self.client.identifiant) + 1
        chan = "/service/" + self.businessId + "/" + self.deploymentId + "/call" 
        requestId = self.client.clientId + ":" + ''.join(random.choice(string.ascii_letters + string.digits) for x in range(7)) + ":1"
        res = [{'id': str(self.client.identifiant), 'channel': chan, 'data': {'debug': 1, 'hardFail': False, 'name': verb, \
              'parameters': params, 'requestId': requestId}, 'clientId': self.client.clientId}]
        
        res = json.dumps(res)
        self.client.ws.send(res)

        self.unsubscribe(verb)

    def on(self, verb, function):
        """ Associate a function to a verb """
        self.callbacks[verb] = function


    def activeCallback(self, verb, params):
        """ Receive message from macro (server) """
        logging.info("Active {} callback with : {}".format(verb, params))
        self.callbacks[verb](params)
        