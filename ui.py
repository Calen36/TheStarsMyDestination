import pygame
from sys import exit
from os import path
from settings import HEIGHT, WIDTH, FPS

img_dir = path.join(path.dirname(__file__), 'img')


def draw_text(surf, text, font, x, y, color):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.image_default = image
        self.image_hover = image.copy()
        self.image_hover.fill((60, 60, 60), special_flags=pygame.BLEND_RGB_ADD)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.path = HEIGHT - 70 - self.rect.centery
        self.halfway = y + self.path // 2
        self.speed = 1

    def move(self):
        self.rect.centery += self.speed
        if self.rect.centery < self.halfway:
            self.speed += 1
        else:
            self.speed = max(self.speed - 1, 1)


def show_start_screen(screen, clock, image_dict, progression, score, fonts):
    pygame.mouse.set_visible(True)
    startbutton = Button(WIDTH // 2, HEIGHT * 4 // 6, image_dict['NewGame'])
    quitbutton = Button(WIDTH // 2, HEIGHT * 8 // 10, image_dict['Quit'])
    ship_dummy = Button(WIDTH // 2, HEIGHT * 3 // 6, image_dict['Player'][0])
    background_rect = image_dict['Background'].get_rect()

    with open('highscores', 'r', encoding='utf-8') as file:
        try:
            highscores = list(map(int, file.read().split(',')))
        except ValueError:
            highscores = [6765, 4181, 2584, 1597, 987, 610, 377]
        highscores.append(score)
        highscores = sorted(highscores, reverse=True)[:7]
    if score > min(highscores):
        with open('highscores', 'w', encoding='utf-8') as file:
            file.write(','.join(map(str,highscores)))

    # SUBCYCLE FOR START MENU
    starting = False  # When true new game will start after animation
    waiting = True

    while waiting:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()

        if not starting:
            # HIGHLIGHTING MENU ITEMS BY MOUSE HOVER
            if startbutton.rect.collidepoint(mouse_pos):
                startbutton.image = startbutton.image_hover
            elif quitbutton.rect.collidepoint(mouse_pos):
                quitbutton.image = quitbutton.image_hover
            else:
                startbutton.image = startbutton.image_default
                quitbutton.image = quitbutton.image_default

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if startbutton.rect.collidepoint(mouse_pos):
                        starting = True
                        startbutton.kill()
                        quitbutton.kill()
                    elif quitbutton.rect.collidepoint(mouse_pos):
                        waiting = False
                        exit()

        # AFTER CLICKING ON START GAME ITEMS
        else:
            ship_dummy.move()
            if ship_dummy.rect.centery >= HEIGHT - 70:
                waiting = False

        # RENDERING START MENU
        screen.blit(image_dict['Background'], background_rect)
        screen.blit(startbutton.image, startbutton.rect)
        screen.blit(quitbutton.image, quitbutton.rect)
        screen.blit(ship_dummy.image, ship_dummy.rect)
        if progression['Win']:
            draw_text(screen, 'You have won!', fonts['bigger'], WIDTH // 2, HEIGHT // 14 - 10, (124, 252, 0))
        else:
            draw_text(screen, 'Highscores:', fonts['base'], WIDTH // 2, HEIGHT // 14, (29, 106, 255))
        for i, highscore in enumerate(highscores):
            if score == highscore:
                draw_text(screen, f'Your score >  {highscore}  < your score', fonts['base'], WIDTH // 2, HEIGHT // 8 + i * 25,
                          (89, 166, 255))
            else:
                draw_text(screen, str(highscore), fonts['base'], WIDTH // 2, HEIGHT // 8 + i * 25, (29, 106, 255))

        pygame.display.flip()


def draw_shield_bar(surf, x, y, shield, maxshield):
    if shield < 0:
        shield = 0
    bar_length = maxshield
    bar_height = 10
    fill = (shield / maxshield) * bar_length
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(surf, (10, 10, 255), fill_rect)
    pygame.draw.rect(surf, (173, 216, 255), outline_rect, 2)


def draw_weapon_bar(surf, x, y, weapon, uptime, length, now):
    colors = {
        'Blaster': (0, 0, 0),
        'Miniblaster': (255, 105, 180),
        'SideGuns': (50, 205, 50),
        'Plasma': (255, 100, 0)
    }
    bar_length = length//100
    bar_height = 10
    fill = 100 - (now - uptime) // 100 if weapon != 'Blaster' else 0
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(surf, colors[weapon], fill_rect)
    pygame.draw.rect(surf, (90, 100, 120), outline_rect, 2)


def draw_lives_and_nukes(surf, x, y, player, image_dict):
    for i in range(player.lives):
        life_rect = image_dict['Player-icon'].get_rect()
        # life_rect.right = x - 29 * i
        life_rect.right = x - (life_rect.width + 3) * i
        life_rect.y = y
        surf.blit(image_dict['Player-icon'], life_rect)
    for i in range(player.nukes):
        nuke_rect = image_dict['Nuke-icon'].get_rect()
        nuke_rect.right = right = x - (nuke_rect.width + 3) * i
        nuke_rect.y = y+40
        surf.blit(image_dict['Nuke-icon'], nuke_rect)
