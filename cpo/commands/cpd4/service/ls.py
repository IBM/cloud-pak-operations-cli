#  Copyright 2021 IBM Corporation
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


from typing import List

import click

from tabulate import tabulate

import cpo.config
import cpo.config.cluster_credentials_manager
import cpo.lib.click.utils
import cpo.lib.cluster
import cpo.utils.download

from cpo.lib.cloud_pak_for_data.cpd_4_0_0.cpd_service_manager import (
    CloudPakForDataServiceManager,
)
from cpo.utils.logging import loglevel_command


@loglevel_command(
    context_settings=cpo.lib.click.utils.create_default_map_from_dict(
        cpo.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
def ls():
    """List installable IBM Cloud Pak for Data services"""

    custom_resources = CloudPakForDataServiceManager().get_custom_resource_metadata_dict()
    cloud_pak_for_data_services_list: List[List[str]] = []

    for service_name, custom_resource_metadata in sorted(
        custom_resources.items(), key=lambda pair: pair[1].description
    ):
        cloud_pak_for_data_services_list.append([service_name, custom_resource_metadata.description])

    click.echo(tabulate(cloud_pak_for_data_services_list, ["Service name", "Description"]))
