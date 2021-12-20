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

from typing import Dict, Type

import semver

import cpo.lib.cloud_pak_for_data.cpd3_manager
import cpo.lib.cloud_pak_for_data.cpd_3_0_1.cpd_manager
import cpo.lib.cloud_pak_for_data.cpd_3_5_0.cpd_manager

from cpo.lib.cloud_pak_for_data.cpd3_manager import (
    AbstractCloudPakForDataManager,
)
from cpo.lib.error import DataGateCLIException


class CloudPakForDataManagerFactory:
    """Provides a static method to return a subclass of
    AbstractCloudPakForDataManager for a given IBM Cloud Pak for Data
    version"""

    @staticmethod
    def get_cloud_pak_for_data_manager(
        cloud_pak_for_data_version: semver.VersionInfo,
    ) -> Type[AbstractCloudPakForDataManager]:
        """Returns a subclass of AbstractCloudPakForDataManager for a given IBM
        Cloud Pak for Data version

        Parameters
        ----------
        cloud_pak_for_data_version
            IBM Cloud Pak for Data version for which a subclass of
            AbstractCloudPakForDataManager shall be returned

        Returns
        -------
        type[AbstractCloudPakForDataManager]
            subclass of AbstractCloudPakForDataManager
        """

        if cloud_pak_for_data_version not in CloudPakForDataManagerFactory._cloud_pak_for_data_managers:
            raise DataGateCLIException(f"Unknown Cloud Pak for Data version ({str(cloud_pak_for_data_version)})")

        return CloudPakForDataManagerFactory._cloud_pak_for_data_managers[cloud_pak_for_data_version]

    _cloud_pak_for_data_managers: Dict[semver.VersionInfo, Type[AbstractCloudPakForDataManager]] = {
        semver.VersionInfo.parse("3.0.1"): cpo.lib.cloud_pak_for_data.cpd_3_0_1.cpd_manager.CloudPakForDataManager,
        semver.VersionInfo.parse("3.5.0"): cpo.lib.cloud_pak_for_data.cpd_3_5_0.cpd_manager.CloudPakForDataManager,
    }
