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
import re as regex
import subprocess

from importlib import metadata

from cpo import distribution_package_name
from cpo.lib.error import DataGateCLIException
from cpo.utils.logging import loglevel_command


@loglevel_command()
def update_dev():
    """Update the CLI to the latest development version"""

    if importlib.metadata.version(distribution_package_name) != "0.0.1":
        raise DataGateCLIException(
            f"Current version is not a development version (use 'pip3 install --upgrade {distribution_package_name}' "
            f"to upgrade a release version)"
        )

    search_result = regex.search("https://(.*)", metadata.metadata(distribution_package_name)["Download-URL"])

    if search_result is not None:
        git_hub_url_without_scheme = search_result.group(1)
        git_hub_url = "git+https://git@" + git_hub_url_without_scheme + ".git"
        args = ["pip3", "install", "--upgrade", git_hub_url]

        subprocess.check_call(args)
