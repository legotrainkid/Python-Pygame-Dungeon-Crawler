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
        self.MAPSIZE = 20
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
        self.player = Player()
        self.spawn_enemies(15)
        
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
        tile_map = {}
        for y in range(len(self.world_map)):
            for x in range(len(self.world_map[y])):
                if self.world_map[y][x] == 2:
                    tile_map[(x, y)] = "."
                else:
                    tile_map[(x, y)] = "#"
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

            tiles_hit = pygame.sprite.spritecollide(self.player, self.tiles_list, False)
            if tiles_hit:
                self.player.pos = tiles_hit[0].pos
            else:
                self.player.pos = [0, 0]

            
            for enemy in enemies:
                if enemy.moved:
                    tiles_hit = pygame.sprite.spritecollide(enemy, self.tiles_list, False)
                    if tiles_hit:
                        enemy.pos = tiles_hit[0].pos
                    else:
                        enemy.pos = [0, 0]

            for enemy in enemies:
                if enemy.update_path:
                    enemy.path = pathfinding.astar_search(tile_map, enemy.pos, self.player.pos)
                    continue

            for sprite in self.all_sprites.sprites():
                sprite.draw(self.screen)

            self.update_fps()
            pygame.display.flip()
            self.clock.tick(self.FPS)

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
    def __init__(self):
        super().__init__()

        self.image = pygame.image.load("graphics/characters/player.png").convert()

        self.rect = self.image.get_rect()

        self.rect.x = int(SCREENSIZE[0]/2-17.5)
        self.rect.y = int(SCREENSIZE[1]/2-17.5)
        self.pos = []

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

    def update(self):
        global move
        to_move = random.choice([True, False])
        if to_move:
            x_move = 0
            y_move = 0
        else:
            x_move = 0
            y_move = 0
        self.rect.x += move[0]+x_move
        self.rect.y += move[1]+y_move
        
        if x_move != 0 and y_move != 0:
            self.moved = True
        else:
            self.moved = False

        
        if move[0] != 0 or move[1] != 0:
            self.player_moved = True
        
        if self.frames_since > 30 and self.player_moved and self.see_player():
            self.update_path = True
            self.frames_since = 0
            self.player_moved = False
        else:
            self.update_path = False
            self.frames_since += 1

    def draw(self, screen):
        if -75 < self.rect.x < SCREENSIZE[0]+75:
            if -75 < self.rect.y < SCREENSIZE[1]+75:
                screen.blit(self.image, self.rect)

    def see_player(self):
        return False
if __name__ == "__main__":
    game = Game()
    game.main()
    
    pygame.quit()
