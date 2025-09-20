from items.item import Item
    
class Speed(Item):
    name = 'speed'
    def __init__(self):
        self.color = (255, 255, 0)
        super().__init__()
    
    def on_collect(self, snake, pos):
        snake.effect = self.while_active
        snake.effect_timer = 3 # duration in seconds
        super().on_collect(snake, pos)

    def while_active(self, snake):
        snake.speed = snake.default_speed + 30