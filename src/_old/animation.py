import pygame


class SpriteAnimation:
    def __init__(self, sprite, size, nb_frames=20):
        self.image = pygame.image.load(sprite)
        self.image.set_colorkey((255, 255, 255))
        self.nb_frames = nb_frames
        self.sprite = []
        self.size = size
        self.sprite = [
            (self.image.subsurface(pygame.Rect(self.size[0] * i, 0, self.size[0], self.size[1])))
            for i in range(self.nb_frames)
        ]

        self.current_frame = 0

    def get_frame(self):
        k = self.current_frame
        if self.current_frame < self.nb_frames - 1:
            self.current_frame += 1
        else:
            self.current_frame = 0
        return self.sprite[k]
