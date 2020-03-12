from util.controller import Controller
from util.audio import play_sound

# Play sound
play_sound("startup.mp3")

# Start controller
controller = Controller()
controller.run_event_loop()
