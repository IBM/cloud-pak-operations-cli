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

from typing import Optional

import click

import cpo.config.cluster_credentials_manager
import cpo.lib.click.utils
import cpo.utils.network

from cpo.lib.ansible.playbook_runners.create_ibm_internal_icsp_for_cpd_runner import CreateIBMInternalICSPForCPDRunner
from cpo.lib.openshift.utils.click import openshift_server_options
from cpo.utils.logging import loglevel_command


@loglevel_command(
    context_settings=cpo.lib.click.utils.create_default_map_from_dict(
        cpo.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
@openshift_server_options
@click.pass_context
def create_ibm_internal_cpd_icsp(
    ctx: click.Context,
    server: Optional[str],
    username: Optional[str],
    password: Optional[str],
    token: Optional[str],
    insecure_skip_tls_verify: Optional[bool],
):
    """Create IBM-internal image content source policy for IBM Cloud Pak for Data"""

    credentials = cpo.lib.click.utils.get_cluster_credentials(ctx, locals().copy())

    CreateIBMInternalICSPForCPDRunner(credentials).run_playbook()
