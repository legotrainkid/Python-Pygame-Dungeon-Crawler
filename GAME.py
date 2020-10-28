import pygame
import math
import random
import generation
import pathfinding
import ENTITIES
import ANIMATIONS
import DATA

pygame.init()

move = [0, 0]
SCREENSIZE = [1200,1000]

class Game():
    def __init__(self, menu, screen):
        self.YELLOW = (255, 255, 0)
        self.BLUE = (10, 10, 220)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.FPS_FONT = pygame.font.Font("freesansbold.ttf", 11)
        self.SCORE_FONT = pygame.font.Font("freesansbold.ttf", 18)
        self.MOVE_SPEED = 2
        self.MAPSIZE = 20
        self.FPS = 60
        self.NUM_ENEMIES = 10
        self.PLAYER_DAMAGE = 5
        self.ARROW_SPEED = 10
        
        self.menu = menu

        self.score = 0
        self.game_running = True

        self.screen = screen

        self.screen.fill(self.BLACK)

        loading = "LOADING..."
        text = self.SCORE_FONT.render(loading, 1, self.WHITE)
        self.screen.blit(text, (600,500))
        pygame.display.flip()

        self.items = DATA.load_items()

        self.clock = pygame.time.Clock()

        dg = generation.Generator(width=self.MAPSIZE, height=self.MAPSIZE)
        dg.gen_level()
        self.world_map = dg.return_tiles()

        self.TILES = {}
        load_tiles = ["empty", "floor", "wall"]
        for tile in load_tiles:
            self.TILES[tile] = pygame.image.load("resources/graphics/world/"+tile+".png")

        self.tiles_list = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        
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
        self.player = ENTITIES.Player(30, 500, self.PLAYER_DAMAGE, SCREENSIZE)
        self.spawn_enemies(self.NUM_ENEMIES)
        
        self.all_sprites.add(self.player)

        self.spawn_player()
        colors = {"red": self.RED, "green":self.GREEN}
        self.hud = ENTITIES.Hud(self.screen, colors, self.player)
        self.all_sprites.add(self.hud)
        self.inventory = ENTITIES.Inventory(self.player)
        self.all_sprites.add(self.inventory)
        self.inventory.add_item(self.items["sword"])

        
        
        player_anim = DATA.load_player_anim()
        self.player_animator = ANIMATIONS.Animator(self.player, player_anim)

        self.animators = []
        self.animators.append(self.player_animator)
        
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

    def shoot_projectile(self, x, y):
        start_x = self.player.rect.x + 7.5
        start_y = self.player.rect.y + 7.5

        # Get from the mouse the destination location for the bullet
        # IMPORTANT! If you have a scrolling screen, you will also need
        # to add in self.view_bottom and self.view_left.
        dest_x = x-10
        dest_y = y-10

        # Do math to calculate how to get the bullet to the destination.
        # Calculation the angle in radians between the start points
        # and end points. This is the angle the bullet will travel.
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        # Angle the bullet sprite so it doesn't look like it is flying
        # sideways.
        image = pygame.image.load("resources/graphics/items/projectiles/arrow.png")
        arrow = ENTITIES.Arrow(start_x, start_y, pygame.transform.rotate(image, -math.degrees(angle)), 3)
        
        # Taking into account the angle, calculate our change_x
        # and change_y. Velocity is how fast the bullet travels.
        arrow.change_x = math.cos(angle) * self.ARROW_SPEED
        arrow.change_y = math.sin(angle) * self.ARROW_SPEED

        # Add the bullet to the appropriate lists
        self.all_sprites.add(arrow)
        self.projectiles.add(arrow)

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
        x = 0
        y = 0
        while self.game_running:
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.menu.running = False
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
                    else:
                        if event.button == 1:
                            mouse_sprite.rect.x , mouse_sprite.rect.y = pygame.mouse.get_pos()
                            center_x = SCREENSIZE[0]/2
                            center_y = SCREENSIZE[1]/2
                            if mouse_sprite.rect.x > center_x:
                                x = -1
                            else:
                                x = 1
                            if mouse_sprite.rect.y > center_y:
                                y = -1
                            else:
                                y = 1
                        elif event.button == 3:
                            mouse_sprite.rect.x , mouse_sprite.rect.y = pygame.mouse.get_pos()
                            self.shoot_projectile(mouse_sprite.rect.x , mouse_sprite.rect.y)
                            

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
                    self.player_animator.play_animation("damage")
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

            for arrow in self.projectiles.sprites():
                wall_list = pygame.sprite.spritecollide(arrow, self.walls, False)
                if wall_list:
                    arrow.kill()
                    del arrow
                else:
                    enemies_list = pygame.sprite.spritecollide(arrow, self.enemies, False)
                    for enemy in enemies_list:
                        enemy.health -= arrow.damage
                    if enemies_list:
                        arrow.kill()
                        del arrow

            killed = True
            left = 0
            for enemy in enemies:
                if x != 0 and self.player.can_attack:
                    lower_x = SCREENSIZE[0]/2-self.player.attack_range
                    upper_x = SCREENSIZE[0]/2+self.player.attack_range
                    if lower_x < enemy.rect.x < upper_x:
                        lower_y = SCREENSIZE[1]/2-self.player.attack_range
                        upper_y = SCREENSIZE[1]/2+self.player.attack_range
                        if lower_y < enemy.rect.y < upper_y:
                            if enemy.rect.x > SCREENSIZE[0]/2:
                                e_x = -1
                            else:
                                e_x = 1
                            if enemy.rect.y > SCREENSIZE[1]/2:
                                e_y = -1
                            else:
                                e_y = 1
                            if e_x == x and e_y == y:
                                enemy.health -= self.player.attack()
                if not enemy.is_dead:
                    killed = False
                    left += 1
                else:
                    enemy.remove(self.enemies)
            
                            
            x, y = 0, 0

            for animator in self.animators:
                animator.update()

            for sprite in self.all_sprites.sprites():
                sprite.draw(self.screen)

            self.update_fps()
            enemy_num_text = "ENEMIES LEFT: " + str(left)
            enemy_text = self.FPS_FONT.render(enemy_num_text, 1, self.BLUE)
            self.screen.blit(enemy_text, (580,0))
            pygame.display.flip()
            self.clock.tick(self.FPS)

            if killed:
                game_over = True
                self.game_running = False

        if self.player.health == 0:
            lost = True
        else:
            lost = False
        if game_over:
            self.exit_screen(lost)

    def exit_screen(self, lost, text=None):
        self.menu.exit_screen()
