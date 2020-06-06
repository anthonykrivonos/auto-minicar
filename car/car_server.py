import sys
from os.path import join, dirname
from util.networking import open_socket
from car.car_constants import CAR_PORT, MIN_SPEED, MAX_SPEED

import atexit
from adafruit_motorkit import MotorKit

sys.path.append(join(dirname(__file__), '..'))

class CarServer:

    def __init__(self, car = MotorKit()):
        # Get car
        self.car = car
        # Turn off all motors
        for motor in [ self.car.motor1, self.car.motor2, self.car.motor3, self.car.motor4 ]:
            motor.throttle = 0
        # Open car socket
        print("Started car socket on port %d" % CAR_PORT)
        open_socket(CAR_PORT, self.__on_msg, self.__on_quit)
        atexit.register(self.__stop_all)

    def __on_msg(self, msg):
        speeds = [ float(msg.strip()) for msg in msg.split(",") ]
        self.__move_speeds(speeds)
        return msg

    def __on_quit(self):
        print("Closed car socket on port %d" % CAR_PORT)

    def __move(self, speed, *motors):
        if speed == 0:
            for motor in motors:
                motor.throttle = 0
            return
        INCREMENT = 0.1
        sign = 1 if speed > 0 else -1
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

    def __move_speeds(self, speeds):
        motors = [ self.car.motor1, self.car.motor2, self.car.motor3, self.car.motor4 ]
        for i, speed in enumerate(speeds):
            self.__move(speed, motors[i])

    def __stop_all(self):
        self.__move_speeds([0, 0, 0, 0])