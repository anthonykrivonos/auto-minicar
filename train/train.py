from cv2 import *
import sys
from os import mkdir, chdir
from time import time
from os.path import realpath, join, dirname, exists

from util.timer import Timer

def get_frame_by_frame(name=None, fps=4):
    """
    Creates a timer that outputs a frame-by-frame set of images into the given folder.
    :param name: The name of the frame by frame folder.
    :param fps: The frames per second.
    :return: A Timer object.
    """
    if name is None:
        name = "fbf_" + str(int(time()))

    dname = join(dirname(realpath(sys.argv[0])), "train", "data", name)
    if not exists(dname):
        mkdir(dname)
    chdir(dname)

    # initialize the camera
    cam = VideoCapture(0)   # 0 -> index of camera

    def snap(camera):
        number_of_files = len([item for item in os.listdir(dname) if os.path.isfile(os.path.join(dname, item))])

        s, img = camera.read()
        path = "./" + str(number_of_files + 1) + ".png"
        if s:
            imwrite(path, img)
            print("Saved to " + dname + "/" + str(number_of_files + 1) + ".png")
        else:
            print("Could not read from camera " + str(number_of_files + 1))

    return Timer(1 / fps, snap, cam)
