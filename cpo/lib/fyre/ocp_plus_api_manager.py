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

import logging

from typing import List, Optional, Tuple, Union

import cpo.config.cluster_credentials_manager
import cpo.lib.fyre.cluster
import cpo.lib.fyre.utils.request_status_progress_bar

from cpo.lib.fyre.data.check_hostname_data import CheckHostNameData
from cpo.lib.fyre.data.ocp_available_data import OCPAvailableData
from cpo.lib.fyre.data.ocpplus_cluster import OCPPlusCluster
from cpo.lib.fyre.data.ocpplus_cluster_data import OCPPlusClusterData
from cpo.lib.fyre.data.ocpplus_cluster_specification import (
    OCPPlusClusterSpecification,
)
from cpo.lib.fyre.data.openshift_version_data import OpenShiftVersionData
from cpo.lib.fyre.data.product_group_quota_data import ProductGroupQuotaData
from cpo.lib.fyre.data.quick_burn_max_hours_data import QuickBurnMaxHoursData
from cpo.lib.fyre.data.quick_burn_size_data import QuickBurnSizeData
from cpo.lib.fyre.data.request_status_data import RequestStatusData
from cpo.lib.fyre.data.status_data import OCPPlusClusterStatus
from cpo.lib.fyre.request_managers.check_hostname_manager import (
    CheckHostnameManager,
)
from cpo.lib.fyre.request_managers.json_request_manager import OCPRequestManager
from cpo.lib.fyre.request_managers.ocp_accept_transfer_put_manager import (
    OCPAcceptTransferPutManager,
)
from cpo.lib.fyre.request_managers.ocp_add_additional_nodes_put_manager import (
    OCPAddAdditionalNodesPutManager,
)
from cpo.lib.fyre.request_managers.ocp_available_manager import (
    OCPAvailableManager,
)
from cpo.lib.fyre.request_managers.ocp_cluster_action_manager import (
    OCPClusterActionManager,
)
from cpo.lib.fyre.request_managers.ocp_default_post_manager import (
    OCPDefaultPostManager,
)
from cpo.lib.fyre.request_managers.ocp_delete_manager import OCPDeleteManager
from cpo.lib.fyre.request_managers.ocp_disable_delete_manager import (
    OCPDisableDeleteManager,
)
from cpo.lib.fyre.request_managers.ocp_disk_put_manager import OCPDiskPutManager
from cpo.lib.fyre.request_managers.ocp_enable_delete_manager import (
    OCPEnableDeleteManager,
)
from cpo.lib.fyre.request_managers.ocp_get_manager import OCPGetManager
from cpo.lib.fyre.request_managers.ocp_get_manager_for_single_cluster import (
    OCPGetManagerForSingleCluster,
)
from cpo.lib.fyre.request_managers.ocp_node_action_manager import (
    OCPNodeActionManager,
)
from cpo.lib.fyre.request_managers.ocp_post_manager import OCPPostManager
from cpo.lib.fyre.request_managers.ocp_quick_burn_max_hours_manager import (
    OCPQuickBurnMaxHoursManager,
)
from cpo.lib.fyre.request_managers.ocp_quick_burn_sizes_manager import (
    OCPQuickBurnSizesManager,
)
from cpo.lib.fyre.request_managers.ocp_resource_put_manager import (
    OCPResourcePutManager,
)
from cpo.lib.fyre.request_managers.ocp_status_manager import OCPStatusManager
from cpo.lib.fyre.request_managers.ocp_transfer_put_manager import (
    OCPTransferPutManager,
)
from cpo.lib.fyre.request_managers.quota_request_manager import (
    QuotaRequestManager,
)
from cpo.lib.fyre.types.ocp_add_additional_nodes_put_request import (
    OCPAddAdditionalNodesPutRequest,
)
from cpo.lib.fyre.types.ocp_disk_put_request import OCPDiskPutRequest
from cpo.lib.fyre.types.ocp_post_request import OCPPostRequest, WorkerData
from cpo.lib.fyre.types.ocp_post_response import OCPPostResponse
from cpo.lib.fyre.types.ocp_resource_put_request import OCPResourcePutRequest
from cpo.lib.fyre.types.ocp_transfer_put_request import OCPTransferPutRequest

logger = logging.getLogger(__name__)


class OCPPlusAPIManager:
    """Manages REST communication with the FYRE/OCP+ API"""

    @staticmethod
    def add_cluster(
        alias: Optional[str],
        cluster_name: str,
        password: str,
        site: Optional[str],
    ):
        """Registers an existing OCP+ cluster

        Parameters
        ----------
        alias
            Alias used to reference a cluster instead of its server URL
        cluster_name
            Name of the OCP+ cluster to be registered
        password
            kubeadmin password
        site
            OCP+ site
        """

        cluster_data = {
            "cluster_name": cluster_name,
            "infrastructure_node_hostname": f"api.{cluster_name}.cp.fyre.ibm.com",
            "insecure_skip_tls_verify": True,
            "password": password,
            "username": "kubeadmin",
        }

        if site is not None:
            cluster_data["site"] = site

        cpo.config.cluster_credentials_manager.cluster_credentials_manager.add_cluster(
            alias if (alias is not None) else "",
            f"https://api.{cluster_name}.cp.fyre.ibm.com:6443",
            cpo.lib.fyre.cluster.CLUSTER_TYPE_ID,
            cluster_data,
        )

    def __init__(self, fyre_api_user_name: str, fyre_api_key: str):
        self._fyre_api_key = fyre_api_key
        self._fyre_api_user_name = fyre_api_user_name

    def accept_transfer(self, cluster_name: str, site: Optional[str]):
        """Accepts an incoming OCP+ cluster transfer

        Parameters
        ----------
        cluster_name
            Name of the OCP+ cluster whose incoming transfer shall be accepted
        site
            OCP+ site
        """

        OCPAcceptTransferPutManager(
            self._fyre_api_user_name, self._fyre_api_key, site, cluster_name
        ).execute_put_request()

    def add_node(
        self,
        cluster_name: str,
        disable_scheduling: bool,
        site: Optional[str],
        worker_node_additional_disk_sizes: List[int],
        worker_node_count: Optional[int],
        worker_node_num_cpus: Optional[int],
        worker_node_ram_size: Optional[int],
    ):
        """Adds an additional worker node to an OCP+ cluster

        Parameters
        ----------
        cluster_name
            Name of the OCP+ cluster to whom a worker node shall be added
        disable_scheduling
            ?
        site
            OCP+ site
        worker_node_additional_disk_sizes
            Sizes of additional worker node disks
        worker_node_count
            Number of worker nodes
        worker_node_num_cpus
            Number of CPUs per worker node
        worker_node_ram_size
            RAM size per worker node
        """

        ocp_add_additional_nodes_put_request: OCPAddAdditionalNodesPutRequest = {
            "additional_disk": list(
                map(lambda additional_disk_size: str(additional_disk_size), worker_node_additional_disk_sizes)
            )
            if len(worker_node_additional_disk_sizes) != 0
            else [],
        }

        if worker_node_num_cpus is not None:
            ocp_add_additional_nodes_put_request["cpu"] = str(worker_node_num_cpus)

        if disable_scheduling:
            ocp_add_additional_nodes_put_request["disable_scheduling"] = str(disable_scheduling)

        if worker_node_ram_size is not None:
            ocp_add_additional_nodes_put_request["memory"] = str(worker_node_ram_size)

        if worker_node_count is not None:
            ocp_add_additional_nodes_put_request["vm_count"] = str(worker_node_count)

        OCPAddAdditionalNodesPutManager(
            self._fyre_api_user_name, self._fyre_api_key, site, cluster_name
        ).execute_request_put_request(ocp_add_additional_nodes_put_request)

    def boot(self, cluster_name: str, site: Optional[str]):
        """Boots an OCP+ cluster

        Parameters
        ----------
        cluster_name
            Name of the OCP+ cluster to be booted
        site
            OCP+ site
        """

        OCPClusterActionManager(
            self._fyre_api_user_name, self._fyre_api_key, site, cluster_name, "boot"
        ).execute_request_put_request()

    def boot_node(self, cluster_name: str, node_name: str, site: Optional[str]):
        """Boots a node of an OCP+ cluster

        Parameters
        ----------
        cluster_name
            Name of the OCP+ cluster
        node_name
            Name of the node to be booted
        site
            OCP+ site
        """

        OCPNodeActionManager(
            self._fyre_api_user_name, self._fyre_api_key, site, cluster_name, node_name, "boot"
        ).execute_request_put_request()

    def check_cluster_name(self, cluster_name: str, site: Optional[str]) -> CheckHostNameData:
        """Checks if a cluster name is available

        Parameters
        ----------
        cluster_name
            Cluster name to be checked
        site
            OCP+ site
        """

        return CheckHostnameManager(
            self._fyre_api_user_name, self._fyre_api_key, site, cluster_name
        ).execute_get_request()

    def create_cluster(self, ocp_plus_cluster_settings: OCPPlusClusterSpecification, site: Optional[str]) -> str:
        """Creates a new OCP+ cluster

        Parameters
        ----------
        ocp_plus_cluster_settings
            OCP+ cluster settings
        site
            OCP+ site

        Returns
        -------
        str
            cluster name
        """

        if ocp_plus_cluster_settings.alias is not None:
            cpo.config.cluster_credentials_manager.cluster_credentials_manager.raise_if_alias_exists(
                ocp_plus_cluster_settings.alias
            )

        ocp_post_request: OCPPostRequest = {}

        self._add_keys(
            ocp_post_request,
            [
                ("description", ocp_plus_cluster_settings.description),
                ("expiration", ocp_plus_cluster_settings.expiration),
                ("fips", ocp_plus_cluster_settings.fips),
                ("name", ocp_plus_cluster_settings.name),
                ("ocp_version", ocp_plus_cluster_settings.ocp_version),
                ("platform", ocp_plus_cluster_settings.platform),
                ("product_group_id", ocp_plus_cluster_settings.product_group_id),
                ("pull_secret", ocp_plus_cluster_settings.pull_secret),
                ("ssh_key", ocp_plus_cluster_settings.ssh_key),
            ],
        )

        if ocp_plus_cluster_settings.haproxy_timeout_settings is not None:
            ocp_plus_cluster_settings.haproxy_timeout_settings.add_settings_to_dict(ocp_post_request)

        if ocp_plus_cluster_settings.quick_burn_settings is not None:
            self._add_keys(
                ocp_post_request,
                [
                    ("quota_type", "quick_burn"),  # default: product_group
                    ("size", ocp_plus_cluster_settings.quick_burn_settings.quick_burn_size),
                    ("time_to_live", ocp_plus_cluster_settings.quick_burn_settings.quick_burn_time_to_live),
                ],
            )

        if (
            worker_node_settings := ocp_plus_cluster_settings.worker_node_settings
        ) is not None and worker_node_settings.worker_settings_exist():
            worker: WorkerData = {}

            if worker_node_settings.worker_node_additional_disk_size is not None:
                worker["additional_disk"] = list(
                    map(
                        lambda additional_disk: str(additional_disk),
                        worker_node_settings.worker_node_additional_disk_size,
                    )
                )
            else:
                worker["additional_disk"] = []

            self._add_keys(
                worker,
                [
                    ("count", worker_node_settings.worker_node_count),
                    ("cpu", worker_node_settings.worker_node_num_cpus),
                    ("memory", worker_node_settings.worker_node_ram_size),
                ],
            )

            ocp_post_request["worker"] = [worker]

        ocp_post_response = OCPPostManager(self._fyre_api_user_name, self._fyre_api_key, site).execute_post_request(
            ocp_post_request
        )

        self._add_cluster(ocp_plus_cluster_settings.alias, site, ocp_post_response)

        return ocp_post_response["cluster_name"]

    def create_cluster_with_defaults(self, alias: Optional[str], platform: str, site: Optional[str]) -> str:
        """Creates a new OCP+ cluster with defaults

        Parameters
        ----------
        alias
            Alias used to reference a cluster instead of its server URL
        platform
            Platform
        site
            OCP+ site

        Returns
        -------
        str
            cluster name
        """

        if alias is not None:
            cpo.config.cluster_credentials_manager.cluster_credentials_manager.raise_if_alias_exists(alias)

        ocp_post_response = OCPDefaultPostManager(
            self._fyre_api_user_name, self._fyre_api_key, site, platform
        ).execute_post_request()

        self._add_cluster(alias, site, ocp_post_response)

        return ocp_post_response["cluster_name"]

    def disable_delete(self, cluster_name: str, site: Optional[str]):
        """Disables erasability of an OCP+ cluster

        Parameters
        ----------
        cluster_name
            Name of the OCP+ cluster whose erasability shall be disabled
        site
            OCP+ site
        """

        OCPDisableDeleteManager(self._fyre_api_user_name, self._fyre_api_key, site, cluster_name).execute_put_request()

    def edit_inf_node(self, cluster_name: str, additional_disk_sizes: List[int], site: Optional[str]):
        """Edits the infrastructure node of an OCP+ cluster

        Parameters
        ----------
        cluster_name
            Name of the OCP+ cluster to be edited
        additional_disk_sizes
            Sizes of additional disks
        """

        if len(additional_disk_sizes) != 0:
            self._add_additional_disks(cluster_name, "inf", additional_disk_sizes, site)

    def edit_master_node(
        self,
        cluster_name: str,
        node_name: str,
        node_num_cpus: Optional[int],
        node_ram_size: Optional[int],
        site: Optional[str],
    ):
        """Edits a master node of an OCP+ cluster

        Parameters
        ----------
        cluster_name
            Name of the OCP+ cluster to be edited
        node_name
            Node name
        node_num_cpus
            Number of CPUs per node
        node_ram_size
            RAM size per node
        """

        self._change_node_resources(cluster_name, node_name, node_num_cpus, node_ram_size, site)

    def edit_worker_node(
        self,
        cluster_name: str,
        node_name: str,
        additional_disk_sizes: Optional[List[int]],
        node_num_cpus: Optional[int],
        node_ram_size: Optional[int],
        site: Optional[str],
    ):
        """Edits a worker node of an OCP+ cluster

        Parameters
        ----------
        cluster_name
            Name of the OCP+ cluster to be edited
        node_name
            Node name
        additional_disk_sizes
            Sizes of additional disks
        node_num_cpus
            Number of CPUs per node
        node_ram_size
            RAM size per node
        """

        self._change_node_resources(cluster_name, node_name, node_num_cpus, node_ram_size, site)

        if additional_disk_sizes is not None and len(additional_disk_sizes) != 0:
            self._add_additional_disks(cluster_name, node_name, additional_disk_sizes, site)

    def enable_delete(self, cluster_name: str, site: Optional[str]):
        """Enables erasability of an OCP+ cluster

        Parameters
        ----------
        cluster_name
            Name of the OCP+ cluster whose erasability shall be enabled
        site
            OCP+ site
        """

        OCPEnableDeleteManager(self._fyre_api_user_name, self._fyre_api_key, site, cluster_name).execute_put_request()

    def get_cluster_details(self, cluster_name: str, site: Optional[str]) -> OCPPlusCluster:
        """Returns details of an OCP+ cluster

        Parameters
        ----------
        cluster_name
            Name of the OCP+ cluster whose details shall be returned
        site
            OCP+ site

        Returns
        -------
        OCPPlusCluster
            object containing details of an OCP+ cluster
        """

        return OCPGetManagerForSingleCluster(
            self._fyre_api_user_name, self._fyre_api_key, site, cluster_name
        ).execute_get_request()

    def get_cluster_status(self, cluster_name: str, site: Optional[str]) -> OCPPlusClusterStatus:
        """Returns the status of an OCP+ cluster

        Parameters
        ----------
        cluster_name
            Name of the OCP+ cluster whose status shall be returned
        site
            OCP+ site

        Returns
        -------
        OCPPlusClusterStatus
            object containing the status of an OCP+ cluster
        """

        return OCPStatusManager(self._fyre_api_user_name, self._fyre_api_key, site, cluster_name).execute_get_request()

    def get_clusters(self, site: Optional[str]) -> OCPPlusClusterData:
        """Returns OCP+ clusters

        Parameters
        ----------
        site
            OCP+ site

        Returns
        -------
        OCPPlusClusterData
            object containing OCP+ clusters
        """

        return OCPGetManager(self._fyre_api_user_name, self._fyre_api_key, site).execute_get_request()

    def get_default_sizes(self, platform: str, site: Optional[str]) -> OCPAvailableData:
        """Returns default node sizes

        Parameters
        ----------
        platform
            Platform
        site
            OCP+ site

        Returns
        -------
        OCPAvailableData
            object containing available OpenShift versions/default node sizes
        """

        return OCPAvailableManager(self._fyre_api_user_name, self._fyre_api_key, site, platform).execute_get_request()

    def get_openshift_versions(self, platform: str, site: Optional[str]) -> OCPAvailableData:
        """Returns available OpenShift Container Platform versions

        Parameters
        ----------
        platform
            Platform
        site
            OCP+ site

        Returns
        -------
        OCPAvailableData
            object containing available OpenShift versions/default node sizes
        """

        return OCPAvailableManager(self._fyre_api_user_name, self._fyre_api_key, site, platform).execute_get_request()

    def get_openshift_versions_all_platforms(self, site: Optional[str]) -> OpenShiftVersionData:
        """Returns available OpenShift Container Platform versions for all
        platforms

        Parameters
        ----------
        site
            OCP+ site

        Returns
        -------
        OpenShiftVersionData
            object containing available OpenShift versions for all platforms
        """

        openshift_versions_p = (
            OCPAvailableManager(self._fyre_api_user_name, self._fyre_api_key, site, "p")
            .execute_get_request()
            .get_openshift_versions()
        )

        openshift_versions_x = (
            OCPAvailableManager(self._fyre_api_user_name, self._fyre_api_key, site, "x")
            .execute_get_request()
            .get_openshift_versions()
        )

        openshift_versions_z = (
            OCPAvailableManager(self._fyre_api_user_name, self._fyre_api_key, site, "z")
            .execute_get_request()
            .get_openshift_versions()
        )

        return OpenShiftVersionData(openshift_versions_p, openshift_versions_x, openshift_versions_z)

    def get_quickburn_max_hours(self, site: Optional[str]) -> QuickBurnMaxHoursData:
        """Returns the maxmimum hours for a quick burn deployment

        Parameters
        ----------
        site
            OCP+ site

        Returns
        -------
        QuickBurnMaxHoursData
            object containing maxmimum hours for a quick burn deployment
        """

        return OCPQuickBurnMaxHoursManager(self._fyre_api_user_name, self._fyre_api_key, site).execute_get_request()

    def get_quickburn_sizes(self, site: Optional[str]) -> QuickBurnSizeData:
        """Returns available sizes for a quick burn deployment

        Parameters
        ----------
        site
            OCP+ site

        Returns
        -------
        QuickBurnSizeData
            object containing available sizes for a quick burn deployment
        """

        return OCPQuickBurnSizesManager(self._fyre_api_user_name, self._fyre_api_key, site).execute_get_request()

    def get_quota(self, site: Optional[str]) -> ProductGroupQuotaData:
        """Returns quotas for product groups the given FYRE user is part of

        Parameters
        ----------
        site
            OCP+ site

        Returns
        -------
        ProductGroupQuotaData
            object containing quotas for product groups the given FYRE user is part
            of
        """

        return QuotaRequestManager(self._fyre_api_user_name, self._fyre_api_key, site).execute_get_request()

    def get_request_status(self, request_id: str) -> RequestStatusData:
        """Get the status of a request

        Parameters
        ----------
        request_id
            Request ID

        Returns
        -------
        RequestStatusData
            object containing the status of a request
        """

        return OCPRequestManager(self._fyre_api_user_name, self._fyre_api_key, request_id).execute_get_request()

    def reboot(self, cluster_name: str, site: Optional[str]):
        """Reboots an OCP+ cluster

        Parameters
        ----------
        cluster_name
            Name of the OCP+ cluster to be rebooted
        site
            OCP+ site
        """

        OCPClusterActionManager(
            self._fyre_api_user_name, self._fyre_api_key, site, cluster_name, "reboot"
        ).execute_request_put_request()

    def reboot_node(self, cluster_name: str, node_name: str, site: Optional[str]):
        """Reboots a node of an OCP+ cluster

        Parameters
        ----------
        cluster_name
            Name of the OCP+ cluster
        node_name
            Name of the node to be rebooted
        site
            OCP+ site
        """

        OCPNodeActionManager(
            self._fyre_api_user_name, self._fyre_api_key, site, cluster_name, node_name, "reboot"
        ).execute_request_put_request()

    def redeploy_node(self, cluster_name: str, node_name: str, site: Optional[str]):
        """Redeploys a node of an OCP+ cluster

        Parameters
        ----------
        cluster_name
            Name of the OCP+ cluster
        node_name
            Name of the node to be redeployed
        site
            OCP+ site
        """

        OCPNodeActionManager(
            self._fyre_api_user_name, self._fyre_api_key, site, cluster_name, node_name, "redeploy"
        ).execute_request_put_request()

    def rm(self, cluster_name, site: Optional[str]):
        """Deletes an OCP+ cluster

        Parameters
        ----------
        cluster_name
            Name of the OCP+ cluster to be deleted
        site
            OCP+ site
        """

        OCPDeleteManager(self._fyre_api_user_name, self._fyre_api_key, site, cluster_name).execute_delete_request()

    def shutdown(self, cluster_name: str, site: Optional[str]):
        """Shuts down an OCP+ cluster

        Parameters
        ----------
        cluster_name
            Name of the OCP+ cluster to be shut down
        site
            OCP+ site
        """

        OCPClusterActionManager(
            self._fyre_api_user_name, self._fyre_api_key, site, cluster_name, "shutdown"
        ).execute_request_put_request()

    def shutdown_node(self, cluster_name: str, node_name: str, site: Optional[str]):
        """Shuts down a node of an OCP+ cluster

        Parameters
        ----------
        cluster_name
            Name of the OCP+ cluster
        node_name
            Name of the node to be shutdown
        site
            OCP+ site
        """

        OCPNodeActionManager(
            self._fyre_api_user_name, self._fyre_api_key, site, cluster_name, node_name, "shutdown"
        ).execute_request_put_request()

    def transfer(
        self,
        cluster_name: str,
        new_owner: Optional[str],
        new_product_group: Optional[int],
        comment: Optional[str],
        site: Optional[str],
    ):
        """Transfer an OCP+ cluster

        Parameters
        ----------
        cluster_name
            Name of the OCP+ cluster to be transferred
        new_owner
            User ID, username, or e-mail address of new owner
        new_product_group
            ID of new FYRE product group
        comment
            Comment
        site
            OCP+ site
        """

        ocp_transfer_put_request: OCPTransferPutRequest = {}

        if comment is not None:
            ocp_transfer_put_request["comment"] = comment

        if new_owner is not None:
            ocp_transfer_put_request["new_owner"] = new_owner

        if new_product_group is not None:
            ocp_transfer_put_request["product_group_id"] = str(new_product_group)

        OCPTransferPutManager(
            self._fyre_api_user_name,
            self._fyre_api_key,
            site,
            cluster_name,
        ).execute_put_request(ocp_transfer_put_request)

    def wait_for_request_completion(self, request_id: str):
        """Waits for an FYRE/OCP+ API request to complete

        The status of a request is itself retrieved using the FYRE/OCP+ API.
        To visualize the progress, a progress bar is shown.

        Parameters
        ----------
        request_id
            request ID
        """

        cpo.lib.fyre.utils.request_status_progress_bar.wait_for_request_completion(request_id, self.get_request_status)

    def _add_additional_disks(
        self, cluster_name: str, node_name: str, additional_disk_sizes: List[int], site: Optional[str]
    ):
        if len(additional_disk_sizes) != 0:
            logger.info("Adding additional disk(s)")

            ocp_disk_put_request: OCPDiskPutRequest = {
                "additional_disk": list(
                    map(lambda additional_disk_size: str(additional_disk_size), additional_disk_sizes)
                )
            }

            OCPDiskPutManager(
                self._fyre_api_user_name, self._fyre_api_key, site, cluster_name, node_name
            ).execute_request_put_request(ocp_disk_put_request)

    def _add_cluster(self, alias: Optional[str], site: Optional[str], ocp_post_response: OCPPostResponse):
        """Registers an existing OCP+ cluster

        Parameters
        ----------
        alias
            Alias used to reference a cluster instead of its server URL
        site
            OCP+ site
        ocp_post_response
            FYRE/OCP+ POST reponse (https://ocpapi.svl.ibm.com/v1/ocp)
        """

        cluster_name = ocp_post_response["cluster_name"]
        password = self.get_clusters(site).get_cluster(ocp_post_response["cluster_name"])["kubeadmin_password"]

        OCPPlusAPIManager.add_cluster(alias, cluster_name, password, site)

    def _add_keys(
        self,
        object: Union[OCPPostRequest, WorkerData],
        key_value_pairs: List[Tuple[str, Optional[Union[bool, int, str]]]],
    ):
        for key, value in key_value_pairs:
            if value is not None:
                object[key] = str(value)

    def _change_node_resources(
        self,
        cluster_name: str,
        node_name: str,
        node_num_cpus: Optional[int],
        node_ram_size: Optional[int],
        site: Optional[str],
    ):
        """Changes the resources of a node of an OCP+ cluster

        Parameters
        ----------
        cluster_name
            Name of the OCP+ cluster to be edited
        node_name
            Node name
        node_num_cpus
            Number of CPUs per node
        node_ram_size
            RAM size per node
        site
            OCP+ site
        """

        ocp_resource_put_request: OCPResourcePutRequest = {}

        if node_num_cpus is not None:
            ocp_resource_put_request["cpu"] = str(node_num_cpus)

        if node_ram_size is not None:
            ocp_resource_put_request["memory"] = str(node_ram_size)

        if len(ocp_resource_put_request) != 0:
            logger.info("Changing node resources")

            OCPResourcePutManager(
                self._fyre_api_user_name, self._fyre_api_key, site, cluster_name, node_name
            ).execute_request_put_request(ocp_resource_put_request)
