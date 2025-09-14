import pygame
from menu.menu import Var
from menu.menu import Selectable

class Selector(Selectable):
    def __init__(self, items_var:Var, on_return = None, pos=(0, 0)):
        super().__init__()
        self.items = items_var
        if on_return:
            self.on_return = lambda selected_item: on_return(selected_item)
        else:
            self.on_return = lambda selected_item: None
        self.selected_index = 0
        self.highlighted_index = 0
        self.pos = pos
        self.on_return(self.get_selected())
        self.redraw()
    
    def redraw(self):
        font = pygame.font.Font(None, 40)
        item_name = self.items.get()[self.highlighted_index][0]
        text_surface = font.render(f"<{item_name}>", False, (255, 255, 255))
        padding = 10
        size = (text_surface.get_width()+2*padding, text_surface.get_height()+2*padding)
        self.image = pygame.Surface(size)
        pygame.draw.rect(self.image, (50, 70, 50), border_radius=padding, rect=pygame.Rect((0, 0), size))
        self.image.blit(text_surface, (padding, padding))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
    
    def get_selected(self):
        return self.items.get()[self.selected_index]
    
    def update(self, events, dt=1):
        if not self.selected: return
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.selected_index = self.highlighted_index
                    self.on_return(self.get_selected())
                elif event.key == pygame.K_RIGHT:
                    self.highlighted_index += 1
                    self.highlighted_index %= len(self.items.get())
                    self.redraw()
                elif event.key == pygame.K_LEFT:
                    self.highlighted_index -= 1
                    self.highlighted_index %= len(self.items.get())
                    self.redraw()