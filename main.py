import atexit
import pygame
from adafruit_motorkit import MotorKit
from evdev import InputDevice, categorize, list_devices
from time import sleep
from enum import Enum

# Movement speeds
go = 0.8
GO_DEFAULT = 0.8
STOP = 0.0
SPEEDS = [ 0.6, 0.7, 0.8, 0.9, 0.95 ]

# Stop on two wheels when turning?
DOUBLE_STOP_DEFAULT = True
double_stop = DOUBLE_STOP_DEFAULT

# Car instance
car = MotorKit()

##
# Reusables
##

def move(speed, *motors):
    for motor in motors:
        cur_motor_idx = SPEEDS.index(abs(go))
        new_motor_idx = SPEEDS.index(abs(speed))
        incrementer = -1 if cur_motor_idx > new_motor_idx else 1
        while cur_motor_idx != new_motor_idx:
            motor.throttle = SPEEDS[cur_motor_idx] * (1 if speed > 0 else -1)
            cur_motor_idx += incrementer
        motor.throttle = SPEEDS[cur_motor_idx] * (1 if speed > 0 else -1)

def correct():
    move(car.motor1.throttle, car.motor1) if car.motor1.throttle != STOP else stop(car.motor1)
    move(car.motor2.throttle, car.motor2) if car.motor2.throttle != STOP else stop(car.motor2)
    move(car.motor3.throttle, car.motor3) if car.motor3.throttle != STOP else stop(car.motor3)
    move(car.motor4.throttle, car.motor4) if car.motor4.throttle != STOP else stop(car.motor4)
    
def double_correct():
    # Fixes motor latency glitch
    correct()
    correct()

def stop(*motors):
    for motor in motors:
        motor.throttle = STOP

def stop_all():
    stop(car.motor1, car.motor2, car.motor3, car.motor4)
    
def reset():
    global go
    global double_stop
    go = GO_DEFAULT
    double_stop = DOUBLE_STOP_DEFAULT
    
def change_speed(mag_int):
    global go
    old_go = go
    new_go = SPEEDS[max(0, min(len(SPEEDS) - 1, SPEEDS.index(abs(old_go)) + mag_int))]
    new_go = new_go if old_go >= 0 else -new_go
    if old_go != new_go:
        move(new_go, car.motor1) if car.motor1.throttle != STOP else stop(car.motor1)
        move(new_go, car.motor2) if car.motor2.throttle != STOP else stop(car.motor2)
        move(new_go, car.motor3) if car.motor3.throttle != STOP else stop(car.motor3)
        move(new_go, car.motor4) if car.motor4.throttle != STOP else stop(car.motor4)
        go = new_go
    else:
        double_correct()

##
# Handlers
##

def unpressed():
    stop_all()

def up_pressed():
    global go
    go = abs(go)
    move(go, car.motor1, car.motor2, car.motor3, car.motor4)

def down_pressed():
    global go
    go = -abs(go)
    move(go, car.motor1, car.motor2, car.motor3, car.motor4)

def left_pressed():
    global double_stop
    move(go, car.motor2, car.motor4)
    stop(car.motor1)
    move(go, car.motor3) if not double_stop else stop(car.motor3)

def right_pressed():
    global double_stop
    move(go, car.motor1, car.motor3)
    stop(car.motor2)
    move(go, car.motor4) if not double_stop else stop(car.motor4)

def a_pressed():
    pass

def b_pressed():
    stop_all()

def x_pressed():
    pass

def y_pressed():
    global double_stop
    double_stop = False if double_stop else True

def left_trigger_pressed():
    change_speed(-1)

def right_trigger_pressed():
    change_speed(1)

def select_pressed():
    stop_all()
    reset()

def start_pressed():
    pass

##
# At Exit
##

atexit.register(stop_all)

##
# Startup Sound
##

pygame.mixer.init()
pygame.mixer.music.set_volume(100.0)
pygame.mixer.music.load("/home/pi/dev/car/startup.mp3")
pygame.mixer.music.play()

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

DEVICE_NAME = "Controller"

def run_event_loop():
    stop_all()
    reset()
    gamepad = None
    while gamepad is None:
        devices = [ InputDevice(path) for path in list_devices() ]
        for device in devices:
            if device.name in DEVICE_NAME:
                gamepad = device
                break
        if gamepad is None:
            print("COULD NOT FIND GAMEPAD, TRYING AGAIN")
            sleep(5)
        else:
            print("GAMEPAD FOUND")
    for event in gamepad.read_loop():
        if event.value is 1:
            # Button
            try:
                button = Button(event.code)
            except:
                print("INVALID")
                continue
            if button is Button.A:
                a_pressed()
            elif button is Button.B:
                b_pressed()
            elif button is Button.X:
                x_pressed()
            elif button is Button.Y:
                y_pressed()
            elif button is Button.LEFT_TRIGGER:
                left_trigger_pressed()
            elif button is Button.RIGHT_TRIGGER:
                right_trigger_pressed()
            elif button is Button.SELECT:
                select_pressed()
            elif button is Button.START:
                start_pressed()
            print(button)
        elif event.type is 3:
            # Directions
            if event.value is 128:
                # Released
                unpressed()
                print("RELEASED")
            else:
                # Pressed
                if event.code is 0:
                    # Horizontal
                    if event.value is 0:
                        # Left
                        left_pressed()
                        print("LEFT")
                    elif event.value is 255:
                        # Right
                        right_pressed()
                        print("RIGHT")
                else:
                    # Vertical
                    if event.value is 0:
                        # Up
                        up_pressed()
                        print("UP")
                    elif event.value is 255:
                        # Down
                        down_pressed()
                    print("DOWN")
                    
while True:
    try:
        run_event_loop()
    except Exception as e:
        print("CAUGHT ERROR", e)
        sleep(2)
        print("RESTARTING...")