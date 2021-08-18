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

from functools import reduce
from typing import Final, List

from dg.lib.openshift.types.catalog_source import CatalogSourceList


class CatalogSourceManager:
    """Manages OpenShift catalog sources"""

    def __init__(self):
        self._catalog_sources: CatalogSourceList = [
            {
                "apiVersion": CatalogSourceManager._API_VERSION,
                "kind": "CatalogSource",
                "metadata": {
                    "name": "ibm-cloud-databases-redis-operator-catalog",
                    "namespace": "openshift-marketplace",
                },
                "spec": {
                    "displayName": "ibm-cloud-databases-redis-operator-catalog",
                    "image": "icr.io/cpopen/ibm-cloud-databases-redis-catalog@sha256:980e4182ec20a01a93f3c18310e0aa5346dc299c551bd8aca070ddf2a5bf9ca5",  # noqa: E501
                    "publisher": "IBM",
                    "sourceType": "grpc",
                },
            },
            {
                "apiVersion": CatalogSourceManager._API_VERSION,
                "kind": "CatalogSource",
                "metadata": {
                    "name": "ibm-cpd-ccs-operator-catalog",
                    "namespace": "openshift-marketplace",
                },
                "spec": {
                    "displayName": "CPD Common Core Services",
                    "image": "icr.io/cpopen/ibm-cpd-ccs-operator-catalog@sha256:34854b0b5684d670cf1624d01e659e9900f4206987242b453ee917b32b79f5b7",  # noqa: E501
                    "imagePullPolicy": "Always",
                    "publisher": "IBM",
                    "sourceType": "grpc",
                },
            },
            {
                "apiVersion": CatalogSourceManager._API_VERSION,
                "kind": "CatalogSource",
                "metadata": {
                    "name": "ibm-cpd-datarefinery-operator-catalog",
                    "namespace": "openshift-marketplace",
                },
                "spec": {
                    "displayName": "Cloud Pak for Data IBM DataRefinery",
                    "image": "icr.io/cpopen/ibm-cpd-datarefinery-operator-catalog@sha256:27c6b458244a7c8d12da72a18811d797a1bef19dadf84b38cedf6461fe53643a",  # noqa: E501
                    "imagePullPolicy": "Always",
                    "publisher": "IBM",
                    "sourceType": "grpc",
                },
            },
            {
                "apiVersion": CatalogSourceManager._API_VERSION,
                "kind": "CatalogSource",
                "metadata": {
                    "name": "ibm-cpd-iis-operator-catalog",
                    "namespace": "openshift-marketplace",
                },
                "spec": {
                    "displayName": "CPD IBM Information Server",
                    "image": "icr.io/cpopen/ibm-cpd-iis-operator-catalog@sha256:3ad952987b2f4d921459b0d3bad8e30a7ddae9e0c5beb407b98cf3c09713efcc",  # noqa: E501
                    "imagePullPolicy": "Always",
                    "publisher": "IBM",
                    "sourceType": "grpc",
                },
            },
            {
                "apiVersion": CatalogSourceManager._API_VERSION,
                "kind": "CatalogSource",
                "metadata": {
                    "name": "ibm-cpd-wml-operator-catalog",
                    "namespace": "openshift-marketplace",
                },
                "spec": {
                    "displayName": "Cloud Pak for Data Watson Machine Learning",
                    "image": "icr.io/cpopen/ibm-cpd-wml-operator-catalog@sha256:d2da8a2573c0241b5c53af4d875dbfbf988484768caec2e4e6231417828cb192",  # noqa: E501
                    "imagePullPolicy": "Always",
                    "publisher": "IBM",
                    "sourceType": "grpc",
                    "updateStrategy": {
                        "registryPoll": {
                            "interval": "45m",
                        }
                    },
                },
            },
            {
                "apiVersion": CatalogSourceManager._API_VERSION,
                "kind": "CatalogSource",
                "metadata": {
                    "name": "ibm-cpd-ws-operator-catalog",
                    "namespace": "openshift-marketplace",
                },
                "spec": {
                    "displayName": "CPD IBM Watson Studio",
                    "image": "icr.io/cpopen/ibm-cpd-ws-operator-catalog@sha256:bf6b42df3d8cee32740d3273154986b28dedbf03349116fba39974dc29610521",  # noqa: E501
                    "imagePullPolicy": "Always",
                    "publisher": "IBM",
                    "sourceType": "grpc",
                },
            },
            {
                "apiVersion": CatalogSourceManager._API_VERSION,
                "kind": "CatalogSource",
                "metadata": {
                    "name": "ibm-cpd-ws-runtimes-operator-catalog",
                    "namespace": "openshift-marketplace",
                },
                "spec": {
                    "displayName": "CPD Watson Studio Runtimes",
                    "image": "icr.io/cpopen/ibm-cpd-ws-runtimes-operator-catalog@sha256:c1faf293456261f418e01795eecd4fe8b48cc1e8b37631fb6433fad261b74ea4",  # noqa: E501
                    "imagePullPolicy": "Always",
                    "publisher": "IBM",
                    "sourceType": "grpc",
                },
            },
            {
                "apiVersion": CatalogSourceManager._API_VERSION,
                "kind": "CatalogSource",
                "metadata": {
                    "name": "ibm-db2aaservice-cp4d-operator-catalog",
                    "namespace": "openshift-marketplace",
                },
                "spec": {
                    "displayName": "IBM Db2aaservice CP4D Catalog",
                    "image": "icr.io/cpopen/ibm-db2aaservice-cp4d-operator-catalog@sha256:a0d9b6c314193795ec1918e4227ede916743381285b719b3d8cfb05c35fec071",  # noqa: E501
                    "imagePullPolicy": "Always",
                    "publisher": "IBM",
                    "sourceType": "grpc",
                },
            },
            {
                "apiVersion": CatalogSourceManager._API_VERSION,
                "kind": "CatalogSource",
                "metadata": {
                    "name": "ibm-db2uoperator-catalog",
                    "namespace": "openshift-marketplace",
                },
                "spec": {
                    "displayName": "IBM Db2U Catalog",
                    "image": "docker.io/ibmcom/ibm-db2uoperator-catalog:latest",
                    "imagePullPolicy": "Always",
                    "publisher": "IBM",
                    "sourceType": "grpc",
                    "updateStrategy": {
                        "registryPoll": {
                            "interval": "45m",
                        },
                    },
                },
            },
            {
                "apiVersion": CatalogSourceManager._API_VERSION,
                "kind": "CatalogSource",
                "metadata": {
                    "name": "ibm-rabbitmq-operator-catalog",
                    "namespace": "openshift-marketplace",
                },
                "spec": {
                    "displayName": "IBM RabbitMQ operator Catalog",
                    "image": "icr.io/cpopen/opencontent-rabbitmq-operator-catalog@sha256:c3b14816eabc04bcdd5c653eaf6e0824adb020ca45d81d57059f50c80f22964f",  # noqa: E501
                    "publisher": "IBM",
                    "sourceType": "grpc",
                    "updateStrategy": {
                        "registryPoll": {
                            "interval": "45m",
                        }
                    },
                },
            },
            {
                "apiVersion": CatalogSourceManager._API_VERSION,
                "kind": "CatalogSource",
                "metadata": {
                    "name": "opencontent-elasticsearch-dev-catalog",
                    "namespace": "openshift-marketplace",
                },
                "spec": {
                    "displayName": "IBM Opencontent Elasticsearch Catalog",
                    "image": "icr.io/cpopen/opencontent-elasticsearch-operator-catalog@sha256:bc284b8c2754af2eba81bb1edf6daa59dc823bf7a81fe91710c603f563a9a724",  # noqa: E501
                    "publisher": "CloudpakOpen",
                    "sourceType": "grpc",
                    "updateStrategy": {
                        "registryPoll": {
                            "interval": "45m",
                        }
                    },
                },
            },
        ]

        self._catalog_sources_foundational_services: CatalogSourceList = [
            {
                "apiVersion": CatalogSourceManager._API_VERSION,
                "kind": "CatalogSource",
                "metadata": {
                    "name": "ibm-operator-catalog",
                    "namespace": "openshift-marketplace",
                },
                "spec": {
                    "displayName": "IBM Operator Catalog",
                    "image": "icr.io/cpopen/ibm-operator-catalog:latest",
                    "publisher": "IBM",
                    "sourceType": "grpc",
                    "updateStrategy": {
                        "registryPoll": {
                            "interval": "45m",
                        },
                    },
                },
            },
        ]

    def get_catalog_sources(self) -> CatalogSourceList:
        """Returns OpenShift catalog sources for IBM Cloud Pak for Data services

        Returns
        -------
        CatalogSourceList
            list of OpenShift catalog sources
        """

        return self._catalog_sources

    def get_catalog_sources_for_foundational_services(self) -> CatalogSourceList:
        """Returns OpenShift catalog sources for IBM Cloud Pak for Data
        foundational services

        Returns
        -------
        CatalogSourceList
            list of OpenShift catalog sources
        """

        return self._catalog_sources_foundational_services

    def get_catalog_source_names(self) -> List[str]:
        """Returns OpenShift catalog source names for IBM Cloud Pak for Data
        services

        Returns
        -------
        List[str]
            list of OpenShift catalog sources names
        """

        return reduce(
            lambda result, catalog_source: result + [catalog_source["metadata"]["name"]],
            self._catalog_sources,
            [],
        )

    def get_catalog_source_names_for_foundational_services(self) -> List[str]:
        """Returns OpenShift catalog source names for IBM Cloud Pak for Data
        foundational services

        Returns
        -------
        List[str]
            list of OpenShift catalog sources names
        """

        return reduce(
            lambda result, catalog_source: result + [catalog_source["metadata"]["name"]],
            self._catalog_sources_foundational_services,
            [],
        )

    _API_VERSION: Final[str] = "operators.coreos.com/v1alpha1"
