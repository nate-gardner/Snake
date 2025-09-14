import pygame
from menu.menu import Selectable
from menu.menu import Clickable

class Button(Clickable, Selectable):
    def __init__(self, text='', command=None, pos=(0, 0)):
        self.command = command
        font = pygame.font.Font(None, 40)
        text_surface = font.render(text, False, (255, 255, 255))
        padding = 10
        size = (text_surface.get_width()+2*padding, text_surface.get_height()+2*padding)
        self.image = pygame.Surface(size)
        pygame.draw.rect(self.image, (50, 70, 50), border_radius=padding, rect=pygame.Rect((0, 0), size))
        self.image.blit(text_surface, (padding, padding))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = pos
    
    def on_click(self):
        if self.command:
            self.command()