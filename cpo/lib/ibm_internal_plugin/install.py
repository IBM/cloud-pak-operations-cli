#  Copyright 2022 IBM Corporation
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

import cpo.utils.process


def install(distribution_package_name: str, artifactory_username: str, artifactory_password: str):
    """Installs the distribution package with the given name"""

    cpo.utils.process.execute_command(
        "pip3",  # type: ignore
        [
            "install",
            distribution_package_name,
            "--index-url",
            (
                f"https://{artifactory_username}:{artifactory_password}@"
                "na.artifactory.swg-devops.com/artifactory/api/pypi/idaa-data-gate-cli-pypi-local/simple"
            ),
            "--user",
        ],
    )
