from collections import namedtuple
from .usb_ids import FAUX_MFR, FAKE_VDR, SCALE, OTHER

MockDevice = namedtuple('MockDevice', ['idVendor', 'idProduct'])

class MockUSBLib(object):
    def __init__(self):
        self.devices = [
            MockDevice(FAUX_MFR, SCALE),
            MockDevice(FAUX_MFR, OTHER),
            MockDevice(FAKE_VDR, SCALE),
            MockDevice(FAKE_VDR, OTHER),
        ]

    def find(self, find_all=False, idVendor=None, idProduct=None):
        if find_all:
            return self.devices

        for device in self.devices:
            if (not idVendor or device.idVendor == idVendor)\
            and (not idProduct or device.idProduct == idProduct):
                return device

        return None
