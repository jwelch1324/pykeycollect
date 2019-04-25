import sys
import Actors
from Application import KSApplication
from thespian.actors import ActorSystem
from thespian.system import multiprocTCPBase
import keyboard
sys.path.append("..")
# Create the application and start running in the background.

if __name__ == "__main__":
    #freeze_support()
    asys = ActorSystem('multiprocTCPBase')
    #asys = ActorSystem('multiprocQueueBase')
    app = KSApplication()
    app.add_actor("TriGraphHoldTimeActorNew")
    app.run()
    asys.shutdown()
