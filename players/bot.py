from players.player import Player
import math

class Bot(Player):
    def __init__(self, id, color=(70, 50, 70)):
        super().__init__(color, {"up":"z", "down":"z", "left":"z", "right":"z"}, id)
    
    def __str__(self):
        return f"Bot {self.id}"
    
    def update(self, events_placeholder, items, players, walls, dt):
        # Change self.direction here
        pos = {"up":[self.pos[0], self.pos[1]-1], "down":[self.pos[0], self.pos[1]+1],
               "left":[self.pos[0]-1, self.pos[1]], "right":[self.pos[0]+1, self.pos[1]]}
        directions = ["up", "right", "down", "left"]
        direction_index = directions.index(self.direction)
        if pos[self.direction] in walls:
            if pos[directions[(direction_index+1)%4]] not in walls:
                self.change_to = directions[(direction_index+1)%4]
            else:
                self.change_to = directions[(direction_index-1)%4]
        else:
            closest_fruit = self.getClosestItem(items)
            if closest_fruit[0] <= self.pos[0] and self.direction == "right" or \
                closest_fruit[0] >= self.pos[0] and self.direction == "left":
                new_direction = "up" if closest_fruit[1] < self.pos[1] else "down"
                if pos[new_direction] not in walls:
                    self.change_to = new_direction
            elif closest_fruit[1] <= self.pos[1] and self.direction == "down" or \
                closest_fruit[1] >= self.pos[1] and self.direction == "up":
                new_direction = "left" if closest_fruit[0] < self.pos[0] else "right"
                if pos[new_direction] not in walls:
                    self.change_to = new_direction
        super().update([], items, players, walls, dt)
    
    def getClosestItem(self, items):
        pos = self.pos
        closest_fruit = pos
        dist_to_closest_fruit = 9999
        for item in items:
            for instance in item:
                dist_to_fruit = math.sqrt((pos[0]-instance[0])**2+(pos[1]-instance[1])**2)
                if dist_to_fruit < dist_to_closest_fruit:
                    closest_fruit = instance
                    dist_to_closest_fruit = dist_to_fruit
        return closest_fruit