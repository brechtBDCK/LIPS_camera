import os
import sys
from pathlib import Path
from openni import openni2

sys.path.append(str(Path(__file__).resolve().parents[1]))
from bootstrap import prepare_openni

prepare_openni()

openni2.initialize(os.environ['OPENNI2_REDIST'])
uris = openni2.Device.enumerate_uris()

if not uris:
    print('Camera not found')
    sys.exit(0)

device = openni2.Device.open_any()
deviceInfo = device.get_device_info()
print(f'Name: {deviceInfo.name}')
print(f'Uri: {deviceInfo.uri}')
print(f'USB Product ID: {deviceInfo.usbProductId}')
print(f'USB Vendor ID: {deviceInfo.usbVendorId}')
print(f'Vendor: {deviceInfo.vendor}')


device.close()
openni2.unload()
