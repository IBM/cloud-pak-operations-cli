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

import re as regex

from typing import Optional

import click


def validate_node_name(ctx, param, value) -> Optional[str]:  # NOSONAR
    if value is not None and regex.match("(inf|(master|worker)\\d+)$", value) is None:
        raise click.BadParameter("Invalid node name")

    return value
