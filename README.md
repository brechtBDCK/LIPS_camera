# LIPS Camera

Small Python workspace for testing a LIPS camera with OpenNI and OpenCV.
Ideal working distance: 40-120 cm
avoid installing the camera at places under direct sunlight or with an illumination level above 1000 lux.

Tested on WSL, ubuntu version 24

## Setup

Install dependencies:

```bash
uv sync
```

Set the OpenNI redistributable path:

```bash
export OPENNI2_REDIST="$PWD/sdk-l210/Redist"
export OPENNI2_INCLUDE="$PWD/sdk-l210/Include"
```

On Ubuntu 24.04 (`noble`), the vendor L210 driver does not install cleanly out of the box.
It links against the legacy Intel TBB runtime `libtbb.so.2` (`libtbb2`), while 24.04 ships `libtbb12` (`libtbb.so.12`).
Use Ubuntu 22.04/20.04 for the packaged installer, or manually provide a compatible `libtbb2` runtime before running `sdk-l210/install.sh`.

## Run

```bash
uv run python main.py
```

## Camera stream options
== color stream ==
[OK] sensor info: 2 supported mode(s)
  - mode[0] 640x480 30fps format=OniPixelFormat.ONI_PIXEL_FORMAT_RGB888
  - mode[1] 1280x800 15fps format=OniPixelFormat.ONI_PIXEL_FORMAT_RGB888
[OK] standard property cropping: id=0
[OK] standard property horizontal_fov: id=1
[OK] standard property vertical_fov: id=2
[OK] standard property video_mode: id=3
[OK] standard property mirroring: id=7
[OK] standard property auto_white_balance: id=100
[OK] standard property auto_exposure: id=101
[OK] standard property exposure: id=102
[OK] standard property gain: id=103
[OK] depth availability

== depth stream ==
[OK] sensor info: 4 supported mode(s)
  - mode[0] 640x400 30fps format=OniPixelFormat.ONI_PIXEL_FORMAT_DEPTH_1_MM
  - mode[1] 640x400 30fps format=OniPixelFormat.ONI_PIXEL_FORMAT_DEPTH_100_UM
  - mode[2] 1280x800 30fps format=OniPixelFormat.ONI_PIXEL_FORMAT_DEPTH_1_MM
  - mode[3] 1280x800 30fps format=OniPixelFormat.ONI_PIXEL_FORMAT_DEPTH_100_UM
[OK] standard property cropping: id=0
[OK] standard property horizontal_fov: id=1
[OK] standard property vertical_fov: id=2
[OK] standard property video_mode: id=3
[OK] standard property max_value: id=4
[OK] standard property min_value: id=5
[OK] standard property stride: id=6
[OK] standard property mirroring: id=7
[OK] ir availability

== ir stream ==
[OK] sensor info: 2 supported mode(s)
  - mode[0] 640x400 30fps format=OniPixelFormat.ONI_PIXEL_FORMAT_GRAY16
  - mode[1] 1280x800 30fps format=OniPixelFormat.ONI_PIXEL_FORMAT_GRAY16
[OK] standard property cropping: id=0
[OK] standard property horizontal_fov: id=1
[OK] standard property vertical_fov: id=2
[OK] standard property video_mode: id=3
[OK] standard property mirroring: id=7
