import pykka
import numpy as np
from keyboard import KeyboardEvent
from keyboard import _os_keyboard
#from KeyEventParser import TriGraphDataCollector, vkconvert
import KeyEventParser
from KeyEventParser import vkconvert
import Plotting.plot_funcs as pf
import os

class DataSaveActor(pykka.ThreadingActor):
    def __init__(self, key_collector_ref):
        super().__init__()
        self.key_collector_ref = key_collector_ref


class TriGraphHoldTimeActor(pykka.ThreadingActor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_collector = KeyEventParser.TriGraphDataCollector()
        self.name = "TGHT"
        
    def on_failure(self, exception_type, exception_value, traceback):
        print("Failure! {}".format(exception_type))
        with open("err.log",'a') as f:
            f.writelines(["Failure! {}:{}".format(exception_type,exception_value)])
    
    def on_receive(self, message):
        super().on_receive(message)
        if 'kbe' in message:
            e = message['kbe']
            if e.event_type == 'up':
                e.event_type = 'U'
            elif e.event_type == 'down':
                e.event_type = 'D'
            else:
                print('Unknown event')
                return
            self.key_collector.AddEvent(_os_keyboard.scan_code_to_vk[e.scan_code],e.event_type,e.time)
        if 'plt' in message:
            pf.plot_tri_matrix(self.key_collector.holdkey_matrix,vkconvert)
        if 'save' in message:
            file_path = message['save']
            if not file_path.endswith(".npy"):
                file_path += ".npy"
            file_path = "{}_{}".format(self.name,file_path)
            cos = False
            if 'clear_on_save' in message:
                cos = message['clear_on_save']
            self.key_collector.SaveState(file_path,cos)
        if 'load' in message:
            file_path = message['load']
            file_path = "{}_{}".format(self.name,file_path)
            print("Attemping to load {}".format(file_path))
            if os.path.exists(file_path):
                self.key_collector.LoadState(file_path)
        if 'stats' in message:
            self.key_collector.PrintStats()
    