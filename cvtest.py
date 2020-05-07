import cv2
import numpy as np

from auto.lkas import get_steering_angle

angle, frame = get_steering_angle('./auto/train_data/train_data_narrow/160.png')

print(angle)

frame.show()