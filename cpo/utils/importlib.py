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

import importlib.metadata
import pathlib

from typing import Optional

from cpo.utils.path import is_relative_to


def get_distribution_package_name() -> str:
    """Returns the distribution package name corresponding to this module

    Returns
    -------
    str
        distribution package name corresponding to this module
    """

    distribution_package_name: Optional[str] = None

    for distribution in importlib.metadata.distributions():
        if is_relative_to(pathlib.Path(__file__), distribution.locate_file("")):
            distribution_package_name = distribution.metadata["name"]

            break

    if distribution_package_name is None:
        raise Exception("Distribution package name could not be identified")

    return distribution_package_name
