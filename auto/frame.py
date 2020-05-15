import cv2
import sys, os
import numpy as np
from colorsys import rgb_to_hsv
from enum import Enum
from os.path import realpath, join, dirname, exists
sys.path.append(join(dirname(__file__), '..'))


# Reference: https://towardsdatascience.com/deeppicar-part-4-lane-following-via-opencv-737dd9e47c96

class Filter(Enum):
    HSV = 0
    COLOR_DETECT = 1
    EDGE_DETECTION = 2
    REGION_ISO = 3
    LINE_DETECTION = 4
    LANE_DETECTION = 5
    LINES = 6
    FLIP = 7


class Region(Enum):
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3


class Frame:
    """
    Wrapper around CV2 image for image processing and lane detection.
    """

    def __init__(self, img_or_path, name="Frame"):
        img, path = self._load_img(img_or_path)
        self._outputs = [img]
        self._output_data = [None]
        self._filters = [None]
        self._name = name
        self._path = path

    def add(self, filter, replace_idx=None, bounds=(200, 400), region=Region.BOTTOM, overlay_layer=0, lines=[],
            color=(0, 0, 0), flip_horizontal=True):
        if replace_idx is None:
            _input, input_data, prev_filter = self.top()
        else:
            _input, input_data, prev_filter = self.get(max(0, replace_idx))

        output = None
        output_data = None
        if filter == Filter.HSV:
            output = self._filter_hsv(_input)
        elif filter == Filter.COLOR_DETECT:
            output = self._filter_color_detect(_input, color)
        elif filter == Filter.EDGE_DETECTION:
            output = self._filter_edge_detection(_input, bounds)
        elif filter == Filter.REGION_ISO:
            output = self._filter_region_isolation(_input, region)
        elif filter == Filter.LINE_DETECTION:
            output, output_data = self._filter_line_detection(_input, self._outputs[overlay_layer])
        elif filter == Filter.LANE_DETECTION:
            if prev_filter != Filter.LINE_DETECTION:
                if replace_idx:
                    raise Exception('Cannot replace layer with Lane Detection if previous layer is not a Line Detection layer.')
                _input, input_data, prev_filter = self.add(Filter.LINE_DETECTION)
            output, output_data = self._filter_lane_detection(_input, input_data, self._outputs[overlay_layer])
        elif filter == Filter.LINES:
            output = self._draw_lines(_input, lines, color)
        elif filter == Filter.FLIP:
            output = self._filter_flip(_input, flip_horizontal)
        else:
            raise Exception("%s is not a valid Filter" % filter)

        if replace_idx is not None:
            self._outputs[replace_idx] = output
            self._output_data[replace_idx] = output_data
            self._filters[replace_idx] = filter
        else:
            self._outputs.append(output)
            self._output_data.append(output_data)
            self._filters.append(filter)

        return output, output_data, filter

    def replace(self, idx, filter, **kwargs):
        self.add(filter, replace_idx=idx, **kwargs)

    def get(self, idx):
        return self._outputs[idx], self._output_data[idx], self._filters[idx]

    def bottom(self):
        return self.get(0)

    def top(self):
        return self.get(-1)

    def show(self, stage_idx=-1, wait_key=0):
        output = self._outputs[stage_idx]
        cv2.imshow(self._name, output)
        cv2.waitKey(wait_key)

    @staticmethod
    def _load_img(img_or_path):
        if isinstance(img_or_path, str):
            path = img_or_path
            if path[0] != '/':
                path = join(os.getcwd(), path)
            print(path)
            image = cv2.imread(path)
        else:
            path = None
            image = img_or_path
        return image, path

    @staticmethod
    def _filter_hsv(_input):
        return cv2.cvtColor(_input, cv2.COLOR_BGR2HSV)

    @staticmethod
    def _filter_color_detect(_input, color):
        def get_color_range(rgb):
            rgb = np.array(rgb) / 255.
            hsv = rgb_to_hsv(*rgb)
            hue = hsv[0] * 179
            lower = np.array([max(0, hue - 5), hsv[1]*255 * 0.4, hsv[1]*255 * 0.2], np.int)
            upper = np.array([min(179, hue + 20), min(255, hsv[1]*255 * 1.2), min(255, hsv[1]*255 * 1.5)], np.int)
            print("initial: %d°, %d%%, %d%%" % (round(hsv[0]*360), round(hsv[1]*100), round(hsv[2]*100)))
            print("lower:   %d°, %d%%, %d%%" % (round(lower[0]*2), round(lower[1]/255*100), round(lower[2]/255*100)))
            print("upper:   %d°, %d%%, %d%%" % (round(upper[0]*2), round(upper[1]/255*100), round(upper[2]/255*100)))
            return lower, upper

        range = get_color_range(color)
        output = cv2.inRange(_input, *range)
        return output

    @staticmethod
    def _filter_edge_detection(_input, bounds):
        return cv2.Canny(_input, *bounds)

    @staticmethod
    def _filter_region_isolation(_input, isolated_region):
        height, width = _input.shape
        mask = np.zeros_like(_input)

        if isolated_region == Region.TOP:
            edges = [(0, 0), (width, 0), (width, height / 2), (0, height / 2)]
        elif isolated_region == Region.RIGHT:
            edges = [(width / 2, 0), (width, 0), (width, height), (width / 2, height)]
        elif isolated_region == Region.BOTTOM:
            edges = [(0, height / 2), (width, height / 2), (width, height), (0, height)]
        else:
            edges = [(0, 0), (width / 2, 0), (width / 2, height), (0, height)]

        edges = np.array([edges], np.int32)
        cv2.fillPoly(mask, edges, 255)

        return cv2.bitwise_and(_input, mask)

    @staticmethod
    def _filter_flip(_input, flip_horizontal):
        return cv2.flip(_input, 1 if flip_horizontal else 0)

    @staticmethod
    def _draw_lines(frame, lines, color):
        output = frame.copy()
        if lines is None:
            lines = []
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
            return _input, lane_lines

        _, width, _ = _input.shape
        left_fit = []
        right_fit = []

        boundary = 1 / 3
        left_region_boundary = width * (1 - boundary)
        right_region_boundary = width * boundary

        for line in lines:
            for x1, y1, x2, y2 in line:
                if x1 == x2:
                    continue
                fit = np.polyfit((x1, x2), (y1, y2), 1)
                slope = fit[0]
                intercept = fit[1]
                if slope < 0 and x1 < left_region_boundary and x2 < left_region_boundary:
                    left_fit.append((slope, intercept))
                elif slope > 0 and x1 > right_region_boundary and x2 > right_region_boundary:
                    right_fit.append((slope, intercept))

        def lines_intersect(a1, a2, b1, b2):
            det = (a2[0] - a1[0]) * (b2[1] - b1[1]) - (b2[0] - b1[0]) * (a2[1] - a1[1])
            if det == 0:
                return False
            lam = ((b2[1] - b1[1]) * (b2[0] - a1[0]) + (b1[0] - b2[0]) * (b2[1] - a1[1])) / det
            gamma = ((a1[1] - a2[1]) * (b2[0] - a1[0]) + (a2[0] - a1[0]) * (b2[1] - a1[1])) / det
            return (0 < lam and lam < 1) and (0 < gamma and gamma < 1)

        def make_points(frame, line):
            height, width, _ = frame.shape
            slope, intercept = line
            y1 = height
            y2 = int(y1 * 1 / 2)
            x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
            x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
            return [[x1, y1, x2, y2]]

        if len(left_fit) > 0:
            left_fit_average = np.average(left_fit, axis=0)
            left_line = make_points(_input, left_fit_average)
            lane_lines.append(left_line)

        if len(right_fit) > 0:
            right_fit_average = np.average(right_fit, axis=0)
            right_line = make_points(_input, right_fit_average)
            lane_lines.append(right_line)

        # Drop the less confident line if the lanes intersect
        if len(lane_lines) == 2:
            point_l1 = np.array(lane_lines[0][0][:2])
            point_l2 = np.array(lane_lines[0][0][2:4])
            point_r1 = np.array(lane_lines[1][0][:2])
            point_r2 = np.array(lane_lines[1][0][2:4])
            left_len, right_len = np.linalg.norm(point_l1 - point_l2), np.linalg.norm(point_r1 - point_r2)
            left_slope, right_slope = left_fit_average[0], right_fit_average[0]
            do_intersect = lines_intersect(point_l1, point_l2, point_r1, point_r2)
            if do_intersect:
                # Drop the less confident line out (greater slope)
                right_confident = abs(left_slope) < abs(right_slope) and right_len > left_len
                del lane_lines[0 if right_confident else 1]

        output = Frame._draw_lines(output, lane_lines, (0, 255, 255))

        return output, lane_lines
