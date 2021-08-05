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

from typing import Any, Callable

from kubernetes import client, config

import dg.utils.network

from dg.lib.error import DataGateCLIException
from dg.lib.openshift.credentials.credentials import AbstractCredentials
from dg.lib.openshift.data.global_pull_secret_data import GlobalPullSecretData

logger = logging.getLogger(__name__)


class OpenShiftAPIManager:
    """Manages REST communication with the OpenShift REST API

    This class uses the Kubernetes Python client
    (https://github.com/kubernetes-client/python). The OpenShift Python
    client (https://github.com/openshift/openshift-restclient-python) was
    deliberately not used as its performance suffers from the amount of REST
    API calls during endpoint discovery.
    """

    def __init__(self, credentials: AbstractCredentials):
        self._credentials = credentials
        self._kube_config_initialized = False

    def credentials_exist(self, registry_location: str) -> bool:
        """Returns whether the global pull secret contains credentials for the
        given registry location

        Parameters
        ----------
        registry_location
            registry location to be searched for

        Returns
        -------
        bool
            true, if the global pull secret contains credentials for the given
            registry location
        """

        global_pull_secret_data = self.get_global_pull_secret_data()

        return global_pull_secret_data.contains(registry_location)

    def delete_credentials(self, registry_location: str):
        """Deletes credentials for the given registry location from the global
        pull secret

        Parameters
        ----------
        registry_location
            registry location for which credentials shall be deleted
        """

        global_pull_secret_data = self.get_global_pull_secret_data()
        global_pull_secret_data.delete_credentials(registry_location)

        self.execute_kubernetes_client(self._patch_credentials, global_pull_secret_data=global_pull_secret_data)

    def execute_kubernetes_client(self, method: Callable[..., Any], **kwargs) -> Any:
        if not self._kube_config_initialized:
            self._set_kube_config()

        if self._credentials.insecure_skip_tls_verify:
            dg.utils.network.disable_insecure_request_warning()

        result: Any = None

        try:
            result = method(**kwargs)
        except client.ApiException as exception:
            if exception.status == 401:
                if not self._credentials.is_refreshable():
                    raise DataGateCLIException("OAuth access token expired and cannot be refreshed")

                self._credentials.refresh_access_token()
                self._set_kube_config()
                result = method(**kwargs)
            else:
                raise exception
        finally:
            dg.utils.network.enable_insecure_request_warning()

        return result

    def get_global_pull_secret_data(self) -> GlobalPullSecretData:
        """Returns the global pull secret as a data object

        Returns
        -------
        GlobalPullSecretData
            global pull secret data object
        """

        return self.execute_kubernetes_client(self._get_credentials)

    def patch_credentials(self, global_pull_secret_data: GlobalPullSecretData):
        """Patches the global pull secret based on the given data object

        Parameters
        ----------
        global_pull_secret_data
            global pull secret data object
        """

        self.execute_kubernetes_client(self._patch_credentials, global_pull_secret_data=global_pull_secret_data)

    def set_credentials(self, registry_location: str, username: str, password: str):
        """Sets credentials for the given registry location

        Parameters
        ----------
        registry_location
            registry location for which credentials shall be set
        username
            registry location username
        password
            registry location password
        """

        global_pull_secret_data = self.get_global_pull_secret_data()
        global_pull_secret_data.set_credentials(registry_location, username, password)

        self.patch_credentials(global_pull_secret_data)

    def _get_credentials(self) -> GlobalPullSecretData:
        core_v1_api = client.CoreV1Api()
        core_v1_api_result: Any = core_v1_api.read_namespaced_secret("pull-secret", "openshift-config")

        return GlobalPullSecretData(core_v1_api_result.data)

    def _patch_credentials(self, global_pull_secret_data: GlobalPullSecretData):
        core_v1_api = client.CoreV1Api()
        core_v1_api.patch_namespaced_secret("pull-secret", "openshift-config", global_pull_secret_data.get_json_patch())

    def _set_kube_config(self):
        """Sets the Kubernetes configuration of the Kubernetes Python client"""

        config.load_kube_config_from_dict(
            {
                "clusters": [
                    {
                        "cluster": {
                            "insecure-skip-tls-verify": self._credentials.insecure_skip_tls_verify,
                            "server": self._credentials.server,
                        },
                        "name": "cluster",
                    }
                ],
                "contexts": [
                    {
                        "context": {
                            "cluster": "cluster",
                            "user": "user",
                        },
                        "name": "context",
                    }
                ],
                "current-context": "context",
                "users": [
                    {
                        "name": "user",
                        "user": {
                            "token": self._credentials.get_access_token(),
                        },
                    }
                ],
            }
        )
