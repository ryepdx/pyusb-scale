import unittest
import mocks
from scale_manager import ScaleManager
from scale import Scale
from reports import WEIGHT_UNITS

KILOS = WEIGHT_UNITS[0x3]
POUNDS = WEIGHT_UNITS[0xC]

class TestScale(unittest.TestCase):
    def setUp(self):
        self.manager = ScaleManager(
            lookup=mocks.usb_ids.USB_IDS,
            usb_lib=mocks.usb_lib.MockUSBLib()
        )
        self.endpoint = mocks.usb_lib.MockEndpoint(0, 0) 

    def test_empty_constructor(self):
        """Make sure it finds a scale by default."""

        scale = Scale(device_manager=self.manager)
        self.assertEqual(scale.device.idProduct, mocks.usb_ids.SCALE)
        
    def test_vendor_constructor(self):
        """Make sure it can find a manufacturer by name."""

        scale = Scale(device_manager=self.manager, manufacturer="Fake Vendor")
        self.assertEqual(scale.device.idVendor, mocks.usb_ids.FAKE_VDR)
        self.assertIn("Fake Vendor", scale.name)

    def test_both_scale_constructor(self):
        """Make sure it can find a scale when both arguments are supplied."""

        scale = Scale(
            device_manager=self.manager, 
            manufacturer="Faux Manufacturer",
            model="Faux Scale"
        )
        self.assertEqual(scale.device.idVendor, mocks.usb_ids.FAUX_MFR)
        self.assertEqual(scale.device.idProduct, mocks.usb_ids.SCALE)
        self.assertIn("Faux Manufacturer", scale.name)
        self.assertIn("Faux Scale", scale.name)

    def test_both_other_constructor(self):
        """Make sure it find anything when both arguments are supplied."""

        scale = Scale(
            device_manager=self.manager, 
            manufacturer="Fake Vendor",
            model="Fake Device of Some Other Stripe"
        )
        self.assertEqual(scale.device.idVendor, mocks.usb_ids.FAKE_VDR)
        self.assertEqual(scale.device.idProduct, mocks.usb_ids.OTHER)
        self.assertIn("Fake Vendor", scale.name)
        self.assertIn("Fake Device of Some Other Stripe", scale.name)

    def test_scale_constructor(self):
        """Make sure it can find a scale when only the model is supplied."""

        scale = Scale(device_manager=self.manager, model="Fake Scale")
        self.assertEqual(scale.device.idProduct, mocks.usb_ids.SCALE)

    def test_neither_constructor(self):
        """Make sure it finds nothing when nothing matches exactly."""

        scale = Scale(
            device_manager=self.manager, 
            manufacturer="Fake Vendor",
            model="DNE"
        )
        self.assertEqual(scale.device, None)

    def test_weigh_0_lb(self):
        """Make sure the scale properly weighs zero pounds."""
        with Scale(device_manager=self.manager) as scale:
            scale.device.set_weight("0 lb")
            weighing = scale.weigh(endpoint=self.endpoint)
            self.assertEqual(weighing.weight, 0)
            self.assertEqual(weighing.unit, POUNDS)

    def test_weigh_5_lb(self):
        """Make sure the scale properly weighs zero ounces."""
        with Scale(device_manager=self.manager) as scale:
            scale.device.set_weight("5.10 lb")
            weighing = scale.weigh(endpoint=self.endpoint)
            self.assertEqual(weighing.weight, 5.10)
            self.assertEqual(weighing.unit, POUNDS)

    def test_weigh_0_kg(self):
        """Make sure the scale properly weighs zero kilos."""
        with Scale(device_manager=self.manager) as scale:
            scale.device.set_weight("0 kg")
            weighing = scale.weigh(endpoint=self.endpoint)
            self.assertEqual(weighing.weight, 0)
            self.assertEqual(weighing.unit, KILOS)

    def test_weigh_2_kg(self):
        """Make sure the scale properly weighs 1.94 kilograms."""
        with Scale(device_manager=self.manager) as scale:
            scale.device.set_weight("1.94 kg")
            weighing = scale.weigh(endpoint=self.endpoint)
            self.assertEqual(weighing.weight, 1.94)
            self.assertEqual(weighing.unit, KILOS)
