#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

class ScaleManager(object):
    """Handles finding devices and device names."""

    def __init__(self, lookup=None, usb_lib=None):
        """
        `lookup` should be a dictionary of dictionaries, with keys in the
        outer dictionary corresponding to vendor ID integers and keys in
        the inner dictionaries corresponding to product ID integers and
        associating with product name strings, with the exception of
        the required "name" key, which should correspond with the vendor's
        name string.

        `usb_lib` should be an object that implements PyUSB's usb.core.find
        method.

        Both arguments are optional. If omitted, `lookup` defaults to
        `usb_ids.USB_IDS` and `usb_lib` defaults to PyUSB's `usb.core`.

        """
        if not usb_lib:
            import usb.core
            usb_lib = usb.core

        if not lookup:
            import usb_ids
            lookup = usb_ids.USB_IDS

        self._lookup = lookup
        self._usb = usb_lib


    ### Read-only public properties ###

    @property
    def usb(self):
        return self._usb


    ### Public methods ###

    def find(self, manufacturer=None, model=None):
        """
        Finds the closest matching device available.
        Returns None if no devices are available.
        
        If no arguments are passed, it finds the
        first device that has " Scale" in its model
        name as returned by `get_model`.
        Returns None if none are found.

        """
        devices = self._usb.find(find_all=True)

        # Returns none if no devices are available.
        if not devices:
            return None

        # If no arguments are passed, returns the first
        # device with " Scale" in its model name.
        # Returns None if none are found.
        if not manufacturer and not model:
            for device in devices:
                if " Scale" in self.get_model(device):
                    return device
            return None

        # Finds the device closest matching the passed-in values...
        for device in devices:
            if (not manufacturer or manufacturer == self.get_manufacturer(device))\
            and (not model or model == self.get_model(device)):
                return device

        # ...and returns None if none are found.
        return None

    def get_manufacturer(self, device):
        """
        Looks up the device's idVendor property in the `lookup`
        dictionary set at ScaleManager's instantiation and returns
        the value assigned to the "name" key in the associated
        dictionary.
        
        Returns a generic string with the property value if there
        is no key corresponding to the idVendor property in the
        `lookup` dictionary or if there is no key corresponding
        to the "name" key in the associated dictionary.

        """
        if device.idVendor in self._lookup \
        and "name" in self._lookup[device.idVendor]:
            return self._lookup[device.idVendor]["name"]
        return "<idVendor:%s>" % device.idVendor

    def get_model(self, device):
        """"
        Looks up the device's idVendor property in the `lookup`
        dictionary set at ScaleManager's instantiation and returns
        the value assigned to the device's idProduct property in
        the associated dictionary.

        Returns a generic string with the property value if there
        is no key corresponding to the idVendor property in the
        `lookup` dictionary or if there is no key corresponding to
        the device's idProduct property in the associated dictionary.

        """
        if device.idVendor in self._lookup \
        and device.idProduct in self._lookup[device.idVendor]:
            return self._lookup[device.idVendor][device.idProduct]
        return "<idProduct:%s>" % device.idProduct


