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

from typing import TypedDict

from cpo.lib.openshift.types.object_meta import ObjectMeta


class RoleBindingRoleRef(TypedDict):
    apiGroup: str
    kind: str
    name: str


class RoleBindingSubject(TypedDict):
    kind: str
    name: str
    namespace: str


class RoleBinding(TypedDict):
    """
    Notes
    -----
    https://docs.openshift.com/container-platform/latest/rest_api/rbac_apis/clusterrolebinding-rbac-authorization-k8s-io-v1.html#clusterrolebinding-rbac-authorization-k8s-io-v1
    https://docs.openshift.com/container-platform/latest/rest_api/rbac_apis/rolebinding-rbac-authorization-k8s-io-v1.html#rolebinding-rbac-authorization-k8s-io-v1
    """

    apiVersion: str
    kind: str
    metadata: ObjectMeta
    roleRef: RoleBindingRoleRef
    subjects: list[RoleBindingSubject]
