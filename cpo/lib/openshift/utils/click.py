#  Copyright 2021, 2023 IBM Corporation
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
import re as regex

from typing import Any, Callable

import click

from click_option_group import optgroup


def openshift_server_command_optgroup_options(f: Callable[..., Any]) -> Callable[..., Any]:
    options = [
        optgroup.option(
            "--insecure-skip-tls-verify", help="Skips checking the server's certificate for validity", is_flag=True
        ),
        optgroup.option("--token", help="OpenShift OAuth access token"),
        optgroup.option("--password", help="OpenShift password"),
        optgroup.option("--username", help="OpenShift username"),
        optgroup.option("--server", help="OpenShift server URL"),
    ]

    return functools.reduce(lambda result, option: option(result), options, f)


def openshift_server_options(f: Callable[..., Any]) -> Callable[..., Any]:
    options = [
        click.option("--use-cluster", help="Alias or server URL of a registered OpenShift cluster to be used"),
        click.option(
            "--insecure-skip-tls-verify",
            default=None,
            help="Skips checking the server's certificate for validity",
            is_flag=True,
        ),
        click.option("--token", help="OpenShift OAuth access token"),
        click.option("--password", help="OpenShift password"),
        click.option("--username", help="OpenShift username"),
        click.option("--server", help="OpenShift server URL"),
    ]

    return functools.reduce(lambda result, option: option(result), options, f)


def validate_ocp_version(ctx, param, value):
    if value is not None and regex.match("\\d+\\.\\d+(\\.\\d)*", value) is None:
        raise click.BadParameter("Invalid OpenShift Container Platform version")

    return value
