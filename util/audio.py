import sys, os
from os.path import join, dirname
from gtts import gTTS
from time import time
sys.path.append(join(dirname(__file__), '..'))

import pygame

def play_sound(sound):
    pygame.mixer.init()
    pygame.mixer.music.set_volume(100.0)
    pygame.mixer.music.load(join(dirname(__file__), "sounds/" + sound))
    pygame.mixer.music.play()

def speak(text, slow = False, delete = True, verbose = True):
    # Print the output if required
    if verbose:
        print("SPOKE: " + text)
    # Create the speech object
    speech = gTTS(text=text, lang="en", slow=slow)
    # Create a filename and file location
    filename = "_".join(text.lower().split(" "))[:10] + "_" + str(int(time())) + ".mp3"
    filepath = join(dirname(__file__), "sounds/tmp/" + filename)
    try:
        # Save the text-to-speech output
        speech.save(filepath)
        # Play the output
        play_sound(filename)
        # Delete the output if necessary
        if delete:
            os.remove(filepath)
    except:
        print("SPEAK ERROR")
    
    # Return the original filename
    return filename
