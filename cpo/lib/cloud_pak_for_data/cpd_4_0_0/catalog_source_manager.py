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

from cpo.lib.openshift.types.catalog_source import CatalogSourceList


class CatalogSourceManager:
    """Manages OpenShift catalog sources"""

    def __init__(self):
        self._catalog_sources: CatalogSourceList = [
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
