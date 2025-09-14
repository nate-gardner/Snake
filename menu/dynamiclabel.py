import pygame
from menu.menu import Var

class DynamicLabel:
    def __init__(self, text=Var(''), pos=(0, 0)):
        self.text = text
        self.pos = pos
        self.redraw()
    
    def redraw(self):
        font = pygame.font.Font(None, 40)
        text_surface = font.render(str(self.text.get()), False, (255, 255, 255))
        padding = 10
        size = (text_surface.get_width()+2*padding, text_surface.get_height()+2*padding)
        self.image = pygame.Surface(size)
        pygame.draw.rect(self.image, (50, 70, 50), border_radius=padding, rect=pygame.Rect((0, 0), size))
        self.image.blit(text_surface, (padding, padding))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
    
    def update(self, events, dt=1):
        self.redraw()