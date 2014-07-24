from collections import namedtuple
from decimal import Decimal

ATTRIBUTES_REPORT = 0x1
CONTROL_REPORT = 0x2
DATA_REPORT = 0x3
STATUS_REPORT = 0x4
WEIGHT_LIMIT_REPORT = 0x5
STATISTICS_REPORT = 0x6

WEIGHT_UNITS = {
    0x1: "milligram",
    0x2: "gram",
    0x3: "kilogram",
    0x4: "carat",
    0x5: "tael",
    0x6: "grain",
    0x7: "pennyweight",
    0x8: "metric ton",
    0x9: "avoir ton",
    0xA: "troy ounce",
    0xB: "ounce",
    0xC: "pound",
    0xD: "reserved (0xD)",
    0xE: "reserved (0xE)",
    0xF: "reserved (0xF)"
}

SCALE_CLASSES = {
    0x1: "Scale Class I Metric",
    0x2: "Scale Class I Metric",
    0x3: "Scale Class II Metric",
    0x4: "Scale Class III Metric",
    0x5: "Scale Class IIIL Metric",
    0x6: "Scale Class IV Metric",
    0x7: "Scale Class III English",
    0x8: "Scale Class IIIL English",
    0x9: "Scale Class IV English",
    0xA: "Scale Class Generic",
    0xB: "Reserved (0x2B)",
    0xC: "Reserved (0x2C)",
    0xD: "Reserved (0x2D)",
    0xE: "Reserved (0x2E)",
    0xF: "Reserved (0x2F)"
}

STATUSES = {
    0x1: "Fault",
    0x2: "Stable at Center of Zero",
    0x3: "In Motion",
    0x4: "Weight Stable",
    0x5: "Under Zero",
    0x6: "Over Weight Limit",
    0x7: "Requires Calibration",
    0x8: "Requires Re-zeroing",
    0x9: "Reserved (0x9)",
    0xA: "Reserved (0xA)",
    0xB: "Reserved (0xB)",
    0xC: "Reserved (0xC)",
    0xD: "Reserved (0xD)",
    0xE: "Reserved (0xE)",
    0xF: "Reserved (0xF)",
    0x10: "Zero Scale",
    0x11: "Enforced Zero Return"
}

ZERO_WEIGHT = 0x2
STABLE_WEIGHT = 0x4


AttributesReport = namedtuple(
    "AttributesReport", ["type", "raw", "scale_class", "unit"]
)
ControlReport = namedtuple(
    "ControlReport", ["type", "raw", "zero_scale", "enforced_zero_return"]
)
DataReport = namedtuple(
    "DataReport", ["type", "raw", "status", "unit", "weight"]
)
StatusReport = namedtuple(
    "StatusReport", ["type", "raw", "status"]
)
WeightLimitReport = namedtuple(
    "WeightLimitReport", ["type", "raw", "unit", "weight"]
)
StatisticsReport = namedtuple(
    "StatisticsReport", ["type", "raw", "calibration_count", "rezero_count"]
)

class ReportFactory(object):
    @classmethod
    def build(cls, data):
        """Returns a named tuple report based on the given data array"""
        if data[0] == ATTRIBUTES_REPORT:
            return AttributesReport(ATTRIBUTES_REPORT, data,
                SCALE_CLASSES[data[1]], WEIGHT_UNITS[data[2]]
            )

        if data[0] == CONTROL_REPORT:
            return ControlReport(CONTROL_REPORT, data,
                (data[1] > 1), ((data[1] % 2) == 1)
            )

        if data[0] == DATA_REPORT:
            return DataReport(DATA_REPORT, data,
                STATUSES[data[1]], WEIGHT_UNITS[data[2]],
                cls.calc_weight(data[3], data[4], data[5])
            )

        if data[0] == STATUS_REPORT:
            return StatusReport(STATUS_REPORT, data, STATUSES[data[1]])

        if data[0] == WEIGHT_LIMIT_REPORT:
            return WeightLimitReport(
                WEIGHT_LIMIT_REPORT, data, WEIGHT_UNITS[data[1]],
                cls.calc_weight(data[2], data[3], data[4])
            )

        if data[0] == STATISTICS_REPORT:
            return StatisticsReport(STATISTICS_REPORT, data,
                (data[1] + data[2] * 256),  (data[3] + data[4] * 256)
            )

    @staticmethod
    def twos_comp(value):
        """Compute the 2's compliment of int value val"""
        num_bits = len(bin(value)) - 2 # Subtract 2 to remove leading '0b'
        if((value & (1 << (num_bits - 1))) != 0):
            value = value - (1 << num_bits)
        return value

    @classmethod
    def calc_weight(cls, scale, lsb, msb):
        """Converts the USB HID's weight data to a float"""
        return float(Decimal(str(10 ** cls.twos_comp(scale))) \
                * Decimal(str(lsb + (256 * msb))))
