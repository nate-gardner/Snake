import pygame
from items.item import Item
import os


class Fruit(Item):
    name = 'fruit'
    def __init__(self):
        self.color = (255, 0, 0)
        super().__init__()

    def on_collect(self, snake, pos):
        snake.score += 1
        snake.segments_to_add += 1
        super().on_collect(snake, pos)