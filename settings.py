# SET SCREENSIZE AND FPS
WIDTH = 600
HEIGHT = 750
FPS = 60


spawn_rates_default = ['Flea']
# SPAWN_RATES = ['Flea']*6 + ['Cricket']*5 + ['Madball']*4 + ['Grasshopper']*3 + ['Mantis']*2 + ['Beetle']
# first value = probability of bonus, tuple = shares of probabilyty for types of bonuses:
# (shield, miniblaster, sideguns, plasma, life, nuke)
bonus_rates_defaults = {
    'Asteroid': (0.1, (5, 5, 0, 0, 0, 0)),     # Lv1 - miniblaster
    'Flea': (0.2, (3, 12, 0, 0, 1, 0)),
    'Cricket': (0.3, (3, 12, 0, 0, 1, 3)),   # Lv2 - nukes #3
    'Madball': (0.5, (3, 5, 7, 0, 1, 3)),     # Lv3 - sideguns,
    'Grasshopper': (0.6, (3, 5, 7, 0, 1, 3)),  # Lv4 - #4
    'Boss': (1, (3, 2, 3, 4, 1, 3)),           # Lv5 - plasma,
    'Mantis': (0.7, (3, 2, 3, 4, 1, 3)),       # Lv6 -
    'Beetle': (0.8, (3, 2, 3, 4, 1, 3)),      # Lv7 - #5
    'CricketDrone': (1, (3, 2, 3, 4, 1, 3)),   # Lv8

}

asteroid_spawn_time = 1000
asteroid_spawn_min = 700
asteroid_spawn_max = 1500
enemy_spawn_time = 2000
enemy_spawn_min = 800
enemy_spawn_max = 2000
nuke_cooldown_time = 2000
nuke_damage = 20

progression_default = {
    'Current level': 1,
    'Boss killed': False,
    'Boss killed time': 0,
    'Final killed': False,
    'Final killed time': 0,
    'Music stops': False,
    'Final fanfare': False,
    'Win': False,
    'Highscores shown': False,
}