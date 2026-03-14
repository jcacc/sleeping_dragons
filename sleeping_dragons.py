import pygame
import math
import os
import sys

# --- Constants ---
WIDTH = 800
HEIGHT = 600
FPS = 60
CENTER = (WIDTH // 2, HEIGHT // 2)
FONT_COLOR = (0, 0, 0)
EGG_TARGET = 20
HERO_START = (200, 300)
ATTACK_DISTANCE = 200
DRAGON_WAKE_TIME = 2    # seconds (lair update ticks)
EGG_HIDE_TIME = 2       # seconds (lair update ticks)
MOVE_DISTANCE = 5

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")
MUSIC_PATH = os.path.join(os.path.dirname(__file__), "music", "dungeon.ogg")

# --- Init ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sleeping Dragons")
game_clock = pygame.time.Clock()

# --- Image cache ---
_image_cache = {}

def load_image(name):
    if name not in _image_cache:
        img = pygame.image.load(os.path.join(IMAGES_DIR, name)).convert_alpha()
        _image_cache[name] = img
    return _image_cache[name]

# --- Actor ---
class Actor:
    def __init__(self, image_name, pos):
        self.image_name = image_name
        self._surface = load_image(image_name)
        self._rect = self._surface.get_rect(center=pos)

    @property
    def image(self):
        return self.image_name

    @image.setter
    def image(self, name):
        self.image_name = name
        center = self._rect.center
        self._surface = load_image(name)
        self._rect = self._surface.get_rect(center=center)

    @property
    def x(self):
        return self._rect.centerx

    @x.setter
    def x(self, val):
        self._rect.centerx = int(val)

    @property
    def y(self):
        return self._rect.centery

    @y.setter
    def y(self, val):
        self._rect.centery = int(val)

    @property
    def pos(self):
        return self._rect.center

    @pos.setter
    def pos(self, val):
        self._rect.center = (int(val[0]), int(val[1]))

    def draw(self, surf):
        surf.blit(self._surface, self._rect)

    def colliderect(self, other):
        return self._rect.colliderect(other._rect)

# --- Animation ---
class Animation:
    def __init__(self, actor, target_pos, duration=0.5, on_finished=None):
        self.actor = actor
        self.start_pos = (float(actor.x), float(actor.y))
        self.target_pos = (float(target_pos[0]), float(target_pos[1]))
        self.duration = duration
        self.elapsed = 0.0
        self.on_finished = on_finished
        self.done = False

    def update(self, dt):
        if self.done:
            return
        self.elapsed += dt
        t = min(self.elapsed / self.duration, 1.0)
        self.actor.x = self.start_pos[0] + (self.target_pos[0] - self.start_pos[0]) * t
        self.actor.y = self.start_pos[1] + (self.target_pos[1] - self.start_pos[1]) * t
        if t >= 1.0:
            self.done = True
            if self.on_finished:
                self.on_finished()

# --- Game state ---
lives = 3
eggs_collected = 0
game_over = False
game_complete = False
reset_required = False
active_animation = None
lair_update_timer = 0.0

def make_lairs():
    return [
        {
            "dragon": Actor("dragon-asleep.png", pos=(600, 100)),
            "eggs": Actor("one-egg.png", pos=(400, 100)),
            "egg_count": 1,
            "egg_hidden": False,
            "egg_hide_counter": 0,
            "sleep_length": 10,
            "sleep_counter": 0,
            "wake_counter": 0,
        },
        {
            "dragon": Actor("dragon-asleep.png", pos=(600, 300)),
            "eggs": Actor("two-eggs.png", pos=(400, 300)),
            "egg_count": 2,
            "egg_hidden": False,
            "egg_hide_counter": 0,
            "sleep_length": 7,
            "sleep_counter": 0,
            "wake_counter": 0,
        },
        {
            "dragon": Actor("dragon-asleep.png", pos=(600, 500)),
            "eggs": Actor("three-eggs.png", pos=(400, 500)),
            "egg_count": 3,
            "egg_hidden": False,
            "egg_hide_counter": 0,
            "sleep_length": 4,
            "sleep_counter": 0,
            "wake_counter": 0,
        },
    ]

lairs = make_lairs()
hero = Actor("hero.png", pos=HERO_START)

# --- Assets ---
background = load_image("dungeon.png")
egg_count_img = load_image("egg-count.png")
life_count_img = load_image("life-count.png")

font_big = pygame.font.SysFont(None, 90)
font_med = pygame.font.SysFont(None, 52)
font_small = pygame.font.SysFont(None, 40)

# --- Music ---
# Drop an OGG/MP3 file at music/dungeon.ogg to enable background music
if os.path.exists(MUSIC_PATH):
    pygame.mixer.music.load(MUSIC_PATH)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

# --- Draw ---
def draw():
    screen.blit(background, (0, 0))
    if game_over:
        draw_game_over()
    elif game_complete:
        draw_win_screen()
    else:
        hero.draw(screen)
        draw_lairs()
        draw_hud()

def draw_lairs():
    for lair in lairs:
        lair["dragon"].draw(screen)
        if not lair["egg_hidden"]:
            lair["eggs"].draw(screen)

def draw_hud():
    screen.blit(egg_count_img, (0, HEIGHT - 30))
    screen.blit(font_small.render(str(eggs_collected), True, FONT_COLOR), (32, HEIGHT - 30))
    screen.blit(life_count_img, (60, HEIGHT - 30))
    screen.blit(font_small.render(str(lives), True, FONT_COLOR), (92, HEIGHT - 30))

def draw_overlay(alpha):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, alpha))
    screen.blit(overlay, (0, 0))

def draw_centered(surf, y):
    screen.blit(surf, surf.get_rect(center=(CENTER[0], y)))

def draw_game_over():
    draw_overlay(170)
    draw_centered(font_big.render("GAME OVER", True, (220, 40, 40)),    CENTER[1] - 80)
    draw_centered(font_med.render(f"You snagged {eggs_collected} of {EGG_TARGET} eggs", True, (255, 200, 200)), CENTER[1])
    draw_centered(font_small.render("Press R to try again", True, (180, 180, 180)),        CENTER[1] + 70)

def draw_win_screen():
    draw_overlay(130)
    draw_centered(font_big.render("YOU WON!", True, (255, 215, 0)),        CENTER[1] - 80)
    draw_centered(font_med.render(f"All {EGG_TARGET} eggs collected!", True, (255, 255, 200)), CENTER[1])
    draw_centered(font_small.render("Press R to play again", True, (180, 180, 180)),       CENTER[1] + 70)

# --- Update ---
def update(dt, keys):
    global active_animation
    if game_over or game_complete:
        return
    if not reset_required:
        handle_input(keys)
    if active_animation:
        active_animation.update(dt)
        if active_animation.done:
            active_animation = None
    check_for_collisions()

def handle_input(keys):
    if keys[pygame.K_RIGHT]:
        hero.x = min(hero.x + MOVE_DISTANCE, WIDTH)
    elif keys[pygame.K_LEFT]:
        hero.x = max(hero.x - MOVE_DISTANCE, 0)
    elif keys[pygame.K_DOWN]:
        hero.y = min(hero.y + MOVE_DISTANCE, HEIGHT)
    elif keys[pygame.K_UP]:
        hero.y = max(hero.y - MOVE_DISTANCE, 0)

def update_lairs():
    for lair in lairs:
        if lair["dragon"].image == "dragon-asleep.png":
            update_sleeping_dragon(lair)
        elif lair["dragon"].image == "dragon-awake.png":
            update_waking_dragon(lair)
        update_egg(lair)

def update_sleeping_dragon(lair):
    if lair["sleep_counter"] >= lair["sleep_length"]:
        lair["dragon"].image = "dragon-awake.png"
        lair["sleep_counter"] = 0
    else:
        lair["sleep_counter"] += 1

def update_waking_dragon(lair):
    if lair["wake_counter"] >= DRAGON_WAKE_TIME:
        lair["dragon"].image = "dragon-asleep.png"
        lair["wake_counter"] = 0
    else:
        lair["wake_counter"] += 1

def update_egg(lair):
    if lair["egg_hidden"]:
        if lair["egg_hide_counter"] >= EGG_HIDE_TIME:
            lair["egg_hidden"] = False
            lair["egg_hide_counter"] = 0
        else:
            lair["egg_hide_counter"] += 1

def check_for_collisions():
    for lair in lairs:
        if not lair["egg_hidden"]:
            check_for_egg_collision(lair)
        if lair["dragon"].image == "dragon-awake.png" and not reset_required:
            check_for_dragon_collision(lair)

def check_for_dragon_collision(lair):
    dx = hero.x - lair["dragon"].x
    dy = hero.y - lair["dragon"].y
    distance = math.hypot(dx, dy)
    in_flame_cone = dx < 50 and abs(dy) < ATTACK_DISTANCE * 0.6
    if distance < ATTACK_DISTANCE and in_flame_cone:
        handle_dragon_collision()

def handle_dragon_collision():
    global reset_required, active_animation
    reset_required = True
    active_animation = Animation(hero, HERO_START, duration=0.5, on_finished=subtract_life)

def check_for_egg_collision(lair):
    global eggs_collected, game_complete
    if hero.colliderect(lair["eggs"]):
        lair["egg_hidden"] = True
        eggs_collected += lair["egg_count"]
        if eggs_collected >= EGG_TARGET:
            game_complete = True

def subtract_life():
    global lives, reset_required, game_over
    lives -= 1
    if lives == 0:
        game_over = True
    reset_required = False

def reset_game():
    global lives, eggs_collected, game_over, game_complete
    global reset_required, lairs, active_animation, lair_update_timer
    lives = 3
    eggs_collected = 0
    game_over = False
    game_complete = False
    reset_required = False
    active_animation = None
    lair_update_timer = 0.0
    lairs = make_lairs()
    hero.pos = HERO_START

# --- Main loop ---
def main():
    global lair_update_timer
    while True:
        dt = game_clock.tick(FPS) / 1000.0
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (game_over or game_complete):
                    reset_game()

        update(dt, keys)

        lair_update_timer += dt
        if lair_update_timer >= 1.0:
            lair_update_timer -= 1.0
            if not game_over and not game_complete:
                update_lairs()

        draw()
        pygame.display.flip()

if __name__ == "__main__":
    main()
