import sys
import time
sys.path.append("..")
import keyboard
from Application import KSApplication
import Actors

#Create the application and start running in the background.

app = KSApplication()
app.AddActor(Actors.TriGraphHoldTimeActor())
app.run()