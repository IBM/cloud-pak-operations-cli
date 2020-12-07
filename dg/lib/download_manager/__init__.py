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

from dg.lib.download_manager.download_manager import DownloadManager
from dg.lib.download_manager.plugins.ibm_cloud_cli_plugin import (
    IBMCloudCLIPlugIn,
)
from dg.lib.download_manager.plugins.ibm_cloud_terraform_provider_plugin import (
    IBMCloudTerraformProviderPlugIn,
)
from dg.lib.download_manager.plugins.openshift_client_cli_plugin import (
    OpenShiftClientCLIPlugIn,
)
from dg.lib.download_manager.plugins.terraform_plugin import TerraformPlugin

download_manager = DownloadManager()
download_manager.register_plugin(IBMCloudCLIPlugIn)
download_manager.register_plugin(IBMCloudTerraformProviderPlugIn)
download_manager.register_plugin(OpenShiftClientCLIPlugIn)
download_manager.register_plugin(TerraformPlugin)
