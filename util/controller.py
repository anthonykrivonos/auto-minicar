import sys
from os.path import join, dirname
sys.path.append(join(dirname(__file__), '..'))

from enum import Enum
from time import sleep
from evdev import InputDevice, list_devices

from car.car import Car
from .audio import speak
from auto.camera import get_frame_by_frame

##
# Controller Polling
##

class Button(Enum):
    A = 305
    B = 306
    X = 304
    Y = 307
    LEFT_TRIGGER = 308
    RIGHT_TRIGGER = 309
    SELECT = 312
    START = 313

# Name of the controller device
DEFAULT_DEVICE_NAME = "Controller"

# Color of the lanes
DEFAULT_TAPE_COLOR = [105, 157, 252]

# FPS of frame by frame for recording
FBF_RECORD_FPS = 4

# FPS of frame by frame for autonomy
FBF_AUTONOMY_FPS = 16

class Controller:

    def __init__(self, speak=True, device_name=DEFAULT_DEVICE_NAME, display_feed=False, tape_color=DEFAULT_TAPE_COLOR):
        self.car = Car(tape_color=tape_color)
        self.device_name = device_name
        self.display_feed = display_feed
        self.speak = speak

        # Frame-by-frame objects
        self.fbf_record = get_frame_by_frame(fps=FBF_RECORD_FPS, write_to_disk=True)
        self.fbf_autonomy = get_frame_by_frame(fps=FBF_AUTONOMY_FPS, write_to_disk=False, on_capture=self.car.move_lkas, display_feed=display_feed)

    def _reset(self):
        self.car.stop_all()
        self.fbf_record.kill()
        self.fbf_autonomy.kill()

    ##
    # Handlers
    ##

    def released(self):
        self.car.stop_all()

    def up_pressed(self):
        self.car.move_forward()

    def down_pressed(self):
        self.car.move_backward()

    def left_pressed(self):
        self.car.move_left()

    def right_pressed(self):
        self.car.move_right()

    def a_pressed(self):
        if self.fbf_record.is_running:
            speak("Stopped recording", fail = not self.speak)
            self.car.stop_all()
            self.fbf_record.kill()
            self.fbf_record = get_frame_by_frame(fps=FBF_RECORD_FPS, write_to_disk=True)
        else:
            speak("Started recording", fail = not self.speak)
            self.fbf_record.start()

    def b_pressed(self):
        self.car.stop_all()

    def x_pressed(self):
        pass

    def y_pressed(self):
        self.car.toggle_double_stop()

    def left_trigger_pressed(self):
        self.car.change_speed(-1)

    def right_trigger_pressed(self):
        self.car.change_speed(1)

    def select_pressed(self):
        self.car.stop_all()
        self.car.reset()

    def start_pressed(self):
        if self.fbf_autonomy.is_running:
            speak("Stopped elkass", fail = not self.speak) # LKAS
            self.car.stop_all()
            self.fbf_autonomy.kill()
            self.fbf_autonomy = get_frame_by_frame(fps=FBF_AUTONOMY_FPS, write_to_disk=False, on_capture=self.car.move_lkas, display_feed=self.display_feed)
        else:
            speak("Started elkass", fail = not self.speak) # LKAS
            self.fbf_autonomy.start()

    def run_event_loop(self, timeout_s=60, retry_s=5):
        # Find gamepad
        gamepad = None
        while gamepad is None:
            devices = [ InputDevice(path) for path in list_devices() ]
            for device in devices:
                if device.name in self.device_name:
                    gamepad = device
                    break
            if gamepad is None:
                speak("Could not find gamepad, trying again", fail = not self.speak)
                sleep(retry_s)
                timeout_s -= retry_s
                if timeout_s < 0:
                    speak("Never found gamepad. Exiting.", fail = not self.speak)
                    self._reset()
                    return
            else:
                speak("Gamepad found.", fail = not self.speak)

        while True:
            try:
                for event in gamepad.read_loop():
                    if event.value is 1:
                        # Button
                        try:
                            button = Button(event.code)
                        except:
                            speak("Invalid button.", fail = not self.speak)
                            continue
                        if button is Button.A:
                            self.a_pressed()
                        elif button is Button.B:
                            self.b_pressed()
                        elif button is Button.X:
                            self.x_pressed()
                        elif button is Button.Y:
                            self.y_pressed()
                        elif button is Button.LEFT_TRIGGER:
                            self.left_trigger_pressed()
                        elif button is Button.RIGHT_TRIGGER:
                            self.right_trigger_pressed()
                        elif button is Button.SELECT:
                            self.select_pressed()
                        elif button is Button.START:
                            self.start_pressed()
                        print(button)

                    elif event.type is 3:
                        # Directions
                        if event.value is 128:
                            # Released
                            self.released()
                            print("RELEASED")
                        else:
                            # Pressed
                            if event.code is 0:
                                # Horizontal
                                if event.value is 0:
                                    # Left
                                    self.left_pressed()
                                    print("LEFT")
                                elif event.value is 255:
                                    # Right
                                    self.right_pressed()
                                    print("RIGHT")
                            else:
                                # Vertical
                                if event.value is 0:
                                    # Up
                                    self.up_pressed()
                                    print("UP")
                                elif event.value is 255:
                                    # Down
                                    self.down_pressed()
                                print("DOWN")
            except Exception as e:
                print("CAUGHT ERROR", e)
                self._reset()
                speak("Restarting...", fail = not self.speak)
                self.run_event_loop(timeout_s, retry_s)
                break
