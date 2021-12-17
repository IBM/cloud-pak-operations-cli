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

import json

from typing import Dict

import cpo.config

from cpo.lib.cloud_pak_for_data.cpd_4_0_0.types.cloud_pak_for_data_service_license import (
    CloudPakForDataServiceLicense,
)
from cpo.lib.cloud_pak_for_data.cpd_4_0_0.types.custom_resource_metadata import (
    CustomResourceMetadata,
)
from cpo.lib.cloud_pak_for_data.cpd_4_0_0.types.subscription_metadata import (
    SubscriptionMetadata,
    SubscriptionMetadataSpec,
)
from cpo.lib.error import DataGateCLIException


class CloudPakForDataServiceManager:
    """Manages IBM Cloud Pak for Data operator subscriptions and custom
    resources"""

    def __init__(self):
        self._custom_resources: Dict[str, CustomResourceMetadata] = {}
        self._subscriptions: Dict[str, SubscriptionMetadata] = {}

    def get_custom_resource_metadata(self, service_name: str) -> CustomResourceMetadata:
        """Returns custom resource metadata for the given service name

        Parameters
        ----------
        service_name
            name of the service for which custom resource metadata shall be returned

        Returns
        -------
        CustomResourceMetadata
            custom resource metadata object
        """

        self._initialize_custom_resources_dict_if_required()

        if service_name not in self._custom_resources:
            raise DataGateCLIException("Unknown IBM Cloud Pak for Data service")

        return self._custom_resources[service_name]

    def get_custom_resource_metadata_dict(self) -> Dict[str, CustomResourceMetadata]:
        """Returns custom resource metadata for all services

        Returns
        -------
        Dict[str, CustomResourceMetadata]
            dictionary mapping service names to custom resource metadata objects
        """

        self._initialize_custom_resources_dict_if_required()

        return self._custom_resources

    def get_subscription_metadata(self, operator_name: str) -> SubscriptionMetadata:
        """Returns subscription metadata for the given operator name

        Parameters
        ----------
        operator_name
            name of the operator for which subscription metadata shall be returned

        Returns
        -------
        SubscriptionMetadata
            subscription metadata object
        """

        self._initialize_subscriptions_dict_if_required()

        if operator_name not in self._subscriptions:
            raise DataGateCLIException("Unknown IBM Cloud Pak for Data service")

        return self._subscriptions[operator_name]

    def get_subscription_metadata_dict_for_cloud_pak_for_data_services(self) -> Dict[str, SubscriptionMetadata]:
        """Returns subscription metadata for all operators

        Returns
        -------
        Dict[str, SubscriptionMetadata]
            dictionary mapping operator names to subscription metadata objects
        """

        self._initialize_subscriptions_dict_if_required()

        return dict(filter(lambda element: element[1].service, self._subscriptions.items()))

    def is_cloud_pak_for_data_service(self, service_name: str):
        """Returns whether there is an IBM Cloud Pak for Data service with the
        given name

        Parameters
        ----------
        service_name
            name of the service to be checked

        Returns
        -------
        bool
            true, if there is an IBM Cloud Pak for Data service with the given name
        """

        self._initialize_custom_resources_dict_if_required()

        return service_name in self._custom_resources

    def _initialize_custom_resources_dict_if_required(self):
        if len(self._custom_resources) == 0:
            with open(
                cpo.config.configuration_manager.get_deps_directory_path() / "config" / "cpd-custom-resources.json"
            ) as json_file:
                for key, value in json.load(json_file).items():
                    self._custom_resources[key] = CustomResourceMetadata(
                        description=value["description"],
                        group=value["group"],
                        kind=value["kind"],
                        licenses=list(map(lambda license: CloudPakForDataServiceLicense[license], value["licenses"])),
                        name=value["name"],
                        operator_name=value["operator_name"],
                        spec=value["spec"],
                        status_key_name=value["status_key_name"],
                        storage_option_required=value["storage_option_required"],
                        version=value["version"],
                    )

    def _initialize_subscriptions_dict_if_required(self):
        if len(self._subscriptions) == 0:
            with open(
                cpo.config.configuration_manager.get_deps_directory_path() / "config" / "cpd-subscriptions.json"
            ) as json_file:
                for key, value in json.load(json_file).items():
                    self._subscriptions[key] = SubscriptionMetadata(
                        dependencies=value["dependencies"],
                        labels=value["labels"],
                        name=value["name"],
                        required_namespace=value["required_namespace"],
                        service=value["service"],
                        spec=SubscriptionMetadataSpec(
                            channel=value["spec"]["channel"],
                            name=value["spec"]["name"],
                            source=value["spec"].get("source"),
                        ),
                    )
