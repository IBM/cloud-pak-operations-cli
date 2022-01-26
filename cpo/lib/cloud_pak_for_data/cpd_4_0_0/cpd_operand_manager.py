#  Copyright 2022 IBM Corporation
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

import json

from typing import Dict

import jsonschema

import cpo.config

from cpo.lib.cloud_pak_for_data.cpd_4_0_0.types.operand_request_metadata import (
    OperandRequestMetadata,
)
from cpo.lib.error import DataGateCLIException


class CloudPakForDataOperandManager:
    """Manages IBM Cloud Pak for Data operand requests"""

    def __init__(self):
        self._json_schema = {
            "additionalProperties": {
                "additionalProperties": False,
                "properties": {
                    "spec": {
                        "additionalProperties": False,
                        "properties": {
                            "requests": {
                                "items": {
                                    "additionalProperties": False,
                                    "properties": {
                                        "operands": {
                                            "items": {
                                                "additionalProperties": False,
                                                "properties": {
                                                    "name": {"type": "string"},
                                                },
                                                "required": [
                                                    "name",
                                                ],
                                                "type": "object",
                                            },
                                            "type": "array",
                                        },
                                        "registry": {"type": "string"},
                                    },
                                    "required": [
                                        "operands",
                                        "registry",
                                    ],
                                    "type": "object",
                                },
                                "type": "array",
                            },
                        },
                        "required": [
                            "requests",
                        ],
                        "type": "object",
                    },
                },
                "required": [
                    "spec",
                ],
                "type": "object",
            },
        }

        self._operands: Dict[str, OperandRequestMetadata] = {}

    def get_operand_request_metadata(self, operand_request_name: str) -> OperandRequestMetadata:
        """Returns operand request metadata for the given operand request name

        Parameters
        ----------
        operand request name
            name of the operand request for which operand request metadata shall be
            returned

        Returns
        -------
        OperandRequestMetadata
            operand request metadata object
        """

        self._initialize_operands_dict_if_required()

        if operand_request_name not in self._operands:
            raise DataGateCLIException("Unknown IBM Cloud Pak for Data service")

        return self._operands[operand_request_name]

    def _initialize_operands_dict_if_required(self):
        if len(self._operands) == 0:
            with open(
                cpo.config.configuration_manager.get_deps_directory_path() / "config" / "cpd-operand-requests.json"
            ) as cpd_operand_requests_file:
                cpd_operand_requests_file_contents = json.load(cpd_operand_requests_file)

                jsonschema.Draft7Validator(self._json_schema).validate(cpd_operand_requests_file_contents)

                for key, value in cpd_operand_requests_file_contents.items():
                    self._operands[key] = value


cloud_pak_for_data_operand_manager = CloudPakForDataOperandManager()
