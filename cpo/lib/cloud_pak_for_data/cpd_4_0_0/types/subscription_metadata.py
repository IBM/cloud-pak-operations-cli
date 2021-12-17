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

from cpo.lib.openshift.types.subscription import Subscription


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

    def get_subscription(self, project: str, catalog_source: Optional[str] = None) -> Subscription:
        """Returns a specification object for passing to the OpenShift REST API
        when creating a subscription

        Parameters
        ----------
        project
            project in which the subscription shall be created
        catalog_source
            catalog to install the operator from. If None (default), use default
            catalog for the operator (usually 'ibm-operator-catalog')

        Returns
        -------
        Subscription
            subscription object
        """
        if catalog_source is not None:
            source = catalog_source
        elif self.spec.source is not None:
            source = self.spec.source
        else:
            source = 'ibm-operator-catalog'

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
                "source": source,
                "sourceNamespace": "openshift-marketplace",
            },
        }

        if len(self.labels) != 0:
            subscription["metadata"]["labels"] = self.labels

        return subscription
