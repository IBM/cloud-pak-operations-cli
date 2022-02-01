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

import pathlib
import sys

from importlib.metadata import Distribution, EntryPoint, distributions
from types import ModuleType
from typing import Any, Optional


class DistributionEntryPointLoader:
    """Determines the corresponding distribution package for a loaded entry
    point if possible

    Notes
    -----
    Starting from Python 3.10, EntryPoint instances have an instance
    variable named "dist" referencing the corresponding distribution package
    if applicable. Therefore, when switching to Python 3.10 or higher, this
    class should be removed.

    https://bugs.python.org/issue42382
    """

    def __init__(self, entry_point: EntryPoint):
        loaded_entry_point = entry_point.load()

        self._distribution: Optional[Distribution] = self._get_distribution_from_loaded_entry_point(loaded_entry_point)
        self._loaded_entry_point = loaded_entry_point

    @property
    def distribution(self) -> Optional[Distribution]:
        return self._distribution

    @property
    def loaded_entry_point(self) -> Any:
        return self._loaded_entry_point

    def _get_distribution_from_loaded_entry_point(self, loaded_entry_point: Any) -> Optional[Distribution]:
        """Determines the corresponding distribution package for a loaded entry
        point if possible

        Parameters
        ----------
        loaded_entry_point
            loaded entry point

        Returns
        -------
        Optional[Distribution]
            corresponding distribution package for the given loaded entry point or
            None if it could not be determined
        """

        if isinstance(loaded_entry_point, ModuleType):
            module_path = loaded_entry_point.__file__
        else:
            module_path = sys.modules[loaded_entry_point.__module__].__file__

        if module_path is None:
            return None

        result: Optional[Distribution] = None

        for distribution in distributions():
            if distribution.files is None:
                continue

            try:
                relative_path = pathlib.Path(module_path).relative_to(distribution.locate_file(""))
            except ValueError:
                pass
            else:
                if relative_path in distribution.files:
                    result = distribution

                    break

        return result
