import sys
from os.path import join, dirname
sys.path.append(join(dirname(__file__), '..'))

import pygame

def play_sound(sound):
    pygame.mixer.init()
    pygame.mixer.music.set_volume(100.0)
    pygame.mixer.music.load(join(dirname(__file__), "sounds/" + sound))
    pygame.mixer.music.play()