import cv2
import numpy as np
from sys import argv
from time import sleep

from auto.camera import get_single_frame
from auto.lkas import get_steering_angle
from auto.frame import WhiteBalance

# Tape colors
INDOOR_BLUE_COLOR = [105, 157, 252]
OUTDOOR_BLUE_COLOR = [100, 180, 250]

tape_color = OUTDOOR_BLUE_COLOR
white_balance = WhiteBalance.DAYLIGHT

# Layer index
layer_idx = int(argv[1]) if len(argv) > 1 else -1

curr_steering_angle = 0
while True:
    img = get_single_frame()

    if img is None:
        print("Camera not found")
        break

    # Get the steering angle
    angle, frame = get_steering_angle(img, curr_steering_angle=curr_steering_angle, stabilize=True, tape_color=tape_color, white_balance=white_balance)
    curr_steering_angle = angle

    # Show the calculated frame
    frame.show(layer_idx, 0)
