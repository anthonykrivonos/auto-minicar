import cv2
import numpy as np
from sys import argv

from auto.camera import get_single_frame
from auto.lkas import get_steering_angle

img = get_single_frame()

angle, frame = get_steering_angle(img)

print(angle)

layer_idx = int(argv[1]) if len(argv) > 1 else -1
frame.show(layer_idx)
