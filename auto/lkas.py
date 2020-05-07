import cv2
import numpy as np
import sys
from os.path import join, dirname
sys.path.append(join(dirname(__file__), '..'))

from auto.frame import Frame, Filter, Region

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

    steering_angle = np.arctan(x_offset / y_offset) + 1.5708  # 90deg in radians

    return steering_angle


def _get_heading_line(width, height, steering_angle):
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 - height / 2 / np.tan(steering_angle))
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


def get_steering_angle(cv2_image, curr_steering_angle = 0, max_angle_deviation_two_lines=5, max_angle_deviation_one_lane=1):
    test_frame = Frame(cv2_image)

    # Change to HSV
    test_frame.add(Filter.HSV)

    # Lift the blue color from the image
    test_frame.add(Filter.COLOR_RANGE, color_range=([60, 40, 40], [150, 255, 255]))

    # Detect the edges of the blue blobs
    test_frame.add(Filter.EDGE_DETECTION)

    # Isolate the bottom region
    test_frame.add(Filter.REGION_ISO, region=Region.BOTTOM)

    # Detect lanes in the image
    test_frame.add(Filter.LANE_DETECTION, overlay_layer=0)

    # Find the steering angle
    img, lanes, _ = test_frame.top()
    steering_angle = _get_steering_angle(img, lanes)

    # Draw heading line (optional)
    # heading_line = _get_heading_line(width, height, steering_angle)
    # test_frame.add(Filter.LINES, lines=[heading_line])
    # test_frame.show()

    # Stabilize the steering angle
    num_lanes = len(lanes)
    max_angle_deviation = max_angle_deviation_two_lines if num_lanes == 2 else max_angle_deviation_one_lane

    steering_angle = _stabilize_steering_angle(curr_steering_angle, steering_angle, max_angle_deviation)

    # Convert to degrees
    steering_angle *= (180 / np.pi)

    return steering_angle
