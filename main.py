import pygame
import math
import random
import generation
import pathfinding
import ENTITIES

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
        self.MOVE_SPEED = 2
        self.MAPSIZE = 80
        self.FPS = 60

        self.score = 0
        self.game_running = True

        self.screen = pygame.display.set_mode(SCREENSIZE)

        self.screen.fill(self.BLACK)

        import DATA

        self.items = DATA.load_items()

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
                    new = ENTITIES.Tile(self.TILES["empty"], x_v, y_v, True, [i, y], SCREENSIZE)
                elif x == 1:
                    new = ENTITIES.Tile(self.TILES["wall"], x_v, y_v, True, [i, y], SCREENSIZE)
                    self.walls.add(new)
                elif x == 2:
                    new = ENTITIES.Tile(self.TILES["floor"], x_v, y_v, False, [i, y], SCREENSIZE)
                x_v += 50
                self.tiles_list.add(new)
                self.all_sprites.add(new)
                i+=1
            y_v += 50
            x_v = 0
            i = 0
        self.player = ENTITIES.Player(30, 500, 1, SCREENSIZE)
        self.spawn_enemies(10)
        
        self.all_sprites.add(self.player)

        self.spawn_player()
        colors = {"red": self.RED, "green":self.GREEN}
        self.hud = ENTITIES.Hud(self.screen, colors, self.player)
        self.all_sprites.add(self.hud)
        self.inventory = ENTITIES.Inventory(self.player)
        self.all_sprites.add(self.inventory)
        self.inventory.add_item(self.items["sword"])
        
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
            self.update()
            hit_list = pygame.sprite.spritecollide(self.player, self.tiles_list, False)
            invalid_spawn = False
            for tile in hit_list:
                if tile.is_barrier:
                    invalid_spawn = True
            move = [0, 0]

    def spawn_enemies(self, num):
        for i in range(num):
            pos = self.spawn_ent()
            enemy = ENTITIES.Enemy(pos, i, SCREENSIZE)
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

    def update(self):
        for sprite in self.all_sprites.sprites():
            sprite.update(move)

    def main(self):
        global move
        can_move = [True, True, True, True]
        last_move = [0, 0]
        enemies = self.enemies.sprites()
        tile_map = []
        game_over = False
        mouse_sprite = ENTITIES.Sprite_Mouse_Location()
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
                    elif event.key == pygame.K_SPACE:
                        self.player.sprint = True
                        self.update_frames = 1
                    elif event.key == pygame.K_e:
                        if self.inventory.show:
                            self.inventory.show = False
                        else:
                            self.inventory.show = True
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_w:
                        move = [0, 0]
                    elif event.key == pygame.K_s:
                        move = [0, 0]
                    elif event.key == pygame.K_a:
                        move = [0, 0]
                    elif event.key == pygame.K_d:
                        move = [0, 0]
                    elif event.key == pygame.K_SPACE:
                        self.player.sprint = False
                        self.update_frames = 5
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.inventory.show:
                        if event.button == 1:
                            mouse_sprite.rect.x , mouse_sprite.rect.y = pygame.mouse.get_pos() # have to have this to update mouse here or get wrong location 
                            for s in self.inventory.items: #can't have outside the event or it will continuously check
                                if pygame.sprite.collide_rect(mouse_sprite, s):
                                    self.inventory.selected = s
                            for s in self.inventory.buttons:
                                if pygame.sprite.collide_rect(mouse_sprite, s):
                                    s.function()

            if self.player.sprint:
                self.MOVE_SPEED = 4
            else:
                self.MOVE_SPEED = 2
            if move[0] > 0:
                move[0] = self.MOVE_SPEED
            elif move[0] < 0:
                move[0] = -self.MOVE_SPEED
            elif move[1] > 0:
                move[1] = self.MOVE_SPEED
            elif move[1] < 0:
                move[1] = -self.MOVE_SPEED
            elif move[0] == 0 and move[1] == 0:
                self.player.sprint = False
            
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
                self.update()
            if hit_walls:
                last_move = move
                move = [0, 0]
            else:
                self.update()
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
                    line = ENTITIES.Line(enemy, self.player, self.screen)
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
                    if not tile_map[end[0]][end[1]] and not tile_map[start[0]][start[1]]:
                        enemy.path = pathfinding.search(tile_map, 1, start, end)
                    continue

            for sprite in self.all_sprites.sprites():
                sprite.draw(self.screen)

            self.update_fps()
            pygame.display.flip()
            self.clock.tick(self.FPS)

        if self.player.health == 0:
            lost = True
        else:
            lost = False
        if game_over:
            self.exit_screen(lost)
        pygame.quit()

    def exit_screen(self, lost, text=None):
        self.screen.fill(self.BLACK)
        if not text:
            if lost:
                text = "Game Over: You Lost"
            else:
                "Game Over: You Win"
        
        to_display = self.SCORE_FONT.render(text, 1, self.RED)
        self.screen.blit(to_display, (600,500))
        pygame.display.flip()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

if __name__ == "__main__":
    game = Game()
    game.main()
    
