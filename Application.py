from PIL import Image, ImageDraw
import pystray
import time
import keyboard
import pykka
from threading import Event
from Actors import DisplayNotificationActor

import platform

if platform.system() == "Windows":
    import win32api
    import win32con    
    g_user = win32api.GetUserNameEx(win32con.NameSamCompatible).replace('\\','-')
else:
    g_user = 'user'
    
print(g_user)

#This is a terrible hack that is needed to use the on_activate callback with pystray MenuItems... However as long as KSApplication is treated like a singleton, it is fine.
KSAPP = None    
def on_activate(icon):
    KSAPP.on_activate(icon)
def on_quit(icon):
    KSAPP.on_quit(icon)

class KSApplication(object):
    def __init__(self):
        
        DisplayNotificationActor.start()
        
        icon = pystray.Icon("KSCollector", menu=pystray.Menu(
            pystray.MenuItem('Enabled',on_activate,default=True,checked=lambda item: self.enabled),
            pystray.MenuItem('Quit',on_quit)))
        
        icon.icon = self.__generate_icon()
        img = self.__generate_icon('yellow')      
        img.save("N.ico")
        self.icon = icon
        self.sequence = None
        self.actors = []
        self.stop_event = Event()
        self.user = g_user
        self.enabled = True
        self.dnaref = pykka.ActorRegistry.get_by_class_name("DisplayNotificationActor")[0]
        self.downKeys = {}
        #Ugly hack that needs to be fixed eventually
        global KSAPP
        KSAPP = self
            
            
    def on_activate(self,icon):
        self.enabled = not self.enabled
        if self.enabled:
            self.icon.icon = self.__generate_icon('green')
            self.dnaref.tell({"title":"KS Collector","text":"Collecting Enabled"})
        else:
            self.icon.icon = self.__generate_icon('blue')
            self.dnaref.tell({"title":"KS Collector","text":"Collecting Paused"})
            
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
        aref = actor.start()
        aref.tell({'load':'{}_hkm_data.npy'.format(self.user)})
        adata = {'actor':actor,'aref':aref,'err':False}
        self.actors.append(adata)
    
    def __key_press_handler(self,event):
        #If we are not collecting then simply skip this event
        if not self.enabled:
            return

        event.time = time.perf_counter()
        if (event.event_type == "down"): 
            if (event.scan_code in self.downKeys):
                print("Held Key {}".format(event.scan_code))
                return
            else:
                self.downKeys[event.scan_code] = True
        if (event.event_type == "up"):
            if (event.scan_code in self.downKeys):
                del self.downKeys[event.scan_code]

            
        for actor in self.actors:
            try:
                actor['aref'].tell({'kbe': event})
            except pykka.ActorDeadError:
                print("Restarting Dead Actor")
                self.dnaref.tell({"title":"KS Collector","text":"Actor Died... Attempting Restart"})
                actor['aref'] = actor['actor'].start()
                actor['aref'].tell({'load':'{}_hkm_data.npy'.format(self.user)})
                
    
    def __runLoop(self,icon):
        icon.visible = True
        self.dnaref.tell({"title":"KS Collector","text":"Collector Enabled"})
        keyboard.hook(self.__key_press_handler)
        
        tnow = time.perf_counter()
        
        #Main Loop
        while not self.stop_event.isSet():            
            tend = time.perf_counter()
            if (tend-tnow) > 15:
                for actor in self.actors:
                    try:
                        actor['aref'].tell({'save':'{}_hkm_data.npy'.format(self.user)})
                        actor['aref'].tell({'stats':None})
                    except pykka.ActorDeadError:
                        print("Restarting Dead Actor")
                        self.dnaref.tell({"title":"KS Collector","text":"Actor Died... Attempting Restart"})
                        actor['aref'] = actor['actor'].start()
                        actor['aref'].tell({'load':'{}_hkm_data.npy'.format(self.user)})
                tnow = time.perf_counter()
            time.sleep(0.5)
            
        #Begin Clean Shutdown Procedure    
        print("Shutting down...")
        self.dnaref.tell({"title":"KS Collector","text":"Collector Shutting Down..."})
        keyboard.unhook(self.__key_press_handler)
        #Tell all the actors to save their current data
        for actor in self.actors:
            try:
                actor['aref'].tell({'save':'{}_hkm_data'.format(self.user)})
            except pykka.ActorDeadError:
                #Nothing we can do at this point... sadly we will have lost some data from the past 15 seconds
                pass
        time.sleep(3) #Time to allow actors to save
        for actor in self.actors:
            try:
                actor['aref'].stop() #Shutdown all actor threads
            except pykka.ActorDeadError:
                pass
            
        self.dnaref.stop()
            
        print("Shutdown Complete...")
        
        icon.visible = False
        icon.stop()
        
    def set_icon_sequence(self,image_list):
        self.sequence = image_list
        
    def run(self):
        self.icon.run(self.__runLoop)
        
        
