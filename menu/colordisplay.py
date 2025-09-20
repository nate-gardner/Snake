import pygame
from menu.menu import Var

class ColorDisplay:
    def __init__(self, size, color_var=Var([255, 255, 255])):
        self.size = size
        self.color_var = color_var
        self.update()
    
    def update(self, events=[], dt=1):
        self.image = pygame.Surface(self.size)
        pygame.draw.rect(self.image, self.color_var.get(), rect=pygame.Rect((0, 0), self.size))
        self.rect = self.image.get_rect()