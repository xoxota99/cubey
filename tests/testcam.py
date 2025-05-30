import yaml
from cv2 import cv2     # OpenCV 4.5.3 and later
import numpy as np

"""
Take a picture of the current cube, then apply six masks, based on HSV bracket 
configuration, writing six resulting files to disk (U.png, R.png, D.png, etc)
"""
config_file = "../config.yaml"
config = {}
with open(config_file, 'r') as ymlfile:
    config = yaml.load(ymlfile, Loader=yaml.FullLoader)

calib_file = "../" + config['cam']['calibration']
calib = {}
with open(calib_file, 'r') as ymlfile:
    calib = yaml.load(ymlfile, Loader=yaml.FullLoader)

cap = cv2.VideoCapture(config['cam']['camera_deviceID'])
_, raw = cap.read()

h, w, c = raw.shape
hsv_img = cv2.cvtColor(raw, cv2.COLOR_BGR2HSV_FULL)

white = np.full((h, w, c), (255, 255, 255), dtype=np.uint8)
white[:] = (255, 255, 255)    # BGR

rename = {"U": "yellow", "B": "red", "R": "blue",
          "D": "white", "L": "green", "F": "orange"}
for clr in calib["colors"]:
    e = calib["colors"][clr]  # blue
    min_hsv = np.array(e["min"])
    max_hsv = np.array(e["max"])
    maskHSV = np.full((h, w, c), (0, 0, 0), dtype=np.uint8)

    if min_hsv[0] <= max_hsv[0] and min_hsv[1] <= max_hsv[1] and min_hsv[2] <= max_hsv[2]:
        maskHSV = cv2.inRange(hsv_img, min_hsv, max_hsv)
    else:
        # hue overflow (red)
        mask1 = cv2.inRange(hsv_img, min_hsv, np.array(
            [255, max_hsv[1], max_hsv[2]]))
        mask2 = cv2.inRange(hsv_img, np.array(
            [0, min_hsv[1], min_hsv[2]]), max_hsv)
        # add masks
        maskHSV = cv2.add(mask1, mask2)

    resultHSV = cv2.bitwise_and(white, white, mask=maskHSV)
    cv2.imwrite("{color}.png".format(color=rename[clr]), resultHSV)

cap.release()
