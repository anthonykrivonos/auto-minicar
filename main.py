from util.controller import Controller
from util.audio import play_sound, speak
from util.networking import get_device_ip
from util.notification import notify

# Notify the operator of the device IP
# -> instead, just ssh pi@raspberrypi.local
# notify(get_device_ip())

# Play sounds
play_sound("startup.mp3")
speak("Revving the car engines")

# Start controller
controller = Controller()
controller.run_event_loop()
