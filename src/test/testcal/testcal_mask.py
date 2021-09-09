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
        bracket1 = cal[key1]
        for key2 in cal:  # 5, 4, 3, 2, 1
            collide = False
            compared[key1].append(key2)
            if key2 != key1 and key1 not in compared[key2]:
                bracket2 = cal[key2]
                if(bracket1["max"][0] < bracket1["min"][0] or bracket2["max"][0] < bracket2["min"][0]):
                    # special case (red). Max H value is less than min.
                    red = bracket1
                    nonred = bracket2
                    if bracket2[1][0] < bracket2[0][0]:  # swap
                        red = bracket2
                        nonred = bracket1

                        collide = (red["max"][0] > nonred["min"][0]
                                   or red["min"][0] < nonred["max"][0])
                    else:
                        # non-red. Do these hues overlap?
                        collide = (bracket1["max"][0] > bracket2["min"][0])

                    # now check S and V, which are the same for red and non-red.
                    collide = collide and (
                        bracket1["min"][0] < bracket2["max"][0]) and (
                        bracket1["max"][1] > bracket2["min"][1]) and (
                        bracket1["min"][1] < bracket1["max"][1]) and (
                        bracket1["max"][2] > bracket2["min"][2]) and (
                        bracket1["min"][2] < bracket2["max"][2])

                    if collide:
                        print("OVERLAP between {0} and {1}".format(key1, key2))
                        print("    min['{0}']: {1}".format(
                            key1, bracket1["min"]))
                        print("    min['{0}']: {1}".format(
                            key2, bracket2["min"]))
                        print("    max['{0}']: {1}".format(
                            key1, bracket1["max"]))
                        print("    max['{0}']: {1}".format(
                            key2, bracket2["max"]))
                        print("")


if __name__ == "__main__":
    with open(config_file, 'r') as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)

    for i, filename in enumerate(input_files):
        img = cv2.imread(input_path + '/' + filename)
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL)

        for clr in config["colors"]:
            e = config["colors"][clr]  # blue
            min_hsv = np.array(e["min"])
            max_hsv = np.array(e["max"])
            h, w, c = img.shape
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

            resultHSV = cv2.bitwise_and(img, img, mask=maskHSV)
            cv2.imwrite(output_file_pattern[i].format(color=clr), resultHSV)

    collision_detect(config)
