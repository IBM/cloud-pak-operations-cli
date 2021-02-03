import json

import click

from dg.lib.ibmcloud import execute_ibmcloud_command


def get_default_public_vlan(zone: str) -> str:
    return _get_default_vlan_id("public", zone)


def get_default_private_vlan(zone: str) -> str:
    return _get_default_vlan_id("private", zone)


def _get_default_vlan_id(vlan_type: str, zone: str) -> str:
    args = ["oc", "vlan", "ls", "--zone", zone, "--json"]
    result = execute_ibmcloud_command(args, capture_output=True)
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
