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

from typing import Dict, List, Optional, Tuple, Union

from cpo.lib.cloud_pak_for_data.cpd_4_0_0.types.cloud_pak_for_data_service_license import (
    CloudPakForDataServiceLicense,
)
from cpo.lib.cloud_pak_for_data.cpd_4_0_0.types.cloud_pak_for_data_storage_vendor import (
    CloudPakForDataStorageVendor,
)
from cpo.lib.error import DataGateCLIException
from cpo.lib.openshift.types.custom_resource import CustomResource
from cpo.lib.openshift.types.kind_metadata import KindMetadata


class CustomResourceMetadata:
    """Manages custom resource metadata"""

    def __init__(
        self,
        description: str,
        group: str,
        kind: str,
        licenses: List[CloudPakForDataServiceLicense],
        name: str,
        operator_name: str,
        spec: Dict[str, str],
        status_key_name: str,
        storage_option_required: bool,
        version: str,
    ):
        self._description = description
        self._group = group
        self._kind = kind
        self._licenses = licenses
        self._name = name
        self._operator_name = operator_name
        self._spec = spec
        self._status_key_name = status_key_name
        self._storage_option_required = storage_option_required
        self._version = version

    def check_options(
        self, license: CloudPakForDataServiceLicense, storage_option: Optional[Union[str, CloudPakForDataStorageVendor]]
    ):
        """Checks if the given license and storage option is valid

        Parameters
        ----------
        license
            license to be checked
        storage_option
            storage class/vendor to be checked
        """

        if license not in self._licenses:
            raise DataGateCLIException(
                f"Unsupported license (supported licenses: "
                f"{', '.join(list(map(lambda license: license.name, self._licenses)))})"
            )

        if storage_option is None and self._storage_option_required:
            raise DataGateCLIException("You must set option '--storage-class' or '--storage-vendor' for this service.")

    @property
    def description(self) -> str:
        return self._description

    def get_custom_resource(
        self,
        project: str,
        license: CloudPakForDataServiceLicense,
        installation_options: List[Tuple[str, Union[bool, int, str]]],
        storage_option: Optional[Union[str, CloudPakForDataStorageVendor]],
    ) -> CustomResource:
        """Returns a specification object for passing to the OpenShift REST API
        when creating a custom resource

        Parameters
        ----------
        project
            project in which the custom resource shall be created
        license
            license to be used when creating the custom resource
        installation_options
            additional installation options
        storage_option
            storage class/vendor to be used when creating the custom resource

        Returns
        -------
        CustomResource
            custom resource object
        """

        self.check_options(license, storage_option)

        custom_resource = CustomResource(
            group=self._group,
            kind=self._kind,
            metadata={
                "name": self._name,
                "namespace": project,
            },
            spec={
                "license": {
                    "accept": True,
                    "license": license.name,
                }
            },
            version=self._version,
        )

        self._process_installation_options(custom_resource, sorted(installation_options, key=lambda pair: pair[0]))
        self._process_spec(custom_resource)
        self._process_storage_option(custom_resource, storage_option)

        return custom_resource

    def get_kind_metadata(self) -> KindMetadata:
        """Returns kind metadata

        Returns
        -------
        KindMetadata
            kind metadata
        """

        plural = self._kind.lower() + ("s" if not self._kind.lower().endswith("s") else "")

        return KindMetadata(self._group, self._kind, plural, self._version)

    @property
    def kind(self) -> str:
        return self._kind

    @property
    def licenses(self) -> List[CloudPakForDataServiceLicense]:
        return self._licenses

    @property
    def name(self) -> str:
        return self._name

    @property
    def operator_name(self) -> str:
        return self._operator_name

    @property
    def status_key_name(self) -> str:
        return self._status_key_name

    def storage_option_is_required(self) -> bool:
        return self._storage_option_required

    def _process_installation_options(
        self,
        custom_resource: CustomResource,
        installation_options: List[Tuple[str, Union[bool, int, str]]],
    ):
        """Adds the given additional installation options to the given custom
        resource object

        Additional installation options are key-value pairs added to the
        object associated with the "spec" key of the given given custom resource
        object.

        A key containing one or more dots consists of several sub keys. For each
        of these sub keys except for the last one, a hierarchical object
        structure is created whereas each sub key is used as the key of an
        object. The last sub key and the value of the corresponding key-value
        pair are added to the inner object.

        If the first sub key of a key is named "spec", it is removed.

        Parameters
        ----------
        custom resource
            custom resource to be modified
        installation_options
            additional installation options to be added

        Examples
        --------
        - Key-value pair: ("a.b.c", "value) or ("spec.a.b.c", "value)
        - Resulting custom resource object:

        {
            …
            "spec": {
                "a": {
                    "b": {
                        "c": "value"
                    }
                }
            }
        }
        """

        for path, value in installation_options:
            current_object = custom_resource.spec
            path_elements = path.split(".")

            if (len(path_elements) != 0) and (path_elements[0] == "spec"):
                path_elements.pop(0)

            for index, path_element in enumerate(path_elements):
                if index == len(path_elements) - 1:
                    current_object[path_elements[index]] = value
                else:
                    if path_element not in current_object:
                        current_object[path_element] = {}

                    current_object = current_object[path_element]

    def _process_spec(self, custom_resource: CustomResource):
        """Adds the key-value pairs passed to the "spec" argument of the
        constructor to the object associated with the "spec" key of the given
        given custom resource object.

        Parameters
        ----------
        custom_resource
            custom resource to be modified
        """

        for key, value in self._spec.items():
            custom_resource.spec[key] = value

    def _process_storage_option(
        self, custom_resource: CustomResource, storage_option: Optional[Union[str, CloudPakForDataStorageVendor]]
    ):
        """Adds the given storage option to the given custom resource object

        Parameters
        ----------
        custom_resource
            custom resource to be modified
        storage_option
            storage option to be added
        """

        if storage_option is not None:
            if isinstance(storage_option, str):
                custom_resource.spec["storageClass"] = storage_option
            else:
                custom_resource.spec["storageVendor"] = storage_option.name
