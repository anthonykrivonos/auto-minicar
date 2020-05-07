import cv2
import numpy as np
from enum import Enum
from os.path import realpath, join, dirname, exists

# Reference: https://towardsdatascience.com/deeppicar-part-4-lane-following-via-opencv-737dd9e47c96

class Filter(Enum):
    HSV = 0
    COLOR_RANGE = 1
    EDGE_DETECTION = 2
    REGION_ISO = 3
    LINE_DETECTION = 4
    LANE_DETECTION = 5
    LINES = 6


class Region(Enum):
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3


class Frame:

    def __init__(self, path, name="Frame"):
        img = self._load_img(path)
        self._outputs = [ img ]
        self._output_data = [ None ]
        self._filters = [ None ]
        self._name = name
        self._path = path
    
    def add(self, filter, color_range=None, bounds=(200, 400), region=Region.BOTTOM, overlay_layer=0, lines=[], color=(0, 0, 0)):
        _input, input_data, prev_filter = self.top()
        output = None
        output_data = None
        if filter == Filter.HSV:
            output = self._filter_hsv(_input)
        elif filter == Filter.COLOR_RANGE:
            output = self._filter_color_range(_input, color_range)
        elif filter == Filter.EDGE_DETECTION:
            output = self._filter_edge_detection(_input, bounds)
        elif filter == Filter.REGION_ISO:
            output = self._filter_region_isolation(_input, region)
        elif filter == Filter.LINE_DETECTION:
            output, output_data = self._filter_line_detection(_input, self._outputs[overlay_layer])
        elif filter == Filter.LANE_DETECTION:
            if prev_filter != Filter.LINE_DETECTION:
                _input, input_data, prev_filter = self.add(Filter.LINE_DETECTION)
            output, output_data = self._filter_lane_detection(_input, input_data, self._outputs[overlay_layer])
        elif filter == Filter.LINES:
            output = self._draw_lines(_input, lines, color)

        self._outputs.append(output)
        self._output_data.append(output_data)
        self._filters.append(filter)

        return output, output_data, filter

    def get(self, idx):
        return self._outputs[idx], self._output_data[idx], self._filters[idx]

    def bottom(self):
        return self.get(0)

    def top(self):
        return self.get(-1)

    def show(self, stage_idx = -1):
        output = self._outputs[stage_idx]
        cv2.imshow(self._name, output)
        cv2.waitKey(0)

    @staticmethod
    def _load_img(path):
        if path[0] != '/':
            path = join(dirname(realpath(__file__)), path)
        image = cv2.imread(path)
        return image

    @staticmethod
    def _filter_hsv(_input):
        return cv2.cvtColor(_input, cv2.COLOR_BGR2HSV)

    @staticmethod
    def _filter_color_range(_input, color_range):
        color_range = [ np.array(color) for color in color_range ]
        return cv2.inRange(_input, *color_range)

    @staticmethod
    def _filter_edge_detection(_input, bounds):
        return cv2.Canny(_input, *bounds)

    @staticmethod
    def _filter_region_isolation(_input, isolated_region):
        height, width = _input.shape
        mask = np.zeros_like(_input)

        if isolated_region == Region.TOP:
            edges = [ (0, 0), (width, 0), (width, height / 2), (0, height / 2) ]
        elif isolated_region == Region.RIGHT:
            edges = [ (width / 2, 0), (width, 0), (width, height), (width / 2, height ) ]
        elif isolated_region == Region.BOTTOM:
            edges = [ (0, height / 2), (width, height / 2), (width, height), (0, height) ]
        else:
            edges = [ (0, 0), (width / 2, 0), (width / 2, height), (0, height) ]
        
        edges = np.array([edges], np.int32)
        cv2.fillPoly(mask, edges, 255)

        return cv2.bitwise_and(_input, mask)

    @staticmethod
    def _draw_lines(frame, lines, color):
        output = frame.copy()
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(output, (x1, y1), (x2, y2), color, 10)
        return output

    @staticmethod
    def _filter_line_detection(_input, output):
        lines = cv2.HoughLinesP(_input, 1, np.pi / 180, 10, np.array([]), minLineLength=4, maxLineGap=4)
        output = Frame._draw_lines(output, lines, (50, 205, 50))
        return output, lines

    @staticmethod
    def _filter_lane_detection(_input, lines, output):
        lane_lines = []
        if lines is None:
            return lane_lines

        _, width, _ = _input.shape
        left_fit = []
        right_fit = []

        boundary = 1/3
        left_region_boundary = width * (1 - boundary)
        right_region_boundary = width * boundary

        for line in lines:
            for x1, y1, x2, y2 in line:
                if x1 == x2:
                    continue
                fit = np.polyfit((x1, x2), (y1, y2), 1)
                slope = fit[0]
                intercept = fit[1]
                if slope < 0:
                    if x1 < left_region_boundary and x2 < left_region_boundary:
                        left_fit.append((slope, intercept))
                else:
                    if x1 > right_region_boundary and x2 > right_region_boundary:
                        right_fit.append((slope, intercept))

        def make_points(frame, line):
            height, width, _ = frame.shape
            slope, intercept = line
            y1 = height
            y2 = int(y1 * 1 / 2)

            x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
            x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
            return [[x1, y1, x2, y2]]

        left_fit_average = np.average(left_fit, axis=0)
        if len(left_fit) > 0:
            lane_lines.append(make_points(_input, left_fit_average))

        right_fit_average = np.average(right_fit, axis=0)
        if len(right_fit) > 0:
            lane_lines.append(make_points(_input, right_fit_average))

        output = Frame._draw_lines(output, lane_lines, (0, 255, 255))

        return output, lane_lines

def get_offset(lane_img, lane_lines):
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

    steering_angle = np.arctan(x_offset / y_offset) + 1.5708 # 90deg in radians

    return x_offset, y_offset, steering_angle


def get_heading_line(x_offset, y_offset, width, height, steering_angle):
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 - height / 2 / np.tan(steering_angle))
    y2 = int(height / 2)
    
    return [[ x1, y1, x2, y2 ]]


def stabilize_steering_angle(
          curr_steering_angle,
          new_steering_angle, 
          num_of_lane_lines, 
          max_angle_deviation_two_lines=5, 
          max_angle_deviation_one_lane=1):
    """
    Using last steering angle to stabilize the steering angle
    if new angle is too different from current angle, 
    only turn by max_angle_deviation degrees
    """
    if num_of_lane_lines == 2 :
        # if both lane lines detected, then we can deviate more
        max_angle_deviation = max_angle_deviation_two_lines
    else :
        # if only one lane detected, don't deviate too much
        max_angle_deviation = max_angle_deviation_one_lane
    
    angle_deviation = new_steering_angle - curr_steering_angle
    if abs(angle_deviation) > max_angle_deviation:
        stabilized_steering_angle = int(curr_steering_angle
            + max_angle_deviation * angle_deviation / abs(angle_deviation))
    else:
        stabilized_steering_angle = new_steering_angle
    return stabilized_steering_angle


def get_lane_lines(img_path):
    test_frame = Frame(img_path)

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

    # Find and and draw the heading line
    img, lanes, _ = test_frame.top()
    height, width, _ = img.shape
    x_offset, y_offset, steering_angle = get_offset(img, lanes)
    heading = get_heading_line(x_offset, y_offset, width, height, steering_angle)
    test_frame.add(Filter.LINES, lines=[heading])

    test_frame.show()


##
#   Test
##

get_lane_lines('train/train_data_narrow/61.png')