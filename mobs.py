import pygame
from itertools import product
from random import randrange, randint, choice, random
from settings import HEIGHT, WIDTH
from weapons import Targeted, Projectile, Effect, Powerup


class Mob(pygame.sprite.Sprite):
    """base class for moving objects"""
    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        if self.rect.width < WIDTH:
            self.rect.x = randrange(WIDTH - self.rect.width)
        self.rect.bottom = -1
        self.shield = 6
        self.score = 1

        self.speedy = 1
        self.speedx = 0

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

    def take_damage(self, hit, effects, animation, sounds, globalscore, powerups, powerup_icons, hit_position, now=None):
        self.shield -= hit
        if self.shield <= 0:
            effects.add(Effect(self.rect.center, choice(animation['explosion'])))
            if random() < self.bonus[0]:
                powerups.add(Powerup(self.rect.center, powerup_icons, rates=self.bonus[1]))
            self.kill()
            choice(sounds['Explosions']).play()
            return self.score
        else:
            effects.add(Effect(start_position=hit_position, animation=animation['adsorb']))
            return 1

class Asteroid(Mob):
    """Asteroid - do nothing, and can hit the player"""
    def __init__(self, image_dict, bonus_rates):
        super().__init__(choice(image_dict["Asteroid"]))
        self.original_image = self.image.copy()  # preserve original image to do the transformations
        self.speedy = randrange(1, 8)
        self.speedx = randrange(-3, 3)
        self.rotation_angle = 0
        self.last_update = pygame.time.get_ticks()
        self.rot_speed = randrange(-8, 8)
        self.bonus = bonus_rates['Asteroid']

        # CALCULATE DAMAGE DEALT TO PLAYER DURING COLLISION AND SCORE DEPENDING OF SIZE
        speed = int((self.speedy**2 + self.speedx**2)**0.5)
        if self.rect.width <= 40:  # small size asteroid
            self.score = speed*3
            self.collision_damage = speed
        elif 40 < self.rect.width < 70:  # medium size
            self.score = self.collision_damage = speed * 2
        else:  # large size
            self.score = speed
            self.collision_damage = speed * 3

    def update(self):
        super(Asteroid, self).update()
        self.rotate()

    def rotate(self):
        now = pygame.time.get_ticks()

        if now - self.last_update > 50:  # sets how often rotation performed
            self.last_update = now
            self.rotation_angle = (self.rotation_angle + self.rot_speed) % 360
            self.image = pygame.transform.rotate(self.original_image, self.rotation_angle)

            old_center = self.rect.center  # smoothens the rotation
            self.rect = self.image.get_rect()
            self.rect.center = old_center

class Nebula(Mob):
    def __init__(self, speed, image_dict):
        super().__init__(choice(image_dict["Nebula"]))
        self.images = image_dict["Nebula"]
        self.rect.centerx = randint(0, WIDTH)
        self.speedy = speed

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10:
            self.image = choice(self.images)
            self.rect = self.image.get_rect()
            self.rect.centerx = randint(0, WIDTH)
            self.rect.bottom = randint(-100, -1)

class Celestial(Mob):
    def __init__(self, image, delay):
        super().__init__(image)
        self.rect.centerx = WIDTH//2 + randrange(-100, 100)
        self.step = 0
        self.delay = delay

    def update(self):
        self.step += 1
        if self.step % self.delay == 0:
            self.rect.centery += 1
        if self.rect.top > HEIGHT:
            self.kill()


class Flea(Mob):
    def __init__(self, bullet_group, image_dict, sound_dict, bonus_rates):
        super().__init__(image_dict["Flea"])
        self.bullet_image = image_dict['SmallOrb']
        self.sound = sound_dict['Orb']
        self.sound.set_volume(0.5)
        self.bullet_group = bullet_group
        self.shield = 16
        self.collision_damage = 16
        self.score = 35
        self.bonus = bonus_rates['Flea']
        self.speedy = randint(1, 3)
        self.shoot_delay = randint(1000, 5000)
        self.last_shot = 0

        # Makes ship do zigzags but not to go out of the screen
        limit = min(self.rect.left, WIDTH-self.rect.right)
        x = randint(limit//4, limit) if limit // 4 > 20 else 0
        self.ofset = [1] * x + [-1] * 2 * x + [1] * x + [0]
        self.step = (self.ofset[x % len(self.ofset)] for x in range(HEIGHT*2))

    def update(self, now, dummy):
        self.rect.centerx += next(self.step)
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            self.bullet_group.add(Projectile(self.rect.center, self.bullet_image, 6, 5))
            self.sound.play()


class Cricket(Mob):
    def __init__(self, bullet_group, image_dict, sound_dict, bonus_rates):
        super().__init__(image_dict['Cricket'])
        self.bullet_image = image_dict['Orb']
        self.sound = sound_dict['Orb']
        self.bullet_group = bullet_group
        self.shield = 20
        self.collision_damage = 20
        self.score = 50
        self.bonus = bonus_rates['Cricket']
        self.speedy = randint(1, 3)
        self.shoot_delay = randint(1000, 5000)
        self.last_shot = 0

        # Makes ship do zigzags but not to go out of the screen
        limit = min(self.rect.left, WIDTH-self.rect.right)
        x = randint(limit//2, limit) if limit // 2 > 20 else 0
        self.ofset = [1] * x + [-1] * 2 * x + [1] * x + [0]
        self.step = (self.ofset[x % len(self.ofset)] for x in range(HEIGHT*2))

    def update(self, now, player_position):
        self.rect.centerx += next(self.step)
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            self.bullet_group.add(Targeted(self.rect.center, self.bullet_image, 4, 7, player_position))
            self.sound.play()


class Madball(Mob):
    def __init__(self, bullet_group, image_dict, sound_dict, bonus_rates):
        super().__init__(image_dict['Madball'][0])
        self.image_jet = image_dict['Madball'][1]
        self.bullet_image = image_dict['MicroOrb']
        self.sounds = sound_dict
        self.bullet_group = bullet_group
        self.shield = 20
        self.collision_damage = 20
        self.score = 50
        self.speedy = randint(1, 2)
        self.bonus = bonus_rates['Madball']
        self.shoot_delay = 100
        self.last_shot = 0
        self.stoptime = randint(1000, 4000)  # Time before stopping prior to attack
        self.stopped = False
        self.charged = False
        self.delay = randint(500, 2000)  # Time of stop
        self.starttime = pygame.time.get_ticks()
        self.offset = random()

    def update(self, now, player_position):
        self.rect.y += self.speedy

        if self.rect.top > HEIGHT:
            self.kill()

        if now > self.starttime + self.stoptime and not self.stopped:
            self.speedy = 0
            self.stopped = True
            self.speedy = 1
        if now > self.starttime + self.stoptime + self.delay:
            if not self.charged:
                self.image = self.image_jet
                self.rect.centery -= 26
                if self.rect.centerx > player_position[0]:
                    self.offset = -self.offset
                self.charged = True
            self.speedy += 0.1
            self.rect.centerx += self.speedy * self.offset

            if now - self.last_shot > self.shoot_delay:
                self.last_shot = now
                self.bullet_group.add(Projectile((self.rect.right - 10, self.rect.bottom+30), self.bullet_image, 20, 1))
                self.bullet_group.add(Projectile((self.rect.left + 10, self.rect.bottom+30), self.bullet_image, 20, 1))
                self.sounds['MicroOrb'].play()


class Grasshopper(Mob):
    def __init__(self, bullet_group, image_dict, sound_dict, bonus_rates):
        super().__init__(image_dict["Grasshopper"])
        self.bullet_image = image_dict['SmallOrb']
        self.sound = sound_dict['Orb']
        self.sound.set_volume(0.5)
        self.bullet_group = bullet_group
        self.shield = 40
        self.collision_damage = 40
        self.score = 75
        self.bonus = bonus_rates['Grasshopper']
        self.speedy = randint(1, 3)

        self.shoot_delay = randint(1000, 5000)
        self.last_shot = 1000
        self.burst_on = False
        self.burst_len = 3
        self.burst_delay = 100

        # Makes ship do zigzags but not to go out of the screen
        limit = min(self.rect.left, WIDTH-self.rect.right)
        x = randint(limit//4, limit) if limit // 4 > 20 else 0
        self.ofset = [1] * x + [-1] * 2 * x + [1] * x + [0]
        self.step = (self.ofset[x % len(self.ofset)] for x in range(HEIGHT*2))

    def update(self, now, player_position):
        self.rect.centerx += next(self.step)
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()
        if not self.burst_on:
            if now - self.last_shot > self.shoot_delay:
                self.last_shot = now
                bullet = Targeted(self.rect.center, self.bullet_image, 6, 5, player_position)
                self.bullet_group.add(bullet)
                self.sound.play()
                self.burst_on = True
        else:
            if now - self.last_shot > self.burst_delay:
                self.last_shot = now
                self.bullet_group.add(Targeted(self.rect.center, self.bullet_image, 6, 5, player_position))
                self.sound.play()
                self.burst_len -= 1
                if self.burst_len == 1:
                    self.burst_len = 3
                    self.burst_on = False


class Mantis(Mob):
    def __init__(self, bullet_group, image_dict, sound_dict, bonus_rates):
        super().__init__(image_dict["Mantis"])
        self.bullet_image = image_dict['Yellow']
        self.sound = sound_dict['Orb']
        self.sound.set_volume(0.5)
        self.bullet_group = bullet_group
        self.shield = 41
        self.collision_damage = 40
        self.score = 95
        self.bonus = bonus_rates['Flea']
        self.speedy = randint(1, 3)
        self.speedx = randint(-3, 4)
        self.shoot_delay = randint(1000, 5000)
        self.last_shot = 0

        self.shoot_delay = randint(1000, 5000)
        self.last_shot = 1000
        self.burst_on = False
        self.burst_delay = 500

    def update(self, now, player_position):
        self.rect.x += self.speedx
        if self.rect.right > WIDTH-10:
            self.rect.right = WIDTH-10
            self.speedx = -self.speedx
        elif self.rect.left < 10:
            self.rect.left = 10
            self.speedx = -self.speedx

        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()
        if not self.burst_on:
            if now - self.last_shot > self.shoot_delay:
                self.last_shot = now
                self.bullet_group.add(Projectile((self.rect.centerx + 15, self.rect.bottom+5), self.bullet_image, 7, 3))
                self.bullet_group.add(Projectile((self.rect.centerx - 15, self.rect.bottom+5), self.bullet_image, 7, 3))
                self.sound.play()
                self.burst_on = True
        else:
            if now - self.last_shot > self.burst_delay:
                self.sound.play()
                self.bullet_group.add(
                    Projectile((self.rect.centerx + 35, self.rect.centery+25), self.bullet_image, 7, 3))
                self.bullet_group.add(
                    Projectile((self.rect.centerx - 35, self.rect.centery+25), self.bullet_image, 7, 3))
                self.bullet_group.add(
                    Projectile((self.rect.centerx + 18, self.rect.centery+35), self.bullet_image, 7, 3))
                self.bullet_group.add(
                    Projectile((self.rect.centerx - 18, self.rect.centery+35), self.bullet_image, 7, 3))
                self.burst_on = False


class Beetle(Mob):
    def __init__(self, bullet_group, image_dict, sound_dict, bonus_rates):
        super().__init__(image_dict["Beetle"])
        self.images = image_dict
        self.sound = sound_dict['Orb'] # TODO звук доделать
        self.sound.set_volume(0.5)
        self.bullet_group = bullet_group
        self.shield = 110
        self.collision_damage = 60
        self.score = 100
        self.bonus = bonus_rates['Beetle']
        self.speedy = 1
        self.shoot_delay = randint(1000, 5000)
        self.last_shot = 0
        self.gun_switch = True

    def update(self, now, player_position):
        if now % 2 == 0:
            self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

        if now - self.last_shot > self.shoot_delay:
            if self.gun_switch:
                self.last_shot = now
                self.bullet_group.add(Projectile(self.rect.center, self.images['YellowBig'], 3, 10))
                self.sound.play()
                self.gun_switch = not self.gun_switch
            else:
                self.last_shot = now
                self.bullet_group.add(Targeted(self.rect.center, self.images['Orb'], 4, 7, player_position))
                self.sound.play()
                self.gun_switch = not self.gun_switch


class Boss(Mob):
    def __init__(self, bullet_group, image_dict, sound_dict, progression, bonus_rates):
        super().__init__(image_dict["Boss"])
        self.rect.centerx = WIDTH//2
        self.images = image_dict
        self.sound = sound_dict['Orb'] # TODO звук доделать + звук появления
        self.sound.set_volume(0.5)
        self.bullet_group = bullet_group
        self.shield = 2500
        self.collision_damage = 150
        self.score = 1000
        self.bonus = bonus_rates['Boss']
        self.speedy = 1
        self.speedx = 0
        self.shoot_delay = 200
        self.last_shot = 0
        self.gun_switch = 0
        self.start_run = True
        self.progression = progression
        self.stage = 0

    def take_damage(self, hit, effects, animation, sounds, score, powerups, powerup_icons, hit_position, now):
        self.shield -= hit
        if self.shield <= 0:
            effects.add(Effect(start_position=self.rect.center,
                               animation=[pygame.transform.scale2x(x) for
                                          x in choice(animation['explosion'])], frame_rate=80))
            effects.add(Effect((self.rect.centerx, self.rect.top), choice(animation['explosion'])))
            effects.add(Effect((self.rect.centerx, self.rect.bottom), choice(animation['explosion'])))
            effects.add(Effect((self.rect.left, self.rect.centery), choice(animation['explosion'])))
            effects.add(Effect((self.rect.right, self.rect.centery), choice(animation['explosion'])))
            score += self.score
            if random() < self.bonus[0]:
                powerups.add(Powerup(self.rect.center, powerup_icons, rates=self.bonus[1]))
            self.progression['Boss killed'] = True
            self.progression['Boss killed time'] = now
            self.kill()
            choice(sounds['Explosions']).play()
            return self.score
        else:
            effects.add(Effect(start_position=hit_position, animation=animation['adsorb']))
            return 1

    def update(self, now, player_position):
        if self.stage == 0 and self.shield < 800:
            self.stage += 2

        self.rect.y += self.speedy
        self.rect.x += self.speedx

        if self.rect.bottom >= HEIGHT//2:
            self.speedx = randint(-2-self.stage, 3+self.stage)
            self.speedy = -randint(1, 3+self.stage)
            self.start_run = False
        if self.rect.right >= WIDTH - 10:
            self.speedx = -randint(1, 3+self.stage)
            self.speedy = randint(-2-self.stage, 3+self.stage)
        elif self.rect.left <= 10:
            self.speedx = randint(1, 3+self.stage)
            self.speedy = randint(-2-self.stage, 3+self.stage)
        elif not self.start_run and self.rect.top <= 10:
            self.speedx = randint(1, 3+self.stage)
            self.speedy = randint(-2-self.stage, 3+self.stage)

        if now - self.last_shot > self.shoot_delay:
            if self.gun_switch in (20, 21, 22):
                self.last_shot = now
                self.bullet_group.add(Targeted(self.rect.center, self.images['Orb'], 4+self.stage, 7+self.stage, player_position))
                self.sound.play()
            elif self.gun_switch == 40:
                self.last_shot = now
                self.bullet_group.add(Projectile((self.rect.left+15, self.rect.centery+35), self.images['YellowBig'], 3+self.stage, 10+self.stage))
                self.bullet_group.add(Projectile((self.rect.right-13, self.rect.centery+35), self.images['YellowBig'], 3+self.stage, 10+self.stage))
                self.sound.play()
            elif self.gun_switch in (60, 61, 62):
                self.last_shot = now
                self.bullet_group.add(Targeted(self.rect.center, self.images['Orb'], 4+self.stage, 7+self.stage, player_position))
                self.sound.play()
            elif self.gun_switch == 80:
                self.last_shot = now
                self.bullet_group.add(Projectile((self.rect.left+45, self.rect.centery+90), self.images['Yellow'], 4+self.stage, 7+self.stage))
                self.bullet_group.add(Projectile((self.rect.right-43, self.rect.centery+90), self.images['Yellow'], 4+self.stage, 7+self.stage))
                self.sound.play()
                self.gun_switch = 0
            self.gun_switch += 1


class FinalBoss(Mob):
    def __init__(self, bullet_group, image_dict, sound_dict, fighters_group, progression, bonus_rates):
        super().__init__(image_dict["Final"][0])
        self.rect.centerx = WIDTH//2
        self.images = image_dict
        self.sounds = sound_dict
        self.sound = sound_dict['Orb']
        self.sound.set_volume(0.5)
        self.bullet_group = bullet_group
        self.shield = 5000
        self.score = 5000
        self.bonus_rates = bonus_rates  # bonus rates to forward to spawned drones
        self.speedy = 1
        self.speedx = 0
        self.shoot_delay = 80
        self.last_shot = 0
        self.gun_switch = 0
        self.start_run = True
        self.fighters = fighters_group  # group to add spawned drones
        self.progression = progression
        self.sounds['BossAlert'].play()
        self.stage = 0

    def take_damage(self, hit, effects, animation, sounds, score, powerups, powerup_icons, hit_position, now):
        self.shield -= hit
        if self.shield <= 0:  # When FinalBoss is destroyed cascade of explosions is created
            effects.add(Effect(start_position=self.rect.center,
                               animation=[pygame.transform.scale2x(x) for
                                          x in choice(animation['explosion'])], frame_rate=80))
            effects.add(Effect((self.rect.centerx, self.rect.top), choice(animation['explosion'])))
            effects.add(Effect((self.rect.centerx, self.rect.bottom), choice(animation['explosion'])))
            effects.add(Effect((self.rect.left, self.rect.centery), choice(animation['explosion'])))
            effects.add(Effect((self.rect.right, self.rect.centery), choice(animation['explosion'])))
            score += self.score
            self.progression['Final killed'] = True
            self.progression['Final killed time'] = now
            self.kill()
            choice(sounds['Explosions']).play()
            return self.score
        else:
            effects.add(Effect(start_position=hit_position, animation=animation['adsorb']))
            return 1

    def update(self, now, player_position):
        """As FinalBoss takes damage it becomes quicker and more deadly"""
        if self.stage == 0 and self.shield < 3000:
            self.stage += 1
        elif self.stage == 1 and self.shield < 2000:
            self.stage += 1
        elif self.stage == 2 and self.shield < 1000:
            self.stage += 1

        self.rect.y += self.speedy
        self.rect.x += self.speedx

        """Randomly moves Final boss in the upper half of the game screen"""
        if self.rect.bottom >= HEIGHT//2:
            self.speedx = randint(-2-self.stage, 3+self.stage)
            self.speedy = -randint(1, 3+self.stage)
            self.start_run = False
        if self.rect.right >= WIDTH - 10:
            self.speedx = -randint(1, 3+self.stage)
            self.speedy = randint(-2-self.stage, 3+self.stage)
        elif self.rect.left <= 10:
            self.speedx = randint(1, 3+self.stage)
            self.speedy = randint(-2-self.stage, 3+self.stage)
        elif not self.start_run and self.rect.top <= 10:
            self.speedx = randint(1, 3+self.stage)
            self.speedy = randint(-2-self.stage, 3+self.stage)

        if now - self.last_shot > self.shoot_delay:
            self.gun_switch += 1
            self.last_shot = now
            if self.gun_switch in (10, 90):  # Fires a volley of yellow beams
                self.bullet_group.add(Projectile((self.rect.left+8, self.rect.centery+5), self.images['Final'][2], 4+self.stage, 15+self.stage))
                self.bullet_group.add(Projectile((self.rect.right-6, self.rect.centery+5), self.images['Final'][2], 4+self.stage, 15+self.stage))
                self.bullet_group.add(Projectile((self.rect.left+32, self.rect.centery+12), self.images['Final'][2], 4+self.stage, 15+self.stage))
                self.bullet_group.add(Projectile((self.rect.right-32, self.rect.centery+12), self.images['Final'][2], 4+self.stage, 15+self.stage))
                self.bullet_group.add(Projectile((self.rect.left+52, self.rect.centery+75), self.images['Final'][2], 4+self.stage, 15+self.stage))
                self.bullet_group.add(Projectile((self.rect.right-52, self.rect.centery+75), self.images['Final'][2], 4+self.stage, 15+self.stage))
                self.sound.play()
            elif self.gun_switch in (40, 50, 60):  # Fires series of red orbs: micro, then small, then normal
                orbtype = {40: ('MicroOrb', 5+self.stage), 50: ('SmallOrb', 7+self.stage), 60: ('Orb', 10+self.stage)}  # {switch_timing:(Orb_name, Damage)}
                for target in [x for x in product([self.rect.centerx + d for d in (-50, 0, 50)], [self.rect.centery + d for d in (-50, 0, 50)]) if x != self.rect.center]:
                    self.bullet_group.add(Targeted(self.rect.center, self.images[orbtype[self.gun_switch][0]], 5+self.stage, orbtype[self.gun_switch][1], target))
                self.sound.play()
            elif self.gun_switch == 120:  # Spawns a fighter drone
                self.gun_switch = 0
                self.fighters.add(CricketDrone(self, self.bullet_group, self.images, self.sounds, self.bonus_rates, self.stage))


class CricketDrone(Mob):
    """Drone fighter spawned by Final Boss"""
    def __init__(self, master, bullet_group, image_dict, sound_dict, bonus_rates, stage):
        super().__init__(image_dict['Cricket'])
        self.rect.centerx = master.rect.centerx
        self.rect.top = master.rect.top + 50
        self.master = master
        self.bullet_image = image_dict['Orb']
        self.sound = sound_dict['Orb']
        self.bullet_group = bullet_group
        self.shield = 80
        self.collision_damage = 20
        self.score = 80
        self.bonus = bonus_rates['CricketDrone']
        self.speedy = randint(1, 3)
        self.shoot_delay = randint(1000, 5000)
        self.last_shot = 0
        self.start_run = True  # Flag that indicates disegagement from FinalBoss
        self.disengage = 0
        self.stage = stage  # Fighter drones became more fast and deadly as FinalBoss gets damage

    def update(self, now, player_position):
        if self.start_run:  # In the beginning fighter moves in syncronization with FinalBoss, slowly disengaging from its back
            self.disengage +=1
            self.rect.centery = self.master.rect.centery - self.disengage
            self.rect.centerx = self.master.rect.centerx
            if self.disengage == 130:
                self.start_run = False
                self.speedx = randint(-2, 3)
                self.speedy = randint(-2, 3)
        else:  # As start_run ends, fighter starts randomly move in the upper half of the game screen
            self.rect.centerx += self.speedx
            self.rect.centery += self.speedy

            if self.rect.bottom >= HEIGHT//2:
                self.speedx = randint(-2-self.stage, 3+self.stage)
                self.speedy = -randint(1, 3+self.stage)
            if self.rect.right >= WIDTH - 10:
                self.speedx = -randint(1, 3+self.stage)
                self.speedy = randint(-2-self.stage, 3+self.stage)
            elif self.rect.left <= 10:
                self.speedx = randint(1, 3+self.stage)
                self.speedy = randint(-2-self.stage, 3+self.stage)
            elif not self.start_run and self.rect.top <= 10:
                self.speedx = randint(1, 3+self.stage)
                self.speedy = randint(-2+self.stage, 3+self.stage)

            if now - self.last_shot > self.shoot_delay:  # Firing
                self.last_shot = now
                self.bullet_group.add(Targeted(self.rect.center, self.bullet_image, 6+self.stage, 8+self.stage, player_position))
                self.sound.play()