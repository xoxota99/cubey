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


def collision_detect(config):
    compared = {"R": [], "O": [], "Y": [], "G": [], "B": [], "W": []}
    cal = config["colors"]

    for key1 in cal:  # 6
        min_hsv_1 = cal[key1]["min"]
        max_hsv_1 = cal[key1]["max"]
        for key2 in cal:  # 5, 4, 3, 2, 1
            compared[key1].append(key2)
            if key2 != key1 and key1 not in compared[key2]:
                min_hsv_2 = cal[key2]["min"]
                max_hsv_2 = cal[key2]["max"]
                # print("#Testing {0} against {1}".format(key1, key2))
                # TODO: doesn't capture red / modulo
                if (max_hsv_1[0] > min_hsv_2[0]) and (min_hsv_1[0] < max_hsv_2[0]) and (max_hsv_1[1] > min_hsv_2[1]) and (min_hsv_1[1] < max_hsv_2[1]) and (max_hsv_1[2] > min_hsv_2[2]) and (min_hsv_1[2] < max_hsv_2[2]):
                    print("OVERLAP between {0} and {1}".format(key1, key2))
                    print("min['{0}']: {1}".format(key1, min_hsv_1))
                    print("min['{0}']: {1}".format(key2, min_hsv_2))
                    print("max['{0}']: {1}".format(key1, max_hsv_1))
                    print("max['{0}']: {1}".format(key2, max_hsv_2))


if __name__ == "__main__":
    with open(config_file, 'r') as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)

    for i, filename in enumerate(input_files):
        img = cv2.imread(input_path+'/'+filename)
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL)

        # for clr in config["colors"]:
        clr = "O"
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

    collision_detect(config)
