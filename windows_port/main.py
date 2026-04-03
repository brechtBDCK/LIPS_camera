from pathlib import Path

import cv2
import numpy as np
from openni import openni2

from bootstrap_windows import prepare_openni_windows


ROOT = Path(__file__).resolve().parent


def read_color_frame(stream) -> np.ndarray:
    frame = stream.read_frame()
    image = np.frombuffer(frame.get_buffer_as_uint8(), dtype=np.uint8).reshape(
        frame.height, frame.width, 3
    )
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


def read_depth_or_ir_frame(stream) -> np.ndarray:
    frame = stream.read_frame()
    return np.frombuffer(frame.get_buffer_as_uint16(), dtype=np.uint16).reshape(
        frame.height, frame.width
    )


def main() -> int:
    redist = prepare_openni_windows()
    openni2.initialize(str(redist))

    device = None
    color = None
    depth = None
    ir = None

    try:
        device = openni2.Device.open_any()

        color = device.create_color_stream()
        depth = device.create_depth_stream()
        ir = device.create_ir_stream()

        assert color is not None
        assert depth is not None
        assert ir is not None

        color.configure_mode(
            width=640,
            height=480,
            fps=30,
            pixel_format=openni2.PIXEL_FORMAT_RGB888,
        )
        depth.configure_mode(
            width=640,
            height=400,
            fps=30,
            pixel_format=openni2.PIXEL_FORMAT_DEPTH_1_MM,
        )
        ir.configure_mode(
            width=640,
            height=400,
            fps=30,
            pixel_format=openni2.PIXEL_FORMAT_GRAY16,
        )

        color.start()
        depth.start()
        ir.start()

        color_image = read_color_frame(color)
        depth_image = read_depth_or_ir_frame(depth)
        ir_image = read_depth_or_ir_frame(ir)

        cv2.imwrite(str(ROOT / "color.png"), color_image)
        cv2.imwrite(str(ROOT / "depth.png"), depth_image)
        cv2.imwrite(str(ROOT / "ir.png"), ir_image)
    finally:
        for stream in (ir, depth, color):
            if stream is None:
                continue
            try:
                stream.stop()
            except Exception:
                pass
            try:
                stream.close()
            except Exception:
                pass

        if device is not None:
            try:
                device.close()
            except Exception:
                pass

        openni2.unload()

    print("Saved color.png, depth.png, ir.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
