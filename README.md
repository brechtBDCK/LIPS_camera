# LIPS Camera

Small Python workspace for testing a LIPS camera with OpenNI and OpenCV.

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
```

## Run

```bash
uv run python main.py
```
