from cv2 import cv2
import numpy as np
import yaml

# A manual test of given hsv calibration settings.
#
# read the images, scan them with the provided HSV calibration data / brackets, output masked images for each scan.
# input files are pictures taken in varying lighting conditions.

input_path = "images"
input_files = [
    "rub00.jpg",
    "rub01.jpg",
    "rub02.jpg",
    "rub03.jpg",
    "rub04.jpg",
    "rub05.jpg",
    "rub06.jpg",
    "rub07.jpg",
    "rub08.jpg",
    "rub09.jpg"
]

output_path = "output"
output_file_pattern = [
    "rub00_{color}.jpg",
    "rub01_{color}.jpg",
    "rub02_{color}.jpg",
    "rub03_{color}.jpg",
    "rub04_{color}.jpg",
    "rub05_{color}.jpg",
    "rub06_{color}.jpg",
    "rub07_{color}.jpg",
    "rub08_{color}.jpg",
    "rub09_{color}.jpg"
]
config_file = "config.yaml"

if __name__ == "__main__":
    with open(config_file, 'r') as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)

    for i, filename in enumerate(input_files):
        img = cv2.imread(input_path+'/'+filename)
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL)

        for clr in config["colors"]:
            # clr = "W"
            e = config["colors"][clr]  # blue
            minHSV = np.array(e["min"])
            maxHSV = np.array(e["max"])
            h, w, c = img.shape
            maskHSV = np.full((h, w, c), (0, 0, 0), dtype=np.uint8)

            if minHSV[0] <= maxHSV[0] and minHSV[1] <= maxHSV[1] and minHSV[2] <= maxHSV[2]:
                maskHSV = cv2.inRange(hsv_img, minHSV, maxHSV)
            else:
                # hue overflow (red)
                mask1 = cv2.inRange(hsv_img, minHSV, np.array(
                    [255, maxHSV[1], maxHSV[2]]))
                mask2 = cv2.inRange(hsv_img, np.array(
                    [0, minHSV[1], minHSV[2]]), maxHSV)
                # add masks
                maskHSV = cv2.add(mask1, mask2)

            resultHSV = cv2.bitwise_and(img, img, mask=maskHSV)
            cv2.imwrite(output_file_pattern[i].format(color=clr), resultHSV)
