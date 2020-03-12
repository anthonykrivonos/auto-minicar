import sys
from os.path import join, dirname
sys.path.append(join(dirname(__file__), '..'))

import atexit
from adafruit_motorkit import MotorKit

# Movement speeds
GO_DEFAULT = 0.8
STOP = 0.0
SPEEDS = [0.6, 0.7, 0.8, 0.9, 0.95]

# Stop on two wheels when turning?
DOUBLE_STOP_DEFAULT = True

class Motor:

    def __init__(self, car=MotorKit(),  go=GO_DEFAULT, double_stop=DOUBLE_STOP_DEFAULT):
        # Car instance
        self.car = car
        self.go = go
        self.double_stop = double_stop

        atexit.register(self.stop_all)

    ##
    # Reusables
    ##

    def move(self, speed, *motors):
        for motor in motors:
            cur_motor_idx = SPEEDS.index(abs(self.go))
            new_motor_idx = SPEEDS.index(abs(speed))
            incrementer = -1 if cur_motor_idx > new_motor_idx else 1
            while cur_motor_idx != new_motor_idx:
                motor.throttle = SPEEDS[cur_motor_idx] * (1 if speed > 0 else -1)
                cur_motor_idx += incrementer
            motor.throttle = SPEEDS[cur_motor_idx] * (1 if speed > 0 else -1)

    def correct(self):
        self.move(self.car.motor1.throttle, self.car.motor1) if self.car.motor1.throttle != STOP else self.stop(self.car.motor1)
        self.move(self.car.motor2.throttle, self.car.motor2) if self.car.motor2.throttle != STOP else self.stop(self.car.motor2)
        self.move(self.car.motor3.throttle, self.car.motor3) if self.car.motor3.throttle != STOP else self.stop(self.car.motor3)
        self.move(self.car.motor4.throttle, self.car.motor4) if self.car.motor4.throttle != STOP else self.stop(self.car.motor4)

    def double_correct(self):
        # Fixes motor latency glitch
        self.correct()
        self.correct()

    def stop(self, *motors):
        for motor in motors:
            motor.throttle = STOP

    def stop_all(self):
        self.stop(self.car.motor1, self.car.motor2, self.car.motor3, self.car.motor4)

    def reset(self):
        self.go = GO_DEFAULT
        self.double_stop = DOUBLE_STOP_DEFAULT

    def change_speed(self, mag_int):
        old_go = self.go
        new_go = SPEEDS[max(0, min(len(SPEEDS) - 1, SPEEDS.index(abs(old_go)) + mag_int))]
        new_go = new_go if old_go >= 0 else -new_go
        if old_go != new_go:
            self.move(new_go, self.car.motor1) if self.car.motor1.throttle != STOP else self.stop(self.car.motor1)
            self.move(new_go, self.car.motor2) if self.car.motor2.throttle != STOP else self.stop(self.car.motor2)
            self.move(new_go, self.car.motor3) if self.car.motor3.throttle != STOP else self.stop(self.car.motor3)
            self.move(new_go, self.car.motor4) if self.car.motor4.throttle != STOP else self.stop(self.car.motor4)
            self.go = new_go
        else:
            self.double_correct()

    def move_forward(self):
        self.go = abs(self.go)
        self.move(self.go, self.car.motor1, self.car.motor2, self.car.motor3, self.car.motor4)

    def move_backward(self):
        self.go = -abs(self.go)
        self.move(self.go, self.car.motor1, self.car.motor2, self.car.motor3, self.car.motor4)

    def move_left(self):
        self.move(self.go, self.car.motor2, self.car.motor4)
        self.stop(self.car.motor1)
        self.move(self.go, self.car.motor3) if not self.double_stop else self.stop(self.car.motor3)

    def move_right(self):
        self.move(self.go, self.car.motor1, self.car.motor3)
        self.stop(self.car.motor2)
        self.move(self.go, self.car.motor4) if not self.double_stop else self.stop(self.car.motor4)

    def toggle_double_stop(self, double_stop=None):
        self.double_stop = double_stop if double_stop is not None else (not self.double_stop)
