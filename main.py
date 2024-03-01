import os

import pygame
import sys
from game import Game
from pygame import mixer

import conf

pygame.init()
mixer.init()
screen = pygame.display.set_mode((1000, 700))
pygame.display.set_caption("Cosmic Glide: UFO Adventure")

path = os.getcwd()

icon = pygame.image.load(conf.icon)
pygame.display.set_icon(icon)

clock = pygame.time.Clock()

mixer.music.load(conf.theme)
mixer.music.set_volume(0.2)
mixer.music.play(loops=-1)

# Sounds
sounds_path = conf.sounds
game_over_sounds = os.listdir(conf.game_over_sounds)

# Skins
skins = conf.skins
main_skin = conf.main_skin

# Background
backgrounds = conf.backgrounds
obstacles_path = conf.obstacle
dead_animation_path = conf.dead_animation
explosion = conf.explosion_sound

# Menu pick
menu_pick = conf.menu_image

try:
    game = Game( main_skin,
                 obstacles_path,
                 backgrounds,
                 menu_pick, # Menu image
                 screen,
                 clock,
                 game_over_sounds,
                 skins,
                 dead_animation_path,
                 explosion
                 )
except FileNotFoundError:
    print("Please check the paths to media files and pictures")
    exit()

game.resize_images()


while game.menu_trigger or game.skins_trigger or game.difficult_trigger:
    game.menu()
    game.change_skin()


SPAWNPIPE = pygame.USEREVENT


pygame.time.set_timer(SPAWNPIPE, 1000)

LOCATION_SPEED = {
        "easy": 2,
        "medium": 4,
        "hard": 7
    }

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game.active:
                game.flap()

            if event.key == pygame.K_SPACE and not game.active:
                mixer.music.set_volume(0.2)
                game.restart_game()

            if not game.active and event.key == pygame.K_ESCAPE:
                mixer.music.set_volume(0.2)
                game.active = False
                game.menu_trigger = True
                game.menu()

        if event.type == SPAWNPIPE:
            game.add_pipe()
    game.show_background()

    if game.active:
        game.show_bird()
        game.update_bird()
        game.show_pipes()
        game.move_pipes()
        game.check_collision()
        game.update_score()
        game.show_score("playing", (255, 255, 255))
        game.play_sounds()
        game.move_location(LOCATION_SPEED[game.level])
    else:
        game.game_over((255, 255, 255))
        mixer.music.set_volume(0.0)
        game.move_location(0.1)

    # game.get_fps()

    pygame.display.update()
    clock.tick_busy_loop(120)
