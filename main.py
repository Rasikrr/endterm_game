import random
import os

import pygame
import sys
from game import Game
from pygame import mixer

import conf

pygame.init()
mixer.init()
screen = pygame.display.set_mode((1000, 720))
pygame.display.set_caption("Pterodactyl Quest")

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
background = conf.background
obstacle = conf.obstacle

# Menu pick
menu_pick = conf.menu_image

game = Game( main_skin,
             obstacle,
             background,
             menu_pick, # Menu image
             screen,
             clock,
             game_over_sounds,
             skins
             )

game.resize_images()

# game.sounds[random.randint(1, len(sounds))].play()

while game.menu_trigger or game.skins_trigger:
    game.menu()
    game.change_skin()


SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 2000)

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
    else:
        game.game_over((255, 255, 255))
        mixer.music.set_volume(0.0)

    game.get_fps()
    # game.show_ground()
    game.move_location(1)

    pygame.display.update()
    clock.tick(120)
