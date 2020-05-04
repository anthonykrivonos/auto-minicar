from cv2 import *
import os, sys
from os import mkdir, chdir
from time import time, sleep
from os.path import realpath, join, dirname, exists

from util.timer import Timer

cwd = os.getcwd()

def get_camera(idx = None):
    if idx is not None:
        print("Selected camera %d" % idx)
        camera = cv2.VideoCapture(idx)
        camera.release()
        return camera
    for i in range(-1, 11):
        camera = cv2.VideoCapture(i)
        if camera is None or not camera.read()[0]:
            break
        camera.release()
        print("Got camera %d" % i)
        return camera
    print("Could not get camera")
    return None

camera = get_camera()

def _snap(dname):
    global camera

    chdir(dname)
    number_of_files = len([item for item in os.listdir(dname) if os.path.isfile(os.path.join(dname, item))])

    s, img = camera.read()
    path = "./" + str(number_of_files + 1) + ".png"
    if s:
        imwrite(path, img)
        print("Saved to " + dname + "/" + str(number_of_files + 1) + ".png")
    else:
        print("Could not read image %d from camera" % (number_of_files + 1))

    chdir(cwd)
    camera.release()

def get_frame_by_frame(name=None, fps=4):
    """
    Creates a timer that outputs a frame-by-frame set of images into the given folder.
    :param name: The name of the frame by frame folder.
    :param fps: The frames per second.
    :return: A Timer object.
    """

    if name is None:
        name = "fbf_" + str(int(time()))

    chdir(cwd)
    dname = join(dirname(realpath(sys.argv[0])), "train", "data", name)
    if not exists(dname):
        mkdir(dname)

    return Timer(1 / fps, _snap, dname)

def record_frame_by_frame(name=None, fps=4, duration_s=30):

    camera = get_camera()

    if name is None:
        name = "fbf_" + str(int(time()))

    chdir(cwd)
    dname = join(dirname(realpath(sys.argv[0])), "train", "data", name)
    if not exists(dname):
        mkdir(dname)

    file_num = len([item for item in os.listdir(dname) if os.path.isfile(os.path.join(dname, item))])

    num_frames = int(duration_s / fps)
    delay = 1 / fps

    for _ in range(num_frames):
        file_num += 1

        s, img = camera.read()
        path = "./" + str(file_num) + ".png"
        if s:
            imwrite(path, img)
            print("Saved to " + dname + "/" + str(file_num) + ".png")
        else:
            print("Could not read image %d from camera" % file_num)

        sleep(delay)