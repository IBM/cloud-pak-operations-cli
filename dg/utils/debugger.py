#  Copyright 2020 IBM Corporation
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

import inspect


def is_debugpy_running() -> bool:
    """Returns whether debugpy is running

    Visual Studio Code uses debugpy (https://github.com/microsoft/debugpy)
    as the default Python debugger.

    Returns
    -------
    bool
        True, if debugpy is running
    """

    for frame in inspect.stack():
        if frame.filename.endswith("debugpy/__main__.py"):
            return True

    return False
