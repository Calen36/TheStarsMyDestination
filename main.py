""" Main game art by Tatermand
Effects animation by Scorpio
Also used art by: Cethiel, phaelax, Rawdanitsu
SFX by: Vinrax
https://opengameart.org/

music: "Space battle 2" by Alexander Brandon
font - Ethnocentric, © 1999 Ray Larabie
"""

import pygame
from random import randint, choice, randrange
from os import path

from settings import HEIGHT, WIDTH, FPS, spawn_rates_default, asteroid_spawn_time, asteroid_spawn_min, asteroid_spawn_max,\
    enemy_spawn_time, enemy_spawn_min, enemy_spawn_max, nuke_cooldown_time, nuke_damage, progression_default, bonus_rates_defaults
from player import Player, Dummy
from weapons import Effect, Powerup
from mobs import Asteroid, Nebula, Celestial, Cricket, Flea, Madball, Grasshopper, Mantis, Beetle, Boss, FinalBoss, CricketDrone
from ui import draw_text, draw_shield_bar, draw_weapon_bar, draw_lives_and_nukes, show_start_screen


def is_player_alive():
    if player.shield <= 0:
        effects.add(Effect(start_position=player.rect.center,
                           animation=[pygame.transform.scale2x(x) for
                                      x in choice(animation['explosion'])], frame_rate=45))
        pygame.mouse.set_pos(WIDTH / 2, HEIGHT - 70)
        player.lives -= 1
        if player.lives < 1:
            player.kill()
            bullets.remove()
        if player.alive():
            player.shield = 100
            sounds['Respawn'].play()
            effects.add(Effect(start_position=player.rect.center,
                               animation=animation['respawn'], frame_rate=60, trailing=player))


# SET DIR NAMES FOR GAME ASSETS
img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')

if __name__ == '__main__':

    # CREATE GAME AND GAME WINDOW
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("The Stars My Destination")
    clock = pygame.time.Clock()

    # LOAD GAME ASSETS
    images = {
        'Background': pygame.image.load(path.join(img_dir, "background.png")).convert(),
        'NewGame': pygame.image.load(path.join(img_dir, "button-new_game.png")).convert_alpha(),
        'Quit': pygame.image.load(path.join(img_dir, "button-quit.png")).convert_alpha(),
        'Player': [pygame.image.load(path.join(img_dir, "player_ship.png")).convert_alpha(),
                   pygame.image.load(path.join(img_dir, "player_ship_miniblaster.png")).convert_alpha(),
                   pygame.image.load(path.join(img_dir, "player_ship_sideguns.png")).convert_alpha(),
                   pygame.image.load(path.join(img_dir, "player_ship_plasma.png")).convert_alpha()],
        'Thrusting dummy': pygame.image.load(path.join(img_dir, "player_ship_thrust.png")).convert_alpha(),
        'Asteroid': [pygame.image.load(path.join(img_dir, img)).convert_alpha() for img in
                     ("asteroid-med1.png", "asteroid-med2.png", "asteroid-med3.png", "asteroid-sm1.png",
                      "asteroid-sm2.png", "asteroid-sm3.png", "asteroid-big1.png", "asteroid-big3.png",
                      "asteroid-big3.png")],
        'Nebula': [pygame.image.load(path.join(img_dir, img)).convert_alpha() for img in
                   ("bg_obj_1.png", "bg_obj_2.png", "bg_obj_3.png", "bg_obj_4.png", "bg_obj_5.png",)],
        'Cricket': pygame.image.load(path.join(img_dir, "enemy-ship-cricket.png")).convert_alpha(),
        'Flea': pygame.image.load(path.join(img_dir, "enemy-ship-flea.png")).convert_alpha(),
        'Madball': [pygame.image.load(path.join(img_dir, "enemy-ship-madball.png")).convert_alpha(),
                    pygame.image.load(path.join(img_dir, "enemy-ship-madball-jet.png")).convert_alpha()],
        'Grasshopper': pygame.image.load(path.join(img_dir, "enemy-ship-grasshopper.png")).convert_alpha(),
        'Mantis': pygame.image.load(path.join(img_dir, "enemy-ship-mantis.png")).convert_alpha(),
        'Boss': pygame.image.load(path.join(img_dir, "enemy-ship-boss.png")).convert_alpha(),
        'Beetle': pygame.image.load(path.join(img_dir, "enemy-ship-beetle.png")).convert_alpha(),
        'Final': [pygame.image.load(path.join(img_dir, "enemy-ship-final.png")).convert_alpha(),
                  pygame.image.load(path.join(img_dir, "enemy-ship-final_jet.png")).convert_alpha(),
                  pygame.image.load(path.join(img_dir, "enemy-bullet-final.png")).convert_alpha(),],
        'Blaster': pygame.image.load(path.join(img_dir, "bullet-blaster.png")).convert_alpha(),
        'Miniblaster': pygame.image.load(path.join(img_dir, "bullet-miniblaster.png")).convert_alpha(),
        'SideGuns': pygame.image.load(path.join(img_dir, "bullet-sideguns.png")).convert_alpha(),
        'Plasma': pygame.image.load(path.join(img_dir, "bullet-plasma.png")).convert_alpha(),
        'Orb': pygame.image.load(path.join(img_dir, "enemy-bullet-orb.png")).convert_alpha(),
        'SmallOrb': pygame.image.load(path.join(img_dir, "enemy-bullet-small_orb.png")).convert_alpha(),
        'MicroOrb': pygame.image.load(path.join(img_dir, "enemy-bullet-micro_orb.png")).convert_alpha(),
        'Yellow': pygame.image.load(path.join(img_dir, "enemy-bullet-yellow.png")).convert_alpha(),
        'YellowBig': pygame.image.load(path.join(img_dir, "enemy-bullet-yellow_big.png")).convert_alpha(),
        'Nuke': pygame.image.load(path.join(img_dir, "pow-nuke.png")).convert_alpha(),
        'Nuke-icon': pygame.image.load(path.join(img_dir, "pow-nuke_small.png")).convert_alpha(),
        'Player-icon': pygame.image.load(path.join(img_dir, "player_ship_small.png")).convert_alpha(),
        'Celestial': [pygame.image.load(path.join(img_dir, f"celestial-{x}.png")).convert_alpha() for x in range(1, 9)]
    }
    background_rect = images['Background'].get_rect()
    pygame.display.set_icon(images['Player-icon'])
    powerup_icons = {
        "Shield": pygame.image.load(path.join(img_dir, "pow-shield.png")).convert_alpha(),
        "Miniblaster": pygame.image.load(path.join(img_dir, "pow-miniblaster.png")).convert_alpha(),
        "SideGuns": pygame.image.load(path.join(img_dir, "pow-sideguns.png")).convert_alpha(),
        "Plasma": pygame.image.load(path.join(img_dir, "pow-plasma.png")).convert_alpha(),
        "Life": pygame.image.load(path.join(img_dir, "pow-life.png")).convert_alpha(),
        "Nuke": pygame.image.load(path.join(img_dir, "pow-nuke.png")).convert_alpha()
    }

    pygame.mixer.music.load(path.join(snd_dir, 'Alexander Brandon - Space Battle 2.ogg'))

    sounds = {'Blaster': pygame.mixer.Sound(path.join(snd_dir, 'shoot.wav')),
              'Miniblaster': pygame.mixer.Sound(path.join(snd_dir, 'shoot-miniblaster.wav')),
              'SideGuns': pygame.mixer.Sound(path.join(snd_dir, 'shoot-sideguns.wav')),
              'Plasma': pygame.mixer.Sound(path.join(snd_dir, 'shoot-plasma.wav')),
              'Upgrade': pygame.mixer.Sound(path.join(snd_dir, 'weapon-upgrade.wav')),
              'Degrade': pygame.mixer.Sound(path.join(snd_dir, 'weapon-degrade.wav')),
              'PickUpShield': pygame.mixer.Sound(path.join(snd_dir, "pow1.wav")),
              'Damage': pygame.mixer.Sound(path.join(snd_dir, 'damage.wav')),
              'Respawn': pygame.mixer.Sound(path.join(snd_dir, "respawn.wav")),
              'Orb': pygame.mixer.Sound(path.join(snd_dir, 'enemy-shoot-orb.wav')),
              'MicroOrb': pygame.mixer.Sound(path.join(snd_dir, 'enemy-shoot-micro_orb.wav')),
              'Explosions': [pygame.mixer.Sound(path.join(snd_dir, snd)) for snd in [f"boom{x}.wav" for x in range(9)]],
              'BossAlert': pygame.mixer.Sound(path.join(snd_dir, 'boss-alert.wav')),
              'Fanfare': pygame.mixer.Sound(path.join(snd_dir, 'fanfare.wav')),
              'Thrust': pygame.mixer.Sound(path.join(snd_dir, 'thrust.wav')),
              }
    sounds['Blaster'].set_volume(0.1)
    # sounds['Plasma'].set_volume(0.1)
    sounds['Miniblaster'].set_volume(0.5)
    sounds['SideGuns'].set_volume(0.5)
    sounds['Damage'].set_volume(0.2)
    sounds['MicroOrb'].set_volume(0.2)
    # for sound in sounds['Explosions']:
    #     sound.set_volume(0.5)

    animation = {'explosion': [[pygame.image.load(path.join(img_dir, f"expl{y}-{x}.png")).convert_alpha()
                            for x in range(1, 16)] for y in range(1, 5)],
                 'nuke': [pygame.transform.scale2x(pygame.image.load(path.join(img_dir, f"nuke-{x}.png")).convert_alpha()) for x in range(9)],
                 'shield': [pygame.image.load(path.join(img_dir, f"shield-{x}.png")).convert_alpha() for x in range(1, 16)],
                 'respawn': [pygame.image.load(path.join(img_dir, f"respawn-{x}.png")).convert_alpha() for x in range(13)],
                 'adsorb': [pygame.image.load(path.join(img_dir, f"adsorb-{x}.png")).convert_alpha() for x in range(9)],}

    fonts = {'base': pygame.font.Font(path.join(img_dir, 'font.ttf'), 18),
             'bigger': pygame.font.Font(path.join(img_dir, 'font.ttf'), 34)}

    # FLAGS
    game_over = True  # Turns on start menu
    running = True

    progression = progression_default.copy()
    local_time = 0
    last_asteroid_spawn = 0
    last_enemy_spawn = 0
    last_nuke = 0
    score = 0

    def go_to_next_level():
        global local_time, now, progression, asteroid_spawn_min, asteroid_spawn_max, enemy_spawn_min, enemy_spawn_max
        local_time = now
        delay = 3 if progression['Current level'] in (4, 7) else 2

        celestials.add(Celestial(images['Celestial'][progression['Current level']], delay))
        asteroid_spawn_min = int(asteroid_spawn_min * 0.9)
        asteroid_spawn_max = int(asteroid_spawn_max * 0.9)
        enemy_spawn_min = int(enemy_spawn_min * 0.9)
        enemy_spawn_max = int(enemy_spawn_max * 0.9)
        player.maxshield += 5
        player.powerup_length += 50

        progression['Current level'] += 1

    # *** GAME CYCLE ***
    while running:

        # *** START MENU SCREEN ***
        if game_over:
            pygame.mixer.music.play(loops=-1)
            show_start_screen(screen, clock, images, progression, score, fonts)

            # *** INITIALIZE NEW GAME***
            pygame.mouse.set_visible(False)
            game_over = False
            progression = progression_default.copy()
            bonus_rates = bonus_rates_defaults.copy()
            spawn_rates = spawn_rates_default.copy()
            local_time = 0
            last_asteroid_spawn = 0
            last_enemy_spawn = 0
            last_nuke = 0
            score = 0
            pause = False

            # CREATE GROUPS FOR SPRITES
            celestials = pygame.sprite.Group()
            general = pygame.sprite.Group()
            asteroids = pygame.sprite.Group()
            bullets = pygame.sprite.Group()
            enemy_bullets = pygame.sprite.Group()
            powerups = pygame.sprite.Group()
            nebulae = pygame.sprite.Group()
            fighters = pygame.sprite.Group()
            effects = pygame.sprite.Group()
            bosses = pygame.sprite.Group()

            # CREATE PLAYER AND MOBS
            player = Player(bullet_group=bullets, image_dict=images, sounds_dict=sounds, progression=progression)
            general.add(player)
            nebulae.add(Nebula(1, images))
            nebulae.add(Nebula(2, images))

            pygame.mouse.set_pos(WIDTH / 2, HEIGHT - 70)  # moves mouse to starting position
            score = 0

        # MAIN GAME
        clock.tick(FPS)

        # GET MOUSE, BUTTONS AND CLOCK STATUS
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed(num_buttons=3)
        now = pygame.time.get_ticks()
        if player.alive():
            if any(mouse_buttons) and last_nuke + nuke_cooldown_time < now and player.nukes > 0:
                last_nuke = now
                effects.add(Effect(start_position=player.rect.center, animation=animation['nuke']))
                player.nukes -= 1
                choice(sounds['Explosions']).play()
                for mob in asteroids:
                    mob.take_damage(nuke_damage, effects, animation, sounds, score, powerups, powerup_icons, mob.rect.center, now)
                for fighter in fighters:
                    fighter.take_damage(nuke_damage, effects, animation, sounds, score, powerups, powerup_icons, fighter.rect.center)

            player_was_alive = now
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:  # Pausing game
                pause = True
                pre_pause_position = mouse_pos
        while pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pause = False
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    pause = False
                    pygame.mouse.set_pos(pre_pause_position)

        """GAME PRORGRESS AND MOB SPAWNING"""

        if not progression['Win'] and last_asteroid_spawn + asteroid_spawn_time < now:
            asteroids.add(Asteroid(images, bonus_rates))
            last_asteroid_spawn = now
            asteroid_spawn_time = randrange(asteroid_spawn_min, asteroid_spawn_max)

        if progression['Current level'] not in (5, 8, 9) and now - last_enemy_spawn > enemy_spawn_time:
            fighters.add(eval(choice(spawn_rates))(enemy_bullets, images, sounds, bonus_rates))
            last_enemy_spawn = now
            enemy_spawn_time = randrange(enemy_spawn_min, enemy_spawn_max)


        if progression['Current level'] == 1 and now - local_time > 30000:
            print('LEVEL 2')
            go_to_next_level()
            asteroid_spawn_min = 600
            asteroid_spawn_max = 1400
            enemy_spawn_min = 800
            enemy_spawn_max = 2000
            spawn_rates = ['Flea'] * 1 + ['Cricket'] * 2

        elif progression['Current level'] == 2 and now - local_time > 90000:
            print('LEVEL 3')
            go_to_next_level()
            asteroid_spawn_min = 500
            asteroid_spawn_max = 1200
            enemy_spawn_min = 700
            enemy_spawn_max = 1500
            spawn_rates = ['Flea'] * 1 + ['Cricket'] * 2 + ['Madball'] * 4
            bonus_rates['Asteroid'] = (0.1, (5, 4, 5, 0, 0, 6))
            bonus_rates['Cricket'] = (0.3, (4, 5, 4, 0, 1, 4))
            bonus_rates['Flea'] = (0.4, (4, 5, 4, 0, 1, 4))

        elif progression['Current level'] == 3 and now - local_time > 120000:  # LEVEL 4
            print('LEVEL 4')
            go_to_next_level()
            player.maxnukes = 4
            player.maxlives = 4
            asteroid_spawn_min = 500
            asteroid_spawn_max = 1100
            enemy_spawn_min = 700
            enemy_spawn_max = 1400
            spawn_rates = ['Flea'] * 1 + ['Cricket'] * 2 + ['Madball'] * 3 + ['Grasshopper'] * 4

        elif progression['Current level'] == 4 and now - local_time > 150000:  # LEVEL 5
            print('LEVEL 5')
            go_to_next_level()
            bosses.add(Boss(enemy_bullets, images, sounds, progression, bonus_rates))
            bonus_rates['Asteroid'] = (0.3, (5, 2, 3, 4, 0, 4))

        elif progression['Current level'] == 5 and progression['Boss killed'] and now - progression['Boss killed time'] > 1000:  # LEVEL 6
            print('LEVEL 6')
            go_to_next_level()
            spawn_rates = ['Flea'] * 1 + ['Cricket'] * 2 + ['Madball'] * 3 + ['Grasshopper'] * 4 + [
                    'Mantis'] * 5
            bonus_rates['Asteroid'] = (0.1, (5, 2, 3, 4, 0, 4))
            bonus_rates['Cricket'] = (0.3, (4, 2, 3, 4, 1, 4))
            bonus_rates['Flea'] = (0.4, (4, 2, 3, 4, 1, 4))
            bonus_rates['Madball'] = (0.5, (4, 2, 3, 4, 1, 4))
            bonus_rates['Grasshopper'] = (0.6, (4, 2, 3, 4, 1, 4))

        elif progression['Current level'] == 6 and now - local_time > 180000:  # LEVEL 7
            print('LEVEL 7')
            go_to_next_level()
            player.maxnukes = 5
            player.maxlives = 5
            asteroid_spawn_min = 500
            asteroid_spawn_max = 1200
            enemy_spawn_min = 1000
            enemy_spawn_max = 2000
            spawn_rates = ['Flea'] * 1 + ['Cricket'] * 2 + ['Madball'] * 3 + ['Grasshopper'] * 4 + [
                    'Mantis'] * 5 + ['Beetle'] * 6

        elif progression['Current level'] == 7 and now - local_time > 210000:  # LEVEL 8 - FINAL
            print('LEVEL 8')
            go_to_next_level()
            bosses.add(FinalBoss(enemy_bullets, images, sounds, fighters, progression, bonus_rates))
            bonus_rates['Asteroid'] = (0.3, (9, 3, 3, 3, 1, 3))

        elif progression['Current level'] == 8:  # ENDGAME
            if progression['Final killed'] and not progression['Music stops']:
                progression['Music stops'] = True
                pygame.mixer.music.fadeout(1000)
            if progression['Final killed'] and not progression['Final fanfare'] and now - progression['Final killed time'] > 2000:
                progression['Final fanfare'] = True
                sounds['Fanfare'].play()
            if progression['Final killed'] and not progression['Win'] and len(fighters) == 0 and now - progression['Final killed time'] > 9000:
                progression['Win'] = True
                general.add(Dummy(images, player.rect.center))
                player.kill()
                sounds['Thrust'].play()

        # UPDATE SPRITES
        general.update(mouse_pos)
        celestials.update()
        bullets.update()
        enemy_bullets.update()
        asteroids.update()
        powerups.update()
        nebulae.update()
        fighters.update(now, player.rect.center)
        effects.update()
        bosses.update(now, player.rect.center)


        # CHECK FOR MOBS BEING HIT BY BULLET
        hits = pygame.sprite.groupcollide(fighters, bullets, False, True)
        hits_b = pygame.sprite.groupcollide(bosses, bullets, False, True)
        hits_a = pygame.sprite.groupcollide(asteroids, bullets, False, True,)
        hits |= hits_a
        hits |= hits_b

        for hit in hits:
            score += hit.take_damage(hits[hit][0].damage, effects, animation, sounds, score, powerups, powerup_icons, hits[hit][0].rect.center, now)

        # CHECK IF PLAYER PICK UP A POWERUP
        hits = pygame.sprite.spritecollide(player, powerups, True, pygame.sprite.collide_rect_ratio(0.7))
        for hit in hits:
            score += 10
            player.powerup(hit.pow_type)

        # CHECK FOR PLAYER BEING HIT BY ENEMY BULLETS
        hits = pygame.sprite.spritecollide(player, enemy_bullets, True, pygame.sprite.collide_rect_ratio(0.7))
        for hit in hits:
            player.shield -= hit.damage
            sounds["Damage"].play()
            effects.add(Effect(start_position=hits[0].rect.center, animation=animation['adsorb']))
            effects.add(Effect(start_position=player.rect.center, animation=animation['shield'], trailing=player))
            is_player_alive()

        # CHECK FOR PLAYER BEING HIT BY FIGHTERS
        hits = pygame.sprite.spritecollide(player, fighters, True, pygame.sprite.collide_rect_ratio(0.8))
        for hit in hits:
            player.shield -= hit.collision_damage
            choice(sounds['Explosions']).play()
            sounds["Damage"].play()
            effects.add(Effect(start_position=hit.rect.center, animation=choice(animation['explosion'])))
            effects.add(Effect(start_position=player.rect.center, animation=animation['shield'], trailing=player))
            is_player_alive()

        # CHECK FOR PLAYER BEING HIT BY BOSS
        hits = pygame.sprite.spritecollide(player, bosses, False, pygame.sprite.collide_rect_ratio(0.8))
        for hit in hits:
            player.shield -= 1
            is_player_alive()

        # CHECK FOR PLAYER BEING HIT BY ASTEROID
        hits = pygame.sprite.spritecollide(player, asteroids, True, pygame.sprite.collide_rect_ratio(0.8))
        for hit in hits:
            player.shield -= hit.collision_damage
            choice(sounds['Explosions']).play()
            sounds["Damage"].play()
            effects.add(Effect(start_position=hit.rect.center, animation=choice(animation['explosion'])))
            effects.add(Effect(start_position=player.rect.center, animation=animation['shield'], trailing=player))
            is_player_alive()

        if not player.alive() and now - player_was_alive > 4000:
            game_over = True

        # RENDERING
        screen.blit(images['Background'], background_rect)
        celestials.draw(screen)
        nebulae.draw(screen)
        general.draw(screen)
        asteroids.draw(screen)
        powerups.draw(screen)
        enemy_bullets.draw(screen)
        bullets.draw(screen)
        fighters.draw(screen)
        bosses.draw(screen)
        effects.draw(screen)

        draw_text(screen, str(score), fonts['base'], WIDTH / 2, 10, (124, 252, 0))
        draw_shield_bar(screen, 15, 13, player.shield, player.maxshield)
        draw_weapon_bar(screen, 15, 33, player.weapon_type, player.pow_uptime, player.powerup_length, now)
        draw_lives_and_nukes(screen, WIDTH - 15, 15, player, images)

        pygame.display.flip()

    pygame.quit()
