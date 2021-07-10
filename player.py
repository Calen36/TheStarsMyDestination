import pygame
from settings import HEIGHT, WIDTH
from weapons import Projectile, Targeted
import random


class Dummy(pygame.sprite.Sprite):
    def __init__(self, image_dict, center):
        pygame.sprite.Sprite.__init__(self)
        self.image = image_dict['Thrusting dummy']
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.rect.centery += 42
        self.speed = 1

    def update(self, position):
        if self.rect.bottom < 0:
            self.kill()
        self.rect.centery -= self.speed
        self.speed += 0.05


class Player(pygame.sprite.Sprite):
    def __init__(self, bullet_group, image_dict, sounds_dict, progression):
        pygame.sprite.Sprite.__init__(self)
        self.images = image_dict
        self.image = image_dict['Player'][0]
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10

        self.last_shot = 0
        self.shoot_delay = 400  # sets frequency of shots
        self.maxshield = 150
        self.shield = 150
        self.lives = 3
        self.maxlives = 3
        self.nukes = 0
        self.maxnukes = 3
        self.pow_uptime = 0
        self.powerup_length = 10000
        self.gun_switcher = True
        self.weapon_type = 'Blaster'

        self.sounds = sounds_dict
        self.miniblaster_sound = sounds_dict['Miniblaster']
        self.progression = progression

        self.bullet_group = bullet_group

    def update(self, position):
        self.rect.center = position
        if self.alive() and not self.progression['Win']:
            self.shoot()

        """Doesn't allow player's ship to go out of game scren"""
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

        if self.weapon_type != 'Blaster' and pygame.time.get_ticks() - self.pow_uptime > self.powerup_length:
            self.weapon_type = 'Blaster'
            center = self.rect.center
            self.image = self.images['Player'][0]
            self.rect = self.image.get_rect()
            self.rect.center = center
            self.shoot_delay = 400
            self.sounds['Degrade'].play()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now

            if self.weapon_type == 'Blaster':
                self.bullet_group.add(Projectile((self.rect.centerx, self.rect.top), self.images['Blaster'], -10, 8))
                self.sounds['Blaster'].play()
            elif self.weapon_type == 'Miniblaster':
                self.gun_switcher = not self.gun_switcher
                self.bullet_group.add(Projectile((self.rect.centerx + (23 if self.gun_switcher else -23),
                                                  self.rect.top), self.images['Miniblaster'], -15, 6))
                self.sounds['Miniblaster'].play()
            elif self.weapon_type == 'SideGuns':
                self.bullet_group.add(Projectile((self.rect.right-7, self.rect.top+10),
                                                 self.images['SideGuns'], -8, 20))
                self.bullet_group.add(Projectile((self.rect.left+7, self.rect.top+10),
                                                 self.images['SideGuns'], -8, 20))
                self.sounds['SideGuns'].play()
            elif self.weapon_type == 'Plasma':
                self.bullet_group.add(Targeted(
                    (self.rect.centerx+random.choice((-33,33,-53,53)),
                     self.rect.centery-25), self.images['Plasma'], 7, 2,
                    (self.rect.centerx+random.randrange(-150, 151), self.rect.top-500),
                    degradable=True))
                if now % 4 == 0:
                    self.sounds['Plasma'].play()

    def nuke(self):
        if self.nukes > 0:
            self.nukes -= 1

    def powerup(self, pow_type):
        if pow_type == 'Shield':
            if self.shield < self.maxshield:
                self.shield = min(self.maxshield, self.shield + random.randrange(10, 21))
                self.sounds['PickUpShield'].play()
        elif pow_type == 'Life':
            self.lives = min(self.lives + 1, self.maxlives)
        elif pow_type == 'Nuke':
            self.nukes = min(self.nukes + 1, self.maxnukes)
        else:
            self.weapon_type = pow_type
            self.pow_uptime = pygame.time.get_ticks()
            self.sounds['Upgrade'].play()
            if pow_type == 'Miniblaster':
                center = self.rect.center
                self.image = self.images['Player'][1]
                self.rect = self.image.get_rect()
                self.rect.center = center
                self.shoot_delay = 100
            elif pow_type == 'SideGuns':
                center = self.rect.center
                self.image = self.images['Player'][2]
                self.rect = self.image.get_rect()
                self.rect.center = center
                self.shoot_delay = 300
            elif pow_type == 'Plasma':
                center = self.rect.center
                self.image = self.images['Player'][3]
                self.rect = self.image.get_rect()
                self.rect.center = center
                self.shoot_delay = 3
