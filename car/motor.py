import sys
import numpy as np
from os.path import join, dirname

import atexit
from adafruit_motorkit import MotorKit

from auto.lkas import get_steering_angle

sys.path.append(join(dirname(__file__), '..'))

# Movement speeds
GO_DEFAULT = 0.95
STOP = 0.0

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

    def __init__(self, car=MotorKit(),  go=GO_DEFAULT, double_stop=DOUBLE_STOP_DEFAULT):
        # Car instance
        self.car = car
        self.go = go
        self.angle = 0
        self.double_stop = double_stop

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
        print("Achieving speed %f" % speed)
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
        motors = [ self.car.motor1, self.car.motor2, self.car.motor3, self.car.motor4]
        for i, speed in enumerate(speeds):
            self.move(speed, motors[i])

    def move_angle(self, angle):
        self.go = MAX_SPEED
        if abs(angle) < 5:
            self.move(self.go, self.car.motor1, self.car.motor2, self.car.motor3, self.car.motor4)
            return
        self.angle = angle
        left_bias = angle > 0
        angle = abs(angle)
        
        # Good values
        # 0-30:
        #   1 .6 1 -1
        # 30-60:
        #   1 0 1 0
        # 60-80:
        #   1 -.6 1 -.6
        # 80-90:
        #   1 0 1 -.6
        fo_speed = MIN_SPEED if angle <= 30 else -MIN_SPEED if (angle > 60 and angle <= 80) else 0
        bo_speed = 0 if (angle > 30 and angle <= 60) else -MAX_SPEED if angle <= 30 else -MIN_SPEED

        front_bias_m  = self.car.motor1 if left_bias else self.car.motor2
        front_other_m = self.car.motor2 if left_bias else self.car.motor1
        back_bias_m   = self.car.motor3 if left_bias else self.car.motor4
        back_other_m  = self.car.motor4 if left_bias else self.car.motor3
        
        print("Angle: %f | fb: %f, fo: %f, bb: %f, bo: %f" % (self.angle, self.go, fo_speed, self.go, bo_speed))

        self.move(self.go, front_bias_m, back_bias_m)
        self.move(fo_speed, front_other_m)
        self.move(bo_speed, back_other_m)

    def move_lkas(self, img):
        current_angle = self.angle
        next_angle, frame = get_steering_angle(img, current_angle)
        self.move_angle(next_angle)
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
