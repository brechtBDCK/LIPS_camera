import os
from openni import openni2
import cv2

openni2.initialize(os.environ['OPENNI2_REDIST'])

openniVersion = openni2.get_version()
print(f'''OpenNI Version: {openniVersion.build}.{openniVersion.major}.{openniVersion.minor}.{openniVersion.maintenance}''')
print(cv2.__version__)

openni2.unload()
