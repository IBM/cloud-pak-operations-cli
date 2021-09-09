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

from dataclasses import dataclass
from typing import Dict, List, Optional

from dg.lib.openshift.types.subscription import Subscription


@dataclass
class SubscriptionMetadataSpec:
    """Manages subscription metadata (spec)"""

    channel: str
    name: str
    source: Optional[str] = None


@dataclass
class SubscriptionMetadata:
    """Manages subscription metadata"""

    dependencies: List[str]
    labels: Dict[str, str]
    name: str
    required_namespace: Optional[str]
    service: bool
    spec: SubscriptionMetadataSpec

    def get_subscription(self, project: str) -> Subscription:
        """Returns a specification object for passing to the OpenShift REST API
        when creating a subscription

        Parameters
        ----------
        project
            project in which the subscription shall be created

        Returns
        -------
        Subscription
            subscription object
        """

        subscription: Subscription = {
            "apiVersion": "operators.coreos.com/v1alpha1",
            "kind": "Subscription",
            "metadata": {
                "name": self.name,
                "namespace": project,
            },
            "spec": {
                "channel": self.spec.channel,
                "installPlanApproval": "Automatic",
                "name": self.spec.name,
                "source": (self.spec.source if self.spec.source is not None else "ibm-operator-catalog"),
                "sourceNamespace": "openshift-marketplace",
            },
        }

        if len(self.labels) != 0:
            subscription["metadata"]["labels"] = self.labels

        return subscription
