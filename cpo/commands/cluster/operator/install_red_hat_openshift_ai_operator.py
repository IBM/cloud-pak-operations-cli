#  Copyright 2024, 2025 IBM Corporation
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
@click.option("--project", default="redhat-ods-operator", help="OpenShift project", show_default=True)
@click.option("--channel", default="stable-2.19", help="Red Hat OpenShift AI update channel", show_default=True)
@click.pass_context
def install_red_hat_openshift_ai_operator(
    ctx: click.Context,
    server: Optional[str],
    username: Optional[str],
    password: Optional[str],
    token: Optional[str],
    insecure_skip_tls_verify: Optional[bool],
    use_cluster: Optional[str],
    project: str,
    channel: str,
):
    """Install the Red Hat OpenShift AI Operator"""

    credentials = cpo.lib.click.utils.get_cluster_credentials(ctx, locals().copy())

    OpenShiftPlaybookRunner(
        "install_red_hat_openshift_ai_playbook.yaml",
        credentials,
        variables={
            "channel": channel,
            "project": project,
        },
    ).run_playbook()
