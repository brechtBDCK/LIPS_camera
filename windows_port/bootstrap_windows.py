import os
from pathlib import Path

DEFAULT_SDK_DIR = Path(r"C:\Program Files\LIPSedge Camera SDK 1.1.0\L210\OpenNI2")


def prepare_openni_windows() -> Path:
    sdk_dir = Path(os.environ.get("LIPS_OPENNI2_DIR", DEFAULT_SDK_DIR))
    redist = sdk_dir / "Redist"
    if not redist.exists():
        redist = sdk_dir

    dll_path = redist / "OpenNI2.dll"
    if not dll_path.exists():
        raise FileNotFoundError(
            f"OpenNI2.dll not found in {redist}. "
            "Set LIPS_OPENNI2_DIR to the folder that contains OpenNI2.dll or its Redist parent."
        )

    os.environ["OPENNI2_REDIST"] = str(redist)

    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(str(redist))

    return redist
