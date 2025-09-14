import pygame
from pygame.locals import *
from menu.grid import Grid

class Menu:
    def __init__(self):
        self.widgets = []
        self.grid = Grid()
        self.selected_widget = None
    
    def add(self, widget, row=-1, column=-1):
        self.widgets.append(widget)
        self.grid.add(widget, row, column)
    
    def remove(self, widget):
        self.widgets.remove(widget)
        self.grid.remove(widget)
    
    def update(self, events):
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == BUTTON_LEFT:
                    for widget in self.widgets:
                        if widget.rect.collidepoint(event.pos):
                            if isinstance(widget, Clickable):
                                widget.on_click()
                            if isinstance(widget, Selectable):
                                widget.select()
                                if self.selected_widget:
                                    self.selected_widget.deselect()
                                self.selected_widget = widget
        for widget in self.widgets:
            widget.update(events)
        self.grid.update()
    
    def draw(self, surface):
        for widget in self.widgets:
            surface.blit(widget.image, widget.rect)

class Var:
    def __init__(self, value):
        self.value = value
    
    def set(self, value): self.value = value
    def get(self): return self.value
    def copy(self):return Var(self.value)
    def __add__(self, value): self.value += value
    def __sub__(self, value): self.value -= value
    def __eq__(self, value):return self.value == value.value

class Clickable:
    def __init__(self):
        self.rect:pygame.Rect
    
    def on_click(self):pass
    
    def update(self, events, dt=1):
        pass

class Selectable:
    def __init__(self):
        self.selected:bool = False
    
    def select(self):
        self.selected = True
    
    def deselect(self):
        self.selected = False

if __name__ == "__main__":
    from button import Button
    from textinput import TextInput
    from label import Label
    from dynamiclabel import DynamicLabel
    from selctor import Selector
    
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    clock = pygame.time.Clock()

    menu = Menu()
    menu.add(Button("Click me!", lambda:print("Button clicked.")), row=0, column=0)
    text = Var("")
    menu.add(TextInput(text, "Type here...", 200), row=1, column=0)
    menu.add(Label("This is a label"), row=2, column=0)
    menu.add(DynamicLabel(text), row=1, column=1)
    s = Selector([("one", 1), ("two", 2)], on_return=print)
    menu.add(s, row=3, column=0)
    s.items.get().append(("three", 3))

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                running = False
        menu.update(events)
        screen.fill((0, 0, 0))
        menu.draw(screen)
        pygame.display.flip()
        clock.tick(20)
        
    pygame.quit()