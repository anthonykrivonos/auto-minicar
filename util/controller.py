import sys
from os.path import join, dirname
sys.path.append(join(dirname(__file__), '..'))

from enum import Enum
from car.motor import Motor
from time import sleep
from evdev import InputDevice, list_devices

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

DEFAULT_DEVICE_NAME = "Controller"

class Controller:

    def __init__(self, car, device_name=DEFAULT_DEVICE_NAME):
        self.motor = Motor(car)
        self.device_name = device_name
        self.motor.stop_all()
        self.motor.reset()

    ##
    # Handlers
    ##

    def unpressed(self):
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
        pass

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
        pass

    def run_event_loop(self, timeout_s=60, retry_s=5):
        # Find gamepad
        gamepad = None
        while gamepad is None:
            devices = [ InputDevice(path) for path in list_devices() ]
            for device in devices:
                if device.name in DEVICE_NAME:
                    gamepad = device
                    break
            if gamepad is None:
                print("COULD NOT FIND GAMEPAD, TRYING AGAIN")
                sleep(retry_s)
                timeout_s -= retry_s
                if timeout_s < 0:
                    print("NEVER FOUND GAMEPAD. EXITING.")
                    return
            else:
                print("GAMEPAD FOUND")

        while True:
            try:
                for event in gamepad.read_loop():
                    if event.value is 1:
                        # Button
                        try:
                            button = Button(event.code)
                        except:
                            print("INVALID")
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
                            self.unpressed()
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
                print("RESTARTING...")
                sleep(retry_s)