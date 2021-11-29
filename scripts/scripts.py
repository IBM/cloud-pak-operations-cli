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

import os
import pathlib
import re as regex
import shutil
import tempfile

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from io import TextIOWrapper
from typing import Final, List, Optional

import click

from dulwich import porcelain
from dulwich.objects import Commit
from dulwich.repo import Repo


@dataclass
class CommitYearRange:
    """Stores the years of the first and the last commit of a file"""

    year_of_first_commit: int
    year_of_last_commit: int


@dataclass
class CopyrightYearRange:
    """Stores the years of creation and last modification contained in a
    copyright header"""

    year_of_creation: int
    year_of_last_modification: Optional[int]

    def requires_modification(self, commit_year_range: CommitYearRange) -> bool:
        """Returns whether the stored years of creation and last modification
        contained in a copyright header are different from the given years of
        the first and last commit, respectively

        Parameters
        ----------
        year_of_first_commit
            year of the first commit
        last_year_of_commit
            year of the last commit

        Returns
        -------
        bool
            True, if the stored and given years are different
        """

        return (
            (self.year_of_creation != commit_year_range.year_of_first_commit)
            or (
                (self.year_of_last_modification is None)
                and (commit_year_range.year_of_first_commit != commit_year_range.year_of_last_commit)
            )
            or (
                (self.year_of_last_modification is not None)
                and (self.year_of_last_modification != commit_year_range.year_of_last_commit)
            )
        )


@dataclass
class CopyrightYearExtractionResult:
    copyright_year_range: Optional[CopyrightYearRange]
    input_file_lines: List[str]


class CopyrightHeaderManager:
    """Checks and corrects copyright headers of Python files"""

    def __init__(self, repo_path: pathlib.Path):
        self._repo = Repo(repo_path)

    def process(self):
        """Iterates over all files of the Git repository given in the
        constructor and corrects copyright headers of non-empty Python files if
        required"""

        for binary_file_name in porcelain.ls_files(self._repo):
            input_file_path = self._repo.path / binary_file_name.decode("utf-8")

            if (input_file_path.name.endswith(".py") and os.stat(input_file_path).st_size > 0) and (
                (commit_year_range := self._get_commit_year_range(binary_file_name)) is not None
            ):
                click.echo(f"Processing file : '{input_file_path}'")

                with open(input_file_path, encoding="utf-8") as input_file:
                    copyright_year_extraction_result = self._extract_copyright_year_range(input_file)

                    if (
                        (copyright_year_extraction_result.copyright_year_range is None)
                        or (
                            copyright_year_extraction_result.copyright_year_range.requires_modification(
                                commit_year_range
                            )
                        )
                        or not self._newline_after_copyright_header(copyright_year_extraction_result.input_file_lines)
                    ):
                        click.echo(f"Updating file   :'{input_file_path}'")

                        output_file_path = self._write_output_file(
                            input_file, copyright_year_extraction_result.input_file_lines, commit_year_range
                        )

                        # TODO replace "str(output_file_path)" with "output_file_path" when
                        # switching to Python 3.9 or higher
                        shutil.move(str(output_file_path), input_file_path)

    def _extract_copyright_year_range(self, input_file: TextIOWrapper) -> CopyrightYearExtractionResult:
        """Extracts the copyright year range from the copyright header of the
        given file if it exists

        Parameters
        ----------
        input_file
            file to be processed

        Returns
        -------
        CopyrightYearExtractionResult
            object containing the extracted copyright year range or read lines if
            the extraction was unsuccessful
        """

        input_file_line = input_file.readline()

        if input_file_line == "":
            return CopyrightYearExtractionResult(None, [])

        input_file_lines: List[str] = []
        input_file_lines.append(input_file_line)

        regex_result = regex.match(CopyrightHeaderManager._COPYRIGHT_REGEX, input_file_line)

        if regex_result is None:
            return CopyrightYearExtractionResult(None, input_file_lines)

        result: Optional[CopyrightYearExtractionResult] = None

        for copyright_header_line in CopyrightHeaderManager._COPYRIGHT_HEADER_REMAINING_LINES:
            input_file_line = input_file.readline()

            if input_file_line == "":
                break

            input_file_lines.append(input_file_line)

            if input_file_line != copyright_header_line:
                result = CopyrightYearExtractionResult(None, input_file_lines)

                break

        if result is None:
            input_file_lines.clear()

            if (input_file_line := input_file.readline()) != "":
                input_file_lines.append(input_file_line)

            result = CopyrightYearExtractionResult(
                CopyrightYearRange(
                    int(regex_result.group(1)),
                    int(regex_result.group(3)) if regex_result.group(3) is not None else None,
                ),
                input_file_lines,
            )

        return result

    def _get_commit_date(self, commit: Commit) -> datetime:
        return datetime.fromtimestamp(commit.commit_time, tz=timezone(timedelta(seconds=commit.commit_timezone)))

    def _get_commit_year_range(self, binary_file_name: bytes) -> Optional[CommitYearRange]:
        """Returns the years of the first and last commit

        Parameters
        ----------
        binary_file_name
            name of the file to be processed

        Returns
        -------
        Optional[CommitYearRange]
            years of the first and last commit or None if the file has no commits
        """

        iterable = self._repo.get_walker(paths=[binary_file_name]).__iter__()
        first_walk_entry = last_walk_entry = next(iterable, None)
        result: Optional[CommitYearRange] = None

        if first_walk_entry is not None and last_walk_entry is not None:
            for last_walk_entry in iterable:
                pass  # NOSONAR

            result = CommitYearRange(
                self._get_commit_date(last_walk_entry.commit).year, self._get_commit_date(first_walk_entry.commit).year
            )

        return result

    def _newline_after_copyright_header(self, input_file_lines: List[str]) -> bool:
        return (len(input_file_lines) != 0) and (input_file_lines[0] == "\n")

    def _remove_leading_empty_lines(self, input_file_lines: List[str]):
        while len(input_file_lines) != 0 and (input_file_lines[0].strip() + "\n") == "\n":
            input_file_lines.pop(0)

    def _write_output_file(
        self, input_file: TextIOWrapper, input_file_lines: List[str], commit_year_range: CommitYearRange
    ) -> pathlib.Path:
        """Writes the given input file with the corrected copyright header to a
        temporary file

        Parameters
        ----------
        input_file
            file to be processed
        input_file_lines
            lines of the input file that were already read
        commit_year_range
            years of the first and last commit

        Returns
        -------
        pathlib.Path
            path to the temporary file
        """

        self._remove_leading_empty_lines(input_file_lines)

        output_file_name = pathlib.Path(tempfile.gettempdir()) / pathlib.Path(input_file.name).name

        with open(output_file_name, "w") as output_file:
            if commit_year_range.year_of_first_commit == commit_year_range.year_of_last_commit:
                output_file.write(
                    CopyrightHeaderManager._COPYRIGHT_HEADER_FIRST_LINE.format(
                        first_year=commit_year_range.year_of_first_commit, last_year="", separator=""
                    )
                )
            else:
                output_file.write(
                    CopyrightHeaderManager._COPYRIGHT_HEADER_FIRST_LINE.format(
                        first_year=commit_year_range.year_of_first_commit,
                        last_year=commit_year_range.year_of_last_commit,
                        separator=", ",
                    )
                )

            for copyright_header_line in CopyrightHeaderManager._COPYRIGHT_HEADER_REMAINING_LINES:
                output_file.write(copyright_header_line)

            output_file.write("\n")

            if len(input_file_lines) != 0:
                for input_file_line in input_file_lines:
                    output_file.write(input_file_line)
            else:
                while (current_line := input_file.readline()) != "":
                    if current_line != "\n":
                        output_file.write(current_line)

                        break

            while (current_line := input_file.readline()) != "":
                output_file.write(current_line)

        return pathlib.Path(output_file_name)

    _COPYRIGHT_HEADER_FIRST_LINE: Final[str] = "#  Copyright {first_year}{separator}{last_year} IBM Corporation\n"
    _COPYRIGHT_HEADER_REMAINING_LINES: Final[List[str]] = [
        "#\n",
        '#  Licensed under the Apache License, Version 2.0 (the "License");\n',
        "#  you may not use this file except in compliance with the License.\n",
        "#  You may obtain a copy of the License at\n",
        "#\n",
        "#  http://www.apache.org/licenses/LICENSE-2.0\n",
        "#\n",
        "#  Unless required by applicable law or agreed to in writing, software\n",
        '#  distributed under the License is distributed on an "AS IS" BASIS,\n',
        "#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n",
        "#  See the License for the specific language governing permissions and\n",
        "#  limitations under the License.\n",
    ]

    _COPYRIGHT_REGEX: Final[str] = "#  Copyright (\\d\\d\\d\\d)(, (\\d\\d\\d\\d))* IBM Corporation\n"


@click.group()
def cli():  # NOSONAR
    pass


@cli.command()
@click.argument("repo_path", type=click.Path(exists=True))
def update_copyright_headers(repo_path: str):
    CopyrightHeaderManager(pathlib.Path(repo_path)).process()


if __name__ == "__main__":
    cli()
