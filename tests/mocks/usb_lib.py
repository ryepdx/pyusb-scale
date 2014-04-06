from array import array
from collections import namedtuple
from .usb_ids import FAUX_MFR, FAKE_VDR, SCALE, OTHER

MockEndpoint = namedtuple(
    "MockEndpoint", ["bEndpointAddress", "wMaxPacketSize"]
)

class MockCtx(object):
    """Simulates the _ctx property expected by usb.util.dispose_resources""" 
    def dispose(self, *args, **kwargs):
        return True

class MockDevice(object):
    """Simulates a device returned by usb.core.find"""

    def __init__(self, idVendor, idProduct):
        self.idVendor = idVendor
        self.idProduct = idProduct
    
        # Actual output recorded from a Mettler Toledo PS60.
        self._weights = {
            "0 lb": array('B', [3, 2, 12, 254, 0, 0]),
            "5.10 lb": array('B', [3, 4, 12, 254, 254, 1]),
            "0 kg": array('B', [3, 2, 3, 254, 0, 0]),
            "1.94 kg": array('B', [3, 4, 3, 254, 194, 0])
        }
        self._weight = "0 lb"
        self._readied = False
        self._ctx = MockCtx()

    def read(self, *args):
        # Simulate the alternating output of the scale.
        if not self._readied:
            self._readied = True
            return array('B', [4, 4])

        return self._weights[self._weight]

    def set_weight(self, weight):
        """For testing. Sets the output 'read' should return."""

        if weight not in self._weights:
            raise Exception("No mock data for " + weight)

        self._weight = weight

    def is_kernel_driver_active(self, *args):
        return True

    def detach_kernel_driver(self, *args):
        return True

    def set_configuration(self, *args):
        return True

    def attach_kernel_driver(self, *args):
        return True


class MockUSBLib(object):
    """Simulates usb.lib.core"""

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
