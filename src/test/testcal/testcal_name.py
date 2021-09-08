from cv2 import cv2
import numpy as np
import yaml

"""
 A manual test of given hsv calibration settings.

 Read the image, scan them with the provided HSV calibration data / brackets, output
 the list of "guessed" colors (O, R, W, G, B, Y), in the order:

 +---+---+---+
 | 1 | 2 | 3 |
 +---+---+---+
 | 4 | 5 | 6 |
 +---+---+---+
 | 7 | 8 | 9 |
 +---+---+---+
"""

config_file = "config.yaml"
img_file = "images/rub00.jpg"
sample_coords = [
    [68, 71],    # W
    [190, 71],   # O
    [305, 68],   # B
    [69, 189],   # R
    [187, 187],  # G
    [300, 181],  # B
    [72, 302],   # O
    [186, 304],  # O
    [306, 297],  # Y
]

if __name__ == "__main__":
    with open(config_file, 'r') as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)

    img = cv2.imread(img_file)
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL)
    r = 10
    # for each of the sample coords
    for i, coord in enumerate(sample_coords):
        x, y = coord[0], coord[1]
        # define a small square (x1,y1,x2,y2) in the frame to sample for color.
        x1, y1 = x - r, y - r
        x2, y2 = x + r, y + r

        block = hsv_img[y1:y2, x1:x2]

        # average hsv in the sample area.
        avg = block.mean(axis=0).mean(axis=0)
        for clr in config["colors"]:
            e = config["colors"][clr]  # blue
            minHSV = np.array(e["min"])
            maxHSV = np.array(e["max"])
            h, w, c = img.shape
            maskHSV = np.full((h, w, c), (0, 0, 0), dtype=np.uint8)

            if clr == "R":
                # red
                mask1 = cv2.inRange(hsv_img, minHSV, np.array(
                    [255, maxHSV[1], maxHSV[2]]))
                mask2 = cv2.inRange(hsv_img, np.array(
                    [0, minHSV[1], minHSV[2]]), maxHSV)
                # add masks
                maskHSV = cv2.add(mask1, mask2)
            else:
                maskHSV = cv2.inRange(hsv_img, minHSV, maxHSV)

            if maskHSV[y, x] != 0:      # Why are x and y reversed? No idea.
                print(clr)
                break