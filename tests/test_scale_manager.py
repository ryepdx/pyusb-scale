import unittest
import mocks
from scale_manager import ScaleManager

class TestScaleManagerFind(unittest.TestCase):
    def setUp(self):
        self.manager = ScaleManager(
            lookup=mocks.usb_ids.USB_IDS,
            usb_lib=mocks.usb_lib.MockUSBLib()
        )

    def test_find_empty(self):
        """Make sure it finds a scale by default."""

        device = self.manager.find()
        self.assertEqual(device.idProduct, mocks.usb_ids.SCALE)
        
    def test_find_vendor(self):
        """Make sure it can find a manufacturer by name."""

        device = self.manager.find(manufacturer="Fake Vendor")
        self.assertEqual(device.idVendor, mocks.usb_ids.FAKE_VDR)

    def test_find_both_scale(self):
        """Make sure it can find a scale when both arguments are supplied."""

        device = self.manager.find(
            manufacturer="Faux Manufacturer",
            model="Faux Scale"
        )
        self.assertEqual(device.idVendor, mocks.usb_ids.FAUX_MFR)
        self.assertEqual(device.idProduct, mocks.usb_ids.SCALE)

    def test_find_both_other(self):
        """Make sure it find anything when both arguments are supplied."""

        device = self.manager.find(
            manufacturer="Fake Vendor",
            model="Fake Device of Some Other Stripe"
        )
        self.assertEqual(device.idVendor, mocks.usb_ids.FAKE_VDR)
        self.assertEqual(device.idProduct, mocks.usb_ids.OTHER)

    def test_find_scale(self):
        """Make sure it can find a scale when only the model is supplied."""

        device = self.manager.find(model="Fake Scale")
        self.assertEqual(device.idProduct, mocks.usb_ids.SCALE)

    def test_find_neither(self):
        """Make sure it finds nothing when nothing matches exactly."""

        device = self.manager.find(
            manufacturer="Fake Vendor",
            model="DNE"
        )
        self.assertEqual(device, None)
