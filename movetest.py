import sys
import numpy as np
from car.motor import Motor
from time import sleep

car = Motor()

speeds = [
    np.round(float(sys.argv[1]), 2),
    np.round(float(sys.argv[2]), 2),
    np.round(float(sys.argv[3]), 2),
    np.round(float(sys.argv[4]), 2)
]

car.move_speeds(speeds)
sleep(float(sys.argv[5]) if len(sys.argv) > 5 else 2)
