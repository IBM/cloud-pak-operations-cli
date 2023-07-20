#  Copyright 2022, 2023 IBM Corporation
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

from dataclasses import dataclass, field
from typing import Any, Optional

from ansible.module_utils.basic import AnsibleModule

import cpo.lib.jmespath

from cpo.lib.ansible.modules.abstract_module import AbstractModule
from cpo.lib.openshift.types.kind_metadata import KindMetadata


@dataclass
class CustomResourceDefinitionsEventData:
    expected_crd_kinds: set[str]
    encountered_crd_kinds: set[str] = field(default_factory=set)


class WaitForCustomResourceDefinitionsModule(AbstractModule):
    def __init__(self):
        argument_spec = {
            "custom_resource_definitions": {
                "type": "list",
                "required": True,
            },
            "kubeconfig": {
                "type": "dict",
                "required": True,
            },
        }

        self._module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

        super().__init__(self._module.params["kubeconfig"])  # type: ignore

        self._custom_resource_definitions: list[str] = self._module.params[
            "custom_resource_definitions"
        ]  # type: ignore

    # override
    def get_module(self) -> AnsibleModule:
        return self._module

    # override
    def run(self):
        result: Optional[dict]

        try:
            self._wait_for_custom_resource(
                KindMetadata(
                    "apiextensions.k8s.io",
                    "CustomResourceDefinition",
                    "customresourcedefinitions",
                    "v1",
                ),
                self._log,
                self._add_event_indicates_custom_resource_definitions_are_created,
                # passed to _add_event_indicates_custom_resource_definitions_are_created
                custom_resource_definitions_event_data=CustomResourceDefinitionsEventData(
                    set(self._custom_resource_definitions)
                ),
            )

            result = {"changed": False}
        except Exception:
            result = {"changed": False, "failed": True}

        self._module.exit_json(**result)

    def _add_event_indicates_custom_resource_definitions_are_created(
        self, event: Any, custom_resource_definitions_event_data: CustomResourceDefinitionsEventData
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
            encountered_crd_kind = cpo.lib.jmespath.get_jmespath_string("object.spec.names.kind", event)

            if encountered_crd_kind in custom_resource_definitions_event_data.expected_crd_kinds:
                self._log(logging.DEBUG, f"Detected creation of custom resource definition '{encountered_crd_kind}'")
                custom_resource_definitions_event_data.encountered_crd_kinds.add(encountered_crd_kind)

            custom_resource_definitions_are_created = (
                custom_resource_definitions_event_data.encountered_crd_kinds
                == custom_resource_definitions_event_data.expected_crd_kinds
            )

        return custom_resource_definitions_are_created


def main():
    WaitForCustomResourceDefinitionsModule().run()


if __name__ == "__main__":
    main()
