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

from typing import Optional

import click

import cpo.config.cluster_credentials_manager

from cpo.utils.logging import loglevel_command


@loglevel_command()
@click.argument("alias_or_server")
@click.option("--alias", help="Alias")
@click.option(
    "--insecure-skip-tls-verify/--no-insecure-skip-tls-verify",
    default=None,
    help="Disables or enables checking the server's certificate for validity",
    is_flag=True,
)
@click.option("--password", help="kubeadmin password")
def edit(alias_or_server: str, alias: Optional[str], insecure_skip_tls_verify: Optional[bool], password: Optional[str]):
    """Edit metadata of a registered OpenShift cluster"""

    metadata_to_be_edited = locals().copy()
    metadata_to_be_edited.pop("alias_or_server")

    if all(value is None for value in metadata_to_be_edited.values()):
        return

    metadata_to_be_edited = dict(filter(lambda pair: pair[1] is not None, metadata_to_be_edited.items()))

    cpo.config.cluster_credentials_manager.cluster_credentials_manager.edit_cluster(
        alias_or_server, metadata_to_be_edited
    )
