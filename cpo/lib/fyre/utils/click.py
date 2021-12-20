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

import functools

from typing import Any, Callable

import click

from click_option_group import optgroup


def fyre_command_optgroup_options(f: Callable[..., Any]) -> Callable[..., Any]:
    options = [
        optgroup.option("--fyre-api-key", help="FYRE API key (see https://fyre.svl.ibm.com/account)", required=True),
        optgroup.option("--fyre-api-user-name", help="FYRE API user name", required=True),
    ]

    return functools.reduce(lambda result, option: option(result), options, f)


def fyre_command_options(f: Callable[..., Any]) -> Callable[..., Any]:
    options = [
        click.option("--fyre-api-key", help="FYRE API key (see https://fyre.svl.ibm.com/account)", required=True),
        click.option("--fyre-api-user-name", help="FYRE API user name", required=True),
    ]

    return functools.reduce(lambda result, option: option(result), options, f)
