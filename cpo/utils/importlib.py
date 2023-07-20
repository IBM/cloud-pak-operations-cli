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

import collections
import importlib.metadata

import cpo

from cpo.utils.error import CloudPakOperationsCLIException


def get_distribution_package_name() -> str:
    """Returns the name of the distribution package providing the "cpo" top-level package

    Returns
    -------
    str
        name of the distribution package providing the "cpo" top-level package
    """

    packages_to_distribution_packages_dict: collections.defaultdict[str, list[str]] = collections.defaultdict(list)

    for distribution in importlib.metadata.distributions():
        file_contents = distribution.read_text("top_level.txt")

        if file_contents is None:
            continue

        for package in file_contents.split():
            distribution_package_name = distribution.metadata["Name"]

            # The second check is required as importlib.metadata.distributions()
            # returns the name of this distribution package twice for unknown
            # reasons when running unit tests.
            if (package not in packages_to_distribution_packages_dict) or (
                distribution_package_name not in packages_to_distribution_packages_dict[package]
            ):
                packages_to_distribution_packages_dict[package].append(distribution_package_name)

    package_name = cpo.__package__

    if package_name not in packages_to_distribution_packages_dict:
        raise CloudPakOperationsCLIException(
            f"Distribution package name could not be identified (no distribution package provides a top-level package "
            f"named '{package_name}')"
        )

    if len(packages_to_distribution_packages_dict[package_name]) != 1:
        raise CloudPakOperationsCLIException(
            f"Distribution package name could not be identified (more than one distribution package provides a "
            f"top-level package named '{package_name}')"
        )

    return packages_to_distribution_packages_dict[package_name][0]
