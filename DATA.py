import pygame

def load_items():
    items = {"sword" : {"image" : pygame.image.load("graphics/items/inventory/sword.png").convert(),
             "selected" : pygame.image.load("graphics/items/inventory/sword_selected.png").convert(),
             "type" : "melee"}}
    return items

def load_player_anim():
    anim = [["graphics/characters/Player/damage_anim/player_damage_", 19, "damage"]]
    return anim
