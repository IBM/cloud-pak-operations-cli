import logging

from dg.lib.error import IBMCloudException
from dg.lib.ibmcloud import execute_ibmcloud_command_without_check

logger = logging.getLogger(__name__)


def install_catalogs_management_plugin():
    _install_plugin("catalogs-management")


def install_container_service_plugin():
    _install_plugin("container-service")


def is_catalogs_management_plugin_installed() -> bool:
    return _is_plugin_installed("catalogs-management")


def is_container_service_plugin_installed() -> bool:
    return _is_plugin_installed("container-service")


def _install_plugin(plugin_name: str):
    logging.info(f"Installing IBM Cloud plug-in '{plugin_name}'")

    args = ["plugin", "install", plugin_name]
    result = execute_ibmcloud_command_without_check(args, capture_output=True)

    if result.return_code != 0:
        raise IBMCloudException(
            f"An error occurred when attempting to install ibmcloud plug-in {plugin_name}",
            result.stderr,
        )


def _is_plugin_installed(plugin_name: str) -> bool:
    args = ["plugin", "list"]
    result = execute_ibmcloud_command_without_check(args, capture_output=True)

    if result.return_code != 0:
        raise IBMCloudException(
            f"An error occurred when attempting to check whether ibmcloud plug-in {plugin_name} is installed",
            result.stderr,
        )

    is_installed = plugin_name in result.stdout

    return is_installed
