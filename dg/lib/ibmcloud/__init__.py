import subprocess

from typing import Final, List, Optional

import dg.utils.process

from dg.config import data_gate_configuration_manager
from dg.lib.error import DataGateCLIException, IBMCloudException

EXTERNAL_IBM_CLOUD_API_KEY_NAME: Final[str] = "dg.api.key"
INTERNAL_IBM_CLOUD_API_KEY_NAME: Final[str] = "ibm_cloud_api_key"


def execute_ibmcloud_command(
    args: List[str], capture_output=False, check=True, print_captured_output=False
) -> dg.utils.process.ProcessResult:
    """Executes the IBM Cloud CLI

    Parameters
    ----------
    args
        arguments to be passed to the IBM Cloud CLI
    capture_output
        flag indicating whether output shall be captured
    check
        flag indicating whether an exception shall be thrown if the IBM Cloud
        CLI returns with a nonzero return code
    print_captured_output
        flag indicating whether captured output shall also be written to
        stdout/stderr

    Returns
    -------
    ProcessResult
        object storing the return code and captured output (if requested)
    """

    ibmcloud_cli_path = data_gate_configuration_manager.get_ibmcloud_cli_path()
    process_result: Optional[dg.utils.process.ProcessResult] = None

    try:
        process_result = dg.utils.process.execute_command(
            ibmcloud_cli_path,
            args,
            capture_output=capture_output,
            check=check,
            print_captured_output=print_captured_output,
        )
    except DataGateCLIException as exception:
        raise IBMCloudException(exception.stderr)

    return process_result


def execute_ibmcloud_command_interactively(args: List[str]) -> int:
    proc = subprocess.Popen(
        [
            str(data_gate_configuration_manager.get_ibmcloud_cli_path()),
        ]
        + args
    )

    proc.communicate()

    return proc.returncode


def execute_ibmcloud_command_without_check(
    args: List[str], capture_output=False, print_captured_output=False
) -> dg.utils.process.ProcessResult:
    """Executes the IBM Cloud CLI without checking its return code

    Parameters
    ----------
    args
        arguments to be passed to the IBM Cloud CLI
    capture_output
        flag indicating whether output shall be captured
    print_captured_output
        flag indicating whether captured output shall also be written to
        stdout/stderr

    Returns
    -------
    ProcessResult
        object storing the return code and captured output (if requested)
    """

    return execute_ibmcloud_command(
        args,
        capture_output=capture_output,
        check=False,
        print_captured_output=print_captured_output,
    )
