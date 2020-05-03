from util.controller import Controller
from util.audio import play_sound, speak

# Play sounds
play_sound("startup.mp3")
speak("Revving the car engines")

# Start controller
controller = Controller()
controller.run_event_loop()
