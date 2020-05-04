from time import sleep
from train.train import get_frame_by_frame

fbf = get_frame_by_frame(fps=4)
print("Frame by frame started")

fbf.start(use_thread=False)
sleep(5)
fbf.stop()

print("done")
