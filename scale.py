#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
import usb.util
from collections import namedtuple
from scale_manager import ScaleManager
from reports import \
        ReportFactory, STATUSES, ZERO_WEIGHT, STABLE_WEIGHT, DATA_REPORT

ScaleReading = namedtuple("ScaleReading", ["weight", "unit"])

class ConnectionError(Exception):
    pass

class Scale(object):
    """Represents a USB-connected scale."""

    def __init__(self, device=None, manufacturer=None, model=None, device_manager=None):
        """
        Instantiates a Scale object.
        
        If no arguments are passed, it wraps itself around whatever device
        calling `device_manager.find` returns and automatically fills in
        its `manufacturer` and `model` properties according to what
        `device_manager.get_manufacturer` and `device_manager.get_model`
        return, respectively.
        
        If a `device` argument is passed, the Scale object wraps it and
        treats it like a PyUSB device.

        If a `device` argument is passed and `manufacturer` and/or `model`
        are omitted, the Scale object will query the `device_manager` object
        to discover and populate the Scale's `manufacturer` and `model`
        properties.
        
        If `manufacturer`, and/or `model` are passed and `device` is omitted,
        Scale will wrap the device returned when those arguments are passed
        to `device_manager.find`.
        
        If `manufacturer`, and/or `model`, and `device` are all passed,
        then the Scale object wraps `device` and sets its own `manufacturer`,
        `model`, and `name` properties accordingly, regardless of `device`'s
        *actual* manufacturer and model.

        If a `device_manager` argument is passed, it uses that object
        instead of a ScaleManager instance to find the attached scale.

        """
        if not device_manager:
            device_manager = ScaleManager()

        device = device_manager.find(manufacturer=manufacturer, model=model)

        if not manufacturer and device:
            manufacturer = device_manager.get_manufacturer(device)

        if not model and device:
            model = device_manager.get_model(device)

        self._device = device
        self._model = model
        self._manufacturer = manufacturer
        self._manager = device_manager
        self._endpoint = None
        self._last_reading = None

        # Initialize the USB connection to the scale.
        if self.device:
            self.connect()
    

    ### Read-only public properties ###

    @property
    def model(self):
        return self._model

    @property
    def manufacturer(self):
        return self._manufacturer

    @property
    def name(self):
        return self.manufacturer + " " + self.model

    @property
    def device(self):
        return self._device

    @property
    def manager(self):
        return self._manager
    
    ### Public methods ###

    def connect(self):
        """Prepares the scale for being read."""
        if not self.device:
            return False

        self._reattach = False
        
        try:
            if self.device.is_kernel_driver_active(0):
                self._reattach = True
                self.device.detach_kernel_driver(0)
        except NotImplementedError:
            pass # libusb-win32 does not implement `is_kernel_driver_active`

        self.device.set_configuration()

        return True

    def disconnect(self):
        """Frees the scale up for other programs/objects to use."""
        if not self.device:
            return False

        self._device.reset()
        usb.util.dispose_resources(self.device)

        try:
            if self._reattach:
                self.device.attach_kernel_driver(0)
        except NotImplementedError:
            pass # libusb-win32 does not implement `is_kernel_driver_active`

        return True

    def weigh(self, endpoint=None, max_attempts=10):
        """Reads from the scale until a stable weight is found"""
        weighed = False
        attempts = 0
        
        while not weighed and attempts < max_attempts:
            attempts += 1
            report = self.read(endpoint=endpoint)

            if not report:
                raise ConnectionError("Scale not found!")

            weighed = (report.type == DATA_REPORT and (
                report.status == STATUSES[STABLE_WEIGHT]
                or report.status == STATUSES[ZERO_WEIGHT]
            ))

        if not weighed:
            report = None

        return report

    def read(self, endpoint=None, max_attempts=10):
        """Takes a reading from the scale and returns a named tuple"""
        if not self.device:
            return False

        data = None
        error = None
        attempts = 0

        if not endpoint:
            endpoint = self.device[0][(0,0)][0]

        # Weighing data consists of a six-element array.
        # In between reads, it returns a two-element array to
        # demonstrate readiness. We can ignore those.
        while not data and attempts < max_attempts:
            attempts += 1
            try:
                data = self.device.read(
                    endpoint.bEndpointAddress,
                    endpoint.wMaxPacketSize
                )
            except Exception as e:
                error = e

        if error and not data:
            raise error

        return ReportFactory.build(data)


    ### Private methods ###

    def __str__(self):
        return self.name

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type, value, traceback):
        self.disconnect()

    def __del__(self):
        self.disconnect
