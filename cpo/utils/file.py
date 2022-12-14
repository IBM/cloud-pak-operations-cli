#  Copyright 2021, 2022 IBM Corporation
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

from enum import Enum
from typing import Optional


class FileType(Enum):
    Directory = 1
    RegularFile = 2


def get_relative_path(path: os.PathLike, subpath: pathlib.Path) -> Optional[pathlib.Path]:
    relative_path: Optional[pathlib.Path] = None

    try:
        relative_path = subpath.relative_to(path)
    except ValueError:
        pass

    return relative_path
