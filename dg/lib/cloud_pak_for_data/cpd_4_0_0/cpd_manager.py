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

import base64
import json
import logging
import re as regex

from typing import (
    Any,
    Callable,
    Dict,
    Final,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)

import urllib3

from halo import Halo
from kubernetes import client, watch

import dg.dg
import dg.lib.jmespath
import dg.utils.logging

from dg.lib.cloud_pak_for_data.cpd_4_0_0.catalog_source_manager import (
    CatalogSourceManager,
)
from dg.lib.cloud_pak_for_data.cpd_4_0_0.cpd_service_manager import (
    CloudPakForDataServiceManager,
)
from dg.lib.cloud_pak_for_data.cpd_4_0_0.types.api_version import APIVersion
from dg.lib.cloud_pak_for_data.cpd_4_0_0.types.cloud_pak_for_data_access_data import (
    CloudPakForDataAccessData,
)
from dg.lib.cloud_pak_for_data.cpd_4_0_0.types.cloud_pak_for_data_service_license import (
    CloudPakForDataLicense,
    CloudPakForDataServiceLicense,
)
from dg.lib.cloud_pak_for_data.cpd_4_0_0.types.cloud_pak_for_data_storage_vendor import (
    CloudPakForDataStorageVendor,
)
from dg.lib.cloud_pak_for_data.cpd_4_0_0.types.custom_resource_metadata import (
    CustomResourceMetadata,
)
from dg.lib.cloud_pak_for_data.cpd_4_0_0.types.kind import Kind
from dg.lib.error import (
    DataGateCLIException,
    JmespathPathExpressionNotFoundException,
)
from dg.lib.openshift.credentials.credentials import AbstractCredentials
from dg.lib.openshift.openshift_api_manager import OpenShiftAPIManager
from dg.lib.openshift.types.catalog_source import CatalogSourceList
from dg.lib.openshift.types.custom_resource import CustomResource
from dg.lib.openshift.types.kind_metadata import KindMetadata

logger = logging.getLogger(__name__)


class CloudPakForDataManager:
    """IBM Cloud Pak for Data 4.0.x management class"""

    def __init__(self, credentials: AbstractCredentials):
        self._cpd_service_manager = CloudPakForDataServiceManager()
        self._custom_resource_definition_names: List[str] = [
            "certmanagers.operator.ibm.com",
            "ibmcpds.cpd.ibm.com",
            "zenservices.zen.cpd.ibm.com",
        ]

        self._custom_resource_definition_names_foundational_services: List[str] = [
            "commonservices.operator.ibm.com",
            "namespacescopes.operator.ibm.com",
            "operandbindinfos.operator.ibm.com",
            "operandconfigs.operator.ibm.com",
            "operandregistries.operator.ibm.com",
            "operandrequests.operator.ibm.com",
            "podpresets.operator.ibm.com",
            "secretshares.ibmcpcs.ibm.com",
        ]

        self._kinds: Dict[Kind, KindMetadata] = {
            Kind.CustomResourceDefinition: KindMetadata(
                "apiextensions.k8s.io",
                "CustomResourceDefinition",
                "customresourcedefinitions",
                "v1",
            ),
            Kind.Ibmcpd: KindMetadata(
                "cpd.ibm.com",
                "Ibmcpd",
                "ibmcpds",
                "v1",
            ),
            Kind.NamespaceScope: KindMetadata(
                "operator.ibm.com",
                "NamespaceScope",
                "namespacescopes",
                "v1",
            ),
            Kind.OperandConfig: KindMetadata(
                "operator.ibm.com",
                "OperandConfig",
                "operandconfigs",
                "v1alpha1",
            ),
            Kind.OperandRegistry: KindMetadata(
                "operator.ibm.com",
                "OperandRegistry",
                "operandregistries",
                "v1alpha1",
            ),
            Kind.OperandRequest: KindMetadata(
                "operator.ibm.com",
                "OperandRequest",
                "operandrequests",
                "v1alpha1",
            ),
            Kind.ZenService: KindMetadata(
                "zen.cpd.ibm.com",
                "ZenService",
                "zenservices",
                "v1",
            ),
        }

        self._openshift_manager = OpenShiftAPIManager(credentials)
        self._operator_names: List[str] = [
            "cpd-platform-operator.ibm-common-services",
            "ibm-cert-manager-operator.ibm-common-services",
            "ibm-zen-operator.ibm-common-services",
        ]

        self._operator_names_foundational_services: List[str] = [
            "ibm-common-service-operator.ibm-common-services",
            "ibm-namespace-scope-operator.ibm-common-services",
            "ibm-odlm.ibm-common-services",
        ]

    def cloud_pak_for_data_service_installed(
        self,
        cpd_instance_project: str,
        service_name: str,
    ) -> bool:
        """Returns whether the Cloud Pak for Data service with the given name is
        completely installed

        Parameters
        ----------
        cpd_instance_project
            IBM Cloud Pak for Data instance project
        service_name
            name of the service to be checked

        Returns
        -------
        bool
            true, if the Cloud Pak for Data service with the given name is
            completely installed
        """

        if not self._cpd_service_manager.is_cloud_pak_for_data_service(service_name):
            raise DataGateCLIException("Unknown IBM Cloud Pak for Data service")

        custom_resource_metadata = self._cpd_service_manager.get_custom_resource_metadata(service_name)
        custom_resource = self._openshift_manager.get_custom_resource_if_exists(
            cpd_instance_project, custom_resource_metadata.name, custom_resource_metadata.get_kind_metadata()
        )

        return (
            self.custom_resource_status_completed(custom_resource, custom_resource_metadata)
            if custom_resource is not None
            else False
        )

    def custom_resource_status_completed(
        self, custom_resource: CustomResource, custom_resource_metadata: CustomResourceMetadata
    ) -> bool:
        result = False

        try:
            status = dg.lib.jmespath.get_jmespath_string(
                f"status.{custom_resource_metadata.status_key_name}", custom_resource
            )

            result = status == "Completed"
        except JmespathPathExpressionNotFoundException:
            pass

        return result

    def get_license_types_for_cloud_pak_for_data_service(
        self, service_name: str
    ) -> List[CloudPakForDataServiceLicense]:
        """Returns available license types for the given IBM Cloud Pak for Data
        service

        Parameters
        ----------
        service_name
            name of the IBM Cloud Pak for Data service for which available license
            types shall be returned

        Returns
        -------
        List[CloudPakForDataServiceLicense]
            available license types for the given IBM Cloud Pak for Data service
        """

        if not self._cpd_service_manager.is_cloud_pak_for_data_service(service_name):
            raise DataGateCLIException("Unknown IBM Cloud Pak for Data service")

        custom_resource_metadata = self._cpd_service_manager.get_custom_resource_metadata(service_name)

        return custom_resource_metadata.licenses

    def install_cloud_pak_for_data(
        self,
        cpd_operators_project: str,
        cpd_instance_project: str,
        ibm_cloud_pak_for_data_entitlement_key: str,
        license: CloudPakForDataLicense,
        storage_class: str,
    ) -> CloudPakForDataAccessData:
        """Installs IBM Cloud Pak for Data

        Parameters
        ----------
        cpd_operators_project
            IBM Cloud Pak for Data operators project
        cpd_instance_project
            IBM Cloud Pak for Data instance project
        ibm_cloud_pak_for_data_entitlement_key
            IBM Cloud Pak for Data entitlement key
        license
            IBM Cloud Pak for Data license
        storage_class
            storage class used for installation

        Returns
        -------
        CloudPakForDataAccessData
            IBM Cloud Pak for Data access data
        """

        if self._openshift_manager.namespaced_custom_resource_exists(
            cpd_instance_project, "ibmcpd-cr", self._kinds[Kind.Ibmcpd]
        ):
            raise DataGateCLIException(
                f"IBM Cloud Pak for Data is already installed in project '{cpd_instance_project}'"
            )

        self.install_cloud_pak_for_data_foundational_services(ibm_cloud_pak_for_data_entitlement_key)

        cloud_pak_for_data_access_data = self._install_cloud_pak_for_data(
            cpd_operators_project, cpd_instance_project, license, storage_class
        )

        return cloud_pak_for_data_access_data

    def install_cloud_pak_for_data_foundational_services(self, ibm_cloud_pak_for_data_entitlement_key: str):
        """Installs IBM Cloud Pak for Data foundational services

        Parameters
        ----------
        ibm_cloud_pak_for_data_entitlement_key
            IBM Cloud Pak for Data entitlement key

        Notes
        -----
        https://www.ibm.com/docs/en/cloud-paks/cp-data/4.0?topic=installing-pre-installation-tasks
        """

        logger.info("Installing IBM Cloud Pak for Data foundational services")
        self._create_project(CloudPakForDataManager._FOUNDATIONAL_SERVICES_PROJECT)
        self._create_operator_group(CloudPakForDataManager._FOUNDATIONAL_SERVICES_PROJECT)
        self._configure_global_pull_secret(ibm_cloud_pak_for_data_entitlement_key)
        self._create_catalog_sources(CatalogSourceManager().get_catalog_sources_for_foundational_services())
        self._create_cloud_pak_foundational_services_operator_subscription(
            CloudPakForDataManager._FOUNDATIONAL_SERVICES_PROJECT
        )

    def install_cloud_pak_for_data_service(
        self,
        cpd_operators_project: str,
        cpd_instance_project: str,
        service_name: str,
        license: CloudPakForDataServiceLicense,
        installation_options: List[Tuple[str, Union[bool, int, str]]],
        storage_option: Optional[Union[str, CloudPakForDataStorageVendor]],
    ):
        """Installs an IBM Cloud Pak for Data service

        Parameters
        ----------
        cpd_operators_project
            IBM Cloud Pak for Data operators project
        cpd_instance_project
            IBM Cloud Pak for Data instance project
        service_name
            name of the service to be installed
        license
            license to be used when creating the custom resource
        installation_options
            additional installation options
        storage_option
            storage class/vendor to be used when creating the custom resource
        """

        if not self._cpd_service_manager.is_cloud_pak_for_data_service(service_name):
            raise DataGateCLIException("Unknown IBM Cloud Pak for Data service")

        custom_resource_metadata = self._cpd_service_manager.get_custom_resource_metadata(service_name)
        custom_resource = self._openshift_manager.get_custom_resource_if_exists(
            cpd_instance_project, custom_resource_metadata.name, custom_resource_metadata.get_kind_metadata()
        )

        kind = custom_resource_metadata.kind

        if custom_resource is not None:
            if self.custom_resource_status_completed(custom_resource, custom_resource_metadata):
                raise DataGateCLIException("IBM Cloud Pak for Data service already installed")
        else:
            custom_resource_metadata.check_options(license, storage_option)
            self._create_operator_subscription(cpd_operators_project, custom_resource_metadata.operator_name)

            custom_resource = custom_resource_metadata.get_custom_resource(
                cpd_instance_project, license, installation_options, storage_option
            )

            with Halo(
                text=f"Waiting for custom resource definition '{kind}' to be created",
                spinner="dots",
            ) as spinner, dg.utils.logging.ScopedSpinnerDisabler(dg.dg.click_logging_handler, spinner):
                self._openshift_manager.execute_kubernetes_client(
                    self._wait_for_custom_resource,
                    encountered_crd_kinds=set(),
                    expected_crd_kinds={kind},
                    kind_metadata=self._kinds[Kind.CustomResourceDefinition],
                    spinner=spinner,
                    success_function=self._custom_resource_definitions_are_created,
                )

            self._openshift_manager.execute_kubernetes_client(
                self._create_custom_resource, custom_resource=custom_resource, project=cpd_instance_project
            )

        with Halo(
            text=f"Waiting for custom resource {kind} '{custom_resource_metadata.name}' to be created",
            spinner="dots",
        ) as spinner, dg.utils.logging.ScopedSpinnerDisabler(dg.dg.click_logging_handler, spinner):
            self._openshift_manager.execute_kubernetes_client(
                self._wait_for_namespaced_custom_resource,
                kind_metadata=custom_resource_metadata.get_kind_metadata(),
                name=custom_resource["metadata"]["name"],
                project=cpd_instance_project,
                spinner=spinner,
                status_key=custom_resource_metadata.status_key_name,
                success_function=self._custom_resource_status_is_completed,
            )

    def uninstall_cloud_pak_for_data(self, cpd_operators_project: str, cpd_instance_project: str, delete_project: bool):
        """Uninstalls IBM Cloud Pak for Data

        Parameters
        ----------
        cpd_operators_project
            IBM Cloud Pak for Data operators project
        cpd_instance_project
            IBM Cloud Pak for Data instance project
        delete_project
            flag indicating whether the operators and instance projects shall be
            deleted
        """

        self._openshift_manager.execute_kubernetes_client(
            self._delete_custom_resource, kind=Kind.Ibmcpd, name="ibmcpd-cr", project=cpd_instance_project
        )

        self._openshift_manager.execute_kubernetes_client(
            self._delete_custom_resource, kind=Kind.OperandRequest, name="empty-request", project=cpd_instance_project
        )

        ibmcpd_instances = self._openshift_manager.execute_kubernetes_client(
            self._get_custom_resources, kind=Kind.Ibmcpd
        )

        if len(ibmcpd_instances) == 0:
            self._uninstall_cloud_pak_for_data_service_operators(cpd_operators_project)

            operand_request_names = self._openshift_manager.execute_kubernetes_client(
                self._get_namespaced_custom_resource_names,
                kind=Kind.OperandRequest,
                project=CloudPakForDataManager._FOUNDATIONAL_SERVICES_PROJECT,
            )

            for operand_request_name in operand_request_names:
                if (operand_request_name == "cert-manager") or (operand_request_name == "zen-service"):
                    self._openshift_manager.execute_kubernetes_client(
                        self._delete_custom_resource,
                        kind=Kind.OperandRequest,
                        name=operand_request_name,
                        project=CloudPakForDataManager._FOUNDATIONAL_SERVICES_PROJECT,
                    )

            self.uninstall_operator(cpd_operators_project, "cpd-platform-operator")

            for custom_resource_definition_name in self._custom_resource_definition_names:
                logger.info(f"Deleting custom resource definition {custom_resource_definition_name}")
                self._openshift_manager.delete_custom_resource_definition(custom_resource_definition_name)

            for operator_name in self._operator_names:
                logger.info(f"Deleting operator '{operator_name}'")
                self._openshift_manager.delete_operator(operator_name)

            # TODO analyze why the following Operator resources cannot be deleted at this point in time although there
            #      are no corresponding subscription, cluster service versions, and custom resource definitions (note:
            #      in OpenShift 4.7, this problem is not the root cause: https://access.redhat.com/solutions/5805841):
            #
            #      - cpd-platform-operator.ibm-common-services
            #      - ibm-cert-manager-operator.ibm-common-services
            #      - ibm-zen-operator.ibm-common-services

            self._delete_catalog_sources(CatalogSourceManager().get_catalog_source_names())

            if delete_project:
                logger.info(f"Deleting project '{cpd_instance_project}'")
                self._openshift_manager.delete_project(cpd_instance_project)

    def uninstall_cloud_pak_for_data_foundational_services(self, delete_project: bool):
        """Uninstalls IBM Cloud Pak foundational services

        Parameters
        ----------
        delete_project
            flag indicating whether the foundational services project shall be
            deleted

        Notes
        -----
        https://www.ibm.com/docs/en/cloud-paks/1.0?topic=online-uninstalling-foundational-services
        """

        project = CloudPakForDataManager._FOUNDATIONAL_SERVICES_PROJECT

        self.uninstall_operator(project, "ibm-common-service-operator")

        operand_request_names = self._openshift_manager.execute_kubernetes_client(
            self._get_namespaced_custom_resource_names, kind=Kind.OperandRequest, project=project
        )

        for operand_request_name in operand_request_names:
            self._openshift_manager.execute_kubernetes_client(
                self._delete_custom_resource, kind=Kind.OperandRequest, name=operand_request_name, project=project
            )

        operand_config_names = self._openshift_manager.execute_kubernetes_client(
            self._get_namespaced_custom_resource_names, kind=Kind.OperandConfig, project=project
        )

        for operand_config_name in operand_config_names:
            self._openshift_manager.execute_kubernetes_client(
                self._delete_custom_resource, kind=Kind.OperandConfig, name=operand_config_name, project=project
            )

        operand_registry_names = self._openshift_manager.execute_kubernetes_client(
            self._get_namespaced_custom_resource_names, kind=Kind.OperandRegistry, project=project
        )

        for operand_registry_name in operand_registry_names:
            self._openshift_manager.execute_kubernetes_client(
                self._delete_custom_resource, kind=Kind.OperandRegistry, name=operand_registry_name, project=project
            )

        namespace_scope_names = self._openshift_manager.execute_kubernetes_client(
            self._get_namespaced_custom_resource_names, kind=Kind.NamespaceScope, project=project
        )

        for namespace_scope_name in namespace_scope_names:
            self._openshift_manager.execute_kubernetes_client(
                self._delete_custom_resource, kind=Kind.NamespaceScope, name=namespace_scope_name, project=project
            )

        self._uninstall_operator(self._FOUNDATIONAL_SERVICES_PROJECT, "ibm-namespace-scope-operator")
        self._uninstall_operator(self._FOUNDATIONAL_SERVICES_PROJECT, "operand-deployment-lifecycle-manager-app")

        for custom_resource_definition_name in self._custom_resource_definition_names_foundational_services:
            logger.info(f"Deleting custom resource definition {custom_resource_definition_name}")
            self._openshift_manager.delete_custom_resource_definition(custom_resource_definition_name)

        for operator_name in self._operator_names_foundational_services:
            logger.info(f"Deleting operator '{operator_name}'")
            self._openshift_manager.delete_operator(operator_name)

        # TODO analyze why the following Operator resources cannot be deleted at this point in time although there
        #      are no corresponding subscription, cluster service versions, and custom resource definitions (note:
        #      in OpenShift 4.7, this problem is not the root cause: https://access.redhat.com/solutions/5805841):
        #
        #      - ibm-cert-manager-operator.ibm-common-services

        self._delete_catalog_sources(CatalogSourceManager().get_catalog_source_names_for_foundational_services())

        if delete_project:
            logger.info(f"Deleting project '{project}'")
            self._openshift_manager.delete_project(project)

    def uninstall_operator(self, project: str, operator_name: str):
        """Uninstalls the operator subscription and the associated cluster
        service version of the operator with the given name

        This method does not delete the operator itself as all custom resource
        definitions created by the operator must be deleted beforehand.

        Parameters
        ----------
        project
            project containing the operator subscription and the associated cluster
            service version
        operator_name
            name of the operator whose operator subscription and associated cluster
            service version shall be deleted
        """

        subscription_metadata = self._cpd_service_manager.get_subscription_metadata(operator_name)

        self._uninstall_operator(project, subscription_metadata.name)

    def uninstall_service_operator(self, project: str, service_name: str):
        """Uninstalls the operator subscription and the associated cluster
        service version of the operator associated with the service with the
        given name

        This method does not delete the operator itself as all custom resource
        definitions created by the operator must be deleted beforehand.

        Parameters
        ----------
        project
            project containing the operator subscription and the associated cluster
            service version
        service_name
            name of the service associated with the operator whose operator
            subscription and associated cluster service version shall be deleted
        """

        custom_resource = self._cpd_service_manager.get_custom_resource_metadata(service_name)

        self.uninstall_operator(project, custom_resource.operator_name)

    def _configure_global_pull_secret(self, ibm_cloud_pak_for_data_entitlement_key: str):
        """Configures the global pull secret to ensure that a cluster has the
        necessary credentials to pull images

        Parameters
        ----------
        ibm_cloud_pak_for_data_entitlement_key
            IBM Cloud Pak for Data entitlement key

        Notes
        -----
        https://www.ibm.com/docs/en/cloud-paks/cp-data/4.0?topic=tasks-configuring-your-cluster-pull-images#preinstall-cluster-setup__pull-secret
        """

        global_pull_secret_data = self._openshift_manager.get_global_pull_secret_data()
        registry_location = "cp.icr.io"
        credentials = global_pull_secret_data.get_credentials(registry_location)

        if credentials is None or (credentials.password != ibm_cloud_pak_for_data_entitlement_key):
            logging.info("Configuring global pull secret")
            global_pull_secret_data.set_credentials(registry_location, "cp", ibm_cloud_pak_for_data_entitlement_key)
            self._openshift_manager.patch_credentials(global_pull_secret_data)
        else:
            logging.info("Skipping configuration of global pull secret")

    def _create_catalog_sources(self, catalog_sources: CatalogSourceList):
        """Creates the IBM Cloud Pak for Data catalog sources

        Parameters
        ----------
        catalog_sources
            catalog sources to be created

        Notes
        -----
        https://www.ibm.com/docs/en/cloud-paks/cp-data/4.0?topic=tasks-configuring-your-cluster-pull-images#preinstall-cluster-setup__catalog-source
        """

        existing_catalog_source_names = self._get_catalog_source_names()

        for catalog_source in catalog_sources:
            catalog_source_name = catalog_source["metadata"]["name"]

            if catalog_source_name not in existing_catalog_source_names:
                logging.info(f"Creating catalog source '{catalog_source_name}'")
                self._openshift_manager.create_catalog_source("openshift-marketplace", catalog_source)
            else:
                logging.info(f"Skipping creation of catalog source '{catalog_source_name}'")

    def _create_cloud_pak_for_data_custom_resource(
        self, cpd_instance_project: str, license: CloudPakForDataLicense, storage_class: str
    ):
        """Creates an Ibmcpd custom resource to install IBM Cloud Pak for Data

        Creating an Ibmcpd custom resource (ibmcpd-cr) creates a ZenService
        custom resource (lite-cr), which is the control plane.

        Creating an Ibmcpd custom resource creates the following operator
        subscriptions/operators:

        - IBM Cert Manager:
            - Operator subscription: ibm-cert-manager-operator
            - Operator: ibm-cert-manager-operator.ibm-common-services

        - IBM Zen Service:
            - Operator subscription: ibm-zen-operator
            - Operator: ibm-zen-operator.ibm-common-services

        Parameters
        ----------
        cpd_instance_project
            IBM Cloud Pak for Data instance project
        license
            IBM Cloud Pak for Data license
        storage_class
            storage class used for installation
        """

        self._wait_for_cloud_pak_for_data_custom_resource_definitions()

        if not self._openshift_manager.namespaced_custom_resource_exists(
            cpd_instance_project, "empty-request", self._kinds[Kind.OperandRequest]
        ):
            operand_request: CustomResource = {
                "apiVersion": "operator.ibm.com/v1alpha1",
                "kind": "OperandRequest",
                "metadata": {
                    "name": "empty-request",
                    "namespace": cpd_instance_project,
                },
                "spec": {
                    "requests": [],
                },
            }

            self._openshift_manager.execute_kubernetes_client(
                self._create_custom_resource,
                custom_resource=operand_request,
                project=cpd_instance_project,
            )

        ibmcpd: CustomResource = {
            "apiVersion": "cpd.ibm.com/v1",
            "kind": "Ibmcpd",
            "metadata": {
                "name": "ibmcpd-cr",
                "namespace": cpd_instance_project,
            },
            "spec": {
                "license": {
                    "accept": True,
                    "license": license.name,
                },
                "storageClass": storage_class,
                "zenCoreMetadbStorageClass": storage_class,
                "version": "4.0.1",
            },
        }

        self._openshift_manager.execute_kubernetes_client(
            self._create_custom_resource,
            custom_resource=ibmcpd,
            project=cpd_instance_project,
        )

    def _create_cloud_pak_for_data_operator_subscription(self, cpd_operators_project: str):
        """Creates the 'Cloud Pak for Data Operator' operator subscription

        The 'Cloud Pak for Data Operator' operator subscription (cpd-operator)
        installs the following operator:

        - Cloud Pak for Data Operator
          (cpd-platform-operator.ibm-common-services)

        Parameters
        ----------
        cpd_operators_project
            IBM Cloud Pak for Data operators project
        """

        self._create_operator_subscription_if_not_exists(cpd_operators_project, "cpd-platform-operator")

    def _create_cloud_pak_foundational_services_operator_subscription(self, project: str):
        """Creates the 'IBM Cloud Pak foundational services' operator
        subscription

        The 'IBM Cloud Pak foundational services' operator subscription
        (ibm-common-service-operator) installs the following operator:

        - IBM Cloud Pak foundational services
          (ibm-common-service-operator.ibm-common-services)

        The 'IBM Cloud Pak foundational services' operator creates the following
        operator subscriptions/operators:

        - IBM NamespaceScope Operator:
            - Operator subscription: ibm-namespace-scope-operator
            - Operator: ibm-namespace-scope-operator.ibm-common-services

        - Operand Deployment Lifecycle Manager:
            - Operator subscription: operand-deployment-lifecycle-manager-app
            - Operator: ibm-odlm.ibm-common-services

        Parameters
        ----------
        project
            project in which the subscription shall be created
        """

        self._create_operator_subscription_if_not_exists(project, "ibm-common-service-operator")

    def _create_custom_resource(self, project: str, custom_resource: CustomResource):
        """Creates a custom resource

        Parameters
        ----------
        project
            project in which the custom resource shall be created
        custom_resource
            specification object for passing to the OpenShift REST API
        """

        api_version = self._extract_group_and_version_from_api_version(custom_resource["apiVersion"])
        body_str = json.dumps(custom_resource, indent="\t", sort_keys=True)
        kind: str = custom_resource["kind"]
        name: str = custom_resource["metadata"]["name"]
        plural = kind.lower() + "s"

        logger.info(f"Creating custom resource {kind} '{name}'")
        logger.debug(f"Sending JSON object:\n{body_str}")

        custom_objects_api = client.CustomObjectsApi()
        custom_objects_api.create_namespaced_custom_object(
            api_version.group,
            api_version.version,
            project,
            plural,
            custom_resource,
        )

    def _create_operator_group(self, project: str):
        """Creates an operator group for the 'ibm-common-services' namespace

        Parameters
        ----------
        project
            project in which the operator group shall be created

        Notes
        -----
        https://www.ibm.com/docs/en/cloud-paks/cp-data/4.0?topic=tasks-creating-projects-namespaces
        """

        operator_group_name = "operatorgroup"

        if not self._openshift_manager.operator_group_exists(project, operator_group_name):
            logger.info(f"Creating operator group for '{project}' project")
            self._openshift_manager.create_operator_group(project, "operatorgroup")

    def _create_operator_subscription(
        self, project: str, operator_name: str, created_dependent_subscriptions: List[str] = []
    ):
        """Creates an operator subscription

        Parameters
        ----------
        project
            project in which the operator subscription shall be created
        operator_name
            name of the operator for which a subscription shall be created
        created_dependent_subscriptions
            list of created dependent subscriptions

        Links
        -----
        https://docs.openshift.com/container-platform/latest/rest_api/operatorhub_apis/subscription-operators-coreos-com-v1alpha1.html
        """

        subscription_metadata = self._cpd_service_manager.get_subscription_metadata(operator_name)

        if len(subscription_metadata.dependencies) != 0:
            for dependent_operator_name in subscription_metadata.dependencies:
                dependent_subscription_name = self._cpd_service_manager.get_subscription_metadata(
                    dependent_operator_name
                ).name

                if dependent_subscription_name in created_dependent_subscriptions:
                    raise DataGateCLIException("Circular dependency detected")

                if self._openshift_manager.subscription_exists(project, dependent_subscription_name):
                    continue

                self._create_operator_subscription(
                    subscription_metadata.required_namespace
                    if subscription_metadata.required_namespace is not None
                    else project,
                    dependent_operator_name,
                    created_dependent_subscriptions + [dependent_subscription_name],
                )

        if not self._openshift_manager.subscription_exists(project, subscription_metadata.name):
            if len(created_dependent_subscriptions) == 0:
                logging.info(f"Creating subscription '{subscription_metadata.name}' for operator '{operator_name}'")
            else:
                logging.info(
                    f"Creating subscription '{subscription_metadata.name}' for dependent operator '{operator_name}'"
                )

            subscription = self._cpd_service_manager.get_subscription_metadata(operator_name).get_subscription(project)

            self._openshift_manager.create_subscription(project, subscription)

    def _create_operator_subscription_if_not_exists(self, project: str, operator_name: str):
        """Creates an operator subscription if it does not exist

        Parameters
        ----------
        project
            project in which the operator subscription shall be created
        operator_name
            name of the operator for which a subscription shall be created
        """

        subscription_metadata = self._cpd_service_manager.get_subscription_metadata(operator_name)

        if not self._openshift_manager.subscription_exists(project, subscription_metadata.name):
            self._create_operator_subscription(project, operator_name)
        else:
            logging.info(
                f"Skipping creation of subscription '{subscription_metadata.name}' for operator '{operator_name}'"
            )

    def _create_project(self, project: str):
        """Creates a project with the given name

        Parameters
        ----------
        project
            name of the project to be created
        """

        if not self._openshift_manager.project_exists(project):
            logging.info(f"Creating project '{project}'")
            self._openshift_manager.create_project(project)
        else:
            logging.info(f"Skipping creation of project '{project}'")

    def _custom_resource_definitions_are_created(
        self, event: Any, expected_crd_kinds: Set[str], encountered_crd_kinds: Set[str], spinner: Halo, **kwargs
    ) -> bool:
        """Callback for checking whether the given set of expected custom
        resource definitions was created

        Parameters
        ----------
        event
            OpenShift watch event
        expected_crd_kinds
            set of expected custom resource definitions
        encountered_crd_kinds
            set of encountered custom resource definitions
        spinner
            active spinner

        Returns
        -------
        bool
            true, if the given set of expected custom resource definitions was
            created
        """

        custom_resource_definitions_are_created = False

        if event["type"] == "ADDED":
            encountered_crd_kind = dg.lib.jmespath.get_jmespath_string("object.spec.names.kind", event)

            if encountered_crd_kind in expected_crd_kinds:
                spinner.stop()
                logger.info(f"Created custom resource definition '{encountered_crd_kind}'")
                encountered_crd_kinds.add(encountered_crd_kind)

            custom_resource_definitions_are_created = encountered_crd_kinds == expected_crd_kinds

            if not custom_resource_definitions_are_created:
                spinner.start()

        return custom_resource_definitions_are_created

    def _custom_resource_is_deleted(self, event: Any, kind_metadata: KindMetadata, name: str) -> bool:
        """Callback for checking whether the custom resource of the given kind
        and the given name was deleted

        Parameters
        ----------
        event
            OpenShift watch event
        kind_metadata
            kind metadata of the custom resource to be checked
        name
            name of the custom resource to be checked

        Returns
        -------
        bool
            true, if the custom resource of the given kind and the given name was
            deleted
        """

        custom_resource_is_deleted = False

        if event["type"] == "DELETED":
            resource_kind = dg.lib.jmespath.get_jmespath_string("object.spec.names.kind", event)
            resource_name = dg.lib.jmespath.get_jmespath_string("object.metadata.name", event)
            custom_resource_is_deleted = (resource_name == name) and (resource_kind == kind_metadata.kind)

        return custom_resource_is_deleted

    def _custom_resource_status_is_completed(
        self, event: Any, kind_metadata: KindMetadata, name: str, status_key: str, spinner: Halo
    ) -> bool:
        """Callback for checking whether the status of the custom resource of
        the given kind and the given name equals "Completed"

        Parameters
        ----------
        event
            OpenShift watch event
        kind_metadata
            kind metadata of the custom resource to be checked
        name
            name of the custom resource to be checked
        status_key
            name of the status key
        spinner
            active spinner

        Returns
        -------
        bool
            true, if the status of the custom resource of the given kind and the
            given name equals "Completed"
        """

        status_is_completed = False

        if event["type"] == "ADDED":
            resource_name = dg.lib.jmespath.get_jmespath_string("object.metadata.name", event)
            status_is_completed = False

            try:
                status = dg.lib.jmespath.get_jmespath_string(f"object.status.{status_key}", event)
                status_is_completed = (resource_name == name) and (status == "Completed")

                if status_is_completed:
                    spinner.stop()
                    logger.info(f"Created custom resource {kind_metadata.kind} '{name}'")
            except JmespathPathExpressionNotFoundException:
                pass

        return status_is_completed

    def _delete_catalog_sources(self, catalog_source_names: List[str]):
        """Deletes the catalog sources with the given names

        Parameters
        ----------
        catalog_source_names
            names of the catalog sources to be deleted
        """

        for catalog_source_name in catalog_source_names:
            logger.info(f"Deleting catalog source '{catalog_source_name}'")
            self._openshift_manager.delete_catalog_source("openshift-marketplace", catalog_source_name)

    def _delete_cluster_service_version(self, project: str, cluster_service_version_name: str):
        """Deletes the cluster service version with the given name

        Parameters
        ----------
        project
            project in which the cluster service version shall be deleted
        cluster_service_version_name
            name of the cluster service version to be deleted
        """

        logger.info(f"Deleting cluster service version (name: {cluster_service_version_name})")
        self._openshift_manager.delete_cluster_service_version(project, cluster_service_version_name)

    def _delete_custom_resource(self, project: str, kind: Kind, name: str):
        """Deletes the custom resource of the given kind and the given name

        Parameters
        ----------
        project
            project in which the custom resource shall be deleted
        kind
            kind of the custom resource to be deleted
        name
            name of the custom resource to be deleted
        """

        logger.info(f"Deleting {str(kind)} '{name}'")

        kind_metadata = self._kinds[kind]

        custom_objects_api = client.CustomObjectsApi()
        custom_objects_api.delete_namespaced_custom_object(
            kind_metadata.group, kind_metadata.version, project, kind_metadata.plural, name
        )

    def _delete_subscription(self, project: str, subscription_name: str):
        """Deletes the subscription with the given name

        Parameters
        ----------
        project
            project in which the subscription shall be deleted
        subscription_name
            name of the subscription to be deleted
        """

        logger.info(f"Deleting subscription (name: {subscription_name})")
        self._openshift_manager.delete_subscription(project, subscription_name)

    def _extract_group_and_version_from_api_version(self, api_version: str) -> APIVersion:
        """Extracts the group and the version from the given API version string

        Parameters
        ----------
        api_version
            API version string

        Returns
        -------
        APIVersion
            API version object
        """

        search_result = regex.match("(.+)\\/(.+)", api_version)

        assert search_result is not None

        return APIVersion(group=search_result.group(1), version=search_result.group(2))

    def _get_access_data(self) -> CloudPakForDataAccessData:
        """Returns IBM Cloud Pak for Data access data

        Returns
        -------
        CloudPakForDataAccessData
            IBM Cloud Pak for Data access data
        """

        cloud_pak_for_data_url = self._openshift_manager.execute_kubernetes_client(self._get_cloud_pak_for_data_url)
        initial_admin_password = self._openshift_manager.execute_kubernetes_client(self._get_initial_admin_password)
        cloud_pak_for_data_access_data = CloudPakForDataAccessData(
            f"https://{cloud_pak_for_data_url}", initial_admin_password
        )

        return cloud_pak_for_data_access_data

    def _get_catalog_source_names(self) -> List[str]:
        """Returns catalog source names

        Returns
        -------
        List[str]
            catalog source names
        """

        existing_catalog_sources = self._openshift_manager.get_catalog_sources("openshift-marketplace")

        return dg.lib.jmespath.get_jmespath_list_of_strings("items[*].metadata.name", existing_catalog_sources)

    def _get_cloud_pak_for_data_url(self) -> str:
        """Returns the IBM Cloud Pak for Data URL

        Returns
        -------
        str
            IBM Cloud Pak for Data URL
        """

        custom_objects_api = client.CustomObjectsApi()
        custom_objects_api_result = custom_objects_api.get_namespaced_custom_object_status(
            "zen.cpd.ibm.com", "v1", "zen", "zenservices", "lite-cr"
        )

        return dg.lib.jmespath.get_jmespath_string("status.url", custom_objects_api_result)

    def _get_custom_resources(self, kind: Kind) -> List[Any]:
        """Returns custom resources of the given kind

        Parameters
        ----------
        kind
            kind of custom resources to return

        Returns
        -------
        List[Any]
            custom resources of the given kind
        """

        kind_metadata = self._kinds[kind]

        custom_objects_api = client.CustomObjectsApi()
        custom_objects_api_result: Any = custom_objects_api.list_cluster_custom_object(
            kind_metadata.group, kind_metadata.version, kind_metadata.plural
        )

        assert "items" in custom_objects_api_result
        assert isinstance(custom_objects_api_result["items"], List)

        return custom_objects_api_result["items"]

    def _get_initial_admin_password(self) -> str:
        """Returns the initial IBM Cloud Pak for Data admin password

        Returns
        -------
        str
            initial IBM Cloud Pak for Data admin password
        """

        core_v1_api = client.CoreV1Api()
        core_v1_api_result = core_v1_api.read_namespaced_secret("admin-user-details", "zen")

        if not isinstance(core_v1_api_result, client.V1Secret):
            raise TypeError("core_v1_api_result is not an instance of client.V1Secret")

        return base64.standard_b64decode(
            dg.lib.jmespath.get_jmespath_string("initial_admin_password", core_v1_api_result.data)
        ).decode("utf-8")

    def _get_namespaced_custom_resource_names(self, project: str, kind: Kind) -> List[str]:
        """Returns names of custom resources of the given kind

        Parameters
        ----------
        project
            project to be searched
        kind
            kind of custom resources to return

        Returns
        -------
        List[str]
            names of custom resources of the given kind
        """

        kind_metadata = self._kinds[kind]

        custom_objects_api = client.CustomObjectsApi()
        custom_objects_api_result = custom_objects_api.list_namespaced_custom_object(
            kind_metadata.group, kind_metadata.version, project, kind_metadata.plural
        )

        return dg.lib.jmespath.get_jmespath_list_of_strings("items[*].metadata.name", custom_objects_api_result)

    def _handle_api_exception(self, exception: client.ApiException, spinner: Halo):
        """Handles Kubernetes Python client API exceptions

        Parameters
        ----------
        exception
            Kubernetes Python client API exception to be handled
        spinner
            active spinner
        """

        # ignore "Expired: too old resource version" error
        if exception.status != 410:
            raise exception

        self._suspend_spinner_and_log_debug_message(spinner, exception.reason)

    def _handle_protocol_error(self, exception: urllib3.exceptions.ProtocolError, spinner: Halo):
        """Handles urllib3 protocol error exceptions

        Parameters
        ----------
        exception
            urllib3 protocol error exception to be handled
        spinner
            active spinner
        """

        if (len(exception.args) < 2) or not isinstance(exception.args[1], urllib3.exceptions.InvalidChunkLength):
            spinner.fail()

            raise exception

        self._suspend_spinner_and_log_debug_message(spinner, "OpenShift API server closed connection")

    def _install_cloud_pak_for_data(
        self, cpd_operators_project: str, cpd_instance_project: str, license: CloudPakForDataLicense, storage_class: str
    ) -> CloudPakForDataAccessData:
        """Installs IBM Cloud Pak for Data

        Parameters
        ----------
        cpd_operators_project
            IBM Cloud Pak for Data operators project
        cpd_instance_project
            IBM Cloud Pak for Data instance project
        license
            IBM Cloud Pak for Data license
        storage_class
            storage class used for installation

        Notes
        -----
        https://www.ibm.com/docs/en/cloud-paks/cp-data/4.0?topic=installing-cloud-pak-data

        Returns
        -------
        CloudPakForDataAccessData
            IBM Cloud Pak for Data access data
        """

        logger.info("Installing IBM Cloud Pak for Data")
        self._create_project(cpd_instance_project)
        self._create_catalog_sources(CatalogSourceManager().get_catalog_sources())
        self._create_cloud_pak_for_data_operator_subscription(cpd_operators_project)
        self._create_cloud_pak_for_data_custom_resource(cpd_instance_project, license, storage_class)
        self._wait_for_cloud_pak_for_data_installation_completion(cpd_instance_project)

        return self._openshift_manager.execute_kubernetes_client(self._get_access_data)

    def _suspend_spinner_and_log_debug_message(self, spinner: Halo, message: str):
        """Suspends the given spinner while logging the given debug message

        If an active spinner is not suspended, concurrently logging a debug
        message garbles the output.

        Parameters
        ----------
        spinner
            active spinner
        message
            debug message to be logged
        """

        if logger.getEffectiveLevel() == logging.DEBUG:
            spinner.stop()
            logger.debug(message)
            spinner.start()

    def _uninstall_cloud_pak_for_data_service_operators(self, cpd_operators_project: str):
        """Uninstalls operator subscriptions and associated cluster service
        versions of all service operators

        Parameters
        ----------
        cpd_operators_project
            project containing operator subscriptions and associated cluster service
            versions
        """

        for (
            subscription_metadata
        ) in self._cpd_service_manager.get_subscription_metadata_dict_for_cloud_pak_for_data_services().values():
            if self._openshift_manager.subscription_exists(cpd_operators_project, subscription_metadata.name):
                self._uninstall_operator(cpd_operators_project, subscription_metadata.name)

    def _uninstall_operator(self, project: str, subscription_name: str):
        """Uninstalls the operator subscription with the given name and the
        associated cluster service version

        This method does not delete the operator itself as all custom resource
        definitions created by the operator must be deleted beforehand.

        Parameters
        ----------
        project
            project containing the operator subscription and the associated cluster
            service version
        subscription_name
            name of the operator subscription be deleted
        """

        subscription = self._openshift_manager.get_subscription(project, subscription_name)
        cluster_service_version_name = subscription["status"]["installedCSV"]

        self._delete_subscription(project, subscription_name)
        self._delete_cluster_service_version(project, cluster_service_version_name)

    def _wait_for_cloud_pak_for_data_custom_resource_definitions(self):
        """Waits for IBM Cloud Pak for Data custom resource definitions to be
        created"""

        with Halo(text="Waiting for custom resource definitions to be created", spinner="dots") as spinner:
            self._openshift_manager.execute_kubernetes_client(
                self._wait_for_custom_resource,
                encountered_crd_kinds=set(),
                expected_crd_kinds={str(Kind.Ibmcpd), str(Kind.OperandRequest)},
                kind_metadata=self._kinds[Kind.CustomResourceDefinition],
                spinner=spinner,
                success_function=self._custom_resource_definitions_are_created,
            )

    def _wait_for_cloud_pak_for_data_installation_completion(self, cpd_instance_project: str):
        """Waits for IBM Cloud Pak for Data to be installed

        Parameters
        ----------
        cpd_instance_project
            project in which IBM Cloud Pak for Data is installed
        """

        with Halo(text="Waiting for IBM Cloud Pak for Data to be installed", spinner="dots") as spinner:
            self._openshift_manager.execute_kubernetes_client(
                self._wait_for_custom_resource,
                encountered_crd_kinds=set(),
                expected_crd_kinds={str(Kind.ZenService)},
                kind_metadata=self._kinds[Kind.CustomResourceDefinition],
                spinner=spinner,
                success_function=self._custom_resource_definitions_are_created,
            )

            spinner.start()
            self._openshift_manager.execute_kubernetes_client(
                self._wait_for_namespaced_custom_resource,
                kind_metadata=self._kinds[Kind.ZenService],
                name="lite-cr",
                project=cpd_instance_project,
                spinner=spinner,
                status_key="zenStatus",
                success_function=self._custom_resource_status_is_completed,
            )

    def _wait_for_custom_resource(
        self, kind_metadata: KindMetadata, success_function: Callable[..., bool], spinner: Halo, **kwargs
    ):
        """Waits for a specific custom resource of the given kind to be created

        The passed callback is used for checking wheter a created custom resource
        of the given kind is the sought-after custom resource.

        Parameters
        ----------
        kind_metadata
            kind metadata of the custom resource
        success_function
            callback for checking OpenShift watch event
        spinner
            active spinner
        """

        custom_objects_api = client.CustomObjectsApi()
        succeeded = False

        while not succeeded:
            try:
                resource_version: Optional[str] = None
                w = watch.Watch()

                for event in w.stream(
                    custom_objects_api.list_cluster_custom_object,
                    kind_metadata.group,
                    kind_metadata.version,
                    kind_metadata.plural,
                    resource_version=resource_version,
                ):
                    resource_version = dg.lib.jmespath.get_jmespath_string("object.metadata.resourceVersion", event)
                    succeeded = success_function(event, kind_metadata=kind_metadata, spinner=spinner, **kwargs)

                    if succeeded:
                        w.stop()
            except client.ApiException as exception:
                self._handle_api_exception(exception, spinner)
                resource_version = None
            except urllib3.exceptions.ProtocolError as exception:
                self._handle_protocol_error(exception, spinner)

    def _wait_for_namespaced_custom_resource(
        self,
        project: str,
        kind_metadata: KindMetadata,
        success_function: Callable[..., bool],
        spinner: Halo,
        **kwargs,
    ):
        """Waits for a specific custom resource of the given kind to be created in
        the given project

        The passed callback is used for checking wheter a created custom resource
        of the given kind is the sought-after custom resource.

        Parameters
        ----------
        project
            project in which the custom resource is created
        kind_metadata
            kind metadata of the custom resource
        success_function
            callback for checking OpenShift watch event
        spinner
            active spinner
        """

        custom_objects_api = client.CustomObjectsApi()
        succeeded = False

        while not succeeded:
            try:
                resource_version: Optional[str] = None
                w = watch.Watch()

                for event in w.stream(
                    custom_objects_api.list_namespaced_custom_object,
                    kind_metadata.group,
                    kind_metadata.version,
                    project,
                    kind_metadata.plural,
                    resource_version=resource_version,
                ):
                    resource_version = dg.lib.jmespath.get_jmespath_string("object.metadata.resourceVersion", event)
                    succeeded = success_function(event, kind_metadata=kind_metadata, spinner=spinner, **kwargs)

                    if succeeded:
                        w.stop()
            except client.ApiException as exception:
                self._handle_api_exception(exception, spinner)
                resource_version = None
            except urllib3.exceptions.ProtocolError as exception:
                self._handle_protocol_error(exception, spinner)

    _FOUNDATIONAL_SERVICES_PROJECT: Final[str] = "ibm-common-services"
