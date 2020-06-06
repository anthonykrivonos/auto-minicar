import sys
import numpy as np
from os.path import join, dirname
from time import sleep
from util.networking import send_to_socket
from util.timer import Timer
from car.car_constants import CAR_PORT, MIN_SPEED, MAX_SPEED, GO_DEFAULT, DOUBLE_STOP_DEFAULT, DEFAULT_TAPE_COLOR, STOP, MAX_ANGLE

import atexit

from auto.lkas import get_steering_angle

sys.path.append(join(dirname(__file__), '..'))

# Wheels 1, 2, 3, 4 -> top-left, top-right, bottom-left, bottom-right


class Car:

    def __init__(self, go=GO_DEFAULT, double_stop=DOUBLE_STOP_DEFAULT, tape_color = DEFAULT_TAPE_COLOR):
        # Car instance
        self.go = go
        self.angle = 0
        self.double_stop = double_stop
        self.tape_color = tape_color
        self.speeds = [ 0, 0, 0, 0 ]

        self.stop_all()
        atexit.register(self.stop_all)

    ##
    # Reusables
    ##

    def move_speeds(self, *speeds):
        speeds = list(speeds)
        def reassign_speeds(res):
            self.speeds = speeds
        send_to_socket(CAR_PORT, str(speeds)[1:-1], reassign_speeds)

    def move_ids(self, speed, *motor_ids):
        speeds = self.speeds.copy()
        for idx in motor_ids:
            id = idx - 1
            speeds[id] = speed
        self.move_speeds(*speeds)

    def move_all(self, speed):
        self.move_idx(speed, 1, 2, 3, 4)

    def stop(self, *motor_ids):
        self.move_ids(0, *motor_ids)

    def stop_all(self):
        self.angle = 0
        self.move_speeds(0, 0, 0, 0)

    def reset(self):
        self.go = GO_DEFAULT
        self.double_stop = DOUBLE_STOP_DEFAULT

    def change_speed(self, mag_int):
        dgo = mag_int / 10
        new_go = max(MIN_SPEED, min(MAX_SPEED, self.go + dgo))
        if self.go != new_go:
            self.move_ids(new_go, 1) if self.speeds[0] != STOP else self.stop(1)
            self.move_ids(new_go, 2) if self.speeds[1] != STOP else self.stop(2)
            self.move_ids(new_go, 3) if self.speeds[2] != STOP else self.stop(3)
            self.move_ids(new_go, 4) if self.speeds[3] != STOP else self.stop(4)
            self.go = new_go

    def move_angle(self, angle):
        self.go = abs(self.go)
        if abs(angle) < 3:
            self.move_all(self.go)
            return
        self.angle = angle
        right_turn = angle > 0
        angle = abs(angle)

        ninety_deg_sec = 2.6
        turn_duration = np.round(ninety_deg_sec * (angle / 90), 2)

        prev_speeds = self.speeds.copy()

        print("Rotating %2.2fdeg" % angle)
        self.stop_all()
        if right_turn:
            self.move_ids(self.go, 1, 3)
        else:
            self.move_ids(self.go, 2, 4)

        Timer(turn_duration, lambda: self.move_speeds(prev_speeds), timeout=True).start()

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
        self.move_ids(self.go, 1, 2, 3, 4)

    def move_backward(self):
        self.angle = 0
        self.go = -abs(self.go)
        self.move_ids(self.go, 1, 2, 3, 4)

    def move_left(self):
        self.angle = -MAX_ANGLE
        self.move_ids(self.go, 2, 4)
        self.stop(1)
        self.move_ids(self.go, 3) if not self.double_stop else self.stop(3)

    def move_right(self):
        self.angle = MAX_ANGLE
        self.move_ids(self.go, 1, 3)
        self.stop(2)
        self.move_ids(self.go, 4) if not self.double_stop else self.stop(4)

    def toggle_double_stop(self, double_stop=None):
        self.double_stop = double_stop if double_stop is not None else (not self.double_stop)
