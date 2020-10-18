import pygame

def load_items():
    items = {"sword" : {"image" : pygame.image.load("graphics/items/inventory/sword.png").convert(),
             "selected" : pygame.image.load("graphics/items/inventory/sword_selected.png").convert(),
             "type" : "melee"}}
    return items
