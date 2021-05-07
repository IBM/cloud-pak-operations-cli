import json
import logging

from typing import List

from dg.lib.error import IBMCloudException
from dg.lib.ibmcloud import (
    execute_ibmcloud_command,
    execute_ibmcloud_command_without_check,
)


class PlugInManager:
    """Manages IBM Cloud CLI plug-ins"""

    def __init__(self):
        self.refresh()

    def install_required_plug_ins(self):
        self._install_plugin("catalogs-management")
        self._install_plugin("container-service")

    def refresh(self):
        self._plug_ins = self._get_plug_ins()

    def _get_plug_ins(self) -> List[str]:
        ibmcloud_plugin_list_command_args = ["plugin", "list", "--output", "json"]
        ibmcloud_plugin_list_command_result = execute_ibmcloud_command(
            ibmcloud_plugin_list_command_args, capture_output=True
        )

        ibmcloud_plugin_list_command_result_json = json.loads(ibmcloud_plugin_list_command_result.stdout)
        plug_ins: List[str] = []

        for plugin in ibmcloud_plugin_list_command_result_json:
            if "Name" in plugin:
                plug_ins.append(plugin["Name"])

        return plug_ins

    def _install_plugin(self, plug_in_name: str):
        if plug_in_name not in self._plug_ins:
            logging.info(f"Installing IBM Cloud plug-in '{plug_in_name}'")

            ibmcloud_plugin_install_command_args = ["plugin", "install", plug_in_name]
            ibmcloud_plugin_install_command_result = execute_ibmcloud_command_without_check(
                ibmcloud_plugin_install_command_args, capture_output=True
            )

            if ibmcloud_plugin_install_command_result.return_code != 0:
                raise IBMCloudException(
                    f"An error occurred when attempting to install IBM Cloud CLI plug-in {plug_in_name}",
                    ibmcloud_plugin_install_command_result.stderr,
                )
