import os
import sys
from pathlib import Path
import cv2
from openni import openni2
import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[1]))
from bootstrap import prepare_openni

prepare_openni()

openni2.initialize(os.environ['OPENNI2_REDIST'])
uris = openni2.Device.enumerate_uris()

if not uris:
    print('Camera not found')
    sys.exit(0)

device = openni2.Device.open_any()

color = device.create_color_stream()
depth = device.create_depth_stream()

assert color is not None
assert depth is not None
color.start()
depth.start()

thresholdValueUp = 800 #depth values higher than this will be filtered out
thresholdValueDown = 500 #depth values lower than this will be filtered out

while True:
    rgbFrame = color.read_frame()
    rgbMat = np.frombuffer(rgbFrame.get_buffer_as_uint8(), dtype=np.uint8).reshape(getattr(rgbFrame, "height"), getattr(rgbFrame, "width"), 3)
    rgbMat = cv2.cvtColor(rgbMat, cv2.COLOR_BGR2RGB)
    cv2.imshow('RGB', rgbMat)

    depthFrame = depth.read_frame()
    depthMat = np.frombuffer(depthFrame.get_buffer_as_uint16(), dtype=np.uint16).reshape(getattr(depthFrame, "height"), getattr(depthFrame, "width"), 1)

    thres = depthMat.copy()
    _, thres = cv2.threshold(thres, thresholdValueDown, 1024, cv2.THRESH_TOZERO)
    _, thres = cv2.threshold(thres, thresholdValueUp, 1024, cv2.THRESH_TOZERO_INV)
    _, thres = cv2.threshold(thres, 1, 1024, cv2.THRESH_BINARY)
    thres = cv2.convertScaleAbs(thres, alpha=255.0 / 1024.0)
    cv2.imshow("Threshold", thres)

    depthMat = cv2.convertScaleAbs(depthMat, alpha=255.0 / 1024.0)
    cv2.imshow('Depth', depthMat)
    
    input = cv2.waitKey(1)
    if input == ord('q'):
        break

cv2.destroyAllWindows()
color.stop()
depth.stop()
device.close()
openni2.unload()
