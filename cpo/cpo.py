#  Copyright 2020, 2021 IBM Corporation
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
import sys

import click

import cpo.commands
import cpo.utils.debugger
import cpo.utils.logging

from cpo import distribution_package_name
from cpo.lib.click.lazy_loading_multi_command import LazyLoadingMultiCommand

click_logging_handler = cpo.utils.logging.init_root_logger()

if cpo.utils.debugger.is_debugpy_running() and (len(sys.argv) == 2):
    if sys.argv[1] == "":
        # filter empty argument added by Visual Studio Code when launching a
        # debug configuration including a promptString input for which an empty
        # string is provided
        sys.argv = [sys.argv[0]]
    else:
        # split single argument into multiple arguments
        # (see https://github.com/microsoft/vscode/issues/83678)
        sys.argv = [sys.argv[0]] + sys.argv[1].split()


@click.group(cls=LazyLoadingMultiCommand, distribution_package_name=distribution_package_name, package=cpo.commands)
@click.version_option(
    message="%(prog)s %(version)s",
    prog_name=importlib.metadata.metadata(distribution_package_name)["Summary"],
    version=importlib.metadata.version(distribution_package_name),
)
def cli():  # NOSONAR
    pass


if __name__ == "__main__":
    cli()
