import sys
import numpy as np
from os.path import join, dirname
from time import sleep

import atexit
from adafruit_motorkit import MotorKit

from auto.lkas import get_steering_angle

sys.path.append(join(dirname(__file__), '..'))

# Movement speeds
GO_DEFAULT = 0.95
STOP = 0.0

# RGB Colors
DEFAULT_TAPE_COLOR = [105, 157, 252]

# Limits
MIN_SPEED = 0.7
MAX_SPEED = 0.95
MAX_ANGLE = 90  # in degrees

# Car dimensions
CAR_DIMS = {
    'WHEELBASE_CM': 11.43,  # height from front track to back track
    'TRACK_CM': 10.16       # width from one wheel to another in the same track
}

# Stop on two wheels when turning?
DOUBLE_STOP_DEFAULT = True

# Wheels 1, 2, 3, 4 -> top-left, top-right, bottom-left, bottom-right

class Motor:

    def __init__(self, car=MotorKit(),  go=GO_DEFAULT, double_stop=DOUBLE_STOP_DEFAULT, tape_color = DEFAULT_TAPE_COLOR):
        # Car instance
        self.car = car
        self.go = go
        self.angle = 0
        self.double_stop = double_stop
        self.tape_color = tape_color

        for motor in [ self.car.motor1, self.car.motor2, self.car.motor3, self.car.motor4]:
            motor.throttle = 0

        atexit.register(self.stop_all)

    ##
    # Reusables
    ##

    def move(self, speed, *motors):
        INCREMENT = 0.1
        sign = 1 if speed > 0 else -1
        if speed == 0:
            return self.stop(*motors)
        speed = min(MAX_SPEED, max(MIN_SPEED, abs(speed))) * sign
        up_to_speed = [ False for _ in range(len(motors)) ]
        while not all(up_to_speed):
            for i, motor in enumerate(motors):
                if not up_to_speed[i]:
                    new_throttle = motor.throttle
                    new_throttle += (1 if new_throttle < speed else -1) * INCREMENT
                    if abs(abs(new_throttle) - abs(speed)) < INCREMENT or abs(new_throttle) > MAX_SPEED:
                        motor.throttle = speed
                    else:
                        motor.throttle = new_throttle
                    if motor.throttle == speed:
                        up_to_speed[i] = True

    def capture_in_order(self):
        return [ self.car.motor1.throttle, self.car.motor2.throttle, self.car.motor3.throttle, self.car.motor4.throttle ]

    def correct(self):
        self.move(self.car.motor1.throttle, self.car.motor1) if self.car.motor1.throttle != STOP else self.stop(self.car.motor1)
        self.move(self.car.motor2.throttle, self.car.motor2) if self.car.motor2.throttle != STOP else self.stop(self.car.motor2)
        self.move(self.car.motor3.throttle, self.car.motor3) if self.car.motor3.throttle != STOP else self.stop(self.car.motor3)
        self.move(self.car.motor4.throttle, self.car.motor4) if self.car.motor4.throttle != STOP else self.stop(self.car.motor4)

    def stop(self, *motors):
        for motor in motors:
            motor.throttle = STOP

    def stop_all(self):
        self.angle = 0
        self.stop(self.car.motor1, self.car.motor2, self.car.motor3, self.car.motor4)

    def reset(self):
        self.go = GO_DEFAULT
        self.double_stop = DOUBLE_STOP_DEFAULT

    def change_speed(self, mag_int):
        dgo = mag_int / 10
        new_go = max(MIN_SPEED, min(MAX_SPEED, self.go + dgo))
        if self.go != new_go:
            self.move(new_go, self.car.motor1) if self.car.motor1.throttle != STOP else self.stop(self.car.motor1)
            self.move(new_go, self.car.motor2) if self.car.motor2.throttle != STOP else self.stop(self.car.motor2)
            self.move(new_go, self.car.motor3) if self.car.motor3.throttle != STOP else self.stop(self.car.motor3)
            self.move(new_go, self.car.motor4) if self.car.motor4.throttle != STOP else self.stop(self.car.motor4)
            self.go = new_go

    def move_speeds(self, speeds):
        motors = [ self.car.motor1, self.car.motor2, self.car.motor3, self.car.motor4 ]
        for i, speed in enumerate(speeds):
            self.move(speed, motors[i])

    def move_angle(self, angle):
        self.go = abs(self.go)
        if abs(angle) < 3:
            self.move(self.go, self.car.motor1, self.car.motor2, self.car.motor3, self.car.motor4)
            return
        self.angle = angle
        right_turn = angle > 0
        angle = abs(angle)

        ninety_deg_sec = 2.6
        turn_duration = np.round(ninety_deg_sec * (angle / 90), 2)

        prev_speeds = self.capture_in_order()

        print("Rotating %2.2fdeg" % angle)
        self.stop_all()
        if right_turn:
            self.move(self.go, self.car.motor1, self.car.motor3)
        else:
            self.move(self.go, self.car.motor2, self.car.motor4)

        sleep(turn_duration)
        self.move_speeds(prev_speeds)

    def move_lkas(self, img):
        current_angle = self.angle
        next_angle, frame = get_steering_angle(img, current_angle, tape_color=self.tape_color)
        if next_angle is not None:
            print("Rotating %1.4fdeg" % next_angle)
            self.move_angle(next_angle)
        else:
            print("Stopping car")
            self.stop_all()
        return frame.top()[0]

    def move_forward(self):
        self.angle = 0
        self.go = abs(self.go)
        self.move(self.go, self.car.motor1, self.car.motor2, self.car.motor3, self.car.motor4)

    def move_backward(self):
        self.angle = 0
        self.go = -abs(self.go)
        self.move(self.go, self.car.motor1, self.car.motor2, self.car.motor3, self.car.motor4)

    def move_left(self):
        self.angle = -MAX_ANGLE
        self.move(self.go, self.car.motor2, self.car.motor4)
        self.stop(self.car.motor1)
        self.move(self.go, self.car.motor3) if not self.double_stop else self.stop(self.car.motor3)

    def move_right(self):
        self.angle = MAX_ANGLE
        self.move(self.go, self.car.motor1, self.car.motor3)
        self.stop(self.car.motor2)
        self.move(self.go, self.car.motor4) if not self.double_stop else self.stop(self.car.motor4)

    def toggle_double_stop(self, double_stop=None):
        self.double_stop = double_stop if double_stop is not None else (not self.double_stop)
