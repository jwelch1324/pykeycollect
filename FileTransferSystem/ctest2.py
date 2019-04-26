import sys
from thespian.actors import ActorSystem, Actor, ActorTypeDispatcher, ActorExitRequest
import logging
import select
import socket
import errno
from datetime import timedelta
from functools import partial
from common import *
import Actors
import time
import signal

capabilities = {'Convention Address.IPv4': ('10.128.108.62', 2212), 'Admin Port': 2213}

if __name__ == "__main__":
    asys = ActorSystem('multiprocTCPBase', capabilities)
    # la = asys.createActor(Actors.LogActor)
    # asys.tell(la,"init")
    time.sleep(2)
    print("Shutting Down")
    # asys.tell(la,ActorExitRequest)
    time.sleep(3)
    asys.shutdown()
