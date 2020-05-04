from cv2 import *
import sys
from os import mkdir, chdir
from time import time
from os.path import realpath, join, dirname, exists

from util.timer import Timer

def get_camera(idx = None):
    if idx is not None:
        print("Selected camera %d" % idx)
        camera = cv2.VideoCapture(idx)
        camera.release()
        return camera
    for i in range(0, 11):
        camera = cv2.VideoCapture(i)
        if camera is None or not camera.read()[0]:
            break
        camera.release()
        print("Got camera %d" % i)
        return camera
    print("Could not get camera")
    return None

camera = None

def _snap(dname):
    global camera

    number_of_files = len([item for item in os.listdir(dname) if os.path.isfile(os.path.join(dname, item))])

    s, img = camera.read()
    path = "./" + str(number_of_files + 1) + ".png"
    if s:
        imwrite(path, img)
        print("Saved to " + dname + "/" + str(number_of_files + 1) + ".png")
    else:
        print("Could not read image %d from camera" % (number_of_files + 1))


def get_frame_by_frame(name=None, fps=4):
    """
    Creates a timer that outputs a frame-by-frame set of images into the given folder.
    :param name: The name of the frame by frame folder.
    :param fps: The frames per second.
    :return: A Timer object.
    """

    global camera

    if name is None:
        name = "fbf_" + str(int(time()))

    camera = get_camera()

    dname = join(dirname(realpath(sys.argv[0])), "train", "data", name)
    if not exists(dname):
        mkdir(dname)
    chdir(dname)

    return Timer(1 / fps, _snap, dname)
