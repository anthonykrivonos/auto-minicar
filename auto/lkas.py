import cv2
import numpy as np
import sys
from os.path import join, dirname
sys.path.append(join(dirname(__file__), '..'))

from auto.frame import Frame, Filter, Region, WhiteBalance

"""
Utility Functions for Lane Keeping Assist System (LKAS)
"""

def _get_steering_angle(lane_img, lane_lines):
    height, width, _ = lane_img.shape
    x_offset, y_offset = 0, 0

    num_lanes = len(lane_lines)

    if num_lanes == 1:
        # One visible lane line
        x1, _, x2, _ = lane_lines[0][0]
        x_offset = x2 - x1
        y_offset = int(height / 2)
    elif num_lanes == 2:
        # Two visible lane lines
        _, _, left_x2, _ = lane_lines[0][0]
        _, _, right_x2, _ = lane_lines[1][0]
        x_offset = int((left_x2 + right_x2) / 2 - width / 2)
        y_offset = int(height / 2)

    if y_offset != 0:
        steering_angle = np.arctan(x_offset / y_offset)
    else:
        steering_angle = 0

    # Convert to degrees
    steering_angle *= (180 / np.pi)

    # Bound to range
    steering_angle = min(89.99, max(-89.99, steering_angle))

    return steering_angle


def _get_heading_line(width, height, steering_angle_deg):
    assert(steering_angle_deg > -90 and steering_angle_deg < 90)
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 - height / 2 / np.tan((steering_angle_deg + 90) * np.pi / 180))
    y2 = int(height / 2)

    return [[x1, y1, x2, y2]]


def _stabilize_steering_angle(curr_steering_angle, new_steering_angle, max_angle_deviation):
    """
    Using last steering angle to stabilize the steering angle
    if new angle is too different from current angle,
    only turn by max_angle_deviation degrees
    """
    angle_deviation = new_steering_angle - curr_steering_angle
    if abs(angle_deviation) > max_angle_deviation:
        stabilized_steering_angle = int(curr_steering_angle + max_angle_deviation * angle_deviation / abs(angle_deviation))
    else:
        stabilized_steering_angle = new_steering_angle
    return stabilized_steering_angle


def get_steering_angle(cv2_image, curr_steering_angle = 0, stabilize = False, max_angle_deviation_two_lines=15, max_angle_deviation_one_lane=30, tape_color=[105, 157, 252], white_balance=None):
    frame = Frame(cv2_image)

    # Change to HSV
    frame.add(Filter.HSV)

    # Lift the tape color from the image
    frame.add(Filter.COLOR_DETECT, color=tape_color, white_balance=white_balance)

    # Detect the edges of the blue blobs
    frame.add(Filter.EDGE_DETECTION)

    # Isolate the bottom region
    frame.add(Filter.REGION_ISO, region=Region.BOTTOM)

    # Detect lanes in the image
    frame.add(Filter.LANE_DETECTION, overlay_layer=0)

    # Find the steering angle
    img, lanes, _ = frame.top()
    steering_angle = _get_steering_angle(img, lanes)

    # Stabilize the steering angle
    if stabilize:
        num_lanes = len(lanes)
        max_angle_deviation = max_angle_deviation_two_lines if num_lanes == 2 else max_angle_deviation_one_lane
        steering_angle = _stabilize_steering_angle(curr_steering_angle, steering_angle, max_angle_deviation)

    # Draw heading line
    height, width, _ = img.shape
    heading_line = _get_heading_line(width, height, steering_angle)
    frame.add(Filter.LINES, lines=[heading_line])

    if len(lanes) == 0:
        steering_angle = None

    return steering_angle, frame
