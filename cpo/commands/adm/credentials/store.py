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
@click.option("--credentials-key", help="Credentials key", required=True)
@click.option("--credentials-value", help="Credentials value", required=True)
def store(credentials_key: str, credentials_value: str):
    """Store credentials

    Credentials are stored in ~/.cpo/credentials.json.
    """

    cpo.config.configuration_manager.store_credentials(
        {
            credentials_key: credentials_value,
        }
    )
