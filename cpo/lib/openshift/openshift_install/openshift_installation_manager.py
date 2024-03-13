#  Copyright 2023, 2024 IBM Corporation
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

import json
import logging
import pathlib
import re as regex
import shutil

from abc import ABC, abstractmethod
from typing import Any, Final

import semver
import yaml

from filelock import FileLock

from cpo.config import configuration_manager
from cpo.config.cluster_credentials_manager import cluster_credentials_manager
from cpo.lib.dependency_manager.dependency_manager import DependencyManager
from cpo.lib.dependency_manager.plugins.openshift.openshift_install_plugin import OpenShiftInstallPlugIn
from cpo.lib.openshift.openshift_install.types.architecture import Architecture
from cpo.utils.error import CloudPakOperationsCLIException

file_lock = FileLock(configuration_manager.get_cli_data_directory_path() / "openshift-install.lock")


class Dumper(yaml.Dumper):
    """Responsible for indenting YAML lists

    Default formatting of lists (yaml package):

    key:
    - element 1
    - element 2
    - …

    Improved formatting of lists:

    key:
      - element 1
      - element 2
      - …
    """

    # override
    def increase_indent(self, flow=False, *args, **kwargs):
        return super().increase_indent(flow=flow, indentless=False)


class OpenShiftInstallationManager(ABC):
    """Responsible for executing openshift-install"""

    def create_cluster(
        self,
        cluster_type: str,
        cluster_name: str,
        base_domain: str,
        alias: str | None,
        insecure_skip_tls_verify: bool | None,
        ocp_version: semver.Version,
        configuration: Any,
        additional_cluster_data: dict[str, Any] | None = None,
    ) -> str:
        OpenShiftInstallationManager._OPENSHIFT_INSTALL_PATH.mkdir(exist_ok=True)

        cluster_fqdn = f"{cluster_name}.{base_domain}"
        assets_directory = self._create_assets_directory(cluster_fqdn)
        install_config_file = assets_directory / "install-config.yaml"

        with open(install_config_file, "w") as yaml_file:
            yaml.dump(configuration, yaml_file, Dumper=Dumper)

        shutil.copy2(install_config_file, assets_directory / "install-config.yaml.bak")

        args = ["create", "cluster", "--dir", str(assets_directory)]

        if logging.getLogger().isEnabledFor(logging.DEBUG):
            args.append("--log-level")
            args.append("debug")

        process_result = DependencyManager.get_instance().execute_binary(
            OpenShiftInstallPlugIn,
            ocp_version,
            args,
            capture_output=True,
            env=self._get_environment(),
            print_captured_output=True,
        )

        cluster_id = self._get_cluster_id(assets_directory)
        search_result = regex.search(
            'Login to the console with user: "(.+)", and password: "(.+)"', process_result.stderr
        )

        if search_result is None:
            raise CloudPakOperationsCLIException("Credentials could not be extracted from openshift-install output")

        cluster_data = {
            "cluster_id": cluster_id,
            "password": search_result.group(2),
            "username": search_result.group(1),
        }

        if insecure_skip_tls_verify is not None:
            cluster_data["insecure_skip_tls_verify"] = insecure_skip_tls_verify

        if additional_cluster_data is not None:
            cluster_data.update(additional_cluster_data)

        cluster_credentials_manager.add_cluster(
            alias if (alias is not None) else "",
            f"https://api.{cluster_name}.{base_domain}:6443",
            cluster_type,
            cluster_data,
        )

        return cluster_id

    def destroy_cluster(self, name: str, base_domain: str):
        """Destroys the OpenShift cluster with the given name and base domain

        The asset directory corresponding to the cluster to be destroyed must be
        located here:

        ~/.cpo/openshift-install/{name}.{base_domain}

        Parameters
        ----------
        name
            Name of the cluster
        base_domain
            Base domain of the cloud provider
        """

        cluster_fqdn = f"{name}.{base_domain}"
        assets_directory = OpenShiftInstallationManager._OPENSHIFT_INSTALL_PATH / cluster_fqdn

        if not assets_directory.exists():
            raise CloudPakOperationsCLIException(f"Assets directory for cluster {cluster_fqdn} does not exist")

        args = ["destroy", "cluster", "--dir", str(assets_directory)]

        if logging.getLogger().isEnabledFor(logging.DEBUG):
            args.append("--log-level")
            args.append("debug")

        DependencyManager.get_instance().execute_binary(OpenShiftInstallPlugIn, None, args, env=self._get_environment())
        shutil.rmtree(assets_directory)

        server = f"https://api.{name}.{base_domain}:6443"

        if cluster_credentials_manager.get_cluster(server) is not None:
            cluster_credentials_manager.remove_cluster(server)

    @file_lock
    def _create_assets_directory(self, cluster_fqdn: str) -> pathlib.Path:
        assets_directory = OpenShiftInstallationManager._OPENSHIFT_INSTALL_PATH / cluster_fqdn

        if assets_directory.exists():
            raise CloudPakOperationsCLIException(f"An assets directory for cluster {cluster_fqdn} already exists")

        assets_directory.mkdir()

        return assets_directory

    def _get_cluster_id(self, assets_directory: pathlib.Path) -> str:
        with open(assets_directory / "terraform.tfvars.json") as terraform_tfvars_file:
            terraform_tfvars_file_contents = json.load(terraform_tfvars_file)

            assert "cluster_id" in terraform_tfvars_file_contents

            return terraform_tfvars_file_contents["cluster_id"]

    @abstractmethod
    def _get_environment(self) -> dict[str, str]:
        pass

    def _get_shared_configuration(
        self,
        cluster_name: str,
        base_domain: str,
        architecture: Architecture,
        hyperthreading: bool,
        num_master_replicas: int,
        num_worker_replicas: int,
        ocp_pull_secret: str,
        ocp_ssh_key: str,
    ) -> Any:
        return {
            "additionalTrustBundlePolicy": "Proxyonly",
            "apiVersion": "v1",
            "baseDomain": base_domain,
            "compute": [
                {
                    "architecture": architecture.name,
                    "hyperthreading": "Enabled" if hyperthreading else "Disabled",
                    "name": "worker",
                    "platform": {},
                    "replicas": num_worker_replicas,
                }
            ],
            "controlPlane": {
                "architecture": architecture.name,
                "hyperthreading": "Enabled" if hyperthreading else "Disabled",
                "name": "master",
                "platform": {},
                "replicas": num_master_replicas,
            },
            "metadata": {
                "creationTimestamp": None,
                "name": cluster_name,
            },
            "networking": {
                "clusterNetwork": [
                    {
                        "cidr": "10.128.0.0/14",
                        "hostPrefix": 23,
                    }
                ],
                "machineNetwork": [
                    {
                        "cidr": "10.0.0.0/16",
                    }
                ],
                "networkType": "OVNKubernetes",
                "serviceNetwork": [
                    "172.30.0.0/16",
                ],
            },
            "platform": {},
            "publish": "External",
            "pullSecret": ocp_pull_secret,
            "sshKey": ocp_ssh_key,
        }

    _OPENSHIFT_INSTALL_PATH: Final[pathlib.Path] = (
        configuration_manager.get_cli_data_directory_path() / "openshift-install"
    )
