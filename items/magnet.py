from items.item import Item

class Magnet(Item):
    name = 'magnet'
    def __init__(self):
        self.color = (0, 0, 0)
        super().__init__()

    def on_collect(self, snake, pos):
        snake.effect = self.while_active
        snake.effect_timer = 5 # duration in seconds
        super().on_collect(snake, pos)

    def while_active(self, snake):
        snake.collection_radius = snake.default_collection_radius + 3