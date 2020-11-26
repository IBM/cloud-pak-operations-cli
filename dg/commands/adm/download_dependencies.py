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

import click

import dg.utils.download.ibm_cloud
import dg.utils.download.openshift
import dg.utils.download.terraform


@click.command()
def download_dependencies():
    """Download dependencies"""

    dg.utils.download.ibm_cloud.download_ibm_cloud_cli()
    dg.utils.download.ibm_cloud.download_ibm_cloud_terraform_provider()
    dg.utils.download.openshift.download_openshift_container_platform_cli()
    dg.utils.download.terraform.download_terraform_cli()
