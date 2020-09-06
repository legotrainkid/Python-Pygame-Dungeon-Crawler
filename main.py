import pygame
import math
import random
import generation
import pathfinding

pygame.init()

move = [0, 0]
SCREENSIZE = [1200,1000]

class Game():
    def __init__(self):
        self.YELLOW = (255, 255, 0)
        self.BLUE = (10, 10, 220)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.FPS_FONT = pygame.font.Font("freesansbold.ttf", 11)
        self.SCORE_FONT = pygame.font.Font("freesansbold.ttf", 18)
        self.MOVE_SPEED = 3
        self.MAPSIZE = 80
        self.FPS = 60

        self.score = 0
        self.game_running = True

        self.screen = pygame.display.set_mode(SCREENSIZE)

        self.screen.fill(self.BLACK)

        loading = "LOADING..."
        text = self.SCORE_FONT.render(loading, 1, self.WHITE)
        self.screen.blit(text, (600,500))
        pygame.display.flip()

        self.clock = pygame.time.Clock()

        dg = generation.Generator(width=self.MAPSIZE, height=self.MAPSIZE)
        dg.gen_level()
        self.world_map = dg.return_tiles()

        self.TILES = {}
        load_tiles = ["empty", "floor", "wall"]
        for tile in load_tiles:
            self.TILES[tile] = pygame.image.load("graphics/world/"+tile+".png")

        self.tiles_list = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        
        self.spawned_tiles = []

        y_v = 0
        x_v = 0
        i = 0
        for y in range(len(self.world_map)):
            for x in self.world_map[y]:
                if x == 0:
                    new = Tile(self.TILES["empty"], x_v, y_v, True, [i, y])
                elif x == 1:
                    new = Tile(self.TILES["wall"], x_v, y_v, True, [i, y])
                    self.walls.add(new)
                elif x == 2:
                    new = Tile(self.TILES["floor"], x_v, y_v, False, [i, y])
                x_v += 50
                self.tiles_list.add(new)
                self.all_sprites.add(new)
                i+=1
            y_v += 50
            x_v = 0
            i = 0
        self.player = Player(30)
        self.spawn_enemies(10)
        
        self.all_sprites.add(self.player)

        self.spawn_player()

    def update_fps(self):
        fps = "FPS: " + str(math.ceil(self.clock.get_fps()))
        fps_text = self.FPS_FONT.render(fps, 1, self.WHITE)
        self.screen.blit(fps_text, (0,0))

    def spawnable_tiles(self):
        spawnable = []
        for y in range(len(self.world_map)):
            for x in range(len(self.world_map[y])):
                if self.world_map[y][x] == 2:
                    spawnable.append([x, y])
        return spawnable

    def spawn_player(self):
        global move
        invalid_spawn = True
        while invalid_spawn:
            move_x = random.randint(0, self.MAPSIZE)
            move_y = random.randint(0, self.MAPSIZE)
            move = [-move_x, -move_y]
            self.all_sprites.update()
            hit_list = pygame.sprite.spritecollide(self.player, self.tiles_list, False)
            invalid_spawn = False
            for tile in hit_list:
                if tile.is_barrier:
                    invalid_spawn = True
            move = [0, 0]

    def spawn_enemies(self, num):
        for i in range(num):
            pos = self.spawn_ent()
            enemy = Enemy(pos, i)
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)

    def spawn_ent(self):
        tiles = self.spawnable_tiles()
        spawned = False
        while not spawned:
            tile = random.choice(tiles)
            if tile not in self.spawned_tiles:
                pos = self.tile_pos(tile)
                self.spawned_tiles.append(tile)
                spawned = True
        return pos

    def tile_pos(self, tile):
        pos_x = tile[0] * 50
        pos_y = tile[1] * 50
        return [pos_x, pos_y]

    def main(self):
        global move
        can_move = [True, True, True, True]
        last_move = [0, 0]
        enemies = self.enemies.sprites()
        tile_map = []
        game_over = False
        for y in range(len(self.world_map)):
            row = []
            for x in range(len(self.world_map[y])):
                if self.world_map[y][x] == 2:
                    row.append(0)
                else:
                    row.append(1)
            tile_map.append(row)
        for enemy in enemies:
            tiles_hit = pygame.sprite.spritecollide(enemy, self.tiles_list, False)
            if tiles_hit:
                enemy.pos = tiles_hit[0].pos
            else:
                enemy.pos = [0, 0]
        while self.game_running:
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w and can_move[1]:
                        move = [0, self.MOVE_SPEED]
                    elif event.key == pygame.K_s and can_move[0]:
                        move = [0, -self.MOVE_SPEED]
                    elif event.key == pygame.K_a and can_move[3]:
                        move = [self.MOVE_SPEED, 0]
                    elif event.key == pygame.K_d and can_move[2]:
                        move = [-self.MOVE_SPEED, 0]
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_w:
                        move = [0, 0]
                    elif event.key == pygame.K_s:
                        move = [0, 0]
                    elif event.key == pygame.K_a:
                        move = [0, 0]
                    elif event.key == pygame.K_d:
                        move = [0, 0]
            
            self.screen.fill(self.BLACK)

            hit_walls = pygame.sprite.spritecollide(self.player, self.walls, False)
            for wall in hit_walls:
                if last_move[0] > 0:
                    move[0] = -self.MOVE_SPEED*2
                elif last_move[0] < 0:
                    move[0] = self.MOVE_SPEED*2
                if last_move[1] > 0:
                    move[1] = -self.MOVE_SPEED*2
                elif last_move[1] < 0:
                    move[1] = self.MOVE_SPEED*2
                self.all_sprites.update()
            if hit_walls:
                last_move = move
                move = [0, 0]
            else:
                self.all_sprites.update()
                last_move = move

            x_pos = 0
            y_pos = 0

            tiles_hit = pygame.sprite.spritecollide(self.player, self.tiles_list, False)
            for tile in tiles_hit:
                x_pos += tile.pos[0]
                y_pos += tile.pos[1]
            if tiles_hit:
                x_pos /= len(tiles_hit)
                y_pos /= len(tiles_hit)
                self.player.pos = [x_pos, y_pos]
            else:
                self.player.pos = [0, 0]

            for enemy in enemies:
                if enemy.moved:
                    x_pos = 0
                    y_pos = 0
                    tiles_hit = pygame.sprite.spritecollide(enemy, self.tiles_list, False)
                    for tile in tiles_hit:
                        x_pos += tile.pos[0]
                        y_pos += tile.pos[1]
                    if tiles_hit:
                        x_pos /= len(tiles_hit)
                        y_pos /= len(tiles_hit)
                        enemy.pos = [x_pos, y_pos]
                    else:
                        enemy.pos = [0, 0]
                if enemy.attack:
                    self.player.health -= enemy.damage
                    print("PLAYER HEALTH: " + str(self.player.health))
                    if self.player.health < 1:
                        game_over = True
                        self.player.health = 0
                        self.game_running = False
            
            for enemy in enemies:
                in_screen = False
                if 0 < enemy.rect.x < SCREENSIZE[0]:
                    if 0 < enemy.rect.y < SCREENSIZE[1]:
                        in_screen = True

                if enemy.frames_since >= 30 and not enemy.see_player and in_screen:
                    line = Line(enemy, self.player, self.screen)
                    line_list = pygame.sprite.spritecollide(line, self.walls, False)
                    if line_list:
                        enemy.see_player = False
                    else:
                        enemy.see_player = True
                    del line
                    continue
                    
                if enemy.update_path:
                    end = [int(self.player.pos[1]), int(self.player.pos[0])]
                    start = [int(enemy.pos[1]), int(enemy.pos[0])]
                    enemy.path = pathfinding.search(tile_map, 1, start, end)
                    continue

            for sprite in self.all_sprites.sprites():
                sprite.draw(self.screen)

            self.update_fps()
            pygame.display.flip()
            self.clock.tick(self.FPS)

        if game_over:
            loading = "GAME OVER"
            text = self.SCORE_FONT.render(loading, 1, self.RED)
            self.screen.blit(text, (600,500))
            pygame.display.flip()
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
        pygame.quit()

class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y, barrier, pos):
        # Call the parent class (Sprite) constructor
        super().__init__()
 
        self.image = image.convert()
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.is_barrier = barrier
        self.pos = pos

    def update(self):
        global move
        self.rect.x += move[0]
        self.rect.y += move[1]

    def draw(self, screen):
        if -55 < self.rect.x < SCREENSIZE[0]:
            if -55 < self.rect.y < SCREENSIZE[1]:
                screen.blit(self.image, self.rect)

class Player(pygame.sprite.Sprite):
    def __init__(self, health):
        super().__init__()

        self.image = pygame.image.load("graphics/characters/player.png").convert()

        self.rect = self.image.get_rect()

        self.rect.x = int(SCREENSIZE[0]/2-17.5)
        self.rect.y = int(SCREENSIZE[1]/2-17.5)
        self.pos = []

        self.health = health

    def update(self):
        pass

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frame):
        super().__init__()
        self.image = pygame.image.load("graphics/characters/enemy.png").convert()
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

    def update(self):
        global move
        self.move_to_player()
        self.rect.x += move[0]+self.to_move_x
        self.rect.y += move[1]+self.to_move_y
        
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
            self.to_move_x = 2*self.goal_x
            self.to_move_y = 2*self.goal_y
        else:
            self.to_move_x = 0
            self.to_move_y = 0

    @property
    def attack(self):
        if SCREENSIZE[0]/2-50 < self.rect.x < SCREENSIZE[0]/2+50:
            if SCREENSIZE[1]/2-50 < self.rect.y < SCREENSIZE[1]/2+50:
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

    @property
    def on_screen(self):
        if -40 < self.rect.x < SCREENSIZE[0] + 40:
            if -75 < self.rect.y < SCREENSIZE[1]+75:
                return True
            else:
                return False
        else:
            return False

class Line(pygame.sprite.Sprite):
    def __init__(self, enemy, player, screen):
        self.rect = pygame.draw.line(screen, (0, 0, 0), player.rect[0:2], enemy.rect[0:2])
        
if __name__ == "__main__":
    game = Game()
    game.main()
    
