import ctypes
import os
from pathlib import Path


def prepare_openni() -> None:
    root = Path(__file__).resolve().parents[2]
    sdk = root / "sdk-l210"
    ctypes.CDLL(str(sdk / "compat" / "libtbb.so.2"), mode=ctypes.RTLD_GLOBAL)
    os.environ["OPENNI2_REDIST"] = str(sdk / "Redist")
