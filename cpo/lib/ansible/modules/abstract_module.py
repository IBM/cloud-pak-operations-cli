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

import logging

from abc import ABC, abstractmethod
from typing import Callable, Optional

import urllib3.exceptions

from ansible.module_utils.basic import AnsibleModule
from kubernetes import client, config, watch
from q import q

import cpo.lib.jmespath

from cpo.lib.ansible.modules.custom_resource_event_result import CustomResourceEventResult
from cpo.lib.openshift.types.kind_metadata import KindMetadata


class AbstractModule(ABC):
    def __init__(self, config_dict: dict):
        config.load_kube_config_from_dict(config_dict)

    @abstractmethod
    def get_module(self) -> AnsibleModule:
        pass

    @abstractmethod
    def run(self):
        pass

    def _handle_api_exception(self, exception: client.ApiException, log_callback: Callable[[int, str], None]):
        """Handles Kubernetes Python client API exceptions

        Parameters
        ----------
        exception
            Kubernetes Python client API exception to be handled
        log_callback
            callback for logging debug messages
        """

        # ignore "Expired: too old resource version" error
        if exception.status != 410:
            raise exception

        if exception.reason is not None:
            log_callback(logging.WARN, exception.reason)

    def _handle_protocol_error(
        self, exception: urllib3.exceptions.ProtocolError, log_callback: Callable[[int, str], None]
    ):
        """Handles urllib3 protocol error exceptions

        Parameters
        ----------
        exception
            urllib3 protocol error exception to be handled
        log_callback
            callback for logging debug messages
        """

        if (len(exception.args) < 2) or not isinstance(exception.args[1], urllib3.exceptions.InvalidChunkLength):
            raise exception

        log_callback(logging.DEBUG, "OpenShift API server closed connection")

    def _log(self, level: int, msg: str):
        q(msg)

        if level >= logging.WARN:
            self.get_module().warn(msg)

    def _wait_for_custom_resource(
        self,
        kind_metadata: KindMetadata,
        log_callback: Callable[[int, str], None],
        success_callback: Callable[..., bool],
        **kwargs,
    ):
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
                    resource_version = cpo.lib.jmespath.get_jmespath_string("object.metadata.resourceVersion", event)
                    succeeded = success_callback(event, **kwargs)

                    if succeeded:
                        w.stop()
            except client.ApiException as exception:
                self._handle_api_exception(exception, log_callback)
                resource_version = None
            except urllib3.exceptions.ProtocolError as exception:
                self._handle_protocol_error(exception, log_callback)

    def _wait_for_namespaced_custom_resource(
        self,
        project: str,
        kind_metadata: KindMetadata,
        log_callback: Callable[[int, str], None],
        success_callback: Callable[..., Optional[CustomResourceEventResult]],
        **kwargs,
    ) -> CustomResourceEventResult:
        custom_objects_api = client.CustomObjectsApi()
        custom_resource_event_result: Optional[CustomResourceEventResult] = None

        while custom_resource_event_result is None:
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
                    resource_version = cpo.lib.jmespath.get_jmespath_string("object.metadata.resourceVersion", event)
                    custom_resource_event_result = success_callback(event, kind_metadata=kind_metadata, **kwargs)

                    if custom_resource_event_result is not None:
                        w.stop()
            except client.ApiException as exception:
                self._handle_api_exception(exception, log_callback)
                resource_version = None
            except urllib3.exceptions.ProtocolError as exception:
                self._handle_protocol_error(exception, log_callback)

        return custom_resource_event_result
