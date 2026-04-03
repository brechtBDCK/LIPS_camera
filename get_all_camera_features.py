import argparse
import ctypes
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SDK = ROOT / "sdk-Lseries"


def prepare_openni() -> None:
    ctypes.CDLL(str(SDK / "compat" / "libtbb.so.2"), mode=ctypes.RTLD_GLOBAL)
    os.environ["OPENNI2_REDIST"] = str(SDK / "Redist")


class CameraExtrinsicMatrix(ctypes.Structure):
    _fields_ = [
        ("rotation", (ctypes.c_float * 3) * 3),
        ("translation", ctypes.c_float * 3),
    ]


class RadialDistortionCoeffs(ctypes.Structure):
    _fields_ = [
        ("k1", ctypes.c_double),
        ("k2", ctypes.c_double),
        ("k3", ctypes.c_double),
        ("k4", ctypes.c_double),
        ("k5", ctypes.c_double),
        ("k6", ctypes.c_double),
    ]


class TangentialDistortionCoeffs(ctypes.Structure):
    _fields_ = [
        ("p1", ctypes.c_double),
        ("p2", ctypes.c_double),
    ]


STANDARD_DEVICE_PROPERTIES = {
    "image_registration": 5,
    "playback_speed": 100,
    "playback_repeat": 101,
}

STANDARD_STREAM_PROPERTIES = {
    "cropping": 0,
    "horizontal_fov": 1,
    "vertical_fov": 2,
    "video_mode": 3,
    "max_value": 4,
    "min_value": 5,
    "stride": 6,
    "mirroring": 7,
    "number_of_frames": 8,
    "auto_white_balance": 100,
    "auto_exposure": 101,
    "exposure": 102,
    "gain": 103,
}

LIPS_DEVICE_PROPERTIES = {
    "device_name": (300, None),
    "sensor_info_ir": (301, None),
    "sensor_info_color": (302, None),
    "sensor_info_depth": (303, None),
    "lens_mode": (304, ctypes.c_int),
    "lens_mode_ext": (305, ctypes.c_int),
    "imu_data": (306, None),
    "laser_enable": (307, ctypes.c_int),
    "imu_enable": (308, ctypes.c_int),
}

LIPS_STREAM_PROPERTIES = {
    "focal_length_x": (200, ctypes.c_float),
    "focal_length_y": (201, ctypes.c_float),
    "principal_point_x": (202, ctypes.c_float),
    "principal_point_y": (203, ctypes.c_float),
    "imu_data": (204, None),
    "focal_length_r": (205, ctypes.c_float),
    "focal_length_l": (206, ctypes.c_float),
    "principal_point_x_r": (207, ctypes.c_float),
    "principal_point_y_r": (208, ctypes.c_float),
    "principal_point_x_l": (209, ctypes.c_float),
    "principal_point_y_l": (210, ctypes.c_float),
    "focal_length_x_r": (211, ctypes.c_float),
    "focal_length_y_r": (212, ctypes.c_float),
    "focal_length_x_l": (213, ctypes.c_float),
    "focal_length_y_l": (214, ctypes.c_float),
    "original_res_x": (215, ctypes.c_int),
    "original_res_y": (216, ctypes.c_int),
    "imu_enable": (217, ctypes.c_int),
    "imu_accel_offset": (218, None),
    "imu_gyro_offset": (219, None),
    "extrinsic_to_depth": (220, CameraExtrinsicMatrix),
    "extrinsic_to_color": (221, CameraExtrinsicMatrix),
    "radial_distortion": (222, RadialDistortionCoeffs),
    "tangential_distortion": (223, TangentialDistortionCoeffs),
    "extrinsic_to_ir": (224, CameraExtrinsicMatrix),
}

LIPS_SENSOR_PROPERTIES = {
    "read_register": (400, None),
    "write_register": (401, None),
    "temperature": (402, ctypes.c_float),
    "low_power_enable": (403, ctypes.c_int),
}


def print_header(title: str) -> None:
    print(f"\n== {title} ==")


def ok(label: str, detail: str = "") -> None:
    if detail:
        print(f"[OK] {label}: {detail}")
    else:
        print(f"[OK] {label}")


def warn(label: str, detail: str = "") -> None:
    if detail:
        print(f"[WARN] {label}: {detail}")
    else:
        print(f"[WARN] {label}")


def fail(label: str, detail: str = "") -> None:
    if detail:
        print(f"[FAIL] {label}: {detail}")
    else:
        print(f"[FAIL] {label}")


def safe_get_property(owner, property_id: int, rettype):
    if rettype is None:
        return None, "opaque"
    try:
        value = owner.get_property(property_id, rettype)
    except Exception as exc:
        return None, str(exc)
    if hasattr(value, "value"):
        return value.value, None
    return value, None


def inspect_stream(name, stream, read_properties: bool, read_frame: bool) -> None:
    print_header(f"{name} stream")

    try:
        sensor_info = stream.get_sensor_info()
        modes = getattr(sensor_info, "videoModes", [])
        ok("sensor info", f"{len(modes)} supported mode(s)")
        for i, mode in enumerate(modes[:10]):
            print(
                f"  - mode[{i}] {mode.resolutionX}x{mode.resolutionY} "
                f"{mode.fps}fps format={mode.pixelFormat}"
            )
        if len(modes) > 10:
            print(f"  - ... {len(modes) - 10} more")
    except Exception as exc:
        fail("sensor info", str(exc))

    for prop_name, prop_id in STANDARD_STREAM_PROPERTIES.items():
        try:
            supported = stream.is_property_supported(prop_id)
        except Exception as exc:
            warn(f"standard property {prop_name}", str(exc))
            continue
        if supported:
            ok(f"standard property {prop_name}", f"id={prop_id}")

    for prop_name, (prop_id, rettype) in LIPS_STREAM_PROPERTIES.items():
        try:
            supported = stream.is_property_supported(prop_id)
        except Exception as exc:
            warn(f"LIPS stream property {prop_name}", str(exc))
            continue
        if not supported:
            continue
        if not read_properties:
            ok(f"LIPS stream property {prop_name}", f"id={prop_id}")
            continue
        value, error = safe_get_property(stream, prop_id, rettype)
        if error is None:
            ok(f"LIPS stream property {prop_name}", f"id={prop_id} value={value}")
        else:
            warn(f"LIPS stream property {prop_name}", f"id={prop_id} read={error}")

    for prop_name, (prop_id, rettype) in LIPS_SENSOR_PROPERTIES.items():
        try:
            supported = stream.is_property_supported(prop_id)
        except Exception as exc:
            warn(f"LIPS sensor property {prop_name}", str(exc))
            continue
        if not supported:
            continue
        if not read_properties:
            ok(f"LIPS sensor property {prop_name}", f"id={prop_id}")
            continue
        value, error = safe_get_property(stream, prop_id, rettype)
        if error is None:
            ok(f"LIPS sensor property {prop_name}", f"id={prop_id} value={value}")
        else:
            warn(f"LIPS sensor property {prop_name}", f"id={prop_id} read={error}")

    if read_frame:
        try:
            stream.start()
            frame = stream.read_frame()
            ok(
                "read_frame",
                f"{frame.width}x{frame.height} index={frame.frameIndex} ts={frame.timestamp}",
            )
        except Exception as exc:
            fail("read_frame", str(exc))
        finally:
            try:
                stream.stop()
            except Exception:
                pass


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify LIPSedge/OpenNI camera features against a live connected camera."
    )
    parser.add_argument(
        "--read-properties",
        action="store_true",
        help="Attempt to read supported LIPS property values, not just support flags.",
    )
    parser.add_argument(
        "--read-frames",
        action="store_true",
        help="Start each stream and read one frame.",
    )
    args = parser.parse_args()

    prepare_openni()

    from openni import openni2

    print_header("environment")
    ok("python", sys.version.split()[0])
    ok("OPENNI2_REDIST", os.environ["OPENNI2_REDIST"])

    try:
        openni2.initialize(os.environ["OPENNI2_REDIST"])
        ok("openni2.initialize")
    except Exception as exc:
        fail("openni2.initialize", str(exc))
        return 1

    try:
        uris = openni2.Device.enumerate_uris()
        ok("enumerate_uris", repr(uris))
        if not uris:
            warn("camera", "No devices enumerated")
            return 2

        device = openni2.Device.open_any()
        info = device.get_device_info()
        print_header("device")
        ok("name", getattr(info, "name", b"")) #type: ignore
        ok("vendor", getattr(info, "vendor", b"")) #type: ignore
        ok("uri", getattr(info, "uri", b"")) #type: ignore
        ok("usb ids", f"vid={info.usbVendorId} pid={info.usbProductId}")

        try:
            supported = device.is_image_registration_mode_supported(
                openni2.IMAGE_REGISTRATION_DEPTH_TO_COLOR
            )
            ok("registration support", str(bool(supported)))
        except Exception as exc:
            warn("registration support", str(exc))

        try:
            sync_enabled = device.get_depth_color_sync_enabled()
            ok("depth_color_sync", str(sync_enabled))
        except Exception as exc:
            warn("depth_color_sync", str(exc))

        for prop_name, prop_id in STANDARD_DEVICE_PROPERTIES.items():
            try:
                supported = device.is_property_supported(prop_id)
            except Exception as exc:
                warn(f"standard device property {prop_name}", str(exc))
                continue
            if supported:
                ok(f"standard device property {prop_name}", f"id={prop_id}")

        for prop_name, (prop_id, rettype) in LIPS_DEVICE_PROPERTIES.items():
            try:
                supported = device.is_property_supported(prop_id)
            except Exception as exc:
                warn(f"LIPS device property {prop_name}", str(exc))
                continue
            if not supported:
                continue
            if not args.read_properties:
                ok(f"LIPS device property {prop_name}", f"id={prop_id}")
                continue
            value, error = safe_get_property(device, prop_id, rettype)
            if error is None:
                ok(f"LIPS device property {prop_name}", f"id={prop_id} value={value}")
            else:
                warn(f"LIPS device property {prop_name}", f"id={prop_id} read={error}")

        sensors = [
            ("color", openni2.SENSOR_COLOR, device.create_color_stream),
            ("depth", openni2.SENSOR_DEPTH, device.create_depth_stream),
            ("ir", openni2.SENSOR_IR, device.create_ir_stream),
        ]
        for sensor_name, sensor_type, create_fn in sensors:
            try:
                has_sensor = device.has_sensor(sensor_type)
            except Exception as exc:
                fail(f"{sensor_name} availability", str(exc))
                continue
            if not has_sensor:
                warn(f"{sensor_name} availability", "sensor not present")
                continue
            ok(f"{sensor_name} availability")
            try:
                stream = create_fn()
                inspect_stream(sensor_name, stream, args.read_properties, args.read_frames)
            except Exception as exc:
                fail(f"{sensor_name} stream create", str(exc))
            finally:
                try:
                    if stream is not None:
                        stream.close()
                except Exception:
                    pass

        device.close()
        return 0
    finally:
        try:
            openni2.unload()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
