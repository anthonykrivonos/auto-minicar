import cv2
from time import sleep
from auto.camera import get_frame_by_frame
from auto.lkas import get_steering_angle

def hud(img):
    angle, frame = get_steering_angle(img)
    img = frame.top()[0]
    return img

print('Creating fbf')
fbf = get_frame_by_frame(fps=6, display_feed=True, on_capture=hud)
print('Waiting 5 seconds')
sleep(5)
print('Starting fbf')
fbf.start()
print('fbf started')
