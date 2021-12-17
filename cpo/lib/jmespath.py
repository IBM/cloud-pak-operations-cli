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

from typing import Any, List

import jmespath

from cpo.lib.error import (
    JmespathPathExpressionNotFoundException,
    UnexpectedTypeException,
)


def get_jmespath_list_of_strings(expression: str, data: Any) -> List[str]:
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
    List[str]
        list of strings extracted from the given object based on the given
        JMESPath expression
    """

    search_result: Any = jmespath.search(expression, data)

    if search_result is None:
        raise JmespathPathExpressionNotFoundException(expression)

    if not isinstance(search_result, List) or not all(isinstance(element, str) for element in search_result):
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
    List[str]
        string extracted from the given object based on the given JMESPath
        expression
    """

    search_result = jmespath.search(expression, data)

    if search_result is None:
        raise JmespathPathExpressionNotFoundException(expression)

    if not isinstance(search_result, str):
        raise UnexpectedTypeException(search_result)

    return search_result
