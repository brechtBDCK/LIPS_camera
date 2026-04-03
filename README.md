# LIPS Camera

Small Python workspace for testing a LIPS camera with OpenNI and OpenCV.
Ideal working distance: 40-120 cm
avoid installing the camera at places under direct sunlight or with an illumination level above 1000 lux.

Standard camera settings can be adjustment in the LIPSedge-L210.json
## Files

- `main.py` prints the detected OpenNI version and OpenCV version.
- `camera_intrinsics.json` contains a JSON summary of the camera intrinsics.
- `dev-doc-code-samples/python/` contains vendor sample scripts.

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
