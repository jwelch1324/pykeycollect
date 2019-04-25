import sys
import Actors
from Application import KSApplication
from thespian.actors import ActorSystem
from multiprocessing import freeze_support
import setproctitle
import thespian
#from thespian.system import multiprocTCPBase, multiprocUDPBase, ActorAddress
#from thespian.system.multiprocTCPBase import TCPTransport
import keyboard
#sys.path.append("..")
# Create the application and start running in the background.

if __name__ == "__main__":
    freeze_support()
    asys = ActorSystem('multiprocTCPBase')
    #asys = ActorSystem('multiprocUDPBase')
    #print("loading app")
    #asys = ActorSystem('multiprocQueueBase')
    app = KSApplication()
    app.add_actor("TriGraphHoldTimeActorNew")
    app.run()
    asys.shutdown()
