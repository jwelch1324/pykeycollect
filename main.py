import sys
import Actors
from Application import KSApplication
sys.path.append("..")
# Create the application and start running in the background.

app = KSApplication()
app.add_actor(Actors.TriGraphHoldTimeActor())
app.run()
