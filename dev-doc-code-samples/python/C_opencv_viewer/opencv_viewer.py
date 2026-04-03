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
# depth = device.create_depth_stream()
# ir = device.create_ir_stream()

assert color is not None
# assert depth is not None
# assert ir is not None   
color.start()
# depth.start()
# ir.start()

while True:
    rgbFrame = color.read_frame()
    rgbMat = np.frombuffer(rgbFrame.get_buffer_as_uint8(), dtype=np.uint8).reshape(getattr(rgbFrame, "height"), getattr(rgbFrame, "width"), 3)
    rgbMat = cv2.cvtColor(rgbMat, cv2.COLOR_BGR2RGB)
    cv2.imshow('RGB', rgbMat)

    # depthFrame = depth.read_frame()
    # depthMat = np.frombuffer(depthFrame.get_buffer_as_uint16(), dtype=np.uint16).reshape(getattr(depthFrame, "height"), getattr(depthFrame, "width"), 1)
    # depthMat = cv2.convertScaleAbs(depthMat, alpha=255.0 / 1024.0)
    # depthMat = cv2.applyColorMap(depthMat, cv2.COLORMAP_JET)
    # cv2.imshow('Depth', depthMat)

    # irFrame = ir.read_frame()
    # irMat = np.frombuffer(irFrame.get_buffer_as_uint16(), dtype=np.uint16).reshape(getattr(irFrame, "height"), getattr(irFrame, "width"), 1)
    # irMat = cv2.convertScaleAbs(irMat, alpha=255.0 / 1024.0)
    # cv2.imshow('IR', irMat)

    input = cv2.waitKey(1)
    if input == ord('q'):
        break

cv2.destroyAllWindows()
color.stop()
# depth.stop()  
# ir.stop()
device.close()
openni2.unload()
