#  Copyright 2021 IBM Corporation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
