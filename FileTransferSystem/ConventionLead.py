import sys
from thespian.actors import ActorSystem, Actor, ActorTypeDispatcher, ActorExitRequest, ActorSystemConventionUpdate
import errno
from datetime import timedelta
from functools import partial
import Actors
import time
import messages
import uuid


class Registrar(ActorTypeDispatcher):
    def __init__(self):
        super().__init__()
        self.participants = {}
        self.actor_systems = {}
        self.rnodes = {}

    def receiveMsg_InitPacket(self, msg, sender):
        self.notifyOnSystemRegistrationChanges(True)
        print("Listening for System Registration Notifications")

    def receiveMsg_ActorExitRequest(self, msg, sender):
        print("Shutting Down Registrar")
        self.notifyOnSystemRegistrationChanges(False)
        self.participants.clear()
        self.actor_systems.clear()

    def receiveMsg_RequestRegistration(self, msg: messages.RequestRegistration, sender):
        # We are receiving a request to register an actor with the registrar
        # First check that we don't already have someone with that name
        if msg.name in self.participants:
            self.send(sender, messages.RegistrationAck(False, "NAME"))
        else:
            self.participants[msg.name] = msg.address
            self.send(sender, messages.RegistrationAck(True))

    def receiveMsg_AddressRequest(self, msg: messages.AddressRequest, sender):
        if msg.name in self.participants:
            messages.AddressResponse(True, self.participants[msg.name])
        else:
            messages.AddressResponse(False, None)

    def receiveMsg_ActorSystemConventionUpdate(self, msg: ActorSystemConventionUpdate, sender):
        if msg.remoteAdded:
            # A new actor system was registered with the convention
            uuid = msg.remoteCapabilities.get('uuid', None)
            if uuid is None:
                print("New Actor System Registered without UUID")
            else:
                print("New Actor System Registered uuid:{}".format(uuid))
                self.rnodes[uuid] = self.createActor("Actors.RegistrarActor", {'uuid': uuid}, 'rnode')

