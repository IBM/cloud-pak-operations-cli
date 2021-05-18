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

import json

import click

from dg.lib.fyre.types.ocp_quick_burn_max_hours_response import (
    OCPQuickBurnMaxHoursResponse,
)


class QuickBurnMaxHoursData:
    def __init__(self, ocp_quick_burn_max_hours_response: OCPQuickBurnMaxHoursResponse):
        self._ocp_quick_burn_max_hours_response = ocp_quick_burn_max_hours_response

    def format(self, use_json: bool = False):
        if use_json:
            click.echo(json.dumps(self._ocp_quick_burn_max_hours_response, indent="\t", sort_keys=True))
        else:
            click.echo(self._ocp_quick_burn_max_hours_response["quick_burn_max_hours"])
