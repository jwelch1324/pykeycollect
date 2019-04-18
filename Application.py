from PIL import Image, ImageDraw
import pystray
import time
import keyboard
import pykka

def setup(icon):
    icon.visible = True
    time.sleep(5)
    icon.stop()

class KSApplication(object):
    def __init__(self):
        icon = pystray.Icon("KSTest")
        icon.icon = self.__generate_icon()      
        self.icon = icon
        self.sequence = None
        
        
    def __generate_icon(self,color='red'):
        width = 200
        height = 200
        image = Image.new("RGB", (width, height), color="black")
        dc = ImageDraw.Draw(image)
        dc.rectangle((width // 2, 0, width, height // 2), fill=color)
        dc.rectangle((0, height // 2, width // 2, height), fill=color)
        return image
    
    def __setup(self,icon):
        icon.visible = True
        
        icon.stop()
        
    def set_icon_sequence(self,image_list):
        self.sequence = image_list
        
    def run(self):
        self.icon.run(self.__setup)
        
        
