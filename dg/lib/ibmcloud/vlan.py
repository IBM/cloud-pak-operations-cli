import json
import logging

from dg.lib.error import DataGateCLIException
from dg.lib.ibmcloud import execute_ibmcloud_command

logger = logging.getLogger(__name__)


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
            if vlan["type"] == vlan_type and vlan["properties"]["vlan_type"] == "standard":
                vlan_id = vlan["id"]

                break

    if not vlan_id:
        logging.info("Returned VLAN information:" + result.stdout)

        raise DataGateCLIException(f"Could not obtain default {vlan_type} VLAN ID for zone {zone}.")

    return vlan_id
