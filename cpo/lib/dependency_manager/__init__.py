#  Copyright 2021, 2022 IBM Corporation
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

from cpo.lib.dependency_manager.dependency_manager import DependencyManager
from cpo.lib.dependency_manager.plugins.ibm_cloud_cli_plugin import IBMCloudCLIPlugIn
from cpo.lib.dependency_manager.plugins.ibm_cloud_pak_cli_plugin import IBMCloudPakCLIPlugIn
from cpo.lib.dependency_manager.plugins.openshift_cli_plugin import OpenShiftCLIPlugIn

dependency_manager = DependencyManager()
dependency_manager.register_plugin(IBMCloudCLIPlugIn)
dependency_manager.register_plugin(IBMCloudPakCLIPlugIn)
dependency_manager.register_plugin(OpenShiftCLIPlugIn)
