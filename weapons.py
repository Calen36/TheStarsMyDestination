import pygame
from os import path
import random
from settings import HEIGHT, WIDTH

img_dir = path.join(path.dirname(__file__), 'img')


class Projectile(pygame.sprite.Sprite):
    """Base class for bullets"""
    def __init__(self, start_position, image, speed, damage):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect()
        self.rect.centerx = start_position[0]
        self.rect.centery = start_position[1]
        self.speed = speed
        self.damage = damage

    def update(self):
        """Moves bullet"""
        self.rect.y += self.speed

        if self.rect.bottom < 0:
            self.kill()


class Targeted(Projectile):
    def __init__(self, start_position, image, speed, damage, target_position, degradable=False):
        super().__init__(start_position, image, speed, damage)

        # Aiming for player
        tx = target_position[0]-start_position[0]
        ty = target_position[1]-start_position[1]
        dhyp = (tx**2+ty**2)**0.5
        k = self.speed/dhyp
        self.dx = round(k*tx)
        self.dy = round(k*ty)
        self.degradable = degradable
        self.lifetime = random.randrange(10, 90)

    def update(self):
        if self.degradable:
            self.lifetime -= 1
        if self.lifetime < 0 or self.rect.left + self.dx > WIDTH or self.rect.right + self.dx < 0\
                or self.rect.top + self.dy > HEIGHT or self.rect.bottom + self.dy < 0:
            self.kill()
        self.rect.center = (self.rect.centerx + self.dx, self.rect.centery + self.dy)


class Powerup(pygame.sprite.Sprite):

    def __init__(self, start_position, icons, rates=None, type=None):
        pygame.sprite.Sprite.__init__(self)
        if type:
            self.pow_type == type
        elif rates:
            self.pow_type = random.choice(['Shield'] * rates[0] + ['Miniblaster'] * rates[1] + ['SideGuns'] * rates[2]
                                          + ['Plasma'] * rates[3] + ['Life'] * rates[4] + ['Nuke'] * rates[5])
        self.image = icons[self.pow_type]
        self.rect = self.image.get_rect()
        self.rect.center = start_position
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class Effect(pygame.sprite.Sprite):
    """Class for animated events such as explosions, etc"""
    def __init__(self, start_position, animation, frame_rate=30, trailing=None):
        pygame.sprite.Sprite.__init__(self)
        self.image = animation[0]
        self.animation = animation
        self.rect = self.image.get_rect()
        self.rect.center = start_position
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = frame_rate  # sets the speed of animation
        self.trailing = trailing  #

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.animation):
                self.kill()
            else:
                # if object is given as trailing arg, animation will accompany this object
                if self.trailing and self.trailing.alive():
                    self.rect.center = self.trailing.rect.center
                self.image = self.animation[self.frame]
