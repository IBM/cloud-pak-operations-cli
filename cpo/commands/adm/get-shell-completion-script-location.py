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

import click

from cpo import distribution_package_name
from cpo.utils.logging import loglevel_command


@loglevel_command()
@click.option("--shell", help="Shell name", required=True, type=click.Choice(["bash", "zsh"]))
def get_shell_completion_script_location(shell: str):
    """Get the location of the shell completion script"""

    click.echo(
        importlib.metadata.distribution(distribution_package_name).locate_file(
            f"cpo/deps/autocomplete/cpo-autocomplete-{shell}.sh"
        )
    )
