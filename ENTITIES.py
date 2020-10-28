import pygame

class Arrow(pygame.sprite.Sprite):
    def __init__(self, x, y, image, damage):
        super().__init__()

        self.image = image.convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.change_x = 0
        self.change_y = 0

        self.damage = damage

    def update(self, move):
        self.rect.x += move[0] + self.change_x
        self.rect.y += move[1] + self.change_y

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y, barrier, pos, SCREENSIZE):
        super().__init__()
 
        self.image = image.convert()
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.is_barrier = barrier
        self.pos = pos

        self.SCREENSIZE = SCREENSIZE

    def update(self, move):
        self.rect.x += move[0]
        self.rect.y += move[1]

    def draw(self, screen):
        if -55 < self.rect.x < self.SCREENSIZE[0]:
            if -55 < self.rect.y < self.SCREENSIZE[1]:
                screen.blit(self.image, self.rect)

class Player(pygame.sprite.Sprite):
    def __init__(self, health, stamina, damage, SCREENSIZE):
        super().__init__()

        self.image = pygame.image.load("resources/graphics/characters/Player/player.png").convert()

        self.rect = self.image.get_rect()

        self.rect.x = int(SCREENSIZE[0]/2-17.5)
        self.rect.y = int(SCREENSIZE[1]/2-17.5)
        self.pos = []

        self.MAX_HEALTH = health
        self.health = health

        self.sprint = False
        self.stamina = stamina
        self.MAX_STAMINA = stamina

        self.NORMAL_DMG = damage
        self.damage = damage
        
        self.update_frames = 1
        self.inventory = []
        self.attack_range = 100

    def update(self, move):
        if self.stamina < 1:
            self.sprint = False
            self.stamina = 0
        if self.sprint:
            if not self.update_frames:
                self.stamina -= 1
                self.update_frames = 1
            else:
                self.update_frames-=1
        elif not self.sprint:
            if not self.update_frames:
                if self.stamina < self.MAX_STAMINA:
                    self.stamina +=1
                    self.update_frames = 5
            else:
                self.update_frames-=1
        if self.update_frames < 0:
            self.update_frames = 0

    def attack(self):
        return self.damage

    @property
    def can_attack(self):
        return True

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frame, SCREENSIZE):
        super().__init__()
        self.image = pygame.image.load("resources/graphics/characters/enemy.png").convert()
        self.rect = self.image.get_rect()

        self.rect.x = pos[0]+5
        self.rect.y = pos[1]+5

        self.pos = [0, 0]

        self.path = []

        self.moved = False

        self.update_path = False
        self.player_moved = False
        self.frames_since = frame

        self.see_player = False

        self.name = str(frame)

        self.goal_x = 0
        self.goal_y = 0

        self.to_move_x = 0
        self.to_move_y = 0

        self.attack_frames = 0
        self.cooldown = 120
        self.damage = 3

        self.SCREENSIZE = SCREENSIZE

        self.health = 10
        self.MAX_HEALTH = self.health

    def update(self, move):
        if not self.is_dead:
            self.move_to_player()
        else:
            self.to_move_x = 0
            self.to_move_y = 0
        self.rect.x += move[0]+self.to_move_x
        self.rect.y += move[1]+self.to_move_y

        if not self.is_dead:
            if self.to_move_x != 0 or self.to_move_y != 0:
                self.moved = True
            else:
                self.moved = False

            
            if move[0] != 0 or move[1] != 0:
                self.player_moved = True
            
            if self.frames_since > 30 and self.player_moved and self.see_player:
                self.update_path = True
                self.frames_since = 0
                self.player_moved = False
            elif self.frames_since > 30:
                self.frames_since = 0
            else:
                self.update_path = False
                self.frames_since += 1
            if self.see_player:
                self.see_player = False

    def move_to_player(self):
        if self.on_screen and self.path:
            if self.pos[0] == self.path[0][0] and self.pos[1] == self.path[0][1]:
                self.path = self.path[1:]
            self.move()
            
    def draw(self, screen):
        if self.on_screen:
            screen.blit(self.image, self.rect)
            if not self.is_dead:
                pygame.draw.rect(screen, (0, 0, 0),
                                           [self.rect.x-5,
                                            self.rect.y-10,
                                            45,
                                            5])
                pygame.draw.rect(screen, (255, 0, 0),
                                            [self.rect.x-5,
                                            self.rect.y-10,
                                            int(45*(self.health/self.MAX_HEALTH)),
                                            5])

    def move(self):
        if self.path:
            if self.pos[0] > self.path[0][0]:
                self.goal_x = -1
                self.goal_y = 0
            elif self.pos[0] < self.path[0][0]:
                self.goal_x = 1
                self.goal_y = 0
            elif self.pos[1] > self.path[0][1]:
                self.goal_y = -1
                self.goal_x = 0
            elif self.pos[1] < self.path[0][1]:
                self.goal_y = 1
                self.goal_x = 0
            self.to_move_x = 3*self.goal_x
            self.to_move_y = 3*self.goal_y
        else:
            self.to_move_x = 0
            self.to_move_y = 0

    @property
    def attack(self):
        if not self.is_dead:
            if self.SCREENSIZE[0]/2-50 < self.rect.x < self.SCREENSIZE[0]/2+50:
                if self.SCREENSIZE[1]/2-50 < self.rect.y < self.SCREENSIZE[1]/2+50:
                    if self.attack_frames > self.cooldown:
                        self.attack_frames = 0
                        return True
                    else:
                        self.attack_frames += 1
                        return False
                else:
                    self.attack_frames += 1
                    return False
            else:
                self.attack_frames += 1
                return False
        else:
            return False
        
    @property
    def on_screen(self):
        if -40 < self.rect.x < self.SCREENSIZE[0] + 40:
            if -75 < self.rect.y < self.SCREENSIZE[1]+75:
                return True
            else:
                return False
        else:
            return False

    @property
    def is_dead(self):
        if self.health < 1:
            self.health = 0
            return True
        else:
            return False

class Line(pygame.sprite.Sprite):
    def __init__(self, enemy, player, screen):
        self.rect = pygame.draw.line(screen, (0, 0, 0), player.rect[0:2], enemy.rect[0:2])

class Hud(pygame.sprite.Sprite):
    def __init__(self, screen, colors, player):
        super().__init__()
        self.colors = colors
        self.image = pygame.image.load("resources/graphics/hud/hud.png")
        self.rect = self.image.get_rect()

        self.rect.x = 0
        self.rect.y = 940

        self.screen = screen

        self.HEALTH_POS = [125, 949, 217, 18]
        self.STAMINA_POS = [125, 975, 217, 16]

        self.player = player

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        if self.player.health > 0:
            pygame.draw.rect(self.screen, self.colors["red"],
                                           [self.HEALTH_POS[0],
                                            self.HEALTH_POS[1],
                                            int(self.HEALTH_POS[2]*(self.player.health/self.player.MAX_HEALTH)),
                                            self.HEALTH_POS[3]])
        if self.player.stamina > 0:
            pygame.draw.rect(self.screen, self.colors["green"],
                                           [self.STAMINA_POS[0],
                                            self.STAMINA_POS[1],
                                            int(self.STAMINA_POS[2]*(self.player.stamina/self.player.MAX_STAMINA)),
                                            self.STAMINA_POS[3]])

class Inventory(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()

        self.image = pygame.image.load("resources/graphics/hud/inventory.png").convert()
        self.rect = self.image.get_rect()

        self.rect.x = 100
        self.rect.y = 100

        self.show = False

        self.player = player
        self.items = []
        self.buttons = []

        self.selected = None

        self.buttons.append(Button(pygame.image.load("resources/graphics/hud/equip_button.png").convert(), 725, 350, self.equip_item))
        self.buttons.append(Button(pygame.image.load("resources/graphics/hud/drop_button.png").convert(), 850, 350, self.drop_item))

        self.ITEM_POS = {"helmet" : [425, 115], "melee" : [347, 186]}
        self.equiped = {"helmet" : None, "melee" : None}

    def add_item(self, item_data):
        if len(self.items) < 364:
            self.items.append(Inventory_Item(item_data))
            return True
        else:
            return False

    def draw(self, screen):
        if self.show:
            screen.blit(self.image, self.rect)
            x = 117
            y = 414
            i = 1
            for item in self.items:
                if i == 21:
                    i = 1
                    x = 117
                    y += 49
                item.draw(x, y, screen)
                x += 49
                i += 1
            for button in self.buttons:
                button.draw(screen)
                equipment = ["helmet", "melee"]
            for item in equipment:
                if self.equiped[item]:
                    self.equiped[item].draw(self.ITEM_POS[item][0], self.ITEM_POS[item][1], screen)

    def update(self, move):
        if not self.show:
            self.selected = None
        for item in self.items:
            if item == self.selected:
                item.image = item.item["selected"]
            else:
                item.image = item.item["image"]

    def drop_item(self):
        if self.selected:
            for i in range(len(self.items)):
                if self.items[i] == self.selected:
                    del self.items[i]
                    break
            
    def equip_item(self):
        if self.selected:
            item_type = self.selected.item["type"]
            if self.equiped[item_type]:
                item = self.equiped[item_type]
                to_equip = self.selected
                for i in range(len(self.items)):
                    if self.items[i] == to_equip:
                        self.items[i] = item
                        self.equiped[item_type] = to_equip
                        break
            else:
                item = self.equiped[item_type]
                to_equip = self.selected
                for i in range(len(self.items)):
                    if self.items[i] == to_equip:
                        self.equiped[item_type] = to_equip
                        del self.items[i]
                        break
            self.selected.image = self.selected.item["image"]
            self.selected = None

class Item(pygame.sprite.Sprite):
    def __init__(self, item_data):
        self.item = item_data
        self.image = self.item["image"]
        self.rect = self.image.get_rect()

        self.rect.x = 0
        self.rect.y = 0

class Inventory_Item(pygame.sprite.Sprite):
    def __init__(self, item_data):
        self.item = item_data
        self.image = self.item["image"]
        self.rect = self.image.get_rect()

        self.rect.x = 0
        self.rect.y = 0

    def draw(self, x, y, screen):
        self.rect.x = x
        self.rect.y = y
        screen.blit(self.image, self.rect)

class Sprite_Mouse_Location(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect( 0 , 0 , 1 , 1 )

class Button(pygame.sprite.Sprite):
    def __init__(self, image, x, y, function):
        self.image = image
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y
        self.function = function

    def draw(self, screen):
        screen.blit(self.image, self.rect)
