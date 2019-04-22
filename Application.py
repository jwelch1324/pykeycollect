from PIL import Image, ImageDraw
import pystray
import time
import keyboard
import pykka
from threading import Event

def setup(icon):
    icon.visible = True
    time.sleep(5)
    icon.stop()


#This is a terrible hack that is needed to use the on_activate callback with pystray MenuItems... However as long as KSApplication is treated like a singleton, it is fine.
KSAPP = None    
def on_activate(icon):
    KSAPP.on_activate(icon)
def on_quit(icon):
    KSAPP.on_quit(icon)

class KSApplication(object):
    def __init__(self):
        
        icon = pystray.Icon("KSCollector", menu=pystray.Menu(
            pystray.MenuItem('Enabled',on_activate,default=True,checked=lambda item: self.enabled),
            pystray.MenuItem('Quit',on_quit)))
        
        icon.icon = self.__generate_icon()      
        self.icon = icon
        self.sequence = None
        self.actors = []
        self.stop_event = Event()
        self.user = 'user'
        self.enabled = True
        
        #Ugly hack that needs to be fixed eventually
        global KSAPP
        KSAPP = self
            
            
    def on_activate(self,icon):
        self.enabled = not self.enabled
        if self.enabled:
            self.icon.icon = self.__generate_icon('green')
        else:
            self.icon.icon = self.__generate_icon('blue')
            
    def on_quit(self,icon):
        self.stop_event.set()
        self.enabled = False
        self.icon.icon = self.__generate_icon('red')
        
    def __generate_icon(self,color='green'):
        width = 200
        height = 200
        image = Image.new("RGB", (width, height), color="black")
        dc = ImageDraw.Draw(image)
        dc.rectangle((width // 2, 0, width, height // 2), fill=color)
        dc.rectangle((0, height // 2, width // 2, height), fill=color)
        return image
    
    def AddActor(self,actor):
        self.actors.append(actor.start())
    
    def __key_press_handler(self,event):
        #If we are not collecting then simply skip this event
        if not self.enabled:
            return

        event.time = time.perf_counter()
        for actor in self.actors:
            actor.tell({'kbe': event})
            
    def __check_esc_key(self,event):
        if event.name == 'esc':
            self.stop_event.set()
    
    def __runLoop(self,icon):
        icon.visible = True
        
        keyboard.hook(self.__key_press_handler)
        keyboard.hook(self.__check_esc_key)
        
        tnow = time.perf_counter()
        
        #Main Loop
        while not self.stop_event.isSet():            
            tend = time.perf_counter()
            if (tend-tnow) > 15:
                for actor in self.actors:
                    actor.tell({'save':'{}_hkm_data'.format(self.user)})
                    actor.tell({'stats':None})
                tnow = time.perf_counter()
            time.sleep(0.5)
            
        #Begin Clean Shutdown Procedure    
        print("Shutting down...")
        keyboard.unhook(self.__key_press_handler)
        keyboard.unhook(self.__check_esc_key)
        #Tell all the actors to save their current data
        for actor in self.actors:
            actor.tell({'save':'{}_hkm_data'.format(self.user)})
        time.sleep(3) #Time to allow actors to save
        for actor in self.actors:
            actor.stop() #Shutdown all actor threads
        print("Shutdown Complete...")
        
        icon.visible = False
        icon.stop()
        
    def set_icon_sequence(self,image_list):
        self.sequence = image_list
        
    def run(self):
        self.icon.run(self.__runLoop)
        
        
