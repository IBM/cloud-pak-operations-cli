#  Copyright 2023 IBM Corporation
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


import pathlib
import shutil
import urllib.parse

import semver

from pypi_simple import PyPISimple

import cpo.utils.process

from cpo.utils.error import CloudPakOperationsCLIException


class IBMInternalPluginInstaller:
    def __init__(self, artifactory_username: str, artifactory_password: str, repository_url: str):
        self._artifactory_password = artifactory_password
        self._artifactory_username = artifactory_username

        if repository_url.startswith("http://"):
            self._repository_url = repository_url.removeprefix("http://")
            self._scheme = "http"
        elif repository_url.startswith("https://"):
            self._repository_url = repository_url.removeprefix("https://")
            self._scheme = "https"
        else:
            self._repository_url = repository_url
            self._scheme = "https"

    def get_packages(self) -> list[list[str]]:
        """Lists IBM-internal CLI plug-ins"""

        package_list: list[list[str]] = []

        with PyPISimple(
            auth=(self._artifactory_username, self._artifactory_password),
            endpoint=f"{self._scheme}://{self._repository_url}",
        ) as client:
            for project_name in client.get_index_page().projects:
                packages = client.get_project_page(project_name).packages
                sdists = list(filter(lambda package: package.package_type == "sdist", packages))
                sdists.sort(
                    key=lambda distribution_package: semver.Version.parse(distribution_package.version)
                    if distribution_package.version is not None
                    else semver.Version(0),
                    reverse=True,
                )

                wheels = list(filter(lambda package: package.package_type == "wheel", packages))
                wheels.sort(
                    key=lambda distribution_package: semver.Version.parse(distribution_package.version)
                    if distribution_package.version is not None
                    else semver.Version(0),
                    reverse=True,
                )

                if (len(wheels) != 0) and (wheels[0].version is not None):
                    package_list.append([project_name, wheels[0].version])
                elif (len(sdists) != 0) and (sdists[0].version is not None):
                    package_list.append([project_name, sdists[0].version])

        return package_list

    def install(self, distribution_package_name: str, **kwargs):
        """Install IBM-internal CLI plug-in"""

        args = [
            "install",
            "--extra-index-url",
            "https://pypi.org/simple",
            "--index-url",
            f"{self._scheme}://{urllib.parse.quote(self._artifactory_username)}:"
            f"{urllib.parse.quote(self._artifactory_password)}@{self._repository_url}",
        ]

        if ((upgrade := kwargs.get("upgrade")) is not None) and upgrade:
            args.append("--upgrade")

        if ((user := kwargs.get("user")) is not None) and user:
            args.append("--user")

        version = kwargs.get("version")

        args.append(distribution_package_name if version is None else f"{distribution_package_name}=={version}")

        program = shutil.which("pip")

        if program is None:
            program = shutil.which("pip3")

        if program is None:
            raise CloudPakOperationsCLIException("pip(3) executable not found")

        cpo.utils.process.execute_command(pathlib.Path(program), args)
