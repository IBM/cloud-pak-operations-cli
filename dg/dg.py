#  Copyright 2020 IBM Corporation
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

import sys

import click
import pkg_resources

import dg.commands
import dg.utils.debugger
import dg.utils.logging

from dg.lib.click.lazy_loading_multi_command import (
    create_click_multi_command_class,
)

click_logging_handler = dg.utils.logging.init_root_logger()

if dg.utils.debugger.is_debugpy_running() and (len(sys.argv) == 2):
    if sys.argv[1] == "":
        # filter empty argument added by Visual Studio Code when launching a
        # debug configuration including a promptString input for which an empty
        # string is provided
        sys.argv = [sys.argv[0]]
    else:
        # split single argument into multiple arguments
        # (see https://github.com/microsoft/vscode/issues/83678)
        sys.argv = [sys.argv[0]] + sys.argv[1].split()


@click.group(cls=create_click_multi_command_class(dg.commands))
@click.version_option(
    message="Db2 Data Gate CLI %(version)s", version=pkg_resources.require("data-gate-cli")[0].version
)
def cli():
    # main Click command
    pass


if __name__ == "__main__":
    cli()
