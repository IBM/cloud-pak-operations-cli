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

from typing import Any

import jmespath

from cpo.utils.error import JmespathPathExpressionNotFoundException, UnexpectedTypeException


def get_jmespath_bool(expression: str, data: Any) -> bool:
    """Returns a bool extracted from the given object based on the given
    JMESPath expression

    Parameters
    ----------
    expression
        JMESPath expression
    data
        object to be searched

    Returns
    -------
    bool
        bool extracted from the given object based on the given JMESPath
        expression
    """

    search_result = jmespath.search(expression, data)

    if search_result is None:
        raise JmespathPathExpressionNotFoundException(expression)

    if not isinstance(search_result, bool):
        raise UnexpectedTypeException(search_result)

    return search_result


def get_jmespath_list_of_strings(expression: str, data: Any) -> list[str]:
    """Returns a list of strings extracted from the given object based on
    the given JMESPath expression

    Parameters
    ----------
    expression
        JMESPath expression
    data
        object to be searched

    Returns
    -------
    list[str]
        list of strings extracted from the given object based on the given
        JMESPath expression
    """

    search_result: Any = jmespath.search(expression, data)

    if search_result is None:
        raise JmespathPathExpressionNotFoundException(expression)

    if not isinstance(search_result, list) or not all(isinstance(element, str) for element in search_result):
        raise UnexpectedTypeException(search_result)

    return search_result


def get_jmespath_string(expression: str, data: Any) -> str:
    """Returns a string extracted from the given object based on the given
    JMESPath expression

    Parameters
    ----------
    expression
        JMESPath expression
    data
        object to be searched

    Returns
    -------
    list[str]
        string extracted from the given object based on the given JMESPath
        expression
    """

    search_result = jmespath.search(expression, data)

    if search_result is None:
        raise JmespathPathExpressionNotFoundException(expression)

    if not isinstance(search_result, str):
        raise UnexpectedTypeException(search_result)

    return search_result
