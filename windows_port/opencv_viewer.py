import cv2
import numpy as np
from openni import openni2

from bootstrap_windows import prepare_openni_windows


def main() -> int:
    redist = prepare_openni_windows()
    openni2.initialize(str(redist))

    device = None
    color = None

    try:
        device = openni2.Device.open_any()

        color = device.create_color_stream()
        assert color is not None

        color.configure_mode(
            width=640,
            height=480,
            fps=30,
            pixel_format=openni2.PIXEL_FORMAT_RGB888,
        )
        color.start()

        while True:
            frame = color.read_frame()
            image = np.frombuffer(
                frame.get_buffer_as_uint8(), dtype=np.uint8
            ).reshape(frame.height, frame.width, 3)
            bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.imshow("RGB", bgr)

            if cv2.waitKey(1) == ord("q"):
                break
    finally:
        cv2.destroyAllWindows()

        if color is not None:
            try:
                color.stop()
            except Exception:
                pass
            try:
                color.close()
            except Exception:
                pass

        if device is not None:
            try:
                device.close()
            except Exception:
                pass

        openni2.unload()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
