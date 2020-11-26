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

import pathlib

import click

import dg.utils.click as dgclick


def get_click_multi_command_class() -> type[click.Command]:
    return dgclick.create_click_multi_command_class(
        dgclick.import_packages_and_modules(__name__, pathlib.Path(__file__).parent)
    )


@click.command(cls=get_click_multi_command_class())
def cluster():
    """Manage a FYRE OpenShift cluster"""

    pass
