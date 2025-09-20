import pygame

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