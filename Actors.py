import pykka
from thespian.actors import Actor
import numpy as np
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


def _DisplayNotification(title, text, icon_path=None, duration=3):
    if toaster is not None:
        toaster.show_toast(
            title, text, icon_path=icon_path, threaded=True, duration=duration
        )


class DataSaveActor(pykka.ThreadingActor):
    def __init__(self, key_collector_ref):
        super().__init__()
        self.key_collector_ref = key_collector_ref


class DisplayNotificationActorNew(Actor):
    def receiveMessage(self, message, sender):
        title = message["title"] if "title" in message else "Notification"
        text = message["text"] if "text" in message else ""
        icon_path = message["icon_path"] if "icon_path" in message else "N.ico"
        duration = message["duration"] if "duration" in message else 1
        _DisplayNotification(title, text, icon_path, duration)        


class DisplayNotificationActor(pykka.ThreadingActor):
    def __init__(self):
        super().__init__()

    def on_receive(self, message):
        super().on_receive(message)
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

    def receiveMessage(self, message, sender):
        if isinstance(message, dict):
            if "kbe" in message:
                e = message["kbe"]
                print(e)
                if e.event_type == "up":
                    e.event_type = "U"
                elif e.event_type == "down":
                    e.event_type = "D"
                else:
                    print("Unknown event")
                    return
                self.key_collector.AddEvent(
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
                self.key_collector.SaveState(file_path, cos)
            if "load" in message:
                file_path = message["load"]
                file_path = "{}_{}".format(self.name, file_path)
                print("Attemping to load {}".format(file_path))
                if os.path.exists(file_path):
                    self.key_collector.LoadState(file_path)
            if "stats" in message:
                self.key_collector.PrintStats()


class TriGraphHoldTimeActor(pykka.ThreadingActor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_collector = KeyEventParser.TriGraphDataCollector()
        self.name = "TGHT"
        self.dnaref = pykka.ActorRegistry.get_by_class_name("DisplayNotificationActor")[0]
        # self.dnaref.tell({"title":"KS Collector TGHT","text":"TriGraph Hold Time Collector Activated"})

    def on_failure(self, exception_type, exception_value, traceback):
        print("Failure! {}".format(exception_type))
        self.dnaref.tell(
            {
                "title": "KS Collector TGHT Error!",
                "text": "{}:{}".format(exception_type, exception_value),
            }
        )
        with open("err.log", "a") as f:
            f.writelines(
                ["Failure! {}:{}:{}".format(exception_type, exception_value, traceback)]
            )

    def on_receive(self, message):
        super().on_receive(message)
        if "kbe" in message:
            e = message["kbe"]
            print(e)
            if e.event_type == "up":
                e.event_type = "U"
            elif e.event_type == "down":
                e.event_type = "D"
            else:
                print("Unknown event")
                return
            self.key_collector.AddEvent(
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
            self.key_collector.SaveState(file_path, cos)

        if "load" in message:
            file_path = message["load"]
            file_path = "{}_{}".format(self.name, file_path)
            print("Attemping to load {}".format(file_path))
            if os.path.exists(file_path):
                self.key_collector.LoadState(file_path)

        if "stats" in message:
            self.key_collector.PrintStats()