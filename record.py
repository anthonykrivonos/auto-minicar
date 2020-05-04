from time import sleep
from train.train import get_frame_by_frame

fbf = get_frame_by_frame(fps=4)
print("Frame by frame started")

fbf.start()
sleep(5)
fbf.stop()

print("done")
