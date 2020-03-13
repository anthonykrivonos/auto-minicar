from cv2 import *
from time import sleep
import sys
from sys import argv
from os import mkdir, chdir
from os.path import realpath, join, dirname, exists

# initialize the camera
cam = VideoCapture(0)   # 0 -> index of camera

def frame_by_frame(name, seconds=60, fps=4):
    num_shots = seconds * fps
    dname = join(dirname(realpath(sys.argv[0])), "data", name) 
    if not exists(dname):
        mkdir(dname)
    chdir(dname)
    for i in range(num_shots):
        s, img = cam.read()
        path = "./" + str(i + 1) + ".png"
        if s:
            imwrite(path, img)
            print("Saved to " + dname + "/" + str(i + 1) + ".png")
            sleep(1/fps)

frame_by_frame(argv[1], int(argv[2]), int(argv[3]))
