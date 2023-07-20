#  Copyright 2021, 2023 IBM Corporation
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

from cpo.lib.openshift.credentials.credentials import AbstractCredentials
from cpo.lib.openshift.openshift_api_manager import OpenShiftAPIManager
from cpo.lib.openshift.types.object_meta import ObjectMeta
from cpo.lib.openshift.types.role_rule import RoleRule

logger = logging.getLogger(__name__)


class NFSSubdirExternalProvisioner:
    """Manages installing the Kubernetes NFS Subdir External Provisioner

    Notes
    -----
    https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner
    """

    def __init__(self, credentials: AbstractCredentials, project: str, nfs_server: str, nfs_path: str):
        self._nfs_path = nfs_path
        self._nfs_server = nfs_server
        self._openshift_api_manager = OpenShiftAPIManager(credentials)
        self._project = project
        self._provisioner_name = "k8s-sigs.io/nfs-subdir-external-provisioner"

    def install_nfs_subdir_external_provisioner(self):
        """Installs the Kubernetes NFS Subdir External Provisioner"""

        self._create_service_account()
        self._create_cluster_role()
        self._create_cluster_role_binding()
        self._create_role()
        self._create_role_binding()
        self._add_scc_to_user()
        self._create_deployment()
        self._create_storage_class()

    def _add_scc_to_user(self):
        """Adds the 'hostmount-anyuid' security context constraint to the
        'nfs-client-provisioner' service account

        Notes
        -----
        oc adm policy add-scc-to-user hostmount-anyuid system:serviceaccount:{PROJECT}:nfs-client-provisioner
        """

        cluster_role_name = "system:openshift:scc:hostmount-anyuid"
        cluster_role_binding_name = "system:openshift:scc:hostmount-anyuid"

        if not self._openshift_api_manager.cluster_role_exists(cluster_role_name):
            logger.info(f"Creating cluster role '{cluster_role_name}'")

            rules: list[RoleRule] = [
                {
                    "apiGroups": [
                        "security.openshift.io",
                    ],
                    "resourceNames": [
                        "hostmount-anyuid",
                    ],
                    "resources": [
                        "securitycontextconstraints",
                    ],
                    "verbs": [
                        "use",
                    ],
                }
            ]

            self._openshift_api_manager.create_system_cluster_role(cluster_role_name, rules)
        else:
            logger.info(f"Skipping creation of cluster role '{cluster_role_name}'")

        if not self._openshift_api_manager.cluster_role_binding_exists(cluster_role_binding_name):
            logger.info(f"Creating cluster role binding '{cluster_role_binding_name}'")

            subjects: list[ObjectMeta] = [
                {
                    "name": "nfs-client-provisioner",
                    "namespace": self._project,
                }
            ]

            self._openshift_api_manager.create_system_cluster_role_binding(
                cluster_role_binding_name, subjects, cluster_role_name
            )
        else:
            logger.info(f"Skipping creation of cluster role binding '{cluster_role_binding_name}'")

    def _create_cluster_role(self):
        """Creates the 'nfs-client-provisioner-runner' cluster role"""

        cluster_role_name = "nfs-client-provisioner-runner"

        if not self._openshift_api_manager.cluster_role_exists(cluster_role_name):
            logger.info(f"Creating cluster role '{cluster_role_name}'")

            rules: list[RoleRule] = [
                {
                    "apiGroups": [""],
                    "resources": ["events"],
                    "verbs": [
                        "create",
                        "patch",
                        "update",
                    ],
                },
                {
                    "apiGroups": [""],
                    "resources": ["nodes"],
                    "verbs": [
                        "get",
                        "list",
                        "watch",
                    ],
                },
                {
                    "apiGroups": [""],
                    "resources": ["persistentvolumeclaims"],
                    "verbs": [
                        "get",
                        "list",
                        "update",
                        "watch",
                    ],
                },
                {
                    "apiGroups": [""],
                    "resources": ["persistentvolumes"],
                    "verbs": [
                        "create",
                        "delete",
                        "get",
                        "list",
                        "watch",
                    ],
                },
                {
                    "apiGroups": ["storage.k8s.io"],
                    "resources": ["storageclasses"],
                    "verbs": [
                        "get",
                        "list",
                        "watch",
                    ],
                },
            ]

            self._openshift_api_manager.create_cluster_role(cluster_role_name, rules)
        else:
            logger.info(f"Skipping creation of cluster role '{cluster_role_name}'")

    def _create_cluster_role_binding(self):
        """Creates the 'run-nfs-client-provisioner' cluster role binding

        This cluster role binding grants the permissions defined in the
        'nfs-client-provisioner-runner' cluster role to the
        'nfs-client-provisioner' service account.
        """

        cluster_role_binding_name = "run-nfs-client-provisioner"

        if not self._openshift_api_manager.cluster_role_binding_exists(cluster_role_binding_name):
            logger.info(f"Creating cluster role binding '{cluster_role_binding_name}'")

            subjects: list[ObjectMeta] = [
                {
                    "name": "nfs-client-provisioner",
                    "namespace": self._project,
                }
            ]

            self._openshift_api_manager.create_cluster_role_binding(
                cluster_role_binding_name, subjects, "nfs-client-provisioner-runner"
            )
        else:
            logger.info(f"Skipping creation of cluster role binding '{cluster_role_binding_name}'")

    def _create_deployment(self):
        """Creates the 'nfs-client-provisioner' deployment

        This deployment creates a pod named 'nfs-client-provisioner' in the
        project specified in the constructor runnning a container with the same
        name based on the
        'k8s.gcr.io/sig-storage/nfs-subdir-external-provisioner' image.
        """

        deployment_name = "nfs-client-provisioner"

        if not self._openshift_api_manager.deployment_exists(self._project, deployment_name):
            logger.info(f"Creating deployment '{deployment_name}'")

            deployment = {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": deployment_name,
                },
                "spec": {
                    "replicas": 1,
                    "selector": {
                        "matchLabels": {
                            "app": "nfs-client-provisioner",
                        }
                    },
                    "strategy": {
                        "type": "Recreate",
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": "nfs-client-provisioner",
                            }
                        },
                        "spec": {
                            "containers": [
                                {
                                    "env": [
                                        {
                                            "name": "NFS_PATH",
                                            "value": self._nfs_path,
                                        },
                                        {
                                            "name": "NFS_SERVER",
                                            "value": self._nfs_server,
                                        },
                                        {
                                            "name": "PROVISIONER_NAME",
                                            "value": self._provisioner_name,
                                        },
                                    ],
                                    "image": "k8s.gcr.io/sig-storage/nfs-subdir-external-provisioner:v4.0.2",
                                    "name": "nfs-client-provisioner",
                                    "volumeMounts": [
                                        {
                                            "mountPath": "/persistentvolumes",
                                            "name": "nfs-client-root",
                                        }
                                    ],
                                }
                            ],
                            "serviceAccountName": "nfs-client-provisioner",
                            "volumes": [
                                {
                                    "name": "nfs-client-root",
                                    "nfs": {
                                        "path": self._nfs_path,
                                        "server": self._nfs_server,
                                    },
                                }
                            ],
                        },
                    },
                },
            }

            self._openshift_api_manager.create_deployment(self._project, deployment)
        else:
            logger.info(f"Skipping creation of deployment '{deployment_name}'")

    def _create_role(self):
        """Creates the 'leader-locking-nfs-client-provisioner' role in the
        project specified in the constructor"""

        role_name = "leader-locking-nfs-client-provisioner"

        if not self._openshift_api_manager.role_exists(self._project, role_name):
            logger.info(f"Creating role '{role_name}'")

            rules: list[RoleRule] = [
                {
                    "apiGroups": [""],
                    "resources": ["endpoints"],
                    "verbs": [
                        "create",
                        "get",
                        "list",
                        "patch",
                        "update",
                        "watch",
                    ],
                }
            ]

            self._openshift_api_manager.create_role(self._project, role_name, rules)
        else:
            logger.info(f"Skipping creation of role '{role_name}'")

    def _create_role_binding(self):
        """Creates the 'leader-locking-nfs-client-provisioner' role binding in
        the project specified in the constructor

        This role binding grants the permissions defined in the
        'leader-locking-nfs-client-provisioner' role to the
        'nfs-client-provisioner' service account.
        """

        role_binding_name = "leader-locking-nfs-client-provisioner"

        if not self._openshift_api_manager.role_binding_exists(self._project, role_binding_name):
            logger.info(f"Creating role binding '{role_binding_name}'")

            subjects: list[ObjectMeta] = [
                {
                    "name": "nfs-client-provisioner",
                    "namespace": self._project,
                }
            ]

            self._openshift_api_manager.create_role_binding(
                self._project, role_binding_name, subjects, "leader-locking-nfs-client-provisioner"
            )
        else:
            logger.info(f"Skipping creation of cluster role binding '{role_binding_name}'")

    def _create_service_account(self):
        """Creates the 'nfs-client-provisioner' service account in the project
        specified in the constructor"""

        service_account_name = "nfs-client-provisioner"

        if not self._openshift_api_manager.service_account_exists(self._project, service_account_name):
            logger.info("Creating service account")
            self._openshift_api_manager.create_service_account(self._project, service_account_name)
        else:
            logger.info("Skipping creation of service account")

    def _create_storage_class(self):
        """Creates the 'managed-nfs-storage' storage class"""

        storage_class_name = "managed-nfs-storage"

        if not self._openshift_api_manager.storage_class_exists(storage_class_name):
            logger.info(f"Creating storage class '{storage_class_name}'")

            parameters = {
                "archiveOnDelete": "false",
            }

            self._openshift_api_manager.create_storage_class(storage_class_name, self._provisioner_name, parameters)
        else:
            logger.info(f"Skipping creation of storage class '{storage_class_name}'")
