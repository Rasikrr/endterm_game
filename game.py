import os

import pygame
import random
import sys
from pygame import mixer
import conf


class Game:
    def __init__(self, bird_img, bottom_pipe_img, background_img, menu_img, screen, clock, game_over_sounds_list, skins_path):
        self.screen = screen
        self.bird = pygame.image.load(bird_img).convert_alpha()
        self.bird_rect = pygame.Rect(200, 300, 100, 70)
        self.menu_img = pygame.image.load(menu_img).convert_alpha()
        self.bottom_pipe = pygame.image.load(bottom_pipe_img).convert_alpha()
        self.background = pygame.image.load(background_img).convert_alpha()
        # self.ground = pygame.image.load(ground_img).convert_alpha()
        self.ground_pos = 0
        self.background_pos = 0
        self.active = True
        self.gravity = 0.1
        self.bird_movement = 0
        self.rotated_bird = pygame.Surface((0, 0))
        self.pipes = []
        self.pipes_height = [280, 425, 562, 400, 300, 440, 278, 200, 342]
        self.font = pygame.font.SysFont(None, 48)
        self.score = 0
        self.high_score = 0
        self.menu_trigger = True
        self.clock = clock
        mixer.init()
        self.colors = {"red": (255, 0, 0),
                       "orange": (255, 153, 51),
                       "yellow": (255, 255, 51),
                       "green": (0, 255, 0)
                       }
        self.path = os.getcwd()
        self.sounds_path = conf.in_game_sounds
        self.sounds_list = os.listdir(self.sounds_path)
        self.sounds = {"5_score": mixer.Sound(self.sounds_path/"5_score.mp3"),
                       "20_score": mixer.Sound(self.sounds_path/"20_score.mp3")
                       }
        self.sound_counter = 0
        self.game_over_sounds_path = fr"{self.path}\sounds\game_over_sounds"
        self.game_over_sounds_list = game_over_sounds_list
        self.game_over_sounds = {i+1: mixer.Sound(fr"{self.game_over_sounds_path}\{name}") for i, name in enumerate(self.game_over_sounds_list)}
        self.skins = {i+1: pygame.image.load(f"{skins_path}\{name}") for i, name in enumerate(os.listdir(skins_path))}
        self.skins_trigger = False
        self.back_button = {"non pressed": pygame.image.load(fr"{self.path}\images\back.png"),
                            "pressed": pygame.image.load(fr"{self.path}\images\back_pressed.png")}

    def resize_images(self):
        # Don't forget to change rect
        self.bird = pygame.transform.scale(self.bird, (100, 70))  # 75, 55
        self.background = pygame.transform.scale(self.background, (1000, 720))
        self.bottom_pipe = pygame.transform.scale(self.bottom_pipe, (100, 650))
        # self.ground = pygame.transform.scale(self.ground, (1000, 160))
        self.menu_img = pygame.transform.scale(self.menu_img, (250, 300))

    def show_background(self):
        self.screen.blit(self.background, (self.background_pos, 0))
        self.screen.blit(self.background, (self.background_pos + 1000, 0))

    # def show_ground(self):
    #     self.screen.blit(self.ground, (self.ground_pos, 630))
    #     self.screen.blit(self.ground, (self.ground_pos + 1000, 630))

    def move_location(self, speed):
        self.ground_pos -= speed
        self.background_pos -= speed
        if self.ground_pos <= -1000:
            self.ground_pos = 0
        if self.background_pos <= -1000:
            self.background_pos = 0

    def show_bird(self):
        pygame.draw.rect(self.screen, (255, 0, 0), self.bird_rect)
        self.screen.blit(self.rotated_bird, self.bird_rect)

    def update_bird(self):
        self.bird_movement += self.gravity
        self.rotated_bird = self.rotate_bird()
        self.bird_rect.centery += self.bird_movement

    def rotate_bird(self):
        new_bird = pygame.transform.rotozoom(self.bird, -self.bird_movement * 3, 1)
        return new_bird

    def flap(self):
        self.bird_movement = 0
        self.bird_movement -= 2.9

    def add_pipe(self):
        random_pipe_pos = random.choice(self.pipes_height)
        bottom_pipe = pygame.Rect(1050, random_pipe_pos, 1, 650)
        top_pipe = pygame.Rect(1050, random_pipe_pos-850, 70, 650)
        self.pipes.append(bottom_pipe)
        self.pipes.append(top_pipe)

    def move_pipes(self):
        for pipe in self.pipes:
            pipe.centerx -= 2.3
            if pipe.centerx <= -50:
                self.pipes.remove(pipe)

    def show_pipes(self):
        for pipe in self.pipes:
            if pipe.bottom >= 700:
                pipe_hitbox = pygame.Rect(pipe.left, pipe.top, self.bottom_pipe.get_width(),
                                          self.bottom_pipe.get_height())  # Create hitbox based on image dimensions
                pygame.draw.rect(self.screen, (0, 0, 255), pipe_hitbox, 2)  # Draw hitbox with a border
                self.screen.blit(self.bottom_pipe, pipe)
            else:
                flip_pipe = pygame.transform.flip(self.bottom_pipe, False, True)
                pipe_hitbox = pygame.Rect(pipe.left, pipe.top, flip_pipe.get_width(),
                                          flip_pipe.get_height())  # Create hitbox for flipped pipe
                pygame.draw.rect(self.screen, (0, 0, 255), pipe_hitbox, 2)  # Draw hitbox with a border
                self.screen.blit(flip_pipe, pipe)

    def check_collision(self):
        for pipe in self.pipes:
            if self.bird_rect.colliderect(pipe):
                self.active = False
                self.game_over_sound_play()

        if self.bird_rect.top <= -10 or self.bird_rect.bottom >= 720:
            self.active = False
            self.game_over_sound_play()

    def update_score(self):
        self.score += 0.01

    def show_score(self, game_state, color):
        score_surface = self.font.render(f"Score: {int(self.score)}", True, color)
        score_rect = score_surface.get_rect(center=(500, 100))
        self.screen.blit(score_surface, score_rect)

        if game_state == "game over":
            restart_text1 = self.font.render("Press Space Bar", True, color)
            menu_text = self.font.render("Press Esc to menu", True, color)
            restart_rect1 = restart_text1.get_rect(center=(500, 300))
            menu_rect = menu_text.get_rect(center=(500, 350))
            self.screen.blit(restart_text1, restart_rect1)
            self.screen.blit(menu_text, menu_rect)

    def game_over(self, color):
        self.update_high_score()
        self.show_score("game over", color)

    def update_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score

    def restart_game(self):
        self.active = True
        del self.pipes[:]
        self.bird_rect.center = (200, 300)
        self.bird_movement = 0
        self.score = 0

    def menu(self):
        play_button = self.font.render("Play", True, (0, 0, 0))
        quit_button = self.font.render("Quit", True, (0, 0, 0))
        skins_button = self.font.render("Skins", True, (0, 0, 0))

        play_rect = pygame.Rect(400, 400, 200, 50)
        skins_rect = pygame.Rect(400, 470, 200, 50)
        quit_rect = pygame.Rect(400, 540, 200, 50)

        while self.menu_trigger and not self.skins_trigger:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.show_background()
            self.get_fps()
            self.screen.blit(self.menu_img, (380, 50))

            # self.show_ground()
            self.author()
            self.move_location(0.1)

            pygame.draw.rect(self.screen, (112, 128, 144), play_rect, border_radius=25, width=5)
            self.screen.blit(play_button, (play_rect.centerx-40, play_rect.centery-15))

            pygame.draw.rect(self.screen, (112, 128, 144), skins_rect, border_radius=25, width=5)
            self.screen.blit(skins_button, (skins_rect.centerx-45, skins_rect.centery-15))

            pygame.draw.rect(self.screen, (112, 128, 144), quit_rect, border_radius=25, width=5)
            self.screen.blit(quit_button, (quit_rect.centerx-40, quit_rect.centery-15))

            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()

            if play_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (112, 128, 144), play_rect, border_radius=25)
                self.screen.blit(play_button, (play_rect.centerx-40, play_rect.centery - 15))
                if mouse_click[0]:
                    self.menu_trigger = False

            if skins_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (112, 128, 144), skins_rect, border_radius=25)
                self.screen.blit(skins_button, (skins_rect.centerx - 45, skins_rect.centery - 15))
                if mouse_click[0]:
                    self.skins_trigger = True
                    self.change_skin()

            if quit_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (112, 128, 144), quit_rect, border_radius=25)
                self.screen.blit(quit_button, (quit_rect.centerx - 40, quit_rect.centery - 15))
                if mouse_click[0]:
                    self.menu_trigger = False
                    pygame.quit()
                    sys.exit()

            self.clock.tick(300)
            pygame.display.flip()

    def get_fps(self):
        FPS_RECT = pygame.Rect(900, 50, 35, 45)
        FPS = self.clock.get_fps()
        if int(FPS)<30:
            FPS_str = self.font.render(str(int(FPS)), True, self.colors["red"])
            self.screen.blit(FPS_str, FPS_RECT)
        elif 30 < int(FPS)< 59:
            FPS_str = self.font.render(str(int(FPS)), True, self.colors["orange"])
            self.screen.blit(FPS_str, FPS_RECT)
        elif 60 < int(FPS)< 90:
            FPS_str = self.font.render(str(int(FPS)), True, self.colors["yellow"])
            self.screen.blit(FPS_str, FPS_RECT)
        else:
            FPS_str = self.font.render(str(int(FPS)), True, self.colors["green"])
            self.screen.blit(FPS_str, FPS_RECT)

    def author(self):
        author_name = self.font.render("Created by Amir, Rassul, Kaminur and Alima", True, (255, 255, 255))
        rect = pygame.Rect(290, 660, 40, 10)
        self.screen.blit(author_name, rect)

    def play_sounds(self):
        if self.sounds_list:
            if round(self.score, 2) % 20 == 0 and self.score and self.active:
                self.sounds["20_score"].play()
                return
            if round(self.score, 2) % 5 == 0 and self.score and self.active:
                self.sounds["5_score"].play()

    def game_over_sound_play(self):
        sound = self.game_over_sounds[random.randint(1, len(self.game_over_sounds_list))]
        sound.play()

    def change_skin(self):
        self.menu_trigger = False

        back_button_rect = pygame.Rect(30, 50, 100, 45)
        rect = pygame.Rect(150, 90, 700, 500)
        skin_number = random.randint(1, len(self.skins))
        skin = self.skins[skin_number]

        while self.skins_trigger:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.show_background()
            self.get_fps()

            # self.show_ground()
            self.author()
            self.move_location(0.1)

            pygame.draw.rect(self.screen, (128, 128, 128), rect, border_radius=10)
            self.screen.blit(self.back_button["non pressed"], back_button_rect)
            self.screen.blit(skin,(rect.centerx-140, rect.centery-150))

            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()

            if back_button_rect.collidepoint(mouse_pos):
                self.screen.blit(self.back_button["pressed"], back_button_rect)
                if mouse_click[0]:
                    self.menu_trigger = True
                    self.skins_trigger = False

            self.clock.tick(300)
            pygame.display.flip()
