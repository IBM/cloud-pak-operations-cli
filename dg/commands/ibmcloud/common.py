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

from typing import Any

import click

from dg.lib.ibmcloud import execute_ibmcloud_command


def is_logged_in() -> bool:
    login_status = False
    target_information = get_ibmcloud_account_target_information()

    if target_information and "user" in target_information:
        login_status = True

    return login_status


def get_ibmcloud_account_target_information() -> Any:
    """Get the targeted region, account, resource group, org or space"""

    result = execute_ibmcloud_command(
        ["target", "--output", "JSON"], capture_output=True
    )

    target_information = json.loads(result.stdout)

    return target_information


def is_logged_in_and_print_help_message_if_not():
    login_status = is_logged_in()
    if not login_status:
        _print_not_logged_in_message()

    return login_status


def _print_not_logged_in_message():
    click.echo(
        (
            "It seems you're not logged in to the IBM cloud CLI. Please execute `dg ibmcloud login` (interactive) and "
            "afterwards re-run the current command."
        )
    )


def get_default_public_vlan(zone: str):
    return _get_default_vlan_id("public", zone)


def get_default_private_vlan(zone: str):
    return _get_default_vlan_id("private", zone)


def _get_default_vlan_id(vlan_type: str, zone: str) -> str:
    get_default_vlan_command = ["oc", "vlan", "ls", "--zone", zone, "--json"]
    result = execute_ibmcloud_command(get_default_vlan_command, capture_output=True)
    result_json = json.loads(result.stdout)

    vlan_id = ""
    if result_json:
        for vlan in result_json:
            if (
                vlan["type"] == vlan_type
                and vlan["properties"]["vlan_type"] == "standard"
            ):
                vlan_id = vlan["id"]
                break

    if not vlan_id:
        click.echo("Returned VLAN information:" + result.stdout)
        raise Exception(
            f"Could not obtain default {vlan_type} VLAN ID for zone {zone}."
        )

    return vlan_id


def get_volume_details(volume_id: str):
    args = ["sl", "file", "volume-detail", "--output", "json", volume_id]
    result = execute_ibmcloud_command(args, capture_output=True)

    return json.loads(result.stdout)


def modify_volume_capacity(volume_id: str, new_capacity: int):
    args = [
        "sl",
        "file",
        "volume-modify",
        volume_id,
        "--new-size",
        str(new_capacity),
        "--force",
    ]

    execute_ibmcloud_command(args)
