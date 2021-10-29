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

def removeprefix(str: str, prefix: str) -> str:
    """Returns the given string without the given prefix if it starts with
    it or otherwise a copy of the original string

    Notes
    -----
    This method can be removed once Python 3.9 is a prerequisite:
    https://docs.python.org/3/library/stdtypes.html#str.removeprefix

    Parameters
    ----------
    str
        string
    prefix
        prefix to be removed

    Returns
    -------
    str
        given string without the given prefix if it starts with it or otherwise
        a copy of the original string
    """

    if str.startswith(prefix):
        return str[len(prefix) :]  # noqa: E203 (https://github.com/PyCQA/pycodestyle/issues/373)

    return str


def removesuffix(str: str, suffix: str) -> str:
    """Returns the given string without the given suffix if it ends with it
    or otherwise a copy of the original string

    Notes
    -----
    This method can be removed once Python 3.9 is a prerequisite:
    https://docs.python.org/3/library/stdtypes.html#str.removesuffix

    Parameters
    ----------
    str
        string
    suffix
        suffix to be removed

    Returns
    -------
    str
        given string without the given suffix if it ends with it or otherwise a
        copy of the original string
    """

    if str.endswith(suffix):
        return str[: -len(suffix)]

    return str
