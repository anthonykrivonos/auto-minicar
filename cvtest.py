import cv2
import numpy as np
from sys import argv
from time import sleep

from auto.camera import get_single_frame
from auto.lkas import get_steering_angle

"""
Abstract: Use this for testing CV functions.
Examples:
    To get the last frame of the 4th image:
    python3 cvtest.py -1 4
    
    For frame-by-frame:
    python3 cvtest.py -1 fbf
    
    For video:
    python3 cvtest.py -1 video
"""

# Tape colors
INDOOR_BLUE_COLOR = [105, 157, 252]
OUTDOOR_BLUE_COLOR = [54, 179, 254]

tape_color = INDOOR_BLUE_COLOR

# Layer index
layer_idx = int(argv[1]) if len(argv) > 1 else -1

fbf = len(argv) > 2 and argv[2] == 'fbf'
video = len(argv) > 2 and argv[2] == 'video'
single = len(argv) == 2 or (len(argv) == 3 and argv[2].isdigit())

if single:
    # Get the frame
    idx = int(argv[2]) if len(argv) > 2 else 1
    if idx == 0:
        img = get_single_frame()
        print('captured image')
    else:
        print('image %d.png' % idx, end='\r')
        img = cv2.imread('auto/train_data/train_data_indoor/%d.png' % idx)

    # Get the steering angle
    angle, frame = get_steering_angle(img, stabilize=False, tape_color=tape_color)

    # Show the calculated frame
    layer_idx = int(argv[1]) if len(argv) > 1 else -1
    frame.show(layer_idx)

if fbf or video:
    # Run through all images
    for i in range(1, 87):
        img = cv2.imread('auto/train_data/train_data_indoor/%d.png' % i)
        print('image %d.png' % i, end='\r')

        # Get the steering angle
        angle, frame = get_steering_angle(img, stabilize=False, tape_color=tape_color)

        # Show the calculated frame
        frame.show(layer_idx, 1 if video else 0)
        if video:
            sleep(0.1)
    print('')
