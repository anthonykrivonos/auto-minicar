import cv2
from sys import argv
from time import sleep

from auto.camera import get_single_frame
from auto.lkas import get_steering_angle
from auto.frame import WhiteBalance

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
white_balance = WhiteBalance.TUNGSTEN

# Layer index
layer_idx = int(argv[1]) if len(argv) > 1 else -1

fbf = len(argv) > 2 and argv[2] == 'fbf'
video = len(argv) > 2 and argv[2] == 'video'
single = len(argv) == 2 or (len(argv) == 3 and argv[2].isdigit())

TRAIN_DATA = 'train_data_narrow'
# TRAIN_DATA = 'train_data_indoor'

if single:
    # Get the frame
    idx = int(argv[2]) if len(argv) > 2 else 1
    if idx == 0:
        img = get_single_frame()
        print('captured image')
    else:
        print('image %d.png' % idx, end='\r')
        img = cv2.imread('auto/train_data/%s/%d.png' % (TRAIN_DATA, idx))

    # Get the steering angle
    angle, frame = get_steering_angle(img, stabilize=False, tape_color=tape_color, white_balance=white_balance)

    # Show the calculated frame
    layer_idx = int(argv[1]) if len(argv) > 1 else -1
    frame.show(layer_idx)

if fbf or video:
    # Run through all images
    curr_steering_angle = 0
    i = 1
    while True:
        img = cv2.imread('auto/train_data/%s/%d.png' % (TRAIN_DATA, i))
        if img is None:
            break
        print('image %d.png' % i, end='\r')

        # Get the steering angle
        angle, frame = get_steering_angle(img, curr_steering_angle=curr_steering_angle, stabilize=True, tape_color=tape_color, white_balance=white_balance)
        curr_steering_angle = angle

        # Show the calculated frame
        frame.show(layer_idx, 1 if video else 0)
        if video:
            sleep(0.1)
        i += 1
    print('')
