import pygame
from menu.menu import Selectable
from menu.menu import Var

class TextInput(Selectable):
    def __init__(self, var=Var(""), default_text=' ', wrap_width=200, on_return=None, pos=(0, 0)):
        self.var = var
        if on_return:
            self.on_return = lambda text_value: on_return(text_value)
        else:
            self.on_return = lambda text_value: None
        self.default_text = default_text
        self.font = pygame.font.Font(None, 40)
        self.wrap_width = wrap_width
        self.pos = pos
        self.cursor_timer = 0
        self.selected = False
        self.cursor_visible = False
        self.draw()
    
    def draw(self):
        text = self.var.get() if self.var.get() != '' else self.default_text
        end = "|" if self.cursor_visible else " "
        if len(text) > len(self.default_text):
            text = text[-10:]
        text_surface = self.font.render(text+end, False, (255, 255, 255), (50, 70, 50))
        padding = 10
        size = (max(text_surface.get_width(), 150)+2*padding, text_surface.get_height()+2*padding)
        self.image = pygame.Surface(size)
        pygame.draw.rect(self.image, (50, 70, 50), border_radius=padding, rect=pygame.Rect((0, 0), size))
        self.image.blit(text_surface, (padding, padding))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
    
    def update(self, events, dt=1):
        if not self.selected:
            return
        text = self.var.get()
        if self.cursor_timer >= 10:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif event.key == pygame.K_RETURN:
                    if self.on_return: self.on_return(text)
                elif event.unicode:
                    text += event.unicode
        self.cursor_timer += dt
        self.var.set(text)
        self.draw()