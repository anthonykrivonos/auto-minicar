import cv2
import numpy as np
from sys import argv

from auto.camera import get_single_frame
from auto.lkas import get_steering_angle

# Tape colors
BLUE_COLOR = [105, 157, 252]

# Get the frame
img = get_single_frame()

# Get the steering angle
angle, frame = get_steering_angle(img, stabilize=False, tape_color=BLUE_COLOR)

# Show the calculated frame
layer_idx = int(argv[1]) if len(argv) > 1 else -1
frame.show(layer_idx)
