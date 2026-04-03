# Python Functions and Camera Option Reference for LIPSedge L210/L215

This document is a practical Python-facing reference for the LIPSedge L210/L215 camera as it is used in this repository.


## Quick Facts

| Item | Value |
| --- | --- |
| Camera family | LIPSedge L210 / L215 |
| SDK style | OpenNI2-compatible driver with LIPS custom extensions |
| Python package | `openni` |
| Streams | `color`, `depth`, `ir` |
| Depth formats seen for this camera family | `DEPTH_1_MM` and `DEPTH_100_UM` |
| Registration modes | `IMAGE_REGISTRATION_OFF`, `IMAGE_REGISTRATION_DEPTH_TO_COLOR` |
| Recommended working distance | `40-120 cm` |
| Light/environment guidance | Avoid direct sunlight and illumination above `1000 lux` |
| RGB shutter | Rolling shutter |
| Depth shutter | Global shutter |

## Startup Pattern

Use the repo bootstrap so the SDK driver and bundled `libtbb.so.2` are loaded correctly:

```python
import os
import sys
from pathlib import Path
from openni import openni2

sys.path.append(str(Path(__file__).resolve().parents[1]))
from bootstrap import prepare_openni

prepare_openni()
openni2.initialize(os.environ["OPENNI2_REDIST"])

device = openni2.Device.open_any()
```

Use this when:

- You want the repo-local SDK binaries, not a system OpenNI install.
- You are running the samples in this workspace.

Returns:

- `openni2.initialize(...)` initializes the OpenNI runtime.
- `openni2.Device.open_any()` returns an opened `Device`.

## Camera Streams and Known Calibrated Modes

These are the modes present in `camera_intrinsics.json`. Treat them as the known calibrated modes for this unit or camera family snapshot.

### Color Stream

| Resolution | Pixel format | HFOV | VFOV | When to use |
| --- | --- | --- | --- | --- |
| `640x480` | `RGB888` | `76.3 deg` | `61.01 deg` | General preview, background removal, faster processing |
| `1280x800` | `RGB888` | `64.3 deg` | `42.89 deg` | Higher detail, calibration-sensitive overlays, offline capture |

### IR Stream

| Resolution | Pixel format | HFOV | VFOV | When to use |
| --- | --- | --- | --- | --- |
| `640x480` | `GRAY16` | `74.52 deg` | `50.83 deg` | Standard IR visualization |
| `640x400` | `GRAY16` | `74.52 deg` | `50.83 deg` | Lower height, reduced processing/load |
| `1280x800` | `GRAY16` | `74.52 deg` | `50.83 deg` | High-detail IR inspection |

### Depth Stream With Registration Off

The checked-in `camera_intrinsics.json` only records the calibrated `DEPTH_1_MM` view of these modes. The Windows viewer reportedly also exposes a `DEPTH_100_UM` option on this camera family.

| Resolution | Pixel format | HFOV | VFOV | When to use |
| --- | --- | --- | --- | --- |
| `640x480` | `DEPTH_1_MM` | `74.52 deg` | `50.83 deg` | General depth work |
| `640x400` | `DEPTH_1_MM` | `74.52 deg` | `50.83 deg` | Lower-height depth stream |
| `1280x800` | `DEPTH_1_MM` | `74.52 deg` | `50.83 deg` | High-detail depth capture |

### Depth Stream With Registration On

With registration enabled, depth uses color-aligned intrinsics.

| Resolution | Pixel format | HFOV | VFOV | When to use |
| --- | --- | --- | --- | --- |
| `640x480` | `DEPTH_1_MM` | `76.3 deg` | `51.83 deg` | RGB/depth overlays, segmentation on color image |
| `640x400` | `DEPTH_1_MM` | `76.3 deg` | `51.83 deg` | Same, lower height |
| `1280x800` | `DEPTH_1_MM` | `64.3 deg` | `42.89 deg` | High-res color-aligned depth |

Notes:

- The checked-in JSON gives resolutions and intrinsics for the `1 mm` depth format, not a complete FPS table and not the full pixel-format list exposed by the runtime/viewer.
- Based on your viewer observation, this camera should also support `openni2.PIXEL_FORMAT_DEPTH_100_UM` in at least some depth modes.
- To inspect the actual supported `fps` values on your connected device, enumerate `device.get_sensor_info(...).videoModes`.

Example:

```python
from openni import openni2

for sensor_name, sensor_type in [
    ("color", openni2.SENSOR_COLOR),
    ("depth", openni2.SENSOR_DEPTH),
    ("ir", openni2.SENSOR_IR),
]:
    info = device.get_sensor_info(sensor_type)
    if info is None:
        continue
    print(sensor_name)
    for mode in info.videoModes:
        print(mode.resolutionX, mode.resolutionY, mode.fps, mode.pixelFormat)
```

## OpenNI Module-Level Python Functions

These come from the upstream `openni.openni2` wrapper.

| Function | Input | Output | When to use | Notes |
| --- | --- | --- | --- | --- |
| `openni2.initialize(dll_directories=None)` | SDK folder or list of SDK folders | `None` | Start the OpenNI runtime | In this repo, pass `os.environ["OPENNI2_REDIST"]` or use `prepare_openni()` first |
| `openni2.is_initialized()` | none | `bool` | Guard repeated setup/teardown | Lightweight check |
| `openni2.unload()` | none | `None` | Clean shutdown | Closes tracked devices, streams, recorders, listeners |
| `openni2.get_version()` | none | `OniVersion` | Inspect runtime version | Returns `major`, `minor`, `maintenance`, `build` |
| `openni2.wait_for_any_stream(streams, timeout=None)` | list of `VideoStream`, optional seconds | `VideoStream` or `None` | Poll multiple streams efficiently | Returns `None` on timeout |
| `openni2.convert_world_to_depth(depth_stream, worldX, worldY, worldZ)` | world coordinates in mm | `(depthX, depthY, depthZ)` floats | Map 3D world coordinates back into depth image coordinates | Use for geometric reasoning |
| `openni2.convert_depth_to_world(depth_stream, depthX, depthY, depthZ)` | depth pixel and depth value | `(worldX, worldY, worldZ)` floats | Turn a depth pixel into 3D coordinates | Use for point clouds, measurements |
| `openni2.convert_depth_to_color(depth_stream, color_stream, depthX, depthY, depthZ)` | depth pixel and value | `(colorX, colorY)` ints | Project a depth point into the color image | Useful even when full registration is off |
| `openni2.configure_logging(directory=None, severity=None, console=None)` | log folder, minimum severity, console flag | `None` | SDK debugging | Severity is `0=Verbose`, `1=Info`, `2=Warning`, `3=Error` |
| `openni2.get_log_filename()` | none | `bytes` or `None` | Find the current SDK log file | Returns `None` when file logging is disabled |
| `openni2.get_bytes_per_pixel(format)` | pixel format constant | currently unusable | Avoid in stock wrapper | The upstream wrapper calls the C API but does not return the value |

## Constants You Will Actually Use

### Sensor Constants

| Constant | Value | Meaning |
| --- | --- | --- |
| `openni2.SENSOR_IR` | `1` | Infrared stream |
| `openni2.SENSOR_COLOR` | `2` | Color stream |
| `openni2.SENSOR_DEPTH` | `3` | Depth stream |

### Image Registration Constants

| Constant | Value | Meaning |
| --- | --- | --- |
| `openni2.IMAGE_REGISTRATION_OFF` | `0` | No alignment |
| `openni2.IMAGE_REGISTRATION_DEPTH_TO_COLOR` | `1` | Align depth into the color camera coordinate system |

### Common Pixel Format Constants

| Constant | Value | Meaning | Typical stream |
| --- | --- | --- | --- |
| `openni2.PIXEL_FORMAT_DEPTH_1_MM` | `100` | 16-bit depth in millimeters | Depth |
| `openni2.PIXEL_FORMAT_DEPTH_100_UM` | `101` | 16-bit depth in `0.1 mm` units | Depth, when the device mode table/viewer exposes the higher-resolution depth format |
| `openni2.PIXEL_FORMAT_SHIFT_9_2` | `102` | Shift format | Rarely used directly in Python |
| `openni2.PIXEL_FORMAT_SHIFT_9_3` | `103` | Shift format | Rarely used directly in Python |
| `openni2.PIXEL_FORMAT_RGB888` | `200` | 8-bit RGB triplets | Color |
| `openni2.PIXEL_FORMAT_YUV422` | `201` | YUV422 | If exposed by device mode table |
| `openni2.PIXEL_FORMAT_GRAY8` | `202` | 8-bit grayscale | Some mono sensors |
| `openni2.PIXEL_FORMAT_GRAY16` | `203` | 16-bit grayscale | IR |
| `openni2.PIXEL_FORMAT_JPEG` | `204` | JPEG-compressed stream | Device dependent |
| `openni2.PIXEL_FORMAT_YUYV` | `205` | YUYV | Device dependent |

## Device Class

### Creation and Discovery

| API | Input | Output | When to use |
| --- | --- | --- | --- |
| `openni2.Device.enumerate_uris()` | none | list of device URIs | Check whether any camera is present before opening |
| `openni2.Device.open_any()` | none | `Device` | Open the first detected camera |
| `openni2.Device.open_all()` | none | list of `Device` | Multi-camera setups |
| `openni2.Device.open_file(filename)` | `.oni` file path | `Device` | Playback from a recording |

### Information and Capability Queries

| API | Input | Output | When to use |
| --- | --- | --- | --- |
| `device.get_device_info()` | none | `DeviceInfo` | Basic identity info |
| `device.device_info` | none | `DeviceInfo` | Property alias for the same data |
| `device.get_sensor_info(sensor_type)` | sensor constant | `SensorInfo` or `None` | Query supported modes for one sensor |
| `device.has_sensor(sensor_type)` | sensor constant | `bool` | Conditional stream creation |
| `device.is_file()` | none | `bool` | Distinguish live device vs `.oni` playback |

`DeviceInfo` contains:

- `uri`
- `vendor`
- `name`
- `usbVendorId`
- `usbProductId`

### Stream Creation

| API | Input | Output | When to use |
| --- | --- | --- | --- |
| `device.create_stream(sensor_type)` | any sensor constant | `VideoStream` | Generic stream factory |
| `device.create_depth_stream()` | none | `VideoStream` or `None` | Depth acquisition |
| `device.create_color_stream()` | none | `VideoStream` or `None` | RGB acquisition |
| `device.create_ir_stream()` | none | `VideoStream` or `None` | IR acquisition |

### Device Settings and Generic Property Access

| API | Input | Output | When to use |
| --- | --- | --- | --- |
| `device.get_property(property_id, rettype)` | numeric property ID and ctypes-compatible type | typed value | Read standard or vendor device properties |
| `device.get_int_property(property_id)` | numeric property ID | `int` | Shortcut for integer-valued properties |
| `device.set_property(property_id, obj, size=None)` | numeric property ID and value/ctypes struct | `None` | Set standard or vendor device properties |
| `device.is_property_supported(property_id)` | numeric property ID | `bool` | Guard optional features before calling them |
| `device.invoke(command_id, data, size=None)` | command ID and typed payload | `None` | Issue device commands such as playback seek |
| `device.is_command_supported(command_id)` | command ID | `bool` | Guard `invoke()` calls |

### Registration and Sync

| API | Input | Output | When to use |
| --- | --- | --- | --- |
| `device.is_image_registration_mode_supported(mode)` | registration mode constant | `bool` | Check whether alignment is available |
| `device.get_image_registration_mode()` | none | registration mode enum | Read current registration mode |
| `device.set_image_registration_mode(mode)` | registration mode enum | `None` | Turn depth-to-color alignment on or off |
| `device.get_depth_color_sync_enabled()` | none | `bool` | Query frame sync status |
| `device.set_depth_color_sync_enabled(enable)` | `bool` | `None` | Ask the device to synchronize depth/color frame delivery |
| `device.depth_color_sync` | `bool` property | `bool` | Convenience property for the above |

Use registration when:

- You want to overlay depth on color.
- You want depth-based masking in the color image space.

Use depth/color sync when:

- You need temporally matched RGB and depth frames.
- You are fusing sensor data frame-by-frame.

### Playback Support

When `device.is_file()` is `True`, `device.playback` becomes available.

| API | Input | Output | When to use |
| --- | --- | --- | --- |
| `device.playback.speed` | float | float | Speed up, slow down, or pause playback |
| `device.playback.repeat` | `bool` | `bool` | Loop `.oni` playback |
| `device.playback.seek(stream, frame_index)` | `VideoStream`, frame index | `None` | Jump to a frame in a recording |
| `device.playback.get_number_of_frames(stream)` | `VideoStream` | `int` | Inspect recording length |

## SensorInfo and VideoMode

### `SensorInfo`

`SensorInfo` gives the supported modes for a sensor.

Fields:

- `sensorType`
- `videoModes`

Use it when:

- You need to discover valid resolution/fps/format combinations before calling `set_video_mode()`.

### `VideoMode`

`VideoMode` is the configuration container used by streams.

Fields:

- `pixelFormat`
- `resolutionX`
- `resolutionY`
- `fps`

Use it when:

- Reading the current stream mode.
- Setting an exact mode.
- Enumerating supported modes.

## VideoStream Class

### Core Streaming

| API | Input | Output | When to use |
| --- | --- | --- | --- |
| `stream.start()` | none | `None` | Begin frame delivery |
| `stream.stop()` | none | `None` | Stop frame delivery |
| `stream.read_frame()` | none | `VideoFrame` | Pull the next frame in a polling loop |
| `stream.close()` | none | `None` | Release the stream handle |

### Stream Information and Mode Control

| API | Input | Output | When to use |
| --- | --- | --- | --- |
| `stream.get_sensor_info()` | none | `SensorInfo` | Query supported video modes from this stream |
| `stream.get_video_mode()` | none | `VideoMode` | Inspect current width/height/fps/format |
| `stream.set_video_mode(video_mode)` | `VideoMode` | `None` | Switch to a supported mode |
| `stream.video_mode` | `VideoMode` property | `VideoMode` | Property alias for the above |
| `stream.configure_mode(width, height, fps, pixel_format)` | width, height, fps, pixel format constant | `None` | Convenience shortcut instead of constructing `VideoMode` manually |

Use `set_video_mode()` or `configure_mode()` when:

- You want lower latency or lower CPU usage at reduced resolution.
- You want higher detail for offline capture.
- You want a specific IR or depth mode to match calibration assumptions.

### Geometry and Metadata

| API | Input | Output | When to use |
| --- | --- | --- | --- |
| `stream.get_horizontal_fov()` | none | `float` radians | Lens geometry calculations |
| `stream.get_vertical_fov()` | none | `float` radians | Lens geometry calculations |
| `stream.get_max_pixel_value()` | none | `int` | Normalize depth or grayscale display |
| `stream.get_min_pixel_value()` | none | `int` | Normalize display or validate sensor output |
| `stream.get_number_of_frames()` | none | `int` | Playback streams and diagnostics |

### Cropping and Mirroring

| API | Input | Output | When to use |
| --- | --- | --- | --- |
| `stream.is_cropping_supported()` | none | `bool` | Check before hardware crop operations |
| `stream.get_cropping()` | none | `OniCropping` | Inspect crop state |
| `stream.set_cropping(originX, originY, width, height)` | crop rectangle | `None` | Hardware-level crop |
| `stream.reset_cropping()` | none | `None` | Return to full frame |
| `stream.get_mirroring_enabled()` | none | `bool` | Read mirror state |
| `stream.set_mirroring_enabled(enabled)` | `bool` | `None` | Mirror/unmirror stream output |
| `stream.mirroring_enabled` | `bool` property | `bool` | Property alias |

When to use hardware cropping:

- You want to reduce data volume before frames hit Python.
- Your region of interest is fixed.

When to use NumPy/OpenCV slicing instead:

- You need flexible ROI changes per frame.
- You want to keep the full frame available for debugging.

### Generic Stream Properties and Commands

| API | Input | Output | When to use |
| --- | --- | --- | --- |
| `stream.get_property(property_id, rettype)` | numeric property ID and ctypes-compatible type | typed value | Standard or vendor stream properties |
| `stream.get_int_property(property_id)` | numeric property ID | `int` | Shortcut for integer properties |
| `stream.set_property(property_id, obj, size=None)` | numeric property ID and value/ctypes struct | `None` | Standard or vendor stream properties |
| `stream.is_property_supported(property_id)` | numeric property ID | `bool` | Guard optional properties |
| `stream.invoke(command_id, data, size=None)` | command payload | `None` | Rare advanced cases |
| `stream.is_command_supported(command_id)` | command ID | `bool` | Guard optional commands |

### New Frame Listeners

| API | Input | Output | When to use |
| --- | --- | --- | --- |
| `stream.register_new_frame_listener(callback)` | callback `(stream) -> None` | `None` | Event-driven capture |
| `stream.unregister_new_frame_listener(callback)` | same callback object | `None` | Remove one listener |
| `stream.unregister_all_new_frame_listeners()` | none | `None` | Cleanup |

Use listeners when:

- You want callback-driven processing instead of manual polling.
- You are integrating the camera into a larger event loop.

### Recorder Helper

| API | Input | Output | When to use |
| --- | --- | --- | --- |
| `stream.get_recoder(filename, allow_lossy_compression=False)` | filename and compression flag | `Recorder` | Quick one-stream recorder setup |

Note:

- The upstream Python wrapper spells this helper as `get_recoder`, not `get_recorder`.

### Camera Settings

`stream.camera` is available when the stream supports standard camera controls. In practice this is most relevant for the color stream.

| API | Input | Output | When to use |
| --- | --- | --- | --- |
| `stream.camera.auto_exposure` | `bool` property | `bool` | Let the sensor manage exposure automatically |
| `stream.camera.auto_white_balance` | `bool` property | `bool` | Let the sensor manage white balance automatically |
| `stream.camera.gain` | `int` property | `int` | Manual image amplification |
| `stream.camera.exposure` | `int` property | `int` | Manual exposure tuning |

Use auto exposure / auto white balance when:

- Lighting changes over time.
- You care more about convenience than perfectly stable color output.

Use manual gain / exposure when:

- You need repeatable color measurements.
- You are doing calibration or dataset capture.
- Auto settings cause visible brightness or color shifts.

## VideoFrame Class

`VideoFrame` is what `stream.read_frame()` returns.

### Important Fields

These come from the wrapped `OniFrame` structure:

- `dataSize`
- `sensorType`
- `timestamp`
- `frameIndex`
- `width`
- `height`
- `videoMode`
- `croppingEnabled`
- `cropOriginX`
- `cropOriginY`
- `stride`

### Buffer Access

| API | Input | Output | When to use |
| --- | --- | --- | --- |
| `frame.get_buffer_as(ctype)` | ctypes scalar type | ctypes array view | Custom unpacking |
| `frame.get_buffer_as_uint8()` | none | `uint8` buffer | Color frames, 8-bit grayscale |
| `frame.get_buffer_as_uint16()` | none | `uint16` buffer | Depth and IR |
| `frame.get_buffer_as_triplet()` | none | RGB triplet buffer | Alternative color unpacking |

Typical NumPy conversions:

```python
rgb = np.frombuffer(
    color_frame.get_buffer_as_uint8(),
    dtype=np.uint8,
).reshape(color_frame.height, color_frame.width, 3)

depth = np.frombuffer(
    depth_frame.get_buffer_as_uint16(),
    dtype=np.uint16,
).reshape(depth_frame.height, depth_frame.width)

ir = np.frombuffer(
    ir_frame.get_buffer_as_uint16(),
    dtype=np.uint16,
).reshape(ir_frame.height, ir_frame.width)
```

## Recorder Class

| API | Input | Output | When to use |
| --- | --- | --- | --- |
| `openni2.Recorder(filename)` | output `.oni` filename as bytes/string accepted by wrapper | `Recorder` | Create a recorder |
| `recorder.attach(stream, allow_lossy_compression=False)` | `VideoStream`, compression flag | `None` | Add one stream to recording |
| `recorder.start()` | none | `None` | Begin writing frames |
| `recorder.stop()` | none | `None` | Stop writing frames |
| `recorder.close()` | none | `None` | Destroy recorder handle |

Use it when:

- You want replayable captures in NiViewer or later OpenNI processing.
- You need reproducible datasets.

The repo sample attaches all three streams:

```python
recorder.attach(color)
recorder.attach(depth)
recorder.attach(ir)
```

## DeviceListener Class

Subclass `openni2.DeviceListener` and override these hooks:

| Method | Input | Output | When to use |
| --- | --- | --- | --- |
| `on_connected(devinfo)` | `DeviceInfo` | none | Hotplug detection |
| `on_disconnected(devinfo)` | `DeviceInfo` | none | Device removal handling |
| `on_state_changed(devinfo, state)` | `DeviceInfo`, device state | none | Connection/state monitoring |
| `unregister()` | none | none | Cleanup |

Use it when:

- Your app must react to camera plug/unplug events.

## FrameAllocator Class

Advanced API for custom frame buffer allocation.

Override:

- `allocate_frame_buffer(size)`
- `free_frame_buffer(pdata)`

Then call:

- `stream.set_frame_buffers_allocator(allocator)`

Use it when:

- You are optimizing memory ownership.
- You need a custom zero-copy or pooled allocation strategy.

Most Python applications do not need this.

## Standard OpenNI Property IDs

These are useful when you want to use generic `get_property()` / `set_property()` calls instead of the convenience methods.

### Device Property IDs

| Constant | ID | Type | Meaning |
| --- | --- | --- | --- |
| `ONI_DEVICE_PROPERTY_FIRMWARE_VERSION` | `0` | string | Firmware version |
| `ONI_DEVICE_PROPERTY_DRIVER_VERSION` | `1` | `OniVersion` | Driver version |
| `ONI_DEVICE_PROPERTY_HARDWARE_VERSION` | `2` | `int` | Hardware revision |
| `ONI_DEVICE_PROPERTY_SERIAL_NUMBER` | `3` | string | Serial number |
| `ONI_DEVICE_PROPERTY_ERROR_STATE` | `4` | device-specific | Current device error state |
| `ONI_DEVICE_PROPERTY_IMAGE_REGISTRATION` | `5` | image registration enum | Registration mode |
| `ONI_DEVICE_PROPERTY_PLAYBACK_SPEED` | `100` | `float` | Playback speed |
| `ONI_DEVICE_PROPERTY_PLAYBACK_REPEAT_ENABLED` | `101` | `bool` | Playback looping |

### Stream Property IDs

| Constant | ID | Type | Meaning |
| --- | --- | --- | --- |
| `ONI_STREAM_PROPERTY_CROPPING` | `0` | `OniCropping` | Crop rectangle |
| `ONI_STREAM_PROPERTY_HORIZONTAL_FOV` | `1` | `float` | Horizontal field of view in radians |
| `ONI_STREAM_PROPERTY_VERTICAL_FOV` | `2` | `float` | Vertical field of view in radians |
| `ONI_STREAM_PROPERTY_VIDEO_MODE` | `3` | `OniVideoMode` | Width, height, fps, pixel format |
| `ONI_STREAM_PROPERTY_MAX_VALUE` | `4` | `int` | Largest possible pixel value |
| `ONI_STREAM_PROPERTY_MIN_VALUE` | `5` | `int` | Smallest possible pixel value |
| `ONI_STREAM_PROPERTY_STRIDE` | `6` | `int` | Bytes per row |
| `ONI_STREAM_PROPERTY_MIRRORING` | `7` | `bool` | Mirroring state |
| `ONI_STREAM_PROPERTY_NUMBER_OF_FRAMES` | `8` | `int` | Frame count, mainly for playback |
| `ONI_STREAM_PROPERTY_AUTO_WHITE_BALANCE` | `100` | `bool` | Auto white balance |
| `ONI_STREAM_PROPERTY_AUTO_EXPOSURE` | `101` | `bool` | Auto exposure |
| `ONI_STREAM_PROPERTY_EXPOSURE` | `102` | `int` | Manual exposure |
| `ONI_STREAM_PROPERTY_GAIN` | `103` | `int` | Manual gain |

### Device Command IDs

| Constant | ID | Payload | Meaning |
| --- | --- | --- | --- |
| `ONI_DEVICE_COMMAND_SEEK` | `1` | `OniSeek` | Seek within a playback device |

## LIPS Vendor-Specific Properties

These are the camera-specific extensions from `sdk-l210/Include/LIPSNICustomProperty.h`.

Verification note:

- Everything in this section is `Declared by LIPS SDK header`.
- These properties were not confirmed on a live camera from this session.
- Treat them as supported entry points that still need on-device validation, especially for opaque IMU and face-recognition payloads.

### How to Access Them From Python

The Python wrapper does not define symbolic constants for these LIPS properties, so use raw numeric IDs plus `device.get_property()` / `device.set_property()` or `stream.get_property()` / `stream.set_property()`.

Example: laser on/off

```python
import ctypes

LIPS_DEVICE_PROPERTY_LASER_ENABLE = 307

laser_enabled = device.get_property(
    LIPS_DEVICE_PROPERTY_LASER_ENABLE,
    ctypes.c_int,
).value

device.set_property(LIPS_DEVICE_PROPERTY_LASER_ENABLE, 1)  # on
device.set_property(LIPS_DEVICE_PROPERTY_LASER_ENABLE, 0)  # off
```

Useful ctypes structures:

```python
import ctypes

class LIPSSensorRegRWCmd(ctypes.Structure):
    _fields_ = [
        ("dev", ctypes.c_uint8),
        ("addr", ctypes.c_uint16),
        ("MSB", ctypes.c_uint8),
        ("LSB", ctypes.c_uint8),
        ("data", ctypes.c_uint32),
    ]

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
```

### Predefined LIPS Mode Values

These numeric values are explicitly defined in the header:

| Constant | Value | Meaning |
| --- | --- | --- |
| `LIPS_CONFIG_NEAR_MODE` | `0` | Near mode |
| `LIPS_CONFIG_NORMAL_MODE` | `1` | Normal mode |

### Power / Functional Mode Values

| Constant | Value | Meaning |
| --- | --- | --- |
| `STANDBY_MODE` | `0` | Standby, same as low-power mode |
| `NORMAL_OPERATION` | `1` | Active streaming mode |
| `DYN_POWER_DOWN` | `2` | Dynamic power down, noted as OPT8320-only |

### LIPS Stream Properties

| Property | ID | Type | Read/Write | When to use | Notes |
| --- | --- | --- | --- | --- | --- |
| `LIPS_STREAM_PROPERTY_FOCAL_LENGTH_X` | `200` | `float` | read | Read depth/IR intrinsics | Focal length in x |
| `LIPS_STREAM_PROPERTY_FOCAL_LENGTH_Y` | `201` | `float` | read | Read depth/IR intrinsics | Focal length in y |
| `LIPS_STREAM_PROPERTY_PRINCIPAL_POINT_X` | `202` | `float` | read | Read intrinsics | Principal point x |
| `LIPS_STREAM_PROPERTY_PRINCIPAL_POINT_Y` | `203` | `float` | read | Read intrinsics | Principal point y |
| `LIPS_STREAM_PROPERTY_IMUDATA` | `204` | opaque SDK IMU type | read | Read IMU data per stream | Header exposes the ID but not the struct layout |
| `LIPS_STREAM_PROPERTY_FOCAL_LENGTH_R` | `205` | `float` | read | Stereo calibration/debugging | Right camera focal length |
| `LIPS_STREAM_PROPERTY_FOCAL_LENGTH_L` | `206` | `float` | read | Stereo calibration/debugging | Left camera focal length |
| `LIPS_STREAM_PROPERTY_PRINCIPAL_POINT_X_R` | `207` | `float` | read | Stereo calibration/debugging | Right camera cx |
| `LIPS_STREAM_PROPERTY_PRINCIPAL_POINT_Y_R` | `208` | `float` | read | Stereo calibration/debugging | Right camera cy |
| `LIPS_STREAM_PROPERTY_PRINCIPAL_POINT_X_L` | `209` | `float` | read | Stereo calibration/debugging | Left camera cx |
| `LIPS_STREAM_PROPERTY_PRINCIPAL_POINT_Y_L` | `210` | `float` | read | Stereo calibration/debugging | Left camera cy |
| `LIPS_STREAM_PROPERTY_FOCAL_LENGTH_X_R` | `211` | `float` | read | Stereo calibration/debugging | Right x focal length |
| `LIPS_STREAM_PROPERTY_FOCAL_LENGTH_Y_R` | `212` | `float` | read | Stereo calibration/debugging | Right y focal length |
| `LIPS_STREAM_PROPERTY_FOCAL_LENGTH_X_L` | `213` | `float` | read | Stereo calibration/debugging | Left x focal length |
| `LIPS_STREAM_PROPERTY_FOCAL_LENGTH_Y_L` | `214` | `float` | read | Stereo calibration/debugging | Left y focal length |
| `LIPS_STREAM_PROPERTY_ORIGINAL_RES_X` | `215` | `int` | read | Recover native calibration resolution | Useful when current stream is cropped/scaled |
| `LIPS_STREAM_PROPERTY_ORIGINAL_RES_Y` | `216` | `int` | read | Recover native calibration resolution | Same as above |
| `LIPS_STREAM_PROPERTY_IMU_EN` | `217` | `int`/`bool` | read/write | Enable IMU on stream path | Header comments say reserved |
| `LIPS_DEPTH_IMU_ACCEL_OFFSET` | `218` | opaque SDK type | read/write | IMU calibration | String name exists, layout does not |
| `LIPS_DEPTH_IMU_GYRO_OFFSET` | `219` | opaque SDK type | read/write | IMU calibration | Same limitation |
| `LIPS_STREAM_PROPERTY_EXTRINSIC_TO_DEPTH` | `220` | `CameraExtrinsicMatrix` | read | Cross-sensor transforms | Transform into depth camera frame |
| `LIPS_STREAM_PROPERTY_EXTRINSIC_TO_COLOR` | `221` | `CameraExtrinsicMatrix` | read | RGB/depth alignment math | Transform into color camera frame |
| `LIPS_STREAM_PROPERTY_RADIAL_DISTORTION` | `222` | `RadialDistortionCoeffs` | read | Lens correction | Radial distortion coefficients |
| `LIPS_STREAM_PROPERTY_TANGENTIAL_DISTORTION` | `223` | `TangentialDistortionCoeffs` | read | Lens correction | Tangential distortion coefficients |
| `LIPS_STREAM_PROPERTY_EXTRINSIC_TO_IR` | `224` | `CameraExtrinsicMatrix` | read | Cross-sensor transforms | Transform into IR camera frame |

When to use these stream properties:

- Camera calibration export
- Custom registration pipelines
- Point cloud reprojection
- IMU-assisted fusion
- Low-level debugging against vendor tools

### LIPS Device Properties

| Property | ID | Type | Read/Write | When to use | Notes |
| --- | --- | --- | --- | --- | --- |
| `LIPS_DEVICE_NAME` | `300` | string | read | Read vendor device name | Wrapper convenience for strings is limited |
| `LIPS_DEVICE_SENSOR_INFO_IR` | `301` | SDK-specific | read | Query IR sensor info | Not typed in the header |
| `LIPS_DEVICE_SENSOR_INFO_COLOR` | `302` | SDK-specific | read | Query color sensor info | Not typed in the header |
| `LIPS_DEVICE_SENSOR_INFO_DEPTH` | `303` | SDK-specific | read | Query depth sensor info | Not typed in the header |
| `LIPS_DEVICE_CONFIG_LENS_MODE` | `304` | `int` | read/write | Switch near vs normal optical mode | Known values in header: `0=near`, `1=normal` |
| `LIPS_DEVICE_CONFIG_LENS_MODE_EXT` | `305` | `int` | read/write | Extended lens mode selection | Numeric mapping is not documented in the checked-in files |
| `LIPS_DEVICE_PROPERTY_IMUDATA` | `306` | opaque SDK IMU type | read | Read device-level IMU packets | Struct layout not included here |
| `LIPS_DEVICE_PROPERTY_LASER_ENABLE` | `307` | `int`/`bool` | read/write | Turn projector/laser on or off | Header explicitly says `1=on`, `0=off` |
| `LIPS_DEVICE_PROPERTY_IMU_EN` | `308` | `int`/`bool` | read/write | Enable or disable IMU globally | Use before streaming IMU data |

When to use device-level controls:

- `LIPS_DEVICE_CONFIG_LENS_MODE`: choose a short-range vs general-range configuration.
- `LIPS_DEVICE_PROPERTY_LASER_ENABLE`: reduce interference, power, or eye-safety exposure when the emitter is not needed.
- `LIPS_DEVICE_PROPERTY_IMU_EN`: turn on motion data before reading IMU packets.

### LIPS Sensor Properties

| Property | ID | Type | Read/Write | When to use | Notes |
| --- | --- | --- | --- | --- | --- |
| `LIPS_DEPTH_SENSOR_READ_REGISTER` | `400` | `LIPSSensorRegRWCmd` | invoke/read | Raw register inspection | Advanced and risky if you do not know the sensor register map |
| `LIPS_DEPTH_SENSOR_WRITE_REGISTER` | `401` | `LIPSSensorRegRWCmd` | write | Raw sensor tuning | Only use with vendor guidance |
| `LIPS_DEPTH_SENSOR_TEMPERATURE` | `402` | likely `float` | read | Thermal monitoring | Header string name is `sensor_temp` |
| `LIPS_DEPTH_SENSOR_LOW_POWER_EN` | `403` | `int`/`bool` | read/write | Enter or exit low-power mode | Header says `1=low-power`, `0=normal` |

When to use sensor properties:

- Temperature checks during long captures
- Controlled power-state changes
- Vendor-supported raw tuning or diagnostics

### Deprecated Property

| Property | ID | Type | Meaning |
| --- | --- | --- | --- |
| `LIPS_CONFIG_LENS_MODE` | `500` | `int` | Deprecated, replaced by `LIPS_DEVICE_CONFIG_LENS_MODE` |

### Face Recognition Properties

These are listed in the header even though this repo does not include Python samples for them.

| Property | ID | Type | Read/Write | Use |
| --- | --- | --- | --- | --- |
| `LIPS_DEVICE_FACE_RECOGNITION` | `600` | vendor-defined payload/result | read/write | Trigger recognition and read result |
| `LIPS_DEVICE_FACE_REGISTRATION` | `601` | vendor-defined payload/result | read/write | Enroll a new face |
| `LIPS_DEVICE_FACE_DELETE_DATABASE` | `602` | vendor-defined payload/result | read/write | Delete one or all enrolled faces |
| `LIPS_DEVICE_FACE_NUMBER_REGISTERED` | `603` | integer-like result | read | Check how many faces are stored |

Use them only if:

- Your camera firmware and SDK bundle include the LIPSFace-capable feature set.
- You have the exact vendor workflow and expected payload/result types.

## Driver JSON Settings in This Repo

The vendor driver bundle in this repo also exposes a small configuration file:

- `sdk-l210/Redist/OpenNI2/Drivers/LIPSedge-L210.json`
- `sdk-l210/Tools/OpenNI2/Drivers/LIPSedge-L210.json`

Current keys:

| JSON path | Current value in repo | Meaning | When to change it |
| --- | --- | --- | --- |
| `debug.logLevel` | `verbose` | Driver log verbosity | Increase for debugging, reduce for quieter logs |
| `debug.defaultRes` | `VGA` | Default startup resolution | Set a preferred default when tools open the camera |
| `debug.showFPS.enable` | `false` | On-screen FPS display | Enable during profiling or debugging |
| `debug.showFPS.interval` | `10` | FPS update interval | Tune how often FPS is refreshed |
| `post-processing.enable` | `false` | Enables the vendor post-processing stage | Use when you want filtered depth output from the driver |
| `post-processing.debug` | `false` | Extra post-processing diagnostics | Enable only while debugging |
| `post-processing.sigma-spatial` | `40` | Spatial smoothing strength | Raise for smoother depth, lower for sharper edges |
| `post-processing.sigma-range` | `21` | Range-domain smoothing strength | Raise to smooth noisy depth bands, lower to preserve depth discontinuities |

Notes:

- These are driver/tool settings, not `openni2` Python methods.
- They affect the vendor driver behavior before frames reach Python.
- The file in this repo is small and not a full schema reference, so treat these as the settings known to exist here.

## Practical Task-to-API Map

| Task | Best API / sample | Why |
| --- | --- | --- |
| Detect the camera and print identity | `hello-lipsedge-sdk.py` | Minimal connectivity check |
| Preview RGB, depth, and IR | `opencv_viewer.py` | Straightest live-view pipeline |
| Read one pixel's depth | `depth-data.py` | Fast way to inspect metric depth values |
| Crop to a region of interest | `roi.py` or `stream.set_cropping(...)` | OpenCV ROI is simpler, hardware crop is more efficient |
| Overlay depth on color | `align-depth-color.py` plus registration | Correct geometric alignment |
| Segment a person or object by distance | `range-filter.py` / `remove-background.py` | Uses the depth stream's millimeter values directly |
| Record a replayable session | `record.py` | Produces `.oni` files usable in OpenNI tools |
| Enumerate supported modes | `device.get_sensor_info(...).videoModes` | Discover valid width/height/fps/format tuples |
| Build a point cloud or 3D measurements | `convert_depth_to_world(...)` | Maps image pixels into metric 3D space |
| Do custom calibration / registration math | LIPS stream properties `200-224` | Gives intrinsics, extrinsics, and distortion data |
| Change optical working mode | LIPS device property `304` | Near/normal lens mode |
| Turn the emitter on or off | LIPS device property `307` | Direct hardware control |
| Enable IMU access | LIPS device properties `308` and `306` or stream `204` | Motion-aware applications |

## Sample Scripts in This Repo

| File | What it demonstrates |
| --- | --- |
| `dev-doc-code-samples/python/A_environment_setup/environment_setup.py` | Verifies environment setup |
| `dev-doc-code-samples/python/B_hello-lipsedge-sdk/hello-lipsedge-sdk.py` | Device enumeration and camera info |
| `dev-doc-code-samples/python/C_opencv_viewer/opencv_viewer.py` | RGB/depth/IR acquisition and display |
| `dev-doc-code-samples/python/D_roi/roi.py` | ROI extraction |
| `dev-doc-code-samples/python/E_depth-data/depth-data.py` | Pixel-by-pixel depth readout |
| `dev-doc-code-samples/python/F_align-depth-color/align-depth-color.py` | Registration and overlay |
| `dev-doc-code-samples/python/G_range-filter/range-filter.py` | Depth thresholding by distance |
| `dev-doc-code-samples/python/H_remove-background/remove-background.py` | Background removal with registered depth |
| `dev-doc-code-samples/python/I_record/record.py` | `.oni` recording |

## Caveats and Repo-Specific Notes

- The Python package `openni` is an OpenNI wrapper, not a LIPS-specific Python SDK. LIPS-specific features come through generic numeric property IDs.
- The wrapper exposes many C-level capabilities but not all of them ergonomically. Device string properties and opaque vendor structs may require extra ctypes work.
- The checked-in `camera_intrinsics.json` includes intrinsics and calibrated resolutions but does not enumerate every supported FPS value.
- `sdk-l210/Redist/OpenNI2/Drivers/LIPSedge-L210.json` contains a small driver config block for debug and post-processing, but it is not a complete capability table.
- The upstream wrapper function `get_bytes_per_pixel()` appears incomplete because it does not return the C API value.
- The upstream wrapper helper name `get_recoder()` is misspelled.

## Minimal Utility Snippets

### Check registration support

```python
from openni import openni2

if device.is_image_registration_mode_supported(
    openni2.IMAGE_REGISTRATION_DEPTH_TO_COLOR
):
    device.set_image_registration_mode(
        openni2.IMAGE_REGISTRATION_DEPTH_TO_COLOR
    )
```

### Switch to a chosen mode

```python
from openni import openni2

depth = device.create_depth_stream()
depth.configure_mode(
    width=640,
    height=480,
    fps=30,
    pixel_format=openni2.PIXEL_FORMAT_DEPTH_1_MM,
)
depth.start()
```

If your device advertises the higher-resolution depth format in `videoModes`, you can request that instead:

```python
depth.configure_mode(
    width=640,
    height=480,
    fps=30,
    pixel_format=openni2.PIXEL_FORMAT_DEPTH_100_UM,
)
```

### Read intrinsics from LIPS custom properties

```python
import ctypes

fx = depth.get_property(200, ctypes.c_float).value
fy = depth.get_property(201, ctypes.c_float).value
cx = depth.get_property(202, ctypes.c_float).value
cy = depth.get_property(203, ctypes.c_float).value
print(fx, fy, cx, cy)
```

### Read one extrinsic transform

```python
extr = depth.get_property(221, CameraExtrinsicMatrix)

rotation = [[extr.rotation[r][c] for c in range(3)] for r in range(3)]
translation_mm = [extr.translation[i] for i in range(3)]
```

### Toggle low-power mode

```python
LIPS_DEPTH_SENSOR_LOW_POWER_EN = 403

device.set_property(LIPS_DEPTH_SENSOR_LOW_POWER_EN, 1)  # low power
device.set_property(LIPS_DEPTH_SENSOR_LOW_POWER_EN, 0)  # normal
```

## Bottom Line

If you only need to build applications, the main things to remember are:

- Use `Device`, `VideoStream`, `VideoFrame`, `Recorder`, and the coordinate converters from `openni2`.
- Use registration for RGB/depth alignment and `convert_depth_to_world()` for real 3D geometry.
- Use `get_sensor_info(...).videoModes` before changing modes.
- Use LIPS custom property IDs when you need calibration data, laser control, lens mode switching, IMU access, temperature, or low-level sensor control.

What I could and could not verify from this environment:

- Verified: the Python binding imports from `.venv`, and the documented core API names are real.
- Verified: the repo samples cover the documented workflows for streaming, registration, thresholding, background removal, and recording.
- Not verified live: camera connection, supported mode list from the actual device, and LIPS custom property behavior on your attached unit.
