import random

import pygame
import sys
from game import Game
from pygame import mixer
import os

pygame.init()
mixer.init()
screen = pygame.display.set_mode((1000, 720))
pygame.display.set_caption("CHINUR")

path = os.getcwd()

icon = pygame.image.load(fr"{path}\images\menu_pick.jpg")
pygame.display.set_icon(icon)

clock = pygame.time.Clock()

mixer.music.load("music.mp3")
mixer.music.set_volume(0.2)
mixer.music.play(loops=-1)

#sounds
sounds = os.listdir(fr"{path}\sounds")
game_over_sounds = os.listdir(fr"{path}\game_over_sounds")

#skins
skins = list(filter(lambda x: x[-4:] == ".png", os.listdir(fr"{path}\images\skins")))


game = Game( fr"{path}\images\skins\sprite_chnur.png", fr"{path}\images\kabel.png", fr"{path}\images\school.jpg",  fr"{path}\images\floor.jpg",  fr"{path}\images\final_pixel_chnur.png",  fr"{path}\images\usb_c.png", screen, clock, sounds, game_over_sounds, skins)
game.resize_images()

game.sounds[random.randint(1, len(sounds))].play()

while game.menu_trigger or game.skins_trigger:
    game.menu()
    game.change_skin()


SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1000)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game.active:
                game.flap()

            if event.key == pygame.K_SPACE and not game.active:
                game.restart_game()

            if not game.active and event.key == pygame.K_ESCAPE:
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

    game.get_fps()
    game.show_ground()
    game.move_location(1)

    pygame.display.update()
    clock.tick(120)
