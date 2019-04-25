from thespian.actors import Actor
from keyboard import KeyboardEvent
from keyboard import _os_keyboard

# from KeyEventParser import TriGraphDataCollector, vkconvert
import KeyEventParser
from KeyEventParser import vkconvert

# import Plotting.plot_funcs as pf
import os
import platform

# Platform Specific Configurations
if platform.system() == "Windows":
    if platform.win32_ver()[0] == "10":
        import win10toast

        toaster = win10toast.ToastNotifier()
    else:
        toaster = None
else:
    toaster = None

print(_os_keyboard.scan_code_to_vk.keys())

def _DisplayNotification(title, text, icon_path=None, duration=3):
    if toaster is not None:
        toaster.show_toast(
            title, text, icon_path=icon_path, threaded=True, duration=duration
        )


class DataStoreActor(Actor):
    def __init__(self):
        super().__init__()
        self.db = {}
        
    def receiveMessage(self, msg, sender):
        if isinstance(msg, dict):
            if 'set' in msg:
                kv = msg['set']
                for k,v in kv.items():
                    self.db[k] = v
            if 'get' in msg:
                key = msg['get']
                if key in self.db:
                    self.send(sender,self.db[key])
                else:
                    self.send(sender,None)


class DisplayNotificationActorNew(Actor):
    def receiveMessage(self, message, sender):
        if isinstance(message, dict):
            title = message["title"] if "title" in message else "Notification"
            text = message["text"] if "text" in message else ""
            icon_path = message["icon_path"] if "icon_path" in message else "N.ico"
            duration = message["duration"] if "duration" in message else 1
            _DisplayNotification(title, text, icon_path, duration)


class TriGraphHoldTimeActorNew(Actor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_collector = KeyEventParser.TriGraphDataCollector()
        self.name = "TGHT"
        self.configured = False
        if 65 not in _os_keyboard.scan_code_to_vk:
            print("Setting up VK Tables")
            _os_keyboard._setup_name_tables()

    def receiveMessage(self, message, sender):       
        if isinstance(message, dict):
            if "kbe" in message:
                e = message["kbe"]
                if e.event_type == "up":
                    e.event_type = "U"
                elif e.event_type == "down":
                    e.event_type = "D"
                else:
                    print("Unknown event")
                    return
                if e.scan_code < 0:
                    #This happens e.g. when in a remote desktop session... for some reason it sends a -255 scan code
                    #My guess is it is to notify the hook that it is losing ownership...?
                    return 
                #print(e.name, _os_keyboard.scan_code_to_vk[e.scan_code], e.event_type)
                self.key_collector.add_event(
                    _os_keyboard.scan_code_to_vk[e.scan_code], e.event_type, e.time
                )

            # if 'plt' in message:
            #    pf.plot_tri_matrix(self.key_collector.holdkey_matrix,vkconvert)

            if "save" in message:
                file_path = message["save"]
                if not file_path.endswith(".npy"):
                    file_path += ".npy"
                file_path = "{}_{}".format(self.name, file_path)
                cos = False
                if "clear_on_save" in message:
                    cos = message["clear_on_save"]
                self.key_collector.save_state(file_path, cos)
                
            if "load" in message:
                file_path = message["load"]
                file_path = "{}_{}".format(self.name, file_path)
                print("Attemping to load {}".format(file_path))
                if os.path.exists(file_path):
                    self.key_collector.load_state(file_path)
                self.configured = True
                    
            if "stats" in message:
                self.key_collector.print_stats()