import os
from pathlib import Path


root = Path(os.getcwd())

icon = root/"images"/"menu_pick_2.jpg"

skins = root/"images"/"skins"
main_skin = skins/"pterodactyl.png"


sounds = root/"sounds"
in_game_sounds = sounds/"in_game_sounds"
game_over_sounds = sounds/"game_over_sounds"
theme = sounds/"theme"/"music.mp3"


level_images = root/"images"/"level"
backgrounds = level_images/"locations"
obstacle = level_images/"pipe.png"
menu_image = root/"images"/"menu_pick_2.jpg"

