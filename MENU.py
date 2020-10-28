import pygame
import GAME

SCREENSIZE = [1200,1000]

class Menu():
    def __init__(self):
        pygame.init()
        self.YELLOW = (255, 255, 0)
        self.BLUE = (10, 10, 220)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.SMALL_FONT = pygame.font.Font("freesansbold.ttf", 15)
        self.LARGE_FONT = pygame.font.Font("freesansbold.ttf", 20)
        
        self.screen = pygame.display.set_mode(SCREENSIZE)

        self.running = True

        self.screen.fill(self.BLACK)

        self.mouse_sprite = Sprite_Mouse_Location()

        self.main_screen()

    def main_screen(self):
        self.screen.fill(self.BLACK)
        buttons = []
        play_button = Button(pygame.image.load("resources/graphics/hud/play_button.png").convert(),
                             500, 300, self.run_game)
        buttons.append(play_button)
        for button in buttons:
            button.draw(self.screen)
        text = self.LARGE_FONT.render("PYTHON DUNGEON CRAWLER", 1, self.WHITE)
        text_w = text.get_width()/2
        self.screen.blit(text, (int(600-text_w), 200))
        pygame.display.flip()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.mouse_sprite.rect.x , self.mouse_sprite.rect.y = pygame.mouse.get_pos()
                        for button in buttons:
                            if pygame.sprite.collide_rect(self.mouse_sprite, button):
                                button.function()
            
    def credit_screen(self):
        pass

    def exit_screen(self):
        self.main_screen()

    def run_game(self):
        game = GAME.Game(self, self.screen)
        game.main()

class Button(pygame.sprite.Sprite):
    def __init__(self, image, x, y, function):
        self.image = image
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y
        self.function = function

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Sprite_Mouse_Location(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect( 0 , 0 , 1 , 1 )

if __name__ == "__main__":
    menu = Menu()
