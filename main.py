from util.controller import Controller
from util.audio import play_sound, speak
from car.car_server import CarServer
from multiprocessing import Process
from time import sleep

# Notify the operator of the device IP
# from util.networking import get_device_ip
# -> instead, just ssh pi@raspberrypi.local
# notify(get_device_ip())

INDOOR_BLUE_COLOR = [105, 157, 252]
OUTDOOR_BLUE_COLOR = [0, 192, 250]

# Color of the current tape
tape_color = INDOOR_BLUE_COLOR

"""
1. Start car server in another process.
"""

Process(target=lambda: CarServer()).start()
sleep(2)

"""
2. Give startup feedback.
"""

# Play sounds
play_sound("startup.mp3")
speak("Revving the car engines", fail = True)

"""
3. Initialize the controller.
"""

controller = Controller(tape_color=tape_color, speak=True, display_feed=True)
controller.run_event_loop()
