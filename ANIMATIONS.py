import pygame

class Animation():
    def __init__(self, path, frames, name):
        self.image = None
        self.path = path
        self.image_list = []
        for i in range(frames):
            image = pygame.image.load(path + str(i+1) + ".png")
            self.image_list.append(image)
        self.name = name
        self.playing = False
        self.frame = -1
        self.index = 0
        self.total = frames

    def start(self):
        self.playing = True
        self.frame = 1
        self.index = 2

    def update(self):
        if self.playing:
            if self.index > 2:
                self.index = 2
            if self.frame == self.total:
                return self.stop()
            elif self.index == 2:
                self.frame += 1
                self.index = 0
                return self.image_list[self.frame-1]
            self.index += 1

    def stop(self):
        self.playing = False
        self.frame = -1
        self.index = 0
        return "end"

class Animator():
    def __init__(self, entity, animations):
        self.entity = entity
        self.animations = []
        self.load_anim(animations)
        self.current = None
        self.playing = False
        self.default = entity.image

    def play_animation(self, name):
        for anim in self.animations:
            if anim.name == name:
                self.current = anim
                self.playing = True
                self.current.start()
                return True
        if not self.playing:
            return False

    def update(self):
        if self.playing and self.current:
            image = self.current.update()
            if image != "end":
                if image:
                    self.entity.image = image.convert()
            else:
                self.stop()

    def stop(self):
        self.current = None
        self.playing = False
        self.entity.image = self.default

    def load_anim(self, anim_data):
        for anim in anim_data:
            animation = Animation(anim[0], anim[1], anim[2])
            self.animations.append(animation)
            


