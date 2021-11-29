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

import os
import pathlib


def is_relative_to(path1: pathlib.Path, path2: os.PathLike) -> bool:
    """Returns whether or not `path1` is relative to `path2`.

    Parameters
    ----------
    path1
        path compared with `path2`
    path2
        path compared with `path1`

    Returns
    -------
    bool
        True, if `path1` is relative to `path2`
    """

    result = False

    try:
        path1.relative_to(path2)

        result = True
    except ValueError:
        pass

    return result
