from PIL import Image, ImageDraw
import pystray
import time
import keyboard
from threading import Event
from Actors import *

import configparser

from thespian.actors import Actor, ActorSystem, ActorAddress, ActorExitRequest

import platform

if platform.system() == "Windows":
    import win32api
    import win32con

    g_user = win32api.GetUserNameEx(win32con.NameSamCompatible).replace("\\", "-")
else:
    g_user = "user"

print(g_user)

# This is a terrible hack that is needed to use the on_activate callback with pystray MenuItems... However as long as KSApplication is treated like a singleton, it is fine.
KSAPP = None


def on_activate(icon):
    KSAPP.on_activate(icon)


def on_quit(icon):
    KSAPP.on_quit(icon)

def getActiveApp():
    if platform.system() == "Darwin":
        active_app = NSWorkspace.sharedWorkspace().frontmostApplication()
        if active_app is None:
            print("No App Name Available!")
        else:
            return active_app.localizedName()
    else:
        return None

class KSApplication(Actor):
    def __init__(self):
        icon = pystray.Icon(
            "KSCollector",
            menu=pystray.Menu(
                pystray.MenuItem(
                    "Enabled",
                    on_activate,
                    default=True,
                    checked=lambda item: self.enabled,
                ),
                pystray.MenuItem("Quit", on_quit),
            ),
        )

        icon.icon = self.__generate_icon()
        img = self.__generate_icon("yellow")
        img.save("N.ico")
        self.icon = icon
        self.sequence = None
        self.actors = []
        self.stop_event = Event()
        self.user = g_user
        self.enabled = True
        self.dnaref = ActorSystem().createActor(DisplayNotificationActorNew, globalName="DisplayNotification")
        self.datastore = ActorSystem().createActor(DataStoreActor, globalName="DataStore")
        self.downKeys = {}
        self.filters = []
        # Ugly hack that needs to be fixed eventually
        global KSAPP
        KSAPP = self


        if os.path.exists('filters.ini'):
            #Load the config file to get the filtered apps
            cfg = configparser.ConfigParser()
            cfg.read("filters.ini")

            if 'Filters' in cfg:
                if 'Apps' in cfg['Filters']:
                    apps = cfg['Filters']['Apps']
                    apps = list(map(lambda x: x.strip(),apps.split(',')))

                    for a in apps:
                        if a == '':
                            continue
                        self.filters.append(a)
        else:
            cfg = configparser.ConfigParser()
            cfg['Filters'] = {'Apps':''}
            with open('filters.ini','w') as cfile:
                cfg.write(cfile)



    def on_activate(self, icon):
        self.enabled = not self.enabled
        if self.enabled:
            self.icon.icon = self.__generate_icon("green")
            ActorSystem().tell(self.dnaref,
                {
                    "title": "KS Collector", 
                    "text": "Collecting Enabled"
                })
        else:
            self.icon.icon = self.__generate_icon("blue")
            ActorSystem().tell(self.dnaref,
                {
                    "title": "KS Collector", 
                    "text": "Collecting Paused"
                })

    def on_quit(self, icon):
        self.stop_event.set()
        self.enabled = False
        self.icon.icon = self.__generate_icon("red")

    def __generate_icon(self, color="green"):
        width = 200
        height = 200
        image = Image.new("RGB", (width, height), color="black")
        dc = ImageDraw.Draw(image)
        dc.rectangle((width // 2, 0, width, height // 2), fill=color)
        dc.rectangle((0, height // 2, width // 2, height), fill=color)
        return image
        

    def add_actor(self, actor_name):     
        class_str = actor_name
        aref = None
        try:
            aref = ActorSystem().createActor(eval(class_str))
        except NameError:
            try:
                class_str = "Actors.{}".format(class_str)
                aref = ActorSystem().createActor(eval(class_str))
            except NameError:
                print("Error: Actor Class {} not found".format(actor_name))
                return
            
        ActorSystem().tell(aref,{"load": "{}_data".format(self.user)})
        for f in self.filters:
            ActorSystem().tell(aref,{"filter_app":f})
        adata = {'actor':class_str, 'aref':aref}
        self.actors.append(adata)

    def __key_press_handler(self, event):
        # If we are not collecting then simply skip this event
        if not self.enabled:
            return

        # This really should be done in the base keyboard library instead of here... but I didn't want to modify the base
        # library so instead I simply set the key time event here... if it turns out there is too much jitter in the results
        # we can change the base library so that the perf_counter call is closer to the actual OS keystroke event. However given that this runs as a
        # separate actor that only collects the data it shouldn't be too bad.
        event.time = time.perf_counter()

        if event.event_type == "down":
            if event.scan_code in self.downKeys:
                print("Held Key {}".format(event.scan_code))
                return
            else:
                self.downKeys[event.scan_code] = True
        if event.event_type == "up":
            if event.scan_code in self.downKeys:
                del self.downKeys[event.scan_code]

        for actor in self.actors:
            ActorSystem().tell(actor['aref'],{"kbe": event,"app":getActiveApp()})

    def __runLoop(self, icon):
        icon.visible = True
        ActorSystem().tell(self.dnaref,{"title": "KS Collector", "text": "Collector Enabled"})
        keyboard.hook(self.__key_press_handler)

        tnow = time.perf_counter()

        # Main Loop
        while not self.stop_event.isSet():
            tend = time.perf_counter()
            if (tend - tnow) > 15:
                for actor in self.actors:
                    ActorSystem().tell(actor["aref"],
                        {"save": "{}_data".format(self.user)}
                    )
                    ActorSystem().tell(actor["aref"],{"stats": None})
                tnow = time.perf_counter()
            time.sleep(0.5)

        # Begin Clean Shutdown Procedure
        print("Shutting down...")
        ActorSystem().tell(self.dnaref,
            {"title": "KS Collector", "text": "Collector Shutting Down..."}
        )
        keyboard.unhook(self.__key_press_handler)
        # Tell all the actors to save their current data
        for actor in self.actors:
            ActorSystem().tell(actor["aref"],{"save": "{}_data".format(self.user)})
        time.sleep(3)  # Time to allow actors to save
        for actor in self.actors:
            ActorSystem().tell(actor["aref"], ActorExitRequest())  # Shutdown all actor threads
        ActorSystem().tell(self.dnaref,ActorExitRequest())

        print("Shutdown Complete...")

        icon.visible = False
        icon.stop()

    def set_icon_sequence(self, image_list):
        self.sequence = image_list

    def run(self):
        self.icon.run(self.__runLoop)
