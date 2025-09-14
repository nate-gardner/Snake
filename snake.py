import pygame
from pygame.locals import *
import random
import math
import os
import json
import menu
# from backups import menu

def sortPair(x1, x2):
    if x1 >= x2: return x1, x2
    elif x2 > x1: return x2, x1

class Item:
    name:str
    def __init__(self):
        self.instances = set()
        self.color:tuple[int, int, int]
        self.image = pygame.Surface((10, 10))
        self.image.fill(self.color)
    
    def __iter__(self):
        return iter(self.instances)
    
    def __contains__(self, value):
        for instance in self.instances:
            if tuple(value) == instance: return True
        return False
    
    def newInstance(self, pos):
        self.instances.add(tuple(pos))
    
    def removeInstance(self, pos):
        self.instances.discard(tuple(pos))
    
    def clearInstances(self):
        self.instances.clear()
    
    def on_collect(self, snake, pos):
        self.removeInstance(pos)
    
    def while_active(self, snake):
        pass

class Fruit(Item):
    name = 'fruit'
    def __init__(self):
        self.color = (255, 0, 0)
        super().__init__()
        self.image = pygame.image.load("images/fruit.png")
        self.sound = pygame.mixer.Sound("sounds/munch.mp3")

    def on_collect(self, snake, pos):
        self.sound.play()
        snake.score += 1
        snake.segments_to_add += 1
        super().on_collect(snake, pos)
    
class Speed(Item):
    name = 'speed'
    def __init__(self):
        self.color = (255, 255, 0)
        super().__init__()
        self.image = pygame.image.load("images/speed.png")
    
    def on_collect(self, snake, pos):
        snake.effect = self.while_active
        snake.effect_timer = 3 # duration in seconds
        super().on_collect(snake, pos)

    def while_active(self, snake):
        snake.speed = snake.default_speed + 30

class Magnet(Item):
    name = 'magnet'
    def __init__(self):
        self.color = (0, 0, 0)
        super().__init__()
        self.image = pygame.image.load("images/magnet.png")

    def on_collect(self, snake, pos):
        snake.effect = self.while_active
        snake.effect_timer = 5 # duration in seconds
        super().on_collect(snake, pos)

    def while_active(self, snake):
        snake.collection_radius = snake.default_collection_radius + 3

class Wall:
    def __init__(self):
        self.color = "#858585"
        self.instances = []
        self.image = pygame.Surface((10, 10))
        self.image.fill(self.color)
    
    def __iter__(self):
        return iter(self.instances)
    
    def __contains__(self, value):
        return tuple(value) in self.instances
    
    def newInstance(self, pos):
        if tuple(pos) in self.instances:
            self.removeInstance(pos)
        else:
            self.instances.append(tuple(pos))

    def removeInstance(self, pos):
        self.instances.remove(tuple(pos))
    
    def clearInstances(self):
        return
    
    def setInstances(self, instances):
        self.instances.clear()
        for instance in instances:
            self.instances.append(tuple(instance))

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
    
    def update(self, events, items:list[Item], players, walls, dt):
        if not self.alive:
            return
        # Process input
        for event in events:
            if event.type == KEYDOWN:
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
    
    def getClosestItem(self, items:list[Fruit]):
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

class World:
    def __init__(self, name=''):
        self.items = [Fruit(), Speed(), Magnet()]
        self.item_weights = [80, 10, 10]
        self.walls = Wall()
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.next_bot_id = 0
        self.name = name
    
    @staticmethod
    def from_data(data, items_by_name):
        world = World(data["name"])
        world.walls.setInstances(data["walls"])
        items = []
        for item_name in data["item_names"]:
            try:
                items.append(items_by_name[item_name]())
            except KeyError:
                pass
        world.items = items
        world.item_weights = data["item_weights"]
        return world
    
    def getData(self):
        data = {}
        data["name"] = self.name
        data["walls"] = list(self.walls.instances)
        item_names = []
        for item in self.items:
            item_names.append(item.name)
        data["item_names"] = item_names
        data["item_weights"] = self.item_weights
        return data
    
    def show_scores(self, players:list[Player]):
        font = pygame.freetype.Font(None, 15)
        image = pygame.Surface((810, 810))
        line = 0
        for player in players:
            if not player.alive:
                continue
            score = f"{player.name.capitalize()}: {player.score}"
            img, rect = font.render(score, "white")
            rect.centerx = player.pos[0] * 10
            rect.centery = player.pos[1] * 10 - 20
            image.blit(img, rect)
            line += 1
        image.set_colorkey("black")
        return image
    
    def scoreboard(self, players:list[Player]):
        font = pygame.freetype.Font(None, 20)
        image = pygame.Surface((810, 810))
        line = 0
        image.fill("purple")
        image.set_colorkey("purple")
        image.fill("#00000073")
        for player in players:
            score = f"{player.name.capitalize()}: {player.score}"
            img, rect = font.render(score, "white")
            rect.centerx = 400
            rect.centery = 100 + line*25
            image.blit(img, rect)
            line += 1
        return image
    
    def start(self, players:list[Player], bots:int):
        for _ in range(bots):
            players.append(Bot(self.new_bot_id()))
        for player in players:
            player.join(self)
        dt = 0
        item_timer = 0
        running = True
        while running:
            one_alive = False
            for player in players:
                if not player.alive:
                    continue
                one_alive = True
                break
            events = pygame.event.get()
            for event in events:
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
            if one_alive:
                while item_timer >= 1.5:
                    item_timer -= 1.5
                    self.new_item(players)
                else:
                    item_timer += dt/1000
                self.screen.fill((0, 0, 0))
                for player in players:
                    if not player.alive:
                        continue
                    player.update(events, self.items, players, self.walls, dt)
                    for part in player.body:
                        pygame.draw.rect(self.screen, player.color, pygame.Rect(part[0]*10, part[1]*10, 10, 10))
                for item in self.items:
                    for instance in item:
                        self.screen.blit(item.image, (instance[0]*10, instance[1]*10))
                for wall in self.walls:
                    self.screen.blit(self.walls.image, (wall[0]*10, wall[1]*10))
                self.screen.blit(self.show_scores(players), (0, 0))
            else:
                self.screen.blit(self.scoreboard(players), (0, 0))
            pygame.display.flip()
            dt = self.clock.tick(40)
            # print(self.clock.get_fps())
        for player in players:
            player.reset()
            player.leave(self)
        for _ in range(bots):
            players.pop()
        for item in self.items:
            item.clearInstances()
        self.next_bot_id = 0

    def new_item(self, players):
        item = random.choice(random.choices(self.items, self.item_weights))
        pos = [random.randint(0, 80), random.randint(0, 80)]
        obstacles = []
        for item0 in self.items:
            obstacles.extend(item0)
        for player in players:
            obstacles.extend(player.body)
        while pos in obstacles:
            pos = [random.randint(0, 80), random.randint(0, 80)]
        item.newInstance(pos)
    
    def new_bot_id(self):
        self.next_bot_id += 1
        return self.next_bot_id + 0.1

    def modify(self):
        running = True
        x1, y1, x2, y2 = None, None, None, None
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                elif event.type == MOUSEBUTTONDOWN:
                    x1, y1 = event.pos[0]//10, event.pos[1]//10
                elif event.type == MOUSEBUTTONUP:
                    if x1 == None or y1 == None: continue
                    x2, y2 = event.pos[0]//10, event.pos[1]//10
                    x1, x2 = sortPair(x1, x2)
                    y1, y2 = sortPair(y1, y2)
                    for x in range(x2, x1+1):
                        for y in range(y2, y1+1):
                            self.walls.newInstance((x, y))
                    x1, y1, x2, y2 = None, None, None, None
            self.screen.fill((0, 0, 0))
            for wall in self.walls:
                self.screen.blit(self.walls.image, (wall[0]*10, wall[1]*10))
            pygame.display.flip()
            dt = self.clock.tick(40)
            # print(self.clock.get_fps())
        pass

class App:
    def __init__(self):
        pygame.init()
        with open("saves/colors.json", "r") as colors:
            self.colors = json.load(colors)
        with open("saves/keysets.json", "r") as keysets:
            self.keysets = json.load(keysets)
        self.players = [Player(self.colors["forest green"], self.keysets["arrows"], 0),]
        
        SIZE = WIDTH, HEIGHT = 810, 810
        self.screen = pygame.display.set_mode(SIZE)
        self.clock = pygame.time.Clock()

        self.items = {Fruit.name: Fruit, Speed.name:Speed}
        self.getWorldSaves()
        self.world = self.worlds[0]

        self.active_menu = None
        self.bots = menu.Var(0)

        # MAIN MENU
        main_menu = menu.Menu()
        # title
        main_menu.widgets.append(menu.Label("Snake Game", (100, 25)))
        # settings menu button
        main_menu.widgets.append(menu.Button("Settings", lambda:self.set_active_menu(settings_menu), (WIDTH//2, HEIGHT//2-30)))
        # play button
        main_menu.widgets.append(menu.Button("Play", lambda:World.start(self.world, self.players, self.bots.get()), (WIDTH//2, HEIGHT//2+30)))

        # SETTINGS MENU
        settings_menu = menu.Menu()
        # title
        settings_menu.add(menu.Label("Settings"), row=0, column=0)
        # space
        settings_menu.add(menu.EmptyWidget((50, 50)), row=1, column=0)
        # bot manager
        settings_menu.add(menu.Label("Bots: "), row=2, column=0)
        settings_menu.add(menu.Button("-", lambda:self.bots.__sub__(1)), row=2, column=1)
        settings_menu.add(menu.DynamicLabel(self.bots), row=2, column=2)
        settings_menu.add(menu.Button("+", lambda:self.bots.__add__(1)), row=2, column=3)
        # space
        settings_menu.add(menu.EmptyWidget((50, 50)), row=3, column=0)
        # Current World Display
        self.world_name = menu.Var(self.world.name)
        settings_menu.add(menu.Label("Current World: "), row=4, column=0)
        settings_menu.add(menu.DynamicLabel(self.world_name), row=4, column=1)
        # world menu button
        settings_menu.add(menu.Button("World Settings", lambda:self.set_active_menu(world_menu)), row=5, column=0)
        # back button
        settings_menu.widgets.append(menu.Button("Back", lambda:self.set_active_menu(main_menu), (700, 750)))

        # WORLD SETTINGS MENU
        world_menu = menu.Menu()
        # title
        world_menu.add(menu.Label("World Settings"), row=0, column=0)
        # space
        world_menu.add(menu.EmptyWidget((50, 50)), row=1, column=0)
        # Current World Display
        world_menu.add(menu.Label("Current World: "), row=2, column=0)
        world_menu.add(menu.DynamicLabel(self.world_name), row=2, column=1)
        # world selection
        world_menu.add(menu.Label("Select World: "), row=3, column=0)
        world_menu.add(menu.Selector(self.world_items_var, self.set_world), row=3, column=1)
        # space
        world_menu.add(menu.EmptyWidget((50, 50)), row=4, column=0)
        # rename world
        world_menu.add(menu.Label("Rename World: "), row=5, column=0)
        world_menu.add(menu.TextInput(default_text='Name', on_return=self.remameWorld), row=5, column=1)
        # new world
        world_menu.add(menu.Button("New World", self.newWorld), row=6, column=0)
        # modify world
        world_menu.add(menu.Button("Modify World", lambda:self.world.modify()), row=7, column=0)
        # save world
        world_menu.add(menu.Button("Save World", self.saveWorld), row=8, column=0)
        # Delete world
        world_menu.add(menu.Button("Delete World", self.delete_world), row=9, column=0)
        # back button
        world_menu.widgets.append(menu.Button("Back", lambda:self.set_active_menu(settings_menu), (700, 750)))

        self.active_menu = main_menu

    def set_world(self, item):
        self.world = item[1]
        self.world_name.set(self.world.name)

    def delete_world(self):
        if self.world.name == "default":
            return
        world_index = self.worlds.index(self.world)
        self.world_items_var.get().remove([self.worlds[world_index].name, self.worlds[world_index]])
        os.remove(f"saves/worlds/{self.world.name}.json")
        self.set_world((self.worlds[world_index-1].name, self.worlds[world_index-1]))
    
    def newWorld(self):
        world = World("world")
        name = world.name
        world_names = []
        for world in self.worlds:
            world_names.append(world.name)
        while name in world_names:
            name = name + '-'
        world.name = name
        with open(f"saves/worlds/{world.name}.json", "w") as f:
            json.dump(world.getData(), f)
        world_items = self.world_items_var.get()
        world_items.append([world.name, world])
        world_items = self.world_items_var.set(world_items)

    def remameWorld(self, name):
        if self.world.name == "default":
            return
        os.rename(f"saves/worlds/{self.world.name}.json", f"saves/worlds/{name}.json")
        for item in self.world_items_var.get():
            if item[0] == self.world.name:
                item[0] = name
        self.world.name = name
        self.world_name.set(name)
        self.saveWorld()
    
    def saveWorld(self):
        if self.world.name == "default":
            return
        with open(f"saves/worlds/{self.world.name}.json", "w") as f:
            json.dump(self.world.getData(), f, indent=4)
    
    def getWorldSaves(self):
        self.worlds = [World("default")]
        with os.scandir("saves/worlds") as saves:
            for save in saves:
                if save.is_file():
                    if save.name.endswith(".json"):
                        with open(save.path, "r") as s:
                            self.worlds.append(World.from_data(json.load(s), self.items))
        world_items = []
        for world in self.worlds:
            world_items.append([world.name, world])
        self.world_items_var = menu.Var(world_items)

    def set_active_menu(self ,menu):
        self.active_menu = menu

    def mainloop(self, framerate=0):
        running = True
        while running:
            if self.bots.get() < 0: self.bots.set(0)
            events = pygame.event.get()
            for event in events:
                if event.type == QUIT:
                    running = False
            self.screen.fill((0, 0, 0))
            self.active_menu.update(events)
            self.active_menu.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(framerate)

        pygame.quit()

if __name__ == "__main__":
    app = App()
    app.mainloop(20)