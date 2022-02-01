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

import pathlib

from typing import Final

import cpo.commands

from cpo.utils.importlib import get_distribution_package_name

commands_package_path: Final[pathlib.Path] = pathlib.Path(cpo.commands.__file__).parent
distribution_package_name: Final[str] = get_distribution_package_name()
plugin_group_name: Final[str] = "cloud_pak_operations_cli_plugins"
