import ctypes
import os
from pathlib import Path

import cv2
import numpy as np
from openni import openni2


root = Path(__file__).resolve().parent
sdk = root / "sdk-l210"

ctypes.CDLL(str(sdk / "compat" / "libtbb.so.2"), mode=ctypes.RTLD_GLOBAL)
os.environ["OPENNI2_REDIST"] = str(sdk / "Redist")

openni2.initialize(os.environ["OPENNI2_REDIST"])

device = openni2.Device.open_any()

color = device.create_color_stream()
depth = device.create_depth_stream()
ir = device.create_ir_stream()

assert color is not None
assert depth is not None
assert ir is not None    

color.start()
depth.start()
ir.start()

color_frame = color.read_frame()
depth_frame = depth.read_frame()
ir_frame = ir.read_frame()

color_frame_height = getattr(color_frame, "height")
color_frame_width = getattr(color_frame, "width")
depth_frame_height = getattr(depth_frame, "height")
depth_frame_width = getattr(depth_frame, "width")
ir_frame_height = getattr(ir_frame, "height")
ir_frame_width = getattr(ir_frame, "width")

color_image = np.frombuffer(color_frame.get_buffer_as_uint8(), dtype=np.uint8).reshape(
    color_frame_height, color_frame_width, 3 
)

depth_image = np.frombuffer(depth_frame.get_buffer_as_uint16(), dtype=np.uint16).reshape(
    depth_frame_height, depth_frame_width 
)

ir_image = np.frombuffer(ir_frame.get_buffer_as_uint16(), dtype=np.uint16).reshape(
    ir_frame_height, ir_frame_width
)

cv2.imwrite(str(root / "color.png"), cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR))
cv2.imwrite(str(root / "depth.png"), depth_image)
cv2.imwrite(str(root / "ir.png"), ir_image)

ir.stop()
depth.stop()
color.stop()

ir.close()
depth.close()
color.close()
device.close()
openni2.unload()

print("Saved color.png, depth.png, ir.png")
