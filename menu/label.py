import pygame
from menu.menu import Var

class Label:
    def __init__(self, text='', pos=(0, 0)):
        self.text = text
        self.last_text = text
        self.redraw()
        self.rect.center = pos
    
    def redraw(self):
        font = pygame.font.Font(None, 40)
        text_surface = font.render(self.text, False, (255, 255, 255))
        padding = 10
        size = (text_surface.get_width()+2*padding, text_surface.get_height()+2*padding)
        self.image = pygame.Surface(size)
        pygame.draw.rect(self.image, (50, 70, 50), border_radius=padding, rect=pygame.Rect((0, 0), size))
        self.image.blit(text_surface, (padding, padding))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
    
    def update(self, events, dt=1):
        if self.text != self.last_text:
            self.last_text = self.text
            self.redraw()