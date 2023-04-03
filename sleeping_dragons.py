import math


WIDTH = 800
HEIGHT = 600
CENTER_X = WIDTH / 2
CENTER_Y = HEIGHT / 2
CENTER = (CENTER_X, CENTER_Y)
FONT_COLOR = (0, 0, 0)
EGG_TARGET = 20
HERO_START = (200, 300)
ATTACK_DISTANCE = 200
DRAGON_WAKE_TIME = 2
EGG_HIDE_TIME = 2
MOVE_DISTANCE = 5

lives = 3
eggs_collected = 0
game_over = False
game_complete = False
reset_required = False


# levels as dictionaries

easy_lair = {
    "dragon": Actor("C:\\tmp\\sleeping_dragons\\images\\dragon-asleep.png", pos=(600, 100)),
    "eggs": Actor("C:\\tmp\\sleeping_dragons\\images\\one-egg.png", pos=(400, 100)),
    "egg_count": 1,
    "egg_hidden": False,
    "sleep_length": 10,
    "sleep_counter": 0,
    "wake_counter": 0
}


medium_lair = {
    "dragon": Actor("C:\\tmp\\sleeping_dragons\\images\\dragon-asleep.png", pos=(600, 300)),
    "eggs": Actor("C:\\tmp\\sleeping_dragons\\images\\two-eggs.png", pos=(400, 300)),
    "egg_count": 2,
    "egg_hidden": False,
    "sleep_length": 7,
    "sleep_counter": 0,
    "wake_counter": 0
}


hard_lair = {
    "dragon": Actor("C:\\tmp\\sleeping_dragons\\images\\dragon-asleep.png", pos=(600, 500)),
    "eggs": Actor("C:\\tmp\\sleeping_dragons\\images\\three-eggs.png", pos=(400, 500)),
    "egg_count": 3,
    "egg_hidden": False,
    "sleep_length": 4,
    "sleep_counter": 0,
    "wake_counter": 0
}

lairs = [easy_lair, medium_lair, hard_lair]
hero = Actor("C:\\tmp\sleeping_dragons\\images\\hero.png", pos=HERO_START)


def draw():
    global lais, eggs_collected, game_complete
    screen.clear()
    screen.blit("C:\\tmp\\sleeping_dragons\\images\\dungeon.png", (0, 0))
    if game_over:
        screen.draw.text("GAME OVER!", fontsize=60, center=CENTER, color=FONT_COLOR)
    elif game_complete:
        screen.draw.text("YOU WON!", fontsize=60, center=CENTER, color=FONT_COLOR)
    else:
        hero.draw()
        draw_lairs(lairs)
        draw_counters(eggs_collected,lives)

    
def draw_lairs(lairs_to_draw):
    for lair in lairs_to_draw:
        lair["dragon"].draw()
        if lair["egg_hidden"] is False:
            lair["eggs"].draw()

def draw_counters(eggs_collected, lives):
    screen.blit("C:\\tmp\\sleeping_dragons\\images\\egg-count.png", (0, HEIGHT - 30))
    screen.draw.text(str(eggs_collected), fontsize=40, pos=(30, HEIGHT -30), color=FONT_COLOR)
    screen.blit("C:\\tmp\\sleeping_dragons\\images\\life-count.png", (60, HEIGHT - 30))
    screen.draw.text(str(lives), fontsize=40, pos=(90, HEIGHT -30), color=FONT_COLOR)


def update():
    if keyboard.right:
        hero.x += MOVE_DISTANCE
        if hero.x > WIDTH:
            hero.x = WIDTH
    elif keyboard.left:
        hero.x -= MOVE_DISTANCE
        if hero.x < 0:
            hero.x = 0
    elif keyboard.down:
        hero.y += MOVE_DISTANCE
        if hero.y > HEIGHT:
            hero.y = HEIGHT
    elif keyboard.up:
        hero.y -= MOVE_DISTANCE
        if hero.y < 0:
            hero.y = 0
    check_for_collisions()

def check_for_collisions():
    pass



