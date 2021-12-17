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

from typing import TypedDict

from cpo.lib.openshift.types.object_meta import ObjectMeta


class SubscriptionSpecRequired(TypedDict):
    name: str
    source: str
    sourceNamespace: str


class SubscriptionSpec(SubscriptionSpecRequired, total=False):
    channel: str
    installPlanApproval: str


class SubscriptionRequired(TypedDict):
    metadata: ObjectMeta
    spec: SubscriptionSpec


class Subscription(SubscriptionRequired, total=False):
    """
    Notes
    -----
    https://docs.openshift.com/container-platform/latest/rest_api/operatorhub_apis/subscription-operators-coreos-com-v1alpha1.html#subscription-operators-coreos-com-v1alpha1
    """

    apiVersion: str
    kind: str
