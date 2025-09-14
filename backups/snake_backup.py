import pygame
import pygame.freetype
from pygame.locals import *
import random
import math
import shelve

def sortPair(x1, x2):
    if x1 >= x2: return x1, x2
    elif x2 > x1: return x2, x1

class Item:
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

class Fruit(Item):
    def __init__(self):
        self.color = (255, 0, 0)
        super().__init__()

    def on_collect(self, snake, pos):
        snake.score += 1
        snake.segments_to_add += 1
        super().on_collect(snake, pos)

class Speed(Item):
    def __init__(self):
        self.color = (255, 255, 0)
        super().__init__()
    
    def on_collect(self, snake, pos):
        snake.speed += 5
        super().on_collect(snake, pos)

class Wall(Item):
    def __init__(self):
        self.color = (150, 150, 150)
        super().__init__()
    
    def newInstance(self, pos):
        if pos in self:
            self.removeInstance(pos)
        else:
            super().newInstance(pos)

    def clearInstances(self):
        return
    
    def setInstances(self, instances):
        self.instances.clear()
        self.instances.update(instances)

    def on_collect(self, snake, pos):
        snake.kill()

class Player:
    def __init__(self, color, controls, id):
        self.pos = [0, 0]
        self.body = [self.pos.copy()]
        self.score = 0
        self.id = id
        self.direction = random.choice(["up", "down", "left", "right"])
        self.controls = controls
        self.color = color
        self.name = f"Default {id}"
        self.segments_to_add = 0
        self.speed = 15 # cells per second
        self.alive = True
        self.change_to = self.direction
        self.accumulated_time = 0
        self.collection_radius = 0
    
    def __str__(self):
        return f"Player {self.id}"
    
    def update(self, events, items:list[Item], players, dt):
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
        while self.accumulated_time >= 1/self.speed:
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
                if self.pos in player.body:
                    self.kill()
                    if len(player.body) > 0 and self.pos == player.body[0]:
                        player.kill()
                    return
            if self.pos in items[1]:
                self.kill()
                return
            # collect fruit
            for x in range(self.pos[0]-self.collection_radius, self.pos[0]+self.collection_radius+1):
                for y in range(int(self.pos[1])-self.collection_radius, int(self.pos[1])+self.collection_radius+1):
                    for item in items:
                        if isinstance(item, Wall):
                            continue
                        if (x, y) in item:
                            item.on_collect(self, (x, y))
            #
            self.body.insert(0, self.pos.copy())
            if self.segments_to_add > 0:
                self.segments_to_add -= 1
            else:
                self.body.pop()
            self.accumulated_time -= 1/self.speed
        else:
            self.accumulated_time += dt/1000
    
    def kill(self):
        self.alive = False
        for pos in self.body:
            self.fruits.newInstance(pos)
        self.body.clear()
    
    def reset(self):
        self.alive = True
        self.pos = [random.randint(0, 40), random.randint(0, 40)]
        self.body = [self.pos.copy()]
        self.score = 0
        self.speed = 15
        self.fruits = []
        self.direction = random.choice(["up", "down", "left", "right"])
        self.change_to = self.direction
        self.accumulated_time = 0
        self.collection_radius = 0
        self.segments_to_add = 0
    
    def join(self, world):
        self.fruits = world.items[0]
        pos = [random.randint(0, 80), random.randint(0, 80)]
        while pos in world.items[1]:
            pos = [random.randint(0, 80), random.randint(0, 80)]
        self.pos = pos
    
    def leave(self, world):
        self.pos = [0, 0]

class Bot(Player):
    def __init__(self, id, color=(70, 50, 70)):
        super().__init__(color, {"up":0, "down":0, "left":0, "right":0}, id)
        self.name = f"Bot {self.id-0.1}"
    
    def __str__(self):
        return f"Bot {self.id}"
    
    def update(self, events_placeholder, items, players, dt):
        # Change self.direction here
        pos = {"up":[self.pos[0], self.pos[1]-1], "down":[self.pos[0], self.pos[1]+1],
               "left":[self.pos[0]-1, self.pos[1]], "right":[self.pos[0]+1, self.pos[1]]}
        directions = ["up", "right", "down", "left"]
        direction_index = directions.index(self.direction)
        walls = items[1]
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
        super().update([], items, players, dt)
    
    def getClosestItem(self, items:list[Item]):
        pos = self.pos
        closest_fruit = pos
        dist_to_closest_fruit = 9999
        for item in items:
            if isinstance(item, Wall):
                continue
            for instance in item:
                dist_to_fruit = math.sqrt((pos[0]-instance[0])**2+(pos[1]-instance[1])**2)
                if dist_to_fruit < dist_to_closest_fruit:
                    closest_fruit = instance
                    dist_to_closest_fruit = dist_to_fruit
        return closest_fruit

class World:
    def __init__(self, name=''):
        self.items = [Fruit(), Wall(), Speed()]
        self.item_weights = [90, 1, 9]
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.next_bot_id = 0
        self.name = name
    
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
                while item_timer >= 1:
                    item_timer -= 1
                    self.new_item(players)
                else:
                    item_timer += dt/1000
                self.screen.fill((0, 0, 0))
                for player in players:
                    if not player.alive:
                        continue
                    player.update(events, self.items, players, dt)
                    for part in player.body:
                        pygame.draw.rect(self.screen, player.color, pygame.Rect(part[0]*10, part[1]*10, 10, 10))
                for item in self.items:
                    for instance in item:
                        self.screen.blit(item.image, (instance[0]*10, instance[1]*10))
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
                            self.items[1].newInstance((x, y))
                    x1, y1, x2, y2 = None, None, None, None
            self.screen.fill((0, 0, 0))
            for item in self.items:
                for instance in item:
                    self.screen.blit(item.image, (instance[0]*10, instance[1]*10))
            pygame.display.flip()
            dt = self.clock.tick(40)
            # print(self.clock.get_fps())
        pass

class App:
    def __init__(self):
        pygame.init()
        self.colors = {'forest green': (50, 70, 50), 'light purple': (217, 217, 255), 'electric blue': (54, 217, 255), 'sea green': (54, 217, 171),
                       'royal purple': (54, 46, 171), 'chocolate brown': (54, 46, 28), 'muted purple': (54, 14, 28), 'light pink': (255, 217, 217),
                       'burgundy': (56, 15, 37), "tangerine": (255, 186, 93)}
        self.keysets = dict([("arrows", {"up":pygame.K_UP, "down":pygame.K_DOWN, "left":pygame.K_LEFT, "right":pygame.K_RIGHT}),
                        ("wasd", {"up":pygame.K_w, "down":pygame.K_s, "left":pygame.K_a, "right":pygame.K_d}),
                        ("tfgh", {"up":pygame.K_t, "down":pygame.K_g, "left":pygame.K_f, "right":pygame.K_h}),
                        ("ijkl", {"up":pygame.K_i, "down":pygame.K_k, "left":pygame.K_j, "right":pygame.K_l}),
                        ("[;'RETURN]", {"up":pygame.K_LEFTBRACKET, "down":pygame.K_QUOTE, "left":pygame.K_SEMICOLON, "right":pygame.K_RETURN}),
                        ("HOME,DELETE,END,PAGEDOWN", {"up":pygame.K_HOME, "down":pygame.K_END, "left":pygame.K_DELETE, "right":pygame.K_PAGEDOWN}),
                        ("KP/789", {"up":pygame.K_KP_DIVIDE, "down":pygame.K_KP8, "left":pygame.K_KP7, "right":pygame.K_KP9}),
                        ("KP5123", {"up":pygame.K_KP_5, "down":pygame.K_KP2, "left":pygame.K_KP1, "right":pygame.K_KP3})])
        self.players = [#Player(self.colors["light purple"], self.keysets["arrows"], 0),
                        Player(self.colors["forest green"], self.keysets["arrows"], 0)]
        import menu#from backups 

        SIZE = WIDTH, HEIGHT = 810, 810
        self.screen = pygame.display.set_mode(SIZE)
        self.clock = pygame.time.Clock()

        self.world = World()
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
        settings_menu.add(menu.DynamicLabel(self.bots, (150, 100)), row=2, column=2)
        settings_menu.add(menu.Button("+", lambda:self.bots.__add__(1)), row=2, column=3)
        # space
        settings_menu.add(menu.EmptyWidget((50, 50)), row=3, column=0)
        # world manager
        # worlds = self.getWorldSaves()
        # settings_menu.add(menu_backup.Label("Load World"), row=4, column=0)
        # settings_menu.add(menu_backup.Selector(worlds, self.loadWorld), row=4, column=1)
        settings_menu.add(menu.Button("World Editor", self.world.modify), row=5, column=0)
        # settings_menu.add(menu_backup.Button("Save Changes", self.saveWorld), row=6, column=0)
        # # new world manager
        # settings_menu.add(menu_backup.Label("New World:"), row=7, column=0)
        # new_world_name = menu_backup.Var('')
        # def addWorld(name):
        #     worlds.append((name, set()))
        #     new_world_name.set('')
        # settings_menu.add(menu_backup.TextInput(new_world_name, 'Name', on_return=addWorld), row=7, column=1)
        # # delete world manager
        # def deleteWorld():
        #     name = self.world.name
        #     if name == "default":
        #         self.world.items[1].instances = set()
        #         return
        #     worlds.remove((name, self.world.items[1].instances))
        #     file = shelve.open("saves/worlds.db")
        #     del file[self.world.name]
        #     file.close()
        # settings_menu.add(menu_backup.Button("Delete World", deleteWorld), row=8, column=0)
        # # space
        # settings_menu.add(menu_backup.EmptyWidget((50, 50)), row=9, column=0)
        # back button
        settings_menu.widgets.append(menu.Button("Back", lambda:self.set_active_menu(main_menu), (700, 750)))

        self.active_menu = main_menu
    
    def loadWorld(self, item):
        self.world.name = item[0]
        self.world.items[1].instances = item[1]

    def saveWorld(self):
        file = shelve.open("saves/worlds.db")
        file[self.world.name] = self.world.items[1].instances
        file.close()
    
    def getWorldSaves(self):
        file = shelve.open("saves/worlds.db")
        file["default"] = set()
        items = list(file.items())
        file.close()
        return items

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