import sys
from car.car import Car

car = Car()

car.move_angle(int(sys.argv[1]))
