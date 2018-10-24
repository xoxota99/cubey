import cv2
import numpy as np
import os.path
from config import cfg

# define a list of colors, with an error bar. The color "Center" is the idealized color,
# and the "radius" is how far off the pixel color can be from the idealized color and
# still be counted as that color.

# COLOR_CENTERS = (
#     (np.array([147.,  147.,  147.]),  30., "W"),
#     (np.array([231.,   95.,   30.]),  60., "B"),
#     (np.array([0.,    0.,  255.]), 110., "R"),
#     (np.array([0.,  133.,  217.]),  30., "O"),
#     (np.array([53.,  176.,  176.]),  30., "Y"),
#     (np.array([160.,  198.,   0.]),  30., "G"),
# )

colorCenters = cfg['cam']['colorCenters']

# Map Color codes (OWYBGR) to Face codes (FBTLRB).
# we take this extra step here, instead of inline in COLOR_CENTERS, to allow for configuring
# the "known" position of cube faces at startup. Because we can't scan the center facelet
# of each side (it is obscured by the gripper), we have to assume that it's a certain color for each side.
# this is basically a config value that describes the positioning of the cube in the robot.
COLOR_TO_FACE = cfg['cam']['colorFaceMap']

FRAME_WIDTH = cfg['cam']['frameWidth']
FRAME_HEIGHT = cfg['cam']['frameHeight']
FPS = cfg['cam']['fps']

# Should we flip the camera image? (Some webcams mirror by default. Super annoying.)
FLIP_CAMERA = cfg['cam']['flipCamera']
FLIP_CODE = cfg['cam']['flipCode']


def guessColor(v):
    # for v2, radius, code in COLOR_CENTERS:
    for v2 in colorCenters:
        d = np.linalg.norm(v - v2['rgb'])
        if d < v2['radius']:
            return v2['code']  # stop checking immediately
    return "X"  # unknown


def devIdFromPath(path):
    realpath = os.path.realpath(path)
    if not "/dev/video" in realpath:
        raise "Not a video device"
    devnum = int(realpath[-1])
    return devnum


class Camera:
    vidcap = None

    sampleCoords = []

    def __init__(self, deviceName, sampleCoords):
        self.vidcap = cv2.VideoCapture(devIdFromPath(deviceName))

        self.vidcap.set(3, FRAME_WIDTH)     # cv2.cv.CV_CAP_PROP_FRAME_WIDTH
        self.vidcap.set(4, FRAME_HEIGHT)     # cv2.cv.CV_CAP_PROP_FRAME_HEIGHT
        self.vidcap.set(5, FPS)      # CAP_PROP_FPS
        self.sampleCoords = sampleCoords

        # vidcap.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS,       0.20 )#0.50 default
        # vidcap.set(cv2.cv.CV_CAP_PROP_CONTRAST,         0.15 )#0.15 default
        # vidcap.set(cv2.cv.CV_CAP_PROP_SATURATION,       0.10 )#0.15 default
        # vidcap.set(cv2.cv.CV_CAP_PROP_GAIN,             0.15 )#0.15 default
        # vidcap.set(cv2.cv.CV_CAP_PROP_EXPOSURE, 0.5 ) #not supported by C310
        # vidcap.set(21, 0.0)#CV_CAP_PROP_AUTO_EXPOSURE #not supported by C310

    def get_colors(self):
        """ Given a camera reference, take a vertical edge-on picture of the cube, and evaluate some of the facelets.
        There are two cameras, Front-Right, and Back-Left.
        In the case of the Front-right camera, for example, return a tuple of FURBDL values that refer to the facelets
        in the (zero-based) F2, R0, F5, R3, F8, R6 positions.
        """
        arr = []

        _, frame = self.vidcap.read()
        if frame != None:

            if FLIP_CAMERA:
                frame = cv2.flip(frame, flipCode=FLIP_CODE)

            for coord in self.sampleCoords:
                x, y = coord[0], coord[1]

                # define a small square (x1,y1,x2,y2) in the frame to sample for color.
                x1, y1 = x - 2, y - 2
                x2, y2 = x + 2, y + 2

                block = frame[y1:y2, x1:x2]
                block_r = block[:, :, 0]    # red
                block_g = block[:, :, 1]    # green
                block_b = block[:, :, 2]    # blue

                # get the average color within the block, for each R/G/B component.
                clr = np.array(
                    (np.median(block_r), np.median(block_g), np.median(block_b)))
                # clr /= np.linalg.norm( clr ) / 255.0

                code = guessColor(clr)
                code = COLOR_TO_FACE[code]

                arr.append(code)

            return tuple(arr)
        else:
            print("no frames!")
            return tuple(np.full(6, "X"))
