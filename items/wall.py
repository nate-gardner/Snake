import pygame

class Wall:
    def __init__(self):
        self.color = "#858585"
        self.instances = []
        self.image = pygame.Surface((10, 10))
        self.image.fill(self.color)
    
    def __iter__(self):
        return iter(self.instances)
    
    def __contains__(self, value):
        return tuple(value) in self.instances
    
    def newInstance(self, pos):
        if tuple(pos) in self.instances:
            self.removeInstance(pos)
        else:
            self.instances.append(tuple(pos))

    def removeInstance(self, pos):
        self.instances.remove(tuple(pos))
    
    def clearInstances(self):
        return
    
    def setInstances(self, instances):
        self.instances.clear()
        for instance in instances:
            self.instances.append(tuple(instance))