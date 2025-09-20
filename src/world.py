import pygame
from pygame.locals import *
from items.magnet import Magnet
from items.fruit import Fruit
from items.speed import Speed
from wall import Wall
from players.bot import Bot
import random

def sortPair(x1, x2):
    if x1 >= x2: return x1, x2
    elif x2 > x1: return x2, x1

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
    
    def show_scores(self, players):
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
    
    def scoreboard(self, players):
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
    
    def start(self, players, bots:int):
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