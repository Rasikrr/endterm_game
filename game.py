import os

import pygame
import random
import sys
from pygame import mixer
import conf


class Game:
    def __init__(self, bird_img, obstacles_path, backgrounds, menu_img, screen, clock, game_over_sounds_list,
                 skins_path, dead_animation_path, explosion_sound):
        """
        Initialize the game object.

        Args:
            bird_img (str): Path to the image file for the bird.
            obstacles_path (str): Path to the folder containing obstacle images.
            backgrounds (str): Path to the folder containing background images.
            menu_img (str): Path to the image file for the menu.
            screen: Pygame screen object.
            clock: Pygame clock object.
            game_over_sounds_list (list): List of file names for game over sounds.
            skins_path (str): Path to the folder containing skin images.
            dead_animation_path (str): Path to the folder containing images for the bird's dead animation.
            explosion_sound (str): Path to the sound file for the explosion sound.
        """
        self.screen = screen
        self.bird = pygame.image.load(bird_img).convert_alpha()
        self.bird_rect = pygame.Rect(100, 100, 100, 70)
        self.bird_mask = pygame.mask.from_surface(self.bird)
        self.menu_img = pygame.image.load(menu_img).convert_alpha()
        self.obstacles = {
            "easy": pygame.image.load(obstacles_path / "fire.png").convert_alpha(),
            "medium": pygame.image.load(obstacles_path / "laser.png").convert_alpha(),
            "hard": pygame.image.load(obstacles_path / "rock.png").convert_alpha()
        }
        self.bottom_pipe = self.obstacles["easy"]
        self.background_pos = 0
        self.active = True
        self.gravity = 0.1
        self.turn_ground = False
        self.bird_movement = 0
        self.rotated_bird = pygame.Surface((0, 0))
        self.pipes = []
        self.pipes_height = [280, 425, 562, 400, 300, 440, 342]
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
        self.sounds = {"5_score": mixer.Sound(self.sounds_path / "5_score.mp3"),
                       "10_score": mixer.Sound(self.sounds_path / "20_score.mp3")
                       }
        self.sound_counter = 0
        self.game_over_sounds_path = fr"{self.path}\sounds\game_over_sounds"
        self.game_over_sounds_list = game_over_sounds_list
        self.game_over_sounds = {i + 1: mixer.Sound(fr"{self.game_over_sounds_path}\{name}") for i, name in
                                 enumerate(self.game_over_sounds_list)}
        self.selected_skin_index = 0
        self.skins_path = skins_path
        self.skins = [pygame.image.load(os.path.join(skins_path, name)) for name in os.listdir(skins_path)]

        self.current_skin = self.skins[self.selected_skin_index]
        self.skins_trigger = False
        self.difficult_trigger = False
        self.levels_location = {
            "easy": pygame.image.load(backgrounds / "space1.jpg"),
            "medium": pygame.image.load(backgrounds / "space2.jpg"),
            "hard": pygame.image.load(backgrounds / "space3.jpg")
        }
        self.background = self.levels_location["easy"]
        self.back_button = {"non pressed": pygame.image.load(fr"{self.path}\images\back.png"),
                            "pressed": pygame.image.load(fr"{self.path}\images\back_pressed.png")}
        self.ok_button = pygame.image.load(fr"{self.path}\images\ok.png")
        self.level = "easy"
        self.move_pipes_speed = {
            "easy": 6.6,
            "medium": 4,
            "hard": 11.0
        }
        self.explosion_images = [pygame.image.load(os.path.join(dead_animation_path, filename)).convert_alpha() for
                            filename in os.listdir(dead_animation_path)]
        self.dead_animation_trigger = False
        self.explosion_sound = mixer.Sound(explosion_sound)

    def resize_images(self):
        """
        Resize images to standard sizes for consistent display.
        """
        self.bird = pygame.transform.scale(self.bird, (100, 70))  # 75, 55
        self.skins = list(map(lambda x: pygame.transform.scale(x, (100, 70)), self.skins))
        self.background = pygame.transform.scale(self.background, (1000, 720))
        self.bottom_pipe = pygame.transform.scale(self.bottom_pipe, (100, 650))
        self.menu_img = pygame.transform.scale(self.menu_img, (500, 300))
        self.explosion_images = list(map(lambda x: pygame.transform.scale(x, (100, 100)), self.explosion_images))
        self.ok_button = pygame.transform.scale(self.ok_button, (150, 75))

    def show_background(self):
        """
        Display the background image.
        """
        self.screen.blit(self.background, (self.background_pos, 0))
        self.screen.blit(self.background, (self.background_pos + 1000, 0))

    def move_location(self, speed):
        """
        Move the location on the background.

        Args:
            speed (float): The speed at which to move the location.
        """
        self.background_pos -= speed
        if self.background_pos <= -1000:
            self.background_pos = 0

    def show_bird(self):
        """
        Display the bird.
        """
        self.screen.blit(self.rotated_bird, self.bird_rect)

    def update_bird(self):
        """
        Update the bird's movement and rotation.
        """
        self.bird_movement += self.gravity
        self.rotated_bird = self.rotate_bird()
        self.bird_rect.centery += self.bird_movement

    def rotate_bird(self):
        """
        Rotate the bird based on its movement.

        Returns:
            Surface: Rotated bird surface.
        """
        new_bird = pygame.transform.rotozoom(self.bird, -self.bird_movement * 3, 1)
        return new_bird

    def flap(self):
        """
        Simulate the bird's flapping movement.
        """
        self.bird_movement = 0
        self.bird_movement -= 4.9

    def add_pipe(self):
        """
        Add a pair of pipes to the game.
        """
        random_pipe_pos = random.choice(self.pipes_height)
        bottom_pipe = pygame.Rect(1050, random_pipe_pos, 1, 650)
        top_pipe = pygame.Rect(1050, random_pipe_pos - 850, 70, 650)
        self.pipes.append(bottom_pipe)
        self.pipes.append(top_pipe)

    def move_pipes(self):
        """
        Move pipes across the screen.
        """
        for pipe in self.pipes:
            pipe.centerx -= self.move_pipes_speed[self.level]
            if pipe.centerx <= -50:
                self.pipes.remove(pipe)

    def show_pipes(self):
        """
        Display pipes on the screen.
        """
        for pipe in self.pipes:
            if pipe.bottom >= 700:
                pipe_hitbox = pygame.Rect(pipe.left, pipe.top, self.bottom_pipe.get_width(),
                                          self.bottom_pipe.get_height())
                self.screen.blit(self.bottom_pipe, pipe)
            else:
                flip_pipe = pygame.transform.flip(self.bottom_pipe, False, True)
                pipe_hitbox = pygame.Rect(pipe.left, pipe.top, flip_pipe.get_width(),
                                          flip_pipe.get_height())
                self.screen.blit(flip_pipe, pipe)

    def check_collision(self):
        """
        Check for collisions between the bird and pipes.
        """
        for pipe in self.pipes:
            if self.bird_rect.colliderect(pipe):
                self.active = False
                self.game_over_sound_play()

        if self.bird_rect.top <= -10 or self.bird_rect.bottom >= 720:
            self.active = False
            self.game_over_sound_play()

    def update_score(self):
        """
        Update the score based on gameplay.
        """
        self.score += 0.01
        if int(self.score) > int(self.high_score):
            self.high_score = self.score

    def show_score(self, game_state, color):
        """
        Display the current score and highest score.

        Args:
            game_state (str): The current state of the game.
            color (tuple): RGB color value.
        """
        score_surface = self.font.render(f"Score: {int(self.score)}", True, color)
        highest_score_surface = self.font.render(f"Highest score: {int(self.high_score)}", True, color)
        score_rect = score_surface.get_rect(center=(500, 100))
        highest_score_rect = score_surface.get_rect(center=(450, 150))
        self.screen.blit(score_surface, score_rect)
        self.screen.blit(highest_score_surface, highest_score_rect)

        if game_state == "game over":
            self.move_location(0.1)
            restart_text1 = self.font.render("Press Space Bar", True, color)
            menu_text = self.font.render("Press Esc to menu", True, color)
            restart_rect1 = restart_text1.get_rect(center=(500, 300))
            menu_rect = menu_text.get_rect(center=(500, 350))
            self.screen.blit(restart_text1, restart_rect1)
            self.screen.blit(menu_text, menu_rect)

    def game_over(self, color):
        """
        Handle game over state.

        Args:
            color (tuple): RGB color value.
        """
        self.update_high_score()
        self.show_score("game over", color)
        if not self.dead_animation_trigger:
            self.dead_animation_trigger = True
            self.dead_animation()

    def dead_animation(self):
        """
        Display an animation when the bird dies.
        """
        explosion_x = self.bird_rect.centerx - self.explosion_images[0].get_width() // 2
        explosion_y = self.bird_rect.centery - self.explosion_images[0].get_height() // 2
        self.explosion_sound.play()

        for explosion_image in self.explosion_images:
            explosion_rect = explosion_image.get_rect(center=(explosion_x, explosion_y))

            self.screen.blit(explosion_image, explosion_rect)

            pygame.display.flip()

            pygame.time.delay(100)
            self.move_location(0.1)

    def update_high_score(self):
        """
        Update the highest score achieved.
        """
        if self.score > self.high_score:
            self.high_score = self.score

    def restart_game(self):
        """
        Restart the game.
        """
        self.active = True
        del self.pipes[:]
        self.bird_rect.center = (200, 300)
        self.bird_movement = 0
        self.score = 0
        self.dead_animation_trigger = False

    def menu(self):
        """
        Display the main menu and handle menu interactions.
        """
        play_button = self.font.render("Play", True, (255, 255, 255))
        quit_button = self.font.render("Quit", True, (255, 255, 255))
        skins_button = self.font.render("Skins", True, (255, 255, 255))

        play_rect = pygame.Rect(400, 400, 200, 50)
        skins_rect = pygame.Rect(400, 470, 200, 50)
        quit_rect = pygame.Rect(400, 540, 200, 50)

        while self.menu_trigger and not self.skins_trigger:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.show_background()

            self.author()
            self.move_location(0.1)
            self.screen.blit(self.menu_img, (260, 50))

            pygame.draw.rect(self.screen, (112, 128, 144), play_rect, border_radius=25, width=5)
            self.screen.blit(play_button, (play_rect.centerx - 40, play_rect.centery - 15))

            pygame.draw.rect(self.screen, (112, 128, 144), skins_rect, border_radius=25, width=5)
            self.screen.blit(skins_button, (skins_rect.centerx - 45, skins_rect.centery - 15))

            pygame.draw.rect(self.screen, (112, 128, 144), quit_rect, border_radius=25, width=5)
            self.screen.blit(quit_button, (quit_rect.centerx - 40, quit_rect.centery - 15))

            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()

            if play_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (112, 128, 144), play_rect, border_radius=25)
                self.screen.blit(play_button, (play_rect.centerx - 40, play_rect.centery - 15))
                if mouse_click[0]:
                    self.difficult_trigger = True
                    self.show_difficulty_menu()

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

    def show_difficulty_menu(self):
        """
        Display the difficulty selection menu.
        """
        easy_button = self.font.render("Easy", True, (255, 255, 255))
        medium_button = self.font.render("Medium", True, (255, 255, 255))
        hard_button = self.font.render("Hard", True, (255, 255, 255))

        button_width = 200
        button_height = 50
        button_padding = 20

        start_x = (1000 - (3 * button_width + 2 * button_padding)) // 2
        start_y = 500

        easy_rect = pygame.Rect(start_x, start_y, button_width, button_height)
        medium_rect = pygame.Rect(start_x + button_width + button_padding, start_y, button_width, button_height)
        hard_rect = pygame.Rect(start_x + 2 * (button_width + button_padding), start_y, button_width, button_height)

        while self.difficult_trigger:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.show_background()

            self.move_location(0.1)

            pygame.draw.rect(self.screen, (112, 128, 144), easy_rect, border_radius=25, width=5)
            self.screen.blit(easy_button, (easy_rect.centerx - 40, easy_rect.centery - 15))

            pygame.draw.rect(self.screen, (112, 128, 144), medium_rect, border_radius=25, width=5)
            self.screen.blit(medium_button, (medium_rect.centerx - 60, medium_rect.centery - 15))

            pygame.draw.rect(self.screen, (112, 128, 144), hard_rect, border_radius=25, width=5)
            self.screen.blit(hard_button, (hard_rect.centerx - 40, hard_rect.centery - 15))

            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()

            if easy_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (112, 128, 144), easy_rect, border_radius=25)
                self.screen.blit(easy_button, (easy_rect.centerx - 40, easy_rect.centery - 15))
                if mouse_click[0]:
                    self.change_level("easy")
                    self.difficult_trigger = False
                    self.menu_trigger = False

            if medium_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (112, 128, 144), medium_rect, border_radius=25)
                self.screen.blit(medium_button, (medium_rect.centerx - 60, medium_rect.centery - 15))
                if mouse_click[0]:
                    self.change_level("medium")
                    self.difficult_trigger = False
                    self.menu_trigger = False

            if hard_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (112, 128, 144), hard_rect, border_radius=25)
                self.screen.blit(hard_button, (hard_rect.centerx - 40, hard_rect.centery - 15))
                if mouse_click[0]:
                    self.change_level("hard")
                    self.difficult_trigger = False
                    self.menu_trigger = False

            self.clock.tick(300)
            pygame.display.flip()

    def change_level(self, level):
        """
        Change the difficulty level of the game.

        Args:
            level (str): The desired difficulty level.
        """
        self.bottom_pipe = self.obstacles[level]
        self.background = self.levels_location[level]
        self.resize_images()
        self.level = level

    def get_fps(self):
        """
        Display the frames per second.
        """
        FPS_RECT = pygame.Rect(900, 50, 35, 45)
        FPS = self.clock.get_fps()
        if int(FPS) < 30:
            FPS_str = self.font.render(str(int(FPS)), True, self.colors["red"])
            self.screen.blit(FPS_str, FPS_RECT)
        elif 30 < int(FPS) < 59:
            FPS_str = self.font.render(str(int(FPS)), True, self.colors["orange"])
            self.screen.blit(FPS_str, FPS_RECT)
        elif 60 < int(FPS) < 90:
            FPS_str = self.font.render(str(int(FPS)), True, self.colors["yellow"])
            self.screen.blit(FPS_str, FPS_RECT)
        else:
            FPS_str = self.font.render(str(int(FPS)), True, self.colors["green"])
            self.screen.blit(FPS_str, FPS_RECT)

    def author(self):
        """
        Display the authors' names.
        """
        author_name = self.font.render("Created by Amir, Rassul, Kaminur and Alima", True, (255, 255, 255))
        rect = pygame.Rect(285, 660, 40, 10)
        self.screen.blit(author_name, rect)

    def play_sounds(self):
        """
        Play sounds during gameplay.
        """
        if self.sounds_list:
            if round(self.score, 2) % 10 == 0 and self.score and self.active:
                self.sounds["10_score"].play()
                return
            if round(self.score, 2) % 5 == 0 and self.score and self.active:
                self.sounds["5_score"].play()

    def game_over_sound_play(self):
        """
        Play a random game over sound.
        """
        sound = self.game_over_sounds[random.randint(1, len(self.game_over_sounds_list))]
        sound.play()

    def change_skin(self):
        """
        Change the bird's skin.
        """
        skins = list(map(lambda x: pygame.transform.scale(x, (300, 150)), self.skins[:]))

        back_button_rect = pygame.Rect(30, 50, 100, 45)
        next_skin_button_rect = pygame.Rect(150, 300, 100, 50)
        prev_skin_button_rect = pygame.Rect(750, 300, 100, 50)
        ok_button_rect = pygame.Rect(420, 500, 150, 75)

        clicked = False

        while self.skins_trigger:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.show_background()

            self.author()
            self.move_location(0.1)

            pygame.draw.rect(self.screen, (128, 128, 128, 128), (150, 90, 700, 500), border_radius=10)
            back_button_flipped = pygame.transform.flip(self.back_button["pressed"], True, True)

            self.screen.blit(self.back_button["non pressed"], back_button_rect)
            self.screen.blit(back_button_flipped, prev_skin_button_rect)
            self.screen.blit(self.back_button["pressed"], next_skin_button_rect)

            self.screen.blit(self.ok_button, ok_button_rect)

            self.screen.blit(skins[self.selected_skin_index], (350, 250))

            mouse_pos = pygame.mouse.get_pos()

            if back_button_rect.collidepoint(mouse_pos):
                self.screen.blit(self.back_button["pressed"], back_button_rect)
                if pygame.mouse.get_pressed()[0] and not clicked:
                    self.skins_trigger = False
                    self.menu_trigger = True

            if prev_skin_button_rect.collidepoint(mouse_pos):
                prev_skin_button_flipped = pygame.transform.flip(self.back_button["non pressed"], True, True)
                self.screen.blit(prev_skin_button_flipped, prev_skin_button_rect)
                if pygame.mouse.get_pressed()[0] and not clicked:
                    self.selected_skin_index -= 1
                    if self.selected_skin_index < 0:
                        self.selected_skin_index = len(skins) - 1
                    clicked = True

            if next_skin_button_rect.collidepoint(mouse_pos):
                self.screen.blit(self.back_button["pressed"], next_skin_button_rect)
                if pygame.mouse.get_pressed()[0] and not clicked:
                    self.selected_skin_index += 1
                    if self.selected_skin_index > len(skins) - 1:
                        self.selected_skin_index = 0
                    clicked = True

            if ok_button_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (112, 128, 144), ok_button_rect, border_radius=25)
                self.screen.blit(self.ok_button, ok_button_rect)
                if pygame.mouse.get_pressed()[0] and not clicked:
                    self.skins_trigger = False
                    self.bird = self.skins[self.selected_skin_index]
                    clicked = True

            if not pygame.mouse.get_pressed()[0]:
                clicked = False

            self.clock.tick(300)
            pygame.display.flip()
