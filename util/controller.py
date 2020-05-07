import sys
from os.path import join, dirname
sys.path.append(join(dirname(__file__), '..'))

from enum import Enum
from time import sleep
from evdev import InputDevice, list_devices

from car.motor import Motor
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

# FPS of frame by frame imaging
FRAME_BY_FRAME_FPS = 4

class Controller:

    def __init__(self, car=None, device_name=DEFAULT_DEVICE_NAME):
        self.motor = Motor() if car is None else Motor(car)
        self.device_name = device_name
        self.motor.stop_all()
        self.motor.reset()
        self.frame_by_frame = get_frame_by_frame(fps=FRAME_BY_FRAME_FPS)

    def _reset(self):
        self.motor.stop_all()
        self.frame_by_frame.kill()

    ##
    # Handlers
    ##

    def released(self):
        self.motor.stop_all()

    def up_pressed(self):
        self.motor.move_forward()

    def down_pressed(self):
        self.motor.move_backward()

    def left_pressed(self):
        self.motor.move_left()

    def right_pressed(self):
        self.motor.move_right()

    def a_pressed(self):
        if self.frame_by_frame.is_running:
            self.frame_by_frame.kill()
            self.frame_by_frame = get_frame_by_frame(fps=FRAME_BY_FRAME_FPS, write_to_disk=True, on_capture=self.motor.move_lkas)
            speak("Stopped LKAS")
        else:
            self.frame_by_frame.start()
            speak("Started LKAS")

    def b_pressed(self):
        self.motor.stop_all()

    def x_pressed(self):
        pass

    def y_pressed(self):
        self.motor.toggle_double_stop()

    def left_trigger_pressed(self):
        self.motor.change_speed(-1)

    def right_trigger_pressed(self):
        self.motor.change_speed(1)

    def select_pressed(self):
        self.motor.stop_all()
        self.motor.reset()

    def start_pressed(self):
        if self.frame_by_frame.is_running:
            self.frame_by_frame.kill()
            self.frame_by_frame = get_frame_by_frame(fps=FRAME_BY_FRAME_FPS, write_to_disk=True)
            speak("Stopped recording")
        else:
            print("Starting fbf")
            self.frame_by_frame.start()
            speak("Started recording")

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
                speak("Could not find gamepad, trying again")
                sleep(retry_s)
                timeout_s -= retry_s
                if timeout_s < 0:
                    speak("Never found gamepad. Exiting.")
                    self._reset()
                    return
            else:
                speak("Gamepad found.")

        while True:
            try:
                for event in gamepad.read_loop():
                    if event.value is 1:
                        # Button
                        try:
                            button = Button(event.code)
                        except:
                            speak("Invalid button.")
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
                speak("Restarting...")
                self.run_event_loop(timeout_s, retry_s)
                break
