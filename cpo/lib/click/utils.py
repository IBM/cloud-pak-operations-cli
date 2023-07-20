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

import json
import pathlib

from typing import Any, Optional

import click

import cpo.config.cluster_credentials_manager
import cpo.lib.openshift.oc

from cpo.lib.openshift.credentials.cluster_based_user_credentials import ClusterBasedUserCredentials
from cpo.lib.openshift.credentials.credentials import AbstractCredentials
from cpo.lib.openshift.credentials.token_credentials import TokenCredentials
from cpo.lib.openshift.credentials.user_credentials import UserCredentials


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


def get_cluster_credentials(ctx: click.Context, options: dict[str, Any]) -> AbstractCredentials:
    """Returns cluster credentials based on the options passed to a Click
    command or the current cluster

    Parameters
    ----------
    ctx
        Click context
    options
        options passed to a Click command

    Returns
    -------
    AbstractCredentials
        cluster credentials
    """

    insecure_skip_tls_verify: Optional[bool] = (
        options["insecure_skip_tls_verify"] if "insecure_skip_tls_verify" in options else None
    )

    result: Optional[AbstractCredentials] = None

    if (
        ("server" in options)
        and (options["server"] is not None)
        and ("username" in options)
        and (options["username"] is not None)
        and ("password" in options)
        and (options["password"] is not None)
        and (("token" not in options) or (options["token"] is None))
    ):
        result = UserCredentials(
            options["server"],
            options["username"],
            options["password"],
            insecure_skip_tls_verify if insecure_skip_tls_verify is not None else False,
        )
    elif (
        ("server" in options)
        and (options["server"] is not None)
        and (("username" not in options) or (options["username"] is None))
        and (("password" not in options) or (options["password"] is None))
        and ("token" in options)
        and (options["token"] is not None)
    ):
        result = TokenCredentials(
            options["server"],
            options["token"],
            insecure_skip_tls_verify if insecure_skip_tls_verify is not None else False,
        )
    elif (
        current_cluster := cpo.config.cluster_credentials_manager.cluster_credentials_manager.get_current_cluster()
    ) is not None:
        result = ClusterBasedUserCredentials(current_cluster, insecure_skip_tls_verify)
    else:
        raise click.UsageError(
            "You must either set options --server/--username/--password, --server/--token, or set a current cluster.",
            ctx,
        )

    return result


def get_oc_login_command_for_remote_host(ctx: click.Context, options: dict[str, Any]) -> str:
    result: Optional[str] = None

    if (
        ("server" in options)
        and (options["server"] is not None)
        and ("username" in options)
        and (options["username"] is not None)
        and ("password" in options)
        and (options["password"] is not None)
        and (("token" not in options) or (options["token"] is None))
    ):
        result = cpo.lib.openshift.oc.get_oc_login_command_with_password_for_remote_host(
            options["server"], options["username"], options["password"]
        )
    elif (
        ("server" in options)
        and (options["server"] is not None)
        and (("username" not in options) or (options["username"] is None))
        and (("password" not in options) or (options["password"] is None))
        and ("token" in options)
        and (options["token"] is not None)
    ):
        result = cpo.lib.openshift.oc.get_oc_login_command_with_token_for_remote_host(
            options["server"], options["token"]
        )
    elif (
        current_cluster := cpo.config.cluster_credentials_manager.cluster_credentials_manager.get_current_cluster()
    ) is not None:
        result = cpo.lib.openshift.oc.get_oc_login_command_with_password_for_remote_host(
            current_cluster.get_server(), current_cluster.get_username(), current_cluster.get_password()
        )
    else:
        raise click.UsageError(
            "You must either set options --server/--username/--password, --server/--token, or set a current cluster.",
            ctx,
        )

    return result


def log_in_to_openshift_cluster(ctx: click.Context, options: dict[str, Any]):
    if (
        ("server" in options)
        and (options["server"] is not None)
        and ("username" in options)
        and (options["username"] is not None)
        and ("password" in options)
        and (options["password"] is not None)
        and (("token" not in options) or (options["token"] is None))
    ):
        cpo.lib.openshift.oc.log_in_to_openshift_cluster_with_password(
            options["server"], options["username"], options["password"]
        )
    elif (
        ("server" in options)
        and (options["server"] is not None)
        and (("username" not in options) or (options["username"] is None))
        and (("password" not in options) or (options["password"] is None))
        and ("token" in options)
        and (options["token"] is not None)
    ):
        cpo.lib.openshift.oc.log_in_to_openshift_cluster_with_token(options["server"], options["token"])
    elif (
        current_cluster := cpo.config.cluster_credentials_manager.cluster_credentials_manager.get_current_cluster()
    ) is not None:
        current_cluster.login()
    else:
        raise click.UsageError(
            "You must either set options --server/--username/--password, --server/--token, or set a current cluster.",
            ctx,
        )
