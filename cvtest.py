import cv2
import numpy as np

test_img_center = cv2.imread('/home/pi/dev/car/train/data/train_data_narrow/61.png')

# Change to HSV
hsv_img = cv2.cvtColor(test_img_center, cv2.COLOR_BGR2HSV)

# Lift the blue color from the image
color_range = (
    np.array([60, 40, 40]),
    np.array([150, 255, 255])
)
masked_img = cv2.inRange(hsv_img, *color_range)

# Detect the edges of the blue blobs

edge_img = cv2.Canny(masked_img, 200, 400)

cv2.imshow('Edge Image', edge_img)

cv2.waitKey(0)
cv2.destroyAllWindows()