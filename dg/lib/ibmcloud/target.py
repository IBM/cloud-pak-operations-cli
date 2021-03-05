import json

from typing import Any

from dg.lib.ibmcloud import execute_ibmcloud_command


def get_ibmcloud_account_target_information() -> Any:
    """Get the targeted region, account, resource group, org or space"""

    args = ["target", "--output", "json"]
    result = execute_ibmcloud_command(args, capture_output=True)
    result_json = json.loads(result.stdout)

    return result_json
