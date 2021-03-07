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

import importlib
import json
import logging
import pathlib

from types import ModuleType
from typing import Any

import click

import dg.config.cluster_credentials_manager
import dg.lib.openshift

from dg.lib.cloud_pak_for_data.cpd_manager import (
    CloudPakForDataAssemblyBuildType,
)


def check_cloud_pak_for_data_options(
    ctx: click.Context,
    build_type: CloudPakForDataAssemblyBuildType,
    options: dict[str, Any],
):
    """Checks if values for required Click options were passed to a Click
    command to install an IBM Cloud Pak for Data assembly

    Parameters
    ----------
    build_type
        build type of an IBM Cloud Pak for Data assembly to be installed
    options
        options passed to a Click command
    """

    if build_type == CloudPakForDataAssemblyBuildType.DEV:
        if (
            ("artifactory_user_name" in options)
            and (options["artifactory_user_name"] is None)
            and ("artifactory_api_key" in options)
            and (options["artifactory_api_key"] is None)
        ):
            raise click.UsageError(
                "Missing options '--artifactory-user-name' and '--artifactory-api-key'",
                ctx,
            )
        elif ("artifactory_user_name" in options) and (options["artifactory_user_name"] is None):
            raise click.UsageError("Missing option '--artifactory-user-name'", ctx)
        elif ("artifactory_api_key" in options) and (options["artifactory_api_key"] is None):
            raise click.UsageError("Missing option '--artifactory-api-key'", ctx)
    else:
        if ("ibm_cloud_pak_for_data_entitlement_key" in options) and (
            options["ibm_cloud_pak_for_data_entitlement_key"] is None
        ):
            raise click.UsageError("Missing option '--ibm-cloud-pak-for-data-entitlement-key'", ctx)


def create_click_multi_command_class(modules: dict[str, ModuleType]) -> type[click.Command]:
    """Creates a definition of a subclass of click.MultiCommand

    This method creates a definition of a subclass of click.MultiCommand
    providing Click commands found in the given Python modules.

    Parameters
    ----------
    modules
        Python modules to be searched for Click commands

    Returns
    -------
    click.Command
        Definition of a subclass of click.MultiCommand
    """

    command_names, commands = create_click_multi_command_data_structures(modules)

    class MultiCommand(click.MultiCommand):
        def __call__(self, *args, **kwargs):
            """Handle exceptions raised by Click commands"""

            try:
                return self.main(*args, **kwargs)
            except Exception as exception:
                click.ClickException(str(exception)).show()

        def get_command(self: click.MultiCommand, ctx: click.Context, cmd_name: str) -> click.Command:
            if cmd_name not in commands:
                raise click.ClickException("Unknown command")

            return commands[cmd_name]

        def list_commands(self: click.MultiCommand, ctx: click.Context) -> list[str]:
            return command_names

    return MultiCommand


def create_click_multi_command_data_structures(
    modules: dict[str, ModuleType]
) -> tuple[list[str], dict[str, click.Command]]:
    """Creates click.MultiCommand data structures

    This method creates two data structures based on Click commands within
    the given Python modules. These data structures may be used when
    defining a subclass of click.MultiCommand:

    - a list of Click command names
    - a dictionary associating Click command names with Click commands

    Parameters
    ----------
    modules
        Python modules

    Returns
    -------
    tuple[list[str], dict[str, click.Command]]
        tuple consisting of a list of Click command names and a dictionary
        associating Click command names with Click commands
    """

    command_names: list[str] = []
    commands: dict[str, click.Command] = {}

    for module_name, module in modules.items():
        module_commands = get_click_commands(module)

        if len(module_commands) != 0:
            commands.update(module_commands)
            command_names.append(module_name.replace("_", "-"))

    command_names.sort()

    return command_names, commands


def create_default_map_from_dict(dict: dict[str, Any]):
    default_map_dict = {}
    default_map_dict["default_map"] = dict

    return default_map_dict


def create_default_map_from_json_file(path: pathlib.Path):
    default_map_dict = {}

    if path.exists() and (path.stat().st_size != 0):
        with open(path) as json_file:
            credentials_file_contents = json.load(json_file)

            default_map_dict["default_map"] = credentials_file_contents

    return default_map_dict


def get_click_commands(module: ModuleType) -> dict[str, click.Command]:
    """Returns Click commands within a Python module

    This method searches the given Python module for Click commands.

    Parameters
    ----------
    modules
        Python modules

    Returns
    -------
    dict[str, click.Command]
        dictionary associating Click command names with Click commands
    """

    commands: dict[str, click.Command] = {}

    for attributeName in dir(module):
        attribute = getattr(module, attributeName)

        if isinstance(attribute, click.Command):
            command_name = attributeName.replace("_", "-")

            commands[command_name] = attribute

    return commands


def get_oc_login_command_for_remote_host(ctx: click.Context, options: dict[str, Any]) -> str:
    result: str

    if (
        ("username" in options)
        and (options["username"] is not None)
        and ("password" in options)
        and (options["password"] is not None)
    ):
        result = dg.lib.openshift.get_oc_login_command_with_password_for_remote_host(
            options["server"], options["username"], options["password"]
        )
    elif ("token" in options) and (options["token"] is not None):
        result = dg.lib.openshift.get_oc_login_command_with_token_for_remote_host(options["server"], options["token"])
    else:
        current_cluster = dg.config.cluster_credentials_manager.cluster_credentials_manager.get_current_cluster()

        if current_cluster is None:
            raise click.UsageError(
                "You must either set options '--server' and '--password', '--token', or set a current cluster.",
                ctx,
            )

        cluster_data = current_cluster.get_cluster_data()

        result = dg.lib.openshift.get_oc_login_command_with_password_for_remote_host(
            cluster_data["server"], cluster_data["username"], cluster_data["password"]
        )

    return result


def import_packages_and_modules(package_name: str, package_directory_path: pathlib.Path) -> dict[str, ModuleType]:
    """Imports all subpackages and submodules within the current package

    Parameters
    ----------
    package_name
        name of the current package (__name__)
    package_directory_path
        path of the directory of the current package (__file__)

    Returns
    -------
    dict[str, ModuleType]
        dictionary associating names of imported modules with imported modules
    """

    modules: dict[str, ModuleType] = {}

    for file_path in package_directory_path.iterdir():
        if file_path.is_dir() and (file_path / "__init__.py").exists():
            package_or_module_name = file_path.name

            logging.debug("Importing package {}.{}".format(package_name, package_or_module_name))
            modules[package_or_module_name] = importlib.import_module(
                "{}.{}".format(package_name, package_or_module_name)
            )
        elif file_path.is_file() and (file_path.suffix == ".py") and (file_path.name != "__init__.py"):
            package_or_module_name = file_path.name[:-3]

            logging.debug("Importing module {}.{}".format(package_name, package_or_module_name))
            modules[package_or_module_name] = importlib.import_module(
                "{}.{}".format(package_name, package_or_module_name)
            )

    return modules


def log_in_to_openshift_cluster(ctx: click.Context, options: dict[str, Any]):
    if (
        ("username" in options)
        and (options["username"] is not None)
        and ("password" in options)
        and (options["password"] is not None)
    ):
        dg.lib.openshift.log_in_to_openshift_cluster_with_password(
            options["server"], options["username"], options["password"]
        )
    elif ("token" in options) and (options["token"] is not None):
        dg.lib.openshift.log_in_to_openshift_cluster_with_token(options["server"], options["token"])
    else:
        raise click.UsageError(
            "You must either set options '--server' and '--password', '--token', or set a current cluster.",
            ctx,
        )
