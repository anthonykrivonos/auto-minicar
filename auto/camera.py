from cv2 import *
import os, sys
from os import mkdir, chdir
from time import time, sleep
from os.path import realpath, join, dirname, exists

from util.timer import Timer

cwd = os.getcwd()

camera = VideoCapture(0)

def reset_camera():
    global camera
    camera.release()
    os.system('sudo rmmod uvcvideo')
    os.system('sudo modprobe uvcvideo nodrop=1 timeout=10000 quirks=0x80')
    camera = VideoCapture(0)
    print("Camera successfully reset")

def get_frame_by_frame(name=None, fps=4, write_to_disk=False, on_capture=None):
    """
    Creates a timer that outputs a frame-by-frame set of images.
    :param name: The name of the frame by frame folder.
    :param fps: The frames per second.
    :param write_to_disk: Write the file to disk? Default false.
    :param on_capture: Callback that passes in the most recent image as a parameter.
    :return: A Timer object.
    """

    reset_camera()

    if name is None:
        name = "fbf_" + str(int(time()))

    chdir(cwd)
    dname = join(dirname(realpath(sys.argv[0])), "train", "data", name)
    if not exists(dname):
        print("Created dir: %s" % dname)
        mkdir(dname)
    else:
        print("Using dir: %s" % dname)

    def _snap(dname, write, capture_callback):
        global camera
        s, img = camera.read()

        if s and capture_callback:
            capture_callback(img)

        if write:
            chdir(dname)
            number_of_files = len([item for item in os.listdir(dname) if os.path.isfile(os.path.join(dname, item))])
            path = "./" + str(number_of_files + 1) + ".png"
            if s:
                imwrite(path, img)
                print("Saved to " + dname + "/" + str(number_of_files + 1) + ".png")
            else:
                print("Could not read image %d from camera" % (number_of_files + 1))
            chdir(cwd)

    return Timer(1 / fps, _snap, dname, write_to_disk, on_capture).use_mp()


def record_frame_by_frame(name=None, fps=4, duration_s=30):
    global camera

    reset_camera()

    if name is None:
        name = "fbf_" + str(int(time()))

    chdir(cwd)
    dname = join(dirname(realpath(sys.argv[0])), "train", "data", name)
    if not exists(dname):
        mkdir(dname)
    chdir(dname)

    file_num = len([item for item in os.listdir(dname) if os.path.isfile(os.path.join(dname, item))])

    num_frames = int(duration_s * fps)
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

    chdir(cwd)
