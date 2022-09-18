import unittest

from pylibcklb.calculation.common import get_size


class Test(unittest.TestCase):

    def test_get_size_byte_1(self):
        assert get_size(512) == "512.00B"

    def test_get_size_kilobyte_1(self):
        assert get_size(1024) == "1.00KB"

    def test_get_size_kilobyte_2(self):
        assert get_size(1100) == "1.07KB"

    def test_get_size_megabyte_1(self):
        assert get_size(1048576) == "1.00MB"

    def test_get_size_megabyte_2(self):
        assert get_size(1253656) == "1.20MB"

    def test_get_size_gigabyte_1(self):
        assert get_size(1073741824) == "1.00GB"

    def test_get_size_gigabyte_2(self):
        assert get_size(1253656678) == "1.17GB"

    def test_get_size_gigabyte_3(self):
        assert get_size(107974182456) == "100.56GB"

    def test_get_size_terabyte_1(self):
        assert get_size(1099511627776) == "1.00TB"

    def test_get_size_terabyte_2(self):
        assert get_size(1999599627776) == "1.82TB"

    def test_get_size_number_to_big(self):
        assert get_size(1999599627776000) == None
