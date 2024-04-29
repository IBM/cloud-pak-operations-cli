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

import cpo.config.cluster_credentials_manager
import cpo.lib.click.utils
import cpo.utils.network

from cpo.lib.ansible.openshift_playbook_runner import OpenShiftPlaybookRunner
from cpo.lib.openshift.utils.click import openshift_server_options
from cpo.utils.logging import loglevel_command


@loglevel_command(
    context_settings=cpo.lib.click.utils.create_default_map_from_dict(
        cpo.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
@openshift_server_options
@click.pass_context
def delete_terminated_pods(
    ctx: click.Context,
    server: str | None,
    username: str | None,
    password: str | None,
    token: str | None,
    insecure_skip_tls_verify: bool | None,
    use_cluster: str | None,
):
    """Delete terminated pods"""

    credentials = cpo.lib.click.utils.get_cluster_credentials(ctx, locals().copy())

    OpenShiftPlaybookRunner("delete_terminated_pods_playbook.yaml", credentials).run_playbook()
