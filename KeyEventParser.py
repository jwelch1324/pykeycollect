import numpy as np
import keyboard
import os
class KeyHoldDistribution(object):
    def __init__(self,key,prior,post):
        self.key = key
        self.prior = prior
        self.post = post
        self.timings = []

    def AddTiming(self,timing):
        self.timings.append(timing)
        
    def AddTimingList(self,timinglist):
        self.timings.extend(timinglist)

    def get_times_ms(self):
        """
            Returns the timing vector in ms
        """
        return list(1000*np.array(self.timings))

    def get_times_sec(self):
        return self.timings

class BufferEventElement(object):
    def __init__(self,key,action,time):
        self.key = key
        self.action = action
        self.time = time
        self.delete = False

class VKKeyCode2KeyStoreKeyCode(object):
    def __init__(self):
        #alpha keys
        alphabet_dict = {k:v for (v,k) in enumerate(range(65,91))}
        alphabet_lookup = {k:v for (v,k) in enumerate([chr(i) for i in range(65,91)])}
        #Numeric Keys
        numeric_dict = {k:(v+len(alphabet_dict)) for (v,k) in enumerate(range(48,58))}
        numeric_lookup = {str(k):(v+len(alphabet_lookup)) for (v,k) in enumerate(range(0,10))}
        #Combine the two dictionaries
        final_dict = {**alphabet_dict,**numeric_dict}
        final_lookup = {**alphabet_lookup, **numeric_lookup}
        
        #Add in shift and return keys
        for i in [16777248, 16777220]:
            final_dict[i] = len(final_dict)
            
        final_lookup['Shift'] = 36
        final_lookup['Return'] = 37
        final_lookup['Enter'] = 37

        self.dict = final_dict
        self.lookup = final_lookup
    
    def convert(self,qt_kc):
        if qt_kc in self.dict:
            return self.dict[qt_kc]
        else:
            return None
    
    def get_code(self,key):
        if key.upper() in self.lookup.keys():
            return self.lookup[key.upper()]
        else:
            return None
        
    def get_key(self,code):
        return next(key for key, value in self.lookup.items() if value == code)
    
vkconvert = VKKeyCode2KeyStoreKeyCode()
    
class GroupingBuffer(object):
    def __init__(self,holdkey_matrix):
        self.events = []
        #This is a failsafe variable designed to prevent the system
        #from hanging in the event that there is a stuck key in the buffer
        self.count_returns = 0
        self.num_downs = 0
        self.num_ups= 0
        self.holdkey_matrix = holdkey_matrix


    def GetEventOffset(self, action, pos):
        """
        Args:
            action: 'D' or 'U'
            pos: offset from the start of the queue
        """
        act_c = 0
        for i in range(len(self.events)):
            if self.events[i].action == action:
                act_c += 1
                if act_c == pos:
                    return self.events[i]
        return None

    def GetEventKey(self, action, key, start_time=None):
        """
        Args:
            action: 'D' or 'U'
            key: the key for which the action is desired
        """
        for i in range(len(self.events)):
            if (self.events[i].key == key) & (self.events[i].action == action):
                if start_time is not None:
                    if self.events[i].time > start_time:
                        return self.events[i]
                else:
                    return self.events[i]
        return None

    def AddEvent(self,buffer_event):
        #if len(self.events) > 0:
        if self.events: #Check if the list is empty or not
            #pop all the deleted or Up actions from the start of the list
            while (self.events[0].delete) or (self.events[0].action == 'U'):
                if self.events[0].action == 'D':
                    self.num_downs -= 1
                else:
                    self.num_ups -= 1

                self.events.pop(0)

        #Add the new event to the end of the buffer
        self.events.append(buffer_event)
        if buffer_event.action == 'D':
            self.num_downs += 1
        else:
            self.num_ups += 1

        #Check if there are 4 Down events in the buffer
        if self.num_downs >= 4:
            #Check if the second down event has a corresponding up event
            s_down = self.GetEventOffset('D', 2)
            s_up = self.GetEventKey('U',s_down.key)

            if (s_up is not None):
                if (s_up.time < s_down.time):
                    #This likely means that we are looking at a double letter press
                    s_up = self.GetEventKey('U',s_down.key,s_down.time)

            if (s_down is not None) & (s_up is not None):
                f_down = self.GetEventOffset('D', 1)
                a_down = self.GetEventOffset('D', 3)

                if a_down is None:
                    for e in self.events:
                        print("{}:{}",e.key,e.action)
                f_down.delete = True
                #print("{}F {}D {}U".format(f_down.time,s_down.time,s_up.time))
                #Exctract the 1,2,3 hold time. 
                #print("{} has a hold time of {}ms when preceeded by {} and followed by {}".format(s_down.key,1000*(s_up.time-s_down.time),f_down.key,a_down.key))
                prior = vkconvert.convert(f_down.key)
                key = vkconvert.convert(s_down.key)
                post = vkconvert.convert(a_down.key)
                if (prior is not None) & (key is not None) & (post is not None):
                    #Add this to the holdkey matrix
                    #print("Adding key data {} {} {}".format(prior,key,post))
                    self.holdkey_matrix[prior,key,post].AddTiming(1000*(s_up.time-s_down.time))
            else:
                #It is likely the case that we have a stuck key, so allow this to go on
                #until we have 10 down events queued, then pop the top down event and set the second down event to delete to un stick it
                if self.num_downs >= 6:
                    print("Popping the top event and setting the delete flag on {} since it seems to be stuck".format(s_down.key))
                    self.events[0].delete = True
                    s_down.delete = True

class TriGraphDataCollector(object):
    def __init__(self):
        self.holdkey_matrix = np.array([[[KeyHoldDistribution(b,c,a) for a in range(38)] for b in range(38)] for c in range(38)])
        self.grp_buffer = GroupingBuffer(self.holdkey_matrix)
        self.num_keys_collected = 0
        
    def AddEvent(self, scan_code, action, time):
        #self.grp_buffer.AddEvent(BufferEventElement(_os_keyboard.scan_code_to_vk[e.scan_code],e.event_type,e.time))
        self.grp_buffer.AddEvent(BufferEventElement(scan_code, action, time))
        self.num_keys_collected += 1
        
    def SaveState(self,file_path,clear_state=False):
        #We want to save the current state of the hold key matrix
        np.save(file_path,self.holdkey_matrix)
        #if clear_state:
            #Remove the current reference
          #  del self.holdkey_matrix
            #Recreate the holdkey matrix
           # self.holdkey_matrix = np.array([[[KeyHoldDistribution(b,c,a) for a in range(38)] for b in range(38)] for c in range(38)])
            
    def LoadState(self,file_path):
        self.holdkey_matrix = np.load(file_path)
        print("Loaded {} holdkey matrix".format(file_path))
            
    def PrintStats(self):
        print("Collected {} keys so far".format(self.num_keys_collected))