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

import json
import logging

from abc import ABC, abstractmethod
from typing import Any, Final, Optional

import jsonschema
import requests

import cpo.lib.fyre.utils.request_status_progress_bar

from cpo.lib.fyre.data.request_status_data import RequestStatusData
from cpo.lib.fyre.response_managers.json_response_manager import (
    AbstractJSONResponseManager,
)
from cpo.lib.fyre.response_managers.ocp_request_get_response_manager import (
    OCPRequestGetResponseManager,
)
from cpo.utils.http_method import HTTPMethod

logger = logging.getLogger(__name__)


class AbstractJSONRequestManager(ABC):
    """Base class of all JSON request managers"""

    def __init__(self, fyre_api_user_name: str, fyre_api_key: str, site: Optional[str] = None):
        self._fyre_api_key = fyre_api_key
        self._fyre_api_user_name = fyre_api_user_name
        self._site = site

    def get_default_request_schema(self) -> Any:
        """Returns the default request JSON schema

        Returns
        -------
        Any
            default request JSON schema
        """

        return {
            "additionalProperties": False,
            "properties": {
                "site": {
                    "type": "string",
                },
            },
            "type": "object",
        }

    @abstractmethod
    def get_error_message(self) -> str:
        """Returns the error message shown when a request failed

        Returns
        -------
        str
            error message shown when a request failed
        """

        pass

    @abstractmethod
    def get_json_response_manager(self) -> AbstractJSONResponseManager:
        """Returns the JSON response manager corresponding to this request
        manager

        Returns
        -------
        AbstractJSONResponseManager
            JSON response manager corresponding to this request manager
        """

        pass

    @abstractmethod
    def get_request_schema(self) -> Any:
        """Returns the request JSON schema

        Returns
        -------
        Any
            request JSON schema
        """

        pass

    @abstractmethod
    def get_url(self) -> str:
        """Returns the request URL

        Returns
        -------
        str
            request URL
        """

        pass

    @abstractmethod
    def is_request_id_to_be_ignored(self) -> bool:
        """Returns whether the request ID returned by a request shall be ignored

        Although some FYRE/OCP+ API endpoints return a request ID, it cannot be
        used to get the request status. Request managers corresponding to these
        endpoints must return True.

        Returns
        -------
        bool
            True, if the request ID returned by a request shall be ignored
        """

        pass

    def _execute_request(
        self,
        http_method: HTTPMethod,
        data: Any = None,
    ) -> Any:
        """Executes a FYRE/OCP+ API JSON request

        Parameters
        ----------
        http_method
            HTTP method
        data
            data

        Returns
        -------
        Any
            FYRE/OCP+ API JSON response
        """

        return self._execute_request_with_params(
            http_method, self.get_url(), self.get_json_response_manager(), self.get_error_message(), data
        )

    def _execute_request_with_params(
        self,
        http_method: HTTPMethod,
        url: str,
        json_response_manager: AbstractJSONResponseManager,
        error_message: str,
        data: Any = None,
    ) -> Any:
        """Executes a FYRE/OCP+ API JSON request

        Parameters
        ----------
        http_method
            HTTP method
        url
            request URL
        json_response_manager
            JSON response manager used to check the JSON response
        error_message
            error message shown when the request failed
        data
            data

        Returns
        -------
        Any
            FYRE/OCP+ API JSON response
        """

        auth = (self._fyre_api_user_name, self._fyre_api_key)
        response: Optional[requests.Response]

        if self._site is not None:
            if data is not None:
                data["site"] = self._site
            else:
                data = {"site": self._site} if self._site is not None else None

        request_schema = self.get_request_schema()

        if request_schema is not None and data is not None:
            jsonschema.Draft7Validator(request_schema).validate(data)

        data_str = json.dumps(data, indent="\t", sort_keys=True) if data is not None else None

        if data_str is not None:
            logger.debug(f"Sending JSON object:\n{data_str}")

        response = requests.request(str(http_method), url, auth=auth, data=data_str, verify=False)  # NOSONAR
        json_response = response.json()

        logger.debug(
            "Received JSON object:\n{json}".format(json=json.dumps(json_response, indent="\t", sort_keys=True))
        )

        if not response.ok:
            json_response_manager.raise_error_if_error_response(
                json_response, f"{error_message} (HTTP status code: {response.status_code})"
            )

        json_response_manager.check_response(json_response, error_message)

        if ("request_id" in json_response) and not self.is_request_id_to_be_ignored():
            cpo.lib.fyre.utils.request_status_progress_bar.wait_for_request_completion(
                json_response["request_id"], self._get_request_status
            )

        return json_response

    def _get_request_status(self, request_id: str) -> RequestStatusData:
        """Get the status of a request

        Parameters
        ----------
        request_id
            Request ID

        Returns
        -------
        RequestStatusData
            object containing the status of a request
        """

        return OCPRequestManager(self._fyre_api_user_name, self._fyre_api_key, request_id).execute_get_request()

    _IBM_OCPPLUS_OCP_REQUEST_ERROR_MESSAGE: Final[str] = "Failed to get request status"
    _IBM_OCPPLUS_OCP_REQUEST_GET_URL: Final[str] = "https://ocpapi.svl.ibm.com/v1/ocp/request/{request_id}"


class OCPRequestManager(AbstractJSONRequestManager):
    def __init__(self, fyre_api_user_name: str, fyre_api_key: str, request_id: str):
        super().__init__(fyre_api_user_name, fyre_api_key)

        self._request_id = request_id

    def execute_get_request(
        self,
    ) -> RequestStatusData:
        return RequestStatusData(self._execute_request(HTTPMethod.GET))

    # override
    def get_error_message(self) -> str:
        return AbstractJSONRequestManager._IBM_OCPPLUS_OCP_REQUEST_ERROR_MESSAGE

    # override
    def get_json_response_manager(self) -> AbstractJSONResponseManager:
        return OCPRequestGetResponseManager()

    # override
    def get_request_schema(self) -> Any:
        return self.get_default_request_schema()

    # override
    def get_url(self) -> str:
        return AbstractJSONRequestManager._IBM_OCPPLUS_OCP_REQUEST_GET_URL.format(request_id=self._request_id)

    # override
    def is_request_id_to_be_ignored(self) -> bool:
        return False
