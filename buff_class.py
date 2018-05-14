import pygame


class Buff:

    def __init__(self, gameDisplay, pos, pic):
        self.pos = pos
        self.pic = pygame.image.load(pic)

        self.gameDisplay = gameDisplay

    def position(self):
        return self.pos

    def draw(self):
        pic_rect = self.pic.get_rect()
        pic_rect.center = self.pos
        self.gameDisplay.blit(pic, pic_rect)
