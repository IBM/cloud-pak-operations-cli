#  Copyright 2024 IBM Corporation
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

import click

import cpo.config

from cpo.utils.logging import loglevel_command


@loglevel_command()
@click.option("--key", help="Name of the key to be set", required=True)
@click.option("--value", help="Value of the key to be set", required=True, type=bool)
def set_bool(key: str, value: bool):
    """Set boolean configuration option"""

    cpo.config.configuration_manager.set_bool_config_value(key, value)
