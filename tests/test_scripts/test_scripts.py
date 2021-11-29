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

import filecmp
import pathlib
import shutil
import unittest

from datetime import datetime
from tempfile import TemporaryDirectory

import click.testing
import dulwich.repo

from scripts.scripts import cli


class TestScripts(unittest.TestCase):
    def test_update_copyright_headers(self):
        """Tests that update-copyright-headers updates copyright headers as
        expected"""

        with TemporaryDirectory() as tempdir:
            # create Git repository in temporary directory and commit test files
            repo = dulwich.repo.Repo.init(tempdir)

            for element in sorted((pathlib.Path(__file__).parent / "dependencies").iterdir()):
                if element.name.endswith(".py"):
                    shutil.copy(element, tempdir)

                    repo.stage(element.name)
                elif element.name.endswith(".py_expected"):
                    with open(element) as input_file, open(pathlib.Path(tempdir) / element.name, "w") as output_file:
                        for line in input_file:
                            output_file.write(line.replace("{current_year}", str(datetime.today().year)))

            repo.do_commit(b"")

            # run "update-copyright-headers" command
            runner = click.testing.CliRunner()
            runner.invoke(
                cli,
                [
                    "update-copyright-headers",
                    tempdir,
                ],
            )

            # compare contents of modified files with contents of expected files
            for element in sorted((pathlib.Path(__file__).parent / "dependencies").iterdir()):
                if element.name.endswith(".py"):
                    file_1 = pathlib.Path(tempdir) / (element.name + "_expected")
                    file_2 = pathlib.Path(tempdir) / element.name

                    self.assertTrue(filecmp.cmp(file_1, file_2, shallow=False), f"{file_1} and {file_2} are not equal")


if __name__ == "__main__":
    unittest.main()
