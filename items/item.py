import pygame
import os

class Item:
    name:str
    def __init__(self):
        self.instances = set()
        self.color:tuple[int, int, int]
        
        image_name = None
        for file in os.scandir(f"images/{self.name}"):
            if file.is_file():
                image_name = file.path

        if image_name:
            self.image = pygame.image.load(image_name)
        else:
            self.image = pygame.Surface((10, 10))
            self.image.fill(self.color)
        
        sound_name = None
        for file in os.scandir(f"sounds/{self.name} collect"):
            if file.is_file():
                sound_name = file.path
        self.sound = pygame.mixer.Sound(sound_name) if sound_name else None
    
    def __iter__(self):
        return iter(self.instances)
    
    def __contains__(self, value):
        for instance in self.instances:
            if tuple(value) == instance: return True
        return False
    
    def newInstance(self, pos):
        self.instances.add(tuple(pos))
    
    def removeInstance(self, pos):
        self.instances.discard(tuple(pos))
    
    def clearInstances(self):
        self.instances.clear()
    
    def on_collect(self, snake, pos):
        self.removeInstance(pos)
        if self.sound:
            self.sound.play()
    
    def while_active(self, snake):
        pass