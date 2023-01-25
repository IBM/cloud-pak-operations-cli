#  Copyright 2021, 2023 IBM Corporation
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

import json
import os
import pathlib
import sys
import urllib.parse

from dataclasses import dataclass
from importlib.metadata import Distribution, EntryPoint, distributions
from types import ModuleType
from typing import Any, Optional, TypedDict

from jsonschema import validate

from cpo.utils.file import get_relative_path


class DirInfoJSONDocumentDirInfo(TypedDict):
    editable: bool


class DirInfoJSONDocument(TypedDict):
    dir_info: DirInfoJSONDocumentDirInfo
    subdirectory: str
    url: str


@dataclass
class DistributionData:
    editable: bool
    path: os.PathLike


class DistributionEntryPointLoader:
    """Determines the corresponding distribution package for a loaded entry
    point if possible

    Notes
    -----
    Starting from Python 3.10, EntryPoint instances have an instance
    variable named "dist" referencing the corresponding distribution package
    if applicable. Therefore, when switching to Python 3.10 or higher, this
    class should be removed.

    https://bugs.python.org/issue42382
    """

    def __init__(self, entry_point: EntryPoint):
        loaded_entry_point = entry_point.load()

        # https://packaging.python.org/en/latest/specifications/direct-url/
        self._direct_url_json_schema = {
            "$defs": {
                "archive_info": {
                    "additionalProperties": False,
                    "properties": {
                        "archive_info": {
                            "properties": {
                                "hash": {
                                    "type": "boolean",
                                }
                            },
                            "type": "object",
                        },
                        "subdirectory": {
                            "type": "string",
                        },
                        "url": {
                            "type": "string",
                        },
                    },
                    "required": [
                        "archive_info",
                        "url",
                    ],
                },
                "dir_info": {
                    "additionalProperties": False,
                    "properties": {
                        "dir_info": {
                            "properties": {
                                "editable": {
                                    "type": "boolean",
                                }
                            },
                            "type": "object",
                        },
                        "subdirectory": {
                            "type": "string",
                        },
                        "url": {
                            "type": "string",
                        },
                    },
                    "required": [
                        "dir_info",
                        "url",
                    ],
                },
                "vcs_info": {
                    "additionalProperties": False,
                    "properties": {
                        "subdirectory": {
                            "type": "string",
                        },
                        "url": {
                            "type": "string",
                        },
                        "vcs_info": {
                            "properties": {
                                "commit_id": {
                                    "type": "string",
                                },
                                "requested_revision": {
                                    "type": "string",
                                },
                                "vcs": {
                                    "type": "string",
                                },
                            },
                            "required": ["commit_id", "vcs"],
                            "type": "object",
                        },
                    },
                    "required": [
                        "url",
                        "vcs_info",
                    ],
                },
            },
            "oneOf": [
                {"$ref": "#/$defs/archive_info"},
                {"$ref": "#/$defs/dir_info"},
                {"$ref": "#/$defs/vcs_info"},
            ],
        }

        self._distribution: Optional[Distribution] = self._get_distribution_from_loaded_entry_point(loaded_entry_point)
        self._loaded_entry_point = loaded_entry_point

    @property
    def distribution(self) -> Optional[Distribution]:
        return self._distribution

    @property
    def loaded_entry_point(self) -> Any:
        return self._loaded_entry_point

    def _get_direct_url_origin_file_contents(self, distribution: Distribution) -> Any:
        """Returns the contents of the direct_url.json file of the given
        distribution or None if the file does not exist

        Parameters
        ----------
        distribution
            distribution to be searched

        Returns
        -------
        Any
            contents of the direct_url.json file of the given distribution or None
            if the file does not exist
        """

        result: Any = None

        assert distribution.files is not None

        for package_path in distribution.files:
            if package_path.name == "direct_url.json":
                file_contents = distribution.read_text(package_path.name)

                if file_contents is None:
                    break

                result = json.loads(file_contents)

                validate(result, self._direct_url_json_schema)

        return result

    def _get_distribution_data(self, distribution: Distribution) -> DistributionData:
        """Returns installation information about the given distribution

        Parameters
        ----------
        distribution
            distribution to be analyzed

        Returns
        -------
        DistributionData
            installation information about the given distribution
        """

        direct_url_origin_file_contents = self._get_direct_url_origin_file_contents(distribution)
        result: Optional[DistributionData] = None

        if self._is_editable_install(direct_url_origin_file_contents):
            result = DistributionData(
                editable=True, path=self._get_path_for_file_uri(direct_url_origin_file_contents["url"])
            )
        else:
            result = DistributionData(editable=False, path=distribution.locate_file(""))

        return result

    def _get_distribution_from_loaded_entry_point(self, loaded_entry_point: Any) -> Optional[Distribution]:
        """Determines the corresponding distribution package for a loaded entry
        point if possible

        Parameters
        ----------
        loaded_entry_point
            loaded entry point

        Returns
        -------
        Optional[Distribution]
            corresponding distribution package for the given loaded entry point or
            None if it could not be determined
        """

        module_path = (
            loaded_entry_point.__file__
            if isinstance(loaded_entry_point, ModuleType)
            else sys.modules[loaded_entry_point.__module__].__file__
        )

        if module_path is None:
            return None

        result: Optional[Distribution] = None

        for distribution in distributions():
            if distribution.files is None:
                continue

            distribution_data = self._get_distribution_data(distribution)

            if distribution_data.editable:
                if get_relative_path(distribution_data.path, pathlib.Path(module_path)) is not None:
                    result = distribution

                    break
            else:
                relative_path = get_relative_path(distribution_data.path, pathlib.Path(module_path))

                if (relative_path is not None) and (relative_path in distribution.files):
                    result = distribution

                    break

        return result

    def _get_path_for_file_uri(self, file_uri: str) -> pathlib.PurePath:
        """Returns the path for the given file URI

        Parameters
        ----------
        file_uri
            file URI

        Returns
        -------
        pathlib.PurePath
            path for the given file URI
        """

        if not file_uri.startswith("file:"):
            raise ValueError(f"Invalid file URI: {file_uri}")

        parse_result = urllib.parse.urlparse(file_uri)
        file_path_str = urllib.parse.unquote(parse_result.path)
        path_class = pathlib.PurePath

        if isinstance(path_class(), pathlib.PureWindowsPath) and file_path_str.startswith("/"):
            result = path_class(file_path_str[1:])
        else:
            result = path_class(file_path_str)

        if not result.is_absolute():
            raise ValueError(f"Invalid file URI: {file_uri}")

        return result

    def _is_editable_install(self, direct_url_origin_file_contents: Any) -> bool:
        if (direct_url_origin_file_contents is not None) and ("dir_info" in direct_url_origin_file_contents):
            dir_info: DirInfoJSONDocument = direct_url_origin_file_contents
            editable = dir_info["dir_info"]["editable"] if "editable" in dir_info["dir_info"] else False
        else:
            editable = False

        return editable
