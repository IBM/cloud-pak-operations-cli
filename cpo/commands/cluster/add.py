#  Copyright 2022 IBM Corporation
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
import cpo.lib.openshift.cluster

from cpo.utils.logging import loglevel_command


@loglevel_command()
@click.option("--server", help="OpenShift server URL", required=True)
@click.option("--alias", help="Alias used to reference a cluster instead of its server URL")
@click.option("--username", default="kubeadmin", help="OpenShift username", show_default=True)
@click.option("--password", help="OpenShift password", required=True)
def add(server: str, alias: Optional[str], username: str, password: str):
    """Register an existing Red Hat OpenShift cluster"""

    cpo.config.cluster_credentials_manager.cluster_credentials_manager.add_cluster(
        alias if (alias is not None) else "",
        server,
        cpo.lib.openshift.cluster.CLUSTER_TYPE_ID,
        {
            "insecure_skip_tls_verify": True,
            "password": password,
            "username": username,
        },
    )
