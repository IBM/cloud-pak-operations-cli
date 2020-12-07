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
