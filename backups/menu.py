import pygame
from pygame.locals import *


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

class Grid:
    def __init__(self, column_spacing=10, row_spacing=10, pos=(0, 0)):
        self.column_spacing = column_spacing
        self.row_spacing = row_spacing
        self.pos = pos
        self.widgets = [[]]
    
    def add(self, widget, row=0, column=0):
        while row >= len(self.widgets):
            self.widgets.append([NoneWidget()])
        while column >= len(self.widgets[row]):
            self.widgets[row].append(NoneWidget())
        if not isinstance(self.widgets[row][column], NoneWidget):
            self.widgets[row].insert(column, widget)
        else:
            self.widgets[row][column] = widget
    
    def remove(self, widget):
        for row in self.widgets:
            if widget in row:
                row.remove(widget)
                break
    
    def update(self):
        for row in range(len(self.widgets)):
            for column in range(len(self.widgets[row])):
                widget = self.widgets[row][column]
                if column != 0:
                    widget.rect.left = self.widgets[row][column-1].rect.right + self.column_spacing
                    widget.rect.top = self.widgets[row][column-1].rect.top
                else:
                    widget.rect.left = self.pos[0]
                    if row != 0:
                        widget.rect.top = self.widgets[row-1][column].rect.bottom + self.row_spacing
                    else:
                        widget.rect.top = self.pos[1]

class NoneWidget:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 0, 0)

class EmptyWidget:
    def __init__(self, size, pos=(0, 0), color=(0, 0, 0)):
        self.image = pygame.Surface(size)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = pos
    
    def update(self, events, dt=1): pass

class ColorDisplay:
    def __init__(self, size, color_var=Var([255, 255, 255])):
        self.size = size
        self.color_var = color_var
        self.update()
    
    def update(self, events=[], dt=1):
        self.image = pygame.Surface(self.size)
        pygame.draw.rect(self.image, self.color_var.get(), rect=pygame.Rect((0, 0), self.size))
        self.rect = self.image.get_rect()

class Selector(Selectable):
    def __init__(self, items:list[tuple[str, object]], on_return = None, pos=(0, 0)):
        super().__init__()
        self.items = items
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
        item_name = self.items[self.highlighted_index][0]
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
        return self.items[self.selected_index]
    
    def update(self, events, dt=1):
        if not self.selected: return
        for event in events:
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    self.selected_index = self.highlighted_index
                    self.on_return(self.get_selected())
                elif event.key == K_RIGHT:
                    self.highlighted_index += 1
                    self.highlighted_index %= len(self.items)
                    self.redraw()
                elif event.key == K_LEFT:
                    self.highlighted_index -= 1
                    self.highlighted_index %= len(self.items)
                    self.redraw()

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
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE:
                    text = text[:-1]
                elif event.key == K_RETURN:
                    if self.on_return: self.on_return(text)
                elif event.unicode:
                    text += event.unicode
        self.cursor_timer += dt
        self.var.set(text)
        self.draw()

if __name__ == "__main__":
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
    s.items.append(("three", 3))

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