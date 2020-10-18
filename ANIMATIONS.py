import pygame

class Animation():
    def __init__(self, path, frames, name):
        self.image = None
        self.path = path
        self.image_list = []
        for i in range(frames):
            image = pygame.image.load(path + str(i))
            self.image_list.append(image)
        self.name = name
        self.playing = False
        self.frame = -1
        self.index = 0
        self.total = frames

    def start(self):
        self.playing = True
        self.frame = 0
        self.index = 1

    def update(self):
        if playing:
            if self.index == 2:
                yield self.image_list[frame]
                self.frame += 1
            else:
                self.index += 1
            if self.frame == self.frames:
                self.stop()

    def stop(self):
        self.playing = False
        self.frame = -1
        self.index = 0
        return False

class Animator():
    def __init__(self, entity, animations):
        self.entity = entity
        self.animations = animations
        self.current = None
        self.playing = False

    def play_animation(self, name):
        for anim in self.animations:
            if anim.name == name:
                self.current = anim
                self.playing = True
                return True
        if not self.playing:
            return False

    def update(self):
        if self.playing and self.current:
            image = self.current.update()
            if image:
                self.entity.image = image.convert()
            else:
                self.stop()

    def stop(self):
        self.current = None
        self.playing = False
            


