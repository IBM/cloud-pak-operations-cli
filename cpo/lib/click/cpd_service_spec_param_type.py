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

from typing import Any, Optional

import click


class CloudPakForDataServiceSpecParamType(click.ParamType):
    """Click parameter type accepting a boolean, integer, or string
    argument"""

    name = "VALUE"

    # override
    def convert(self, value: Any, param: Optional[click.Parameter], ctx: Optional[click.Context]) -> Any:
        try:
            return click.BOOL.convert(value, param, ctx)
        except click.BadParameter:
            pass

        try:
            return click.INT.convert(value, param, ctx)
        except click.BadParameter:
            pass

        return click.STRING.convert(value, param, ctx)
