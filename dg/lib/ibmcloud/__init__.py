import subprocess

from typing import Final

import dg.utils.process

from dg.config import data_gate_configuration_manager

EXTERNAL_IBM_CLOUD_API_KEY_NAME: Final[str] = "dg.api.key"
INTERNAL_IBM_CLOUD_API_KEY_NAME: Final[str] = "ibm_cloud_api_key"


def execute_ibmcloud_command(args: list[str]) -> subprocess.CompletedProcess:
    ibmcloud_cli_path = data_gate_configuration_manager.get_ibmcloud_cli_path()

    return dg.utils.process.execute_command(ibmcloud_cli_path, args)


def execute_ibmcloud_command_interactively(args: list[str]) -> int:
    proc = subprocess.Popen(
        [
            str(data_gate_configuration_manager.get_ibmcloud_cli_path()),
        ]
        + args
    )

    proc.communicate()

    return proc.returncode


def execute_ibmcloud_command_without_check(
    args: list[str],
) -> subprocess.CompletedProcess:
    ibmcloud_cli_path = data_gate_configuration_manager.get_ibmcloud_cli_path()

    return dg.utils.process.execute_command_without_check(ibmcloud_cli_path, args)
