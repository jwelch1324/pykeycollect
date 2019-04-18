#%%
import sys
import time
sys.path.append("..")
import keyboard
from PIL import Image, ImageDraw
import pystray
from queue import Queue
from pykkatests import KeyboardActor
import Plotting.plot_funcs as pf
from threading import Event
import time


icon = pystray.Icon("KSTest")

width = 200
height = 200

image = Image.new("RGB", (width, height), color="black")
dc = ImageDraw.Draw(image)
dc.rectangle((width // 2, 0, width, height // 2), fill="red")
dc.rectangle((0, height // 2, width // 2, height), fill="red")

icon.icon = image

key_actor = KeyboardActor().start()

def print_pressed_keys(e):
    print(e)
    line = ", ".join(str(code) for code in keyboard._pressed_events)
    # '\r' and end='' overwrites the previous line.
    # ' '*40 prints 40 spaces at the end to ensure the previous line is cleared.
    print("\r" + line + " " * 40, end="")
_res = None

def key_press_handler(event):
   event.time = time.perf_counter()
   key_actor.tell({'kbe': event})


stop_event = Event()
def check_esc_key(event):
   if event.name == 'esc':
      stop_event.set()

def setup(icon):
   print("Starting...")
   icon.visible = True
   keyboard.hook(key_press_handler)
   keyboard.hook(check_esc_key)
   tnow = time.perf_counter()
   while not stop_event.isSet():
      tend = time.perf_counter()
      if (tend - tnow) > 15:
         key_actor.tell({'save':'hkm_data.npy'})
         key_actor.tell({'stats':None})
         tnow = time.perf_counter()
      time.sleep(0.5)
   keyboard.unhook(key_press_handler)   
   icon.stop()
   global _res
   key_actor.tell({'save':'hkm_data.npy'})
   key_actor.tell({'plt':True})
icon.run(setup)

#icon.visible = True
#%%





#%%

