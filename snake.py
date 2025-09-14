import pygame
from pygame.locals import *
import os
import json
import menu
from items.fruit import Fruit
from items.speed import Speed
from players.player import Player
from world import World
# from backups import menu

class App:
    def __init__(self):
        pygame.init()
        
        with open(os.path.join("saves", "colors.json"), "r") as colors:
            self.colors = json.load(colors)
            
        with open(os.path.join("saves", "keysets.json"), "r") as keysets:
            self.keysets = json.load(keysets)
            
        self.menu_music = None
        for file in os.scandir(os.path.join("sounds", "menu background")):
            if file.is_file():
                self.menu_music = file.path
                
        self.game_music = None
        for file in os.scandir(os.path.join("images", "game background")):
            if file.is_file():
                self.game_music = file.path
        
        if self.menu_music:
            pygame.mixer_music.load(self.menu_music)
            pygame.mixer_music.play(-1)
            
        self.players = [Player(self.colors["forest green"], self.keysets["arrows"], 0),]
        
        SIZE = WIDTH, HEIGHT = 810, 810
        self.screen = pygame.display.set_mode(SIZE)
        self.clock = pygame.time.Clock()

        self.items = {Fruit.name:Fruit, Speed.name:Speed}
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
        def start_game():
            pygame.mixer_music.stop()
            pygame.mixer_music.unload()
            pygame.mixer_music.load(self.game_music)
            pygame.mixer_music.play(-1)
            self.world.start(self.players, self.bots.get()), (WIDTH//2, HEIGHT//2+30)
            pygame.mixer_music.stop()
            pygame.mixer_music.unload()
            pygame.mixer_music.load(self.menu_music)
            pygame.mixer_music.play(-1)
            
        main_menu.widgets.append(menu.Button("Play", start_game))

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
        os.remove(os.path.join("saves", "worlds", f"{self.world.name}.json"))
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
        with open(os.path.join("saves", "worlds", f"{world.name}.json"), "w") as f:
            json.dump(world.getData(), f)
        world_items = self.world_items_var.get()
        world_items.append([world.name, world])
        world_items = self.world_items_var.set(world_items)

    def remameWorld(self, name):
        if self.world.name == "default":
            return
        os.rename(os.path.join("saves", "worlds", f"{self.world.name}.json"),
                  os.path.join("saves", "worlds", f"{name}.json"))
        for item in self.world_items_var.get():
            if item[0] == self.world.name:
                item[0] = name
        self.world.name = name
        self.world_name.set(name)
        self.saveWorld()
    
    def saveWorld(self):
        if self.world.name == "default":
            return
        with open(os.path.join("saves", "worlds", f"{self.world.name}.json"), "w") as f:
            json.dump(self.world.getData(), f, indent=4)
    
    def getWorldSaves(self):
        self.worlds = [World("default")]
        with os.scandir(os.path.join("saves", "worlds")) as saves:
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
                    
            self.active_menu.update(events)
            
            self.screen.fill((0, 0, 0))
            
            self.active_menu.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(framerate)

        pygame.quit()

if __name__ == "__main__":
    app = App()
    app.mainloop(20)