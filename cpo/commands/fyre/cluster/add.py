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

from cpo.lib.fyre.ocp_plus_api_manager import OCPPlusAPIManager
from cpo.utils.logging import loglevel_command


@loglevel_command()
@click.option("--alias", help="Alias used to reference a cluster instead of its server URL")
@click.option("--cluster-name", help="Name of the OCP+ cluster to be registered", required=True)
@click.option("--password", help="kubeadmin password", required=True)
@click.option("--site", help="OCP+ site", type=click.Choice(["rtp", "svl"]))
def add(alias: Optional[str], cluster_name: str, password: str, site: Optional[str]):
    """Register an existing OCP+ cluster"""

    OCPPlusAPIManager.add_cluster(alias, cluster_name, password, site)
