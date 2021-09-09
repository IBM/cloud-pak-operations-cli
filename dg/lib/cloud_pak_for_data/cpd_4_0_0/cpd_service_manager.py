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

from typing import Dict

from dg.lib.cloud_pak_for_data.cpd_4_0_0.types.cloud_pak_for_data_service_license import (
    CloudPakForDataServiceLicense,
)
from dg.lib.cloud_pak_for_data.cpd_4_0_0.types.custom_resource_metadata import (
    CustomResourceMetadata,
)
from dg.lib.cloud_pak_for_data.cpd_4_0_0.types.subscription_metadata import (
    SubscriptionMetadata,
    SubscriptionMetadataSpec,
)
from dg.lib.error import DataGateCLIException


class CloudPakForDataServiceManager:
    """Manages IBM Cloud Pak for Data operator subscriptions and custom
    resources"""

    def __init__(self):
        self._custom_resources: Dict[str, CustomResourceMetadata] = {
            # https://www.ibm.com/docs/en/cloud-paks/cp-data/4.0?topic=iddg-installing-db2-data-gate#operator-install__install
            "datagate": CustomResourceMetadata(
                api_version="datagate.cpd.ibm.com/v1",
                description="Db2 Data Gate",
                kind="DatagateService",
                licenses=[
                    CloudPakForDataServiceLicense.Enterprise,
                    CloudPakForDataServiceLicense.Standard,
                ],
                name="datagateservice-cr",
                operator_name="ibm-datagate-operator",
                spec={
                    "datagate": "yes",
                    "version": "2.0.1",
                },
                status_key_name="datagateStatus",
                storage_option_required=True,
            ),
            # https://www.ibm.com/docs/en/cloud-paks/cp-data/4.0?topic=id-installing-db2#operator-install__install
            "db2oltp": CustomResourceMetadata(
                api_version="databases.cpd.ibm.com/v1",
                description="Db2",
                kind="Db2oltpService",
                licenses=[
                    CloudPakForDataServiceLicense.Advanced,
                    CloudPakForDataServiceLicense.Community,
                    CloudPakForDataServiceLicense.Standard,
                ],
                name="db2oltp-cr",
                operator_name="ibm-db2oltp-cp4d-operator",
                spec={},
                status_key_name="db2oltpStatus",
                storage_option_required=False,
            ),
            # https://www.ibm.com/docs/en/cloud-paks/cp-data/4.0?topic=idw-installing-db2-warehouse#operator-install__install
            "db2wh": CustomResourceMetadata(
                api_version="databases.cpd.ibm.com/v1",
                description="Db2 Warehouse",
                kind="Db2whService",
                licenses=[
                    CloudPakForDataServiceLicense.Enterprise,
                    CloudPakForDataServiceLicense.Standard,
                ],
                name="db2wh-cr",
                operator_name="ibm-db2wh-cp4d-operator",
                spec={},
                status_key_name="db2whStatus",
                storage_option_required=False,
            ),
            # https://www.ibm.com/docs/en/cloud-paks/cp-data/4.0?topic=iddmc-installing-db2-data-management-console#operator-install__conref-L1-section-install
            "dmc": CustomResourceMetadata(
                api_version="dmc.databases.ibm.com/v1",
                description="Db2 Data Management Console",
                kind="Dmcaddon",
                licenses=[
                    CloudPakForDataServiceLicense.Enterprise,
                    CloudPakForDataServiceLicense.Standard,
                ],
                name="dmc-addon",
                operator_name="ibm-dmc-operator",
                spec={
                    "version": "4.0.1",
                },
                status_key_name="dmcAddonStatus",
                storage_option_required=False,
            ),
        }

        self._subscriptions: Dict[str, SubscriptionMetadata] = {
            "analyticsengine-operator": SubscriptionMetadata(
                dependencies=[],
                labels={
                    "app.kubernetes.io/instance": "ibm-cpd-ae-operator-subscription",
                    "app.kubernetes.io/managed-by": "ibm-cpd-ae-operator",
                    "app.kubernetes.io/name": "ibm-cpd-ae-operator-subscription",
                },
                name="ibm-cpd-ae-operator-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="stable-v1",
                    name="analyticsengine-operator",
                ),
            ),
            "cloud-native-postgresql": SubscriptionMetadata(
                dependencies=[],
                labels={},
                name="cloud-native-postgresql-catalog-subscription",
                required_namespace="openshift-operators",
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="stable",
                    name="cloud-native-postgresql",
                    source="cloud-native-postgresql-catalog",
                ),
            ),
            "cpd-platform-operator": SubscriptionMetadata(
                dependencies=[],
                labels={},
                name="cpd-operator",
                required_namespace=None,
                service=False,
                spec=SubscriptionMetadataSpec(
                    channel="v2.0",
                    name="cpd-platform-operator",
                ),
            ),
            "db2u-operator": SubscriptionMetadata(
                dependencies=[],
                labels={},
                name="ibm-db2u-operator",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v1.1",
                    name="db2u-operator",
                ),
            ),
            "ibm-bigsql-operator": SubscriptionMetadata(
                dependencies=[
                    "db2u-operator",
                ],
                labels={},
                name="ibm-bigsql-operator-catalog-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v7.2",
                    name="ibm-bigsql-operator",
                ),
            ),
            "ibm-ca-operator": SubscriptionMetadata(
                dependencies=[],
                labels={
                    "app.kubernetes.io/instance": "ibm-ca-operator",
                    "app.kubernetes.io/managed-by": "ibm-ca-operator",
                    "app.kubernetes.io/name": "ibm-ca-operator",
                },
                name="ibm-ca-operator-catalog-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v4.0",
                    name="ibm-ca-operator",
                ),
            ),
            "ibm-cde-operator": SubscriptionMetadata(
                dependencies=[],
                labels={
                    "app.kubernetes.io/instance": "ibm-cde-operator-subscription",
                    "app.kubernetes.io/managed-by": "ibm-cde-operator",
                    "app.kubernetes.io/name": "ibm-cde-operator-subscription",
                },
                name="ibm-cde-operator-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v1.0",
                    name="ibm-cde-operator",
                ),
            ),
            "ibm-common-service-operator": SubscriptionMetadata(
                dependencies=[],
                labels={},
                name="ibm-common-service-operator",
                required_namespace=None,
                service=False,
                spec=SubscriptionMetadataSpec(
                    channel="v3",
                    name="ibm-common-service-operator",
                ),
            ),
            "ibm-cpd-dods": SubscriptionMetadata(
                dependencies=[],
                labels={
                    "app.kubernetes.io/instance": "ibm-cpd-dods-operator-catalog-subscription",
                    "app.kubernetes.io/managed-by": "ibm-cpd-dods-operator",
                    "app.kubernetes.io/name": "ibm-cpd-dods-operator-catalog-subscription",
                },
                name="ibm-cpd-dods-operator-catalog-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v4.0",
                    name="ibm-cpd-dods",
                ),
            ),
            "ibm-cpd-edb": SubscriptionMetadata(
                dependencies=[
                    "cloud-native-postgresql",
                ],
                labels={},
                name="ibm-cpd-edb-operator-catalog-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="stable",
                    name="ibm-cpd-edb",
                ),
            ),
            "ibm-cpd-hadoop": SubscriptionMetadata(
                dependencies=[],
                labels={
                    "app.kubernetes.io/instance": "ibm-cpd-hadoop-operator-catalog-subscription",
                    "app.kubernetes.io/managed-by": "ibm-cpd-hadoop-operator",
                    "app.kubernetes.io/name": "ibm-cpd-hadoop-operator-catalog-subscription",
                },
                name="ibm-cpd-hadoop-operator-catalog-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v1.0",
                    name="ibm-cpd-hadoop",
                ),
            ),
            "ibm-cpd-mongodb": SubscriptionMetadata(
                dependencies=[
                    "mongodb-enterprise",
                ],
                labels={},
                name="ibm-cpd-mongodb-catalog-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="stable",
                    name="ibm-cpd-mongodb",
                ),
            ),
            "ibm-cpd-openpages-operator": SubscriptionMetadata(
                dependencies=[
                    "ibm-db2aaservice-cp4d-operator",
                ],
                labels={},
                name="ibm-cpd-openpages-operator",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v1.0",
                    name="ibm-cpd-openpages-operator",
                ),
            ),
            "ibm-cpd-productmaster": SubscriptionMetadata(
                dependencies=[],
                labels={},
                name="ibm-productmaster-catalog-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="alpha",
                    name="ibm-cpd-productmaster",
                ),
            ),
            "ibm-cpd-rstudio": SubscriptionMetadata(
                dependencies=[],
                labels={
                    "app.kubernetes.io/instance": "ibm-cpd-rstudio-operator-catalog-subscription",
                    "app.kubernetes.io/managed-by": "ibm-cpd-rstudio-operator",
                    "app.kubernetes.io/name": "ibm-cpd-rstudio-operator-catalog-subscription",
                },
                name="ibm-cpd-rstudio-operator-catalog-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v1.0",
                    name="ibm-cpd-rstudio",
                ),
            ),
            "ibm-cpd-spss": SubscriptionMetadata(
                dependencies=[],
                labels={
                    "app.kubernetes.io/instance": "ibm-cpd-spss-operator-catalog-subscription",
                    "app.kubernetes.io/managed-by": "ibm-cpd-spss-operator",
                    "app.kubernetes.io/name": "ibm-cpd-spss-operator-catalog-subscription",
                },
                name="ibm-cpd-spss-operator-catalog-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v1.0",
                    name="ibm-cpd-spss",
                ),
            ),
            "ibm-cpd-wkc": SubscriptionMetadata(
                dependencies=[
                    "db2u-operator",
                ],
                labels={
                    "app.kubernetes.io/instance": "ibm-cpd-wkc-operator-catalog-subscription",
                    "app.kubernetes.io/managed-by": "ibm-cpd-wkc-operator",
                    "app.kubernetes.io/name": "ibm-cpd-wkc-operator-catalog-subscription",
                },
                name="ibm-cpd-wkc-operator-catalog-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v1.0",
                    name="ibm-cpd-wkc",
                ),
            ),
            "ibm-cpd-wml-accelerator-operator": SubscriptionMetadata(
                dependencies=[],
                labels={},
                name="ibm-cpd-wml-accelerator-operator",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="WML-Accelerator-2.3",
                    name="ibm-cpd-wml-accelerator-operator",
                ),
            ),
            "ibm-cpd-wml-operator": SubscriptionMetadata(
                dependencies=[],
                labels={
                    "app.kubernetes.io/instance": "ibm-cpd-wml-operator-subscription",
                    "app.kubernetes.io/managed-by": "ibm-cpd-wml-operator",
                    "app.kubernetes.io/name": "ibm-cpd-wml-operator-subscription",
                },
                name="ibm-cpd-wml-operator-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v1.1",
                    name="ibm-cpd-wml-operator",
                ),
            ),
            "ibm-cpd-wos": SubscriptionMetadata(
                dependencies=[],
                labels={
                    "app.kubernetes.io/instance": "ibm-watson-openscale-operator-subscription",
                    "app.kubernetes.io/managed-by": "ibm-watson-openscale-operator",
                    "app.kubernetes.io/name": "ibm-watson-openscale-operator-subscription",
                },
                name="ibm-watson-openscale-operator-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v1",
                    name="ibm-cpd-wos",
                ),
            ),
            "ibm-cpd-ws-runtimes": SubscriptionMetadata(
                dependencies=[],
                labels={
                    "app.kubernetes.io/instance": "ibm-cpd-ws-runtimes-operator-catalog-subscription",
                    "app.kubernetes.io/managed-by": "ibm-cpd-ws-runtimes-operator",
                    "app.kubernetes.io/name": "ibm-cpd-ws-runtimes-operator",
                },
                name="ibm-cpd-ws-runtimes-operator",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v1.0",
                    name="ibm-cpd-ws-runtimes",
                ),
            ),
            "ibm-cpd-wsl": SubscriptionMetadata(
                dependencies=[],
                labels={},
                name="ibm-cpd-ws-operator-catalog-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v2.0",
                    name="ibm-cpd-wsl",
                ),
            ),
            "ibm-datagate-operator": SubscriptionMetadata(
                dependencies=[],
                labels={
                    "app.kubernetes.io/instance": "ibm-datagate-operator-subscription",
                    "app.kubernetes.io/managed-by": "ibm-datagate-operator",
                    "app.kubernetes.io/name": "ibm-datagate-operator-subscription",
                },
                name="ibm-datagate-operator-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v2.0",
                    name="ibm-datagate-operator",
                ),
            ),
            "ibm-datastage-operator": SubscriptionMetadata(
                dependencies=[],
                labels={},
                name="ibm-datastage-operator",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v1.0",
                    name="ibm-datastage-operator",
                ),
            ),
            "ibm-db2aaservice-cp4d-operator": SubscriptionMetadata(
                dependencies=[],
                labels={},
                name="ibm-db2aaservice-catalog-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v1.0",
                    name="ibm-db2aaservice-cp4d-operator",
                ),
            ),
            "ibm-db2oltp-cp4d-operator": SubscriptionMetadata(
                dependencies=[
                    "db2u-operator",
                ],
                labels={},
                name="ibm-db2oltp-cp4d-operator-catalog-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v1.0",
                    name="ibm-db2oltp-cp4d-operator",
                ),
            ),
            "ibm-db2wh-cp4d-operator": SubscriptionMetadata(
                dependencies=[
                    "db2u-operator",
                ],
                labels={},
                name="ibm-db2wh-cp4d-operator-catalog-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v1.0",
                    name="ibm-db2wh-cp4d-operator",
                ),
            ),
            "ibm-dmc-operator": SubscriptionMetadata(
                dependencies=[],
                labels={},
                name="ibm-dmc-operator-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v1.0",
                    name="ibm-dmc-operator",
                ),
            ),
            "ibm-dv-operator": SubscriptionMetadata(
                dependencies=[
                    "db2u-operator",
                ],
                labels={},
                name="ibm-dv-operator-catalog-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v1.7",
                    name="ibm-dv-operator",
                ),
            ),
            "ibm-mdm": SubscriptionMetadata(
                dependencies=[],
                labels={
                    "app.kubernetes.io/instance": "ibm-mdm-operator-subscription",
                    "app.kubernetes.io/managed-by": "ibm-mdm-operator",
                    "app.kubernetes.io/name": "ibm-mdm-operator-subscription",
                },
                name="ibm-mdm-operator-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v1.1",
                    name="ibm-mdm",
                ),
            ),
            "ibm-planning-analytics-operator": SubscriptionMetadata(
                dependencies=[],
                labels={},
                name="ibm-planning-analytics-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v1.0",
                    name="ibm-planning-analytics-operator",
                ),
            ),
            "ibm-voice-gateway-operator": SubscriptionMetadata(
                dependencies=[],
                labels={},
                name="ibm-voice-gateway-operator-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v1.0",
                    name="ibm-voice-gateway-operator",
                ),
            ),
            "ibm-watson-assistant-operator": SubscriptionMetadata(
                dependencies=[],
                labels={},
                name="ibm-watson-assistant-operator-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v4.0",
                    name="ibm-watson-assistant-operator",
                ),
            ),
            "ibm-watson-discovery-operator": SubscriptionMetadata(
                dependencies=[],
                labels={
                    "app.kubernetes.io/instance": "ibm-watson-discovery-operator-subscription",
                    "app.kubernetes.io/managed-by": "ibm-watson-discovery-operator",
                    "app.kubernetes.io/name": "ibm-watson-discovery-operator-subscription",
                },
                name="ibm-watson-discovery-operator-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v4.0",
                    name="ibm-watson-discovery-operator",
                ),
            ),
            "ibm-watson-speech-operator": SubscriptionMetadata(
                dependencies=[],
                labels={},
                name="ibm-watson-speech-operator-subscription",
                required_namespace=None,
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="v4.0",
                    name="ibm-watson-speech-operator",
                ),
            ),
            "mongodb-enterprise": SubscriptionMetadata(
                dependencies=[],
                labels={},
                name="ibm-mongodb-enterprise-catalog-subscription",
                required_namespace="openshift-operators",
                service=True,
                spec=SubscriptionMetadataSpec(
                    channel="stable",
                    name="mongodb-enterprise",
                    source="ibm-mongodb-enterprise-catalog",
                ),
            ),
        }

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

        return service_name in self._custom_resources
