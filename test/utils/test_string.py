import unittest

from dg.utils.string import removeprefix, removesuffix


class TestStringUtilities(unittest.TestCase):
    def test_removeprefix(self):
        """Tests dg.utils.string.removeprefix()"""

        self.assertEqual(removeprefix("XYZ", "X"), "YZ")
        self.assertEqual(removeprefix("XYZ", "Z"), "XYZ")
        self.assertEqual(removeprefix("", "X"), "")
        self.assertEqual(removeprefix("", ""), "")

    def test_removesuffix(self):
        """Tests dg.utils.string.test_removesuffix()"""

        self.assertEqual(removesuffix("XYZ", "Z"), "XY")
        self.assertEqual(removesuffix("XYZ", "X"), "XYZ")
        self.assertEqual(removesuffix("", "Z"), "")
        self.assertEqual(removesuffix("", ""), "")


if __name__ == "__main__":
    unittest.main()
