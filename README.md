pyusb-scale
===========

Wrote this for the purpose of interfacing with a Mettler-Toledo PS60 scale, but it should work for any other scale that supports the [Universal Serial Bus HID Point of Sale Usage Tables](http://www.usb.org/developers/devclass_docs/pos1_02.pdf).

Requires [PyUSB](https://github.com/walac/pyusb).

Run tests from the project root with [unittest2](https://pypi.python.org/pypi/unittest2):

    unit2 discover

Feature-complete, but not yet production-tested. Be prepared to fix and extend this library as you have need. (And remember to issue pull requests for your changes!)

## Example

Assuming you've pulled this repository into a directory called `scale`:

    from scale import Scale
    scale = Scale()
    reading = scale.weigh()
    
Assuming you're weighing a 1 pound object and your scale is set to "pounds":

    reading.weight == 1.0 # True
    reading.unit == "pounds" # True

This is a very simple example. If you want to dive in deeper, try examining the unit tests.
