import sys
from car.motor import Motor
from time import sleep

car = Motor()

car.move_angle(int(sys.argv[1]))
