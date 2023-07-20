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

from dataclasses import dataclass
from typing import Any, Optional

from ansible.module_utils.basic import AnsibleModule

import cpo.lib.jmespath

from cpo.lib.ansible.modules.abstract_module import AbstractModule
from cpo.lib.ansible.modules.custom_resource_event_result import CustomResourceEventResult
from cpo.lib.jmespath import JmespathPathExpressionNotFoundException
from cpo.lib.openshift.types.kind_metadata import KindMetadata


@dataclass
class CustomResourceEventData:
    custom_resource_name: str


class WaitForNamespacedCustomResourceModule(AbstractModule):
    def __init__(self):
        argument_spec = {
            "custom_resource_name": {
                "type": "str",
                "required": True,
            },
            "group": {
                "type": "str",
                "required": True,
            },
            "jmespath_expression": {
                "type": "str",
                "required": False,
            },
            "kind": {
                "type": "str",
                "required": True,
            },
            "kubeconfig": {
                "type": "dict",
                "required": True,
            },
            "plural": {
                "type": "str",
                "required": True,
            },
            "project": {
                "type": "str",
                "required": True,
            },
            "version": {
                "type": "str",
                "required": True,
            },
        }

        self._module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
        super().__init__(self._module.params["kubeconfig"])  # type: ignore

        self._custom_resource_name: str = self._module.params["custom_resource_name"]  # type: ignore
        self._jmespath_expression: Optional[str] = self._module.params["jmespath_expression"]  # type: ignore
        self._kind_metadata = KindMetadata(
            self._module.params["group"],  # type: ignore
            self._module.params["kind"],  # type: ignore
            self._module.params["plural"],  # type: ignore
            self._module.params["version"],  # type: ignore
        )

        self._project: str = self._module.params["project"]  # type: ignore

    # override
    def get_module(self) -> AnsibleModule:
        return self._module

    # override
    def run(self):
        result: Optional[dict]

        try:
            self._wait_for_namespaced_custom_resource(
                self._project,
                self._kind_metadata,
                self._log,
                self._success_callback,
                # passed to _add_event_indicates_custom_resource_definitions_are_created
                custom_resource_event_data=CustomResourceEventData(custom_resource_name=self._custom_resource_name),
            )

            result = {"changed": False}
        except Exception:
            result = {"changed": False, "failed": True}

        self._module.exit_json(**result)

    def _success_callback(
        self, event: Any, kind_metadata: KindMetadata, custom_resource_event_data: CustomResourceEventData
    ) -> Optional[CustomResourceEventResult]:
        custom_resource_event_result: Optional[CustomResourceEventResult] = None

        if (event["type"] == "ADDED") or (event["type"] == "MODIFIED"):
            resource_name = cpo.lib.jmespath.get_jmespath_string("object.metadata.name", event)

            try:
                if resource_name == custom_resource_event_data.custom_resource_name:
                    if (self._jmespath_expression is None) or cpo.lib.jmespath.get_jmespath_bool(
                        self._jmespath_expression, event
                    ):
                        custom_resource_event_result = CustomResourceEventResult(True)
            except JmespathPathExpressionNotFoundException:
                pass

        return custom_resource_event_result


def main():
    WaitForNamespacedCustomResourceModule().run()


if __name__ == "__main__":
    main()
