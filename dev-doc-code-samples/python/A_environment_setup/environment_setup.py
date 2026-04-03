import os
import sys
from pathlib import Path
import cv2

sys.path.append(str(Path(__file__).resolve().parents[1]))
from bootstrap import prepare_openni

prepare_openni()

print(os.environ['OPENNI2_REDIST'])
print(cv2.__version__)
