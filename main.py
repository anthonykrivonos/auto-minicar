from util.controller import Controller
from util.audio import play_sound, speak
from util.networking import get_device_ip

# Notify the operator of the device IP
# -> instead, just ssh pi@raspberrypi.local
# notify(get_device_ip())

INDOOR_BLUE_COLOR = [105, 157, 252]
OUTDOOR_BLUE_COLOR = [0, 192, 250]

# Play sounds
play_sound("startup.mp3")
speak("Revving the car engines", fail = True)

# Start controller
tape_color = OUTDOOR_BLUE_COLOR
controller = Controller(tape_color=tape_color, speak=True, display_feed=True)
controller.run_event_loop()
