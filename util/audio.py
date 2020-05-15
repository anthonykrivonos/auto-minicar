import sys, os
from os import mkdir
from os.path import join, dirname, exists
from gtts import gTTS
from time import time
sys.path.append(join(dirname(__file__), '..'))

import pygame

def play_sound(sound):
    pygame.mixer.init()
    pygame.mixer.music.set_volume(100.0)
    pygame.mixer.music.load(join(dirname(__file__), "sounds/" + sound))
    pygame.mixer.music.play()

def speak(text, slow = False, delete = True, verbose = True, fail = False):
    if fail:
        return
    # Print the output if required
    if verbose:
        print("SPOKE: " + text)
    # Create the speech object
    speech = gTTS(text=text, lang="en", slow=slow)
    # Create a filename and file location
    temp_dir = join(dirname(__file__), "sounds/tmp")
    if not exists(temp_dir):
        mkdir(temp_dir)
    filename = "_".join(text.lower().split(" "))[:10] + "_" + str(int(time())) + ".mp3"
    filepath = join(temp_dir, filename)
    try:
        # Save the text-to-speech output
        speech.save(filepath)
        # Play the output
        play_sound("tmp/" + filename)
        # Delete the output if necessary
        if delete:
            os.remove(filepath)
    except Exception as e:
        print("SPEAK ERROR: %s" % e)
    
    # Return the original filename
    return filename
