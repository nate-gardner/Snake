import pygame
import random

class Player:
    def __init__(self, color, controls, id):
        self.pos = [0, 0]
        self.body = [self.pos.copy()]
        self.score = 0
        self.id = id
        self.direction = random.choice(["up", "down", "left", "right"])
        self.controls = {}
        self.controls["up"] = pygame.key.key_code(controls["up"])
        self.controls["down"] = pygame.key.key_code(controls["down"])
        self.controls["left"] = pygame.key.key_code(controls["left"])
        self.controls["right"] = pygame.key.key_code(controls["right"])
        self.color = color
        self.name = f"Player {id}"
        self.segments_to_add = 0
        self.default_speed = 10 # cells per second
        self.speed = self.default_speed
        self.alive = True
        self.change_to = self.direction
        self.accumulated_time = 0
        self.default_collection_radius = 0
        self.collection_radius = self.default_collection_radius
        self.effect = lambda s:None
        self.effect_timer = 0
    
    def reset(self):
        self.alive = True
        self.pos = [random.randint(0, 40), random.randint(0, 40)]
        self.body = [self.pos.copy()]
        self.score = 0
        self.speed = self.default_speed
        self.fruits = []
        self.direction = random.choice(["up", "down", "left", "right"])
        self.change_to = self.direction
        self.default_collection_radius = 0
        self.collection_radius = self.default_collection_radius
        self.segments_to_add = 0
        self.accumulated_time = 0
        self.effect_timer = 0
        self.effect = lambda s:None
    
    def __str__(self):
        return f"Player {self.id}"
    
    def update(self, events, items, players, walls, dt):
        if not self.alive:
            return
        # Process input
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == self.controls["up"]:
                    self.change_to = "up"
                elif event.key == self.controls["down"]:
                    self.change_to = "down"
                elif event.key == self.controls["left"]:
                    self.change_to = "left"
                elif event.key == self.controls["right"]:
                    self.change_to = "right"
        # only update according to speed
        self.speed = self.default_speed
        self.collection_radius = self.default_collection_radius
        self.effect_timer -= dt/1000
        if self.effect_timer <= 0:
            self.effect = lambda s:None
        self.effect(self)
        while self.accumulated_time > 1/self.speed:
            self.accumulated_time -= 1/self.speed

            # don't run into yourself
            if self.change_to  == "up" and self.direction != "down":
                self.direction = "up"
            elif self.change_to  == "down" and self.direction != "up":
                self.direction = "down"
            elif self.change_to  == "left" and self.direction != "right":
                self.direction = "left"
            elif self.change_to  == "right" and self.direction != "left":
                self.direction = "right"
            # move pos
            if self.direction == "up":
                self.pos[1] -= 1
            elif self.direction == "down":
                self.pos[1] += 1
            elif self.direction == "left":
                self.pos[0] -= 1
            elif self.direction == "right":
                self.pos[0] += 1
            # wrap around
            if self.pos[0] <= -1:
                self.pos[0] = 80
            elif self.pos[0] >= 81:
                self.pos[0] = 0
            elif self.pos[1] <= -1:
                self.pos[1] = 80
            elif self.pos[1] >= 81:
                self.pos[1] = 0
            # kill if touching any player
            for player in players:
                # if player is self: continue
                if self.pos in player.body:
                    self.kill()
                    if len(player.body) > 0 and self.pos == player.body[0]:
                        player.kill()
                    return
            if tuple(self.pos) in walls: self.kill()
            # collect fruit
            for x in range(self.pos[0]-self.collection_radius, self.pos[0]+self.collection_radius+1):
                for y in range(int(self.pos[1])-self.collection_radius, int(self.pos[1])+self.collection_radius+1):
                    for item in items:
                        if (x, y) in item:
                            item.on_collect(self, (x, y))
            #
            self.body.insert(0, self.pos.copy())
            if self.segments_to_add > 0:
                self.segments_to_add -= 1
            else:
                self.body.pop()
        else:
            self.accumulated_time += dt/1000
    
    def kill(self):
        self.alive = False
        for pos in self.body:
            self.fruits.newInstance(pos)
        self.body.clear()
    
    def join(self, world):
        self.fruits = world.items[0]
        pos = [random.randint(0, 80), random.randint(0, 80)]
        while pos in world.walls:
            pos = [random.randint(0, 80), random.randint(0, 80)]
        self.pos = pos
    
    def leave(self, world):
        self.pos = [0, 0]